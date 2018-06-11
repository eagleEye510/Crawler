from pymysql import connect




class SearchSpiderTools(object):

    def get_key(self):
        conn = connect(host='192.168.1.193', port=3306, user='root', password='Zkfr_duba@0623.', database='zkdp',
                       charset='utf8')
        sql = 'select DISTINCT(key_word) from keyword'
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        final_result = [i[0] for i in res ]
        print(final_result)

    def none_replace(self, row):
        result = ['', '']
        if not row[0]:
            result[0] = ''
        else:
            result[0] = row[0]
        if not row[1]:
            result[1] = ''
        else:
            result[1] = row[1]
        return result

    def get_key_word(self):
        conn = connect(host='192.168.1.193', port=3306, user='root', password='Zkfr_duba@0623.', database='zkdp', charset='utf8')
        sql = 'SELECT * FROM zkdp.keyword;'
        cur = conn.cursor()
        cur.execute(sql)
        ress = cur.fetchall()

        result = [self.none_replace(res) for res in ress]
        return result


if __name__ == '__main__':
    tool = SearchSpiderTools()
    # res = tool.get_key_word()
    # print(res)
    res = tool.get_key_word()
    print(res)

'''
{'class': ['l_post', 'j_l_post', 'l_post_bright', 'noborder', ''],
 'data-field': '{"author":{"user_id":2910260631,"user_name":"Robesir","name_u":"Robesir&ie=utf-8","user_sex":1,"portrait":"970d526f626573697277ad","is_like":1,"level_id":3,"level_name":"\\u79c0\\u624d","cur_score":17,"bawu":0,"props":null},"content":{"post_id":116118996937,"is_anonym":false,"open_id":"tbclient","open_type":"android","date":"2017-12-12 22:53","vote_crypt":"","post_no":1,"type":"0","comment_num":0,"ptype":"0","is_saveface":false,"props":null,"post_index":0,"pb_tpoint":null}}'}
'''