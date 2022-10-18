# coding=utf-8
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from fastapi import FastAPI
import requests
import json
import re

from lxml import html

from app.schemas import Url

app = FastAPI()


@app.post("/api")
async def api(urlstr: Url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'
    }
    cruises = []
    base_url = urlstr.base_url
    response = requests.request("GET", base_url, headers=headers)
    tree = html.fromstring(response.text)
    cruis_group = tree.xpath('//div[@class="c"]/div[@class="p"]')
    for cruis in cruis_group:
        cr = cruis.xpath('./@data-ecom-impressions-obj')[0]
        if len(cr) > 0:
            cr = re.sub('\t*\n*\r*', '', cr)
            cr = cr.replace('"', r'\"')
            cr = cr.replace("'", '"')
            cr = json.loads(cr)
        else:
            cr = ''

        stops = cruis.xpath('.//div[@class="p__stops"]/span/text()')
        stops = ' '.join([str(stops[0]), ', '.join(stops[1:len(stops)])])
        cr['stops'] = stops

        cr_date = cruis.xpath('.//div[@class = "p__info"]//span/text()')
        date = str(cr_date[0])
        days = str(cr_date[1])
        cr['date'] = date
        cr['days'] = days

        icons = cruis.xpath('.//div[@class = "p__icons"]//img/@title')
        icons = '###'.join(icons)
        cr['icons'] = icons

        price = cruis.xpath('.//meta[@itemprop = "price"]/@content')
        if len(price) > 0:
            price = str(price[0])
        else:
            price = ''
        cr['price'] = price

        currency = cruis.xpath('.//meta[@itemprop = "priceCurrency"]/@content')
        if len(currency) > 0:
            currency = str(currency[0])
        else:
            currency = ''
        cr['priceCurrency'] = currency

        descr = cruis.xpath('./meta[@itemprop = "description"]/@content')
        if len(descr) > 0:
            descr = str(descr[0])
        else:
            descr = ''
        cr['descr'] = descr

        img = cruis.xpath('./a/meta[@itemprop="image"]/@content')
        if len(img) > 0:
            img = str(img[0])
        else:
            img = ''
        cr['img'] = img

        tags = []
        tags_list = cruis.xpath('./a/div[@class="tags"]/div[not(@class = "tags__item tags__item--lvl tags__item--t")]/text()')
        for t in tags_list:
            tag = re.sub('\t*\n*\r*', '', t)
            tag = tag.strip()
            tags.append(tag)
        cr['tags'] = tags
        cruises.append(cr)

    return {"cruises": cruises}
