#!/usr/bin/env python3

import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd
from Bio import SeqIO


def extract(fasta, list_file):
    with open(list_file, "w") as out:
        with open(fasta) as handle:
            for record in SeqIO.parse(handle, "fasta"):
                description = record.description
                short_description = description.strip(record.name).strip(' ')
                out.write(short_description)
                out.write("\n")


def make_table(list_file, tsv_file):
    with open(list_file, "r") as term_list:
        terms = term_list.read().split('\n')
    term_dict = defaultdict(lambda: 0)
    for term in terms:
        term_dict[term] += 1

    df = pd.DataFrame.from_dict(term_dict, orient='index', columns=['count'])
    df.index.rename('description', inplace=True)
    df.sort_values('count', inplace=True, ignore_index=False, ascending=False)

    with open(tsv_file, "w") as csv_output:
        csv_output.write(df.to_csv(sep='\t'))


def main():
    files = list(Path('.').glob("*.fasta"))
    for file in files:
        prefix = file.stem
        list_file = f"{prefix}.list"
        tsv_file = f"{prefix}.tsv"

        extract(file, list_file)
        make_table(list_file, tsv_file)


if __name__ == "__main__":
    sys.exit(main())
