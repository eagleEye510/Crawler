import Configs
from lxml import etree
import re
from BBSSpiderTools import BBSSpiderTools
import time
import gevent


class BBSSpider(object):

    def __init__(self):
        self.bbs_tool = BBSSpiderTools()
        # self.base_url = 'https://bbs.51credit.com/forum.php?gid=46'
        self.xpath = '//td/h2/a/@href'
        self.detail_xpath = "//a[@class='s xst']/@href"
        self.div_pattern = re.compile('(.*)\s{2}(.*)')

    def parse_base_url(self, base_url, source_spider):
        self.source_spider = source_spider
        html = Configs.ToolsObjManager.extract_tool.extract_html(base_url)[0]
        xhtml = etree.HTML(html)
        bank_hrefs = xhtml.xpath(self.xpath)
        print(bank_hrefs)
        self.host = Configs.ToolsObjManager.str_tool.extract_host(base_url)
        # 'https://bbs.51credit.com/forum-3-1.html', 'https://bbs.51credit.com/forum-8-1.html', 'https://bbs.51credit.com/forum-5-1.html'
        real_bank_hrefs = [Configs.ToolsObjManager.str_tool.deal_relative_href(self.host, h) for h in bank_hrefs]
        last_flag = 'strong>1</strong'
        for real_bank_href in real_bank_hrefs:
            self.end_page = 0
            index = 1
            while self.end_page < 20:
                current_page_href = real_bank_href.replace('-1.htm', '-%s.htm' % index)
                bank_html = Configs.ToolsObjManager.extract_tool.extract_html(current_page_href)[0]
                # 判断是否是最后一页
                if index > 1:
                    if bank_html.find(last_flag) > 0:
                        self.end_page += 20

                bank_xhtml = etree.HTML(bank_html)
                detail_hrefs = bank_xhtml.xpath(self.detail_xpath)
                # https://bbs.51credit.com/thread-3937140-1-1.html
                real_detail_hrefs = [Configs.ToolsObjManager.str_tool.deal_relative_href(self.host, h) for h in detail_hrefs]
                for real_detail_href in real_detail_hrefs:
                    # self.crawl_detail(real_detail_href, [])
                    try:
                        self.crawl_detail(real_detail_href, [])
                    except:
                        pass
                    # try:
                    #     self.crawl_detail(real_detail_href, [])
                    # except Exception as e:
                    #     print(e)
                        # if self.end_page:
                        #     break
                index += 1

    def time_convert(self, tm):
        time_array = time.strptime(tm, '%Y-%m-%d %H:%M:%S')
        return str(int(time.mktime(time_array))*1000)

    # 爬取详情页信息
    def crawl_detail(self, real_detail_href, article, href=''):
        if not href:
            href = real_detail_href
        # 'https://bbs.51credit.com/thread-3932083-1-1.html', 'https://bbs.51credit.com/thread-3933293-1-1.html'
        print('try save href:' + href)
        try:
            self.host = self.host
        except:
            self.host = Configs.ToolsObjManager.str_tool.extract_host(real_detail_href)
        print('crawling:' + real_detail_href)
        save_field = {
            'next_page': '.bm_h【href】',
            'title': 'title',
            'article': [
                "div[id='postlist'] > div",
                [
                    "div[class='authi'] > a",
                    "td .t_f",
                    ".authi > em > span【title】| .authi > em"
                ]
            ]
        }
        result = {}
        field_result = Configs.ToolsObjManager.extract_tool.extract_by_bs4(real_detail_href, save_field)
        row_data = Configs.MongoConfigs.sns_web.find_one({'original_url': href})
        # 把字段给弄进去。。
        result['title'] = field_result[0]['title']
        result['original_url'] = href
        result['url'] = Configs.ToolsObjManager.str_tool.shrink_url(href)
        result['floor_message_list'] = article + field_result[0]['article']
        try:
            if not result['floor_message_list'][-1][0]:
                result['floor_message_list'].pop()
        except:
            # 空串  无需处理
            pass

        if field_result[0]['next_page']:
            key_href = href
            href = Configs.ToolsObjManager.str_tool.deal_relative_href(self.host, field_result[0]['next_page'])
            self.crawl_detail(href, result['floor_message_list'], href=key_href)
        else:
            # 存库
            result['source_spider'] = self.source_spider
            # 时间戳重新刷一遍
            for i in range(len(result['floor_message_list'])):
                result['floor_message_list'][i][2] = self.bbs_tool.impurity_time_converter(result['floor_message_list'][i][2])
                if len(result['floor_message_list'][i][2]) < 5:
                    result['floor_message_list'][i][2] = result['crawling_time']
            # 请登陆信息 去掉
            try:
                result['floor_message_list'][0][1] = self.bbs_tool.extract_article(result['floor_message_list'][0][1]).strip()
            except:
                # 错误信息无需处理。
                pass
            if row_data:
                if row_data['floor_message_list'] == result['floor_message_list']:
                    self.end_page += 1
                    return
                else:
                    result['crawling_time'] = row_data['crawling_time']
                    result['create_time'] = row_data['create_time']
                    try:
                        result['last_time'] = result['floor_message_list'][-1][2]
                    except:
                        Configs.MongoConfigs.col_error.insert_one({
                            'error_type': 'bbs_time_extract_error',
                            'msg': result['original_url']
                        })
                        result['last_time'] = 0
                    Configs.MongoConfigs.sns_web.update({'original_url': href}, result)
            else:
                result['crawling_time'] = str(int(time.time()*1000))
                result['create_time'] = result['floor_message_list'][0][2]
                result['last_time'] = result['floor_message_list'][-1][2]
                Configs.MongoConfigs.sns_web.insert_one(result)


if __name__ == '__main__':
    span_list = []
    #
    while True:

        # spider = BBSSpider()
        # spider.parse_base_url('https://bbs.51credit.com/forum.php?gid=46', '我爱卡')
        spider = BBSSpider()
        span_list.append(gevent.spawn(spider.parse_base_url, 'http://bbs.creditcard.com.cn/forum.php?gid=4', '信用卡之窗'))
        spider = BBSSpider()
        span_list.append(gevent.spawn(spider.parse_base_url, 'https://bbs.51credit.com/forum.php?gid=46', '我爱卡'))
        gevent.joinall(span_list)
