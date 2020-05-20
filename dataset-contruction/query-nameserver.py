import json # for loading api responses
import requests # for sending api requests
import threading # for threads
import time # for time info
import os # to create directories
# import fileinput
import dns.name
import dns.query
import dns.dnssec
import dns.message
import dns.resolver
import dns.rdatatype
from config import TOKEN

NS = 'citynetwork.se'
# url for api calls to host.io
URL = 'https://host.io/api/domains/ns/{}?limit={}&page={}&token={}'
DIR_NAME = '{0}-scan'
INPUT_FILE = '{0}-scan/{0}-domains-{1}-input.txt'
OUTPUT_FILE = '{0}-scan/{0}-domains-{1}-output.txt'
SUMMARY_FILE = '{0}-scan/{0}-domains-{1}-summary.txt'

# gets and validates the DNSKEY
# returns:
#   0 if query for DNSKEY fails
#   1 if no DNSKEY RRSIG is returned and cannot validate
#   2 if DNSKEY is returned and validated
#   -1 if failed validation
#   -2 some other error (domain/ nameserver wasn't resolved, ect)
#   > 2, something went wrong. Too many records were returned
def verify_dnskey(domain):
    # get namserver for domain
    res = None
    try:
        res = dns.resolver.query(domain, dns.rdatatype.NS)
    except:
        # Domain could not be resolved
        return -2
    nsname = res.rrset[0].to_text() # name
    # find nameserver address
    try:
        res = dns.resolver.query(nsname, dns.rdatatype.A)
    except:
        return -2
    nsaddr = res.rrset[0].to_text() # IPv4
    # get DNSKEY for zone
    # corresponds to: 'dig +dnssec DNSKEY {domain}'
    # note that dig on many websites including example.com
    # does not succeed because the RRSIG for DNSKEY is not returned
    req = dns.message.make_query(
            domain,
            dns.rdatatype.DNSKEY,
            want_dnssec=True)
    # send query
    res = dns.query.udp(req, nsaddr)
    if res.rcode() != 0:
        # query failed
        return 0
    # answer should be two RRSETS: DNSKEY and RRSIG (DNSKEY)
    ans = res.answer
    if len(ans) != 2:
        # answer probably didn't respond with DNSKEY RRSIG
        if len(ans) > 2:
            return 3
        else:
            return len(ans)
    # the DNSKEY should be self signed, validate it
    name = dns.name.from_text(domain)
    try:
        dns.dnssec.validate(ans[0],ans[1], {name: ans[0]})
    except dns.dnssec.ValidationFailure:
        # failed validation
        return -1
    except AttributeError:
        return -1
    else:
        # SUCCESS
        return 2

def format_summary(summary):
    return '''summary of results:
        # domains that didn't exist       : {nxdomain}
        # domains that failed verificaiton: {failure}
        # failed queries                  : {query_fail}
        # domains missing RRSIG           : {missing}
        # responded with too many records : {too_many}
        # successful verifications        : {success}
    '''.format(
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
    -2: DNS query responded with NXDOMAIN
    -1: DNSSEC verification failed
    0 : query failed for some other reason
    1 : domain responeded without the RRSIG record
    2 : DNSSEC verification was successful
    3 : too many records were returned
record summary of results to summary_file
'''
def verify_domains(input_file, output_file, summary_file, verbose=False):
    if verbose:
        print('======= STARTING ========')
    start_time, round_start_time = time.time(), time.time()
    count, summary = 0, {-2: 0, -1: 0, 0: 0, 1: 0, 2: 0, 3: 0} 
    with open(output_file, 'w') as f_out:
        with open(input_file, 'r') as f_in:
            for dom in f_in:
                dnssec_res = verify_dnskey(dom[:-1])
                summary[dnssec_res] += 1
                f_out.write('{} {}\n'.format(dom, dnssec_res))
                count += 1
                if (count % 20 == 0 and verbose):
                    print('----- done processing {} domains, round took {} seconds------'
                            .format(count, round(time.time() - round_start_time, 3)))
                    round_start_time = time.time()
        f_in.close()
    f_out.close()
    with open(summary_file, 'w') as f_sum:
        f_sum.write(format_summary(summary))
        f_sum.write('elapsed time: {} seconds'.format(time.time() - start_time))
    f_sum.close()
    if verbose:
        print(format_summary(summary))
        print('number of doms: ', count)
        print('elapsed time: {} seconds'.format(time.time() - start_time))
        print('======= ENDING ========')

def get_total_doms():
    res = requests.get(URL.format(NS, 1, 0, TOKEN))
    if (res.status_code != 200):
        raise ValueError('status code {} returned from requst {}'.format(res.status_code))
    res = json.loads(res.content.decode('utf-8'))
    return res['total']

def verify_nameserver_domains(name_server):
    doms_per_file = 250
    tot = get_total_doms()
    total_pages = int((tot - 1) / doms_per_file) + 1
    for i in range(total_pages):
        with open(INPUT_FILE.format(name_server, i), 'w') as f:
            res = requests.get(URL.format(name_server, doms_per_file, i, TOKEN))
            if (res.status_code != 200):
                raise ValueError('status code {} returned from request'.format(res.status_code))
            res = json.loads(res.content.decode('utf-8'))
            for dom in res['domains']:
                f.write('{}\n'.format(dom))
        f.close()
        # TODO make this a thread call
        verify_domains(
                INPUT_FILE.format(name_server, i),
                OUTPUT_FILE.format(name_server, i),
                SUMMARY_FILE.format(name_server, i),
                verbose=True)
    # TODO wait for threads and merge all files together


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
        verify_nameserver_domains(NS)
    except FileExistsError:
        print('''
        {}/ already has been made!
        Have you already scaned this nameserver? If so, then no need to 
        scan again! If you want new results, move the existing directory
        or rename it maybe
        '''.format(DIR_NAME.format(NS)))

