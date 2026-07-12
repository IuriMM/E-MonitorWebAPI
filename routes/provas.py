from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from database import get_db
from models import Prova, ProvaCreate, ProvaUpdate

router = APIRouter(prefix="/provas", tags=["Provas"])

@router.post("/", response_model=Prova, status_code=status.HTTP_201_CREATED)
async def create_prova(prova: ProvaCreate):
    db = get_db()
    prova_dict = prova.model_dump()
    result = await db.provas.insert_one(prova_dict)
    created_prova = await db.provas.find_one({"_id": result.inserted_id})
    return created_prova

@router.get("/", response_model=List[Prova])
async def list_provas():
    db = get_db()
    provas = await db.provas.find().to_list(1000)
    return provas

@router.get("/{id}", response_model=Prova)
async def get_prova(id: str):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    prova = await db.provas.find_one({"_id": ObjectId(id)})
    if not prova:
        raise HTTPException(status_code=404, detail="Prova not found")
    return prova

@router.put("/{id}", response_model=Prova)
async def update_prova(id: str, prova_update: ProvaUpdate):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    update_data = {k: v for k, v in prova_update.model_dump().items() if v is not None}
    if update_data:
        result = await db.provas.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Prova not found")
    
    updated_prova = await db.provas.find_one({"_id": ObjectId(id)})
    return updated_prova

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prova(id: str):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.provas.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prova not found")
