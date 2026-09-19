from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bootstrap.api.router import api_router
from bootstrap.config.settings import get_settings
from bootstrap.database.init import create_tables
from bootstrap.database.session import close_engine, engine

settings = get_settings()

LOCAL_DEVELOPMENT_ORIGIN_REGEX = (
    r"https?://(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$"
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_tables(engine)
    yield
    await close_engine()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Qwen demo API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_origin_regex=(
        LOCAL_DEVELOPMENT_ORIGIN_REGEX if settings.app_env == "development" else None
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)
