from aiogram import Router

from .callbacks import router as callbacks_router
from .commands import router as commands_router
from .quiz_callbacks import router as quiz_router
from .listeners import router as listeners_router

router = Router()
router.include_router(callbacks_router)
router.include_router(commands_router)
router.include_router(quiz_router)
router.include_router(listeners_router)
