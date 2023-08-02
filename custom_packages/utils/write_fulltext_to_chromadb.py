#! usr/bin/env python3
import warnings
import numpy as np
import pandas as pd
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer
import chromaDB as cbd  # specter_ef, create_text_splitter, create_chroma_client
from db_tools import db_connection
from utils import import_config
import logging
from glob import glob

# hide warnings
warnings.filterwarnings("ignore")


def remove_exisiting(df, collection):
    """ Remove existing ids from dataframe """
    # get unique ids from collection that are the corpus ids
    query_filter = {
        "$or": [{'corpusid': str(c)} for c in df['corpusid'].unique()]
    }

    # get ids in df from collection
    temp = collection.get(
        include=["metadatas"],
        where=query_filter
    )

    if len(temp['ids']) > 0: 
        test_ids = pd.DataFrame(temp['metadatas'])

        existing_ids = test_ids.astype(str)['corpusid'].unique()

        df = df[~df['corpusid'].astype(str).isin(existing_ids)]
        
    return df

def create_split_text(df):

    df['documents'] = df.apply(
        lambda x: specter_embeder.split_text(x['documents']), axis=1)

    return df


def create_ids(df):
    """ Create ids for each chunk """

    df['ids'] = df.apply(lambda x: [
                         f"{x['corpusid']}-{i}" for i in range(len(x['documents']))], axis=1)

    return df


def create_metadatas(df):
    """ Create metadatas for each chunk """

    df['metadatas'] = df.apply(lambda x: [{'corpusid': x['corpusid'], 'chunk':i} for i in range(
        len(x['documents']))], axis=1)

    return df


def create_embeddings(df):

    df['embeddings'] = df.apply(
        lambda x: specter_embeder.embed_documents(x['documents']), axis=1)

    return df


if __name__ == "__main__":
    # ... (remaining imports)
    logging.basicConfig(
        filename='/home/ubuntu/work/therapeutic_accelerator/logs/abstract_embeddings_dask.log', level=logging.ERROR)

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
        "fulltext_specter", embedding_function=specter_embeder)

    print('Collection count start: ', collection.count())

    file_list = glob('/home/ubuntu/work/data/fulltext_parquets/*.parquet')

    for f in tqdm(file_list, desc="Processing files"):
        print(f)
        df = pd.read_parquet(f)
        df = df.rename({'text':'documents'}, axis = 1)
        df = df.dropna(subset=['documents'])
        
        # Add documents to collection
        n_partitions = len(df) // 5

        # split into smaller arrays for easier processing without overloading system
        df_split = np.array_split(df, n_partitions)

        for i in tqdm(range(len(df_split)), desc="---- partitions"):
            df_split[i] = remove_exisiting(df_split[i], collection)
            if len(df_split[i]) > 0:
                df = create_split_text(df_split[i])
                df = create_embeddings(df)
                df = create_ids(df)
                df = create_metadatas(df)
                df = df.drop(columns=['corpusid'])
                dict_series = df.to_dict('records')

                temp_dict = {
                    'documents': [],
                    'ids': [],
                    'embeddings': [],
                    'metadatas': []
                }

                # combine dictionaries into one
                for ds in dict_series:
                    for k in temp_dict.keys():
                        temp_dict[k] = temp_dict[k] + ds[k]

                try:
                    collection.add(**temp_dict)

                    print('Collection count: ', collection.count())
                    
                    # track which files are completed
                    with open('/home/ubuntu/work/therapeutic_accelerator/logs/finished_fulltext_files.txt', 'a') as file:
                        # Step 2: Write the text to append
                        file.write(f)
                
                except Exception as e:
                    logging.exception(
                        "Error occurred while adding documents to collection")

