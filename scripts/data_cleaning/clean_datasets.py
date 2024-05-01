import pandas as pd
# from metapub import PubMedFetcher
# import requests
# from semanticscholar import SemanticScholar
# import urllib
from pathlib import Path
import duckdb
import chardet
import numpy as np
import re

from dotenv import dotenv_values
config = dotenv_values('../../.env-secrets')
from glob import glob
import os
import re

cwd = Path(__file__).parent
root_dir_name = "therapeutic_accelerator"
root_dir_path = Path(
    *cwd.parts[: cwd.parts.index("therapeutic_accelerator") + 1])
config = dotenv_values(str(Path(root_dir_path, ".env-secrets")))


def isEnglish(s):
    try:
        s.encode(encoding='ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True

def extract_field_of_study(x): 
    if isinstance(x, np.ndarray): 
        return list(np.unique([i['category'] for i in x]))
    else: 
        return x

def load_df(file_path): 
    df = duckdb.sql(f"select * from '{file_path}'").fetchdf()
    return df

def cleaning_df(df): 
    df = df.drop(columns=['publicationvenueid'])
    df = df[df['isopenaccess']]
    df['is_english'] = df['title'].apply(isEnglish)
    df = df[df['is_english']] # assumption based on encoding
    df['title'] = df['title'].str.replace("\u2013", ' ')
    df['year'] = df['year'].fillna('').astype(str).str.strip('0').str.strip('.')
    df['eternalids'] = df['eternalids'].apply(lambda y: {k:v for k,v in y.items() if v})
    
    return df

def write_out_df(df, file_path): 
    parquet_file = re.sub('|'.join(Path(file_path).suffixes), '', str(Path(file_path)))  + '.parquet.gzip'
    print(parquet_file)
    df.to_parquet(parquet_file)
    
def main(file_path): 
    df = load_df(file_path)
    df = cleaning_df(df)
    write_out_df(df, file_path)
    
metadata_files = glob(str(root_dir_path) + '/data/papers_metadata/*.gz', recursive=True)

# fulltext_files = glob('../data/fulltext-zipped/*.gz', recursive=True)

pd.Series(metadata_files).map(main)

