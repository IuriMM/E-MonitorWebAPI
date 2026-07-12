from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection
from routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa no início
    await connect_to_mongo()
    yield
    # Executa no final
    await close_mongo_connection()

app = FastAPI(
    title="eMonitor Web API",
    description="API para o sistema eMonitor usando FastAPI e MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://e-monitorwebapi.onrender.com",
        "https://e-monitor.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do eMonitor! Acesse /docs para a documentação Swagger."}
