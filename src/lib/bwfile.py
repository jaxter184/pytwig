# All classes regarding bitwig files
from src.lib import objects
from collections import OrderedDict
from src.lib.util import *


class BW_File:
	bytecode = None
	def __init__(self, type = None):
		if type == None:
			self.header = ''
			self.meta = objects.BW_Meta(None)
			self.contents = objects.Contents(None)
			return
		self.header = 'BtWgXXXXX'
		self.meta = objects.BW_Meta(type)
		self.meta.data = OrderedDict(sorted(self.meta.data.items(), key=lambda t: t[0])) # Sorts the dict. CLEAN: maybe put this somewhere else?
		self.contents = None

	def __str__(self):
		return "File: " +  self.meta.data['device_name']

	def set_header(self, value):
		"""Sets self.header, checking for validity before doing so.

		Args:
			value (str): Header string to be checked and written

		Returns:
			BW_File: self is returned so the function can be daisy-chained
		"""
		if not (value[:4] == 'BtWg' and value[4:].isdigit() and len(value) == 40):
			raise TypeError('"{}" is not a valid header'.format(value))
		else:
			self.header = value
		return self

	def set_contents(self, value):
		"""Sets self.contents, checking very superficially for validity before doing so.

		Args:
			value (BW_Object): Bitwig object to be set as this object's contents

		Returns:
			BW_File: self is returned so the function can be daisy-chained
		"""
		if not isinstance(value, BW_Object):
			raise TypeError('"{}" is not an atom'.format(value))
		else:
			self.contents = value
		return self

	def set_uuid(self, value):
		self.contents.data['device_UUID'] = value
		self.meta.data['device_uuid'] = value
		self.meta.data['device_id'] = value
		return self

	def set_description(self, value):
		self.meta.data['device_description'] = value
		self.contents.data['description'] = value
		return self

	def serialize(self):
		objects.serialized = [None]
		output = self.header[:11] + '1' + self.header[12:]
		output += self.meta.serialize()
		output += '\n'
		objects.serialized = [None]
		output += self.contents.serialize()
		return output

	def encode(self):
		bytecode = BW_Bytecode()
		bytecode.write(bytearray(self.header[:11] + '2' + self.header[12:], "utf-8"))
		self.meta.encode_to(bytecode)
		bytecode.write(bytearray('\n', "utf-8"))
		self.contents.encode_to(bytecode)
		return bytecode

	def decode(self, bytecode):
		self.header = bytecode.read_str(40)
		if self.header[:4] == 'BtWg' and int(self.header[4:40], 16):
			if self.header[11] == '2':
				self.meta.decode(bytecode)
				while bytecode.read(1) == 0x20: #TODO: change to != 0x0a
					pass
				if meta_only:
					return;
				self.contents = BW_Object.decode(bytecode)
			elif self.header[11] == '1':
				raise TypeError('"' + self.header + '" is a json typed file')
				'''
			elif self.header[11] == '0':
				bytecode = self.meta.decode(bytecode[40:])
				while bytecode[0] == 0x20:
					bytecode = bytecode[1:]
				bytecode = bytecode[1:]
				'''
			else:
				raise TypeError('"' + self.header + '" is not a valid type')
		else:
			raise TypeError('"' + self.header + '" is not a valid header')

	def write(self, path, json = False):
		from src.lib import fs
		output = self.encode()
		fs.write_binary(path, output)

	def export(self, path):
		from src.lib import fs
		fs.write(path, self.serialize().replace('":', '" :'))

	def read(self, path, raw = False, meta_only = False):
		from src.lib import fs
		self.bytecode = BW_Bytecode().set_contents(fs.read_binary(path))
		self.bytecode.meta_only = meta_only
		self.bytecode.raw = raw
		self.decode(self.bytecode)

class BW_Bytecode:
	contents = b''
	contents_len = 0
	position = 0
	string_mode = "PREPEND_LEN"
	meta_only = False
	raw = False
	obj_list = [None]
	reading_meta = True

	def __init__(self, contents = ''):
		if contents != '':
			self.contents = contents

	def set_contents(self, contents):
		self.contents = contents
		self.contents_len = len(contents)
		self.position = 0
		return self

	def set_string_mode(self, new_string_mode):
		self.string_mode = new_string_mode

	def reset_pos(self):
		self.position = 0

	def read(self, length = 1):
		output = self.peek(length)
		self.position += length
		return output

	def read_str(self, length = None):
		if length != None:
			output = self.peek(length)
			self.position += length
			return str(output, "utf-8")
		else:
			if self.string_mode == "PREPEND_LEN":
				str_len = self.read_int()
				char_enc = False #false:utf-8, true:utf-16
				if (str_len & 0x80000000):
					str_len &= 0x7fffffff
					char_enc = True
				if (str_len > 100000):
					raise TypeError('String is too long')
				return self.read_str(str_len)
			elif self.string_mode == "NULL_TERMINATED":
				output = b''
				while self.peek(1) != 0x00:
					output += self.read()
				self.increment_position(1) # increment position to pass over null
				return str(output, "utf-8")

	def read_int(self, len = 4):
		return btoi(self.read(len))

	def write(self, append):
		if isinstance(append, bytearray):
			contents += append
		elif isinstance(append, string):
			contents += bytearray.fromhex(a)
		self.contents_len = len(contents)

	def write_str(self, string):
		if string_mode == "PREPEND_LEN":
			contents += bytearray.fromhex(hexPad(len(string), 8))
			contents.extend(string.encode('utf-8'))
		elif string_mode == "NULL_TERMINATED":
			contents.extend(string.encode('utf-8'))
			contents += bytearray([0])

	def increment_position(self, amt):
		self.position = self.position + amt
		if self.position + length > self.contents_len:
			raise EOFError("End of file")

	def peek(self, length):
		if self.position + length > self.contents_len:
			raise EOFError("End of file")
		return self.contents[self.position:self.position+length]
