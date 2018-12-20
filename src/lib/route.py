# No clue what this is or what it is used for. I just made a data structure to match what was in the files.

class Route:
	type = 'route'
	def __init__(self):
		self.type = 'route'
		self.data = {}

	def __repr__(self):
	    return self.__str__()

	def __str__(self):
		return "Route: {}".format(self.data)
