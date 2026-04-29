from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine, Base

# Import all models so Base knows about them before create_all
import models.user      # noqa
import models.profile   # noqa
import models.diet      # noqa
import models.other     # noqa

from routers.auth          import router as auth_router
from routers.profile       import router as profile_router
from routers.chat          import router as chat_router
from routers.diet          import router as diet_router
from routers.community     import router as community_router
from routers.content_cycle import content_router, cycle_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="NourisHer API",
    description="PCOS Wellness App — Backend API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROUTES ───────────────────────────────────────────────────
API = "/api"
app.include_router(auth_router,      prefix=API)
app.include_router(profile_router,   prefix=API)
app.include_router(chat_router,      prefix=API)
app.include_router(diet_router,      prefix=API)
app.include_router(community_router, prefix=API)
app.include_router(content_router,   prefix=API)
app.include_router(cycle_router,     prefix=API)


@app.get("/", tags=["Health"])
async def root():
    return {"app": "NourisHer API", "version": "1.0.0", "status": "running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
