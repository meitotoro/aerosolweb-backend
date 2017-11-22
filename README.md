# aerosolweb-backend

## 安装virtualenv
sudo apt-get install virtualenv

## 建立虚拟环境
```
virtualenv .venv
```

## 启用虚拟环境
```
source .venv/bin/activate
```

## 安装依赖库
```
sudo apt-get install python-pip

pip install -r requirements.txt
```

## 启动 web 服务
```
uwsgi --http :9000 --wsgi-file app.py --callable api --py-autoreload 1
```