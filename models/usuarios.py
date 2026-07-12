from pydantic import BaseModel, Field
from typing import List, Optional
from .base import BaseDBModel

class Usuario(BaseDBModel):
    nome: str
    sobrenome: str
    fotoPerfil: bool = False
    curso: str
    matricula: str
    senha: str
    materias: List[str] = []

class UsuarioCreate(BaseModel):
    nome: str
    sobrenome: str
    fotoPerfil: bool = False
    curso: str
    matricula: str
    senha: str
    materias: List[str] = []

class UsuarioResponse(BaseDBModel):
    nome: str
    sobrenome: str
    fotoPerfil: bool = False
    curso: str
    matricula: str
    materias: List[str] = []

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    sobrenome: Optional[str] = None
    fotoPerfil: Optional[bool] = None
    curso: Optional[str] = None
    matricula: Optional[str] = None
    senha: Optional[str] = None
    materias: Optional[List[str]] = None

class UsuarioLogin(BaseModel):
    matricula: str
    senha: str
