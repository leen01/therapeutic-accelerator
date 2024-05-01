#!usr/bin/ python

import duckdb
import requests
import urllib
import os
from urllib.request import urlretrieve, urlcleanup
from tqdm import tqdm
import re
from dotenv import dotenv_values
from pathlib import Path

cwd = Path(__file__).parent
root_dir_name = "therapeutic_accelerator"
root_dir_path = Path(
    *cwd.parts[: cwd.parts.index("therapeutic_accelerator") + 1])

config = dotenv_values(str(Path(root_dir_path, ".env-secrets")))


def get_dataset_semantic(dataset_id):
    base_url = "http://api.semanticscholar.org/datasets/v1/release/latest/dataset/"
    return requests.get(
        base_url + dataset_id, headers={"x-api-key": config["semantic"]}
    ).json()

def download_gz(url_list, out_dir):
    # # download files
    for url in tqdm(url_list):
        try: 
            url_parsed = urllib.parse.urlparse(url)
            out_file = Path(out_dir, Path(url_parsed.path).stem + ".json.gz")
            if not out_file.exists():
                print(out_file)
                url_path, message = urlretrieve(url, out_file)
                urlcleanup()
            else:
                print("Path exists for: ", out_file)
        except: 
            pass


papers_metadata = get_dataset_semantic("papers")

data_dir = Path(root_dir_path, "data/papers_metadata/")
data_dir.mkdir(
    parents=True, exist_ok=True
)

download_gz(papers_metadata["files"], data_dir)

# full text
full_text = get_dataset_semantic("s2orc")

data_dir = Path(root_dir_path, "data/fulltext-zipped/")

data_dir.mkdir(
    parents=True, exist_ok=True
)

download_gz(full_text["files"], data_dir)

