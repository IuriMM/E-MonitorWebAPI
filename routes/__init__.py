from fastapi import APIRouter
from .materias import router as materias_router
from .provas import router as provas_router
from .usuarios import router as usuarios_router
from .duvidas import router as duvidas_router
from .mensagens import router as mensagens_router
from .materiais_estudo import router as materiais_estudo_router

router = APIRouter()

router.include_router(materias_router)
router.include_router(provas_router)
router.include_router(usuarios_router)
router.include_router(duvidas_router)
router.include_router(mensagens_router)
router.include_router(materiais_estudo_router)
