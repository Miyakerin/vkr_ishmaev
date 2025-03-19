import aiohttp
from authlib.jose import JsonWebKey
from sqlalchemy.ext.asyncio import AsyncEngine

from shared.db.sql_database import Database
from ..db_models import MyBase
from ..settings import settings, Settings


async def init():
    db = Database(engines_params=settings.all_db)
    await db.run_sync_batch(MyBase.metadata.create_all)
    for engine in (await db.get_engines()).values():
        await raw_sql_scripts_init(engine=engine)
    await get_public_key(settings_=settings)


async def raw_sql_scripts_init(engine: AsyncEngine):
    async with engine.begin() as conn:
        pass


async def get_public_key(settings_: Settings):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{settings_.auth_service_settings.url}/auth/api/v1/jwk") as resp:
            settings_.auth_key = JsonWebKey.import_key(await resp.json())
