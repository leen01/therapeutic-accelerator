# usr/bin/env python3
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, MetaData, text


# create function to submit query to database with sqlalchemy
def query_db(query):
    with engine.connect() as con:
        rs = con.execute(text(query))
        return rs


# get all table names in postgresql database
def get_table_names():
    metadata = MetaData()
    metadata.reflect(engine)
    return metadata.tables.keys()


# get metadata for table in postgresql database
def get_metadata(table_name):
    metadata = MetaData()
    metadata.reflect(engine)
    table = metadata.tables[table_name]
    return table


# display metadata for table in postgresql database as json
def display_metadata(table_name):
    table = get_metadata(table_name)
    return table.columns.keys()


def db_connection(password, host, port=5432, database="postgres", username="postgres"):
    
    url_object = URL.create(
        "postgresql",
        username="postgres",
        password=password,
        host=host,
        database="postgres",
        port=5432
    )

    # Create engine to connect to database
    # psql_string = f'postgresql://postgres:{keys["postgres"]}@{config["database"]["host"]}:5432/postgres'
    engine = create_engine(url_object)

    return engine
