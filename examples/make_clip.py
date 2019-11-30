from src.lib import bwfile
from src.lib.obj import objects, atoms
from src.lib.obj import bwobj as BW
from src.lib.obj import clip as c
import extract_field_lists as e

# This script creates a clip from scratch

if __name__ == "__main__":
	# Create a BW_File object, then populate its contents by reading from the file
	ppcrn = c.BW_Clip_File()
	ppcrn.set_header('BtWg00010002008c000015120000000000000000')
	# Make objects
	c.DEFAULT_NOTE_LENGTH = 0.1
	clip = c.Note_Clip()
	root_note = 67
	for i in range(2):
		offset = float(i*4)
		clip.add_note(root_note+12, offset + 0.0)
		clip.add_note(root_note+10, offset + 0.5)
		clip.add_note(root_note+12, offset + 1.0)
		clip.add_note(root_note+ 7, offset + 1.5)
		clip.add_note(root_note+ 3, offset + 2.0)
		clip.add_note(root_note+ 7, offset + 2.5)
		clip.add_note(root_note+ 0, offset + 3.0)
	clip.add_note(root_note+12,  8.0)

	for i in range(2):
		offset = float(i)
		clip.add_note(root_note+14, offset +  8.5)
		clip.add_note(root_note+15, offset +  9.0)
		clip.add_note(root_note+12, offset + 10.5)
		clip.add_note(root_note+14, offset + 11.0)
		clip.add_note(root_note+10, offset + 12.5)
		clip.add_note(root_note+12, offset + 13.0)
	clip.add_note(root_note+ 8, 14.5)
	clip.add_note(root_note+12, 15.0)

	#clip.set_loop(True, 5)
	clip.set_duration(16)
	#clip.get(648).get(1180).get(6347)[-1].set(238, 60)

	ppcrn.set_clip(clip)

	# Write the file in both human-readable json and compressed bytecode formats
	ppcrn.export('ppcrn json.bwclip')
	ppcrn.write('ppcrn.bwclip')
