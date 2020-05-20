## Nameserver Scan

Scan the domains that a nameserver is authoritative for in order to verify
the usage of DNSSEC. 
In particular, check if it has a present DNSKEY and that the key can be
verified by a present RRSIG.

### Technologies:

- dataset of domains that a name-server is authoritative for is not
publicly accessible or queryable. We rely on `Host.io` for this information,
using a free tier api
- DNS domains are verified through dig commands built through python's `dns'
module

### To Run


TODO : make this more use interactive

currently, change NS variable in `query-nameserver.py` in order to pick the
nameserver that will be queried.
