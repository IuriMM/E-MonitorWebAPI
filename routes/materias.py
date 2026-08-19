from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from database import get_db
from models import Materia, MateriaCreate, MateriaUpdate
from auth import get_current_user

router = APIRouter(prefix="/materias", tags=["Materias"])

@router.post("/", response_model=Materia, status_code=status.HTTP_201_CREATED)
async def create_materia(materia: MateriaCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    materia_dict = materia.model_dump()
    result = await db.materias.insert_one(materia_dict)
    created_materia = await db.materias.find_one({"_id": result.inserted_id})
    return created_materia

@router.get("/", response_model=List[Materia])
async def list_materias(current_user: dict = Depends(get_current_user)):
    db = get_db()
    materias = await db.materias.find().to_list(1000)
    return materias

@router.get("/{id}", response_model=Materia)
async def get_materia(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    materia = await db.materias.find_one({"_id": ObjectId(id)})
    if not materia:
        raise HTTPException(status_code=404, detail="Materia not found")
    return materia

@router.put("/{id}", response_model=Materia)
async def update_materia(id: str, materia_update: MateriaUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    update_data = {k: v for k, v in materia_update.model_dump().items() if v is not None}
    if update_data:
        result = await db.materias.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Materia not found")

    updated_materia = await db.materias.find_one({"_id": ObjectId(id)})
    return updated_materia

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.materias.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Materia not found")
