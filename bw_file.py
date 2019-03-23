# All classes used by all Bitwig files
from collections import OrderedDict
from pytwig.src.lib import util
from pytwig import bw_object


class BW_File:
	def __init__(self, type = None):
		#self.num_spaces = 0
		self.bytecode = None
		if type == None:
			self.header = ''
			self.meta = BW_Meta(None)
			self.contents = None
			return
		self.header = 'BtWgXXXXX'
		self.meta = BW_Meta('application/bitwig-' + type)
		self.contents = None

	def __str__(self):
		return "File"

	def __iter__(self):
		yield "header", self.header
		yield "meta", self.meta
		yield "contents", self.contents

	def show(self):
		print(str(self.__dict__()).replace(', ', ',\n').replace('{', '{\n').replace('}', '\n}'))

	def set_header(self, value):
		"""Sets self.header, checking for validity before doing so.

		Args:
			value (str): Header string to be checked and written

		Returns:
			BW_File: self is returned so the function can be daisy-chained
		"""
		if not (value[:4] == 'BtWg' and int(value[4:],16) and len(value) == 40):
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

	def get_contents(self):
		return self.contents

	def set_uuid(self, value):
		self.contents.data['device_UUID'] = value
		self.meta.data['device_uuid'] = value
		self.meta.data['device_id'] = value
		return self

	def set_description(self, value):
		self.meta.data['device_description'] = value
		#self.contents.data['description'] = value
		return self

	def set_version(self, value):
		self.meta.data['application_version_name'] = value
		return self

	def serialize(self):
		bw_object.serialized = [None]
		output = self.header[:11] + '1' + self.header[12:]
		output += self.meta.serialize()
		output += '\n'
		bw_object.serialized = [None]
		output += self.contents.serialize()
		return output

	def encode_to(self, bytecode):
		if bytecode.string_mode == "PREPEND_LEN":
			str_byte = '2'
		elif bytecode.string_mode == "NULL_TERMINATED":
			str_byte = '0'
		elif bytecode.string_mode == None:
			str_byte = self.header[11]
			bytecode.set_string_mode(str_byte)
		else:
			raise SyntaxError("Invalid string mode")
		bytecode.write(bytes(self.header[:11] + str_byte + self.header[12:], "utf-8"))
		self.meta.encode_to(bytecode)
		#bytecode.write(bytes(' '*self.num_spaces , "utf-8")) # for debug purposes
		bytecode.write(bytes('\n', "utf-8"))
		self.contents.encode_to(bytecode)

	def decode(self, bytecode, meta_only = False):
		if bytecode.contents_len < 40:
			return
		bytecode.set_string_mode()
		self.header = bytecode.read_str(40)
		if self.header[:4] == 'BtWg' and int(self.header[4:40], 16):
			if self.header[11] == '2' or self.header[11] == '0':
				bytecode.set_string_mode(self.header[11])
				self.meta.decode(bytecode)
				while bytecode.read_int(1) != 0x0a:
					pass
				#	self.num_spaces += 1 # for debug purposes
				#print("spaces count: " + str(self.num_spaces))
				if meta_only:
					return;
				self.contents = bw_object.BW_Object.decode(bytecode)
			elif self.header[11] == '1':
				raise TypeError('"' + self.header + '" is a json typed file')
			else:
				raise TypeError('"' + self.header + '" is not a valid type')
		else:
			print(self.header)
			raise TypeError('"' + self.header + '" is not a valid header')

	def set_meta(self):
		pass

	def write(self, path, json = False):
		self.set_meta()
		from pytwig.src.lib import fs
		bytecode = BW_Bytecode()
		self.encode_to(bytecode)
		fs.write_binary(path, bytecode.contents)

	def export(self, path):
		self.set_meta()
		from pytwig.src.lib import fs
		fs.write(path, self.serialize().replace('":', '" :'))

	def read(self, path, raw = True, meta_only = False):
		from pytwig.src.lib import fs
		bytecode = BW_Bytecode().set_contents(fs.read_binary(path))
		bytecode.raw = raw
		bytecode.debug_obj = self
		#self.num_spaces = 0
		self.decode(bytecode, meta_only = meta_only)

# Templates for meta data in the case that the file is created from scratch.
BW_VERSION = '2.4.2'
BW_FILE_META_TEMPLATE = [
	'application_version_name', 'branch', 'creator',
	'revision_id', 'revision_no', 'tags', 'type',]
BW_DEVICE_META_TEMPLATE = [
	'comment',  'device_category', 'device_id' , 'device_name',
	'additional_device_types', 'device_description', 'device_type', 'device_uuid',
	# TODO: find out what these do
	'has_audio_input', 'has_audio_output', 'has_note_input', 'has_note_output',
	'suggest_for_audio_input', 'suggest_for_note_input',]
