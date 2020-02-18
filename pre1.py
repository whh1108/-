import time
import json
import requests
from datetime import datetime
import numpy as np
import matplotlib
import matplotlib.figure
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Polygon
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams['font.sans-serif'] = ['FangSong']  # 设置默认字体
#不加这个 无法识别中文
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时'-'显示为方块的问题

def catch_area_distribute():

    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5&callback=&_=%d' % int(time.time() * 1000)
    data = json.loads(requests.get(url=url).json()['data'])
    # print(data.keys())
    province = {}
    #定位到省份和确诊数据所在数据
    num = data['areaTree'][0]['children']

    #遍历所获得数据
    for item in num:
        #遍历name，由于省份name是json文件是第一级，城市的name是子节点，所以并不冲突
        if item['name'] not in province:
            #遍历后加入之前定义的空字典
            province.update({item['name']:0})
        for city_data in item['children']:
            #将省份以及确证数据相加，确证数据在total的confilm中
            province[item['name']] +=int(city_data['total']['confirm'])
    return province

def polt_draw_dist():
    data = catch_area_distribute()
    print(data)
    font = FontProperties(fname='res/simsun.ttf', size=14)
    # 下面是北纬0-60度，东经70-130度
    lat_min = 0
    lat_max = 60
    lon_min = 70
    lon_max = 140
    # alpha为透明度，linewidth：线宽
    handles = [
        matplotlib.patches.Patch(color='#ffaa85', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#ff7b69', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#bf2121', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#7f1818', alpha=1, linewidth=0),
    ]
    #图示
    labels = ['1-99人','100-999人','1000-9999人','>10000人']
    # matplotlib绘图工具包

    # figure其中一个子模块，共定义了三个类AxesStack、Figure、SubplotParams 。就是呈现图片的那个窗口。

    # Figure：matplotlib.figure下的一个类。
    fig = matplotlib.figure.Figure()
    # 设置绘图板的尺寸
    fig.set_size_inches(10, 8)
    axes = fig.add_axes((0.1, 0.12, 0.8, 0.8))  # rect = l,b,w,h
    # 下面是关于basemap的使用
    m = Basemap(llcrnrlon=lon_min, urcrnrlon=lon_max, llcrnrlat=lat_min, urcrnrlat=lat_max, resolution='l', ax=axes)
    # 读取引用文件
    m.readshapefile("res/china-shapefiles-master/china", 'province', drawbounds=True)
    m.readshapefile('res/china-shapefiles-master/china_nine_dotted_line', 'section', drawbounds=True)
    m.drawcoastlines(color='black')  # 洲际线
    m.drawcountries(color='black')  # 国界线
    m.drawparallels(np.arange(lat_min, lat_max, 10), labels=[1, 0, 0, 0])  # 画经度线
    m.drawmeridians(np.arange(lon_min, lon_max, 10), labels=[0, 0, 0, 1])  # 画纬度线

    for info, shape in zip(m.province_info, m.province):
        pname = info['OWNER'].strip('\x00')
        fcname = info['FCNAME'].strip('\x00')
        if pname != fcname:  # 不绘制海岛
            continue

        for key in data.keys():
            if key in pname:
                if data[key] == 0:
                    color = '#f0f0f0'
                elif data[key] < 100:
                    color = '#ffaa85'
                elif data[key] < 1000:
                    color = '#ff7b69'
                elif data[key] < 10000:
                    color = '#bf2121'
                else:
                    color = '#7f1818'
                break

        poly = Polygon(shape, facecolor=color, edgecolor=color)
        axes.add_patch(poly)

    axes.legend(handles, labels, bbox_to_anchor=(0.5, -0.11), loc='lower center', ncol=4, prop=font)
    axes.set_title("NCP疫情地图", fontproperties=font)
    FigureCanvasAgg(fig)
    fig.savefig('NCP疫情地图.png')
def catch_daily():
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5&callback=&_=%d' % int(time.time() * 1000)
    pre_data = json.loads(requests.get(url=url).json()['data'])
    #以下为各种数据，以数组的形式存储
    date_list = list() # 日期
    confirm_list = list() # 确诊
    suspect_list = list() # 疑似
    dead_list = list() # 死亡
    heal_list = list() # 治愈
    chinaDayAddList =pre_data['chinaDayAddList']
    # print(chinaDayAddList)
    for item in chinaDayAddList:
        month, day = item['date'].split('.')
        # 添加年月日到date_list,由于数据源没有年，自己添加了年
        date_list.append(datetime.strptime('2020-%s-%s' % (month, day), '%Y-%m-%d'))
        # 其他数据就不再解释，由数据源获取就是。
        # 举例第一个 confilm是由 \"confirm\": \"440\",\n ，先定位item['confirm']，再找到int的数据。
        confirm_list.append(int(item['confirm']))
        suspect_list.append(int(item['suspect']))
        dead_list.append(int(item['dead']))
        heal_list.append(int(item['heal']))
    return date_list,confirm_list,suspect_list,dead_list,heal_list

def plot_daily():
    # 获取上述数据
    date_list, confirm_list, suspect_list, dead_list, heal_list = catch_daily()
    # print(confirm_list)
    # num:图像编号或名称，数字为编号 ，字符串为名称,facecolor:背景颜色,figsize:指定figure的宽和高，单位为英寸；
    plt.figure('新型肺炎疫情统计图表', facecolor='#f4f4f4', figsize=(10, 8))
    # 设置标题，fontsize:字体大小

    plt.title('NCP疫情曲线', fontsize=20)
    # 接下去为重要的绘图功能，
    # plt.plot()函数的本质就是根据点连接线。根据x(数组或者列表) 和 y(数组或者列表)组成点，然后连接成线。
    # 首先对于x轴，我们要绘制日期为x轴，传date_list作为x轴的数据
    # 对于y轴，y轴为展示的数量，图示的label传入后推测会自动加图示，大概是plot的方法的调用。
    plt.plot(date_list, confirm_list, label='确诊')
    plt.plot(date_list, suspect_list, label='疑似')
    plt.plot(date_list, dead_list, label='死亡')
    plt.plot(date_list, heal_list, label='治愈')
    # 以下基本为固定使用方法，直接使用
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))  # 格式化时间轴标注
    plt.gcf().autofmt_xdate()  # 优化标注（自动倾斜）
    plt.grid(linestyle=':')  # 显示网格
    plt.legend(loc='best')  # 显示图例
    plt.savefig('NCP疫情曲线.png')  # 保存为文件

