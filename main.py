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


def getHtml(u, proxy):
    html = None
    retry_count = 2
    if not proxy == 'no proxy!':
        while retry_count > 0:
            try:
                print("代理 ：" + proxy.decode("utf8"))
                html = requests.get(u, proxies={"http": "http://{}".format(proxy.decode("utf8"))}, timeout=2)
                return html
            except Exception as e:
                retry_count -= 1
                print(e)
        delete_proxy(proxy.decode("utf8"))

    try:
        html = requests.get(u, headers=headers)
        return html
    except Exception as e:
        print(e)
    return None


def dodetail(url, categorie):
    print(url)
    r3 = getHtml(url, get_proxy())

    ids = re.findall(r"venderId:(.*?),\s.*?shopId:'(.*?)'", r3.text)
    if not ids:
        ids = re.findall(r"venderId:(.*?),\s.*?shopId:(.*?),", r3.text)

    vender_id = ids[0][0]
    shop_id = ids[0][1]

    response = Selector(r3)

    itemurl = r3.url

    name = ''
    if shop_id == '0':
        name = '京东自营'
    else:
        try:
            name = response.xpath('//ul[@class="parameter2 p-parameter-list"]/li/a//text()').extract()[0]
        except:
            try:
                name = response.xpath('//div[@class="name"]/a//text()').extract()[0].strip()
            except:
                try:
                    name = response.xpath('//div[@class="shopName"]/strong/span/a//text()').extract()[0].strip()
                except:
                    try:
                        name = response.xpath('//div[@class="seller-infor"]/a//text()').extract()[0].strip()
                    except:
                        name = u'京东自营'

    try:
        title = response.xpath('//div[@class="sku-name"]/text()').extract()[0].replace(u"\xa0", "").strip()
    except Exception as e:
        title = response.xpath('//div[@id="name"]/h1/text()').extract()[0]

    product_id = r3.url.split('/')[-1][:-5]

    desc = response.xpath('//ul[@class="parameter2 p-parameter-list"]//text()').extract()
    desc2 = ';'.join([i.strip() for i in desc])

    price_url = 'https://p.3.cn/prices/mgets?skuIds=J_'

    response = getHtml(price_url + product_id, get_proxy())
    price_json = response.json()
    reallyPrice = price_json[0]['p']
    originalPrice = price_json[0]['m']
    comment_url = 'https://club.jd.com/comment/productPageComments.action?productId=%s&score=0&sortType=5&page=%s&pageSize=10'
    url = comment_url % (product_id, 1)

    response2 = getHtml(url, get_proxy())

    data = json.loads(response2.text)

    commentcount = data["productCommentSummary"]["commentCount"]

    print((name, title, product_id, itemurl, reallyPrice, originalPrice, url, commentcount, desc2))

    # 入库
    print(desc2)
    print(len(desc2))

    try:

        its = ma_myitems1(shopname=name,
                          title=title,
                          product_id=product_id,
                          itemurl=itemurl,
                          reallyPrice=reallyPrice,
                          originalPrice=originalPrice,
                          url=url,
                          commentcount=commentcount,
                          desc2=desc2,
                          shop_id=shop_id,
                          categorie=categorie)

        sessionDb.add(its)
        sessionDb.commit()
    except Exception as e:
        sessionDb.rollback()
        print(e)


response3 = requests.get('https://www.jd.com/allSort.aspx')

selector = Selector(response3)

categories = []

texts = selector.xpath('//div[@class="category-item m"]/div[@class="mc"]/div[@class="items"]/dl/dd/a').extract()
for text in texts:
    items = re.findall(r'<a href="(.*?)" target="_blank">(.*?)</a>', text)
    for item in items:
        #         print(item)
        if 'cat=1713' in item[0]:
            print(item)
            categories.append(item)

for categorie in categories:
    print(categorie[1])

    # 分页 &page=3&sort=sort_totalsales15_desc&trans=1&JL=6_0_0#J_main

    for rg in range(1, 100):

        url = 'https:' + categorie[0] + "&page={0}&sort=sort_totalsales15_desc&trans=1&JL=6_0_0#J_main".format(rg)
        print(url)

        r1 = requests.get(url)
        selector = Selector(r1)
        texts = selector.xpath('//*[@id="plist"]/ul/li/div/div[@class="p-img"]/a').extract()

        for text in texts:

            items2 = re.findall(r'<a target="_blank" href="(.*?)">', text)

            try:

                dodetail('http:' + items2[0], categorie[1])
            except  Exception as e:
                print(e)
                print("-" * 80)


