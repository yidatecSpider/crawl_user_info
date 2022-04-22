import random
from time import sleep

import requests
import json

requests.packages.urllib3.disable_warnings()

did = [
    # 'web_548fc678bf8c2b3ee7b6d4a661746c82',
    # 'web_8e3b9cee6ad044c04ce4f0c4cbaf8197',
    'web_f32bb951ef9a49cd7314bdf2df558e79'
]


def get_user_page_url(user_id, retries=0):
    if retries >= 4:
        pass
    url = "https://www.kuaishou.com/graphql"

    payload = json.dumps({
        "operationName": "graphqlSearchUser",
        "variables": {
            "keyword": str(user_id)
        },
        "query": "query graphqlSearchUser($keyword: String, $pcursor: String, $searchSessionId: String) {\n  visionSearchUser(keyword: $keyword, pcursor: $pcursor, searchSessionId: $searchSessionId) {\n    result\n    users {\n      fansCount\n      photoCount\n      isFollowing\n      user_id\n      headurl\n      user_text\n      user_name\n      verified\n      verifiedDetail {\n        description\n        iconType\n        newVerified\n        musicCompany\n        type\n        __typename\n      }\n      __typename\n    }\n    searchSessionId\n    pcursor\n    __typename\n  }\n}\n"
    })
    headers = {
        # 'Host': 'www.kuaishou.com',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'accept': '*/*',
        'content-type': 'application/json',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'Origin': 'https://www.kuaishou.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.kuaishou.com/search/video?searchKey=%E8%B5%B5%E5%9B%9B',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': f'kpf=PC_WEB; kpn=KUAISHOU_VISION; clientid=3; did={random.choice(did)}; didv=1647788114096; client_key=65890b29; ktrace-context=1|MS43NjQ1ODM2OTgyODY2OTgyLjE5NzE3MzU1LjE2NTAyOTE2MTY5NzQuMjQ2OTcxNA==|MS43NjQ1ODM2OTgyODY2OTgyLjc3ODc5ODYxLjE2NTAyOTE2MTY5NzQuMjQ2OTcxNQ==|0|graphql-server|webservice|false|NA'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    data = json.loads(response.content)
    try:
        user_page_url = f"https://www.kuaishou.com/profile/{data.get('data').get('visionSearchUser').get('users')[0].get('user_id')}"
    except AttributeError:
        print("接口反爬,等待恢复")
        sleep(1)
        return get_user_page_url(user_id, retries + 1)
    except (IndexError, TypeError):
        print("数据异常")
        sleep(1)
        return get_user_page_url(user_id, retries + 1)
    return user_page_url


if __name__ == '__main__':
    users = [7997704,
             850900304,
             2365249937,
             1342130938,
             1768005190,
             23624634,
             1792453648,
             1306178589,
             2433265038,
             2753912023,
             318491199,
             318491199,
             418691249,
             1081405067,
             1001575607,
             1668535,
             1554806132,
             5064471,
             2075472862,
             773791121,
             1467228603,
             1467228603,
             2090144388,
             1467228603,
             2123503682,
             121147832,
             1174902160
             ]
    [get_user_page_url(user_id) for user_id in users]
