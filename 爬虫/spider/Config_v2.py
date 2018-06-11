from 爬虫.spider.A1_MongoConfigs import MongoConfig
from 爬虫.spider.A3_MySqlTools import MySqlTools
from 爬虫.spider.B2_ExtractTool import ExtractTools
from 爬虫.spider.B1_StrTools import StrTools
from 爬虫.spider.C2_EmailTools import EmailToos

# 各个工具启用接口
class Config:
    class ToolObj:
        mongo_cfg = MongoConfig()
        mysql_tool = MySqlTools()
        str_tool = StrTools()
        extract = ExtractTools()
        email_tool = EmailToos()

    @staticmethod
    def ToolCls():
        pass

