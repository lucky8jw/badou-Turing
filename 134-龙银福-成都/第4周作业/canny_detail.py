import math
import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # 加载原始图像
    pic_path = 'lenna.png'
    img = plt.imread(pic_path)

    # 图像可视化
    fig = plt.figure()
    fig.canvas.set_window_title("Canny边缘检测")  # 设置窗口名称
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决plt中的中文不可显示的问题
    plt.rcParams['axes.unicode_minus'] = False
    plt.subplot(231), plt.title("原图像"), plt.imshow(img), plt.axis('off')
    # .png图片在这里的存储格式是0到1的浮点数，所以要扩展到255再计算
    if pic_path[-4:] == '.png':
        img = img * 255  # 还是浮点数类型

    # [1] 灰度化：在channel维度取均值就是灰度化([height,width,channel])
    img = img.mean(axis=-1)
    plt.subplot(232), plt.title("灰度化"), plt.imshow(img, cmap='gray'), plt.axis('off')

    # [2] 高斯滤波
    sigma = 0.5  # 标准差(可调)：高斯平滑时的高斯核参数, 标准差的值越小, 图像的形状越廋
    dim = int(np.round(6 * sigma + 1))  # round是四舍五入函数，根据标准差求高斯核是几乘几的，也就是维度
    if dim % 2 == 0:  # 最好是奇数,不是的话加一变成奇数
        dim += 1
    Gaussian_filter = np.zeros([dim, dim])  # 存储高斯核(5x5)，这是数组不是列表
    tmp = [i - dim // 2 for i in range(dim)]  # 生成一个序列 [-2 -1 0 1 2]
    n1 = 1 / (2 * math.pi * sigma ** 2)  # 计算高斯核
    n2 = -1 / (2 * sigma ** 2)
    for i in range(dim):
        for j in range(dim):
            Gaussian_filter[i, j] = n1 * math.exp(n2 * (tmp[i] ** 2 + tmp[j] ** 2))
    Gaussian_filter = Gaussian_filter / Gaussian_filter.sum()
    dx, dy = img.shape
    img_new = np.zeros(img.shape)  # 存储平滑之后的图像，zeros函数得到的是浮点型数据
    tmp = dim // 2  # tmp: 2 --> 边缘填充的圈数
    img_pad = np.pad(img, ((tmp, tmp), (tmp, tmp)), 'constant')  # 边缘填补，constant_values缺省，则默认填充均为0
    for i in range(dx):
        for j in range(dy):
            img_new[i, j] = np.sum(img_pad[i:i + dim, j:j + dim] * Gaussian_filter)
    plt.subplot(233), plt.title("高斯滤波"), plt.axis('off')
    # img_new是255的浮点型数据，强制类型转换为np.uint8才能进行可视化
    plt.imshow(img_new.astype(np.uint8), cmap='gray')

    # [3] 求梯度检测边缘
    # 以下两个是滤波求梯度用的sobel矩阵(检测图像中的水平、垂直和对角边缘)
    sobel_kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_kernel_y = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    img_tidu_x = np.zeros(img_new.shape)  # 存储梯度图像
    img_tidu_y = np.zeros([dx, dy])
    img_tidu = np.zeros(img_new.shape)
    img_pad = np.pad(img_new, ((1, 1), (1, 1)), 'constant')  # 核为3x3，边缘填补1，保证输入输出图像大小一致
    for i in range(dx):
        for j in range(dy):
            img_tidu_x[i, j] = np.sum(img_pad[i:i + 3, j:j + 3] * sobel_kernel_x)  # x方向
            img_tidu_y[i, j] = np.sum(img_pad[i:i + 3, j:j + 3] * sobel_kernel_y)  # y方向
            img_tidu[i, j] = np.sqrt(img_tidu_x[i, j] ** 2 + img_tidu_y[i, j] ** 2)
    img_tidu_x[img_tidu_x == 0] = 0.00000001  # img_tidu_x作为除数不能为0
    angle = img_tidu_y/img_tidu_x
    plt.subplot(234), plt.title("Sobel算子检测边缘"), plt.axis('off')
    plt.imshow(img_tidu.astype(np.uint8), cmap='gray')

    # [4] 非极大值抑制
    img_yizhi = np.zeros(img_tidu.shape)
    for i in range(1, dx - 1):
        for j in range(1, dy - 1):
            flag = True  # 在8邻域内是否要抹去做个标记
            temp = img_tidu[i - 1:i + 2, j - 1:j + 2]  # 梯度幅值的8邻域矩阵
            if angle[i, j] <= -1:  # 使用线性插值法判断抑制与否
                num_1 = (temp[0, 1] - temp[0, 0]) / angle[i, j] + temp[0, 1]
                num_2 = (temp[2, 1] - temp[2, 2]) / angle[i, j] + temp[2, 1]
                if not (img_tidu[i, j] > num_1 and img_tidu[i, j] > num_2):  # 如果梯度不是极大值，则抹去
                    flag = False
            elif angle[i, j] >= 1:
                num_1 = (temp[0, 2] - temp[0, 1]) / angle[i, j] + temp[0, 1]
                num_2 = (temp[2, 0] - temp[2, 1]) / angle[i, j] + temp[2, 1]
                if not (img_tidu[i, j] > num_1 and img_tidu[i, j] > num_2):
                    flag = False
            elif angle[i, j] > 0:
                num_1 = (temp[0, 2] - temp[1, 2]) * angle[i, j] + temp[1, 2]
                num_2 = (temp[2, 0] - temp[1, 0]) * angle[i, j] + temp[1, 0]
                if not (img_tidu[i, j] > num_1 and img_tidu[i, j] > num_2):
                    flag = False
            elif angle[i, j] < 0:
                num_1 = (temp[1, 0] - temp[0, 0]) * angle[i, j] + temp[1, 0]
                num_2 = (temp[1, 2] - temp[2, 2]) * angle[i, j] + temp[1, 2]
                if not (img_tidu[i, j] > num_1 and img_tidu[i, j] > num_2):
                    flag = False
            if flag:  # flag为True, 则为极大值, 保留下来, 其余点为0
                img_yizhi[i, j] = img_tidu[i, j]
    plt.subplot(235), plt.title("非极大值抑制"), plt.axis('off')
    plt.imshow(img_yizhi.astype(np.uint8), cmap='gray')

    # [5] 双阈值检测: 连接边缘
    # 遍历所有一定是边的点,查看8邻域是否存在有可能是边的点，进栈
    lower_boundary = img_tidu.mean() * 0.5  # 低阈值
    high_boundary = lower_boundary * 3  # 高阈值: 低阈值的三倍
    zhan = []
    for i in range(1, img_yizhi.shape[0] - 1):  # 不考虑外圈
        for j in range(1, img_yizhi.shape[1] - 1):
            if img_yizhi[i, j] >= high_boundary:  # 强边缘像素
                img_yizhi[i, j] = 255
                zhan.append([i, j])  # 取一定是边的点
            elif img_yizhi[i, j] <= lower_boundary:  # 舍去
                img_yizhi[i, j] = 0

    while not len(zhan) == 0:  # zhan中包含了所有的强边缘像素, 当zhan中没有强边缘像素时停止
        temp_1, temp_2 = zhan.pop()  # 出栈: pop()函数用于移除列表中的一个元素（默认最后一个元素），并且返回该元素的值
        a = img_yizhi[temp_1 - 1:temp_1 + 2, temp_2 - 1:temp_2 + 2]
        if (a[0, 0] < high_boundary) and (a[0, 0] > lower_boundary):
            img_yizhi[temp_1 - 1, temp_2 - 1] = 255  # 这个像素点标记为边缘
            zhan.append([temp_1 - 1, temp_2 - 1])  # 进栈
        if (a[0, 1] < high_boundary) and (a[0, 1] > lower_boundary):
            img_yizhi[temp_1 - 1, temp_2] = 255
            zhan.append([temp_1 - 1, temp_2])
        if (a[0, 2] < high_boundary) and (a[0, 2] > lower_boundary):
            img_yizhi[temp_1 - 1, temp_2 + 1] = 255
            zhan.append([temp_1 - 1, temp_2 + 1])
        if (a[1, 0] < high_boundary) and (a[1, 0] > lower_boundary):
            img_yizhi[temp_1, temp_2 - 1] = 255
            zhan.append([temp_1, temp_2 - 1])
        if (a[1, 2] < high_boundary) and (a[1, 2] > lower_boundary):
            img_yizhi[temp_1, temp_2 + 1] = 255
            zhan.append([temp_1, temp_2 + 1])
        if (a[2, 0] < high_boundary) and (a[2, 0] > lower_boundary):
            img_yizhi[temp_1 + 1, temp_2 - 1] = 255
            zhan.append([temp_1 + 1, temp_2 - 1])
        if (a[2, 1] < high_boundary) and (a[2, 1] > lower_boundary):
            img_yizhi[temp_1 + 1, temp_2] = 255
            zhan.append([temp_1 + 1, temp_2])
        if (a[2, 2] < high_boundary) and (a[2, 2] > lower_boundary):
            img_yizhi[temp_1 + 1, temp_2 + 1] = 255
            zhan.append([temp_1 + 1, temp_2 + 1])
    # 所有不是强边缘的像素均设为0
    for i in range(img_yizhi.shape[0]):
        for j in range(img_yizhi.shape[1]):
            if img_yizhi[i, j] != 0 and img_yizhi[i, j] != 255:
                img_yizhi[i, j] = 0
    plt.subplot(236), plt.title("双阈值检测")
    plt.imshow(img_yizhi.astype(np.uint8), cmap='gray')
    plt.axis('off')  # 关闭坐标刻度值

    plt.show()
