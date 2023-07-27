#! usr/bin/bash python3
import sys

sys.path.append(
    "/home/ubuntu/work/therapeutic_accelerator/custom_packages/utils")

import utils
import chromaDB

# get user input
def get_user_input():
    # Ask the user for their name
    message = input("Send a message: ")
    return message

if __name__ == "__main__":    
    chunk_size = 1024
    chroma_server_host = "52.23.195.129"
    
    config, keys = utils.import_config()
    
    chroma_client = chromaDB.create_chroma_client(chroma_server_host)
    
    collection = chroma_client.get_or_create_collection("specter_abstracts")
    
    print("-" * 20)
    user_input = input("Send a Message: ")
    print("-" * 20)

    query_results = chromaDB.query_chroma_with_embeddings(collection, user_input, n_results=5)

    print(query_results)