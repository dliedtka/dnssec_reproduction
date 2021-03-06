# one time script to generate a list of keys to work with
# runtime was about 4 hours on my computer, key list file is ~250 MB


import datetime
import bigjson
import json


print (datetime.datetime.now())
print ("getting keys")

with open("../../data/dnssec-resolver.lz4", "rb") as fin:
    data = bigjson.load(fin)
    
    #print (data["pdnssec-ba-29-211-894"].keys())    
    key_list = list(data.keys())

print (datetime.datetime.now())
print ("writing file")

with open("../../data/key_list.json", "w") as fout:
    json.dump(key_list, fout)

print (datetime.datetime.now())
print ("done")
