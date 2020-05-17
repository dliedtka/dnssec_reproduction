
'''
# see how many lines file is
# ANSWER: 526,263,299

with open("../../data/dnssec-resolver.lz4", "rb") as fin:
    counter = 0
    while True:

        line = fin.readline()
        if not line:
            break

        counter += 1
        if counter % 1000000 == 0:
            print (counter)
        

print (counter)
'''

# if bigjson generation of keys doesn't work, might have to get creative with pulling keys from line by line parse

# use count of brackets {} to know when you've reached a new entry
# if using a subset, skip with a certain probability

import json
import datetime


# first experiment, replicate first paragraph of section 5.3 
# (number of exit nodes, countries, ASes, days, resolvers, resolvers with DO bit set)
# still need to add resolver functionality
def exp_1(scenario):

	if "ex" in scenario.keys():
		ex_id = scenario["ex"][0]
		ex_co = scenario["ex"][4]
		ex_as = scenario["ex"][2]
	else:
		ex_id = None
		ex_co = None
		ex_as = None

	day = scenario["date"]

	return (ex_id, ex_co, ex_as, day)




# run different tasks based on exp_list
def run_exp(exp_list):
	print ("running")
	#scenario_list = []

	# experiment data
	ex_id_set = set()
	ex_co_set = set()
	ex_as_set = set()
	day_set = set()

	fin = open("../../data/dnssec-resolver.lz4", "r")

	# skip first line
	fin.readline()

	# start 
	bracket_depth = 0
	json_obj = ""

	counter = 0

	# read
	while True: #not break_condition:
		
		line = fin.readline()
		if not line:

			# temp
			print ("final")
			print ("ids", len(ex_id_set))
			print ("cos", len(ex_co_set))
			print ("ases", len(ex_as_set))
			print ("days", len(day_set))
			print (day_set)

			break
		
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

				if bracket_depth == 0:

					scenario = json.loads(json_obj)
					#scenario_list.append(scenario)

					if 1 in exp_list:
						(new_ex_id, new_ex_co, new_ex_as, new_day) = exp_1(scenario)
						if new_ex_id is not None:
							ex_id_set.add(new_ex_id)
						if new_ex_co is not None:
							ex_co_set.add(new_ex_co)
						if new_ex_as is not None:
							ex_as_set.add(new_ex_as)
						day_set.add(new_day)

					if counter % 10000 == 0:
						print (counter)
						#print (scenario)
						print ("ids", len(ex_id_set))
						print ("cos", len(ex_co_set))
						print ("ases", len(ex_as_set))
						print ("days", len(day_set))

					counter += 1
					json_obj = ""

					break

	#print (json_list)
	#for item in json_list:
	#	print (item)


start_time = datetime.datetime.now()
run_exp([1])
end_time = datetime.datetime.now()

print (start_time, end_time)