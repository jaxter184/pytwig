from src.lib import bwfile

if __name__ == "__main__":
	test = bwfile.BW_File()
	test.read('input/preset.bwpreset')
	test.export("output/preset json.bwpreset")
	test.write("output/preset.bwpreset")
