from lxml import etree
import Configs
import re
import json


class Public_Wechat(object):
    def __init__(self):
        self.pub_url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query='
        self.pub_xpath = "//ul[@class='news-list2']//@href"
        self.pattern_js = re.compile("msgList = (.*)")

    def search_link(self, base_url, key_word):
        url = base_url + key_word
        html = Configs.ToolsObjManager.extract_tool.extract_html_by_count(url, 6000)
        xhtml = etree.HTML(html)
        hrefs = xhtml.xpath(self.pub_xpath)

        # 过滤掉javascript
        hrefs = [Configs.ToolsObjManager.str_tool.deal_relative_href('', href) for href in hrefs]
        hrefs = [href for href in hrefs if href]
        return set(hrefs)

    def get_pub_link(self, pub_code):
        return self.search_link(self.pub_url, pub_code)

    def extract_pub_items(self, href):
        html = Configs.ToolsObjManager.extract_tool.extract_html(href)[0]
        data = self.pattern_js.search(html).group(1)
        # 去除末尾的字符（生成json）
        data = data[:-2]
        data = json.loads(data)['list']
        data = [item['app_msg_ext_info'] for item in data]
        return data

    def get_current_url(self, pub_code, title):
        hrefs = self.get_pub_link(pub_code)
        for href in hrefs:
            print(href)
            data_list = self.extract_pub_items(href)
            for item in data_list:
                if item['title'].strip() == title.strip():
                    item['content_url'] = Configs.ToolsObjManager.str_tool.html_label_conveter(item['content_url'])
                    return 'https://mp.weixin.qq.com' + item['content_url']


if __name__ == '__main__':
    wechat = Public_Wechat()
    res = wechat.get_current_url('oksadamu', '火灾现场的转型宣传手册')
    print(res)


# if __name__ == '__main__':
#     url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%81%AB%E7%81%BE'
#     wechat = Public_Wechat()
#     wechat.repeat_request(url)


