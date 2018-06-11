from lxml import etree
import time
from 爬虫.spider.Configs import Configs
import re
import gevent
import sys
import io
from 爬虫.spider.Config_v2 import Config as ConfigV2


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
'''
{"FlightWay":"S","SegmentList":[{"DCityCode":"TYO","ACityCode":"NYC","DCity":"Tokyo|东京(TYO)|228|TYO|540","ACity":"New York|纽约(NYC)|633|NYC|-240","DepartDate":"2018-5-11","DCityName":"东京","ACityName":"纽约"}],"TransferCityID":0,"Quantity":1,"ClassGrade":"Y","TransNo":"2cba41de6dae45718b446d48b43cf3d9","SearchRandomKey":"","AirportCityBusSwitch":false,"RecommendedFlightSwitch":1,"EngineFlightSwitch":1,"SearchKey":"07F691B499AFAA497550538E2A92D855A921D5D617B7813D641DF6A6025C9B8ABAF56A4A2DE1F6E1","MultiPriceUnitSwitch":1,"TransferCitySwitch":false,"EngineScoreABTest":"A","SearchStrategySwitch":1,"MaxSearchCount":3,"TicketRemarkSwitch":1,"RowNum":"1500","TicketRemarkChannels":["GDS-WS","ZY-WS"],"AddSearchLogOneByOne":true,"TFAirlineQTE":"AA","IsWifiPackage":0,"SegmentVerifySwitch":false,"ComparePriceByAttributeSwitch":true,"IsOpenCFNoDirectRecommendYS":false,"IsDomesticIntlPUVersionSwitch":true,"DisplayBaggageSizeSwitch":true,"IsOpen24Refund":true,"IsOpenTransPU":true,"IsOpenVirtualFlight":true,"IsOpenNew3X":false,"NewAirlineLogoSwitch":false,"NewAirlineLogoSortTopSwitch":false,"IsNewImpower":false,"FromJavaVersion":false,"IsLowPrice":false,"OpenJawCitySequence":0}
'''


'''
1. 来源站点   
    泛化的解决方案： 
        通过来源定位位置 来源  
        a标签 href的抽取  的查找 
2. 176数据库丢失的全站网站的Config数据， 迁移 
3. 可视化配置界面 
4. 短网址，修复， 通过redis映射来 
5. 微信的链接处理（实时爬取）

转载来源处理
'''

