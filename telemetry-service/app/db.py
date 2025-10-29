from __future__ import annotations

from typing import Any, Dict, Optional

from psycopg.rows import tuple_row
from psycopg.types.json import Json
from psycopg_pool import AsyncConnectionPool


class DB:
    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 10):
        self._dsn = dsn
        self._pool: Optional[AsyncConnectionPool] = AsyncConnectionPool(
            dsn, min_size=min_size, max_size=max_size
        )

    async def connect(self):
        await self._pool.open()

    async def close(self):
        if self._pool:
            await self._pool.close()

    @property
    def pool(self) -> AsyncConnectionPool:
        assert self._pool is not None, (
            "DB pool is not initialized. Call connect() first."
        )
        return self._pool

    async def insert_telemetry(
        self, *, tenant_id: int, device_id: int, key: str, value: Dict[str, Any], ts
    ):
        sql = """
            INSERT INTO public.telemetry_telemetry
            (created_at, updated_at, tenant_id, device_id, key, value, ts)
            VALUES (NOW(), NOW(), %s, %s, %s, %s, %s)
        """
        async with self.pool.connection() as conn:
            async with conn.cursor(row_factory=tuple_row) as cur:
                await cur.execute(sql, (tenant_id, device_id, key, Json(value), ts))
