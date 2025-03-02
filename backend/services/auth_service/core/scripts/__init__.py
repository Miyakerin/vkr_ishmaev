from shared.db import Database
from ..settings import settings


async def init():
    db_settings = [
        {
            "name": settings.auth_db_settings.name,
            "url": settings.auth_db_settings.url,
            "echo": settings.auth_db_settings.echo,
            "pool_size": settings.auth_db_settings.pool_size,
            "max_overflow": settings.auth_db_settings.max_overflow
        }
    ]

    db = Database(engines_params=db_settings)
