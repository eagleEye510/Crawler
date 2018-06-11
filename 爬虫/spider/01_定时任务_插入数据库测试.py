import time
import Configs

Configs.MongoConfigs.conn.test.log.insert_one({'log': str(int(time.time()))})
