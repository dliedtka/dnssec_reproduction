import sys
import dns.name
import dns.query
import dns.dnssec
import dns.message
import dns.resolver
import dns.rdatatype
# gets and validates the DNSKEY
# returns:
#   0 if query for DNSKEY fails
#   1 if no DNSKEY RRSIG is returned and cannot validate
#   2 if DNSKEY is returned and validated
#   -1 if failed validation
#   -2 some other error (domain/ nameserver wasn't resolved, ect)
#   -3 timeout on dnssec query
def verify_dnskey(domain, verbose=False, max_wait_time=2):
    # get namserver for domain
    if verbose:
        print('domain scan of: {}'.format(domain))
    res = None
    try:
        res = dns.resolver.query(domain, dns.rdatatype.NS)
    except:
        # Domain could not be resolved
        return -2
    nsname = res.rrset[0].to_text() # name
    if verbose:
        print('name of NS: {}'.format(nsname))
    # find nameserver address
    try:
        res = dns.resolver.query(nsname, dns.rdatatype.A)
    except:
        return -2
    nsaddr = res.rrset[0].to_text() # IPv4
    if verbose:
        print('NS address: {}'.format(nsaddr))
    # get DNSKEY for zone
    # corresponds to: 'dig +dnssec DNSKEY {domain}'
    # note that dig on many websites including example.com
    # does not succeed because the RRSIG for DNSKEY is not returned
    req = dns.message.make_query(
            domain,
            dns.rdatatype.DNSKEY,
            want_dnssec=True)
    # send query
    try:
        res = dns.query.udp(req, nsaddr, timeout=max_wait_time)
    except dns.exception.Timeout:
        # timeout
        return -3
    except dns.message.TrailingJunk:
        # malformed dns packet
        return -3
    except:
        return -3

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
    except:
        -3
    else:
        # SUCCESS
        return 2

# verifies that we can get a DS record
# returns:
#   0 if DS record is not present
#   1 
#   2  if DS record present
#   -1
#   -2
#   -3
def verify_ds(domain, verbose=False, max_wait_time=2):
    # get namserver for domain
    if verbose:
        print('getting DS of: {}'.format(domain))
    res = None
    try:
        res = dns.resolver.query(domain, dns.rdatatype.DS)
    except:
        # Domain could not be resolved
        return 0
    return 2 # successfully got DS 

# verifies that we can get a DS record
# returns:
#   0 if DS record present and invlid DNSKEY present
#   1 if DNSKEY record present
#   2 if DS and DNSKEY records present
#   -1 if neither present
#   -2 if missing DS but has invlid DNSKEY
#   -3
def verify_ds_and_dnskey(domain, verbose=False, max_wait_time=2):
    dnskey = verify_dnskey(domain, verbose=False)
    if verbose:
        print('dnskey result = {}'.format(dnskey))
    ds = verify_ds(domain, verbose=False)
    if verbose:
        print('ds result = {}'.format(ds))
    if ds == 2 and dnskey == 2:
        return 2
    if ds == 2 and (dnskey == -1 or dnskey == -3):
        # dnskey present but failed validate, and ds present
        return 0
    if dnskey == 2:
        # dnskey present and validated, missing ds
        return 1
    if (dnskey == -1 or dnskey == -3):
        # missing ds and invalid dnskey
        return -2
    else:
        # missing both ds and dnskey
        return -1

if __name__=='__main__':
    if len(sys.argv) < 3:
        raise 'Not enough input args'
    domain = sys.argv[1]
    mode = sys.argv[2]
    if mode == 'verify_dnskey':
        print(verify_dnskey(domain, verbose=True))
    if mode == 'verify_DS':
        print(verify_DS(domain, verbose=True))
