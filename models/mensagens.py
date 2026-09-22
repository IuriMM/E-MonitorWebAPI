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
    # Security: Apenas o texto pode ser editado. Remetente, destinatario e horario são imutáveis.
    texto: Optional[str] = None
