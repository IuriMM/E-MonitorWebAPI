from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from auth import get_current_user, get_current_user_ws
from database import get_db
from models import Mensagem, MensagemUpdate, MensagemWSIn
from ws_manager import manager

router = APIRouter(prefix="/mensagens", tags=["Mensagens"])


@router.websocket("/ws")
async def mensagens_ws(websocket: WebSocket, current_user: dict = Depends(get_current_user_ws)):
    nome_usuario = current_user["nome"]
    db = get_db()
    await manager.connect(nome_usuario, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            try:
                payload = MensagemWSIn(**data)
            except Exception:
                await websocket.send_json({"type": "error", "detail": "Payload inválido"})
                continue

            mensagem_dict = {
                "destinatario": payload.destinatario,
                "remetente": nome_usuario,
                "texto": payload.texto,
                "horario": datetime.now(timezone.utc).isoformat(),
            }
            result = await db.mensagens.insert_one(mensagem_dict)
            # insert_one() muta mensagem_dict in-place adicionando "_id" como ObjectId;
            # o "_id" explícito (string) precisa vir depois do spread para vencer o merge.
            evento = {**mensagem_dict, "type": "mensagem", "_id": str(result.inserted_id)}

            await manager.send_to_user(payload.destinatario, evento)
            await manager.send_to_user(nome_usuario, evento)
    except WebSocketDisconnect:
        manager.disconnect(nome_usuario, websocket)


@router.get("/", response_model=List[Mensagem])
async def list_mensagens(
    remetente: Optional[str] = None,
    destinatario: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    nome_usuario = current_user["nome"]

    if (remetente is not None or destinatario is not None) and nome_usuario not in (remetente, destinatario):
        raise HTTPException(status_code=403, detail="Você só pode ver conversas das quais participa")

    if remetente is not None or destinatario is not None:
        query = {}
        if remetente is not None:
            query["remetente"] = remetente
        if destinatario is not None:
            query["destinatario"] = destinatario
    else:
        query = {"$or": [{"remetente": nome_usuario}, {"destinatario": nome_usuario}]}

    mensagens = await db.mensagens.find(query).sort("_id", 1).skip(skip).limit(limit).to_list(limit)
    return mensagens

@router.get("/{id}", response_model=Mensagem)
async def get_mensagem(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    mensagem = await db.mensagens.find_one({"_id": ObjectId(id)})
    if not mensagem:
        raise HTTPException(status_code=404, detail="Mensagem not found")
    if current_user["nome"] not in (mensagem["remetente"], mensagem["destinatario"]):
        raise HTTPException(status_code=403, detail="Você não participa desta conversa")
    return mensagem

@router.put("/{id}", response_model=Mensagem)
async def update_mensagem(id: str, mensagem_update: MensagemUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    mensagem = await db.mensagens.find_one({"_id": ObjectId(id)})
    if not mensagem:
        raise HTTPException(status_code=404, detail="Mensagem not found")
    if current_user["nome"] not in (mensagem["remetente"], mensagem["destinatario"]):
        raise HTTPException(status_code=403, detail="Você não participa desta conversa")

    update_data = {k: v for k, v in mensagem_update.model_dump().items() if v is not None}
    if update_data:
        result = await db.mensagens.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Mensagem not found")

    updated_mensagem = await db.mensagens.find_one({"_id": ObjectId(id)})

    evento = {"type": "update", "_id": id, **{k: v for k, v in updated_mensagem.items() if k != "_id"}}
    await manager.send_to_user(updated_mensagem["remetente"], evento)
    await manager.send_to_user(updated_mensagem["destinatario"], evento)

    return updated_mensagem

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mensagem(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    mensagem = await db.mensagens.find_one({"_id": ObjectId(id)})
    if not mensagem:
        raise HTTPException(status_code=404, detail="Mensagem not found")
    if current_user["nome"] not in (mensagem["remetente"], mensagem["destinatario"]):
        raise HTTPException(status_code=403, detail="Você não participa desta conversa")

    result = await db.mensagens.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Mensagem not found")

    evento = {"type": "delete", "_id": id}
    await manager.send_to_user(mensagem["remetente"], evento)
    await manager.send_to_user(mensagem["destinatario"], evento)
