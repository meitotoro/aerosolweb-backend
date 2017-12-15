# -*- coding: utf-8 -*-
import datetime
import math
import os
import numpy as np
import image
import pyhdf
from pyhdf import SD
import json
import codecs

class AodPoint(object):
    '''创建一个像素点对象'''

    def __init__(self, year, month, aod, lon, lat):
        self.year = year
        self.month = month
        self.aod = aod
        self.lon = lon
        self.lat = lat

    def __repr__(self):
        return "\n{}-{} {}".format(self.year, self.month, self.aod)


class SrapData(object):
    '''输入经纬度坐标，找到对应的光学厚度值'''

    def __init__(self, path):
        self.path = path
        obj = SD.SD(path, SD.SDC.READ)
        ''' #经纬度图像450*1150
        self.lon=obj.select("Longitude").get()
        self.lat=obj.select("Latitude").get() '''
        #光学厚度图像676*451
        self.aod_550 = obj.select("SRAP_AOD_MONTH_AVE at 550nm").get() * 0.001

    def locate(self, lon, lat):
        '''在modis图像中找到与指定坐标最接近的坐标点索引，以及该点的坐标值'''
        '''
        dlon=np.square(np.abs(self.lon-lon))       
        dlat=np.square(np.abs(self.lat-lat))
        dist=np.add(dlon,dlat)
        flat_index=np.argmin(dist)
        print(flat_index)        
        index=np.unravel_index(flat_index,dist.shape)
        print(index,self.lon[index],self.lat[index])
        return index,self.lon[index],self.lat[index],self.aod_550[index] '''
        y_index = int(round((lon - 35) / 0.1))
        x_index = int(round((lat - 15) / 0.1))
        index = (x_index, y_index)
        print(self.aod_550[index])
        return index, self.aod_550[index]


'''
遍历文件夹下的所有HDF文件，拿到对应的时间段范围的HDF文件列表
假设时间是以年为单位，比如2003-2009年
'''


def compare_aod_data(a, b):
    if a.year < b.year:
        return -1
    elif a.year > b.year:
        return 1
    if a.month < b.month:
        return -1
    elif a.month > b.month:
        return 1
    return 0


def fileList(path, time_start, time_end, lon, lat):
    files = os.listdir(path)
    year_aod = []
    for file in files:
        #判断是否文件夹
        if not os.path.isdir(file):
            year = int(file.split('.')[1][15:19])
            month = int(file.split('.')[1][19:21])
            file_path = path + file
            if (year >= time_start and year <= time_end):
                #在hdf文件中找到距离目标站点最接近的点的AOD
                srap = SrapData(file_path)
                index, aod_550 = srap.locate(lon, lat)
                if (aod_550 < 0):
                    continue
                else:
                    point = AodPoint(year, month, aod_550, lon, lat)
                    year_aod.append(point)
    year_aod.sort(cmp=compare_aod_data)
    year_aod = [p.__dict__ for p in year_aod]
    print(year_aod)
    return year_aod


def monthMap(path, year, month): 
    date=str(year)+"-"+str(month)
    files = os.listdir(path)
    month_aod = []
    image_path="/home/mei/aerosolweb-backend/aod-image/"
    #image_aod=[]
    for file in files:
        if not os.path.isdir(file):
            temp_year = int(file.split('.')[1][15:19])
            temp_month = int(file.split('.')[1][19:21])
            file_path = path + file
            if (temp_year == year and temp_month == month):
                srap = SrapData(file_path)
                month_aod = srap.aod_550
                image_name=image.plot_image(month_aod,year,month)
                site_path="/home/mei/aerosolweb-backend/sites.txt" 
                sites_aod={}
                sites=[]
                aod=[]                             
                try:
                    file_object=codecs.open(site_path,"r")
                    read= file_object.read()
                    site_json=json.loads(read)
                    print(site_json)
                    for key,value in site_json.items():
                        lon=value[0]
                        lat=value[1]
                        index, aod_550 = srap.locate(lon, lat)
                        
                        sites.append(key)
                        aod.append(aod_550)
                         
                finally:
                    file_object.close()
                    sites_aod["sites"]=sites
                    sites_aod["aod"]=aod
                    contents=json.dumps(sites_aod)
                    filename=image_path+"site-aod-"+date+".txt"
                    fh = codecs.open(filename, 'w',"utf-8") 
                    fh.write(contents.encode("gb2312")) 
                    fh.close() 
                    print(sites_aod)
                return image_name,sites_aod 
            
    #return month_aod.tolist()
    return []  # 没有找到匹配文件


if __name__ == "__main__":
    files_path = "/home/mei/aerosolweb-backend/data/MODIS/"
    #页面传过来站点名称或者经纬度信息
    temp_lon = 50
    temp_lat = 40
    #srap的经纬度信息
    lon = np.linspace(35, 150, 1150)
    lat = np.linspace(15, 60, 450)
    
    #year_aod = fileList(files_path, 2001, 2017, temp_lon, temp_lat)
   
    month_aod,sites_aod = monthMap(files_path, 2006, 1)
    print("first 10 items in image: {}".format(month_aod[:10]))
    print("first 5 items in image: {}".format(sites_aod[:5]))
