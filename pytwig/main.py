from src.lib import fs, objects, atoms, route, dicttobw
from src.lib.luts import typeLists

# This script generates a blank device file
if __name__ == "__main__":
	#test = objects.BW_File('application/bitwig-device')
	test = objects.BW_File('application/bitwig-device')
	test.set_contents(objects.BW_Object(151))
	print(test.encode_to_json())
