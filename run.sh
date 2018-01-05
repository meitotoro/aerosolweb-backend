#!/bin/bash
source .venv/bin/activate
uwsgi --http :9000 --wsgi-file app.py --callable api --py-autoreload 1