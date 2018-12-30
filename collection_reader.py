from src.lib import bwfile

name = "test4.collection"

if __name__ == "__main__":
	test = bwfile.BW_Collection()
	test.read('input/' + name)

	print(str(test).replace(', ', ',\n'))

	test.write('output/' + name)
