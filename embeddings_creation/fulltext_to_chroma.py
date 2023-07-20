#! /usr/bin/env python

from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel

# from IPython.display import Markdown, display

from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import ChromaVectorStore
from llama_index import VectorStoreIndex, SimpleDirectoryReader

from chromadb.utils import embedding_functions
from chromadb.config import Settings
import chromadb

from langchain.text_splitter import CharacterTextSplitter

import pandas as pd
import sqlalchemy as sa

from transformers import T5Tokenizer

import dask
from dask import dataframe as dd
from dask.diagnostics import ProgressBar
import dask.distributed as distributed

import warnings
import logging

import yaml

# set up
with open("/home/ubuntu/work/therapeutic_accelerator/config/main.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

with open("/home/ubuntu/work/therapeutic_accelerator/config/keys.yaml", "r") as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)


if __name__ == "__main__":
    # Launches a scheduler and workers locally
    cluster = distributed.LocalCluster(
        name='local', n_workers=7, memory_limit='4GiB', threads_per_worker=4)
    client = distributed.client._get_global_client() or distributed.Client(cluster)

    print("-" * 20, "\n", client, "\n", "-" * 20)


    max_sequence_length = 1200
    embedding_size = 200

    # Create tokenizer for T5 model
    T5tokens = T5Tokenizer.from_pretrained(
        't5-base', model_max_length=max_sequence_length)

    # Create dask cluster
    # overwrite default with multiprocessing scheduler
    # dask.config.set(scheduler='processes')


    # # Create Embeddings

    def token_len(text):
        """ Get the length of tokens from text"""
        tokens = T5tokens.encode(text)
        return len(tokens)


    chunk_size = 2000

    # create text splitters for processing the texts
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=chunk_size,
        chunk_overlap=20,
        length_function=token_len
    )

    # ## Now with Dask
    # Functions to clean up dataframes
    def split_text(ddf):
        """ Split text into chunks """
        return ddf['text'].apply(text_splitter.split_text)


    def create_doc(split_text, corpusid):
        """ Create documents for each chunk """

        try:
            docs = {
                # list of all documents [doc1, doc2, doc3, ...]
                "documents": split_text,
                # list of all ids [id1, id2, id3, ...]
                'ids': [f'{corpusid}-{i}' for i in range(len(split_text))],
                # list of dictionaries with metadata for each document
                'metadatas': [{'corpusid': int(corpusid), 'chunk': i} for i in range(len(split_text))]
            }
            return docs

        except Exception as e:
            logging.error(e)


    def mp_create_doc(ddf):
        """ Used for mapping partitions"""
        return ddf.apply(lambda x: create_doc(x['split_text'], x['corpusid']), axis=1)


    def add_to_collection(text, corpusid):

        doc = create_document(text, corpusid)

        try:
            dask.delayed(collection.add)(**doc)
        except Exception as e:
            logging.error(e)


    # Read in fulltext from csvs for dask
    ft = dd.read_parquet('/home/ubuntu/work/data/fulltext_parquets/fulltext-*.parquet', sample=10000000,
                        sample_rows=10,
                        lineterminator=None,
                        dtype={'corpusid': 'int', 'text': 'object'})

    # Cleanup dataframes
    ft = ft.map_partitions(pd.DataFrame.dropna, subset='text')

    ft = ft.map_partitions(pd.DataFrame.drop_duplicates, subset='text')

    ft = ft.map_partitions(pd.DataFrame.reset_index, drop=True)

    ft = ft.persist()

    # split the text into chunks
    ft_test = ft.assign(split_text=ft.apply(lambda x: dask.delayed(
        text_splitter.split_text)(x['text']), axis=1, meta=('split_text', 'object')))

    # Don't need text col anymore
    ft_test = ft_test.drop(columns=['text'])


    @dask.delayed
    def create_doc(split_text, corpusid):
        """Create Documents for Each Chunk 

        Returns:
            _type_: _description_
        """

        doc = {
            # list of all documents [doc1, doc2, doc3, ...]
            "documents": split_text,
            # list of all ids [id1, id2, id3, ...]
            'ids': [f'{corpusid}-{i}' for i in range(len(split_text))],
            # list of dictionaries with metadata for each document
            'metadatas': [{'corpusid': int(corpusid), 'chunk': i} for i in range(len(split_text))]
        }
        return doc


    # Create documents
    ft_docs = ft_test.apply(lambda df: create_doc(
        df['split_text'], df['corpusid']), axis=1, meta=('documents', 'object'))
    ft_docs = ft_docs.persist()

    ft_docs.to_delayed()[0].compute()

    ft_docs.to_delayed()[0].compute()[0].compute()


    # # Llama Indexing for Chroma
    # Create chroma client

    chroma_client = chromadb.Client(Settings(chroma_api_impl="rest",
                                    chroma_server_host="18.233.156.143",  # EC2 instance public IPv4
                                    chroma_server_http_port=8000))

    # returns a nanosecond heartbeat. Useful for making sure the client remains connected.
    print("Nanosecond heartbeat on server", chroma_client.heartbeat())

    # Check Existing connections
    chroma_client.list_collections()
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    collection = chroma_client.get_or_create_collection("fulltext")


    # Add documents to collection
    def add_to_collection(docs):
        """ Add documents to collection """
        try:
            collection.add(**docs)
        except Exception as e:
            logging.error(e)


    for d in tqdm(ft_docs.to_delayed()):
        # gets the dataframe from the delayed object
        d.compute().apply(lambda x: add_to_collection(x.compute()))

    ft_docs.apply(add_to_collection, axis=1, meta=('docs', 'object'), pure=False)
