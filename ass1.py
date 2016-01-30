import sys
import ast
schemas = {}
records = {}


def removeFirst(arr):
	return arr[1:]


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
				dic[attr] = tup[k]
			records[nameOfTable].append(dic)
		content = content[numberOfRecords:]
print(records)
print(schemas)
