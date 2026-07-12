from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from database import get_db
from models import Duvida, DuvidaCreate, DuvidaUpdate

router = APIRouter(prefix="/duvidas", tags=["Duvidas"])

@router.post("/", response_model=Duvida, status_code=status.HTTP_201_CREATED)
async def create_duvida(duvida: DuvidaCreate):
    db = get_db()
    duvida_dict = duvida.model_dump()
    result = await db.duvidas.insert_one(duvida_dict)
    created_duvida = await db.duvidas.find_one({"_id": result.inserted_id})
    return created_duvida

@router.get("/", response_model=List[Duvida])
async def list_duvidas():
    db = get_db()
    duvidas = await db.duvidas.find().to_list(1000)
    return duvidas

@router.get("/{id}", response_model=Duvida)
async def get_duvida(id: str):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    duvida = await db.duvidas.find_one({"_id": ObjectId(id)})
    if not duvida:
        raise HTTPException(status_code=404, detail="Duvida not found")
    return duvida

@router.put("/{id}", response_model=Duvida)
async def update_duvida(id: str, duvida_update: DuvidaUpdate):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    update_data = {k: v for k, v in duvida_update.model_dump().items() if v is not None}
    if update_data:
        result = await db.duvidas.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Duvida not found")
    
    updated_duvida = await db.duvidas.find_one({"_id": ObjectId(id)})
    return updated_duvida

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_duvida(id: str):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.duvidas.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Duvida not found")
