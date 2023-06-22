import os
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
import time
import requests
import yaml
from urllib.request import urlopen
from shutil import copyfileobj


with open("../config/main.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

with open("../config/keys.yaml", "r") as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)

root_path = config['paths']['root']
bucket_path = os.path.join(root_path, config['paths']['mount'])
papers_path = os.path.join(root_path, config['paths']['papers'])
working_path = os.path.join(root_path, config['paths']['wkdir'])
# full text
# follow s3 link
full_text = requests.get("http://api.semanticscholar.org/datasets/v1/release/latest/dataset/s2orc",
                      headers={'x-api-key':keys['x-api-key']}).json()

temp = pd.DataFrame(full_text)
temp[['base_url', 'file_name', 'access_key']] = temp.files.str.split("s2orc/|\?", expand = True)
temp.head()

for u, f in tqdm(list(zip(temp.files, temp.file_name))): 
    file_path = os.path.join(root_path, bucket_path, 'fulltext-zipped/', f)
    if os.path.exists(file_path) != True: 
        with urlopen(u) as in_stream, open(file_path, 'wb') as out_file:
            copyfileobj(in_stream, out_file)