
import asyncio
from src.db.database import Base, async_engine
from src.db.config import settings

print("Подключение к БД:", settings.DATABASE_URL_asyncpg) 

async def delete_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

asyncio.run(delete_tables())