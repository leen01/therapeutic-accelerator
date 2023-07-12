#! /bin/sh
sudo apt-get update -y
sudo apt-get install awscli -y
sudo apt-get install s3fs -y
aws configure

# keygen for github
ssh-keygen -t ed25519 -C "your.email@abc.com"

# git config
git config --global user.name "First Last"
git config --global user.email "email@abc.com"

# Git repository
git clone git@github.com:leen01/therapeutic_accelerator.git

# add anaconda
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh

# start anaconda installer
bash Anaconda3-2023.03-1-Linux-x86_64.sh
# enter, then space bar down to agreement
# enter to confirm location
# intialize

# restart terminal
exec bash

# setup virtual environment
conda env create -n ta --file /home/ubuntu/work/therapeutic_accelerator/setup/environment.yml

echo "<accessKey>:<value>" > ${HOME}/.passwd-s3fs;
chmod 600 ${HOME}/.passwd-s3fs

mkdir bucket
mkdir attributes

# mount buckets
sudo s3fs papers-fulltext /home/ubuntu/work/bucket  -o passwd_file=$HOME/.passwd-s3fs,nonempty,rw,allow_other,complement_stat,mp_umask=002;
sudo s3fs papers-attributes /home/ubuntu/work/attributes  -o passwd_file=$HOME/.passwd-s3fs,nonempty,rw,allow_other,complement_stat,mp_umask=002


