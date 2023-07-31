
from transformers import AutoModel, AutoTokenizer
from utils import import_config
from db_tools import db_connection
import chromaDB as cbd  # specter_ef, create_text_splitter, create_chroma_client
import sys

import pandas as pd
import sqlalchemy as sa
import ast
from glob import glob
from tqdm import tqdm
import warnings
import logging

warnings.filterwarnings('ignore')

max_sequence_length = 1200
embedding_size = 200


config, keys = import_config()

# Chroma setup --------------------------------------------------------------------------------
chroma_server_host = "3.88.178.230"

chroma_client = cbd.create_chroma_client(chroma_server_host)

# Modelish stuff --------------------------------------------------------------------------------

model = AutoModel.from_pretrained("allenai/specter")
tokenizer = AutoTokenizer.from_pretrained("allenai/specter")

# Create embeddings function with specter model
specter_embeder = cbd.specter_ef(model, tokenizer)

specter_embeder.create_text_splitter()


# Working Collection
collection = chroma_client.get_or_create_collection(
    "fulltext_specter", embedding_function=specter_embeder)

print(collection.count())


def split_text(df):
    """ Split text into chunks """
    df = df.assign(split_text=df['text'].apply(text_splitter.split_text))
    df = df.drop(columns='text')
    return df

# ------------------------------------------------------------------------------------


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


def df_create_doc(df):
    """ Used for mapping partitions

    Takes dataframe

    Returns a series

    """
    return df.apply(lambda x: create_doc(x['split_text'], x['corpusid']), axis=1)


def mp_create_doc(ddf):
    """ Used for mapping partitions"""
    return ddf.apply(df_create_doc, axis=1)

# ------------------------------------------------------------------------------------
# Add documents to collection


def add_to_collection(docs, collection):
    """ Add documents to collection """
    try:
        collection.add(**docs)
    except Exception as e:
        logging.error(e)


def ddf_add_to_collection(series, **kwargs):
    """ Add documents to collection """
    return series.apply(add_to_collection)


file_list = glob(
    '/home/ubuntu/work/data/fulltext_docs_csvs_cleaned/fulltext_doc_*.csv')

# ------------------------------------------------------------------------------------
# Add documents to collection
def add_to_collection(docs):
    """ Add documents to collection """

    docs = ast.literal_eval(docs)  # since dictionaries were stored as string

    docs['embeddings'] = specter_embeder.embed_documents(docs['documents'])

    try:
        collection.upsert(**docs)

    except Exception as e:
        logging.error(e)


for f in tqdm(file_list):
    # print(f)
    df = pd.read_csv(f).iloc[:, 0]

    df.apply(add_to_collection)


collection.count()
