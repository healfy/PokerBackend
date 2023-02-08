from enum import Enum, IntEnum


class SeatStatus(str, Enum):
    FREE = 'free'
    RESERVED = 'reserved'
    IN_GAME = 'in_game'
    PLAYED = "played"
    WAITING = "waiting"


class TablePositions(str, Enum):
    UNKNOWN = 'unknown'
    SMALL_BLIND = 'small_blind'
    BIG_BLIND = 'big_blind'


class SeatNumber(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6


class TableLimit(str, Enum):
    MICRO_1 = "0.1/0.2"
    MICRO_2 = "0.2/0.5"
