#! usr/bin/env python3

# setup -----------------------------------------------------------------------

# Base
import pandas as pd
import numpy as np
import re

# LLM packages
from transformers import (
    pipeline,
    set_seed,
    AutoTokenizer,
    AutoModelWithLMHead,
    AutoModel,
)

# Chunk context into 512  tokens
from langchain.text_splitter import RecursiveCharacterTextSplitter

import chromadb
from chromadb.config import Settings
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

# Hard Coded Variables --------------------------------------------------------
chunk_size = 1024
chroma_server_host = "34.238.51.66"


# Functions -------------------------------------------------------------------
class text_splitter:
    def __init__(self, tokenizer, max_length=512, chunk_size=512, chunk_overlap=20):
        self.tokenizer = tokenizer
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_length = max_length

    def token_len(self, text):
        """Get the length of tokens from text"""
        tokens = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=self.max_length,
        )["input_ids"][0]
        return len(tokens)

    def create_text_splitter(self):
        """Create text splitter for processing the texts"""
        text_splitter = RecursiveCharacterTextSplitter(
            # separator = ["\n\n", "\n", ". ", "? ", "! ", "; "],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.token_len,
        )
        return text_splitter


# Create embeddings function with specter model
class specter_ef(EmbeddingFunction):
    def __init__(
        self,
        model=AutoModel.from_pretrained("allenai/specter"),
        tokenizer=AutoTokenizer.from_pretrained("allenai/specter"),
    ):
        self.model = model
        self.tokenizer = tokenizer

    def embed_documents(self, texts: Documents) -> Embeddings:
        text_list = [re.sub("\n", " ", p) for p in texts]
        texts = [re.sub("\s\s+", " ", t) for t in text_list]

        # embed the documents somehow
        embeddings = []

        for text in texts:
            inputs = self.tokenizer(
                text, padding=True, truncation=True, return_tensors="pt", max_length=512
            )
            result = self.model(**inputs)
            embeddings.append(result.last_hidden_state[:, 0, :])

        return embeddings


def create_chroma_client(chroma_server_host):
    chroma_client = chromadb.Client(
        Settings(
            chroma_api_impl="rest",
            chroma_server_host=chroma_server_host,  # EC2 instance public IPv4
            chroma_server_http_port=8000,
        )
    )

    # returns a nanosecond heartbeat. Useful for making sure the client remains connected.
    print("Nanosecond heartbeat on server", chroma_client.heartbeat())

    # Check Existing connections
    display(chroma_client.list_collections())

    return chroma_client


def get_question_embeddings(question):
    # Embed question
    question_embeddings = specter_ef().embed_documents([question])[0][0].tolist()

    return question_embeddings


def query_chroma(collection, question, n_results=10):
    # Query ChromaDB with Embeddings
    question_embeddings = get_question_embeddings(question)

    results = collection.query(
        query_embeddings=[question_embeddings],
        n_results=n_results
        # where={"metadata_field": "is_equal_to_this"},
        # where_document={"$contains":"search_string"}
    )

    for k in results.keys():
        try:
            results[k] = results[k][0]
        except:
            pass

    return results

# Main ------------------------------------------------------------------------
# tokenizer = AutoTokenizer.from_pretrained("allenai/specter")
# model = AutoModel.from_pretrained("allenai/specter")
# specter_embeder = specter_ef(model, tokenizer)
# collection = chroma.get_or_create_collection("specter_abstracts")
