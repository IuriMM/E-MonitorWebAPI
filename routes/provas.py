from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from bson import ObjectId
from database import get_db
from models import Prova, ProvaCreate, ProvaUpdate, Papel
from auth import get_current_user, require_role

router = APIRouter(prefix="/provas", tags=["Provas"])

async def _check_monitor_da_materia_da_prova(db, current_user: dict, prova: dict) -> None:
    if current_user["papel"] == Papel.ADMIN:
        return
    materia = await db.materias.find_one({"codigo": prova["materia"]})
    # materia.monitores guarda o `nome` do monitor, mesma convenção usada em
    # mensagens.remetente/destinatario e materiais_estudo.autor.
    if not materia or current_user["nome"] not in materia.get("monitores", []):
        raise HTTPException(status_code=403, detail="Só um monitor da matéria desta prova ou admin pode alterá-la")

@router.post("/", response_model=Prova, status_code=status.HTTP_201_CREATED)
async def create_prova(prova: ProvaCreate, current_user: dict = Depends(require_role(Papel.MONITOR, Papel.ADMIN))):
    db = get_db()
    prova_dict = prova.model_dump()
    result = await db.provas.insert_one(prova_dict)
    created_prova = await db.provas.find_one({"_id": result.inserted_id})
    return created_prova

@router.get("/", response_model=List[Prova])
async def list_provas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    provas = await db.provas.find().sort("_id", 1).skip(skip).limit(limit).to_list(limit)
    return provas

@router.get("/{id}", response_model=Prova)
async def get_prova(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    prova = await db.provas.find_one({"_id": ObjectId(id)})
    if not prova:
        raise HTTPException(status_code=404, detail="Prova not found")
    return prova

@router.put("/{id}", response_model=Prova)
async def update_prova(id: str, prova_update: ProvaUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    prova = await db.provas.find_one({"_id": ObjectId(id)})
    if not prova:
        raise HTTPException(status_code=404, detail="Prova not found")
    await _check_monitor_da_materia_da_prova(db, current_user, prova)

    update_data = {k: v for k, v in prova_update.model_dump().items() if v is not None}
    if update_data:
        await db.provas.update_one({"_id": ObjectId(id)}, {"$set": update_data})

    updated_prova = await db.provas.find_one({"_id": ObjectId(id)})
    return updated_prova

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prova(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    prova = await db.provas.find_one({"_id": ObjectId(id)})
    if not prova:
        raise HTTPException(status_code=404, detail="Prova not found")
    await _check_monitor_da_materia_da_prova(db, current_user, prova)
    await db.provas.delete_one({"_id": ObjectId(id)})
