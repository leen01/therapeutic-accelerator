import pandas as pd
import numpy as np

from tqdm import tqdm
import time

# for using configuration files like yamls. This is to help key our keys safe
import yaml # for configuration files 
import hydra
from omegaconf import DictConfig, OmegaConf

import multiprocessing
import requests

import urllib
import os
import json
import glob
# import orjson # for faster reading of json
import jsonlines # for opening jsonl files

# unzip files
# import gzip
# import shutil

# @hydra.main(config_path="../conf", config_name="main", version_base=None)

from sqlalchemy.orm import Session
from sqlalchemy import select, Table, Column, Integer, String, Boolean, MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import ARRAY
# connection libraries
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy

with open("../config/main.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

with open("../config/keys.yaml", "r") as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)

root_path = "/home/nick_lee_berkeley_edu/"
mount_path = os.path.join(root_path, "mount-folder")

attribute_files = glob.glob("".join([mount_path, '/extracted/*?.jsonl']))

# connect to goolge cloud postgres db
def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = config['database']['connection'] # i.e demo-project:us-central1:demo-instance
    db_user = config['database']['user']
    db_pass = config['database']['password']
    db_name = config['database']['name']

    ip_type = IPTypes.PRIVATE # if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            db=db_name,
            user=db_user,
            password = db_pass,
            # enable_iam_auth=True,
            ip_type=ip_type
        )
        return conn

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # [START_EXCLUDE]
        # Pool size is the maximum number of permanent connections to keep.
        pool_size=5,
        # Temporarily exceeds the set pool_size if no connections are available.
        max_overflow=2,
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        pool_timeout=30,  # 30 seconds
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # re-established
        pool_recycle=1800,  # 30 minutes
        # [END_EXCLUDE]
    )
    return pool

def json_to_df(j): 
    """ Create dataframe to upload into database """
    return pd.DataFrame([json.loads(j)])

def df_to_db(df): 
    with pool.connect() as db_conn:
        df.to_sql('article_attributes', con = db_conn, if_exists='append', index = False)

def preprocess_df(df): 
    df.year = df.year.astype("Int64")
    return df

pool = connect_with_connector()

for jl in tqdm(attribute_files): 
    with jsonlines.open(jl) as f:
        for line in tqdm(f.iter()): 
            df_to_db(preprocess_df(pd.DataFrame([line]))) # reads json, converts to dataframe, preprocess functions and appends results to database