from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import SessionLocal, engine, Base

from app.models import User, Category, Resource, SearchLog, Announcement, Wish, WishReply, DonationConfig  # noqa: F401

from app.api.auth import router as auth_router
from app.api.search import router as search_router
from app.api.announcements import router as announcements_router
from app.api.wishes import router as wishes_router
from app.api.donation import router as donation_router
from app.api.admin.resources import router as admin_resources_router
from app.api.admin.categories import router as admin_categories_router
from app.api.admin.users import router as admin_users_router
from app.api.admin.ai_parse import router as admin_ai_router
from app.api.admin.stats import router as admin_stats_router
from app.api.admin.models import router as admin_models_router
from app.api.admin.announcements import router as admin_announcements_router
from app.api.admin.wishes import router as admin_wishes_router
from app.api.admin.donation import router as admin_donation_router
from app.api.admin.upload import router as admin_upload_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    from app.models.user import User as UserModel
    from app.utils.security import hash_password
    db = SessionLocal()
    try:
        admin = db.query(UserModel).filter(UserModel.username == settings.ADMIN_USERNAME).first()
        if not admin:
            admin = UserModel(
                username=settings.ADMIN_USERNAME,
                email="admin@example.com",
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                role="super_admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
        elif admin.role != "super_admin":
            admin.role = "super_admin"
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(
    title="云盘资源搜索系统",
    description="CloudDrive Search System API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(search_router)
app.include_router(announcements_router)
app.include_router(wishes_router)
app.include_router(donation_router)
app.include_router(admin_resources_router)
app.include_router(admin_categories_router)
app.include_router(admin_users_router)
app.include_router(admin_ai_router)
app.include_router(admin_stats_router)
app.include_router(admin_models_router)
app.include_router(admin_announcements_router)
app.include_router(admin_wishes_router)
app.include_router(admin_donation_router)
app.include_router(admin_upload_router)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
async def root():
    return {"message": "云盘资源搜索系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
