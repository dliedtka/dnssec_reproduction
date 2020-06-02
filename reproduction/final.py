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
resolvers_correct = {}
for resolver in resolvers:
	resolvers_correct[resolver] = True

for scenario in scenarios:
	for zone in scenario["zones-requested"].keys():
			for rec_type in scenario["zones-requested"][zone].keys():
				for entry in scenario["zones-requested"][zone][rec_type]:
					resolver = entry[0]
					if scenario["zones-resolved"] != ["gowritearticle"]:
						resolvers_correct[resolver] = False

counter = 0
for resolver in resolvers:
	if resolvers_correct[resolver]:
		counter += 1

print (counter / len(resolvers))