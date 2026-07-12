from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from database import get_db
from models import Mensagem, MensagemCreate, MensagemUpdate

router = APIRouter(prefix="/mensagens", tags=["Mensagens"])

@router.post("/", response_model=Mensagem, status_code=status.HTTP_201_CREATED)
async def create_mensagem(mensagem: MensagemCreate):
    db = get_db()
    mensagem_dict = mensagem.model_dump()
    result = await db.mensagens.insert_one(mensagem_dict)
    created_mensagem = await db.mensagens.find_one({"_id": result.inserted_id})
    return created_mensagem

@router.get("/", response_model=List[Mensagem])
async def list_mensagens():
    db = get_db()
    mensagens = await db.mensagens.find().to_list(1000)
    return mensagens

@router.get("/{id}", response_model=Mensagem)
async def get_mensagem(id: str):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    mensagem = await db.mensagens.find_one({"_id": ObjectId(id)})
    if not mensagem:
        raise HTTPException(status_code=404, detail="Mensagem not found")
    return mensagem

@router.put("/{id}", response_model=Mensagem)
async def update_mensagem(id: str, mensagem_update: MensagemUpdate):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    update_data = {k: v for k, v in mensagem_update.model_dump().items() if v is not None}
    if update_data:
        result = await db.mensagens.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Mensagem not found")
    
    updated_mensagem = await db.mensagens.find_one({"_id": ObjectId(id)})
    return updated_mensagem

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mensagem(id: str):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.mensagens.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Mensagem not found")
