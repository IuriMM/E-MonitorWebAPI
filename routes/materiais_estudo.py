from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from database import get_db
from models import MaterialEstudo, MaterialEstudoCreate, MaterialEstudoUpdate

router = APIRouter(prefix="/materiais_estudo", tags=["Materiais Estudo"])

@router.post("/", response_model=MaterialEstudo, status_code=status.HTTP_201_CREATED)
async def create_material_estudo(material_estudo: MaterialEstudoCreate):
    db = get_db()
    material_dict = material_estudo.model_dump()
    result = await db.materiais_estudo.insert_one(material_dict)
    created_material = await db.materiais_estudo.find_one({"_id": result.inserted_id})
    return created_material

@router.get("/", response_model=List[MaterialEstudo])
async def list_materiais_estudo():
    db = get_db()
    materiais = await db.materiais_estudo.find().to_list(1000)
    return materiais

@router.get("/{id}", response_model=MaterialEstudo)
async def get_material_estudo(id: str):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    material = await db.materiais_estudo.find_one({"_id": ObjectId(id)})
    if not material:
        raise HTTPException(status_code=404, detail="MaterialEstudo not found")
    return material

@router.put("/{id}", response_model=MaterialEstudo)
async def update_material_estudo(id: str, material_update: MaterialEstudoUpdate):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    update_data = {k: v for k, v in material_update.model_dump().items() if v is not None}
    if update_data:
        result = await db.materiais_estudo.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="MaterialEstudo not found")
    
    updated_material = await db.materiais_estudo.find_one({"_id": ObjectId(id)})
    return updated_material

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material_estudo(id: str):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.materiais_estudo.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="MaterialEstudo not found")
