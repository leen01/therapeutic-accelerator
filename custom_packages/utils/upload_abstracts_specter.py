#! usr/bin/env python
import warnings
import tensorflow as tf
import os
import torch
from transformers import AutoModel, AutoTokenizer
from dask.diagnostics import ProgressBar
from dask import distributed, dataframe as dd
from dask.distributed import TimeoutError, KilledWorker
import dask
from tqdm.notebook import tqdm_notebook
from tqdm import tqdm
import ast
import re
import logging
import numpy as np
import pandas as pd
import sys


# sys.path.append(
#     "/home/ubuntu/work/therapeutic_accelerator/custom_packages/utils")
# sys.path.append(
#     "/home/ubuntu/work/therapeutic_accelerator/custom_packages/database")

from utils import import_config
from db_tools import db_connection
import chromaDB as cbd  # specter_ef, create_text_splitter, create_chroma_client

# hide warnings

def remove_exisiting(df):
    """ Remove existing ids from dataframe """
    # get unique ids from collection that are the corpus ids
    existing_ids = np.unique(pd.DataFrame(collection.get(include=['metadatas']))['ids'].str.split(
        '-', expand=True).rename(columns={0: 'id', 1: 'part'})['id'].tolist()).tolist()
    print('N existing ids: ', len(existing_ids))
    print(df.shape)

    df = df[~df['corpusId'].astype(str).isin(existing_ids)]

    print(df.shape)

    return df

def create_ids_metadatas(corpusid, num_chunks):
    """ Create ids for each chunk """

    ids = [f"{corpusid}-{i}" for i in range(num_chunks)]

    metadatas = [{'corpusid': corpusid, 'chunk': i} for i in range(num_chunks)]

    return ids, metadatas


def process_dict(d):

    corpusid = d['corpusId']

    documents = specter_embeder.split_text(d['documents'])

    ids, metadatas = create_ids_metadatas(corpusid, len(documents))

    embeddings = specter_embeder.embed_documents(documents)

    new_dict = {
        'ids': ids,
        'documents': documents,
        'metadatas': metadatas,
        'embeddings': embeddings
    }

    try:
        collection.upsert(**new_dict)
        return True
    except:
        return False


if __name__ == "__main__":
    
    # Disable TensorFlow INFO and WARNING messages
    # os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    # tf.get_logger().setLevel('ERROR')  # Disable TensorFlow ERROR messages (optional)

    # Filter out Dask client warnings
    warnings.filterwarnings("ignore")

    config, keys = import_config()

    # Chroma setup --------------------------------------------------------------------------------
    chroma_server_host = "3.86.216.30"
    
    chroma_client = cbd.create_chroma_client(chroma_server_host)

    # Modelish stuff --------------------------------------------------------------------------------

    model = AutoModel.from_pretrained("allenai/specter")
    
    tokenizer = AutoTokenizer.from_pretrained("allenai/specter")

    # Create embeddings function with specter model
    specter_embeder = cbd.specter_ef(model, tokenizer)

    specter_embeder.create_text_splitter()

    # Working Collection
    collection = chroma_client.get_or_create_collection(
        "specter_abstracts", embedding_function=specter_embeder)
    
    abstracts = pd.read_csv("/home/ubuntu/work/data/abstracts.csv")

    abstracts = remove_exisiting(abstracts)

    # # Dask functions
    # Create dask cluster
    # overwrite default with multiprocessing scheduler
    dask.config.set(scheduler='processes')

    # Launches a scheduler and workers locally
    cluster = distributed.LocalCluster(
        name='local', n_workers=5,
        memory_limit='5GiB',
        threads_per_worker=1, 
        retries=10)

    client = distributed.Client(cluster, ip='http://127.0.0.1:8787')

    print('-' * 20)
    print(client)
    print('-' * 20)

    # # Add documents to collection

    # ab_tester = abstracts.iloc[:10000, :]
    n_partitions = len(abstracts) // 100
    print(n_partitions)

    abstracts_dict = abstracts.to_dict('records')

    chunked_abstracts = np.array_split(abstracts_dict, n_partitions)

    partition_size = 10

    for i in tqdm(range(len(chunked_abstracts)), desc='chunk'):

        dict_chunk = chunked_abstracts[i]

        futures = [dask.delayed(process_dict)(d) for d in dict_chunk]

        num_partitions = len(futures)//partition_size

        futures_split = np.array_split(futures, num_partitions)

        for j in tqdm(range(len(futures_split)), leave=True, desc='partition'):

            fs = futures_split[j]
            try: 
                results = dask.compute(*fs, optimize_graph=True)
                del results
                
            except TimeoutError:
                print('TimeoutError')
                continue
            
            except KilledWorker as e:
                # Handle the KilledWorker error here
                # You can perform cleanup, logging, or take appropriate action
                print("A Dask worker was killed:", e)
                pass
            
        client.restart()

        del dict_chunk, futures, futures_split

    # Optionally, you can close the Dask client after your computation is done
    client.close()
