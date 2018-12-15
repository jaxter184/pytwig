from src.lib import bwfile

if __name__ == "__main__":
	test = bwfile.BW_File()
	test.read('input/preset2.bwpreset', raw = False)
	test.export("output/preset2 json.bwpreset")
	test.write("output/preset2.bwpreset")
