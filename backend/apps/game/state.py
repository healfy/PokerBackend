import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Type, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from backend.apps.game.consts import GameState
from backend.apps.game.models import GameHistory
from backend.apps.game.structures import PokerDeck, SeatInfo, PlayerInfo, SixMaxGameInfo
from backend.apps.lobby.consts import TablePositions, SeatStatus, TableLimit
from backend.apps.user.models import User, Wallet
from backend.apps.lobby.models import Tables, Seats
from backend.core.database.repository import PostgresRepository


logger = logging.getLogger(__name__)


class BaseState(ABC):
    id: GameState

    def __init__(self, repository: PostgresRepository, table_id: int):
        self.repository = repository
        self.table_id = table_id

    async def validate(
            self,
            to_state: Type['BaseState'],
            raise_exception=True
    ) -> bool:
        """
        returns True if new state can be set
        """
        valid = self.check_new_state(self.__class__, to_state)
        if raise_exception and not valid:
            raise ValueError(
                f'Сan not update the state {self.__class__}. '
                f'Transition to state {to_state} is prohibited.')
        return valid

    @staticmethod
    def check_new_state(
            from_state: Type['BaseState'],
            to_state: Type['BaseState'],
    ) -> bool:
        return to_state in __STATES_TRANSITION__[from_state]

    async def set(self, to_state: Type['BaseState']):
        logger.info(f"Setting {to_state=} for table {self.table_id}")
        await self.validate(to_state)
        await self.repository.update(GameHistory, {
            "state": to_state.id,
        }, custom_filter=[GameHistory.table_id == self.table_id])

    @abstractmethod
    async def make_transition(self):
        pass


class InitialGameState(BaseState):
    id = GameState.INITIAL

    async def make_transition(self):
        table: Tables = await self.repository.get_table(self.table_id)
        if len([seat for seat in table.seats if seat.status != SeatStatus.FREE]) >= 2:
            return await self.set(StartGameState)
        logger.info(f"Table {self.table_id=} is not ready to start game")


class StartGameState(BaseState):
    id = GameState.START

    def __init__(self, repository: PostgresRepository, table_id: int):
        super().__init__(repository, table_id)
        self.cards_generator = PokerDeck()

    @staticmethod
    def parse_blinds(limit: TableLimit) -> List[Decimal]:
        return [Decimal(value) for value in limit.split('/')]

    async def set_blind(self, seat_id: int, user_id: int, value: Decimal, position: TablePositions):
        await self.repository.update(Seats,
                                     custom_filter=[Seats.id == seat_id],
                                     values={'position': position, "status": SeatStatus.WAITING})
        await self.repository.update(Wallet,
                                     values={'amount': Wallet.amount - value},
                                     custom_filter=[Wallet.user_id == user_id])

    @staticmethod
    def get_sb_seat_number(seats: List[Seats]) -> Optional[int]:
        for ind, seat in enumerate(seats):
            if seat.position == TablePositions.SMALL_BLIND:
                return ind
        return None

    @staticmethod
    def is_last_element(seats: List, seat: Seats):
        return seats[-1] == seat

    async def make_transition(self):
        async with self.repository.atomic():
            table: Tables = await self.repository.get_table(self.table_id)
            sb, bb = self.parse_blinds(table.limit)
            seat_data = {}
            seats = table.seats
            sb_seat_index = self.get_sb_seat_number(table.seats)
            if not sb_seat_index or len(seats) - 1 == sb_seat_index:
                sb_seat, bb_seat = seats[:2]
                next_seat = seats[2:][0] if seats[2:] else sb_seat
            else:
                sb_seat = seats[sb_seat_index + 1]
                bb_seat = seats[0] if self.is_last_element(seats, sb_seat) else seats[sb_seat_index + 2]
                next_seat = seats.index(bb_seat) + 1 if self.is_last_element(seats, bb_seat) else seats[0]
            await self.set_blind(sb_seat.id, sb_seat.user_id, sb, TablePositions.SMALL_BLIND)
            await self.set_blind(bb_seat.id, bb_seat.user_id, bb, TablePositions.BIG_BLIND)
            await self.repository.update(Seats,
                                         custom_filter=[Seats.id == next_seat.id],
                                         values={"status": SeatStatus.IN_GAME, 'position': TablePositions.UNKNOWN})
            await self.repository.update(Seats,
                                         custom_filter=[
                                             Seats.id.not_in([next_seat.id, sb_seat.id, bb_seat.id]),
                                             Seats.status != SeatStatus.FREE],
                                         values={"status": SeatStatus.WAITING}
                                         )

            for seat in seats:
                seat_data[f'seat_{seat.number}'] = SeatInfo(
                    id=seat.id,
                    position=seat.position,
                    status=seat.status,
                    player=None if not seat.user else PlayerInfo(
                        id=seat.user.id,
                        name=seat.user.email,
                        stack=seat.user.wallet.amount,
                        hand=[self.cards_generator.get_card(), self.cards_generator.get_card()],
                    )
                )

            data = SixMaxGameInfo(
                small_blind=sb,
                big_blind=bb,
                bank=sb + bb,
                states_flow=[GameState.START],
                deck=self.cards_generator.deck,
                flop=[self.cards_generator.get_card(), self.cards_generator.get_card(), self.cards_generator.get_card()],
                turn=[self.cards_generator.get_card()],
                river=[self.cards_generator.get_card()],
                **seat_data,
            )
            logger.info(f'Started table {self.table_id} with {data=}')
            await self.repository.update(GameHistory, {
                "data": data.json(),
            }, custom_filter=[GameHistory.table_id == self.table_id])
            await self.set(PreFlopState)


class PreFlopState(BaseState):
    id = GameState.PREFLOP


class FlopState(BaseState):
    id = GameState.FLOP


class TurnState(BaseState):
    id = GameState.TURN


class RiverState(BaseState):
    id = GameState.RIVER


class ShowDownState(BaseState):
    id = GameState.SHOWDOWN


class FinishedState(BaseState):
    id = GameState.FINISHED


def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]


def state_cls_by_enum(state: GameState) -> Type[BaseState]:
    __CLASSES__ = {c.id: c for c in all_subclasses(BaseState)}
    return __CLASSES__[state]


__STATES_TRANSITION__: Dict[Type[BaseState], List[Type[BaseState]]] = {
    InitialGameState: [StartGameState],
    StartGameState: [PreFlopState],
    PreFlopState: [FlopState, FinishedState],
    FlopState: [TurnState, FinishedState],
    TurnState: [RiverState, FlopState],
    RiverState: [ShowDownState, FinishedState],
    FinishedState: [InitialGameState]
}
