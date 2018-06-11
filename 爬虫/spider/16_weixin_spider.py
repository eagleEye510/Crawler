import Configs
import gevent
from lxml import etree
import time
from Config_v2 import Config as Config_v2
import json


''' 
'''


class WeiXinSpider(object):
    def __init__(self):
        self.base_url = "http://weixin.sogou.com/weixin?type=2&ie=utf8&query=%s"
        self.user_agent = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
        }

    def parse_detail(self, url, key_word):
        # 去重判断（筛选法）
        flag_sub = url[73: 94]
        added = Configs.ToolsObjManager.redis_tool.sadd_value("we_chat", flag_sub)
        if not added:
            return
        html = Configs.ToolsObjManager.extract_tool.sougou_get_html(url)[0]
        xhtml = etree.HTML(html)
        title = xhtml.xpath("//*[@id='activity-name']/text()")
        title = title[0].strip()
        create_time_str = xhtml.xpath("//*[@id='post-date']/text()")[0]
        main_article = xhtml.xpath("//*[@id='js_content']//p")
        pub_code = xhtml.xpath('//*[@id="js_profile_qrcode"]/div/p[1]/span/text()')

        article = []
        for item in main_article:
            paragraph = item.xpath('string()').strip()
            if paragraph:
                article.append(paragraph)
        md5 = Configs.ToolsObjManager.general_tool.article2md5(article)
        refer_item = Configs.MongoConfigs.db_web.web_data.find_one({'article_md5': md5})
        if refer_item:
            return
            refer_article_id = refer_item['_id']
            article = []

        else:
            refer_article_id = ''
        # url = "http://111.207.68.147:5021/wechat?pub_code=%s&title=%s" % (pub_code[0], title)
        if not pub_code:
            pub_code = ['']
        data = {
            "pub_code": pub_code[0],
            "title": title
        }
        url = "wechat" + json.dumps(data)
        shrink_url = Configs.ToolsObjManager.str_tool.shrink_url(url)
        # 插入到193的MySQL中
        Config_v2.ToolObj.mysql_tool.insert_html_map(shrink_url, html)
        Configs.MongoConfigs.col_data.insert_one({
            'url': shrink_url,
            'title': title,
            'pub_code': pub_code[0],
            'crawling_time': str(int(time.time()*1000)),
            'create_time': str(int(1000*Configs.ToolsObjManager.extract_tool.convert_day2timestamp(create_time_str))),
            'source_spider': '搜狗微信搜索',
            'key_word': key_word,
            'article': article,
            'article_md5': md5,
            'refer_article_id': refer_article_id,
        })

    def parse_list_page(self, url, key_word):
        html = Configs.ToolsObjManager.extract_tool.sougou_get_html(url)[0]
        xhtml = etree.HTML(html)
        son_hrefs = xhtml.xpath('//h3//a/@href')
        for href in son_hrefs:
            self.parse_detail(href, key_word)
            # try:
            #     self.parse_detail(href, key_word)
            # except:
            #     pass

    def search(self, key_word):
        url_with_key = self.base_url % key_word
        for i in range(1, 2):
            item_pg_url = url_with_key + "&page=%s" % i
            self.parse_list_page(item_pg_url, key_word)
            # try:
            #     self.parse_list_page(item_pg_url, key_word)
            # except:
            #     pass


if __name__ == '__main__':
    weixin_spider = WeiXinSpider()
    keywords = Configs.ToolsObjManager.searchspider_tools.get_key_word()
    # keywords = ["windows"]
    # url = 'https://mp.weixin.qq.com/s?src=11&timestamp=1520296945&ver=737&signature=QRJHGseikuSTfUGEu8FS-QDNoyz116ZisfWU*aZ8Curgs35ikSZggbgfV9-Eqar-RB3gWDlx87pG4uEldgoFWifju5eDPjWbjnNUallDmC3oLHrA4OHUe2YYu59PJaQX&new=1'
    # weixin_spider.parse_detail(url, '')
    g_list = []
    for keyword in keywords:
        keyword = ' '.join(keyword).strip()
        # weibo_spider.search(keyword)
        if keyword:
            # 加入到公众号缓存
            cache = Config_v2.ToolObj.mongo_cfg.db_wechat.pub_count_cache.find_one({
                'keyword': keyword
            })

            g_list.append(gevent.spawn(weixin_spider.search, keyword))
    gevent.joinall(g_list)
