from pymysql import connect
class GetKeywordTools(object):
    def get_mysql_keywords(self):
        conn = connect(host='192.168.1.193', port=3306, user='root', password='Zkfr_duba@0623.', database='zkdp', charset='utf8')
        sql = 'SELECT * FROM zkdp.key_word_copy;'
        cur = conn.cursor()
        cur.execute(sql)
        tuple_keywords_set = cur.fetchall()
        each_keywords_list = []
        for each_keywords in tuple_keywords_set:
            each_keywords_list.append(list(each_keywords))
        # print(each_keywords_list)
        return  each_keywords_list

if __name__ == '__main__':
    getwords = GetKeywordTools()
    res = getwords.get_mysql_keywords()