BW_MODULATOR_META_TEMPLATE = [
	'comment',  'device_category', 'device_id' , 'device_name',
	'device_creator', 'device_type', 'preset_category', 'referenced_device_ids', 'referenced_packaged_file_ids',]
BW_PRESET_META_TEMPLATE = [
	'comment',  'device_category', 'device_id' , 'device_name',
	'device_creator', 'device_type', 'preset_category',
	'referenced_device_ids', "referenced_modulator_ids", "referenced_module_ids", "referenced_packaged_file_ids",]
BW_CLIP_META_TEMPLATE = [
	"beat_length", "bpm", "referenced_packaged_file_ids",
]
class BW_Meta(bw_object.BW_Object):

	def __init__(self, type = None):
		self.data = OrderedDict()

		if type == None:
			return
		self.classname = 'meta'
		# Default headers
		for each_field in BW_FILE_META_TEMPLATE:
			self.data[each_field] = util.get_field_default(each_field)
		if (type == 'application/bitwig-device'):
			for each_field in BW_DEVICE_META_TEMPLATE:
				self.data[each_field] = util.get_field_default(each_field)
		elif (type == 'application/bitwig-modulator'):
			for each_field in BW_MODULATOR_META_TEMPLATE:
				self.data[each_field] = util.get_field_default(each_field)
		elif (type == 'application/bitwig-preset'):
			for each_field in BW_PRESET_META_TEMPLATE:
				self.data[each_field] = util.get_field_default(each_field)
		elif (type == 'application/bitwig-note-clip'):
			for each_field in BW_CLIP_META_TEMPLATE:
				self.data[each_field] = util.get_field_default(each_field)
		else:
			raise TypeError('Type "' + type + '" is an invalid application type')
		self.data['application_version_name'] = BW_VERSION
		self.data['type'] = type
		# Placeholder
		self.data = OrderedDict(sorted(self.data.items(), key=lambda t: t[0])) # Sorts the dict

	def encode_to(self, bytecode):
		bytecode.write('00000004')
		bytecode.write_str('meta')
		for each_field in self.data:
			bytecode.write('00000001')
			bytecode.write_str(each_field)
			self.encode_field(bytecode, each_field)
		bytecode.write('00000000')

	def decode(self, bytecode):
		if not bytecode.reading_meta:
			raise SyntaxError("BW_Bytecode in wrong read mode")
		if bytecode.read(4) != bytes([0,0,0,4]):
			raise TypeError()
		self.classname = bytecode.read_str()
		while bytecode.peek(4) != bytes([0,0,0,0]):
			type = bytecode.read_int()
			if type == 0x1: #field
				key = bytecode.read_str()
				self.data[key] = self.parse_field(bytecode)
			elif type == 0x4: #object
				raise TypeError("No objects should be in root of metadata")
				str_len = util.btoi(bytecode[:4])
				bytecode = bytecode[4:]
				name = str(bytecode[:length], 'utf-8')
				bytecode = bytecode[str_len:]
				#objList.append(Atom(name))
			else:
				bytecode.increment_position(-48)
				print(bytecode.peek(40))
				raise TypeError("mystery type?!?")
		bytecode.increment_position(4)
		return

class BW_Collection():
	def __init__(self):
		self.header = 0
		self.packaged_items = []
		self.unpackaged_items = []

	def read(self, path):
		from pytwig.src.lib import fs
		bytecode = BW_Bytecode().set_contents(fs.read_binary(path))
		bytecode.raw = True
		bytecode.set_string_mode("PREPEND_LEN")
		bytecode.debug_obj = self
		self.decode(bytecode)

	def decode(self, bytecode):
		self.header = bytecode.read(16)
		num_unpackaged = bytecode.read_int()
		for i in range(num_unpackaged):
			self.unpackaged_items.append(bytecode.read_str())
			bytecode.increment_position(4)
		num_packaged = bytecode.read_int()
		for i in range(num_packaged):
			self.packaged_items.append(bytecode.read_str())

	def encode_to(self, bytecode):
		bytecode.write(self.header)
		bytecode.write_int(len(self.unpackaged_items))
		for each_entry in self.unpackaged_items:
			bytecode.write_str(each_entry)
			bytecode.write_int(0)
		bytecode.write_int(len(self.packaged_items))
		for each_entry in self.packaged_items:
			bytecode.write_str(each_entry)

	def write(self, path):
		bytecode = BW_Bytecode()
		bytecode.set_string_mode("PREPEND_LEN")
		bytecode.raw = True
		bytecode.debug_obj = self
		self.encode_to(bytecode)
		from pytwig.src.lib import fs
		fs.write_binary(path, bytecode.contents)

	def __str__(self):
		return str(self.unpackaged_items + self.packaged_items)

	def __dict__(self):
		return {"header":self.header, "meta":self.meta, "contents":self.contents}

