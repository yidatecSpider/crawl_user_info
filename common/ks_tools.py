
import random
import ctypes
import requests
import hashlib
from urllib.parse import unquote

def get_web_did():
    d = ''
    n = 0
    while n < 32:
        n+=1
        d += hex(int(16 * random.random()))[2:]
    did = 'web_' + d
    print(did)
    return did

def str_to_map(str):
    '''url的参数转为字典'''
    map = {}
    str_list = str.split('&')
    for data in str_list:
        item = data.split('=')
        map[item[0]] = item[1]
    return map

def map_sort_salt(map1,map2,salt = '382700b563f4'):
    '''把url参数和formdata参数排序，加盐，返回字符串'''
    map = dict(map1,**map2)
    aps = sorted(map.items(), key = lambda d: d[0])
    data = {}
    for i in aps:
        if i[0] == 'sig' or i[0] == '__NS_sig3' or i[0] == '__NStokensig':
            pass
        else:
            data.update(dict({i[0]:i[1]}))
    url_str = ""
    for key,value in data.items():
        str = key + '=' + unquote(value)
        url_str += str
    return url_str + salt

def data_md5(content):
    m = hashlib.md5()
    m.update(content.encode("utf-8"))
    return m.hexdigest()

def get_sign(query_str,post_arr):
    url_arr = str_to_map(query_str)
    str = map_sort_salt(url_arr, post_arr)
    return data_md5(str)

def int_overflow(val):
    maxint = 2147483647
    if not -maxint-1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val

def int_move(n, i):
    '''实现无符号右移动(>>>),n:要移动的数字，i:移动的位数'''
    # 数字小于0，则转为32位无符号uint
    if n<0:
        n = ctypes.c_uint32(n).value
    # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
    if i<0:
        return -int_overflow(n << abs(i))
    #print(n)
    return int_overflow(n >> i)

def get_tokensig(sig='b6eb03bead56bf591cca596af3899cbe', api_client_salt='956b02b563cc2333e135e29b4f2a32c5'):
    # api_client_salt是登录时抓包返回的值，该值只在登录时才会返回
    tokenSin = sig + api_client_salt
    tokenSin_b = tokenSin.encode('UTF-8')

    s256 = hashlib.sha256()
    s256.update(tokenSin_b)
    bArr = s256.digest()

    cArr = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    length = len(bArr)
    # print(length)
    cArr2 =  [''] * 64
    i1, i2 = 0, 0
    while i2 < length:
        i3 = i1 + 1
        cArr2[i1] = cArr[int_move((bArr[i2] & 240), 4)]
        i1 = i3 + 1
        cArr2[i3] = cArr[bArr[i2] & 15]
        i2 += 1
    tokenSin = ''.join(cArr2)
    # print(tokenSin)
    return tokenSin


def post_resp(user_id,did='132557A7-C0CA-422D-991F-A02437C1F6F0'):

    # 推荐流
    url = 'http://api.ksapisrv.com/rest/n/feed/hot?'
    url_str = f'isp=CTCC&pm_tag=&mod=Meizu%28m3%20note%29&lon=113.968423&country_code=cn&kpf=ANDROID_PHONE&did={did}&kpn=KUAISHOU&net=WIFI&app=0&oc=MEIZU&ud=0&hotfix_ver=&c=MEIZU&sys=ANDROID_7.0&appver=6.3.3.8915&ftt=&language=zh-cn&iuid=&lat=22.583945&did_gt=1556199685379&ver=6.3&max_memory=256&type=7&page=1&coldStart=false&count=20&pv=false&id=25&refreshTimes=2&pcursor=&source=1&needInterestTag=false&browseType=1&client_key=3c2cd3f3&os=android'
    # 个人主页
    url = 'http://api.gifshow.com/rest/n/user/profile/v2?'
    url_str = f'isp=CMCC&mod=nubia%28NX511J%29&lon=116.375547&country_code=cn&kpf=ANDROID_PHONE&did={did}&kpn=KUAISHOU&net=WIFI&app=0&oc=XB_GIONE&hotfix_ver=&c=XB_GIONE&sys=ANDROID_5.1.1&appver=6.8.0.10654&ftt=&language=zh-cn&iuid=&lat=40.094897&ver=6.8&max_memory=192'

    # 添加登录token
    token = ''
    api_client_salt = ''
    param = {
        'user': str(user_id),
        'pv':'true',
        'client_key':'3c2cd3f3',
        'os':'android',
        'token': token
    }
    sign = get_sign(url_str,param)
    __NStokensig = get_tokensig(sign, api_client_salt)
    url = url + url_str
    param.update({'__NStokensig': __NStokensig, 'sig': sign})
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'kwai-android',
        'Accept-Encoding': 'gzip',
    }

    resp = requests.post(url, headers=headers, data=param, verify=False)
    return resp

if __name__ == '__main__':

    # 操作太快是did失效，签名失败是tokne和api_client_salt没有传
    print(post_resp(1320640507).text)





