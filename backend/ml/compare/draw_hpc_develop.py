import matplotlib
# matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

from matplotlib.pyplot import MultipleLocator

plt.rcParams['font.sans-serif'] = ['SimHei']
# 定义数据
years = [
    "1993年6月", "1993年11月", "1994年6月", "1994年11月", "1995年6月", "1995年11月",
    "1996年6月", "1996年11月", "1997年6月", "1997年11月", "1998年6月", "1998年11月",
    "1999年6月", "1999年11月", "2000年6月", "2000年11月", "2001年6月", "2001年11月",
    "2002年6月", "2002年11月", "2003年6月", "2003年11月", "2004年6月", "2004年11月",
    "2005年6月", "2005年11月", "2006年6月", "2006年11月", "2007年6月", "2007年11月",
    "2008年6月", "2008年11月", "2009年6月", "2009年11月", "2010年6月", "2010年11月",
    "2011年6月", "2011年11月", "2012年6月", "2012年11月", "2013年6月", "2013年11月",
    "2014年6月", "2014年11月", "2015年6月", "2015年11月", "2016年6月", "2016年11月",
    "2017年6月", "2017年11月", "2018年6月", "2018年11月", "2019年6月", "2019年11月",
    "2020年6月", "2020年11月", "2021年6月", "2021年11月", "2022年6月", "2022年11月",
    "2023年6月", "2023年11月"
]

values = [
    59.7,
    124,
    143.4,
    170,
    170,
    170,
    220.4,
    368.2,
    1100,
    1300,
    1300,
    1300,
    2100,
    2400,
    2400,
    4900,
    7200,
    7200,
    35900,
    35900,
    35900,
    35900,
    35900,
    70700,
    136800,
    280600,
    280600,
    280600,
    280600,
    478200,
    1000000,
    1100000,
    1100000,
    1800000,
    1800000,
    2600000,
    8200000,
    10500000,
    16300000,
    17600000,
    33900000,
    33900000,
    33900000,
    33900000,
    33900000,
    33900000,
    93000000,
    93000000,
    93000000,
    93000000,
    122300000,
    143500000,
    148600000,
    148600000,
    415500000,
    442000000,
    442000000,
    442000000,
    1100000000,
    1100000000,
    1200000000,
    1200000000,
]

styles = plt.style.available


for style in styles:
    # 创建图形
    fig=plt.figure()
    plt.style.use(style)
    plt.rcParams['font.sans-serif'] = ['SimHei']


    # date_format = "%Y年%m月"
    # # 将日期转换为 matplotlib 内部日期表示形式
    # dates = [datetime.strptime(date.replace("年", "-").replace("月", ""), "%Y-%m") for date in years]
    # print(dates)

    # 绘制折线图
    ax=plt.plot(years, values, marker='o', linestyle='-')

    # 设置横纵坐标标签和标题
    plt.xlabel('时间')
    plt.ylabel('性能')
    plt.title('高性能计算机性能增长趋势')
    # 使用对数坐标
    plt.yscale('log')
    # 设置纵坐标刻度为指定单位
    plt.yticks([
        10,100, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000,
        10000000000,
        # 100000000000, 1000000000000
    ], [
        '10 GFlop/s', '100 GFlop/s', '1 TFlop/s',
        '10 TFlop/s', '100 TFlop/s', '1 PFlop/s', '10 PFlop/s', '100 PFlop/s',
        '1 EFlop/s',
        '10 EFlop/s'
    ])
    # 设置 x 轴主要定位器为年份
    plt.gca().xaxis.set_major_locator(MultipleLocator(3))
    w, h = plt.gcf().get_size_inches()
    plt.gcf().set_size_inches(2*w, 1.5*h)

    # 旋转 x 轴标签
    plt.xticks(rotation=45)
    # plt.tick_params(axis='x', direction='out', pad=200)

    # 显示图例
    plt.legend(['性能'])

    # 显示图形
    plt.grid(True)
    plt.tight_layout()
    # plt.savefig('top500.svg')
    plt.show()