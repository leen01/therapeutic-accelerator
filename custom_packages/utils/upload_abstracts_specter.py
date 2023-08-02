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


# @dask.delayed
def create_split_text(df): 
    
    df['documents'] = df.apply(lambda x: specter_embeder.split_text(x['documents']), axis=1)
    
    return df

def create_ids(df): 
    """ Create ids for each chunk """
    
    df['ids'] = df.apply(lambda x: [f"{x['corpusid']}-{i}" for i in range(len(x['documents']))], axis=1)
    
    return df

def create_metadatas(df): 
    """ Create metadatas for each chunk """
    
    df['metadatas'] = df.apply(lambda x: [{'corpusid': x['corpusid'], 'chunk':i} for i in range(len(x['documents']))], axis=1)
    
    return df

def create_embeddings(df): 
    
    df['embeddings'] = df.apply(lambda x: specter_embeder.embed_documents(x['documents']), axis=1)
    
    return df


if __name__ == "__main__":
    # ... (remaining imports)
    logging.basicConfig(filename='/home/ubuntu/work/therapeutic_accelerator/logs/abstract_embeddings_dask.log', level=logging.ERROR)

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
    
    print('Collection count: ', collection.count())

    abstracts = pd.read_csv("/home/ubuntu/work/data/abstracts.csv")

    abstracts = abstracts.rename({'corpusId':'corpusid'}, axis = 1)
    
    # Add documents to collection
    n_partitions = len(abstracts) // 100
    
    print('Partitions: ', n_partitions)
    
    abstracts_split = np.array_split(abstracts, n_partitions)

    for i in tqdm(range(len(abstracts_split)), desc="Processing abstract partitions"):
        abstracts_split[i] = remove_exisiting(abstracts_split[i], collection)
        if len(abstracts_split[i]) > 0: 
            df = create_split_text(abstracts_split[i])
            df = create_embeddings(df)
            df = create_ids(df)
            df = create_metadatas(df)
            df = df.drop(columns = ['corpusid'])
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
            except Exception as e: 
                logging.exception("Error occurred while adding documents to collection")
                # back up abstracts
                abstracts.to_csv("/home/ubuntu/work/data/abstracts_backup.csv", index = False)
                
                # create new csv so chroma does not have to start from beginning
                pd.concat(abstracts_split).to_csv("/home/ubuntu/work/data/abstracts.csv", index = False)
        else: 
            print('No new abstracts to add to collection')
            abstracts.to_csv("/home/ubuntu/work/data/abstracts_backup.csv", index = False)
            
            # create new csv so chroma does not have to start from beginning
            pd.concat(abstracts_split).to_csv("/home/ubuntu/work/data/abstracts.csv", index = False)
        
            
