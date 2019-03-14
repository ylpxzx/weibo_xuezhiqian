from urllib.parse import urlencode
import urllib
import requests
from pyquery import PyQuery as pq
import time
from pymongo import MongoClient

base_url='https://m.weibo.cn/api/container/getIndex?'

headers={
    'Referer':'https://m.weibo.cn/u/1239246050',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest',
}


client=MongoClient()
db=client['weibo']
collection=db['weibo_xuezhiqian']

def get_page(page):
    params={
        'uid':'1239246050',
        'luicode':'10000011',
        'lfid':'100103type=1&q=薛之谦',
        'type':'uid',
        'value':'1239246050',
        'containerid':'1076031239246050',
        'page':page
    }
    url=base_url+urlencode(params)
    try:
        response=requests.get(url,headers=headers)
        if response.status_code==200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error',e.args)
def parse_page(json,page):
    if json:
        items = json.get('data').get('cards')
        for index, item in enumerate(items):
            if page == 1 and index == 1:
                continue
            else:
                item = item.get('mblog', {})
                weibo = {}
                weibo['id'] = item.get('id')
                weibo['text'] = pq(item.get('text')).text()
                weibo['attitudes'] = item.get('attitudes_count')
                weibo['comments'] = item.get('comments_count')
                weibo['reposts'] = item.get('reposts_count')
                weibo['create_time']=item.get('created_at')
                if item.get('bmiddle_pic'):
                    weibo['photo']=item.get('bmiddle_pic')
                time.sleep(2)
                yield weibo

def save_to_mongo(result):
    if collection.insert(result):
        print('Saved to Mongo!')

if __name__=='__main__':
    for page in range(1,60):
        json=get_page(page)
        results=parse_page(json,page)
        for result in results:
            print(result)
            save_to_mongo(result)
