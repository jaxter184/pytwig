from src.lib import bwfile

# This script reads an input file

filename = "Chain.bwdevice"
#filename = "Default keyboard mappings (My version).bwkeymap"
#filename = "proj.bwproject"
#filename = "clip.bwclip"
#filename = "preset.bwpreset"
#filename = "2.4.3.prefs"

DEBUG = False

if __name__ == "__main__":
	# Separate file extension from file name
	import os
	name, extension = os.path.splitext(filename)

	# Create a BW_File object, then populate its contents by reading from the file
	test = bwfile.BW_File()
	test.read('input/{}{}'.format(name, extension))

	if DEBUG:
		from src.lib.luts import non_overlap
		# Debug stuff for getting field types and class names. Don't do this for normal use.
		if non_overlap.confirmed_names:
			import os
			with open("confimed_names.py", 'w') as file:
				file.write(str(non_overlap.confirmed_names).replace(", ",",\n"))
		if non_overlap.confirmed_fields:
			import os
			with open("confimed_fields.py", 'w') as file:
				file.write(str(non_overlap.confirmed_fields).replace(", ",",\n"))

	# Write the file in both human-readable json and compressed bytecode formats
	test.export('output/{} dup json{}'.format(name, extension))
	test.write('output/{} dup{}'.format(name, extension))
