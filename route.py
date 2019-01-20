# No clue what this is or what it is used for. I just made a data structure to match what was in the files.
# int is probably a reference to an existing object

class Route:
	type = 'route'
	def __init__(self):
		self.type = 'route'
		self.data = {}

	def __iter__(self):
		yield 'type', self.type
		yield 'data', self.type

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return "Route: {}".format(self.data)

	def show(self):
		print(str(self.__dict__()).replace(', ', ',\n').replace('{', '{\n').replace('}', '\n}'))
