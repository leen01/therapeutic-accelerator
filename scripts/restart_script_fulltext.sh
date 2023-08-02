#!/bin/bash

# Function to run the Python script in a loop
function run_python_script {
    while true; do
        python /home/ubuntu/work/therapeutic_accelerator/custom_packages/utils/write_fulltext_to_chromadb.py
        echo "Python script for full text upload exited unexpectedly. Restarting in 5 seconds..."
        sleep 5
    done
}

# Call the function to run the Python script
run_python_script
