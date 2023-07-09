#! usr/bin/env python

from dask import delayed
import logging
from chromadb.utils import embedding_functions
from chromadb.config import Settings
import chromadb
from langchain.text_splitter import CharacterTextSplitter
from dask.distributed import Client, LocalCluster
import pandas as pd

from transformers import T5Tokenizer

from dask import dataframe as dd
from dask.diagnostics import ProgressBar

from dask.distributed import Client, TimeoutError

import warnings 

def token_len(text):
    """ Get the length of tokens from text"""
    tokens = T5tokens.encode(text)
    return len(tokens)

# Create collection to store embeddings with T5 sentence transformer
def create_collection(chroma, name, metadata={"hnsw:space": "cosine"}, embedding_function=default_ef):
    try:
        chroma.create_collection(
            name=name, metadata=metadata, embedding_function=embedding_function)
    except Exception as e:
        logging.error(e)
        


def create_document(texts, corpusid):
    # create metadatas
    metadatas = [{
        'corpusid': int(corpusid),
        'chunk': i
    } for i in range(len(texts))]

    ids = [f'{corpusid}-{i}' for i in range(len(texts))]

    try:
        docs = {
            # list of all documents [doc1, doc2, doc3, ...]
            "documents": texts,
            'ids': ids,  # list of all ids [id1, id2, id3, ...]
            'metadatas': metadatas  # list of dictionaries with metadata for each document
        }
        return docs

    except Exception as e:
        logging.error(e)


@delayed
def add_to_collection(doc):
    try:
        collection.add(**doc)
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    
    warnings.filterwarnings('ignore')

    max_sequence_length = 1200
    embedding_size = 200

    # Create tokenizer for T5 model
    T5tokens = T5Tokenizer.from_pretrained(
        't5-base', model_max_length=max_sequence_length)

    cluster = LocalCluster(name='local', n_workers=12, memory_limit='2GiB',
                        threads_per_worker=2)  # Launches a scheduler and workers locally
    try:
        client = Client(cluster, timeout='2s')
    except TimeoutError:
        pass
    print("-" * 20, client , "-" * 20)

    chunk_size = 1200

    # create text splitters for processing the texts
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=chunk_size,
        chunk_overlap=20,
        length_function=token_len
    )

    chroma = chromadb.Client(Settings(chroma_api_impl="rest",
                                    chroma_server_host="54.175.241.78",  # EC2 instance public IPv4
                                    chroma_server_http_port=8000))

    # returns a nanosecond heartbeat. Useful for making sure the client remains connected.
    print("Nanosecond heartbeat on server", chroma.heartbeat())

    # Sentence Transformers all-MiniLM-L6-v2
    default_ef = embedding_functions.DefaultEmbeddingFunction()

    collection = chroma.get_or_create_collection("fulltext")
        
        
    # Read in fulltext from csvs for dask
    ft = dd.read_csv('/home/ubuntu/work/data/fulltext_csvs/fulltext-*.csv', sample=10000000,
                    sample_rows=10,
                    lineterminator=None,
                    dtype={'corpusid': 'int', 'text': 'object'})

    ft = ft.map_partitions(pd.DataFrame.drop, columns='id',)
    ft = ft.map_partitions(pd.DataFrame.dropna, subset='text')
    ft = ft.map_partitions(pd.DataFrame.reset_index, drop=True)

    # split the text in partitions
    ft = ft.map_partitions(lambda df: df.assign(text=df['text'].apply(text_splitter.split_text)),
                        meta={'corpusid': 'int', 'text': 'object'})

    # create documents
    ft = ft.map_partitions(lambda df: df.assign(docs=df[['text', 'corpusid']].apply(lambda x: create_document(x[0], x[1]), axis=1)),
                        meta={'corpusid': 'int', 'text': 'object', 'docs': 'object'})

    futures = ft['docs'].apply(
        add_to_collection, meta=('docs', 'object')).to_delayed()
    results = client.compute(futures)

    futures = ft['docs'].apply(
        add_to_collection, meta=('docs', 'object')).to_delayed()

    results = client.compute(futures)
        
    client.close()
    cluster.close()