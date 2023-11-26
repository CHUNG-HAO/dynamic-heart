import random
from math import sin, cos, pi, log
from tkinter import *

CANVAS_WIDTH = 1900  # 畫布的宽
CANVAS_HEIGHT = 1080  # 畫布的高
CANVAS_CENTER_X = CANVAS_WIDTH / 2  
CANVAS_CENTER_Y = CANVAS_HEIGHT / 2  
IMAGE_ENLARGE = 11  # 放大比例
HEART_COLOR = "#ff2121"  # 颜色


def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    
    # 基礎函數
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

    # 放大
    x *= shrink_ratio
    y *= shrink_ratio

    # 移到畫布中央
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y

    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    """
    隨機內部擴散
    :param x: 原x
    :param y: 原y
    :param beta: 强度
    :return: 新坐標
    """
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())

    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)

    return x - dx, y - dy


def shrink(x, y, ratio):
    """
    抖動
    :param x: 原x
    :param y: 原y
    :param ratio: 比例
    :return: 新坐標
    """
    force = -1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.6)  # 这个参数...
    dx = ratio * force * (x - CANVAS_CENTER_X)
    dy = ratio * force * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p):
    """
    自訂義曲線函數
    :param p: 参数
    :return: 正弦
    """
    # 可以换其他的動態函數
    return 2 * (2 * sin(4 * p)) / (2 * pi)


class Heart:
    """
    愛心
    """

    def __init__(self, generate_frame=20):
        self._points = set()  # 原始愛心座標集合
        self._edge_diffusion_points = set()  # 邊緣擴散效果集合
        self._center_diffusion_points = set()  # 中心擴散效果集合
        self.all_points = {}  # 每帧痛太點座標
        self.build(2000)

        self.random_halo = 1000

        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
        # 愛心
        for _ in range(number):
            t = random.uniform(0, 2 * pi)  #隨機不到的地方造成缺口
            x, y = heart_function(t)
            self._points.add((x, y))

        # 愛心內擴散
        for _x, _y in list(self._points):
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))

        # 愛心內再次擴散
        point_list = list(self._points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        # 調整缩放比例
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 + (y - CANVAS_CENTER_Y) ** 2) ** 0.520)  # 参数

        dx = ratio * force * (x - CANVAS_CENTER_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTER_Y) + random.randint(-1, 1)

        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 10 * curve(generate_frame / 10 * pi)  # 縮放比例

        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))

        all_points = []

        # 光環
        heart_halo_point = set()  # 光環的點座標集合
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)  # 隨機不到的地方造成愛心缺口
            x, y = heart_function(t, shrink_ratio=11.6)  # 参数
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_point:
                # 處理新的點
                heart_halo_point.add((x, y))
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                size = random.choice((1, 2, 2))
                all_points.append((x, y, size))

        # 輪廓
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))

        # 内容
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points

    def render(self, render_canvas, render_frame):
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_rectangle(x, y, x + size, y + size, width=0, fill=HEART_COLOR)


def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
    render_canvas.delete('all')
    render_heart.render(render_canvas, render_frame)
    main.after(160, draw, main, render_canvas, render_heart, render_frame + 1)


if __name__ == '__main__':
    root = Tk()
    root.attributes('-fullscreen', True)  # 讓視窗全螢幕顯示

    # 獲取螢幕的寬度和高度
    CANVAS_WIDTH = root.winfo_screenwidth()
    CANVAS_HEIGHT = root.winfo_screenheight()
    CANVAS_CENTER_X = CANVAS_WIDTH / 2
    CANVAS_CENTER_Y = CANVAS_HEIGHT / 2

    canvas = Canvas(root, bg='black', height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
    canvas.pack()
    heart = Heart()
    draw(root, canvas, heart)
    root.mainloop()