from flask import Flask, jsonify, request, render_template
import pymysql
import datetime
import socket

app = Flask(__name__)

# MySQL 配置
MYSQL_HOST = '10.10.117.156'
MYSQL_PORT=8070
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_DATABASE = 'monitoring'



@app.route('/', methods = ["GET"])
def index():
    return render_template("index.html")



@app.route('/show/<ip>', methods = ["GET"])
def show(ip):
    # 获取参数
    #req=request.args
    #ip = req.get("ip", "")
    #print("ip=%s" % ip)

    return render_template("show.html", host_ip=ip)



def get_host_ip():
    """获取主机的 IP 地址"""
    hostname = socket.gethostname() #'jinlab-svr1.icb.ac.cn'
    host_ip=socket.gethostbyname(hostname) #'10.10.117.156'
    return [hostname, host_ip]








#############################
# API section
#############################

@app.route('/api/')
def hello():
    return "For json data, pls visit: http://10.10.117.156:8071/api_usage_data"

@app.route('/api/usage_data', methods=['GET'])
def get_latest_data():
    # 获取查询参数
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    host_ip = request.args.get('ip', "")

    if start_time and end_time:
        # 使用用户提供的时间段
        query_start = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        query_end = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    else:
        # 默认使用过去3小时
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=3)
        query_start = start_time
        query_end = end_time

    # 连接到 MySQL 数据库
    db = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DATABASE)
    cursor = db.cursor()

    # 查询指定时间段的数据
    #query = "SELECT timestamp, cpu_usage, memory_usage FROM system_usage WHERE timestamp BETWEEN %s AND %s"
    # 查询指定时间段的数据，并添加整数形式的时间戳
    query = """
    SELECT 
        timestamp, 
        UNIX_TIMESTAMP(timestamp) AS unix_timestamp, 
        cpu_usage, 
        memory_usage,
        host_ip,
        hostname
    FROM 
        system_usage 
    WHERE 
        (timestamp BETWEEN %s AND %s)
    """

    # 如果提供了 IP 参数，添加到查询条件中
    if host_ip:
        query += " AND host_ip = %s ORDER BY timestamp;"
        cursor.execute(query, (query_start, query_end, host_ip))
    else:
        query += " ORDER BY timestamp;"
        cursor.execute(query, (query_start, query_end))


    # 获取结果
    results = cursor.fetchall()
    cursor.close()
    db.close()

    # 格式化为字典
    data = []
    for row in results:
        data.append({
            'timestamp': row[0].strftime('%Y-%m-%d %H:%M:%S'),
            'unix_timestamp': row[1],  # 整数形式的时间戳
            'cpu_usage': row[2],
            'memory_usage': row[3],
            'host_ip': row[4],
            'hostname': row[5]
        })

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8071)

