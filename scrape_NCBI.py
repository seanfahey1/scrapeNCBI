#!/usr/bin/env python3

import http.client
import json
import logging
import sys
from pathlib import Path
from time import sleep
from urllib.error import HTTPError

from Bio import Entrez

import config  # requires config.py file with Entrez credentials.

logging.basicConfig(filename="info.log", level=logging.DEBUG)

Entrez.email = config.email
Entrez.api_key = config.api_key


def get_search(term_list):
    terms = " OR ".join([f"{x}[Title]" for x in term_list])
    query = (
        f"({terms}) AND phage[Title] NOT hypothetical[Title] NOT putative[Title] NOT putitive[Title] "
        f"NOT probable[Title] NOT possible[Title] NOT unknown[Title] AND 50:1000000[SLEN]"
    )

    with Entrez.esearch(
        db="protein", term=query, idtype="acc", usehistory="y"
    ) as handle:
        search_results = Entrez.read(handle)
    return search_results


def get_sequences(
    search_results,
    out_file,
    batch_size=200,
    start_batch=0,
    json_dict=None,
    key=None,
    write=False,
):
    webenv = search_results["WebEnv"]
    query_key = search_results["QueryKey"]
    count = int(search_results["Count"])

    with open(out_file, "a") as out:
        for start in range(start_batch, count, batch_size):
            logging.info(
                f"\t{key} - start: {start}, end: {start + batch_size}, total: {count}"
            )
            sleep(10)

            attempt = 0
            while attempt < 20:
                try:
                    fetch_handle = Entrez.efetch(
                        db="protein",
                        rettype="fasta",
                        retmode="text",
                        retstart=start,
                        retmax=batch_size,
                        webenv=webenv,
                        query_key=query_key,
                        idtype="acc",
                    )
                    attempt = 0
                    break
                except HTTPError as err:
                    attempt += 1
                    logging.error(
                        f"{key} - start: {start} | Received HTTP error. Attempt number {attempt}"
                    )
                    logging.error(err)
                    sleep(15 * attempt)

                except ValueError as err:
                    attempt += 1
                    logging.error(
                        f"{key} - start: {start} | Received urllib HTTP error. Attempt number {attempt}"
                    )
                    logging.error(err)
                    sleep(180)

                except Exception as err:
                    attempt += 1
                    logging.error(
                        f"UNCAUGHT EXCEPTION!!! | {key} - start: {start} | attempt number {attempt}"
                    )
                    logging.error(err)
                    logging.error(f"skipping the following ids:")
                    logging.error("\t".join(search_results.get("IdList")))
                    continue

            if attempt >= 20:
                logging.error("Reached max number of attempts in a row without success")
                raise HTTPError

            data = fetch_handle.read()
            fetch_handle.close()
            out.write(data)

            if write and key is not None and json_dict is not None:
                json_dict[key]["completed"] = start + batch_size
                with open("terms.json", "w") as json_in:
                    json.dump(json_dict, json_in, indent=2, sort_keys=True)


def main(dry_run=False):
    logging.info("Starting...")
    with open("terms.json", "r") as json_in:
        terms = json.load(json_in)

    for key, dictionary in terms.items():
        term_list = dictionary.get("labels")
        start = dictionary.get("completed")

        logging.info(f"Starting key: {key}")
        out_path = Path(f"{key}.fasta")

        search_results = get_search(term_list)

        if not dry_run:
            get_sequences(
                search_results,
                out_file=out_path,
                start_batch=start,
                json_dict=terms,
                key=key,
                write=True,
            )

        else:
            logging.info(f"Count = {search_results.get('Count')}")
            print(search_results.get("Count"))


if __name__ == "__main__":
    sys.exit(main())
