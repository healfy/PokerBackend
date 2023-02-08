import asyncio
import logging
from asyncio import CancelledError
from sqlalchemy import select


from backend.apps.game.consts import GameState
from backend.apps.game.state import state_cls_by_enum
from backend.apps.game.models import GameHistory
from backend.core.database.repository import PostgresRepository

logger = logging.getLogger(__name__)


class StateManagerTask:

    def __init__(self, repository: PostgresRepository):
        self.repository = repository
        self._run = True

    async def change_states(self):
        async with self.repository.atomic():
            smt = select(GameHistory).where(GameHistory.state.in_([GameState.INITIAL, GameState.FINISHED])).execution_options(yield_per=10)
            async for game_history in await self.repository.session.stream_scalars(smt):
                state_cls = state_cls_by_enum(game_history.state)
                await state_cls(self.repository, game_history.table_id).make_transition()

    async def run(self):
        while self._run:
            try:
                await self.change_states()
                logger.info("change_states task")
                await asyncio.sleep(5)
            except CancelledError:
                logger.info("Stopeed change_states task")
                self._run = False

