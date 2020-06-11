#!python 3
import json # for loading api responses
import requests # for sending api requests
import threading # for threads
import queue # for producer / consumer workload
import time # for time info
import queue
import os # to create directories
# import fileinput
import dns.name
import dns.query
import dns.dnssec
import dns.message
import dns.resolver
import dns.rdatatype
from config import TOKEN
# other files
from verifications import verify_dnskey
from verifications import verify_ds
from verifications import verify_ds_and_dnskey
from merge_summaries import merge_summaries
from merge_summaries import write_parseable_summary

# NS = 'akam.net'# 'godaddy.com' # 'citynetwork.se'
NS = 'name-s.net'#'binero.se' #'transip.nl' # 'transip.net' #'hyp.net' # 'loopia.se' # 'ovh.net'# 'pcextreme.ml' #'is.nl'# 'wix.com'

VERIFICATION_MODE = 'DS_DNSKEY'
VERIFICATION_MODES = {
        'DNSKEY': verify_dnskey,
        'DS': verify_ds,
        'DS_DNSKEY': verify_ds_and_dnskey
        }
# url for api calls to host.io
URL = 'https://host.io/api/domains/ns/{}?limit={}&page={}&token={}'
DIR_NAME = '{}-'.format(VERIFICATION_MODE) + '{0}-scan'
INPUT_FILE = '{}-'.format(VERIFICATION_MODE) + '{0}-scan/{0}-domains-{1}-input.txt'
OUTPUT_FILE = '{}-'.format(VERIFICATION_MODE) + '{0}-scan/{0}-domains-{1}-output.txt'
SUMMARY_FILE = '{}-'.format(VERIFICATION_MODE) + '{0}-scan/{0}-domains-{1}-summary.txt'

LIMIT_ON_ACTIVE_THREADS = 20


def format_summary(summary):
    return '''summary of results:
        # dnsec query timeouts            : {timeouts}
        # domains that didn't exist       : {nxdomain}
        # domains that failed verificaiton: {failure}
        # failed queries                  : {query_fail}
        # domains missing RRSIG           : {missing}
        # responded with too many records : {too_many}
        # successful verifications        : {success}
    '''.format(
        timeouts = summary[-3],
        nxdomain = summary[-2],
        failure = summary[-1],
        query_fail = summary[0],
        missing = summary[1],
        too_many = summary[3],
        success = summary[2])


'''
dig for DNS key of each domain specified in input_file,
output results of each query to output_file in the form:
    {domain} {res}
where res can have the following meanings:
    -3: DNSSEC query timeout
    -2: DNS query responded with NXDOMAIN
    -1: DNSSEC verification failed
    0 : query failed for some other reason
    1 : domain responeded without the RRSIG record
    2 : DNSSEC verification was successful
    3 : too many records were returned
record summary of results to summary_file

this function is run through a thread, so as to parallelize the writes
to files
'''
def verify_domains(name_server, thread_i, verbose=False, taciturn=False, 
        verification_mode=VERIFICATION_MODES[VERIFICATION_MODE]):
    input_file = INPUT_FILE.format(name_server, thread_i)
    output_file = OUTPUT_FILE.format(name_server, thread_i)
    summary_file = SUMMARY_FILE.format(name_server, thread_i)
    if verbose or taciturn:
        print('======= STARTING thread {} ========'.format(thread_i))
    start_time, round_start_time = time.time(), time.time()
    count, summary = 0, {-3: 0, -2: 0, -1: 0, 0: 0, 1: 0, 2: 0, 3: 0} 
    with open(output_file, 'w') as f_out:
        with open(input_file, 'r') as f_in:
            for dom in f_in:
                dom = dom[:-1] # remove newline
                dnssec_res = verification_mode(dom)
                summary[dnssec_res] += 1
                f_out.write('{} {}\n'.format(dom, dnssec_res))
                count += 1
                if (count % 20 == 0 and verbose):
                    print('----- done processing {} domains in thread {}, round took {} seconds------'
                            .format(count, thread_i, round(time.time() - round_start_time, 3)))
                    round_start_time = time.time()
        f_in.close()
    f_out.close()
    with open(summary_file, 'w') as f_sum:
        f_sum.write(write_parseable_summary(summary))
        f_sum.write(format_summary(summary))
        f_sum.write('elapsed time: {} seconds'.format(round(time.time() - start_time, 3)))
    f_sum.close()
    if verbose:
        print(format_summary(summary))
        print('number of doms: ', count)
    if verbose or taciturn:
        print('======= FINISHED thread {} in {} seconds ========'.format(thread_i, round(time.time() - start_time, 3)))

