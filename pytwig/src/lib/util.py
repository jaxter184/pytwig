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
def hexPad(data, pad = 8):
	if isinstance(data, bytearray):
		return bytearray.fromhex((pad/2-len(value))*'00') + data
	elif isinstance(data, int):
		value = hex(data)[2:]
		return bytearray.fromhex((pad-len(value))*'0'+value)
	else:
		print("jerror: incorrect input for pad prepend")
		return data

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
