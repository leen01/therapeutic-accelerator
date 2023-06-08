#!/bin/user/env bash
sudo jupyter serverextension enable --py jupyterlab --sys-prefix
jupyter lab --ip 0.0.0.0 --port 8080 --no-browser
