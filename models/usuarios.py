from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from .base import BaseDBModel

class Papel(str, Enum):
    ALUNO = "aluno"
    MONITOR = "monitor"
    ADMIN = "admin"

class Usuario(BaseDBModel):
    nome: str
    sobrenome: str
    fotoPerfil: bool = False
    curso: str
    matricula: str
    senha: str
    papel: Papel = Papel.ALUNO
    materias: List[str] = []
    monitor: List[str] = []

# `papel` propositalmente fora de UsuarioCreate/UsuarioUpdate: o cadastro público
# e a auto-edição (PUT /usuarios/{id}, restrito ao dono) nunca podem setar o
# próprio papel. Promoção a monitor/admin só via seed manual no banco ou uma
# rota futura restrita a admin.
class UsuarioCreate(BaseModel):
    nome: str
    sobrenome: str
    fotoPerfil: bool = False
    curso: str
    matricula: str
    senha: str
    materias: List[str] = []
    monitor: List[str] = []

class UsuarioResponse(BaseDBModel):
    nome: str
    sobrenome: str
    fotoPerfil: bool = False
    curso: str
    matricula: str
    papel: Papel = Papel.ALUNO
    materias: List[str] = []
    monitor: List[str] = []

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    sobrenome: Optional[str] = None
    fotoPerfil: Optional[bool] = None
    curso: Optional[str] = None
    matricula: Optional[str] = None
    senha: Optional[str] = None
    materias: Optional[List[str]] = None
    monitor: Optional[List[str]] = None

class UsuarioLogin(BaseModel):
    matricula: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
