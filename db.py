import os
import aiomysql
from typing import Optional, Any, Iterable, Mapping
from dotenv import load_dotenv

POOL: aiomysql.Pool | None = None

async def init_pool(host, port, user, passwd, table) -> aiomysql.Pool:
    global POOL
    if POOL:
        return POOL
    host = host or os.getenv("DB_HOST", "127.0.0.1")
    port = port or int(os.getenv("DB_PORT", "3306"))
    user = user or os.getenv("DB_USER")
    passwd = passwd or os.getenv("DB_PASS")
    table = table or os.getenv("DB_TABLE")
    POOL = await aiomysql.create_pool(
        host=host,
        port=port,
        user=user,
        password=passwd,
        db=table,
        minsize=1, maxsize=10, autocommit=True, charset="utf8mb4"
    )
    return POOL

async def close_pool():
    if POOL:
        POOL.close()
        await POOL.wait_closed()

async def fetchall(sql: str, params: Iterable[Any] | Mapping[str, Any] | None = None):
    async with POOL.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql, params or ())
            return await cur.fetchall()

async def fetchone(sql: str, params=None):
    async with POOL.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql, params or ())
            return await cur.fetchone()

async def execute(sql: str, params=None) -> int:
    async with POOL.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params or ())
            return cur.lastrowid