class BaiduSpider(object):
    def __init__(self):
        self.final_count = 10
        self.repeat_remain = self.final_count
        res = Configs.MongoConfigs.col_baidu_forbid_pattern.find()
        self.forbid_pattern = []
        self.pattern_redirect_url = re.compile('window\.location\.replace\("(.*?)"\)\}')
        for pattern in res:
            self.forbid_pattern.append(re.compile(pattern['pattern']))

    def append(self, word1, word2):
        res = ''
        if word1:
            res += word1
        if word2:
            res += ' ' + word2
        return res

    def run(self, base_url, keywords, offset, href_xpath, max_index, filter_before=True, index=0, sourse_spider=''):
        '''
        执行方法。
        :param base_url:
        :param key_word:
        :param offset:
        :param href_xpath:
        :param col:
        :param filter_before:
        :param index:
        :return:
        '''
        self.keywords = keywords
        self.source_spider = sourse_spider
        item = self.append(keywords[0], keywords[1])
        self.key_word = item
        end = False
        while not end:
            url = base_url % (item, index)
            url = url.replace("__", "%")
            index += offset
            if index > max_index:
                break
            list_html = Configs.ToolsObjManager.extract_tool.extract_html(url)[0]
            list_xhtml = etree.HTML(list_html)
            detail_hrefs = list_xhtml.xpath(href_xpath)
            for detail_href in detail_hrefs:
                # try:

                    if filter_before:
                        detail_href = ConfigV2.ToolObj.extract.get_before_redirect(detail_href)
                        print(detail_href)
                    # url去重
                    repeat = Configs.ToolsObjManager.redis_tool.sismember_value('real_baidu', detail_href)
                    if not repeat:
                        # harvest = Configs.ToolsObjManager.extract_tool.extract(detail_href)
                        '''文章内容分析'''
                        harvest = ConfigV2.ToolObj.extract.extract(detail_href)
                        # harvest 返回的是一个字典
                        if not harvest:
                            Configs.ToolsObjManager.redis_tool.sadd_value('real_baidu', detail_href)
                            continue

                        self.save_harvest(harvest)
                # except Exception as e:
                #     print(e)
                #     pass

    def contains_key(self, row, word):
        if word == '':
            return True
        if isinstance(row, list):
            row = ''.join(row)
        if row.find(word) > 0:
            return True


    # 保存数据 向mongodb 数据库中 web_data
    def save_harvest(self, harvest):
        crawling_time = str(int(time.time() * 1000))
        # 进行关键词查询
        # contains1 = self.con tains_key(harvest['article'], self.keywords[0])
        # contains2 = self.contains_key(harvest['article'], self.keywords[1])
        # if contains1 and contains2:
        if True:
            harvest['create_time'] = str(int(harvest['create_time'] * 1000))
            if len(harvest['create_time']) < 10:
                harvest['create_time'] = crawling_time
            # 去重url
            Configs.ToolsObjManager.redis_tool.sadd_value('real_baidu', harvest['url'])
            url = Configs.ToolsObjManager.str_tool.shrink_url(harvest['url'])
            print(harvest['url'])
            seach_flag = ConfigV2.ToolObj.str_tool.get_url_seach_patition(harvest["url"])
            #黑名单
            black = Configs.ToolsObjManager.redis_tool.sismember_value(Configs.ToolsObjManager.redis_tool.back_key, seach_flag)
            if black:
                return
            if harvest['article']:
                # 转载校验
                host_name = ConfigV2.ToolObj.str_tool.host2site(harvest['url'])
                md5 = Configs.ToolsObjManager.general_tool.article2md5(harvest['article'])
                refer_item = Configs.MongoConfigs.db_web.web_data.find_one({'article_md5': md5})
                refer_article_id = ''
                if refer_item:
                    harvest['article'] = []
                    refer_article_id = refer_item['_id']
                # 数据插入mongodb web_data
                Configs.MongoConfigs.db_web.web_data.insert_one({
                    'refer_article_id': refer_article_id,
                    'article_md5': md5,
                    'source_spider': host_name+"##"+self.source_spider,
                    'title': harvest['title'],
                    'source_from': harvest['source_from'],
                    'article': harvest['article'],
                    'crawling_time': crawling_time,
                    'create_time': harvest['create_time'],
                    'url': url,
                    'original_url': harvest['url'],
                    'key_word': self.key_word
                })



def test_back(url):
    seach_flag = ConfigV2.ToolObj.str_tool.get_url_seach_patition(url)
    # 黑名单 过滤
    black = Configs.ToolsObjManager.redis_tool.sismember_value(Configs.ToolsObjManager.redis_tool.back_key, seach_flag)
    if black:
        return
    print("爬取开始  表演。。")


def run_baidu():
    while True:
        span_list = []
        # 从 MySQL 数据库中查关键词
        keywords = Configs.ToolsObjManager.searchspider_tools.get_key_word()

        # keywords = [["火灾", "基站"], ["火灾", ""], [["起火", "机房"]]]

        tm = int(time.time())
        for keyword in keywords:
            spider = BaiduSpider()
            url = "http://www.baidu.com/s?wd=%s&pn=%s"
            span_list.append(gevent.spawn(spider.run, 'http://www.baidu.com/s?wd=%s&gpc=stf__3D'+str(tm-24*60*60)+'__2C' + str(tm)+'__7Cstftype__3D1&pn=%s', keywords=keyword, offset=10,
                       href_xpath='//h3/a/@href', max_index=50, filter_before=True, sourse_spider='百度搜索'))
            span_list.append(gevent.spawn(spider.run, "http://news.baidu.com/ns?word=%s&pn=%s", keywords=keyword, offset=10,
                       href_xpath='//h3/a/@href', max_index=100, filter_before=False, sourse_spider='百度新闻搜索'))
            # spider = BaiduSpider()
            # span_list.append(
            #     gevent.spawn(spider.run, 'http://news.baidu.com/ns?word=%s&pn=%s', keywords=keyword, offset=20,
            #                  href_xpath='//h3/a/@href', max_index=500, filter_before=True, sourse_spider='百度新闻'))
            # spider.run('https://www.baidu.com/s?wd=%s&pn=%s', keywords=keyword, offset=10,
            #            href_xpath='//h3/a/@href', max_index=100, filter_before=False, sourse_spider='百度搜索')
            # spider.run('http://news.baidu.com/ns?word=%s&pn=%s', keywords=keyword, offset=20,
            #            href_xpath='//h3/a/@href', max_index=100, filter_before=True, sourse_spider='百度新闻')
        gevent.joinall(span_list)


if __name__ == '__main__':
    run_baidu()
