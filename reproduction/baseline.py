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

print (len(resolvers), "resolvers")


# find correctly validating resolvers
'''
for scenario in scenarios:
	for zone in scenario["zones-requested"].keys():
			for rec_type in scenario["zones-requested"][zone].keys():
				for entry in scenario["zones-requested"][zone][rec_type]:
					if entry[3] == "Bahnhof Internet AB":
					#if "Comcast" in entry[3]:
						pprint.pprint(scenario)
'''
counter = 0
for scenario in scenarios:
	if scenario["zones-resolved"] == ["gowritearticle"]:
		counter += 1
print (counter / len(scenarios))