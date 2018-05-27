import os

import re

os.chdir('D:\\pyrojects\\bijia')

import requests
import json

from scrapy import Selector
from urllib.parse import unquote
import time
import requests_cache

requests_cache.install_cache('demo_cache')
from model import *
from tomorrow import threads


def get_proxy():
    try:
        with requests_cache.disabled():
            ct = requests.get("http://127.0.0.1:5010/get/").content
            return ct
    except Exception as e:
        print("代理失效")
        return b"no proxy!"


user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
headers = {'User-Agent': user_agent}


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def getHtml(u, proxy, isdisable=False):
    html = None
    retry_count = 1
    if not proxy == 'no proxy!':
        while retry_count > 0:
            try:
                if isdisable:
                    with requests_cache.disabled():
                        print("代理 ：" + proxy.decode("utf8"))
                        html = requests.get(u, timeout=1)
                        # 使用代理访问
                        # print(html.text)
                        return html
                else:
                    print("代理 ：" + proxy.decode("utf8"))
                    html = requests.get(u, proxies={"http": "http://{}".format(proxy.decode("utf8"))}, timeout=1)
                    # 使用代理访问
                    # print(html.text)
                    return html
            except Exception as e:
                retry_count -= 1
                print(e)

        # 出错5次, 删除代理池中代理
        delete_proxy(proxy.decode("utf8"))

    # 使用本机ip尝试获取
    try:
        html = requests.get(u, headers=headers)

        # 使用代理访问
        # print(html.text)
        return html
    except Exception as e:
        print(e)

    return None


def get_east8_date_str(format_long=True):
    """
    获取东八区的当前时间：上海时间
    :param format_long: 是否是长格式：默认是长格式 2017-05-08 03:32:49  ，短格式：2017-05-08
    :return: 字符串格式的日期时间
    """
    dt = datetime.utcnow()
    dt = dt.replace(tzinfo=timezone.utc)
    if format_long:
        return dt.astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt.astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")


# @threads(10)
def dodetail(product_id):
    print(product_id)

    for page in range(1, 100):

        comment_url = 'https://club.jd.com/comment/productPageComments.action?productId=%s&score=0&sortType=5&page=%s' \
                      '&pageSize=100'
        url = comment_url % (product_id, page)

        response2 = getHtml(url, get_proxy())

        print('-'*90)
        print(url)
        print(response2.content)
        print('-'*90)

        data = json.loads(response2.text)

        print(data)

        comments = data["comments"]

        for comment in comments:

            print('-' * 100)
            content = comment['content']
            score = comment['score']
            print((product_id, content, score))
            print('-' * 100)
            try:

                if not sessionDb.query(ma_comment).filter_by(product_id=product_id, content=content).count():
                    print("插入数据------------------")
                    its = ma_comment(
                        product_id=product_id,
                        content=content,
                        score=score
                    )
                    sessionDb.add(its)
                    sessionDb.commit()
                    print("插入成功")

                else:
                    print("数据重复")
            except Exception as e:
                sessionDb.rollback()
                print(e)


for m in sessionDb.query(ma_myitems1).all():
    print(m.product_id)

    # try:
    dodetail(m.product_id)
    # except Exception as e:
    #     print(e)
    #     print("%" * 30)
