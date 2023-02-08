from enum import Enum


class CommandTypes(str, Enum):
    GAME = "game"
    TABLE = "table"


class BaseCommand(str, Enum):
    pass


class TableCommand(BaseCommand):
    INFO = "info"


class GameCommand(BaseCommand):
    BET = "bet"
    FOLD = "fold"
    RAISE = "raise"
    CHECK = "check"
