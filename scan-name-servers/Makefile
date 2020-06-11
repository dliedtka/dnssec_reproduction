#######################################
## MAKEFILE for Dataset Construction ##
#######################################

TEST-SITE:= citynetwork.se
TEST-FOLDER:=$(TEST-SITE)-scan/

test:
	rm -rf $(TEST-FOLDER)
	python query-nameserver.py 

move:
	cp DS_DNSKEY-*-scan/*--1-summary.txt ./analysis/results_DS_DNSKEY
