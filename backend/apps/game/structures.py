import random
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, conlist
from typing import List, Optional
import itertools

from backend.apps.game.commands.consts import GameCommand
from backend.apps.game.consts import  GameState
from backend.apps.lobby.consts import TablePositions, SeatStatus
from backend.apps.game.consts import CardRank, CardSuit, RANKS, SUITS


class HandPower(BaseModel):
    value: int
    combination: str


class TimerInfo(BaseModel):
    start_time: datetime
    end_time: datetime


class RoundSession(BaseModel):
    user_id: int
    seat_id: int
    table_id: int

    @property
    def key(self) -> str:
        return f"SeatId-{self.seat_id}::UserId-{self.user_id}"

    @property
    def hash_key(self) -> str:
        return f'{self.table_id}::TableId'


class PokerCard(BaseModel):
    suit: CardSuit
    rank: CardRank

    def __hash__(self):
        return hash([self.rank, self.suit])

    def __eq__(self, other: "PokerCard") -> bool:
        return self.rank == other.rank and self.suit == other.suit


class PokerDeck:
    deck: List[PokerCard]

    def __init__(self):
        self.deck = [PokerCard(suit=suit, rank=rank) for suit, rank in itertools.product(SUITS, RANKS)]
        random.shuffle(self.deck)
        self.indexes = set()

    def get_card(self) -> PokerCard:
        index = self.deck.index(random.choice(self.deck))
        while index in self.indexes:
            index = self.deck.index(random.choice(self.deck))
        self.indexes.add(index)
        return self.deck[index]


HAND = conlist(PokerCard, max_items=2, min_items=2, unique_items=True)
FLOP = conlist(PokerCard, max_items=3, min_items=0, unique_items=True)
TURN = conlist(PokerCard, max_items=1, min_items=0)
RIVER = conlist(PokerCard, max_items=1, min_items=0)
WINNER_COMBO = conlist(PokerCard, max_items=5, min_items=2, unique_items=True)


class Action(BaseModel):
    command: GameCommand
    amount: Optional[Decimal]


class PlayerInfo(BaseModel):
    id: int
    name: str
    hand: HAND
    stack: Decimal
    actions: List[Action] = Field(default_factory=list)


class SeatInfo(BaseModel):
    id: int
    player: Optional[PlayerInfo]
    position: TablePositions
    status: SeatStatus


class SixMaxGameInfo(BaseModel):
    deck: List[PokerCard]
    small_blind:  Decimal
    big_blind: Decimal
    bank: Decimal
    states_flow: List[GameState]
    flop: FLOP = Field(default_factory=list)
    turn: TURN = Field(default_factory=list)
    river: RIVER = Field(default_factory=list)
    winner_combo: WINNER_COMBO = Field(default_factory=list)
    winner: Optional[PlayerInfo]
    seat_1: SeatInfo
    seat_2: SeatInfo
    seat_3: SeatInfo
    seat_4: SeatInfo
    seat_5: SeatInfo
    seat_6: SeatInfo

    class Config:
        json_encoders = {Decimal: str}
