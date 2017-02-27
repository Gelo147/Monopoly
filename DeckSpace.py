from Space import Space
from collections import deque
class DeckSpace(Space):
	def __init__(self,text,deck):
		#deck space is a space which contains a deck of cards which can be drawn from
		super().__init__("DECK",text)
		self._deck = deque(deck)

	def drawCard(self):
		#remove card from top of deck and put same card back to the bottom, return card
		topcard = self._deck.pop()
		self._deck.appendleft(topcard)
		return topcard