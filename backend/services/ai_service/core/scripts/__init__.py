import uuid

import aiohttp
import asyncio
from authlib.jose import JsonWebKey
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from shared.db.sql_database import Database
from ..db_models import MyBase, Chat, Message, MessageData, MessageDataXFile
from ..settings import settings


async def init():
    db = Database(engines_params=settings.all_db)
    await db.run_sync_batch(MyBase.metadata.create_all)
    for engine in (await db.get_engines()).values():
        await raw_sql_scripts_init(engine=engine)


async def raw_sql_scripts_init(engine: AsyncEngine):
    async with engine.begin() as conn:

        # =================================================================

        table_name = Chat.__tablename__
        function_name = f"trigger_on_{table_name}"
        query = f"""
            CREATE OR REPLACE FUNCTION {function_name}() RETURNS TRIGGER AS ${function_name}$
                BEGIN
                    IF (NEW.delete_timestamp IS NOT NULL) THEN
                        UPDATE {Message.__tablename__}
                        SET delete_timestamp = NEW.delete_timestamp
                        WHERE chat_id = NEW.chat_id;
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

        # =================================================================

        table_name = Message.__tablename__
        function_name = f"trigger_on_{table_name}"
        query = f"""
                    CREATE OR REPLACE FUNCTION {function_name}() RETURNS TRIGGER AS ${function_name}$
                        BEGIN
                            IF (NEW.delete_timestamp IS NOT NULL) THEN
                                UPDATE {MessageData.__tablename__}
                                SET delete_timestamp = NEW.delete_timestamp
                                WHERE message_id = NEW.message_id;
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

        # =================================================================

        table_name = MessageData.__tablename__
        function_name = f"trigger_on_{table_name}"
        query = f"""
                            CREATE OR REPLACE FUNCTION {function_name}() RETURNS TRIGGER AS ${function_name}$
                                BEGIN
                                    IF (NEW.delete_timestamp IS NOT NULL) THEN
                                        UPDATE {MessageDataXFile.__tablename__}
                                        SET delete_timestamp = NEW.delete_timestamp
                                        WHERE message_data_id = NEW.message_data_id;
                                    END IF;
                                    
                                    IF (NEW.is_main = true) THEN
                                        UPDATE {MessageData.__tablename__}
                                        SET is_main = false
                                        WHERE message_id = NEW.message_id AND message_data_id <> NEW.message_data_id;
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


async def refresh_key_every_n_minutes(minutes: int = 30, max_errors=10):
    error_counter = 0
    while True:
        try:
            await get_public_key()
            await asyncio.sleep(minutes*60)
        except Exception:
            error_counter += 1
            if error_counter < max_errors:
                continue
            error_counter = 0
            print(f"max errors reached, sleeping for 5 minutes")
            await asyncio.sleep(5 * 60)


async def refresh_api_tokens_n_minutes(minutes: int = 15, max_errors=10):
    error_counter = 0
    while True:
        try:
            await refresh_gigachat()
            await asyncio.sleep(minutes*60)
        except Exception:
            error_counter += 1
            if error_counter < max_errors:
                continue
            error_counter = 0
            print(f"max errors reached, sleeping for 5 minutes")
            await asyncio.sleep(5*60)


async def get_public_key():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{settings.auth_service_settings.url}/api/v1/jwk") as resp:
                settings.auth_key = JsonWebKey.import_key(await resp.json())
        except Exception:
            settings.auth_key = None


async def refresh_gigachat():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    f"{settings.api_settings.gigachat.auth_url}",
                    ssl=False,
                    headers={
                        "RqUID": str(uuid.uuid4()),
                        "Authorization": f"Basic {settings.api_settings.gigachat.auth_key}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={"scope": settings.api_settings.gigachat.scope},
            ) as resp:
                settings.api_settings.gigachat.access_token = (await resp.json())["access_token"]
        except Exception:
            settings.api_settings.gigachat.access_token = None
