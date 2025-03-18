import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from shared.db.sql_database import Database
from ..db_models import MyBase
from ..settings import settings


async def init():
    db = Database(engines_params=settings.all_db)
    await db.run_sync_batch(MyBase.metadata.create_all)
    for engine in (await db.get_engines()).values():
        await raw_sql_scripts_init(engine=engine)


async def raw_sql_scripts_init(engine: AsyncEngine):
    async with engine.begin() as conn:
        pass
