from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from database import get_db
from models import Usuario, UsuarioCreate, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def create_usuario(usuario: UsuarioCreate):
    db = get_db()
    usuario_dict = usuario.model_dump()
    result = await db.usuarios.insert_one(usuario_dict)
    created_usuario = await db.usuarios.find_one({"_id": result.inserted_id})
    return created_usuario

@router.get("/", response_model=List[Usuario])
async def list_usuarios():
    db = get_db()
    usuarios = await db.usuarios.find().to_list(1000)
    return usuarios

@router.get("/{id}", response_model=Usuario)
async def get_usuario(id: str):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    usuario = await db.usuarios.find_one({"_id": ObjectId(id)})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario not found")
    return usuario

@router.put("/{id}", response_model=Usuario)
async def update_usuario(id: str, usuario_update: UsuarioUpdate):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    update_data = {k: v for k, v in usuario_update.model_dump().items() if v is not None}
    if update_data:
        result = await db.usuarios.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuario not found")
    
    updated_usuario = await db.usuarios.find_one({"_id": ObjectId(id)})
    return updated_usuario

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(id: str):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.usuarios.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario not found")
