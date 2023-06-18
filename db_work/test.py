#!/usr/bin/env python3
import argparse
import sys

import work.therapeutic_accelerator.old.get_papers as get_papers

pmid_file = "pmid-p53-set.txt"
output = "papers.csv"
fields = ['corpusId', 'abstract']

args = argparse.Namespace(pmid_file=pmid_file, output=output, fields=fields)
get_papers.main(args)

with open(pmid_file, 'r') as file:
    expected_count = len(file.readlines())

with open(output, 'r') as file:
    actual_count = len(file.readlines())

# For occasionally verifying this script, error if we don't find enough records.
if actual_count < expected_count * 0.98:
    print(f'Too many records missing. S2, please investigate.')
    sys.exit(1)