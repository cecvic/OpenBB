from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from archon.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Archon API",
        description="Glass-Box Trading Intelligence Platform",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1", tags=["analysis"])

    @app.get("/")
    async def root():
        return {
            "name": "Archon",
            "description": "Glass-Box Trading Intelligence Platform",
            "version": "0.1.0",
            "docs": "/docs",
        }

    return app


app = create_app()
