from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseDBModel

class Mensagem(BaseDBModel):
    destinatario: str # Monitor para qual a mensagem foi enviada (ex: "José")
    remetente: str
    texto: str
    horario: str

class MensagemWSIn(BaseModel):
    destinatario: str
    texto: str

class MensagemUpdate(BaseModel):
    # SECURITY FIX: Removed remetente, destinatario, horario from update schema
    # to prevent Mass Assignment and unauthorized modification of metadata.
    texto: Optional[str] = None
