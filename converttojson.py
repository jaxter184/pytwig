from src.lib import bwfile, objects
from src.lib import color as col
from src.lib.luts import non_overlap

name = "group.bwscene"
#name = "proj.bwproject"
#name = "clip.bwclip"
#name = "preset.bwpreset"

if __name__ == "__main__":
	test = bwfile.BW_File()
	test.read('input/' + name)

	if non_overlap.confirmed_names:
		import os
		with open("confimed.py", 'w') as file:
			file.write(str(non_overlap.confirmed_names).replace(", ",",\n"))
	if non_overlap.confirmed_fields:
		import os
		with open("confimedfuield.py", 'w') as file:
			file.write(str(non_overlap.confirmed_fields).replace(", ",",\n"))

	test.write('output/{}.bwpreset'.format(name))
	test.export('output/{} json.bwpreset'.format(name))
