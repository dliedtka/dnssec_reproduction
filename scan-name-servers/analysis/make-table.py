import json
import glob
import os
import statistics

PATH = 'results_DS_DNSKEY/'

counts_all = { str(i): 0 for i in range(-3, 4) }
counts_net = { str(i): 0 for i in range(-3, 4) }
counts_org = { str(i): 0 for i in range(-3, 4) }
counts_com = { str(i): 0 for i in range(-3, 4) }

def add_to_counts(data, counts):
    for k, v in data.items():
        counts[k] += v


for filename in os.listdir(PATH):
    with open(os.path.join(PATH, filename), 'r') as f_in:
        try:
            data = json.load(f_in)
        except:
            continue
        add_to_counts(data, counts_all)
        if (filename.find('.net') != -1):
            add_to_counts(data, counts_net)
        if (filename.find('.org') != -1):
            add_to_counts(data, counts_org)
        if (filename.find('.com') != -1):
            add_to_counts(data, counts_com)

def print_results(counts):
    count_total = sum(counts.values())
    print('total domains scanned: {}'.format(count_total))
    if count_total != 0:
        print('percent of domains with DNSKEY record: ', 
                (counts['-2'] + counts['0'] + counts['1'] + counts['2']) / count_total)
    if count_total != 0:
        print('percent of domains with DNSKEY record: ', 
                (counts['1'] + counts['2']) / count_total)
    if (counts['1'] + counts['2'] + counts['0'] > 0):
        print('percent of domains missing DS record: ', 
                (counts['1']) / (counts['1'] + counts['2'] + counts['0']))

def print_all_results():
    print('==== results for all \n')
    print_results(counts_all)
    print('==== results for net \n')
    print_results(counts_net)
    print('==== results for org \n')
    print_results(counts_org)
    print('==== results for com \n')
    print_results(counts_com)

def print_each_domain():
    for filename in os.listdir(PATH):
        counts = { str(i): 0 for i in range(-3, 4) }
        with open(os.path.join(PATH, filename), 'r') as f_in:
            try:
                data = json.load(f_in)
            except:
                continue
        add_to_counts(data, counts)
        print('=== results for {}'.format(filename))
        print('domains signed: {}'.format(counts['1'] + counts['0'] + counts['2']))
        print('domains with DS: {}'.format(counts['0'] + counts['2']))
        if counts['1'] + counts['0'] + counts['2'] > 0:
            print('DS publishing ratio: {}'.format((counts['0'] + counts['2']) / (counts['1'] + counts['0'] + counts['2'])))
        # print_results(counts)
        print('')

if __name__=='__main__':
    print_all_results()
    print_each_domain()
    

