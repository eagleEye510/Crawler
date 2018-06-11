import requests
import chardet
from lxml import etree
# Article 正文泛化系统
from newspaper import Article
import re
class ExtractTool(object):
    def extract_title(self, each_article_link):
        # newspaper article 正文泛化系统
        a = Article(each_article_link, language='zh')
        a.download()
        a.parse()
        html = a.html
        title = a.title
        # text = a.text.split() 空格分割 返回list
        article = [i.strip() for i in a.text.split("\n") if i.strip()]
        return html
        # print("title:%s" % title + "article:%s" % article)
if __name__ == '__main__':
    test=ExtractTool()
    # http://www.baidu.com/link?url=BvOUqYL8ipPk-9XFISCaRuI44K_mvrvjDi4NQVrTDHZ49JiommucmECVL3VbXm4HUqmCX6kB-_AGFen_mTJM3Ad8yL_fH9YnQ2QPmd3xMBi
    test.extract_title('http://www.baidu.com/link?url=BvOUqYL8ipPk-9XFISCaRuI44K_mvrvjDi4NQVrTDHZ49JiommucmECVL3VbXm4HUqmCX6kB-_AGFen_mTJM3Ad8yL_fH9YnQ2QPmd3xMBi')

    ''' request = requests.get(each_article_link)
        byte_each_article_html = request.content
        print('解码之前:%s'%byte_each_article_html)
        code = chardet.detect(byte_each_article_html)['encoding']
        decode_html = byte_each_article_html.decode(code)
        # obj_xpath= etree.HTML(decode_html)
        # title = obj_xpath.xpath('//title/text()')
        # xpath匹配规则无法泛化
        # source_spider = obj_xpath.xpath("//*/a[@class='source']/text()")
        # release_time = obj_xpath.xpath("//*/span[@ class='date']/text()")
        '''













