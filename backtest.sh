#!/bin/bash
sudo apt-get install virtualenv
virtualenv .venv
source .venv/bin/activate
sudo apt-get install python-pip
pip install -r requirements.txt