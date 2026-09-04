from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from bson import ObjectId
from database import get_db
from models import Duvida, DuvidaCreate, DuvidaUpdate, Papel
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
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
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

    duvidas = await db.duvidas.find(query).sort("_id", 1).skip(skip).limit(limit).to_list(limit)
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

    duvida_existente = await db.duvidas.find_one({"_id": ObjectId(id)})
    if not duvida_existente:
        raise HTTPException(status_code=404, detail="Duvida not found")

    is_autor = duvida_existente.get("usuario") == str(current_user["_id"])
    if not is_autor and current_user["papel"] not in (Papel.MONITOR, Papel.ADMIN):
        raise HTTPException(status_code=403, detail="Só o autor da dúvida ou monitor/admin pode editá-la")

    if duvida_update.usuario is not None:
        if not ObjectId.is_valid(duvida_update.usuario):
            raise HTTPException(status_code=400, detail="Invalid Usuario ID")
        usuario_exists = await db.usuarios.find_one({"_id": ObjectId(duvida_update.usuario)})
        if not usuario_exists:
            raise HTTPException(status_code=404, detail="Usuario not found")

    if duvida_update.status is not None and current_user["papel"] not in (Papel.MONITOR, Papel.ADMIN):
        raise HTTPException(status_code=403, detail="Só monitor/admin pode alterar o status da dúvida")

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
    duvida = await db.duvidas.find_one({"_id": ObjectId(id)})
    if not duvida:
        raise HTTPException(status_code=404, detail="Duvida not found")
    is_autor = duvida.get("usuario") == str(current_user["_id"])
    if not is_autor and current_user["papel"] not in (Papel.MONITOR, Papel.ADMIN):
        raise HTTPException(status_code=403, detail="Só o autor da dúvida ou monitor/admin pode excluí-la")
    await db.duvidas.delete_one({"_id": ObjectId(id)})
