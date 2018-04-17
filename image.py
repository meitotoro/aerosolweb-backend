# -*- coding: utf-8 -*-
"""图像处理模块"""
import numpy as np
from mpl_toolkits.basemap import Basemap
import shapefile
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import matplotlib
from matplotlib.font_manager import *
import matplotlib.pyplot as plt
from enum import Enum,unique
import json

myfont=FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
matplotlib.rcParams["axes.unicode_minus"]=False
def creatDateString(date):
    '''将时间“2004”“200401”“2004-spring”转换为字符串格式'''
    if date.find('-')==-1 and len(date)!=4:
        year=date[0:4]
        month=date[4:]
        date=year+"-"+month 
    return date

def clipImage(data,satellite,minLon,minLat,maxLon,maxLat):
    data[data > 1.5] = 1.5  
    if satellite=="modis":#modis原始数据经度35-150,0.1度一个像素，纬度15-60
        minrow_index=int(600-10*maxLat)
        maxrow_index=int(600-10*minLat)
        mincolumn_index=int(10*minLon-350)
        maxcolumn_index=int(10*maxLon-350)
    elif satellite=="avhrr":
        minrow_index=int(450-10*maxLat)
        maxrow_index=int(450-10*minLat)
        mincolumn_index=int(10*minLon-750)
        maxcolumn_index=int(10*maxLon-750)
    elif satellite=="fy": #fy数据纬度15-57，经度70-138度,分辨率0.05度
        minrow_index=int(1140-20*maxLat)
        maxrow_index=int(1140-20*minLat)
        mincolumn_index=int(20*minLon-1400)
        maxcolumn_index=int(20*maxLon-1400)
    else:
        return        
    data = data[minrow_index:maxrow_index, mincolumn_index:maxcolumn_index]  #切片后的数据
    img_data = np.ma.masked_equal(data, -9.999)
    return img_data

def plotChina_image(data,date,satellite):
    date=creatDateString(date)
    """从aod数据生成图像"""
    data[data > 1.5] = 1.5  
    if satellite=="modis":#原始数据经度35-150,0.1度一个像素，纬度15-60
        data = data[30:450, 350:1030]  #切片后的数据纬度15-57，经度70-138度，包含了中国的国界线
    img_data = np.ma.masked_equal(data, -9.999)
    min_value = 0
    max_value = 1.6
    # create figure and axes instances
    fig = plt.figure()
    m = Basemap(
        projection='merc',
        llcrnrlon=70,
        llcrnrlat=15,
        urcrnrlon=138,
        urcrnrlat=57,
        resolution='l')
    parallels = np.arange(15, 57, 10.)
    meridians = np.arange(70, 138, 10.) 
    lats, lons = np.mgrid[57:15:-0.1, 70:138:0.1]
    if satellite=="modis":       
        # add title
        plt.title('MODIS AOD_'+date)
        filename="modis-aod-"+date+"-china.png"
    elif satellite=="avhrr": #avhrr数据经度75-135,0.1度一个像素，纬度15-45
        lats, lons = np.mgrid[45:15:-0.1, 75:135:0.1]  
        # add title
        plt.title('AVHRR AOD_'+date)
        filename="avhrr-aod-"+date+"-china.png"   
    elif satellite=='fy':
        lats, lons = np.mgrid[57:15:-0.05, 70:138:0.05]
        plt.title('FY AOD_'+date)
        filename="fy-aod-"+date+"-china.png"

    # read shapefile.生成全国底图的image
    m.readshapefile("shape_files/ChinaProvince", "ChinaProvince")
    # draw coastlines, state and country boundaries, edge of map.
    m.drawcoastlines(linewidth=0.3)
    # draw parallels.    
    m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
    # draw meridians    
    m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)    
    # draw filled contours.
    clevs = np.arange(min_value, max_value, 0.1)
    print(lons.shape," ",lats.shape," ",img_data.shape)
    cs = m.contourf(
        lons, lats, img_data, clevs, cmap=plt.cm.rainbow, latlon=True)    
    # add colorbar.
    cbar = m.colorbar(cs, location='bottom', pad="8%",ticks=[0.0,0.3,0.6,0.9,1.2,1.5])
    cbar.set_label('Aerosol Optical Depth')
    plt.margins()
    fig.canvas.draw()
    width, height = fig.canvas.get_width_height()
    data = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    data.shape = (width, height, 4)
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    data = np.roll(data, 3, axis=2)
    #plt.show()    
    #fig.tight_layout()
    if satellite=="modis":
        plt.savefig("aod-image/modis-aod-%s-china.png" % date, format = 'png',bbox_inches='tight')
    elif satellite=="avhrr":
        plt.savefig("aod-image/avhrr-aod-%s-china.png" % date, format = 'png',bbox_inches='tight')
    elif satellite=="fy":
        plt.savefig("aod-image/fy-aod-%s-china.png" % date, format = 'png',bbox_inches='tight')
    else:
        return    
    plt.close("all")
    return filename

