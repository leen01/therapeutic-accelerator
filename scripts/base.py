import yaml
from sqlalchemy.engine import URL
from sqlalchemy import create_engine

# set up
with open("/home/ubuntu/work/therapeutic_accelerator/config/main.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
with open("/home/ubuntu/work/therapeutic_accelerator/config/keys.yaml", "r") as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)
    
url_object = URL.create(
    'postgresql', 
    username='postgres',
    password=keys["postgres"], 
    host=config["database"]["host"],
    database='postgres',
    port=5432
)

# Create engine to connect to database
# psql_string = f'postgresql://postgres:{keys["postgres"]}@{config["database"]["host"]}:5432/postgres'
engine = create_engine(url_object)