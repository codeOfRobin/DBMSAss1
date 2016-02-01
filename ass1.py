import sys
import ast
import json
import re
from prettytable import PrettyTable
schemas = {}
records = {}
relations = []

def removeFirst(arr):
	return arr[1:]

def attemptConversion(var, typeToAssign,nameOfTable):
	if typeToAssign == "int":
		try:
		    return int(var)
		except ValueError:
			print("invalid")
			schemas[nameOfTable]["invalid"] = True
			# raise AssertionError("There's a type mismatch for "+ var)
	elif typeToAssign == "float":
		try:
		    return float(var)
		except ValueError:
			print("invalid")
			schemas[nameOfTable]["invalid"] = True
		    # raise AssertionError("There's a type mismatch for "+ var)
	elif typeToAssign == "str":
		try:
		    return str(var)
		except ValueError:
			print("invalid")
			schemas[nameOfTable]["invalid"] = True
		    # raise AssertionError("There's a type mismatch for "+ var)

def sqlJoin(firstRecords,secondRecords,commonAttr):
	joinedResults = []
	for record1 in firstRecords:
		for record2 in secondRecords:
			if record1[commonAttr] == record2[commonAttr]:
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
				dic = {}
				tup = content[j][1:-1].split(',')

				for k,attr in enumerate(attrNames):
					if schemas[nameOfTable][attr]["isKey"] == "1" and not(tup[k] in [str(x[attr]) for x in records[nameOfTable]]):
						dic[attr] = attemptConversion(tup[k],schemas[nameOfTable][attr]["type"],nameOfTable)
					elif schemas[nameOfTable][attr]["isKey"] == "0":
						dic[attr] = attemptConversion(tup[k],schemas[nameOfTable][attr]["type"],nameOfTable)
					else:
						print("invalid")
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
			if mytuple[1] in schemas[mytuple[0]].keys() and mytuple[3] in schemas[mytuple[2]].keys():
				if set([x[mytuple[3]] for x in records[mytuple[2]]]).issubset([x[mytuple[1]] for x in records[mytuple[0]]]):
					print("relation added")
					relations.append((mytuple[0],mytuple[2]))
				else:
					# raise AssertionError("one of the foreign keys doesn't exist in the PK table")
					print("invalid")
					schemas[mytuple[0]]["invalid"] = True
					schemas[mytuple[2]]["invalid"] = True
			else:
				# raise AssertionError("Looks like one of the attrs in the table doesn't exist")
				print("invalid")
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
		for j in range(0,numberOfAttrs):
			tup = content[j][1:-1].split(',')
			tablesInSubschemas.append(tup[0])
			attrsInSubschemas.append(tup[1])

		print((attrsInSubschemas))
		print((tablesInSubschemas))
		commonAttrs = set.intersection(*([set(list(schemas[x].keys())) for x in schemas.keys()]))
		print(commonAttrs)
		if commonAttrs!=set():
			print("do a join")
			commonAttr = list(commonAttrs)[0]
			#assuming : join by one attr. http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.join.html
			print(commonAttr)
			joinedTable = records[tablesInSubschemas[0]]
			for table in tablesInSubschemas[1:]:
				joinedTable = sqlJoin(joinedTable,records[table],commonAttr)
			t = PrettyTable([x for x in attrsInSubschemas])
			for row in joinedTable:
				t.add_row([row[key] for key in attrsInSubschemas])
			print(t)

		else:
			cartedTable = records[tablesInSubschemas[0]]
			for table in tablesInSubschemas[1:]:
				cartedTable = cartTables(cartedTable,records[table])
			t = PrettyTable([x for x in attrsInSubschemas])
			for row in cartedTable:
				t.add_row([row[key] for key in attrsInSubschemas])
			print(t)
			print("do a cartesian")

main()
