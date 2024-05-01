#! /bin/sh
sudo apt-get update -y;
sudo apt-get install awscli -y;
sudo apt-get install s3fs -y;
aws configure;

echo "AKIAUKGQGDD7B7GOCCXZ:YGQnsrfkK8YCFxT5bEzj3C0UTgfX1MJnjo8vIvKb" > ${HOME}/.passwd-s3fs;
chmod 600 ${HOME}/.passwd-s3fs;

mkdir bucket
mkdir attributes

# mount buckets
sudo s3fs papers-fulltext /home/ubuntu/work/bucket  -o passwd_file=$HOME/.passwd-s3fs,nonempty,rw,allow_other,complement_stat,mp_umask=002;
sudo s3fs papers-attributes /home/ubuntu/work/attributes  -o passwd_file=$HOME/.passwd-s3fs,nonempty,rw,allow_other,complement_stat,mp_umask=002


# keygen for github
ssh-keygen -t ed25519 -C nicholas.lee@sagebase.com

# git config
git config --global user.name "Nicholas Lee"
git config --global user.email "nick.lee@berkeley.edu"

git clone git@github.com:leen01/therapeutic_accelerator.git
# add anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh

bash Anaconda3-2023.03-1-Linux-x86_64.sh
# enter, then space bar down to agreement
# enter to confirm location
# intialize

# restart terminal
exec bash

# setup virtual environment
conda env create -n ta --file /home/ubuntu/work/therapeutic_accelerator/setup/environment.yml

# install poetry  without conda deactivated
curl -sSL https://install.python-poetry.org | python3 -

# for install hnswlib need these packages on the instance
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev libpq-dev

# use jupyter notebook in vscode

poetry shell
code . # open a with the venv
poetry config virtualenvs.in-project true # create the install in the local project
poetry install # get all the packages
poetry env  info # get information about the poetry environme

# ADD THE PYTHON ENVIRONMENT TO JUPYTER NOTEBOOK
export PATH=/home/ubuntu/work/therapeutic_accelerator/.venv/bin/:$PATH