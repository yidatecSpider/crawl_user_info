# -*- coding: utf-8 -*-

import time
import requests
import cv2
import numpy as np
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from requests.utils import dict_from_cookiejar
import urllib3
from selenium.webdriver.common.by import By

urllib3.disable_warnings()
from PIL import Image
from io import BytesIO


class SlideCrack(object):
    def __init__(self, gap, bg, out=None):
        """
        init code
        :param gap: 缺口图片
        :param bg: 背景图片
        :param out: 输出图片
        """
        self.gap = gap
        self.bg = bg
        self.out = out

    @staticmethod
    def clear_white(img):
        # 清除图片的空白区域，这里主要清除滑块的空白
        img = cv2.imdecode(np.frombuffer(requests.get(url=img, verify=False).content, np.uint8), cv2.IMREAD_UNCHANGED)
        rows, cols, channel = img.shape
        min_x = 255
        min_y = 255
        max_x = 0
        max_y = 0
        for x in range(1, rows):
            for y in range(1, cols):
                t = set(img[x, y])
                if len(t) >= 2:
                    if x <= min_x:
                        min_x = x
                    elif x >= max_x:
                        max_x = x

                    if y <= min_y:
                        min_y = y
                    elif y >= max_y:
                        max_y = y
        img1 = img[min_x:max_x, min_y: max_y]
        return img1

    def template_match(self, tpl, target):
        th, tw = tpl.shape[:2]
        result = cv2.matchTemplate(target, tpl, cv2.TM_CCOEFF_NORMED)
        # 寻找矩阵(一维数组当作向量,用Mat定义) 中最小值和最大值的位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        tl = max_loc
        # br = (tl[0] + tw, tl[1] + th)
        # 绘制矩形边框，将匹配区域标注出来
        # target：目标图像
        # tl：矩形定点
        # br：矩形的宽高
        # (0,0,255)：矩形边框颜色
        # 1：矩形边框大小
        # cv2.rectangle(target, tl, br, (0, 0, 255), 2)
        # if self.out:
        #     cv2.imwrite(self.out, target)
        return tl[0]

    @staticmethod
    def image_edge_detection(img):
        edges = cv2.Canny(img, 100, 200)
        return edges

    def discern(self):
        img1 = self.clear_white(self.gap)
        img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        slide = self.image_edge_detection(img1)
        back = cv2.cvtColor(np.asarray(Image.open(BytesIO(requests.get(url=self.bg, verify=False).content))),
                            cv2.COLOR_RGB2GRAY)
        back = self.image_edge_detection(back)
        slide_pic = cv2.cvtColor(slide, cv2.COLOR_GRAY2RGB)
        back_pic = cv2.cvtColor(back, cv2.COLOR_GRAY2RGB)
        x = self.template_match(slide_pic, back_pic)  # 滑块偏移值
        # 输出横坐标, 即 滑块在图片上的位置
        return x


def get_distance(fg, bg):
    """
    计算滑动距离
    """
    sc = SlideCrack(fg, bg, "img/33.png")
    distance = int(sc.discern() // 4.1)
    return distance


def get_tracks(distance, rate=0.6, t=0.2, v=0):
    """
    将distance分割成小段的距离
    :param distance: 总距离
    :param rate: 加速减速的临界比例
    :param a1: 加速度
    :param a2: 减速度
    :param t: 单位时间
    :param t: 初始速度
    :return: 小段的距离集合
    """
    tracks = []
    # 加速减速的临界值
    mid = rate * distance
    # 当前位移
    s = 0
    # 循环
    while s < distance:
        # 初始速度
        v0 = v
        if s < mid:
            a = 20
        else:
            a = -3
        # 计算当前t时间段走的距离
        s0 = v0 * t + 0.5 * a * t * t
        # 计算当前速度
        v = v0 + a * t
        # 四舍五入距离，因为像素没有小数
        tracks.append(round(s0))
        # 计算当前距离
        s += s0
    return tracks


def get_did():
    print("开始获取did...")
    check_url = 'https://www.kuaishou.com/search/author?searchKey=aaa'
    driver_path = r'../driver/chromedriver'
    option = webdriver.ChromeOptions()
    # option.add_argument('--headless')
    option.add_argument('--disable-gpu')  # 不需要GPU加速
    option.add_argument('--no-sandbox')  # 无沙箱
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument("disable-blink-features")
    option.add_argument("disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=option, executable_path=driver_path)
    driver.get(check_url)
    for i in range(4):
        driver.refresh()
        time.sleep(1)
    time.sleep(1)

    while True:
        try:
            driver.switch_to.frame(driver.find_element(by=By.XPATH, value='/html/body/div[2]/iframe'))
            break
        except NoSuchElementException:
            driver.refresh()
            time.sleep(1)
            continue
    # bg_url = driver.find_element_by_class_name('bg-img').get_attribute('src')
    # fg_url = driver.find_element_by_class_name('slider-img').get_attribute('src')
    # distance = get_distance(fg_url, bg_url)
    # print(distance)
    # slider = driver.find_element_by_class_name('slider-shadow')
    # ActionChains(driver).click_and_hold(slider).perform()
    # ActionChains(driver).move_by_offset(distance - 20, 0).perform()
    # for i in get_tracks(distance - 10):
    #     ActionChains(driver).move_by_offset(i, 0).perform()
    # ActionChains(driver).release().perform()
    time.sleep(10)
    driver.refresh()
    did = driver.get_cookies()[0]['value']
    # driver.close()
    # driver.quit()
    # return did


print(get_did())
