from motor.motor_asyncio import AsyncIOMotorClient
import os

# Padrão: usar localhost, mas pode ser sobreposto via variável de ambiente
MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "eMonitorDB"

client = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    print(f"Conectado ao MongoDB: {MONGODB_URL} no banco {DB_NAME}")
    await create_indexes()

async def create_indexes():
    await db.usuarios.create_index("matricula", unique=True)
    await db.duvidas.create_index("usuario")
    await db.duvidas.create_index([("materia", 1), ("status", 1)])
    await db.mensagens.create_index([("remetente", 1), ("destinatario", 1)])
    await db.materiais_estudo.create_index([("materia", 1), ("autor", 1)])

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Conexão com o MongoDB encerrada.")

def get_db():
    return db
