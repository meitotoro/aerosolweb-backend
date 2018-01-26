#!/usr/bin/python
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
import h5py

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

class AVHRRData(object):
    def __init__(self,path):
        self.path=path
        f = h5py.File(path, 'r')
        # List all groups
        print("Keys: %s" % f.keys())
        # Get the data
        #光学厚度图像301*601
        self.aod_550 = f["Aerosol_Optical_Depth_Mean: Mean of Daily"][0]
        print(self.aod_550)
       
       

    def locate(self, lon, lat):
        '''在modis图像中找到与指定坐标最接近的坐标点索引，以及该点的坐标值'''
        y_index = int(round((lon - 75) / 0.1))
        x_index = int(round((lat - 15) / 0.1))
        index = (x_index, y_index)
        print(self.aod_550[index])
        return index, self.aod_550[index]

class SrapData(object):
    '''输入经纬度坐标，找到对应的光学厚度值'''

    def __init__(self, path):
        self.path = path
        obj = SD.SD(path, SD.SDC.READ)
        #光学厚度图像676*451
        self.aod_550 = obj.select("SRAP_AOD_MONTH_AVE at 550nm").get() * 0.001

    def locate(self, lon, lat):
        '''在modis图像中找到与指定坐标最接近的坐标点索引，以及该点的坐标值'''
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


def monthMap(path, satellite, year, month,area): 
    date=str(year)+"-"+str(month)
    files = os.listdir(path)
    month_aod = []
    image_path="aod-image/"
    #image_aod=[]
    for file in files:
        if not os.path.isdir(file):
            if satellite=="modis":
                temp_year = int(file.split('.')[1][15:19])
                temp_month = int(file.split('.')[1][19:21])
            elif satellite=="avhrr":
                temp_year=int(file[19:23])
                temp_month=int(file[24:26])
            else:
                return
            file_path = path + file
            if (temp_year == year and temp_month == month):
                if satellite=="modis":
                    srap = SrapData(file_path)
                    month_aod = srap.aod_550
                elif satellite=="avhrr":
                    avhrr = AVHRRData(file_path)
                    month_aod=avhrr.aod_550
                else:
                    return
                if(area=="china"):
                    #全国地理底图的aod数据
                    image_name=image.plotChina_image(month_aod,year,month,satellite)
                elif (area=="jingjinji"):
                    #京津冀经度（113,120）,纬度(36,43)
                    image_name=image.plot_VectorClipImage(month_aod,year,month,113,36,120,42.8,"jingjinji")
                elif (area=="changsanjiao"):
                    #长三角经纬度（118,123），纬度（28,34）
                    image_name=image.plot_VectorClipImage(month_aod,year,month,115.5,27.7,123,34.8,"changsanjiao")
                elif(area=="zhusanjiao"):
                    #珠三角经度(111,116)，纬度(21,25)
                    image_name=image.plot_VectorClipImage(month_aod,year,month,111.2,21.5,115.5,24.5,"zhusanjiao")
                else:
                    image_name=""
                    return "",""
                site_path=area+"-"+"sites.txt" 
                sites_aod={}
                sites=[]
                aod=[]
                locate=[]                             
                try:
                    file_object=codecs.open(site_path,"r")
                    read= file_object.read()
                    site_json=json.loads(read)
                    print(site_json)
                    for key,value in site_json.items():
                        lon=value[0]
                        lat=value[1]
                        if satellite=="modis":
                            index, aod_550 = srap.locate(lon, lat)
                        elif satellite=="avhrr":
                            index, aod_550=avhrr.locate(lon,lat)                        
                        locate.append(value)
                        sites.append(key)
                        aod.append(aod_550)
                         
                finally:
                    file_object.close()
                    sites_aod["sites"]=sites
                    sites_aod["aod"]=aod
                    sites_aod["locate"]=locate
                    contents=json.dumps(sites_aod)
                    filename=image_path+satellite+"-"+area+"-site-aod-"+date+".txt"
                    fh = codecs.open(filename, 'w',"utf-8") 
                    fh.write(contents.encode("gb2312")) 
                    fh.close() 
                    print(sites_aod)
                return image_name,sites_aod 
            
    #return month_aod.tolist()
    return "",""  # 没有找到匹配文件


if __name__ == "__main__":
    files_path_modis = "data/MODIS/"
    files_path_avhrr="data/AVHRR/"
    #页面传过来站点名称或者经纬度信息
    temp_lon = 50
    temp_lat = 40
    #srap的经纬度信息
    lon = np.linspace(35, 150, 1150)
    lat = np.linspace(15, 60, 450)
    
    #year_aod = fileList(files_path, 2001, 2017, temp_lon, temp_lat)
   
    #image_name,sites_aod = monthMap(files_path_modis,"modis", 2006, 1,"china")
    image_name,sites_aod = monthMap(files_path_avhrr,"avhrr", 2006, 1,"china")
    ''' print(month_aod)
    print(sites_aod) '''
    # print("first 10 items in image: {}".format(month_aod[:10]))
