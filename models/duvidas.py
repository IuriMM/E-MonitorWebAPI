from pydantic import BaseModel, Field
from typing import List, Optional
from .base import BaseDBModel

class Comentario(BaseModel):
    usuario: str
    classe: str
    texto: str

class Duvida(BaseDBModel):
    materia: str
    horario: str
    duvida: str
    status: str
    usuario: Optional[str] = None
    comentarios: List[Comentario] = []

class DuvidaCreate(BaseModel):
    materia: str
    horario: str
    duvida: str
    status: str
    comentarios: List[Comentario] = []

class DuvidaUpdate(BaseModel):
    materia: Optional[str] = None
    horario: Optional[str] = None
    duvida: Optional[str] = None
    status: Optional[str] = None
    usuario: Optional[str] = None
    comentarios: Optional[List[Comentario]] = None
