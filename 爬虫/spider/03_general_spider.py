import Configs
from FullSpider import FullSpider
import gevent
from gevent import monkey
monkey.patch_all()
import time

if __name__ == '__main__':

    # g = GeneralSpider('http://www.people.com.cn/')
    # g.start()

    while True:
        res = Configs.MongoConfigs.col_site_rule.find()
        spawn_list = []
        for i in res:

            g = FullSpider(i['base_url'])
            spawn_list.append(gevent.spawn(g.start))
        gevent.joinall(spawn_list)
