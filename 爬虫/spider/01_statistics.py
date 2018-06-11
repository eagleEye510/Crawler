from Config_v2 import Config
import time


class Statistics:

    def get_source_spiders(self):
        res = Config.ToolObj.mongo_cfg.col_sites.find()
        return [i['source_spider'] for i in res]

    def insert_query(self, query, count, statistics_time):
        if not query:
            query = {"from": "total"}
        query['count'] = count
        query['statistics_time'] = statistics_time
        Config.ToolObj.mongo_cfg.col_statistics_hourly.insert_one(query)

    def save_count(self, query, start_time, end_time):
        # 通过id查 所以先将id查询出来。
        start_time = int(start_time)
        end_time = int(end_time)
        start_mongoid = None
        temp = Config.ToolObj.mongo_cfg.db_portal.web_data.find_one(
            dict({"crawling_time": {"$gte": str(start_time*1000)}}, **query)
        )
        if temp:
            start_mongoid = temp.get('_id')

        if not start_mongoid:
            self.insert_query(query, 0, end_time)
            return

        # start_mongoid 的条件加入进来。
        total_query = dict({
            "_id": {"$gte": start_mongoid}
        }, **query)

        end_mongoid = None
        if end_time:
            first_collection = Config.ToolObj.mongo_cfg.db_portal.web_data.find_one(
                {"crawling_time": {"$gte": str(end_time*1000)}}
            )
            if first_collection:
                end_mongoid = first_collection.get("_id")

        if end_mongoid:
            total_query["_id"] = dict(
                {"$lte": end_mongoid}, **total_query.get("_id", {})
            )
        count = Config.ToolObj.mongo_cfg.db_portal.web_data.count(total_query)
        self.insert_query(query, count, end_time)

    # 0.0.0.0 account.jetbrains.com
    def record(self, current_timestamp):
        # 取整点的时间戳以减小误差（例如 6:02 取 6：00）
        hours = (current_timestamp + 60 * 30) // (60 * 60)
        end_timestamp = hours * 60 * 60
        start_timestamp = end_timestamp - 60*60
        query_totals = [{}]

        # 获取source_spider查询条件
        source_spiders = [i['source_spider'] for i in Config.ToolObj.mongo_cfg.col_map.find()]
        source_spider_query = [{"source_spider": source_spider} for source_spider in source_spiders]
        query_totals += source_spider_query

        # 获取keyword 查询条件
        key_words = Config.ToolObj.mysql_tool.get_keywords()
        for keyword in key_words:
            query_totals.append({
                "key_word": keyword
            })

        for query_total in query_totals:
            self.save_count(query_total, start_timestamp, end_timestamp)


if __name__ == '__main__':
    statistics = Statistics()
    current_timestamp = time.time()
    print(current_timestamp)
    statistics.record(current_timestamp)

