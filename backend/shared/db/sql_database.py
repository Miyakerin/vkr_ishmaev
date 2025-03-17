import copy
import datetime
import json
import typing as tp
import uuid
from asyncio import current_task
from itertools import chain

import asyncio
import sqlalchemy as sa
from sqlalchemy import text, TextClause
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker, \
    async_scoped_session
import re


def serialize_json(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError("Type not serializable")


class DBError(Exception):
    ...


class DataBaseSession:
    def __init__(self, db_params: tp.Dict[str, tp.Any]) -> None:
        self.db_params = db_params
        self.__engine = None
        self.__session = None

    @property
    async def engine(self) -> AsyncEngine:
        if self.__engine is None:
            self.__engine = create_async_engine(**self.db_params)
        return self.__engine

    @property
    async def session(self) -> AsyncSession:
        if not self.__session:
            self.__session = async_scoped_session(
                session_factory=async_sessionmaker(
                    bind=await self.engine,
                    autocommit=False,
                    autoflush=False,
                    expire_on_commit=False,
                    class_=AsyncSession
                ),
                scopefunc=current_task
            )
        return self.__session

    async def execute(self, *args, **kwargs) -> tp.Any:
        return await (await self.session).execute(*args, **kwargs)

    async def commit(self) -> None:
        if self.__session:
            await self.__session.commit()

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()

    async def rollback(self) -> None:
        if self.__session:
            await self.__session.rollback()

    async def run_sync(self, func: tp.Callable, *args, **kwargs) -> tp.Any:
        async with (await self.engine).begin() as conn:
            await conn.run_sync(func, *args, **kwargs)

    async def query(self, query: tp.Union[str, TextClause], params=None):
        if isinstance(query, str):
            query = text(query)
        async with await self.session as session:
            result = await session.execute(query, params=params)
            response = [dict(r._mapping) for r in result]
        return response


# noinspection SqlResolve
class Database:
    column_types_cache = []

    def __init__(self, engines_params: list[dict[str, tp.Union[int, str, bool]]]):
        self.__sessions: dict[str, tp.Optional[DataBaseSession]] = {}
        self.__engines_params = {}
        for engine_params in engines_params:
            name = engine_params.pop("name")
            self.__engines_params[name] = engine_params

    @property
    async def sessions(self) -> dict[str, tp.Optional[DataBaseSession]]:
        if not self.__sessions:
            for db_name, engine_params in self.__engines_params.items():
                self.__sessions[db_name] = DataBaseSession(
                    db_params=engine_params
                )
        return self.__sessions

    async def run_sync_batch(self, func: tp.Callable, *args, **kwargs):
        for db_name, session in (await self.sessions).items():
            await session.run_sync(func, *args, **kwargs)

    async def run_sync(self,db_name: str, func: tp.Callable, *args, **kwargs):
        current_session = (await self.sessions)[db_name]
        await current_session.run_sync(func, *args, **kwargs)

    async def get_engines(self) -> dict[str, AsyncEngine]:
        mapping = {}
        for db_name, session in (await self.sessions).items():
            mapping[db_name] = await session.engine
        return mapping

    async def get_scoped_session(self, db_name: str) -> DataBaseSession:
        return (await self.sessions)[db_name]

    async def get_column_type_cache(self, db_name: str, table_name: str):
        column_type = list(
            filter(
                lambda x: x['db_name'] == db_name and x['table_name'] == table_name,
                self.column_types_cache
            )
        )
        if column_type:
            column_type = column_type[0]['structure']
        return column_type

    async def set_column_type_cache(self, db_name, table_name, structure):
        self.column_types_cache.append(
            {
                'db_name': db_name,
                'table_name': table_name,
                'structure': structure
            }
        )

    async def get_column_types(self, table_name, db_name):
        column_types = await self.get_column_type_cache(db_name=db_name, table_name=table_name)
        if not column_types:
            column_types = await self.query(
                f'''
                        SELECT
                            column_name,
                            data_type,
                            character_maximum_length,
                            udt_name
                        FROM
                            information_schema.columns
                        WHERE
                            table_name = '{table_name}';
                    ''',
                db_name=db_name
            )
            self.set_column_type_cache(db_name=db_name, table_name=table_name, structure=column_types)
        return column_types

    async def query(
            self,
            query: str,
            db_name: str,
            params: dict = None,
            pagination: list[int, int] = None,
    ):
        if params is None:
            params = dict()

        # Выбор Базы Данных
        session = await self.get_scoped_session(db_name=db_name)

        # - pagination
        if pagination:
            pagination_filter = ''

            if pagination[0] is not None and pagination[1] is not None:
                pagination_filter = f' LIMIT {pagination[1] - pagination[0] + 1} OFFSET {pagination[0] - 1}'

            query += pagination_filter

        # response = await session.query(query=query, params=params)
        try:
            response = await session.query(
                query=text(query),  # .execution_options(autocommit=autocommit),
                params=params
            )
        except sa.exc.ResourceClosedError:
            response = []
        except Exception as e:
            raise e

        return response

    async def insert(self, **kwargs):
        return await self.insert_update(insert=True, update=False, **kwargs)

    async def update(self, **kwargs):
        return await self.insert_update(insert=False, update=True, **kwargs)

    async def insert_update(self, table_name, values, db_name, constraint=None,
                            insert=True, update=True, returning=None, return_query=False,
                            add_query=None, query_select='*'):
        """
        если returning != None : ключ для получения возвращаемого значения ['returning_value']  str
        constraint - значения по которым нужно обновить данные str|list
        """

        values = copy.deepcopy(values)
        if not values:
            return {'code': 0, 'message': 'Данные не были переданы'}

        # Проверка параметров и конвертации
        if isinstance(constraint, str):
            constraint = [constraint]

        if constraint:
            constraint = [str(x).lower() for x in constraint]

        if not update and not insert:
            raise DBError('Не включен ни update, ни insert')

        if update is True and constraint is None:
            raise DBError('Не задан constraint для update')

        if isinstance(returning, str):
            returning = [returning]

        if isinstance(values, dict):
            values = [values]

        for row_ind, value_row in enumerate(values):
            values[row_ind] = {k.lower(): v for k, v in value_row.items()}

        # Все используемые ключи - названия столбцов
        all_values_keys = set(chain.from_iterable(values))
        if constraint is not None:
            all_values_keys = all_values_keys | set(constraint)
        all_values_keys = list(all_values_keys)
        all_values_keys = [str(x).strip().lower() for x in all_values_keys]
        used_columns = []

        # Получение данных о столбцах через алхимию
        column_types = await self.get_column_types(db_name=db_name, table_name=table_name)

        columns_data = {x['column_name']: x for x in column_types}
        udt_names = {x['column_name']: x['udt_name'] for x in column_types}
        column_types = {x['column_name']: x['data_type'] for x in column_types}
        for col_name in all_values_keys:
            col_name = str(col_name).strip().lower()
            col_type = sa.String
            if column_types.get(col_name) is None and column_types.get(col_name.lower()) is None:
                raise DBError(f'Столбец "{col_name}" не задан')
            col_type_name = column_types[col_name].lower()

            if 'integer' in col_type_name:
                col_type = sa.Integer
            if 'bigint' in col_type_name:
                col_type = sa.BIGINT
            if 'numeric' in col_type_name or 'double' in col_type_name:
                col_type = sa.Float
            if 'bool' in col_type_name:
                col_type = sa.Boolean

            used_columns.append(sa.column(col_name, col_type))

        # Приведение типа данных CHAR к CHAR(int)
        column_types = {
            k: v if v != 'character' else f'''{v}({columns_data[k]['character_maximum_length']})''' for k, v in
            column_types.items()
        }

        extra_columns = list(set(all_values_keys) - set(column_types.keys()))
        if extra_columns:
            start_text = 'Столбец'
            if len(extra_columns) > 1:
                start_text = 'Столбцы'
            raise DBError(f'''{start_text} {', '.join([
                f'"{x}"' for x in extra_columns
            ])} не заданы в {table_name}''')

        # Формирование пар ключ-значение
        column_types_to_change = dict()
        for val_ind, value in enumerate(values):
            for k in all_values_keys:
                v = value.get(k)
                if type(v) is datetime.datetime:
                    value[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                if type(v) is datetime.date:
                    value[k] = v.strftime('%Y-%m-%d')
                if type(v) is datetime.timedelta:
                    value[k] = str(v)
                if type(v) is dict or type(v) is list:
                    value[k] = json.dumps(v, ensure_ascii=False, default=serialize_json)

                if v is not None:
                    if 'char' in column_types[k].lower():
                        value[k] = str(v)
                    elif 'bool' in column_types[k].lower():
                        value[k] = bool(v)
                    elif 'int' in column_types[k].lower():
                        value[k] = int(v)
                    elif 'array' in column_types[k].lower():
                        value[k] = str(v).replace('[', '{').replace(']', '}')
                        column_types_to_change[k] = udt_names[k]
                    elif 'json' in column_types[k].lower():
                        pass
                    else:
                        value[k] = str(v)

        for k, udt_name in column_types_to_change.items():
            column_types[k] = udt_name

        # Формирование запроса
        query = ''

        # Данные на входе - DATA
        # применение параметризованного построения запроса
        session = await self.get_scoped_session(db_name=db_name)

        values_list = [
            [v[k] for k in all_values_keys] for v in values
        ]
        values_clause = sa.values(
            *used_columns,
            name="DATA",
        ).data(values_list).compile(
            session.engine,
            dialect=sa.dialects.postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        )

        values_clause = re.sub("%%", "%", str(values_clause))
        values_clause = values_clause.replace('\\\\', '\\')

        statement = f"""\
           WITH DATA({', '.join([f'"{k}"' for k in all_values_keys])})  AS (
           {values_clause}
           ),

           """
        query += statement

        # Обновление данных по совпадающим constraint
        if update:
            query += f'\nUPD AS ('
            query += f'''
                   UPDATE {table_name} as t
                   SET
                       {','.join([f"{k} = d.{k}::{column_types[k]}" for k in all_values_keys if k not in constraint])}

                   FROM DATA AS d
                   '''

            query += f'''
                   WHERE {' AND '.join([f"(t.{k} IS NOT DISTINCT FROM d.{k}::{column_types[k]})" for k in constraint])}
                   '''

            if returning:
                returning_str = ', '.join([f"t.{x}" for x in returning])
                query += f' \nRETURNING {returning_str}'

            query += '\n)\n'
            if insert:
                query += ','
            query += '\n\n'

        # Вставка данных, если не указан constraint - принудительно
        # Иначе при отсутствии совпадающих по constraint
        if insert:
            query += f'''\nINS AS (\n'''
            query += f'''
               INSERT
               INTO    {table_name} ({', '.join([f'"{k}"' for k in all_values_keys])})

               SELECT {', '.join([f'd.{k}::{column_types[k]}' for k in all_values_keys])}
               FROM DATA d
               '''

            if constraint:
                query += f'''
                       WHERE NOT EXISTS (SELECT 1
                       FROM {table_name} as t2
                       WHERE 
                           {' AND '.join([f"(t2.{k} IS NOT DISTINCT FROM d.{k}::{column_types[k]})" for k in constraint])}
                       )
                   '''

            if returning:
                returning_str = ', '.join(returning)
                query += f' \nRETURNING {returning_str}'

            query += '\n)\n'

        if returning:
            query += f'\n SELECT {query_select} FROM ('
            if update:
                query += f'''\nSELECT * FROM UPD'''
            if update and insert:
                query += '''\nUNION'''
            if insert:
                query += f'''\nSELECT * FROM INS'''

            query += ') as t\n\n'
        else:
            query += f'''\nSELECT; '''

        if add_query:
            query += str(add_query)

        if return_query:
            return query

        try:
            response = await self.query(query, db_name=db_name)
        except Exception as e:
            raise DBError(f'Ошибка вставки значения в таблицу {table_name}: {str(e)}')

        primary_key_value = None

        if returning is not None:
            response = [x for x in response]

            if len(response) != 0:
                primary_key_value = response[0]
                if len(returning) == 1:
                    primary_key_value = primary_key_value.get(returning[0])
        else:
            response = []

        return {
            'code': 1,
            'message': f'Таблица {table_name} обновлена',
            'returning_value': primary_key_value,
            'returning': response
        }


class DbDependency:
    def __init__(self, engines_params: list[dict[str, tp.Union[int, str, bool]]]):
        self.db = Database(engines_params)

    async def __call__(self) -> Database:

        try:
            yield self.db
            to_commit = []
            for db_name, session in (await self.db.sessions).items():
                to_commit.append(session.commit())
            if to_commit:
                await asyncio.gather(*to_commit)
        except Exception as e:
            to_rollback = []
            for db_name, session in (await self.db.sessions).items():
                to_rollback.append(session.rollback())
            if to_rollback:
                await asyncio.gather(*to_rollback)
            raise e
        finally:
            to_close = []
            for db_name, session in (await self.db.sessions).items():
                to_close.append(session.close())
            if to_close:
                await asyncio.gather(*to_close)