class BW_Bytecode:

	def __init__(self, contents = ''):
		self.debug_obj = None
		self.contents = b''
		self.contents_len = 0
		if contents != '':
			self.contents = contents
		self.position = 0
		self.reading_meta = True
		self.obj_list = [None]
		self.meta_only = False
		self.raw = False
		self.string_mode = None

	def set_contents(self, contents):
		self.contents = contents
		self.contents_len = len(contents)
		self.position = 0
		if self.contents_len >= 40:
			if self.contents[11] == b'2':
				self.string_mode = "PREPEND_LEN"
			elif self.contents[11] == b'0':
				self.string_mode = "NULL_TERMINATED"
		return self

	def set_string_mode(self, new_string_mode = None):
		if new_string_mode == None:
			new_string_mode = str(self.contents[11])
		if len(new_string_mode) == 1:
			if new_string_mode == '0':
				self.string_mode = "NULL_TERMINATED"
			elif new_string_mode == '2':
				self.string_mode = "PREPEND_LEN"
			elif new_string_mode == '1':
				raise SyntaxError("invalid string mode: header is json typed")
			else:
				raise SyntaxError("invalid string mode: " + new_string_mode)
		else:
			self.string_mode = new_string_mode

	def reset_pos(self):
		self.position = 0

	def peek(self, length = 1):
		#if self.position + length > self.contents_len:
		#	raise EOFError("End of file")
		return self.contents[self.position:self.position+length]

	def read(self, length = 1):
		output = self.peek(length)
		self.position += length
		return output

	def read_str(self, length = None):
		if length != None:
			output = self.peek(length)
			self.position += length
			try:
				return str(output, "utf-8")
			except UnicodeDecodeError:
				return output
				return str(output, "utf-16")
		else:
			if self.string_mode == "PREPEND_LEN":
				str_len = self.read_int()
				if (str_len & 0x80000000):
					str_len &= 0x7fffffff
					char_enc = 'utf-16'
					char_len = 2
				else:
					char_enc = 'utf-8'
					char_len = 1
				if (str_len > 100000):
					raise TypeError('String is too long')
				else:
					return self.read(str_len*(char_len)).decode(char_enc)
				return self.read_str(str_len)
			elif self.string_mode == "NULL_TERMINATED":
				output = b''
				while self.peek_int(1):
					output += self.read()
				self.increment_position(1) # increment position to pass over null
				return str(output, "utf-8")
			else:
				print(self.string_mode)
				raise SyntaxError("Invalid string mode")

	def read_int(self, len = 4):
		return util.btoi(self.read(len))

	def peek_int(self, len = 4):
		return util.btoi(self.peek(len))

	def write(self, append):
		if isinstance(append, bytes):
			self.contents += append
		elif isinstance(append, str):
			self.contents += bytes.fromhex(append)
		else:
			raise TypeError("Cannot write a non-bytes file")
		self.contents_len = len(self.contents)

	def write_str(self, string):
		if self.string_mode == "PREPEND_LEN":
			try: string.encode("ascii")
			except UnicodeEncodeError:
				self.contents += bytes.fromhex(hex(0x80000000 + len(string))[2:])
				self.contents += string.encode('utf-16be')
			else:
				self.contents += util.hex_pad(len(string), 8)
				self.contents += string.encode('utf-8')
		elif self.string_mode == "NULL_TERMINATED":
			self.contents += string.encode('utf-8')
			self.contents += bytes([0])
		else:
			raise SyntaxError("Invalid string mode")

	def write_int(self, num, pad = 8):
		self.contents += util.hex_pad(num, pad)
		self.contents_len = len(self.contents)

	def increment_position(self, amt):
		if self.position + amt > self.contents_len:
			raise EOFError("End of file")
		self.position = self.position + amt

class BW_Clip_File(BW_File):
	def __init__(self, track = None):
		super().__init__('note-clip')
		document = bw_object.BW_Object(46)
		if track != None:
			document.get("track_group(1245)").get("main_tracks(1246)").append(track)
		self.contents = bw_object.BW_Object("clip_document(479)").set("document(2409)", document)

	def set_meta(self):
		self.meta.data['beat_length'] = 1.0

	def get_main_track(self):
		if len(self.contents.get(2409).get(1245).get(1246)) == 0:
			print("No main tracks in clip file")
			return None
		return self.contents.get(2409).get(1245).get(1246)[0]

	def set_main_track(self, track):
		self.contents.get(2409).get(1245).get(1246).insert(0, track)
		return self

class BW_Device(BW_File):
	def __init__(self, track = None):
		super().__init__('device')
		self.contents = bw_object.BW_Object(151)

	def get_atoms(self):
		return self.contents.get(173) + self.contents.get(177) + self.contents.get(178)

	def get_panels(self):
		return self.contents.get(6213)
