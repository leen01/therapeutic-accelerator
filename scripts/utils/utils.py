# usr/bin/env python3
import yaml

def import_config(): 
    # set up
    with open("/home/ubuntu/work/therapeutic_accelerator/config/main.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        
    with open("/home/ubuntu/work/therapeutic_accelerator/config/keys.yaml", "r") as f:
        keys = yaml.load(f, Loader=yaml.FullLoader)
        
    return config, keys



