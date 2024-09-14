#!/bin/bash

# MySQL 配置
MYSQL_HOST="10.10.117.156"
MYSQL_PORT="8070"
MYSQL_USER="root"
MYSQL_PASSWORD="123456"
MYSQL_DATABASE="monitoring"

# 获取当前时间
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# 获取 CPU 使用情况，1-100
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')

# 获取内存使用情况，1-100
MEMORY_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')

# 获取主机名
HOST_NAME=$(hostname)
HOST_IP=$(hostname -I | awk '{print $1}')


# 将结果写入 MySQL 数据库
mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -P"$MYSQL_PORT" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "INSERT INTO system_usage (timestamp, cpu_usage, memory_usage, hostname, host_ip) VALUES ('$TIMESTAMP', $CPU_USAGE, $MEMORY_USAGE, '$HOST_NAME', '$HOST_IP');"
