import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from shared.db.sql_database import Database
from ..db_models import MyBase, UserXProfilePicture
from ..settings import settings


async def init():
    db = Database(engines_params=settings.all_db)
    await db.run_sync_batch(MyBase.metadata.create_all)
    for engine in (await db.get_engines()).values():
        await raw_sql_scripts_init(engine=engine)


async def raw_sql_scripts_init(engine: AsyncEngine):

    async with engine.begin() as conn:
        table_name = UserXProfilePicture.__tablename__
        function_name = f"trigger_on_{table_name}"
        query = f"""
            CREATE OR REPLACE FUNCTION {function_name}() RETURNS TRIGGER AS ${function_name}$
                BEGIN
                    IF (NEW.is_main = true) THEN
                        UPDATE {table_name}
                        SET is_main = false
                        WHERE user_x_profile_picture_id <> NEW.user_x_profile_picture_id;
                    END IF;
                    
                    RETURN NEW;
                END;
            ${function_name}$ LANGUAGE plpgsql;
        """
        await conn.execute(text(query))
        query = f"""CREATE OR REPLACE TRIGGER {function_name} BEFORE INSERT OR UPDATE ON {table_name}
                                FOR EACH ROW EXECUTE FUNCTION {function_name}();
                            """
        await conn.execute(text(query))

