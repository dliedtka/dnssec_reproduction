import json
import datetime
import bigjson
import random

# 10,435,705 unique keys
fin = open("../../data/key_list.json", "r")
key_list = json.load(fin)
fin.close()

fin2 = open("../../data/dnssec-resolver.lz4", "rb")
data = bigjson.load(fin2)


# see how long it takes to access each key

# causes delay
# shuffle in case we decide to run baseline over smaller set
#random.shuffle(key_list)

print ("accessing keys")
#print (data[key_list[0]].keys())    
counter = 0
for key in key_list:    
    print (key)
    junk = data[key]
    counter += 1
    if counter == 1000:
        break

print ("done")

# run experiments over subset of key list?

fin2.close()
