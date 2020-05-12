# Readings

These are various readings that may be useful to us.

- Illustrated Guide to the Kaminsky DNS Vulnerability
  - defines a DSN vulnerability that DNSSEC aims to defend against
- How DNSSEC Works - Cloudflare
  - Best resource for details how DNSSEC works
- RFC 1035
  - An initial RFC for DNS
  - defines the exact structure of DNS records (A, AAAA, ect.)
- RFC 4034
  - An initial RFC for DNSSEC
  - defines the exact stucture for DNSSEC records (DNSKEY, RRSIG, DS, ect.),
  which is vital for understanding the response from a call to 
  `dig github.com any` or any other method of receiving records.
- The DNSSEC Root Signing Ceremony - Cloudflare
  - Just a fun article on how they create the private / public key for the
  root zone.

