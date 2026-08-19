import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException, Query, WebSocket, WebSocketException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import ALLOWED_ORIGINS
from models import Papel

# Padrão: usar uma chave de desenvolvimento, mas deve ser sobreposta via variável de ambiente em produção
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key-nao-usar-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

bearer_scheme = HTTPBearer()


def create_access_token(usuario_id: str, matricula: str, nome: str, papel: Papel) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": usuario_id, "matricula": matricula, "nome": nome, "papel": papel.value, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> Optional[dict]:
    """Decodifica o JWT e monta o usuário autenticado só a partir das claims,
    sem round-trip ao Mongo. Válido enquanto o token não expirar (24h) — um
    usuário deletado nesse meio-tempo continua autenticado até o token expirar."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

    usuario_id = payload.get("sub")
    nome = payload.get("nome")
    if not usuario_id or not ObjectId.is_valid(usuario_id) or not nome:
        return None

    # Tokens emitidos antes do campo `papel` existir não têm essa claim;
    # cai no papel menos privilegiado em vez de quebrar sessões já ativas.
    try:
        papel = Papel(payload.get("papel", Papel.ALUNO.value))
    except ValueError:
        papel = Papel.ALUNO

    return {
        "_id": ObjectId(usuario_id),
        "nome": nome,
        "matricula": payload.get("matricula"),
        "papel": papel,
    }


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    usuario = _decode_token(credentials.credentials)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario


async def get_current_user_ws(websocket: WebSocket, token: str = Query(...)) -> dict:
    origin = websocket.headers.get("origin")
    if origin is not None and origin not in ALLOWED_ORIGINS:
        raise WebSocketException(code=4403, reason="Origem não permitida")

    usuario = _decode_token(token)
    if usuario is None:
        raise WebSocketException(code=4401, reason="Token inválido ou expirado")
    return usuario


def require_role(*allowed: Papel):
    """Dependency factory: só deixa passar quem tem um dos papéis em `allowed`.
    current_user segue dict (não o model Usuario) para manter o dependency
    stateless igual get_current_user — nenhuma chamada extra ao Mongo."""

    async def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["papel"] not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ação não permitida para seu papel.")
        return current_user

    return checker