def readSitesCor():
    with open("area-site.txt",'r') as load_f:
        load_dict = json.load(load_f)
        print(load_dict)
        return load_dict

def plot_VectorClipImage(data,date,minLon,minLat,maxLon,maxLat,name,satellite):
    date=creatDateString(date)
    """从aod数据生成图像"""
    data=clipImage(data,satellite,minLon,minLat,maxLon,maxLat)
    min_value = 0
    max_value = 1.6
    # create figure and axes instances
    fig = plt.figure()
    #ax=fig.add_subplot(111)
    ax = plt.gca()
    m = Basemap(
        projection='merc',
        llcrnrlon=minLon,
        llcrnrlat=minLat,
        urcrnrlon=maxLon,
        urcrnrlat=maxLat,
        resolution='l')
    shapefile_path="shape_files/"+name+"/"+name
    m.readshapefile(shapefile_path, name)
    parallels=[]
    meridians=[]
    sitesCoors=readSitesCor()
    sites=sitesCoors[name]    
    for site in sites:
        x,y=sites[site][0],sites[site][1]     
        plt.text(x,y,site,FontProperties=myfont,color="black",fontsize=7)  
    if name=='jingjinji':
        parallels=np.arange(36,43,2)
        meridians=np.arange(114,121,2)
        beijing_x,beijing_y=m(116.2,40.2)
        plt.text(beijing_x,beijing_y,u'北京',FontProperties=myfont,color="red",fontsize=8)         
    elif name=='zhusanjiao':
        parallels=np.arange(22,25,1)
        meridians=np.arange(111,116,1)
    else:
        parallels=np.arange(28,35,2)
        meridians=np.arange(116,124,2)                
    m.drawparallels(parallels, linewidth=0.5,dashes=[5, 2,2,2], labels=[1, 0, 0, 0], fontsize=10)
    m.drawmeridians(meridians, linewidth=0.5,dashes=[5, 2,2,2], labels=[0, 0, 0, 1], fontsize=10)
    if satellite=="fy":
        lats, lons = np.mgrid[maxLat:minLat:-0.05, minLon:maxLon:0.05]
        clevs = np.arange(min_value, max_value, 0.05)
    else:
        lats, lons = np.mgrid[maxLat:minLat:-0.1, minLon:maxLon:0.1]
        clevs = np.arange(min_value, max_value, 0.1)
    cs = m.contourf(
        lons, lats, data, clevs, cmap=plt.cm.rainbow, latlon=True)
    
    #生成区域光学厚度图
    #读取矢量数据
    shp_path="shape_files/"+name+"/"+name+".shp"
    #shp_path="shape_files/Zhusanjiao_Cities/Dongguan.shp"
    sf=shapefile.Reader(shp_path)
    #生成京津冀的边缘区域clip
    vertices = []
    codes = []
    for shape_rec in sf.shapeRecords():
        pts = shape_rec.shape.points
        prt = list(shape_rec.shape.parts) + [len(pts)]
        for i in range(len(prt) - 1):
            for j in range(prt[i], prt[i+1]):
                # project the coordinates
                x, y = m(pts[j][0], pts[j][1])
                vertices.append((x, y))
            vertices.append((0, 0))
            codes += [Path.MOVETO]
            codes += [Path.LINETO] * (prt[i+1] - prt[i] -1)
            codes += [Path.CLOSEPOLY]
    clip = Path(vertices, codes)
    clip = PathPatch(clip, facecolor='none', edgecolor='none')
    # draw a invisible patch, otherwise the clip has no effect
    ax.add_patch(clip)

    # 裁切数据
    for contour in cs.collections:
        contour.set_clip_path(clip)
    # add colorbar.
    cbar = m.colorbar(cs, location='bottom', pad="8%",ticks=[0.0,0.3,0.6,0.9,1.2,1.5])
    cbar.set_label('Aerosol Optical Depth')
    # add title
    name=name.capitalize()
    plt.title(name+'_'+satellite.upper()+'_'+'AOD_'+date)
    plt.margins()
    fig.canvas.draw()
    width, height = fig.canvas.get_width_height()
    data = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    data.shape = (width, height, 4)
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    data = np.roll(data, 3, axis=2)
   
    #plt.show()
    filename=satellite+"-aod-"+date+"-"+name.lower()+".png"
    #fig.tight_layout()
    plt.savefig("aod-image/"+filename, format = 'png',bbox_inches='tight')
    plt.close("all")
    return filename
