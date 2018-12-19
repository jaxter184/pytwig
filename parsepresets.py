#from pytwig import * #this doesn't work, don't even bother trying to uncomment it
from src.lib import bwfile
import os

input_directory = 'input/bitwig-presets'
output_directory = 'output'
output = ""
tags_to_remove = ["2018", "2019", "monthly", "january", "february", "march", "april", "may", "june", "july", "august"]

def search(current_d): #d is short for directory
	global output, tags_to_remove
	for filename in os.listdir(current_d):
		if filename.endswith('.bwpreset'):
			#print(filename)
			each_preset = bwfile.BW_File()
			each_preset.read(current_d + '/' + filename, meta_only = True)
			output += "**{}**  \n".format(filename.replace('.bwpreset', ''))
			output += "Author: {}  \n".format(each_preset.meta.get("creator"))
			output += "Device: {}  \n".format(each_preset.meta.get("device_name"))
			output += "Description: {}  \n".format(each_preset.meta.get("comment").replace("\n", "\n\t"))
			if each_preset.meta.get("comment") == "":
				print(each_preset.meta.get("creator"))
			tags = each_preset.meta.get("tags").replace(",", "").split(" ")
			for each_tag in tags_to_remove:
				if each_tag in tags:
					tags.remove(each_tag)
			output += "Tags: {}  \n\n".format(", ".join(tags))
		elif os.path.isdir(current_d + '/' + filename):
			search(current_d + '/' + filename)

if __name__ == '__main__':
	if not os.path.exists(output_directory):
		os.mkdir(output_directory, 0o777)
	for dir in os.listdir(input_directory):
		if os.path.isdir(input_directory + '/' + dir):
			output += "## {} ##\n\n".format(dir)
			if not os.path.exists(output_directory + '/' + dir):
				os.mkdir(output_directory + '/' + dir, 0o777)
			search(input_directory + '/' + dir);
			with open(output_directory + '/' + dir + "/README.md", 'w') as file:
				file.write(output)
			output = ""
