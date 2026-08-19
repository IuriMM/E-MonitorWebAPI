from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from bson import ObjectId
from database import get_db
from models import Duvida, DuvidaCreate, DuvidaUpdate
from auth import get_current_user

router = APIRouter(prefix="/duvidas", tags=["Duvidas"])

@router.post("/", response_model=Duvida, status_code=status.HTTP_201_CREATED)
async def create_duvida(duvida: DuvidaCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()

    duvida_dict = duvida.model_dump()
    duvida_dict["usuario"] = str(current_user["_id"])
    result = await db.duvidas.insert_one(duvida_dict)
    created_duvida = await db.duvidas.find_one({"_id": result.inserted_id})
    return created_duvida

@router.get("/", response_model=List[Duvida])
async def list_duvidas(
    usuario: Optional[str] = None,
    materia: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: dict = Depends(get_current_user),
):
    db = get_db()

    if usuario is not None and usuario != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Você só pode filtrar suas próprias dúvidas")

    query = {}
    if usuario is not None:
        query["usuario"] = usuario
    if materia is not None:
        query["materia"] = materia
    if status_filter is not None:
        query["status"] = status_filter

    duvidas = await db.duvidas.find(query).to_list(1000)
    return duvidas

@router.get("/{id}", response_model=Duvida)
async def get_duvida(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    duvida = await db.duvidas.find_one({"_id": ObjectId(id)})
    if not duvida:
        raise HTTPException(status_code=404, detail="Duvida not found")
    return duvida

@router.put("/{id}", response_model=Duvida)
async def update_duvida(id: str, duvida_update: DuvidaUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    if duvida_update.usuario is not None:
        if not ObjectId.is_valid(duvida_update.usuario):
            raise HTTPException(status_code=400, detail="Invalid Usuario ID")
        usuario_exists = await db.usuarios.find_one({"_id": ObjectId(duvida_update.usuario)})
        if not usuario_exists:
            raise HTTPException(status_code=404, detail="Usuario not found")

    update_data = {k: v for k, v in duvida_update.model_dump().items() if v is not None}
    if update_data:
        result = await db.duvidas.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Duvida not found")

    updated_duvida = await db.duvidas.find_one({"_id": ObjectId(id)})
    return updated_duvida

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_duvida(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.duvidas.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Duvida not found")
