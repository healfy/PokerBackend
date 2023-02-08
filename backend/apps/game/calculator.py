from typing import List
from backend.apps.game.structures import CardSuit, PokerCard, PokerDeck, CardRank
from collections import Counter


def get_hand_power(hand: List[PokerCard]):
    # Create a list to store the numerical values of the cards
    values: List[int] = [CardRank.get_strength(card.rank) for card in hand]
    # Create a list to store the suits of the cards
    suits: List[CardSuit] = [card.suit for card in hand]
    # Sort the values and suits in descending order
    values.sort(reverse=True)
    suits.sort()
    if values == [14, 5, 4, 3, 2]:
        values = [5, 4, 3, 2, 1]
    # Create a Counter object to count the occurrences of each value
    counter = Counter(values)
    # Check for a straight flush (5 cards in sequence with the same suit)
    if values == list(range(values[0], values[0]-5, -1)) and len(set(suits)) == 1:
        power = 900 + values[0]
    # Check for four of a kind
    elif counter.most_common(1)[0][1] == 4:
        power = 800 + counter.most_common(1)[0][0]
    # Check for a full house (3 cards of one value and 2 cards of another value)
    elif counter.most_common(2)[0][1] == 3 and counter.most_common(2)[1][1] == 2:
        power = 700 + counter.most_common(2)[0][0]
    # Check for a flush (5 cards of the same suit)
    elif len(set(suits)) == 1:
        power = 600 + sum(values)
    # Check for a straight (5 cards in sequence)
    elif values == list(range(values[0], values[0]-5, -1)):
        power = 500 + values[0]
    # Check for three of a kind
    elif counter.most_common(1)[0][1] == 3:
        power = 400 + counter.most_common(1)[0][0]
    # Check for two pairs
    elif counter.most_common(2)[0][1] == 2 and counter.most_common(2)[1][1] == 2:
        power = 300 + counter.most_common(2)[0][0] + counter.most_common(2)[1][0]
    # Check for one pair
    elif counter.most_common(1)[0][1] == 2:
        power = 200 + counter.most_common(1)[0][0]
    # Otherwise, use the value of the highest card
    else:
        power = 100 + values[0]
    return power


deck = PokerDeck()
hand = [deck.get_card() for _ in range(5)]
result = get_hand_power(hand)
print()
