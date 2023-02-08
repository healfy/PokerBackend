import logging
from backend.core.service import AbstractService
from backend.core.timer import TimerClient
from backend.apps.game.structures import TimerInfo, RoundSession
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class BiddingService(AbstractService):

    def __init__(self, timer_client: TimerClient, ttl: int = 30):
        self.timer_client = timer_client
        self.deviation = 1  # sec
        self.ttl = ttl

    async def start_round(self, data: RoundSession):
        now = datetime.now()
        logger.info(f"Starting round for {data.hash_key}, {data.key}")
        result = await self.timer_client.start_session(
            data.hash_key, data.key, TimerInfo(start_time=now, end_time=now + timedelta(seconds=self.ttl + self.deviation))
        )
        if not result:
            logger.error("Duplicate key error")
            raise ValueError
        logger.info(f"Started round for {data.hash_key}, {data.key}")

    async def end_round(self, data: RoundSession):
        logger.info(f"Ending round for {data.hash_key}, {data.key}")
        await self.timer_client.close_session(data.hash_key, data.key)
        logger.info(f"Ended round for {data.hash_key}, {data.key}")

    async def round_is_expired(self, data: RoundSession) -> bool:
        logger.info(f"Check if round for {data.hash_key}, {data.key} is expired")
        data = await self.timer_client.get_timer_info(data.hash_key, data.key)
        return True if not data else (data.end_time - datetime.now()).seconds < self.ttl + self.deviation
