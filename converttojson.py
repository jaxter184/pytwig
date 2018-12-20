from src.lib import bwfile
from src.lib.luts import non_overlap

if __name__ == "__main__":
    test = bwfile.BW_File()
    test.read('input/clip4.bwclip', meta_only = False, raw = True)
    #test.read('input/proj.bwproject', meta_only = False, raw = True)
    #test.read('input/preset.bwpreset', meta_only = False, raw = True)

    if non_overlap.confirmed_names:
        import os
        with open("confimed.py", 'w') as file:
            file.write(str(non_overlap.confirmed_names).replace(", ",",\n"))
    if non_overlap.confirmed_fields:
        import os
        with open("confimedfuield.py", 'w') as file:
            file.write(str(non_overlap.confirmed_fields).replace(", ",",\n"))

    test.export('output/clip json.bwclip')
    test.write('output/clip.bwclip')
    #test.export('output/proj json.bwproject')
    #test.write('output/proj.bwproject')
    #test.write('output/preset.bwpreset')
    #test.export('output/preset json.bwpreset')
