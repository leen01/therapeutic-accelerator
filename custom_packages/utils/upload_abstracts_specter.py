#! usr/bin/env python3
import warnings
import dask
from dask.distributed import LocalCluster, Client, TimeoutError, KilledWorker
import numpy as np
import pandas as pd
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer
import chromaDB as cbd  # specter_ef, create_text_splitter, create_chroma_client
from db_tools import db_connection
from utils import import_config

# hide warnings
warnings.filterwarnings("ignore")


def remove_existing(df, collection):
    """ Remove existing ids from the dataframe """
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

def process_dict(d, specter_embeder, collection):
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
    # ... (remaining imports)

    # Chroma setup
    chroma_server_host = "3.88.178.230"
    chroma_client = cbd.create_chroma_client(chroma_server_host)

    # Modelish stuff
    model = AutoModel.from_pretrained("allenai/specter")
    tokenizer = AutoTokenizer.from_pretrained("allenai/specter")
    specter_embeder = cbd.specter_ef(model, tokenizer)
    specter_embeder.create_text_splitter()

    # Working Collection
    collection = chroma_client.get_or_create_collection(
        "specter_abstracts", embedding_function=specter_embeder)
    
    print(collection.count())

    abstracts = pd.read_csv("/home/ubuntu/work/data/abstracts.csv")
    
    abstracts = remove_existing(abstracts, collection)

    # Add documents to collection
    n_partitions = len(abstracts) // 100
    
    print(n_partitions)

    abstracts_dict = abstracts.to_dict('records')
    
    for d in tqdm(range(len(abstracts_dict)), desc='abstracts'):
        process_dict(abstracts_dict[d], specter_embeder, collection)