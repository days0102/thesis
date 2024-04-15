import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

df = pd.read_csv('posix.csv', delimiter=',')
columns = set([
    c for c in df.columns if 'perc' in c.lower() or 'log10' in c.lower()
]).difference(["POSIX_LOG10_agg_perf_by_slowest"])

# print(df[list(columns)])

X, y = df['POSIX_BYTES_READ'], df.POSIX_agg_perf_by_slowest
# X, y = df['POSIX_READS','POSIX_BYTES_READ'], df.POSIX_agg_perf_by_slowest
z=df['POSIX_READS']

styles = plt.style.available


for style in styles:

    # plt.scatter(z,X,y)
    # 创建一个 Matplotlib 图形对象
    fig = plt.figure()

    plt.style.use(style)
    plt.rcParams['font.sans-serif'] = ['SimHei']

    # 创建一个三维坐标轴对象
    ax = fig.add_subplot(111, projection='3d')

    # 绘制散点图
    ax.scatter(z,X, y)

    # 设置坐标轴标签
    ax.set_xlabel('read')
    ax.set_ylabel('read bytes')
    ax.set_zlabel('perf')

        
    # 设置坐标轴箭头
    # ax.arrow
    # ax.quiver(0, 0, 0, 1, 0, 0, length=0.1, normalize=True, color='r')  # X 轴箭头
    # ax.quiver(0, 0, 0, 0, 1, 0, length=0.1, normalize=True, color='g')  # Y 轴箭头
    # ax.quiver(0, 0, 0, 0, 0, 1, length=0.1, normalize=True, color='b')  # Z 轴箭头
    # 添加坐标轴箭头
    arrow_length = 0.1
    ax.plot([0, arrow_length], [0, 0], [0, 0], color='r')  # x 轴箭头
    ax.plot([0, 0], [0, arrow_length], [0, 0], color='g')  # y 轴箭头
    ax.plot([0, 0], [0, 0], [0, arrow_length], color='b')  # z 轴箭头

    plt.tight_layout()

    plt.show()