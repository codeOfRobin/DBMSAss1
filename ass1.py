import sys
import ast
import json
import re
schemas = {}
records = {}
relations = {}

def removeFirst(arr):
	return arr[1:]

def attemptConversion(var, typeToAssign):
	if typeToAssign == "int":
		try:
		    return int(var)
		except ValueError:
		    raise AssertionError("There's a type mismatch for "+ var)
	elif typeToAssign == "float":
		try:
		    return float(var)
		except ValueError:
		    raise AssertionError("There's a type mismatch for "+ var)
	elif typeToAssign == "str":
		try:
		    return str(var)
		except ValueError:
		    raise AssertionError("There's a type mismatch for "+ var)


def main():
	if len(sys.argv) != 2:
		raise ValueError('You done screwed up')

	with open(sys.argv[1]) as f:
		content = [x[:-1] for x in f.readlines()]
		numberOfTables = int(content[0])
		content = removeFirst(content)

		for i in range(0,numberOfTables):
			nameOfTable = content[0]
			schemas[nameOfTable] = {}
			records[nameOfTable] = []
			content = removeFirst(content)
			numberOfAttrs = int(content[0])
			content = removeFirst(content)
			attrNames = []
			for j in range(0,numberOfAttrs):
				tup = content[j][1:-1].split(',')
				schemas[nameOfTable][tup[0]] = {}
				schemas[nameOfTable][tup[0]]['type'] = tup[1]
				schemas[nameOfTable][tup[0]]['isKey'] = tup[2]
				attrNames.append(tup[0])
			content = content[numberOfAttrs:]
			numberOfRecords = int(content[0])
			content = removeFirst(content)
			for j in range(0, numberOfRecords):
				dic = {}
				tup = content[j][1:-1].split(',')
				for k,attr in enumerate(attrNames):
					dic[attr] = attemptConversion(tup[k],schemas[nameOfTable][attr]["type"])
				records[nameOfTable].append(dic)
			content = content[numberOfRecords:]
		numberOfRelations = int(content[0])
		content = removeFirst(content)
		print(json.dumps(schemas,sort_keys=True, indent=4))
		for i in range(0,numberOfRelations):
			relationString = str(content[i])
			regexPattern = '|'.join(map(re.escape, ['(',')',',']))
			elements = [x for x in re.split(regexPattern,relationString) if x!='']
			mytuple = tuple(elements)
			print(mytuple)
			if mytuple[1] in schemas[mytuple[0]].keys() and mytuple[3] in schemas[mytuple[2]].keys():
				print("true")
			else:
				raise AssertionError("Looks like one of the relations couldn't be created")
		content = content[numberOfRelations:]
	print(json.dumps(records,sort_keys=True, indent=4))
	print(json.dumps(schemas,sort_keys=True, indent=4))
	# print(records["NAME_table"][0]["entry_num"])


main()
