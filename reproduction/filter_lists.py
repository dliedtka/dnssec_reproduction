# create a list of filtered nodes and resolvers to use to filter scenarios



import json



# keep track of (1) number of resolvers for each exit node, (2) number of times resolvers tested
node_resolvers = {}
resolver_tests = {}



# reuse some modified functions from exploration
def get_exit_node_info(scenario):

	if "ex" in scenario.keys():
		return scenario["ex"][0]
	else:
		return None


def get_resolver_info(scenario):

	resolvers = set()

	if "zones-requested" in scenario.keys():
		for zone in scenario["zones-requested"].keys():
			for rec_type in scenario["zones-requested"][zone].keys():
				for entry in scenario["zones-requested"][zone][rec_type]:
					resolvers.add(entry[0])
					
	return resolvers



# first scan
print ("scanning file")

# read in file the same way as in data exploration
fin = open("../../data/dnssec-resolver.lz4", "r")
fin.readline()

# start 
bracket_depth = 0
json_obj = ""
counter = 0

while True: 
	
	line = fin.readline()

	# reached end of file, runtime usually ~48 mins
	if not line:
		break
	
	# use count of brackets {} to know when you've reached a new entry
	for char in line:
		if char == '{' and bracket_depth == 0:
			json_obj += char
			bracket_depth += 1
		elif bracket_depth > 0:
			json_obj += char
			if char == '{':
				bracket_depth += 1
			elif char == '}':
				bracket_depth -= 1

			# complete entry
			if bracket_depth == 0:

				scenario = json.loads(json_obj)

				# tracking functionality
				ex_id = get_exit_node_info(scenario)
				resolvers = get_resolver_info(scenario)

				# 1
				if ex_id not in node_resolvers.keys():
					node_resolvers[ex_id] = set()
				for resolver in resolvers:
					node_resolvers[ex_id].add(resolver)

				# 2
				for resolver in resolvers:
					if resolver not in resolver_tests.keys():
						resolver_tests[resolver] = 1
					else:
						resolver_tests[resolver] += 1


				if counter % 10000 == 0:
					print (counter)
					print (len(node_resolvers.keys()), len(resolver_tests.keys()))
					#print (scenario)

				counter += 1
				json_obj = ""

				break

fin.close()



# now filter
print ("filtering nodes and resolvers")

filtered_nodes = []
filtered_resolvers = []

# keep nodes with just one resolver
for node in node_resolvers.keys():
	if len(node_resolvers[node]) == 1:
		filtered_nodes.append(node)

# keep resolvers tested 10 or more times
for resolver in resolver_tests.keys():
	if resolver_tests[resolver] >= 10:
		filtered_resolvers.append(resolver)



# write to file
print ("writing object,", len(filtered_nodes), "nodes", len(filtered_resolvers), "resolvers")
with open("filtered_lists.json", "w") as fout:
    json.dump([filtered_nodes, filtered_resolvers], fout)