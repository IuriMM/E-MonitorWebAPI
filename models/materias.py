from pydantic import BaseModel, Field
from typing import List, Optional
from .base import BaseDBModel, PyObjectId

class CronogramaItem(BaseModel):
    dia_semana: str
    horario: str
    sala: str

class Materia(BaseDBModel):
    codigo: str # Ex: MAT032
    nome: str
    monitores: List[str] = []
    cronograma: List[CronogramaItem] = []

class MateriaCreate(BaseModel):
    codigo: str
    nome: str
    monitores: List[str] = []
    cronograma: List[CronogramaItem] = []

class MateriaUpdate(BaseModel):
    codigo: Optional[str] = None
    nome: Optional[str] = None
    monitores: Optional[List[str]] = None
    cronograma: Optional[List[CronogramaItem]] = None
