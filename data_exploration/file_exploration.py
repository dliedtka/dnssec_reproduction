# using json and bigjson is too slow for 14GB structure
# instead we perform all operations as we read in file line-by-line

import json
import datetime


# "experiment zero", just count the numnber of lines in the file
# ANSWER: 526,263,299
def exp_0():

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
	return


# EXPERIMENT 1
# replicate exit node parts of first paragraph of section 5.3 
# (number of exit nodes, countries, ASes, days)
# RESULT: numbers didn't match up, looks like there is an extra day of data corresponding with section 5.4 maybe?
# use experiment 2 to figure this out
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


# EXPERIMENT 2
# uses same function as 1, but sorts by day, later group sets together to see if we can find outlier day
# run from a python terminal to combine different sets after run
# RESULT: numbers still don't add up if you exclude any single day; going to email author about this


# EXPERIMENT 3
# count unique resolvers, resolvers with DO bit set
# RUNNING
def exp_3(scenario):

	resolvers = set()
	do_resolvers = set()

	if "zones-requested" in scenario.keys():
		for zone in scenario["zones-requested"].keys():
			for rec_type in scenario["zones-requested"][zone].keys():
				#try:
				for entry in scenario["zones-requested"][zone][rec_type]:
					resolvers.add(entry[0])
					if entry[1]:
						do_resolvers.add(entry[0])
				#except:
				#	print ("failed here")
			    #	print (rec_type)
				#	print (scenario)
				#	import sys
				#	sys.exit()

	return (resolvers, do_resolvers)


# run different tasks based on exp_list
# experiments 0 and 2 can only be run by themself
def run_exp(exp_list):

	print ("running experiments", exp_list)
	if 0 in exp_list or 2 in exp_list:
		if len(exp_list) != 1:
			raise Exception("can only run experiments 0 and 2 by themselves")

	if 0 in exp_list:
		exp_0()
		return

	#scenario_list = []

	# experiment data
	# exp_1
	ex_id_set = set()
	ex_co_set = set()
	ex_as_set = set()
	day_set = set()
	# exp_2
	day_objects = {}
	# exp_3
	resolver_set = set()
	do_resolver_set = set()

	fin = open("../../data/dnssec-resolver.lz4", "r")

	# skip first line
	fin.readline()

	# start 
	bracket_depth = 0
	json_obj = ""
	counter = 0

	# read
	# if using a subset, skip with a certain probability (NOT IMPLEMENTED)
	while True: 
		
		line = fin.readline()

		# reached end of file, runtime usually ~48 mins
		if not line:

			if 1 in exp_list:
				print ("exp_1 results")
				print ("ids", len(ex_id_set))
				print ("cos", len(ex_co_set))
				print ("ases", len(ex_as_set))
				print ("days", len(day_set))
				print (day_set)

			if 2 in exp_list:
				return day_objects

			if 3 in exp_list:
				print ("exp_3 results")
				print ("resolvers", len(resolver_set))
				print ("DO resolvers", len(do_resolver_set))

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
					#scenario_list.append(scenario)

					# run exp_1 functionality
					if 1 in exp_list:
						(new_ex_id, new_ex_co, new_ex_as, new_day) = exp_1(scenario)
						if new_ex_id is not None:
							ex_id_set.add(new_ex_id)
						if new_ex_co is not None:
							ex_co_set.add(new_ex_co)
						if new_ex_as is not None:
							ex_as_set.add(new_ex_as)
						day_set.add(new_day)

					# run exp_2 functionality
					if 2 in exp_list:
						(new_ex_id, new_ex_co, new_ex_as, new_day) = exp_1(scenario)
						if new_day not in day_objects.keys():
							day_objects[new_day] = {}
							day_objects[new_day]["ex_id"] = set()
							day_objects[new_day]["ex_co"] = set()
							day_objects[new_day]["ex_as"] = set()
						if new_ex_id is not None:
							day_objects[new_day]["ex_id"].add(new_ex_id)
						if new_ex_co is not None:
							day_objects[new_day]["ex_co"].add(new_ex_co)
						if new_ex_as is not None:
							day_objects[new_day]["ex_as"].add(new_ex_as)

					# run exp_3 functionality
					if 3 in exp_list:
						(new_resolvers, new_do_resolvers) = exp_3(scenario)
						resolver_set = resolver_set.union(new_resolvers)
						do_resolver_set = do_resolver_set.union(new_do_resolvers)

					if counter % 10000 == 0:
						print (counter)
						print (len(resolver_set), len(do_resolver_set))
						#print (scenario)

					counter += 1
					json_obj = ""

					break

	#print (json_list)
	#for item in json_list:
	#	print (item)


if __name__ == "__main__":
	
	start_time = datetime.datetime.now()
	run_exp([3])
	end_time = datetime.datetime.now()

	print (start_time, end_time)