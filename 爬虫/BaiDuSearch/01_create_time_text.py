import time
import datetime
from 爬虫.BaiDuSearch.ExtractTool import ExtractTool
from 爬虫.spider.B1_StrTools import StrTools
class Test():
    def extract_timestamp(self, html):
        '''
        从一段字符串（HTML）源码中， 提取最接近的 timestamp
        :param html:
        :return:
        '''

        time_tuple = StrTools().pattern_time.findall(html)
        lengths = [len(i[0]) for i in time_tuple]
        max_length = max(lengths)
        # 找出发布时间
        precise_time_tuple = [i for i in time_tuple if len(i[0]) >= max_length - 3]

        time_stamp_list = []
        current_timestamp = time.time()

        for time_item in precise_time_tuple:
            if not time_item[1]:
                stamp_result = StrTools().convert_time_format2stamp("%s-%s" % (datetime.datetime.now().year, time_item[0]))
            elif len(time_item[1]) == 2:
                stamp_result = StrTools().convert_time_format2stamp("20%s-%s" % (datetime.datetime.now().year, time_item[0]))
            else:
                stamp_result = StrTools().convert_time_format2stamp(time_item[0])
            if stamp_result < current_timestamp:
                time_stamp_list.append(stamp_result)
                print("1111%s"%time_stamp_list)

        time_stamp_list.sort()
        print("2222%s" % time_stamp_list[len(time_stamp_list) // 2])
        return time_stamp_list[len(time_stamp_list) // 2]
if __name__ == '__main__':

    r_html = ExtractTool().extract_title('http://news.163.com/18/0604/16/DJFHSPLT000189FH.html')
    # print(r_html)
    create_time = Test().extract_timestamp(r_html)
    # print(create_time)
