import os
from multiprocessing.pool import Pool
import requests
from urllib.parse import urlencode
from hashlib import md5
import re

GROUP_START = 1
GROUP_END = 20

URL = "https://www.toutiao.com/search_content/?"

def get_page(offset):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
        "cookie": "csrftoken=2863caf55551dc02df0e73fe0825c8c5; tt_webid=6818413566569367053; s_v_web_id=verify_k9axrexf_8FT1z4KG_JO0n_4BlJ_AUXn_9Mwmjn1JObyM; ttcid=01def0dbb1d2427f8fab235ff4c5b34785; SLARDAR_WEB_ID=b6008e63-0fd5-437d-a4d7-9121829e3f0a; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6818413566569367053; __tasessionId=r71cddt0d1587542430798; tt_scid=89cvvXIl7SiyAgniwo0DKwuUE8cknzf0SMcYnooqArvdM6LenCHE7xpEptWxWPSR715a",
        "x-requested-with": "XMLHttpRequest",
        'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    }
    params = {
        "aid":'24',
        "app_name":'web_search',
        "offset": offset,
        "format": "json",
        "keyword": "街拍",
        "autoload": "true",
        "count": 20,
        "cur_tab": 1,
        "from": "search_tab",
        "pd":'synthesis',
    }
   
    url = URL + urlencode(params)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None

def get_images(json):
    if json.get('data'): 
        for item in json.get('data'):
            if item.get('title') is None:
                continue
            title = re.sub('[\t]', '', item.get('title'))
            images = item.get('image_list')
            if images:
                for image in images:
                    origin_image = re.sub("list.*?pgc-image", "large/pgc-image", image.get('url'))
                    yield {
                        'image':origin_image,
                        'title':title
                    }

def save_image(item):
    img_path = 'img' + os.path.sep + item.get('title')
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    try:
        resp = requests.get('https:'+item.get('image').replace('list', 'large'))
        if resp.status_code == 200:
            file_path = img_path + os.path.sep + '{file_name}.{file_suffix}'.format(
                file_name=md5(resp.content).hexdigest(),
                file_suffix='jpg' 
            )
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(resp.content)
                print('Downloaded image path is %s' % file_path)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to Save Image, item %s' % item)


def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)


if __name__=='__main__':
    pool = Pool()
    groups = [x*20 for x in range(GROUP_START,GROUP_END+1)]
    pool.map(main, groups)
    pool.close()
    pool.join()

