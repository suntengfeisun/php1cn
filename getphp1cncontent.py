# -*- coding: utf-8 -*-

import time
import requests
from lxml import etree
from public.mysqlpooldao import MysqlDao
from public.headers import Headers


def get_content():
    mysql_dao = MysqlDao()
    while True:
        sql = 'select `url`,`cate` FROM it_url WHERE `type`=0 limit 10'
        res = mysql_dao.execute(sql)
        if len(res) == 0:
            break
        if len(res) > 0:
            res = res[0]
            url = res[0]
            cate = res[1]
            # url = 'http://www.php1.cn/Content/WanShan_DEDECMS_ZhongDeTuPianBenHuaGongNeng.html'
            sql = 'update it_url SET `type`=2 WHERE `url`="%s"' % url
            try:
                mysql_dao.execute(sql)
            except:
                mysql_dao = MysqlDao()
            headers = Headers.get_headers()
            print(url)
            try:
                req = requests.get(url, headers=headers)
            except:
                time.sleep(600)
                req = requests.get(url, headers=headers)
            if req.status_code == 200:
                html = req.content
                selector = etree.HTML(html)
                titles = selector.xpath('//div[@class="article_box"]/h1[1]/text()')
                contents = selector.xpath('//div[@class="article_content"]/descendant::text()')
                contents.pop()
                contents.pop()
                if len(titles) > 0 and len(contents) > 0:
                    title = titles[0]
                    content = ''
                    for c in contents:
                        content = content + '{ycontent}' + c.replace('"', '').replace('\'', '')
                    sql = 'insert ignore into it_content (`title`,`content`,`category_id`) VALUES ("%s","%s","%s")' % (
                        title, content, cate)
                    try:
                        mysql_dao.execute(sql)
                    except:
                        mysql_dao = MysqlDao()
            sql = 'update it_url SET `type`=1 WHERE `url`="%s"' % url
            try:
                mysql_dao.execute(sql)
            except:
                mysql_dao = MysqlDao()


if __name__ == '__main__':
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    print(u'开始获取分类下文章内容...')
    get_content()
    print(u'获取完成...')
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
