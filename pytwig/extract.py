import os
from src import extractor
from src.lib import fs, util, atoms, route, dicttobw
from src.lib.luts import typeLists


extract_enable = 0 #change this to 0 for regular operation and 1 for class extraction. most users won't need class extraction, as it is just a tool I use to make internal files

def extract_data(name, directory): #decodes then reencodes a single file
	global extractedClasses, extractedFields
	device_data = fs.read_binary(os.path.join(directory, name))
	header = device_data[:40].decode("utf-8") #'BtWg00010001008d000016a00000000000000000'
	if (header[11] == '2'):
		if (extract_enable):
			classes,fields = extractor.bwExtract(device_data)
			extractedClasses.append(classes)
			extractedFields.append(fields)
	elif (header[11] == '1'):
		pass
	else:
		print("Error: Not a Bitwig file. Improper header.")

def extractClasses():
	global extractedClasses, extractedFields
	class_t_l = typeLists.class_type_list
	field_t_l = typeLists.field_type_list
	#collatedClassListErrors = {}
	for eachFile in extractedClasses:
		for eachClass in eachFile:
			if eachClass in class_t_l:
				# Check to see if the class matches the existing class
				if class_t_l[eachClass] != eachFile[eachClass]:
					if set(eachFile[eachClass])>set(class_t_l[eachClass]):
						class_t_l[eachClass] = eachFile[eachClass]
					elif set(eachFile[eachClass])<set(class_t_l[eachClass]):
						eachFile[eachClass] = class_t_l[eachClass]
					if class_t_l[eachClass] != eachFile[eachClass]:
						print("Error: \'conflicting class\'")
						print(eachClass)
						print(class_t_l[eachClass])
						print(eachFile[eachClass])
						#collatedClassListErrors[eachClass] = (eachFile[eachClass])
			else:
				#print(eachFile[eachClass])
				class_t_l[eachClass] = (eachFile[eachClass])
	for eachFile in extractedFields:
		for eachField in eachFile:
			if eachField in field_t_l:
				###check to see if the class matches the existing class
				#diffkeys = [k for k in field_t_l[eachClass] if field_t_l[eachClass][k] != eachFile[k]]
				#if diffkeys:
				if field_t_l[eachField] != eachFile[eachField]:
					if field_t_l[eachField] == None:
						field_t_l[eachField] = eachFile[eachField]
					elif eachFile[eachField] == None:
						eachFile[eachField] = field_t_l[eachField]
					if field_t_l[eachField] != eachFile[eachField]:
						print("Error: \'conflicting field\'")
						print(field_t_l[eachField])
						print(eachFile[eachField])
						#collatedClassListErrors[eachField] = (eachFile[eachField])
			else:
				#print(eachFile[eachField])
				field_t_l[eachField] = (eachFile[eachField])
	with open('typeLists.py', 'w') as file:
		output = str(class_t_l).replace('], ', '],\n').replace('{', 'classList = {\n').replace('}', '\n}')
		output2 = str(field_t_l).replace(', ', ',\n').replace('{', 'fieldList = {\n').replace('}', '\n}')
		file.write(output + '\n' + output2)

root_dir ='.\devices'
folder={0:'.\devices',
		1:'.\devices\old devices'}

if __name__ == "__main__":

	# Intro
	print (
	"""Heyo I'm Jaxter, thanks for using my little script.
	This is something that I made, and you should therefore be pretty careful about using it. I won't take responsibility for breaking your Bitwig devices, so make sure you have a copy of them saved somewhere before starting.
	Also, be cautious in general; just because I trust my own work doesn't mean you should.

	Now, with the fearmongering out of the way, lets get started.
	To avoid files, change the filename to have a '-' at the beginning.
	""")
	if extract_enable:
		print ("Extraction mode enabled. This shouldn't be on unless you deliberately turned it on.")

	# Prompt directory name
	try:
		directory = input("Enter the subdirectory that your devices are in. (If they're in the 'inputs' folder, just press enter)") # TODO* change text. There is no 'inputs' folder.
	except SyntaxError:
		directory = ''

	# Setup stuff
	if not directory:
		directory = 'input'
	else:
		directory = '.' + directory
	if not os.path.exists('output'):
		os.mkdir('output')
	extractedClasses = []
	extractedFields = []

	# Iterates through and processes each file
	for file in os.listdir(directory):
		if file.endswith((".bwdevice",".bwmodulator",".bwpreset",".bwclip",".bwscene",".bwremotecontrols",".bwproject")):
			print ('Processing '+file)
			if extract_enable:
				extract_data(file, directory)
			else:
				device_data = fs.read_binary(os.path.join(directory, name))
				header = device_data[:40].decode("utf-8") # Ex: 'BtWg00010001008d000016a00000000000000000'
				if (header[11] == '2'): # Standard unreadable Bitwig file
					decoded = process_data(device_data, 'decode')
					reencoded = process_data(decoded, 'encode')
					with open('output\\converted ' + name, 'wb') as file1, open('output\\reconverted ' + name, 'wb') as file2:
						file1.write(decoded.encode("utf-8"))
						file2.write(reencoded)
				elif (header[11] == '1'): # Plaintext readable Bitwig File
					# TODO test this
					device_data = fs.read(os.path.join(directory, name))[40:]

					# Forgot what this does
					i = 1
					brackSum = 1
					while brackSum:
						if device_data[i] == '{':
							brackSum += 1
						elif device_data[i] == '}':
							brackSum -= 1
						i += 1
					objectified = [dicttobw.convert(util.json_decode(device_data[:i])),dicttobw.convert(util.json_decode(device_data[i:]))]
					print(objectified)

					reencoded = process_data(objectified, 'encode')
					with open('output\\jsonconv ' + name, 'wb') as file:
						file.write(reencoded)
				else:
					print("Error: Not a Bitwig file. Improper header.")



		elif file.startswith('-',):
			print ('*skipping '+file)

	# Prints the extracted class list
	if extract_enable:
		extractClasses()
	input("All done. Let me know if you had any issues using this or have suggestions for improving it. [Press Enter to exit]")
