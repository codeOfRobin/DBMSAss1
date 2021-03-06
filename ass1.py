import sys
import ast
import json
import re
from datetime import datetime, date, time
from prettytable import PrettyTable
schemas = {}
records = {}
relations = []

def removeFirst(arr):
	return arr[1:]

def attemptConversion(var, typeToAssign,nameOfTable):
	if typeToAssign == "INTEGER":
		try:
		    return int(var)
		except ValueError:
			print("invalid" + nameOfTable + "due to types" + typeToAssign)
			schemas[nameOfTable]["invalid"] = True
			# raise AssertionError("There's a type mismatch for "+ var)
	elif typeToAssign == "REAL" or typeToAssign == "FLOAT":
		try:
		    return float(var)
		except ValueError:
			print("invalid" + nameOfTable + "due to types" + typeToAssign)
			schemas[nameOfTable]["invalid"] = True
		    # raise AssertionError("There's a type mismatch for "+ var)
	elif typeToAssign == "BOOLEAN":
		if var == "TRUE" or var == "FALSE":
			return str(var)
		else:
			print("invalid" + nameOfTable + "due to types" + typeToAssign)
			schemas[nameOfTable]["invalid"] = True
	elif typeToAssign == "DATE":
		try:
			datetime.strptime(var,"%d/%m/%Y")
			return str(var)
		except ValueError as err:
			print("invalid" + nameOfTable + "due to types" + typeToAssign)
			schemas[nameOfTable]["invalid"] = True
	elif typeToAssign == "CURRENCY":
		if (re.compile("\$\d+").match(var)):
			return str(var)
		else:
			print("invalid" + nameOfTable + "due to types" + typeToAssign)
			schemas[nameOfTable]["invalid"] = True
	else:
		try:
		    return str(var)
		except ValueError:
			print("invalid" + nameOfTable + "due to types" + typeToAssign)
			schemas[nameOfTable]["invalid"] = True
		    # raise AssertionError("There's a type mismatch for "+ var)

def sqlJoin(firstRecords,secondRecords,commonAttrList):
	joinedResults = []
	for record1 in firstRecords:
		for record2 in secondRecords:
			if all(x==True for x in [record1[commonAttr] == record2[commonAttr] for commonAttr in commonAttrList]):
				joinRecord = {}
				for key in record1.keys():
					joinRecord[key] = record1[key]
				for key in record2.keys():
					joinRecord[key] = record2[key]
				joinedResults.append(joinRecord)
	return joinedResults

def cartTables(firstRecords,secondRecords):
	cartedResults = []
	# print(json.dumps(firstRecords,sort_keys=True, indent=4))
	# print(json.dumps(secondRecords,sort_keys=True, indent=4))
	for record1 in firstRecords:
		for record2 in secondRecords:
			cartRecord = {}
			# print(json.dumps(record1,sort_keys=True, indent=4))
			# print(json.dumps(record2,sort_keys=True, indent=4))
			for key in record1.keys():
				cartRecord[key] = record1[key]
			for key in record2.keys():
				cartRecord[key] = record2[key]
			# print(json.dumps(cartRecord,sort_keys=True, indent=4))
			cartedResults.append(cartRecord)
	# print(json.dumps(cartedResults,sort_keys=True, indent=4))
	return cartedResults
