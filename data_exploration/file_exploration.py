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

# if bigjson generation of keys doesn't work, might have to get creative with pulling keys from line by line parse
