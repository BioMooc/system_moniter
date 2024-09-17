import pymysql
import socket

################
# 模式设置：决定着 读取哪个配置文件
################
# test: 本机测试
# pro: 生产环境
import configparser
settings = configparser.ConfigParser()
settings.read("config.ini")
#mode = settings.get("sys", "mode")

# MySQL 配置
MYSQL_HOST = settings.get("mysql", "host")
MYSQL_PORT=int(settings.get("mysql", "port"))
MYSQL_USER = settings.get("mysql", "user")
MYSQL_PASSWORD = settings.get("mysql", "password")
MYSQL_DATABASE = settings.get("mysql", "database")

version = settings.get("sys", "version")



#############################
# functions
#############################

def get_host_ip():
    """获取主机的 IP 地址"""
    hostname = socket.gethostname() #'jinlab-svr1.icb.ac.cn'
    host_ip=socket.gethostbyname(hostname) #'10.10.117.156'
    return [hostname, host_ip]


def db_query(sql):
    # 连接到 MySQL 数据库
    db = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DATABASE)
    cursor = db.cursor()

    cursor.execute(sql)
    
    # 获取结果
    results = cursor.fetchall()
    cursor.close()
    db.close()

    return(results)