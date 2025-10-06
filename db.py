import os
import aiomysql
from typing import Optional, Any, Iterable, Mapping
from dotenv import load_dotenv

POOL: aiomysql.Pool | None = None

async def init_pool() -> aiomysql.Pool:
    global POOL
    if POOL:
        return POOL
    POOL = await aiomysql.create_pool(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        db=os.getenv("DB_NAME"),
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
