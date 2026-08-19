from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from bson import ObjectId
from database import get_db
from models import MaterialEstudo, MaterialEstudoCreate, MaterialEstudoUpdate
from auth import get_current_user

router = APIRouter(prefix="/materiais_estudo", tags=["Materiais Estudo"])

@router.post("/", response_model=MaterialEstudo, status_code=status.HTTP_201_CREATED)
async def create_material_estudo(material_estudo: MaterialEstudoCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    material_dict = material_estudo.model_dump()
    result = await db.materiais_estudo.insert_one(material_dict)
    created_material = await db.materiais_estudo.find_one({"_id": result.inserted_id})
    return created_material

@router.get("/", response_model=List[MaterialEstudo])
async def list_materiais_estudo(
    materia: Optional[str] = None,
    autor: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    db = get_db()

    if autor is not None and autor != current_user["nome"]:
        raise HTTPException(status_code=403, detail="Você só pode filtrar os seus próprios materiais")

    query = {}
    if materia is not None:
        query["materia"] = materia
    if autor is not None:
        query["autor"] = autor

    materiais = await db.materiais_estudo.find(query).sort("_id", 1).skip(skip).limit(limit).to_list(limit)
    return materiais

@router.get("/{id}", response_model=MaterialEstudo)
async def get_material_estudo(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    material = await db.materiais_estudo.find_one({"_id": ObjectId(id)})
    if not material:
        raise HTTPException(status_code=404, detail="MaterialEstudo not found")
    return material

@router.put("/{id}", response_model=MaterialEstudo)
async def update_material_estudo(id: str, material_update: MaterialEstudoUpdate, current_user: dict = Depends(get_current_user)):
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
async def delete_material_estudo(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.materiais_estudo.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="MaterialEstudo not found")
