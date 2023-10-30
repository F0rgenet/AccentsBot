from aiogram import Router
from .user import router as user_handlers_router
from .admin import router as admin_handlers_router

router = Router()
router.include_router(user_handlers_router)
router.include_router(admin_handlers_router)
