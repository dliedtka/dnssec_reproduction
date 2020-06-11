import json
import pprint


# load filtered scenarios
fin = open("filtered_scenarios.json", "r")
scenarios = json.load(fin)
fin.close()


# count resolvers
resolvers = set()
for scenario in scenarios:
	for zone in scenario["zones-requested"].keys():
			for rec_type in scenario["zones-requested"][zone].keys():
				for entry in scenario["zones-requested"][zone][rec_type]:
					resolvers.add(entry[0])
					
#print (len(resolvers), "resolvers")


# experiments
# correctly validating means 90% of exit nodes receive an error (no response) when resolver receives invalid record
# incorrectly validating means 90% of exit nodes receive a response when resolver receives invalid record
# otherwise resolver deemed "ambiguous"

invalid_zones = ['missing-ksk', 'missing-rrsig-ksk', 'mismatch-ds', 
	'invalid-rrsig-a', 'invalid-rrsig-ksk', 'missing-zsk', 
	'missing-rrsig-a', 'past-rrsig-a', 'future-rrsig-a']
valid_zones = ['gowritearticle', 'gowritepaper']

resolvers_record = {}
for resolver in resolvers:
	resolvers_record[resolver] = {}
	resolvers_record[resolver]["correct"] = 0
	resolvers_record[resolver]["total"] = 0

incorrect_resolvers = []

malady_list = {}
for resolver in resolvers:
	malady_list[resolver] = {}
	malady_list[resolver]["visited"] = False
	for inv_zone in invalid_zones:
		malady_list[resolver][inv_zone] = False

for scenario in scenarios:

	# get resolver 
	scenario_resolver = set()
	for zone in scenario["zones-requested"].keys():
		for rec_type in scenario["zones-requested"][zone].keys():
			for entry in scenario["zones-requested"][zone][rec_type]:
				scenario_resolver.add(entry[0])
	assert(len(scenario_resolver) <= 1)
	if len(scenario_resolver) == 0:
		continue
	scenario_resolver = list(scenario_resolver)[0]

	# check for a invalid request
	use_scenario = False
	for inv_zone in invalid_zones:
		if inv_zone in scenario["zones-requested"]:
			use_scenario = True
	
	# determine if exit node receives bad record
	if use_scenario:
		resolvers_record[scenario_resolver]["total"] += 1
		invalid_resolve = False
		for inv_zone in invalid_zones:
			if inv_zone in scenario["zones-resolved"]:
				invalid_resolve = True
				malady_list[scenario_resolver]["visited"] = True
				malady_list[scenario_resolver][inv_zone] = True
		if not invalid_resolve:
			resolvers_record[scenario_resolver]["correct"] += 1
		else:
			incorrect_resolvers.append(scenario_resolver)


# count
correct_counter = 0
incorrect_counter = 0
total_counter = 0
for resolver in resolvers:
	if resolvers_record[resolver]["total"] > 0:
		total_counter += 1
		if resolvers_record[resolver]["correct"] / resolvers_record[resolver]["total"] > 0.9:
			correct_counter += 1
		if resolvers_record[resolver]["correct"] / resolvers_record[resolver]["total"] < 0.1:
			incorrect_counter += 1


print ("\nExperiments:")
print ("Correctly validating resolvers:", (correct_counter / total_counter))
print ("Incorrectly validating resolvers:", (incorrect_counter / total_counter))
print ("Ambiguous:", (1 - (correct_counter / total_counter) - (incorrect_counter / total_counter) ))

print ("Total resolvers tested:", total_counter)
print ("Total resolvers:", len(resolvers))



# recreate table 5
print ("\nbad resolver list:")

bad_resolvers = {}

for scenario in scenarios:
	isp = ""
	country = ""

	# get resolver
	scenario_resolver = set()
	for zone in scenario["zones-requested"].keys():
		for rec_type in scenario["zones-requested"][zone].keys():
			for entry in scenario["zones-requested"][zone][rec_type]:
				scenario_resolver.add(entry[0])
				isp = entry[3]
				country = entry[4]

	assert(len(scenario_resolver) <= 1)
	if len(scenario_resolver) == 0:
		continue
	scenario_resolver = list(scenario_resolver)[0]

	if scenario_resolver in incorrect_resolvers:

		if (isp, country) not in bad_resolvers.keys():
			bad_resolvers[(isp, country)] = {}
			bad_resolvers[(isp, country)]["resolvers"] = set()
			bad_resolvers[(isp, country)]["nodes"] = set()

		bad_resolvers[(isp, country)]["resolvers"].add(scenario_resolver)
		bad_resolvers[(isp, country)]["nodes"].add(scenario["ex"][1])

# sort by num resolvers
resolver_mapping = {}
for isp in bad_resolvers.keys():
	num_resolvers = len(bad_resolvers[isp]["resolvers"])
	#assert(num_resolvers not in resolver_mapping.keys())
	resolver_mapping[num_resolvers] = isp

top_5 = list(resolver_mapping.keys())
top_5.sort(reverse=True)
top_5 = top_5[:5]

for key in top_5:
	isp = resolver_mapping[key]
	print (isp, len(bad_resolvers[isp]["resolvers"]), len(bad_resolvers[isp]["nodes"]))


# analysis of bad resolvers
print ("\nresolver issue analysis:")

malady_resolvers = 0
for resolver in resolvers:
	if malady_list[resolver]["visited"]:
		malady_resolvers += 1

for inv_zone in invalid_zones:
	malady_counter = 0
	for resolver in resolvers:
		if malady_list[resolver][inv_zone]:
			malady_counter += 1
	print (inv_zone, (malady_counter / malady_resolvers))

print ("")