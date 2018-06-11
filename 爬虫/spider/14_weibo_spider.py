import json
from lxml import etree
import Configs
import re
import time
import datetime
import gevent


class WeiboSpider(object):
    def __init__(self):

        self.unit_multi = {
            '分钟前': 60,
            '小时前': 60*60,
            '天前': 24*60*60
        }
        self.unit_before_pattern = re.compile('(\d*)(.*?前)')
        self.date_form_pattern = re.compile('\d*-\d*')
        self.year_form_pattern = re.compile('\d{4}-\d*-\d*')

    def covert_str2time(self, time_str, current_time_int):
        time_str = time_str.strip()
        if time_str.startswith('刚刚'):
            return current_time_int
        if time_str.startswith('昨天'):
            return current_time_int-24*60*60
        before = self.unit_before_pattern.search(time_str)
        if before:
            return current_time_int-int(before.group(1))*self.unit_multi[before.group(2)]
        year_pattern = self.year_form_pattern.search(time_str)
        if year_pattern:
            date_form = "%s 00:00:01" % year_pattern.group(0)
            timeArray = time.strptime(date_form, "%Y-%m-%d %H:%M:%S")
            return time.mktime(timeArray)
        date_form = self.date_form_pattern.search(time_str)

        if date_form:
            date_form = "%s-%s 00:00:01" % (datetime.datetime.now().year, date_form.group(0))
            timeArray = time.strptime(date_form, "%Y-%m-%d %H:%M:%S")
            return time.mktime(timeArray)

    def search_item_page(self, key_word, page):
        pg_kw_url = 'http://m.weibo.cn/api/container/getIndex?containerid=100103type%3D60%26q=' + key_word + '&page=%s' % page
        html = Configs.ToolsObjManager.extract_tool.extract_html(pg_kw_url)[0]
        res = json.loads(html)
        self.parse_dict(res, key_word)

    def search(self, key_word):
        for page in range(1, 20):
            self.search_item_page(key_word, page)
            try:
                pass
            except Exception as e:
                print(e)

    def parse_dict(self, row, key_word):
        l = row['data']['cards']
        crawling_time_int = time.time()
        for i in l[0]['card_group']:
            data = i['mblog']
            article_id = data['id']
            ori_url = "https://m.weibo.cn/status/%s" % article_id
            added = Configs.ToolsObjManager.redis_tool.sadd_value(
                Configs.Configs.redis_key_general_spider, ori_url)
            if added:
                xhtml = etree.HTML(data['text'])
                temp_text = xhtml.xpath('string(.)')
                time_str = data['created_at']
                # print(temp_text)
                timestamp = self.covert_str2time(time_str, crawling_time_int)
                create_time = str(int(timestamp*1000))
                crawling_time = str(int(crawling_time_int*1000))
                # hrefs = xhtml.xpath('//a')
                # for i in hrefs:
                #     href = i.xpath('text()')
                #     if href:
                #         if href[0].find('全文') >= 0:
                #             html = Configs.ToolsObjManager.extract_tool.extract_html(ori_url)[0]
                #             with open('weibo.html', 'w') as f:
                #                 f.write(html)
                #             xhtml = etree.HTML(html)
                #             temp_text = xhtml.xpath("//div[@class='weibo-text']/text()")
                #             break
                Configs.MongoConfigs.col_data.insert_one({
                    'original_url': ori_url,
                    'title': '',
                    'article': [temp_text],
                    'crawling_time': crawling_time,
                    'create_time': create_time,
                    'url': ori_url,
                    'refer_article_id': '',
                    'source_spider': '微博搜索',
                    'key_word': key_word
                })
                print("success...." + ori_url)


if __name__ == '__main__':
    weibo_spider = WeiboSpider()
    span_list = []
    keywords = Configs.ToolsObjManager.searchspider_tools.get_key_word()
    for keyword in keywords:
        keyword = ' '.join(keyword).strip()
        print(keyword)
        print(type(keyword))
        span_list.append(gevent.spawn(weibo_spider.search, keyword))
    gevent.joinall(span_list)