def main():
	if len(sys.argv) != 3:
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
				if "invalid" in schemas[nameOfTable]:
					break
				dic = {}
				tup = content[j].split(',')
				for k,attr in enumerate(attrNames):
					if schemas[nameOfTable][attr]["isKey"] == "1" and not(tup[k] in [str(x[attr]) for x in records[nameOfTable]]):
						dic[attr] = attemptConversion(tup[k],schemas[nameOfTable][attr]["type"],nameOfTable)
					elif schemas[nameOfTable][attr]["isKey"] == "0":
						dic[attr] = attemptConversion(tup[k],schemas[nameOfTable][attr]["type"],nameOfTable)
					else:
						print("invalid" + nameOfTable + "due to primary key inconsistencies")
						schemas[nameOfTable]["invalid"] = True
						# raise AssertionError("looks like a primary key record was duplicated,specifically "+ tup[k])
				records[nameOfTable].append(dic)
			content = content[numberOfRecords:]
		numberOfRelations = int(content[0])
		content = removeFirst(content)
		for i in range(0,numberOfRelations):
			relationString = str(content[i])
			regexPattern = '|'.join(map(re.escape, ['(',')',',']))
			elements = [x for x in re.split(regexPattern,relationString) if x!='']
			mytuple = tuple(elements)
			print(mytuple)
			if "invalid" in schemas[mytuple[0]] or "invalid" in schemas[mytuple[2]]:
				schemas[mytuple[0]]["invalid"] = True
				schemas[mytuple[2]]["invalid"] = True
			else:
				if mytuple[0] in schemas.keys() and mytuple[2] in schemas.keys():
					if mytuple[1] in schemas[mytuple[0]].keys() and mytuple[3] in schemas[mytuple[2]].keys():
						if set([x[mytuple[3]] for x in records[mytuple[2]]]).issubset([x[mytuple[1]] for x in records[mytuple[0]]]):
							print("relation added")
							relations.append((mytuple[0],mytuple[2]))
						else:
							# raise AssertionError("one of the foreign keys doesn't exist in the PK table")
							print("invalidness in " + schemas[mytuple[0]] + " and " + schemas[mytuple[0]])
							schemas[mytuple[0]]["invalid"] = True
							schemas[mytuple[2]]["invalid"] = True
					else:
						# raise AssertionError("Looks like one of the attrs in the table doesn't exist")
						print("invalid as attr doesn't exist")
						schemas[mytuple[0]]["invalid"] = True
						schemas[mytuple[2]]["invalid"] = True
		content = content[numberOfRelations:]
	# print(json.dumps(records,sort_keys=True, indent=4))
	# print(json.dumps(schemas,sort_keys=True, indent=4))
	# print(records["NAME_table"][0]["entry_num"])
	for relationTuple in relations:
		if ("invalid" in schemas[relationTuple[0]]) or ("invalid" in schemas[relationTuple[1]]):
			schemas[relationTuple[0]]["invalid"] = True
			schemas[relationTuple[1]]["invalid"] = True
	for tableName in schemas.keys():
		if "invalid" in schemas[tableName]:
			pass
		else:
			t = PrettyTable([x for x in schemas[tableName].keys()])
			for row in records[tableName]:
				t.add_row([row[key] for key in schemas[tableName].keys()])
			print(t)
	# second part
	with open(sys.argv[2]) as f:
		content = [x[:-1] for x in f.readlines()]
		numberOfAttrs = int(content[0])
		content = removeFirst(content)
		attrsInSubschemas = []
		tablesInSubschemas = []
		resultTable = []
		resultTableAttrs = []
		for j in range(0,numberOfAttrs):
			print("NUMBER" + str(j))
			tup = content[j][1:-1].split(',')
			tablesInSubschemas.append(tup[0])
			attrsInSubschemas.append(tup[1])
			newTable = tup[0]
			newAttr = tup[1]
			if len(tablesInSubschemas) == 1 and len(attrsInSubschemas) == 1:
				print("FIRST")
				resultTable = records[tablesInSubschemas[0]]
				resultTableAttrs = [col for col in schemas[tablesInSubschemas[0]].keys() ]
				print(resultTableAttrs)
			else:
				print(resultTableAttrs)
				x = set([col for col in schemas[newTable].keys()])
				y =set(resultTableAttrs)
				commonAttrs = x.intersection(y)
				if "invalid" in commonAttrs:
					print("removed invalid")
					commonAttrs.discard("invalid")
				if commonAttrs!=set():
					print("nat")
					print(commonAttrs)
					resultTable = sqlJoin(resultTable,records[newTable],list(commonAttrs))
					resultTableAttrs = list(set(resultTableAttrs).union(set([col for col in schemas[newTable].keys()])))
				else:
					print("cat")
					resultTable = cartTables(resultTable,records[newTable])
					resultTableAttrs = resultTableAttrs + ([col for col in schemas[newTable].keys()])
		attrsInSubschemas = list(set(attrsInSubschemas))
		t = PrettyTable([x for x in attrsInSubschemas])
		for row in resultTable:
			print(row)
			t.add_row([row[key] for key in attrsInSubschemas])
		print(t)

main()
