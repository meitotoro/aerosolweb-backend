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

image_path="aod-image/"

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

class SatelliteData(object):
    def __init__(self,satellite,path,_aod550=np.array([])):
        self.path=path
        print(path)
        self.satellite=satellite
        self.aod_550=np.array([0])
        if not _aod550.any():            
            if(satellite=="modis"):
                obj = SD.SD(path, SD.SDC.READ)
                #光学厚度图像676*451
                aod_550 = obj.select("SRAP_AOD_MONTH_AVE at 550nm").get() * 0.001
            elif(satellite=="avhrr"):                
                f = h5py.File(path, 'r')
                # List all groups
                print("Keys: %s" % f.keys())
                # Get the data
                #光学厚度图像301*601
                data = f["Aerosol_Optical_Depth_Mean: Mean of Daily"]
                aod_550=data[0:300,0:600][::-1]
            self.aod_550=aod_550   
                  
        else:
            self.aod_550=_aod550 
    
    def locate(self, lon, lat):
        '''在modis图像中找到与指定坐标最接近的坐标点索引，以及该点的坐标值'''
        if self.satellite=="modis":
            y_index = int(round((lon - 35) / 0.1))
            x_index = int(round((lat - 15) / 0.1))
            index = (x_index, y_index)
            print(self.aod_550[index])
            return index, self.aod_550[index]
        elif self.satellite=="avhrr":
            y_index = int(round((lon - 75) / 0.1))
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


def fileList(path, satellite,time_start, time_end, lon, lat):
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
                srap = SatelliteData(satellite,file_path)
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

def getSitesAOD(satellite,aod,area,date):
    date=str(date)
    satellite_data=SatelliteData(satellite,"",aod)
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
            index, aod_550 = satellite_data.locate(lon, lat)                      
            locate.append(value)
            sites.append(key)
            aod.append(aod_550)
                
    finally:
        file_object.close()
        sites_aod["sites"]=sites
        sites_aod["aod"]=aod
        sites_aod["locate"]=locate
        contents=json.dumps(sites_aod)
        filename=image_path+satellite+"-site-aod-"+date+"-"+area+".txt"
        fh = codecs.open(filename, 'w',"utf-8") 
        fh.write(contents.encode("gb2312")) 
        fh.close() 
        print(sites_aod)
    return sites_aod 

def getYearAOD(satellite,path,year):
    files=os.listdir(path)
    year_aod=np.array([0])
    count=0     
    for file in files:
        if not os.path.isdir(file):
            if satellite=="modis":
                temp_year = int(file.split('.')[1][15:19])
            elif satellite=="avhrr":
                temp_year=int(file[19:23])   
            else:
                return
            file_path = path + file           
            if (temp_year == year):
                count=count+1
                month_aod_550=SatelliteData(satellite,file_path).aod_550
                month_aod_550[month_aod_550<0]=0
                year_aod=np.add(year_aod,month_aod_550)
    if count==0:
        year_aod=np.array([])
    else:
        year_aod=year_aod/count
        year_aod[year_aod==0]=-9999            
    return year_aod

def getSeasonAOD(satellite,year,season,path):
    #已知卫星、年份和季节（spring,summer等），求季平均AOD
    files=os.listdir(path)
    season_aod=np.array([0])
    count=0
    years=[year,year,year]
    if season=="winter":
        years[1]=year+1
        years[2]=year+1
        months=[12,1,2]
    elif season=="spring":
        months=[3,4,5]
    elif season=="summer":
        months=[6,7,8]
    elif season=="autumn":
        months=[9,10,11]
    for (i,j) in zip(years,months):
        for file in files:
            if not os.path.isdir(file):
                if satellite=="modis":
                    temp_year = int(file.split('.')[1][15:19])
                    temp_month=int(file.split('.')[1][19:21])
                elif satellite=="avhrr":
                    temp_year=int(file[19:23])
                    temp_month=int(file[24:26])
                else:
                    return
                file_path = path + file           
                if (temp_year == i and temp_month==j):
                    count=count+1
                    month_aod_550=SatelliteData(satellite,file_path).aod_550
                    month_aod_550[month_aod_550<0]=0
                    season_aod=np.add(season_aod,month_aod_550)    
    if count==0:
        season_aod=np.array([])
    else:
        season_aod=season_aod/count
        season_aod[season_aod==0]=-9999            
    return season_aod

def getMonthAOD(satellite,year,month,path):
    date=str(year)+str(month)
    print(date)
    files = os.listdir(path)
    month_aod = np.array([0])
    count=0
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
                count=count+1
                satellite_data = SatelliteData(satellite,file_path)
                month_aod = satellite_data.aod_550
    if count==0:
        month_aod=np.array([])           
    return month_aod

def getMap(path,satellite, date,area,flag):
    if flag=="year":
        year=int(date)
        aod=getYearAOD(satellite,path,year)
    elif flag=="month":
        year=int(date[0:4])
        month=int(date[4:])
        aod=getMonthAOD(satellite,year,month,path)
    elif flag=="season":
        #season的格式为“2004-spring”
        year=int(date.split('-')[0])
        season=date.split('-')[1]
        aod=getSeasonAOD(satellite,year,season,path)
    if not aod.any():
        return "",""
    if(area=="china"):
        #全国地理底图的aod数据
        image_name=image.plotChina_image(aod,date,satellite)
    elif (area=="jingjinji"):
        #京津冀经度（113,120）,纬度(36,43)
        image_name=image.plot_VectorClipImage(aod,date,113,36,120,42.8,"jingjinji",satellite)
    elif (area=="changsanjiao"):
        #长三角经纬度（118,123），纬度（28,34）
        image_name=image.plot_VectorClipImage(aod,date,115.5,27.7,123,34.8,"changsanjiao",satellite)
    elif(area=="zhusanjiao"):
        #珠三角经度(111,116)，纬度(21,25)
        image_name=image.plot_VectorClipImage(aod,date,111.2,21.5,115.5,24.5,"zhusanjiao",satellite)
    else:
        image_name=""
        return "",""
    sites_aod=getSitesAOD(satellite,aod,area,date)
    return image_name,sites_aod 


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
   
    image_name,sites_aod = getMap(files_path_avhrr,"avhrr", "2006-spring","china","season")
    #image_name,sites_aod = monthMap(files_path_avhrr,"avhrr", 1996, 1,"zhusanjiao")
    #image_name,sites_aod=yearMap(files_path_avhrr,"avhrr",2010,"china")
    #image_name,sites_aod=yearMap(files_path_modis,"modis",2010,"jingjinji")
    ''' print(month_aod)
    print(sites_aod) '''
    # print("first 10 items in image: {}".format(month_aod[:10]))
