1. Aim
监控局域网内的若干台服务器的CPU和内存使用情况

2. 整体设计
(1) 一台服务器作为主程序，下载本项目
安装mysql5.7，推荐docker版
配置mysql数据库登录方式、创建表结构
(2) 每个服务器通过crontab 运行定时脚本 monitor_CPU_RAM.sh，比如每6分钟发送数据到mysql。
(3) 主服务器依赖Flask提供REST API，依赖 Chart.js 绘制折线图。
https://www.chartjs.org/


3. 端口
需要至少2个端口：
- mysql: 8070
- Flask: 8071


4. 默认
显示最新的30条记录。
url 支持参数: ?last=30
默认删除2周前的数据：冲突点是，系统时间有差异，有的相差7个小时?!
    怎么自动同步不同机器的系统时间？
    使用中心 api 接收信息?
    目前使用的是 mysql 远程，需要每个server都有 mysql 客户端。


5. How to add GPU info?
new table: 见下文 1(3B)



###############
How to run?
###############

1. Database settings [on one server]

- I use database name "monitoring", table name "system_usage".
- You may use the port and database name and table name you like.

(1) Start mysql server.

I use mysql 5.7 in docker:
```
$ docker run -e MYSQL_DATABASE=monitoring -e MYSQL_ROOT_PASSWORD=123456 \
-p 8070:3306 -v /datapool/wangjl/dockerFile:/var/lib/mysql --name mysql \
-d dawneve/mysql:latest
```

(2) open port

`$ sudo iptables -I INPUT -p tcp --dport 8071 -j ACCEPT`

(3) create table

```
$ mysql -h 127.0.0.1 -P 8070 -u root -p

USE monitoring;

CREATE TABLE system_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    cpu_usage FLOAT NOT NULL,
    memory_usage FLOAT NOT NULL
);

ALTER TABLE system_usage
    ADD COLUMN host_ip VARCHAR(45),
    ADD COLUMN hostname VARCHAR(100);
```

Check data:
```
> SET time_zone = 'Asia/Shanghai';  -- 替换为你需要的时区

SELECT * FROM system_usage;

select * FROM system_usage WHERE timestamp < NOW() - INTERVAL 1 MINUTE;
```

(3B) create table GPU
```
USE monitoring;

CREATE TABLE gpu_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    gpu_usage FLOAT NOT NULL,
    gpu_temperature FLOAT NOT NULL,
    gpu_memory_usage FLOAT NOT NULL,
    host_ip VARCHAR(45) NOT NULL,
    hostname VARCHAR(100)
);

# check
desc gpu_usage;
```

(4) write the mysql seetings in `/config.ini` under "mysql" section.



2. Input data to database from each server. [on each server]

(1) modify mysql settings in shell script `/monitor_CPU_RAM.sh`;

(2) copy it to each server;

(3) run this script every 5-20 minites using `crontab` to send CPU and memory usage to database;

```
$ crontab -e
*/6 * * * * bash /datapool/wangjl/web/docs/code/system/monitor_CPU_RAM.sh
```

Or use watch in tmux:
`$ watch -n 360 bash /datapool/wangjl/web/docs/code/system/monitor_CPU_RAM.sh`



(4) 也可以通过curl提交数据
```
https://github.com/louislam/uptime-kuma/issues/819

curl -s "https://uk.****.com/api/push/******?status=up&msg=Disk%20usage%20is%20Fixed:${DISKUSAGE}%25"
```



3. Start web server [on one server]

(1) open a port on your server

```
$ sudo iptables -I INPUT -p tcp --dport 8071 -j ACCEPT

$ python3 -m http.server 8071
check in web browser http://ip:8070
then ctrl+C to stop the testing server.
```

(2) install python3 packages when needed.

```
$ pip3 install pymysql
$ pip3 install flask
```

(3) write this port in `/config.ini` under "sys" section: `port = 8071`

(4) Run server: `$ python3 flask_app.py`

check in web browser http://ip:8070




4. more API usage 

设置时间范围参数:
http://10.10.117.156:8071/api/usage_data?start=2024-09-17%2009:00:00&end=2024-09-17%2010:00:00

支持设置IP
http://10.10.117.156:8071/api/usage_data?start=2024-09-17%2009:00:00&end=2024-09-17%2010:00:00&ip=10.10.117.156



5. 定期清理垃圾数据：超过2周的删除
    select * FROM system_usage WHERE timestamp < NOW() - INTERVAL 336 HOUR;
    DELETE FROM system_usage WHERE timestamp < NOW() - INTERVAL 336 HOUR;

设置每周天晚上23点执行，删除两周前的数据：24*14=336
$ crontab -e
0 23 * * 0   bash /datapool/wangjl/web/docs/code/system/monitor_clean_week_ago.sh
