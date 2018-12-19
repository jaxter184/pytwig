# No clue what this is or what it is used for. I just made a data structure to match what was in the files.

class Route:
	type = 'route'
	def __init__(self, num, str):
		self.type = 'route'
		self.data = {"num":num, "str":str}

	def __repr__(self):
	    return self.__str__()

	def __str__(self):
		return "Route: s{}, n{}".format(self.data["num"], self.data["str"])
