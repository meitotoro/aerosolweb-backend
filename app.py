# -*- coding: utf-8 -*-
import falcon
from falcon_cors import CORS
import pyhdf
import readhdf
import numpy as np
import json
import os

public_cors = CORS(allow_all_origins=True)


class MonthMap(object):
    def on_get(self, req, resp):
        files_path = "/home/mei/aerosolweb-backend/data/MODIS/"
        #页面传过来的年份
        year = int(req.get_param('year'))
        month = int(req.get_param('month'))
        month_aod = readhdf.monthMap(files_path, year, month)
        resp.media = {"data":month_aod}


class AodResource(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        files_path = "/home/mei/aerosolweb-backend/data/MODIS/"
        #页面传过来站点名称或者经纬度信息
        temp_lon = float(req.get_param('lon'))
        temp_lat = float(req.get_param('lat'))
        start = int(req.get_param('start_time'))
        end = int(req.get_param('end_time'))
        #srap的经纬度信息
        lon = np.linspace(35, 150, 1150)
        lat = np.linspace(15, 60, 450)
        year_aod = readhdf.fileList(files_path, start, end, temp_lon, temp_lat)

        resp.media = { "data": year_aod }
class ImageResource(object):
    def on_get(self,req,resp,filename):
        print(dir(req))
        resp.status=falcon.HTTP_200
        resp.content_type="image/png"
        image_path="/home/mei/aerosolweb-backend/aod-image/"
        path=image_path+filename
        with open(path,"r")as f:
            resp.body=f.read()

class SitesAODResource(object):
    def on_get(self,req,resp):
        resp.status=falcon.HTTP_200
        year=int(req.get_param("year"))
        month=int(req.get_param("month"))
        area=str(req.get_param("area"))
        satellite=str(req.get_param("satellite"))
        image_path="/home/mei/aerosolweb-backend/aod-image/"
        data_path = "/home/mei/aerosolweb-backend/data/"+satellite.upper()+"/"
        files=os.listdir(image_path)
        name=satellite+"-aod-"+str(year)+"-"+str(month)+"-"+area+".png"
        print(name)
        for file in files:
            print(file)
            if not os.path.isdir(file):
                #文件夹中存在这个image，返回image和aod_site
                if file==name:
                    filename=name
                    AODfilename=satellite+"-"+"site-aod-"+str(year)+"-"+str(month)+"-"+area+".txt"
                    aod_path=image_path+AODfilename
                    fh = open(aod_path, 'r')
                    sites_aod=json.loads(fh.read())
                    break
        else:
            filename,sites_aod=readhdf.monthMap(data_path,satellite,year, month,area)
                  
        resp.media={"aod":sites_aod,"filename":filename}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
        

api = falcon.API(middleware=[public_cors.middleware])
api.add_route('/aod', AodResource())
api.add_route('/map', SitesAODResource())
api.add_route('/map/{filename}', ImageResource())
