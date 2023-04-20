# scrapeNCBI

## Setup

1. python3 -m venv .venv
2. source .venv/bin/activate
3. pip install -U pip
4. pip install -r requirements.txt
5. create config.py file with Entrez credentials in the following format:
```
    api_key = "[API KEY HERE]"
    email = "[email/username]"
```
6. Alter the terms.json file to match the desired search terms
7. python3 scrapeNCBI.py

## Purpose

This tool will search the online NCBI database using the Entrez biopython library for phage protein sequences with 
titles that match one of the labels in the terms.json file. 

## Description

This script will produce one .fasta formatted file for each top level key in the terms.json file. Each label must 
appear in the __TITLE__ field, along with the term __PHAGE__. The tool also filters out any sequence with a title that 
match the terms __hypothetical__, __putative__, __putitive__ (due to frequent typos in the NCBI database) __probable__, 
__possible__, or __unknown__.

If NCBI returns an HTTP error, the script will continue retrying with progressively longer delays until 20 errors are
returned in a row.

If the script is stopped prematurely, it can be easily restarted with the same command. As long as the terms.json file
is not replaced, the script should pick up on the batch that it left off at.
