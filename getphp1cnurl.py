# -*- coding: utf-8 -*-

import time
import requests
import re
from lxml import etree
from public.mysqlpooldao import MysqlDao
from public.headers import Headers


def get_category():
    mysql_dao = MysqlDao()
    sql = 'select `id`,`url` from  it_category'
    res = mysql_dao.execute(sql)
    return res


def get_url(cates):
    for cate in cates:
        print(cate)
        cate_id = cate[0]
        cate_url = cate[1]
        headers = Headers.get_headers()
        try:
            req = requests.get(cate_url, headers=headers, timeout=10)
            if req.status_code == 200:
                html = req.content
                selector = etree.HTML(html)
                last_pages = selector.xpath('//div[@class="ListPageNum"]/ul/li[last()]/a/@href')
                if len(last_pages) > 0:
                    last_page = last_pages[0]
                    match_obj = re.match(r'http://www.php1.cn/category/(.*?)/(.*?).html', last_page, re.M | re.I)
                    # print "matchObj.group() : ", match_obj.group()
                    # print "matchObj.group(1) : ", match_obj.group(1)
                    # print "matchObj.group(2) : ", match_obj.group(2)
                    page_num = int(match_obj.group(2))
                    mysql_dao = MysqlDao()
                    while True:
                        if page_num <= 0:
                            break
                        list_url = 'http://www.php1.cn/category/%s/%s.html' % (cate_id, page_num)
                        headers = Headers.get_headers()
                        try:
                            print(list_url)
                            req = requests.get(list_url, headers=headers, timeout=10)
                            if req.status_code == 200:
                                html = req.content
                                selector = etree.HTML(html)
                                urls = selector.xpath('//ul[@class="NewsList"]/li/div[@class="NewTitle"]/h2/a/@href')
                                for url in urls:
                                    sql = 'insert ignore into it_url(`url`,`cate`,`type`) VALUES ("%s",%s,0)' % (
                                        url, cate_id)
                                    mysql_dao.execute(sql)
                        except:
                            print(list_url, 'timeout')
                        page_num = page_num - 1
        except:
            print(cate_url, 'timeout')


if __name__ == '__main__':
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    print(u'开始获取分类url...')
    cates = get_category()
    print(u'获取分类url完成...')
    print(u'开始获取分类下文章url...')
    get_url(cates)
    print(u'获取完成...')
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
