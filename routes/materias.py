from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from bson import ObjectId
from database import get_db
from models import Materia, MateriaCreate, MateriaUpdate, Papel
from auth import get_current_user, require_role

router = APIRouter(prefix="/materias", tags=["Materias"])

@router.post("/", response_model=Materia, status_code=status.HTTP_201_CREATED)
async def create_materia(materia: MateriaCreate, current_user: dict = Depends(require_role(Papel.MONITOR, Papel.ADMIN))):
    db = get_db()
    materia_dict = materia.model_dump()
    result = await db.materias.insert_one(materia_dict)
    created_materia = await db.materias.find_one({"_id": result.inserted_id})
    return created_materia

@router.get("/", response_model=List[Materia])
async def list_materias(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    materias = await db.materias.find().sort("_id", 1).skip(skip).limit(limit).to_list(limit)
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

def _is_monitor_da_materia(current_user: dict, materia: dict) -> bool:
    if current_user["papel"] == Papel.ADMIN:
        return True
    # materia.monitores guarda o `nome` do monitor (mesma convenção de
    # mensagens.remetente/destinatario e materiais_estudo.autor), não a matricula.
    return current_user["nome"] in materia.get("monitores", [])

@router.put("/{id}", response_model=Materia)
async def update_materia(id: str, materia_update: MateriaUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    materia = await db.materias.find_one({"_id": ObjectId(id)})
    if not materia:
        raise HTTPException(status_code=404, detail="Materia not found")
    if not _is_monitor_da_materia(current_user, materia):
        raise HTTPException(status_code=403, detail="Só um monitor desta matéria ou admin pode editá-la")

    update_data = {k: v for k, v in materia_update.model_dump().items() if v is not None}
    if update_data:
        await db.materias.update_one({"_id": ObjectId(id)}, {"$set": update_data})

    updated_materia = await db.materias.find_one({"_id": ObjectId(id)})
    return updated_materia

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    materia = await db.materias.find_one({"_id": ObjectId(id)})
    if not materia:
        raise HTTPException(status_code=404, detail="Materia not found")
    if not _is_monitor_da_materia(current_user, materia):
        raise HTTPException(status_code=403, detail="Só um monitor desta matéria ou admin pode excluí-la")
    await db.materias.delete_one({"_id": ObjectId(id)})
