# Get all file paths. It is in attributes but it is the full papers
import glob
import yaml
import os
import gzip
import shutil

with open("/home/ubuntu/work/therapeutic_accelerator/config/main.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
bucket_path = os.path.join(config['paths']['root'], config['paths']['mount'])

fulltext_files = glob.glob("".join([bucket_path, '/fulltext-zipped/', '/*?[.gz|!.zip]']))

for file in fulltext_files: 
    with open(file, 'rb') as f_in:
        try: 
            with gzip.open(file.strip("\.gz"), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        except: 
            print(f"could not extract file {file}")