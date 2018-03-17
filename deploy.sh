#!/bin/bash

# create virtual environment
virtualenv .venv
# activate venv
. .venv/bin/activate

# install system-wide dependencies
sudo apt install libjpeg8-dev zlib1g-dev libhdf4-dev proj-bin proj-data libgeos-dev python-tk

# install local dependencies
pip install -r requirements.txt
## pyhdf
wget http://hdfeos.org/software/pyhdf/pyhdf-0.9.0.tar.gz
tar zxf pyhdf-0.9.0.tar.gz
cd pyhdf-0.9.0
python setup.py install
cd ..
rm -rf pyhdf-0.9.0
rm pyhdf-0.9.0.tar.gz
## basemap
wget https://github.com/matplotlib/basemap/archive/v1.1.0.tar.gz -O basemap-1.1.0.tar.gz
tar zxf basemap-1.1.0.tar.gz
cd basemap-1.1.0
python setup.py install
cd ..
rm -rf basemap-1.1.0
rm basemap-1.1.0.tar.gz

# firewall rule
sudo ufw allow 9000
