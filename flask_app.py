from flask import Flask, jsonify, request, render_template, send_from_directory
import datetime, os

from MyLib import *

app = Flask(__name__)


#############################
# Action
#############################

@app.route('/', methods = ["GET"])
def index():
    req=request.args
    last_number = req.get("last", "30")
    return render_template("index.html", version=version, last_number=last_number)


@app.route('/show/<ip>', methods = ["GET"])
def show(ip):
    # 获取参数
    req=request.args
    last_number = req.get("last", "30")
    print("last_number=%s" % last_number)

    return render_template("show.html", host_ip=ip, last_number=last_number)


# GPU basic panel
@app.route('/show_GPU/<ip>', methods = ["GET"])
def show_gpu(ip):
    # 获取参数
    req=request.args
    last_number = req.get("last", "30")
    print("last_number=%s" % last_number)

    return render_template("show_GPU.html", host_ip=ip, last_number=last_number)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, ''),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


#############################
# API section
#############################

@app.route('/api/')
def hello():
    html="""
        <p><a href="/">Go to Home page</a></p>
        <h2>Help</h2>
        <p class="light">http://10.10.117.156:8071/</p>
        <p class="light">http://10.10.117.156:8071/?last=10</p>
    """
    return html + "For json data, pls visit: http://10.10.117.156:%s/api/usage_data" % settings.get("sys", "port")


@app.route('/api/ip_list', methods=['GET'])
def get_ip_list():
    sql = "select distinct(host_ip) FROM system_usage;"
    results=db_query(sql)
    return jsonify(results) 

@app.route('/api/usage_data', methods=['GET'])
def get_latest_data():
    """
    默认显示最新的30条信息
    """

    # 获取查询参数
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    host_ip = request.args.get('ip', "")

    last_number = int( request.args.get("last", "30") )

    if start_time and end_time:
        # 使用用户提供的时间段
        query_start = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        query_end = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    else:
        # 默认使用过去3小时
        #end_time = datetime.datetime.now()
        #start_time = end_time - datetime.timedelta(hours=3)
        #query_start = start_time
        #query_end = end_time
        query_start=datetime.datetime.now()
        query_end=query_start - datetime.timedelta(hours=3)


    # 查询指定时间段的数据
    #query = "SELECT timestamp, cpu_usage, memory_usage FROM system_usage WHERE timestamp BETWEEN %s AND %s"
    # 查询指定时间段的数据，并添加整数形式的时间戳
    sql = """
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
        1
    """

    if start_time and end_time:
        sql += " AND (timestamp BETWEEN '%s' AND '%s')" % (query_start, query_end)

    if host_ip:
        sql += " AND (host_ip = '%s')" % host_ip

    sql += " ORDER BY timestamp DESC"

    if start_time and end_time:
        pass
    else:
        sql += " limit %d;" % last_number

    #print(sql)
    results=db_query(sql)

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


@app.route('/api/ip_list_gpu', methods=['GET'])
def get_ip_list_gpu():
    sql = "select distinct(host_ip) FROM gpu_usage;"
    results=db_query(sql)
    return jsonify(results) 

@app.route('/api/usage_data_gpu', methods=['GET'])
def get_latest_data_gpu():
    """
    默认显示最新的30条信息
    """

    # 获取查询参数
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    host_ip = request.args.get('ip', "")

    last_number = int( request.args.get("last", "30") )

    if start_time and end_time:
        # 使用用户提供的时间段
        query_start = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        query_end = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    else:
        # 默认使用过去3小时
        #end_time = datetime.datetime.now()
        #start_time = end_time - datetime.timedelta(hours=3)
        #query_start = start_time
        #query_end = end_time
        query_start=datetime.datetime.now()
        query_end=query_start - datetime.timedelta(hours=3)


    # 查询指定时间段的数据
    #query = "SELECT timestamp, cpu_usage, memory_usage FROM system_usage WHERE timestamp BETWEEN %s AND %s"
    # 查询指定时间段的数据，并添加整数形式的时间戳
    sql = """
    SELECT 
        timestamp, 
        UNIX_TIMESTAMP(timestamp) AS unix_timestamp, 
        gpu_usage,
        gpu_temperature,
        gpu_memory_usage,
        host_ip,
        hostname
    FROM 
        gpu_usage 
    WHERE 
        1
    """

    if start_time and end_time:
        sql += " AND (timestamp BETWEEN '%s' AND '%s')" % (query_start, query_end)

    if host_ip:
        sql += " AND (host_ip = '%s')" % host_ip

    sql += " ORDER BY timestamp DESC"

    if start_time and end_time:
        pass
    else:
        sql += " limit %d;" % last_number

    #print(sql)
    results=db_query(sql)

    # 格式化为字典
    data = []
    for row in results:
        data.append({
            'timestamp': row[0].strftime('%Y-%m-%d %H:%M:%S'),
            'unix_timestamp': row[1],  # 整数形式的时间戳
            'gpu_usage': row[2],
            'gpu_temperature': row[3],
            'gpu_memory_usage': row[4],
            'host_ip': row[5],
            'hostname': row[6]
        })

    return jsonify(data)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(settings.get("sys", "port")) )

