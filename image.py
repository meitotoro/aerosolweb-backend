# -*- coding: utf-8 -*-
"""图像处理模块"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import shapefile
from matplotlib.path import Path
from matplotlib.patches import PathPatch


def plot_image(data,year,month):
    date=str(year)+"-"+str(month)
    """从aod数据生成图像"""
    data[data > 1.5] = 1.5  #原始数据经度35-150,0.1度一个像素，纬度15-60
    data = data[30:450, 350:1030]  #切片后的数据纬度15-57，经度70-138度，包含了中国的国界线
    img_data = np.ma.masked_equal(data, -9.999)
    min_value = 0
    max_value = 1.6
    # create figure and axes instances

    # fig = plt.figure(figsize=(7, 4.5))
    china_m = Basemap(
        projection='merc',
        llcrnrlon=70,
        llcrnrlat=15,
        urcrnrlon=138,
        urcrnrlat=57,
        resolution='l')
    jingjinji_m=Basemap(
        projection='merc',
        llcrnrlon=113,
        llcrnrlat=36,
        urcrnrlon=120,
        urcrnrlat=43,
        resolution='l')
    jingjinji_m.readshapefile("shape_files/jingjinji/jingjinji", "jingjinji")
    parallels = np.arange(36, 43, 2.)
    m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
    meridians = np.arange(113, 120, 2.)
    m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)
    lats, lons = np.mgrid[43:36:-0.1, 113:120:0.1]
    # draw filled contours.
    clevs = np.arange(min_value, max_value, 0.1)
    cs = m.contourf(
        lons, lats, img_data, clevs, cmap=plt.cm.rainbow, latlon=True)
    
    #生成京津冀的光学厚度图
    fig_jingjinji=plt.figure(figsize=(7, 4.5))
    ax_jingjinji=fig_jingjinji.add_subplot(111)
    #读取京津冀地区矢量数据
    jingjinji_path="/home/mei/aerosolweb-backend/shape_files/jingjinji/jingjinji.shp"
    jingjinji_sf=shapefile.Reader(jingjinji_path)
    #生成京津冀的边缘区域clip
    for shape_rec in jingjinji_sf.shapeRecords():
        vertices = []
        codes = []
        pts = shape_rec.shape.points
        prt = list(shape_rec.shape.parts) + [len(pts)]
        for i in range(len(prt) - 1):
            for j in range(prt[i], prt[i+1]):
                vertices.append((pts[j][0], pts[j][1]))
            codes += [Path.MOVETO]
            codes += [Path.LINETO] * (prt[i+1] - prt[i] -2)
            codes += [Path.CLOSEPOLY]
        clip = Path(vertices, codes)
        clip = PathPatch(clip, transform=ax_jingjinji.transData)
    
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
    #画京津冀地区的aod图
    
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
    for contour in cs.collections:
        contour.set_clip_path(clip)
    plt.show()
    #plt.show()
    filename="sarp-aod-"+date+".png"
    #fig.tight_layout()
    plt.savefig("aod-image/sarp-aod-%s.png" % date, format = 'png',bbox_inches='tight')
    plt.close("all")
    return filename
