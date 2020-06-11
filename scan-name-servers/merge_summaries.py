import json
import os
import sys


VERIFICATION_MODES = [
        'DNSKEY',
        'DS',
        'DS_DNSKEY'
        ]


def write_parseable_summary(summary):
    return json.dumps(summary) + '\n'

'''
merge summaries into a super summary
''' 
def merge_summaries(name_server, num_files, SUMMARY_FILE):
    super_summary = {str(i): 0 for i in range(-3, 4)}
    for f in range(num_files):
        with open(SUMMARY_FILE.format(name_server, f), 'r') as f_sum:
            f_sum.seek(0)
            summary = json.loads(f_sum.readline()[:-1]) # TODO fix this to load integers intead of strings
            for i in range(-3, 4):
                super_summary[str(i)] += summary[str(i)]
        f_sum.close()
    with open(SUMMARY_FILE.format(name_server, '-1'), 'w') as f_super:
        f_super.write(write_parseable_summary(super_summary))
    f_super.close() 
    print(super_summary)


def merge_summaries_auto(name_server, verification_mode):
    DIR_NAME = '{}-'.format(verification_mode) + '{0}-scan'.format(name_server)
    SUMMARY_FILE = '{}-'.format(verification_mode) + '{0}-scan/{0}-domains-{1}-summary.txt'
    super_summary = {str(i): 0 for i in range(-3, 4)}
    for filename in os.listdir(DIR_NAME):
        if filename.endswith('summary.txt'):
            with open(DIR_NAME + '/' + filename, 'r') as f_sum:
                f_sum.seek(0)
                summary = json.loads(f_sum.readline()[:-1]) # TODO fix this to load integers intead of strings
                for i in range(-3, 4):
                    super_summary[str(i)] += summary[str(i)]
            f_sum.close()
    with open(SUMMARY_FILE.format(name_server, '-1'), 'w') as f_super:
        f_super.write(write_parseable_summary(super_summary))
    f_super.close() 
    print(super_summary)

if __name__=='__main__':
    if (len(sys.argv) < 3):
        raise 'USAGE: merge_summaries [name_server] [verification_mode]'
    verification_mode = sys.argv[2]
    if verification_mode not in VERIFICATION_MODES:
        raise 'ERROR: invalid verification_mode'
    name_server = sys.argv[1]
    merge_summaries_auto(name_server, verification_mode)
