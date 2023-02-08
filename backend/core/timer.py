from aioredis import Redis

from backend.apps.game.structures import TimerInfo
from typing import Optional


class TimerClient:

    def __init__(self, redis: Redis, ttl: int = 40):
        self.redis = redis
        self.ttl = ttl

    async def exists(self, hash_key: str, key: str) -> bool:
        return await self.redis.hexists(hash_key, key)

    async def delete_hash(self, hash_key: str):
        await self.redis.delete(hash_key)

    async def all_sessions_closed(self, hash_key: str) -> bool:
        return bool(await self.redis.hlen(hash_key))

    async def get_timer_info(self, hash_key: str, key: str) -> Optional[TimerInfo]:
        data = await self.redis.hget(hash_key, key)
        return TimerInfo.parse_raw(data) if data else None

    async def start_session(self, hash_key: str, key: str, data: TimerInfo) -> int:
        return await self.redis.hsetnx(hash_key, key, data.json())

    async def close_session(self, hash_key: str, key: str):
        await self.redis.hdel(hash_key, key)
