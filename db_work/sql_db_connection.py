# connection libraries
from google.cloud.sql.connector import Connector
import sqlalchemy
import pg8000

# Add files to database
# initialize Connector object
connector = Connector()

# function to return the database connection object
# @hydra.main(config_path="../conf", config_name="main", version_base=None)
def getconn():
    INSTANCE_CONNECTION_NAME = f"{config['project_id']}:{config['instance']['region']}:{config['instance']['name']}" # i.e demo-project:us-central1:demo-instance
    DB_USER = config['database']['user']
    DB_PASS = config['database']['password']
    DB_NAME = config['database']['name']
    
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn