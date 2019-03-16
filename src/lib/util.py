#author: stylemistake https://github.com/stylemistake

import json

# removed: def json_encode(x):

# removed: def json_decode(x):

def json_print(x):
	print(json_encode(x))

def find_top_level_json(text):
	nesting = 0
	start_index = None
	ctx = None
	objects = []
	for i, x in enumerate(text):
		if ctx == 'string':
			if x == '"':
				ctx = None
				continue
			continue
		if x == '{':
			if nesting == 0:
				start_index = i
			nesting += 1
			continue
		if x == '}':
			if nesting == 0:
				raise Exception('Invalid JSON')
			nesting -= 1
			if nesting == 0:
				obj_text = text[start_index:i + 1]
				obj = json_decode(obj_text)
				objects.append(obj)
			continue
	return objects

# removed: def fix_lazy_json(text):

# removed: def remove_bracketed_hashes(obj):

def uuid_from_text(text):
	import hashlib
	import uuid
	hasher = hashlib.md5()
	hasher.update(text.encode('utf-8'))
	digest = hasher.digest()
	return str(uuid.UUID(bytes = digest[:16]))

# removed: def parse_bitwig_device(device_data):

# removed: def serialize_bitwig_device(device):

# Adds leading 0s to a hex value
def hex_pad(data, pad = 8):
	if isinstance(data, bytes):
		return bytes.fromhex((pad/2-len(value))*'00') + data
	elif isinstance(data, int):
		value = hex(data)[2:]
		return bytes.fromhex((pad-len(value))*'0'+value)
	else:
		raise TypeError("incorrect input type for zero padding")

# Gets the classnum or fieldnum from a string
def extract_num(name):
	#print(name.replace(')', '').split('('))
	name = name.replace(')', '(').split('(')
	for i in range(len(name)):
		try :
			return int(name[-i - 1])
		except:
			pass
	return name[0]

def btoi(byte):
	return int.from_bytes(byte, byteorder='big')

import uuid
from pytwig.src.lib.luts import field_lists, defaults
from pytwig import bw_object
from pytwig import color as bwcol
from pytwig import route as bwroute
#TODO make type list for each version

null_defaults = {
	1:0,
	5:False,
	6:0.0,
	7:0.0,
	8:'',
	9:None,
}

def get_field_default(fieldnum):
	type = field_lists.field_type_list[fieldnum]
	if fieldnum in defaults.defaults:
		if type == 9:
			return bw_object.BW_Object(defaults.defaults[fieldnum])
		elif type == 0x12:
			return [bw_object.BW_Object(defaults.defaults[fieldnum])]
		return defaults.defaults[fieldnum]
	#else:
	if type in (0x12, 0x17, 0x19): # object list
		return []
	elif type == 0x14:
		return {"type": "map<string,object>", "data": {}}
	elif type == 0x15:
		return uuid.uuid4()
	elif type == 0x16:
		return bwcol.Color(0.5,0.5,0.5,1)
	elif type == 0x1a:
		return bwroute.Route()
	else:
		return null_defaults[type]
