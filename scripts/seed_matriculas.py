"""Importa matrículas autorizadas a se cadastrar no eMonitor.

Uso:
    python scripts/seed_matriculas.py matriculas.txt

Formato do arquivo: uma matrícula por linha. Linhas em branco e que
começam com # são ignoradas. Idempotente — rodar de novo com uma lista
maior só adiciona as matrículas novas, nunca remove as já cadastradas.
Usa a mesma variável de ambiente MONGODB_URL do resto da API.
"""
import os
import sys

from pymongo import MongoClient

MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "eMonitorDB"


def main(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        matriculas = [
            linha.strip()
            for linha in f
            if linha.strip() and not linha.strip().startswith("#")
        ]

    if not matriculas:
        print("Nenhuma matrícula encontrada no arquivo.")
        return

    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]
    db.matriculas_permitidas.create_index("matricula", unique=True)

    inseridas = 0
    for matricula in matriculas:
        result = db.matriculas_permitidas.update_one(
            {"matricula": matricula}, {"$setOnInsert": {"matricula": matricula}}, upsert=True
        )
        if result.upserted_id is not None:
            inseridas += 1

    print(f"{inseridas} matrícula(s) nova(s) adicionada(s) de {len(matriculas)} no arquivo.")
    client.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python scripts/seed_matriculas.py <arquivo_com_matriculas.txt>")
        sys.exit(1)
    main(sys.argv[1])
