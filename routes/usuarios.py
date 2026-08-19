from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from database import get_db
from models import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioLogin, Token
from security import get_password_hash, verify_password
from auth import create_access_token, get_current_user

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(usuario: UsuarioCreate):
    db = get_db()
    usuario_dict = usuario.model_dump()
    usuario_dict["senha"] = get_password_hash(usuario_dict["senha"])
    try:
        result = await db.usuarios.insert_one(usuario_dict)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Matrícula já cadastrada")
    created_usuario = await db.usuarios.find_one({"_id": result.inserted_id})
    return created_usuario

@router.post("/login", response_model=Token)
async def login(credentials: UsuarioLogin):
    db = get_db()
    usuario = await db.usuarios.find_one({"matricula": credentials.matricula})
    if not usuario:
        raise HTTPException(status_code=401, detail="Matrícula ou senha incorretos")

    if not verify_password(credentials.senha, usuario["senha"]):
        raise HTTPException(status_code=401, detail="Matrícula ou senha incorretos")

    access_token = create_access_token(str(usuario["_id"]), usuario["matricula"], usuario["nome"])
    return Token(access_token=access_token, usuario=usuario)


@router.get("/", response_model=List[UsuarioResponse])
async def list_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    usuarios = await db.usuarios.find({}, {"senha": 0}).sort("_id", 1).skip(skip).limit(limit).to_list(limit)
    return usuarios

@router.get("/{id}", response_model=UsuarioResponse)
async def get_usuario(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    usuario = await db.usuarios.find_one({"_id": ObjectId(id)}, {"senha": 0})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario not found")
    return usuario

@router.put("/{id}", response_model=UsuarioResponse)
async def update_usuario(id: str, usuario_update: UsuarioUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    if str(current_user["_id"]) != id:
        raise HTTPException(status_code=403, detail="Você só pode atualizar o seu próprio usuário")
    update_data = {k: v for k, v in usuario_update.model_dump().items() if v is not None}

    if "senha" in update_data:
        update_data["senha"] = get_password_hash(update_data["senha"])

    if update_data:
        try:
            result = await db.usuarios.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        except DuplicateKeyError:
            raise HTTPException(status_code=409, detail="Matrícula já cadastrada")
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuario not found")

    updated_usuario = await db.usuarios.find_one({"_id": ObjectId(id)}, {"senha": 0})
    return updated_usuario

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    if str(current_user["_id"]) != id:
        raise HTTPException(status_code=403, detail="Você só pode excluir o seu próprio usuário")
    result = await db.usuarios.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario not found")
