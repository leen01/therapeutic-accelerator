with open("/home/ubuntu/work/therapeutic_accelerator/scripts/base.py") as f:
    exec(f.read())
    
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text

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