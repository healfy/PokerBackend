from enum import Enum
from typing import List


class GameState(str, Enum):
    INITIAL = "initial"
    START = "start"
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"
    FINISHED = "finished"


class CardSuit(str, Enum):
    SPADES = "SPADES",
    DIAMONDS = "DIAMONDS",
    HEARTS = "HEARTS",
    CLUBS = "CLUBS",

    @classmethod
    def get_image(cls, suit: 'CardSuit'):
        _mapping = {
            cls.SPADES: "♠︎",
            cls.DIAMONDS: "♦",
            cls.HEARTS: "♥",
            cls.CLUBS: "♣",
        }
        return _mapping[suit]


class Combinations(str, Enum):
    ROYAL_FLUSH = "ROYAL FLUSH"
    STREET_FLUSH = "STREET FLUSH"
    FOUR_OF_KIND = "FOUR OF KIND"


class CardRank(str, Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "T"
    JACKET = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

    @classmethod
    def get_strength(cls, rank: "CardRank") -> int:
        strength_mapping = {
            cls.TWO: 2,
            cls.THREE: 3,
            cls.FOUR: 4,
            cls.FIVE: 5,
            cls.SIX: 6,
            cls.SEVEN: 7,
            cls.EIGHT: 8,
            cls.NINE: 9,
            cls.TEN: 10,
            cls.JACKET: 11,
            cls.QUEEN: 12,
            cls.KING: 13,
            cls.ACE: 14
        }
        return strength_mapping[rank]


SUITS: List[CardSuit] = [CardSuit.CLUBS, CardSuit.HEARTS, CardSuit.DIAMONDS, CardSuit.SPADES]
RANKS: List[CardRank] = [
    CardRank.TWO, CardRank.THREE, CardRank.FOUR, CardRank.FIVE,
    CardRank.SEVEN, CardRank.EIGHT, CardRank.NINE, CardRank.TEN, CardRank.JACKET, CardRank.SIX,
    CardRank.QUEEN, CardRank.KING,
    CardRank.ACE
]
