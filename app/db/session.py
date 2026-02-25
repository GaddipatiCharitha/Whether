from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# ================= DATABASE ENGINE =================

engine = create_async_engine(
    settings.DATABASE_URL,   # sqlite+aiosqlite:///./weather.db
    echo=False,
    future=True,
)

# ================= SESSION =================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ================= BASE =================

Base = declarative_base()


# ================= DEPENDENCY =================

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session