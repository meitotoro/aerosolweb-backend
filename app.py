# -*- coding: utf-8 -*-
import falcon
from falcon_cors import CORS
import pyhdf
import readhdf
import numpy as np
import json
import os
import logging


public_cors = CORS(allow_all_origins=True)


class AodResource(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        files_path = "data/MODIS/"
        #页面传过来站点名称或者经纬度信息
        temp_lon = float(req.get_param('lon'))
        temp_lat = float(req.get_param('lat'))
        start = int(req.get_param('start_time'))
        end = int(req.get_param('end_time'))
        #srap的经纬度信息
        lon = np.linspace(35, 150, 1150)
        lat = np.linspace(15, 60, 450)
        year_aod = readhdf.fileList(files_path,"modis", start, end, temp_lon, temp_lat)
        resp.media = { "data": year_aod }
        
class ImageResource(object):
    def on_get(self,req,resp,filename):
        print(dir(req))
        resp.status=falcon.HTTP_200
        resp.content_type="image/png"
        image_path="aod-image/"
        path=image_path+filename
        with open(path,"r")as f:
            resp.body=f.read()

class SitesAODResource(object):
    def on_get(self,req,resp):
        resp.status=falcon.HTTP_200
        year=int(req.get_param("year"))
        area=str(req.get_param("area"))
        satellite=str(req.get_param("satellite"))
        image_path="aod-image/"
        data_path = "data/"+satellite.upper()+"/"
        files=os.listdir(image_path)
        strName=""
        date=""
        if req.get_param("month") is None:  
            if req.get_param("season") is None:
                flag="year"
                date=req.get_param("year")                                 
            else:
                flag="season"
                date=req.get_param("year")+"-"+req.get_param("season")              
        else:
            flag="month"
            date=req.get_param("year")+req.get_param("month")                  
        strName=date+"-"+area      
        name=satellite+"-aod-"+strName+".png"
        print(name)
        for file in files:
            print(file)
            if not os.path.isdir(file):
                #文件夹中存在这个image，返回image和aod_site
                if file==name:
                    print(file)
                    filename=name
                    AODfilename=satellite+"-"+"site-aod-"+strName+".txt"
                    aod_path=image_path+AODfilename
                    fh = open(aod_path, 'r')
                    sites_aod=json.loads(fh.read())
                    resp.media={"aod":sites_aod,"filename":filename}
                    return
        filename,sites_aod=readhdf.getMap(data_path,satellite,date,area,flag)
        resp.media={"aod":sites_aod,"filename":filename}     
                    
                  
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
        
def server_error(ex, req, resp, params):
    logging.exception(ex)
    raise falcon.HTTPInternalServerError(description=str(ex))

api = falcon.API(middleware=[public_cors.middleware])
api.add_error_handler(Exception, server_error)
api.add_route('/aod', AodResource())
api.add_route('/map', SitesAODResource())
api.add_route('/map/{filename}', ImageResource())
