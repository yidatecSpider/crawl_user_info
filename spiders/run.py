import requests
import execjs

from spiders.get_cookie import get_cookies


class Sign(object):
    def __init__(self):
        self.cookies = get_cookies()

    def dy_sign(self, method, kw=None):
        with open('../js/signature.js', 'r', encoding='utf-8') as f:
            b = f.read()
        c = execjs.compile(b)
        d = c.call(method, kw)
        # cookies = get_cookies()
        # cookies = 'MONITOR_DEVICE_ID=60aa3dd7-10fd-4fca-bea9-d6e27935f594; _tea_utm_cache_2018=undefined; s_v_web_id=verify_4fecdf9365645b7817e8590e6bf279a7; MONITOR_WEB_ID=a9461edd-7d88-46d1-bd06-97726c189495; __ac_referer=__ac_blank;'
        headers = {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.douyin.com/",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "cookie": self.cookies
        }
        e = requests.get(d, headers=headers)
        if not e.text:
            self.cookies = get_cookies()
            return self.dy_sign(method, kw)
        else:
            return e.text


if __name__ == '__main__':
    sign = Sign()
    # 首页推荐视频
    # print(dy_sign(method='feed'))
    # 搜索视频
    # print(dy_sign(method='search_item', kw='冬奥会'))
    # 搜索用户
    # print(dy_sign(method='search_user', kw='冬奥会'))
    # 评论
    # print(dy_sign(method='cooment',kw='6989198974582263070'))
    # 作品
    print(sign.dy_sign(method='aweme_post', kw='MS4wLjABAAAA7Z64D-3Mlj3pwzQIKDFvEfVG_Bj9DhZX4HUSKjWzzOs'))
    # TODO 其他的自行补充吧
    ...
