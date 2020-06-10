# create a list of filtered scenarios for use in future experiments



import json



# load filtered list of nodes, resolvers
fin = open("filtered_lists.json", "r")
lists = json.load(fin)
fin.close()
filtered_nodes = lists[0]
filtered_resolvers = lists[1]



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



# scan file
print ("scanning file")

filtered_scenarios = []

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

				# decide whether filtered, ordered for runtime optimization
				ex_id = get_exit_node_info(scenario)
				resolvers = get_resolver_info(scenario)

				keep_scenario = True

				for resolver in resolvers:
					if keep_scenario:
						if resolver not in filtered_resolvers:
							keep_scenario = False

				if keep_scenario:
					if ex_id is None or ex_id not in filtered_nodes:
						keep_scenario = False

				if keep_scenario:
					filtered_scenarios.append(scenario)

				if counter % 10000 == 0:
					print (counter)
					print (len(filtered_scenarios))
					#print (scenario)

				counter += 1
				json_obj = ""

				break

fin.close()


# write json object of filtered scenarios
print ("writing object,", len(filtered_scenarios), "scenarios")
with open("filtered_scenarios.json", "w") as fout:
    json.dump(filtered_scenarios, fout)