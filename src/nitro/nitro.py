#modules that deal primarily with parsing nitro code

def countIOs(text):
	length = len(text)
	i = 0
	inports = 0
	outports = 0
	while (i < length):
		# Find keyword '_inport'
		if (i < length - len("_inport")): # TODO: convert to .find()
			if text[i:i+len("_inport")] == "_inport":
				# After keyword inport is found,
				i+=len("_inport")
				if text[i] == '[':
					# Find close bracket
					if ']' in text[i:i+30]: # could hypoyhetically use a while loop since a close bracket is guaranteed
						end = text[i:i+30].index(']')
						arraySize = text[i+1:i+end] # arraySize = characters inside the brackets
						arraySize = expression(text, arraySize) # parse array
						i += end
						inports += arraySize
					else:
						print("Nitro Parse Error: Nitro expression is too long.")
				else:
					# If input is not an array
					inports += 1
		# Find keyword '_outport' (basically the same as inport)
		if (i < length - len("_outport")):
			if text[i:i+len("_outport")] == "_outport":
				i+=len("_outport")
				if text[i] == '[':
					if ']' in text[i:i+30]:
						end = text[i:i+30].index(']')
						arraySize = text[i+1:i+end]
						if arraySize.isdigit(): # Not sure why this is here, should automatically do this inside of expression()
							arraySize = int(arraySize)
						else:
							arraySize = expression(text, arraySize)
						i+= end
						outports += arraySize
					else:
						print("Nitro Parse Error: Nitro expression is too long.")
				else:
					outports += 1
		i+=1
	return inports, outports

def getName(text):
	index = text.find("@name")
	length = 0
	if index != -1:
		index += 7
		while text[index + length] not in ('\\','"',):
			length += 1
	else:
		index = text.find("component ") # TODO consolidate these into: if ((index = text.find("component ")) != -1)
		if index != -1:
			index += 10
			while text[index + length] != '\\':
				length += 1
		else:
			return "nameless nitro"
	return text[index:index+length]

def expression(text, exp): #exp is a list of terms TODO implement parentheses and subtraction
	if isinstance(exp, str):
		exp.replace('+', ' + ')
		exp.replace('*', ' * ')
		exp = exp.split()
	variables = {}
	if len(exp) == 1:
		if isinstance(exp[0], int) or exp[0].isdigit():
			return int(exp[0])
		else:#its a variable name
			j = text.find('const i32 '+exp[0]) + len('const i32 '+exp[0])
			while not text[j].isdigit():
				j+=1
			nLen = 0
			while text[j+nLen].isdigit():
				nLen+=1
			return int(text[j:j+nLen])
	while '*' in exp:
		i = exp.index('*')
		exp[i] = int(expression(text, [exp[i-1]])*expression(text, [exp[i+1]]))
		del exp[i+1], exp[i-1]
	while '+' in exp:
		i = exp.index('+')
		exp[i] = int(expression(text, [exp[i-1]])+expression(text, [exp[i+1]]))
		del exp[i+1], exp[i-1]
	if len(exp) == 1:
		if isinstance(exp[0], int) or exp[0].isdigit():
			return int(exp[0])
	print("Error: unknown expression in nitro interpretation")
	return
