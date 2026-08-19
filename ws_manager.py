from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    """Registro em memória das conexões WebSocket ativas, indexado pelo nome
    do usuário (mesma identidade já usada em mensagens.remetente/destinatario).
    Só funciona para deploy de instância única — não há broadcast entre
    processos."""

    def __init__(self):
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, nome: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(nome, set()).add(websocket)

    def disconnect(self, nome: str, websocket: WebSocket) -> None:
        conexoes = self.active.get(nome)
        if not conexoes:
            return
        conexoes.discard(websocket)
        if not conexoes:
            del self.active[nome]

    async def send_to_user(self, nome: str, payload: dict) -> None:
        for websocket in list(self.active.get(nome, ())):
            await websocket.send_json(payload)


manager = ConnectionManager()
