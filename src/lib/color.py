import struct
from src.lib import util

class Color():
	"""Data storage object that contains parameters for Bitwig colors.
	"""
	def __init__(self, rd, gr, bl, al):
		"""Initialization for Color object

		Reads color and alpha values and stores them in an array. If alpha value is 1.0, it is ignored and data array is length 3.

		Args:
			rd (float): Red
			gr (float): Green
			bl (float): Blue
			al (float): Alpha
		"""
		self.type = 'color'
		self.data = [rd, gr, bl, al]
		if (al == 1.0):
			self.data = self.data[:-1]
		return

	def __repr__(self):
	    return self.__str__()

	def __str__(self):
		return "Color: " + str(self.data)

	def encode(self):
		"""Encodes the color object into Bitwig bytecode.

		Returns:
			bytearray: Bitwig bytecode representation of the Color object.
		"""
		output = bytearray(b'')
		count = 0
		for item in self.data:
			flVal = struct.unpack('>I', struct.pack('>f', item))[0]
			output += util.hexPad(flVal,8)
			count += 1
		if count == 3:
			output += struct.pack('>f', 1.0)
		return output
