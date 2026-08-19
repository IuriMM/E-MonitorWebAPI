from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from database import get_db
from models import Mensagem, MensagemCreate, MensagemUpdate
from auth import get_current_user

router = APIRouter(prefix="/mensagens", tags=["Mensagens"])

@router.post("/", response_model=Mensagem, status_code=status.HTTP_201_CREATED)
async def create_mensagem(mensagem: MensagemCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if mensagem.remetente != current_user["nome"]:
        raise HTTPException(status_code=403, detail="Remetente deve ser o usuário autenticado")
    mensagem_dict = mensagem.model_dump()
    result = await db.mensagens.insert_one(mensagem_dict)
    created_mensagem = await db.mensagens.find_one({"_id": result.inserted_id})
    return created_mensagem

@router.get("/", response_model=List[Mensagem])
async def list_mensagens(
    remetente: Optional[str] = None,
    destinatario: Optional[str] = None,
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

    mensagens = await db.mensagens.find(query).to_list(1000)
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
