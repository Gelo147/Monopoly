class Card:
	def __init__(self,card_type,text,value):
		#takes in a predefined card type, text to display and refers to some space or amount of money
		self._type = card_type
		self._text = text
		self._value = value

	def getType(self):
		return self._type

	def getValue(self):
		return self._value

	def getText(self):
		return self._text