def catch_daily_rate():
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5&callback=&_=%d' % int(time.time() * 1000)
    pre_data = json.loads(requests.get(url=url).json()['data'])
    hubeiRate_list = list()
    notHubeiRate_list = list()
    countryRate_list = list()
    date_list = list()  # 日期
    chinaDayAddList = pre_data['dailyDeadRateHistory']
    # print(chinaDayAddList)
    for item in chinaDayAddList:
        month, day = item['date'].split('.')
        date_list.append(datetime.strptime('2020-%s-%s' % (month, day), '%Y-%m-%d'))
        hubeiRate_list.append(item['hubeiRate'])
        notHubeiRate_list.append(item['notHubeiRate'])
        countryRate_list.append(item['countryRate'])
    hubeiRate_list.sort()
    notHubeiRate_list.sort()
    countryRate_list.sort()
    return date_list,hubeiRate_list,notHubeiRate_list,countryRate_list



def plot_daily_rate():
    date_list,hubeiRate_list,notHubeiRate_list,countryRate_list = catch_daily_rate()
    # plt.figure('全国NCP死亡率疫情曲线', facecolor='#f4f4f4', figsize=(10, 8))
    # plt.title('全国NCP死亡率疫情曲线', fontsize=20)
    # plt.figure('湖北NCP死亡率疫情曲线', facecolor='#f4f4f4', figsize=(10, 8))
    # plt.title('湖北NCP死亡率疫情曲线', fontsize=20)
    plt.figure('非湖北NCP死亡率疫情曲线', facecolor='#f4f4f4', figsize=(10, 8))
    plt.title('非湖北NCP死亡率疫情曲线', fontsize=20)
    # plt.plot(date_list, hubeiRate_list, label='湖北地区死亡率')
    plt.plot(date_list, notHubeiRate_list, label='非湖北地区死亡率')
    #plt.plot(date_list, countryRate_list, label='全国死亡率')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))  # 格式化时间轴标注
    plt.gcf().autofmt_xdate()  # 优化标注（自动倾斜）
    plt.grid(linestyle=':')  # 显示网格
    plt.legend(loc='best')  # 显示图例
    #plt.savefig('全国地区死亡率疫情曲线.png')  # 保存为文件
    #plt.savefig('湖北地区死亡率疫情曲线.png')  # 保存为文件
    plt.savefig('非湖北地区死亡率疫情曲线.png')  # 保存为文件


if __name__ == '__main__':
    # polt_draw_dist()
    # plot_daily()
    plot_daily_rate()


