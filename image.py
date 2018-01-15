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

myfont=FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
matplotlib.rcParams["axes.unicode_minus"]=False

def plotChina_image(data,year,month):
    date=str(year)+"-"+str(month)
    """从aod数据生成图像"""
    data[data > 1.5] = 1.5  #原始数据经度35-150,0.1度一个像素，纬度15-60
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
    # read shapefile.生成全国底图的image
    m.readshapefile("shape_files/ChinaProvince", "ChinaProvince")
    # draw coastlines, state and country boundaries, edge of map.
    m.drawcoastlines(linewidth=0.3)
    #m.drawcountries()
    # draw parallels.
    parallels = np.arange(15, 57, 10.)
    m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
    # draw meridians
    meridians = np.arange(70, 138, 10.)
    m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)
    lats, lons = np.mgrid[57:15:-0.1, 70:138:0.1]
    # draw filled contours.
    clevs = np.arange(min_value, max_value, 0.1)
    cs = m.contourf(
        lons, lats, img_data, clevs, cmap=plt.cm.rainbow, latlon=True)
    
    # add colorbar.
    cbar = m.colorbar(cs, location='bottom', pad="8%",ticks=[0.0,0.3,0.6,0.9,1.2,1.5])
    cbar.set_label('Aerosol Optical Depth')
    # add title
    plt.title('SARP AOD_'+date)
    plt.margins()
    fig.canvas.draw()
    width, height = fig.canvas.get_width_height()
    data = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    data.shape = (width, height, 4)
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    data = np.roll(data, 3, axis=2)
    #plt.show()
    filename="sarp-aod-"+date+".png"
    #fig.tight_layout()
    plt.savefig("aod-image/sarp-aod-%s.png" % date, format = 'png',bbox_inches='tight')
    plt.close("all")
    return filename
    
def plot_VectorClipImage(data,year,month,minLon,minLat,maxLon,maxLat,name):
    date=str(year)+"-"+str(month)
    """从aod数据生成图像"""
    data[data > 1.5] = 1.5  #原始数据经度35-150,0.1度一个像素，纬度15-60
    minrow_index=int(600-10*maxLat)
    maxrow_index=int(600-10*minLat)
    mincolumn_index=int(10*minLon-350)
    maxcolumn_index=int(10*maxLon-350)
    data = data[minrow_index:maxrow_index, mincolumn_index:maxcolumn_index]  #切片后的数据
    img_data = np.ma.masked_equal(data, -9.999)
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
    jingjinji_sites={
        #'beijing':[u"北京",116.2,40.2],
        'tianjin':[u"天津",117,39.13],
        'tangshan':[u'唐山',118.02,39.63],
        'qinhuangdao':[u'秦皇岛',119.,39.95],
        'chengde':[u'承德',117.2,41.1],
        'zhangjiakou':[u'张家口',114.87,40.82],
        'baoding':[u'保定',115,38.85],
        'langfang':[u'廊坊',116.2,39,53],
        'cangzhou':[u'沧州',116.43,38.23],
        'hengshui':[u'衡水',115.52,37.62],
        'shijiazhuang':[u'石家庄',114.18,38.03],
        'xingtai':[u'邢台',114.48,37.05],
        'handan':[u'邯郸',114.47,36.4]
    }
    changsanjiao_sites={
        'yancheng':[u"盐城",120,33.35],
        'nanjing':[u'南京',118.49,31.95],
        'yangzhou':[u'扬州',119.22,32.52],
        'taizhou':[u'泰州',119.93,32.46],
        'nantong':[u'南通',120.89,31.98],
        'changzhou':[u'常州',119.17,31.42],
        'wuxi':[u'无锡',120.11,31.49],
        'suzhou':[u'苏州',120.48,31.19],
        'shanghai':[u'上海',121.07,31],
        'huzhou':[u'湖州',119.69,30.69],
        'jiaxing':[u'嘉兴',120.55,30.60],
        'hangzhou':[u'杭州',119.2,29.97],
        'shaoxing':[u'绍兴',120.38,29.73],
        'jinhua':[u'金华',119.65,29.08],
        'ningbo':[u'宁波',121.15,29.77],
        'taizhou':[u'台州',120.92,28.76],
        'chuzhou':[u'滁州',117.8,32.5],
        'hefei':[u'合肥',117.03,31.82],
        'maanshan':[u'马鞍山',118.21,31.47],
        'wuhu':[u'芜湖',118.1,31.1],
        'tongling':[u'铜陵',117.71,30.85],
        'anqing':[u'安庆',116.26,30.44],
        'chizhou':[u'池州',117.09,30.26],
        'xuancheng':[u'宣城',118.53,30.65],
        'zhengjiang':[u'镇江',119.23,32.]
    }
    zhusanjiao_sites={        
        'guangzhou':[u'广州',113.4,23.3],
        'foshan':[u'佛山',112.9,23],
        'huizhou':[u'惠州',114.3,23.2],
        'jiangmen':[u'江门',112.6,22.3],
        'shenzhen':[u'深圳',113.9,22.6],
        'zhongshan':[u'中山',113.29,22.5],
        'zhuhai':[u'珠海',113.15,22.1],
        'zhaoqing':[u'肇庆',112.2,23.5],
        'dongguan':[u'东莞',113.75,22.9]
    }
    if name=='jingjinji':
        parallels=np.arange(36,43,2)
        meridians=np.arange(114,121,2)
        beijing_x,beijing_y=m(116.2,40.2)
        plt.text(beijing_x,beijing_y,u'北京',FontProperties=myfont,color="red",fontsize=8)        
        for key in jingjinji_sites:
            value=jingjinji_sites[key]
            text_site=value[0]
            x,y=m(value[1],value[2])      
            plt.text(x,y,text_site,FontProperties=myfont,color="black",fontsize=7)              
    elif name=='zhusanjiao':
        parallels=np.arange(22,25,1)
        meridians=np.arange(111,116,1)
        for key in zhusanjiao_sites:
            value=zhusanjiao_sites[key]
            text_site=value[0]
            x,y=m(value[1],value[2]) 
            plt.text(x,y,text_site,FontProperties=myfont,color="black",fontsize=7)
    else:
        parallels=np.arange(28,35,2)
        meridians=np.arange(116,124,2)
        for key in changsanjiao_sites:
            value=changsanjiao_sites[key]
            text_site=value[0]
            x,y=m(value[1],value[2])
            plt.text(x,y,text_site,FontProperties=myfont,color="black",fontsize=7)
    
    m.drawparallels(parallels, linewidth=0.5,dashes=[5, 2,2,2], labels=[1, 0, 0, 0], fontsize=10)
    m.drawmeridians(meridians, linewidth=0.5,dashes=[5, 2,2,2], labels=[0, 0, 0, 1], fontsize=10)
    lats, lons = np.mgrid[maxLat:minLat:-0.1, minLon:maxLon:0.1]
    # draw filled contours.
    clevs = np.arange(min_value, max_value, 0.1)
    cs = m.contourf(
        lons, lats, img_data, clevs, cmap=plt.cm.rainbow, latlon=True)
    
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
    plt.title(name+'_SARP AOD_'+date)
    plt.margins()
    fig.canvas.draw()
    width, height = fig.canvas.get_width_height()
    data = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    data.shape = (width, height, 4)
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    data = np.roll(data, 3, axis=2)
   
    #plt.show()
    filename="sarp-aod-"+date+"-"+name.lower()+".png"
    #fig.tight_layout()
    plt.savefig("aod-image/sarp-aod-%s-%s.png" % (date,name.lower()), format = 'png',bbox_inches='tight')
    plt.close("all")
    return filename
