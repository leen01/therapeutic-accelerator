from dask import dataframe as dd
import yaml

with open("/home/ubuntu/work/therapeutic_accelerator/config/main.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
with open("/home/ubuntu/work/therapeutic_accelerator/config/keys.yaml", "r") as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)


ddf = dd.read_sql_table('fulltext', 
                        con = f'postgresql://postgres:{keys["postgres"]}@{config["database"]["host"]}:5432/postgres',
                        index_col = 'id',
                        head_rows = 10,
                        npartitions = 400)

ft = ddf.loc[:, ['corpusid', 'text']]

# write out dask series to parquet
name_function = lambda x: f"fulltext-{x}.parquet"
ft.to_parquet('/home/ubuntu/work/data/fulltext_parquets/', name_function=name_function)  