from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseDBModel

class MaterialEstudo(BaseDBModel):
    materia: str
    autor: str
    titulo: str
    comentario: str
    link: str
    data: str

class MaterialEstudoCreate(BaseModel):
    materia: str
    autor: str
    titulo: str
    comentario: str
    link: str
    data: str

class MaterialEstudoUpdate(BaseModel):
    materia: Optional[str] = None
    autor: Optional[str] = None
    titulo: Optional[str] = None
    comentario: Optional[str] = None
    link: Optional[str] = None
    data: Optional[str] = None
