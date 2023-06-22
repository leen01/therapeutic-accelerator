import os
import yaml
import pandas as pd
import numpy as np

# set up
with open("/home/ubuntu/work/therapeutic_accelerator/config/main.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
with open("../config/keys.yaml", "r") as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)