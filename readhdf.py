import datetime
import math
import os

import pyhdf
import numpy as np

from pyhdf import SD
'''
输入经纬度坐标，找到对应的光学厚度值
'''
def readModisData(lat, lon):
    path = "/home/mei/aerosolweb-backend/data/MOD04_3K.A2015001.0225.006.2015033055335.hdf"
    obj = SD.SD(path, SD.SDC.READ)
    lon=obj.select("Longitude").get()
    lat=obj.select("Latitude").get()
    print lon
    
    ()


if __name__ == "__main__":
    readModisData()