'''
query the API once in order to get the number of total number of domains
that need to be 'dig'ed
'''
# TODO : this can be optimized away
def get_total_doms():
    res = requests.get(URL.format(NS, 1, 0, TOKEN))
    if (res.status_code != 200):
        raise ValueError('status code {} returned from requst {}'.format(res.status_code))
    res = json.loads(res.content.decode('utf-8'))
    return res['total']


'''
verify each domain that points to name_server, as according to host.io
done through writes to files, so that failure does not lose work
'''
# TODO allow this function to start at an arbitary page instead of 0
# allows to use multiple access tokens over the same scan
def verify_nameserver_domains(name_server, 
        doms_per_query=1000, doms_per_thread=25, starting_page=0,
        use_threads=True, verbose=False):
    tot = get_total_doms()
    total_queries = int((tot - 1) / doms_per_query) + 1
    threads  = []
    start_time = time.time()
    if verbose:
        print('\n +=+=+=+=+=+ STARTING NAMESERVER SCAN of {} +=+=+=+=+=+ \n'.format(name_server))
    for query_i in range(starting_page, total_queries):
        res = requests.get(URL.format(name_server, doms_per_query, query_i, TOKEN))
        if (res.status_code != 200):
            raise ValueError('status code {} returned from request for query'.format(res.status_code, query_i))
        res = json.loads(res.content.decode('utf-8'))
        # write response to doms_per_query / doms_per_file seperate files
        needed_threads = min(
                int(doms_per_query/doms_per_thread), 
                int(len(res['domains']) / doms_per_thread))
        for thread_i in range(needed_threads):
            thread_id = int(query_i * (doms_per_query/ doms_per_thread) + thread_i)
            with open(INPUT_FILE.format(name_server, thread_id), 'w') as f:
                for dom_i in range(
                        thread_i * doms_per_thread, 
                        min((thread_i + 1) * doms_per_thread, len(res['domains']))
                        ):
                    dom = res['domains'][dom_i]
                    f.write('{}\n'.format(dom))
            f.close()
            threads.append(
                    threading.Thread(
                        target=verify_domains,
                        args=(name_server, thread_id),
                        kwargs=dict(verbose=False, taciturn=verbose)
                    )
                )

            threads[-1].start()
            if not use_threads:
                threads[-1].join()
            # TODO this should have been implemented with a master slave threading style
            if threading.active_count() >= LIMIT_ON_ACTIVE_THREADS:
                for t in threads:
                    t.join()
                threads = []
    for t in threads:
        t.join()
    if verbose:
        print('\n +=+=+=+=+=+ FINISHED NAMESERVER SCAN of {} in {} seconds+=+=+=+=+=+ \n'.format(name_server, round(time.time() - start_time, 3)))
    if verbose:
        print('\n +=+=+=+=+=+ STARTING MERGE of SUMMARIES for {} +=+=+=+=+=+ \n'.format(name_server))
    number_of_files = int(tot / doms_per_thread)
    merge_summaries(name_server, number_of_files, SUMMARY_FILE)

if __name__=='__main__':
    try:
        TOKEN
    except NameError:
        print('''
        TOKEN is not defined!!!
        Go to host.io to get an api token. Then add it to a file named config.py
        in this directory in order to run this program
        ''')
        exit(1)
    try:
        os.mkdir(DIR_NAME.format(NS))
        verify_nameserver_domains(NS, doms_per_query=1000, doms_per_thread=10, use_threads=True, verbose=True)
    except FileExistsError:
        print('''
        {}/ already has been made!
        Have you already scaned this nameserver? If so, then no need to 
        scan again! If you want new results, move the existing directory
        or rename it maybe
        '''.format(DIR_NAME.format(NS)))

