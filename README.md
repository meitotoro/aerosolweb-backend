# aerosolweb-backend

```
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
uwsgi --http :9000 --wsgi-file app.py --callable api
```