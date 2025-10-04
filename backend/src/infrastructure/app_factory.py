"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from adapters.inbound.api_router import create_rule_router
from adapters.outbound.file_repository import FileRuleRepository
from application.services import EvaluationService, RuleService
from infrastructure.config import config


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    config.ensure_data_directory()

    app = FastAPI(
        title=config.APP_NAME,
        version=config.APP_VERSION,
        description=config.APP_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    repository = FileRuleRepository(config.RULES_FILE)
    rule_service = RuleService(repository)
    evaluation_service = EvaluationService(repository)

    router = create_rule_router(rule_service, evaluation_service)
    app.include_router(router)

    @app.get("/", include_in_schema=False)
    async def root():
        """Redirect root to API documentation."""
        return RedirectResponse(url="/docs")

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": config.APP_NAME, "version": config.APP_VERSION}

    return app

