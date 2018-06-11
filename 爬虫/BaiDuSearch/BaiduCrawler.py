import requests
from lxml import etree
import chardet
import time
from 爬虫.BaiDuSearch.GetKeywordTools import GetKeywordTools
from 爬虫.BaiDuSearch.ExtractTool import ExtractTool

'''
获取关键词MySQL->搜索->保存信息数据到mongodb
'''
class BaiduCrawler(object):
    @staticmethod
    def get_html(url):
        each_page_url = requests.get(url)
        bytes_each_page_html = each_page_url.content
        # print('1111:%s'%each_page_url.url)
        code = chardet.detect(each_page_url.content)["encoding"]
        each_page_html = bytes_each_page_html.decode(code)
        # print(code)
        obj_xpath = etree.HTML(each_page_html)
        # //*/h3/a/@href
        each_href = obj_xpath.xpath('//*/h3/a/@href')
        article_url = []
        for i in each_href:
            article_url.append(i)
        return article_url
            # print('百度首页的全部链接2222: %s' % article_url)
            # print('百度首页的全部链接: %s'%article_url)
        # return article_url

    @staticmethod
    def paging(base_url, keywords, page=0):
        # self.keywords = keywords
        real_url_list = []
        while page < 50:
            real_url = base_url % (keywords, page)
            real_url_final = real_url.replace('__', '% ')
            page += 10
            real_url_list.append(real_url_final)
        return real_url_list

    def run_baidu(self):
        baidu = BaiduCrawler()
        keywords = GetKeywordTools().get_mysql_keywords()
        for each_keyword in keywords:
            if each_keyword[1] == None:
                keyword = each_keyword[0]
                print('0 :%s' % keyword)
            else:
                keyword = each_keyword[0] + each_keyword[1]
                print('0+1 :%s' % keyword)
            base_url = 'http://www.baidu.com/s?wd=%s&pn=%s' + '&gpc=stf__3D' + str(int(time.time()) - 24 * 60 * 60) + '__2C' + str(int(time.time())) + '__7Cstftype__3D1'
            each_keyword_url = baidu.paging(base_url, keywords=keyword)
            # print('关键词: %s'%each_keyword_url)
            # t_url=[]
            for each_page_url in each_keyword_url:
                # print('按页链接:%s'%each_page_url)
                print('每一页的10条链接:%s' % (baidu.get_html(each_page_url)))
                # t_url.append(baidu.get_html(each_page_url))
                link = baidu.get_html(each_page_url)
                for each_link in link:
                    try:
                        ExtractTool().extract_title(each_link)
                    except:
                        print("error link !!!%s" % each_link)
                        continue

            # return t_url

if __name__ == '__main__':
    run = BaiduCrawler()
    print(run.run_baidu())








'''
    baidu =BaiduCrawler()
    # baidu.get_html('https://www.baidu.com/s?wd=888')
    # baidu.get_html('http://www.baidu.com/s?wd=特朗普宣战司法部&pn=50&gpc=stf%3D1526889056%2C1526975456%7Cstftype%3D1')
    # keywords = Configs.ToolsObjManager.searchspider_tools.get_key_word()
    # 处理 关键词+限定词
    keywords = GetKeywordTools().get_mysql_keywords()
    for each_keyword in keywords:
        if each_keyword[1] == None:
            keyword = each_keyword[0]
            print('0 :%s' % keyword)
        else:
            keyword = each_keyword[0]+each_keyword[1]
            print('0+1 :%s' % keyword)

        base_url='http://www.baidu.com/s?wd=%s&pn=%s'+'&gpc=stf__3D'+str(int(time.time())-24*60*60)+'__2C'+str(int(time.time()))+'__7Cstftype__3D1'
        each_keyword_url = baidu.paging(base_url,keywords=keyword)
        # print(each_keyword_url)
        # count = 0
        for each_page_url in each_keyword_url:
            baidu.get_html(each_page_url)
            # print(t_url)
        # count += 1
        # print('计数:%s%s'%(count, each_url))

    # baidu.get_html(url)
    # print(baidu.get_html(url))

    # def run_baidu_spider(self):
    #     while True:

'''





