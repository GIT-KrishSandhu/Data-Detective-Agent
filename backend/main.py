import logging
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api.v1.router import api_router

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("data_detective.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Evidence-first multi-agent data readiness platform backend built for Microsoft Agents League Hackathon.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS Middleware
# Next.js frontend will interact with these endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs"
    }

@app.on_event("startup")
async def on_startup():
    logger.info("==================================================")
    logger.info("  Data Detective Agent API is starting up...")
    logger.info(f"  Environment: {settings.ENVIRONMENT}")
    logger.info(f"  CORS Allowed Origins: {settings.BACKEND_CORS_ORIGINS}")
    
    # Automatically initialize tables
    try:
        from database.session import engine, Base
        from models.dataset import DatasetModel  # noqa
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
            # Idempotent migration for Datetime Timezone Compatibility
            # pyrefly: ignore [missing-import]
            from sqlalchemy import text
            
            check_query = text(
                "SELECT data_type FROM information_schema.columns "
                "WHERE table_name = 'datasets' AND column_name = 'created_at';"
            )
            result = await conn.execute(check_query)
            row = result.fetchone()
            if row:
                col_type = row[0].lower()
                if "with time zone" not in col_type:
                    logger.info("  Migrating 'datasets.created_at' column to TIMESTAMP WITH TIME ZONE...")
                    await conn.execute(text(
                        "ALTER TABLE datasets ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE "
                        "USING created_at AT TIME ZONE 'UTC';"
                    ))
                    logger.info("  Migration completed successfully.")
                else:
                    logger.info("  Column 'datasets.created_at' is already timezone-aware. Skipping migration.")
            else:
                logger.warning("  Table 'datasets' or column 'created_at' not found in information_schema.")
            
            # Create index if not exists
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_dataset_created_at ON datasets(created_at);"
            ))
            logger.info("  Index idx_dataset_created_at verified/created successfully.")
            
        logger.info("  Database tables initialized successfully.")
    except Exception as e:
        logger.warning(f"  Failed to initialize database tables: {e}")
        logger.info("  Continuing startup (database connection will be verified on request).")
        
    logger.info("==================================================")
