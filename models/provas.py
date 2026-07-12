from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseDBModel

class Prova(BaseDBModel):
    nome: str
    dia: str
    horario: str
    materia: str

class ProvaCreate(BaseModel):
    nome: str
    dia: str
    horario: str
    materia: str

class ProvaUpdate(BaseModel):
    nome: Optional[str] = None
    dia: Optional[str] = None
    horario: Optional[str] = None
    materia: Optional[str] = None
