#!/bin/bash

# v0.2 add GPU info

#######################
# Part 0 settings
#######################
# MySQL 配置
MYSQL_HOST="10.10.117.156"
MYSQL_PORT="8070"
MYSQL_USER="root"
MYSQL_PASSWORD="123456"
MYSQL_DATABASE="monitoring"

# 获取当前时间
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# 获取主机名
HOST_NAME=$(hostname)
HOST_IP=$(hostname -I | awk '{print $1}')

#######################
# Part I CPU & memory
#######################
# 获取 CPU 使用情况，1-100
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')

# 获取内存使用情况，1-100
MEMORY_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')

# 将结果写入 MySQL 数据库
mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -P"$MYSQL_PORT" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" \
    -e "INSERT INTO system_usage (timestamp, cpu_usage, memory_usage, hostname, host_ip) \
    VALUES ('$TIMESTAMP', $CPU_USAGE, $MEMORY_USAGE, '$HOST_NAME', '$HOST_IP');"


#######################
# Part II GPU
#######################
# 判断nvidia-smi命令是否存在
if command -v nvidia-smi &> /dev/null
then
    # echo 'nvidia-smi check pass' `date` > /dev/null
    # 有GPU就获取其信息
    GPU_info=`nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,memory.total,memory.used --format=csv,noheader,nounits`
    # 1. 获取GPU使用率
    GPU_USAGE=$(echo $GPU_info | awk -F ', ' '{print $1}')
    # 2. 获取GPU温度
    GPU_TEMPERATURE=$(echo $GPU_info | awk -F ', ' '{print $2}')
    # 3. 获取GPU显存使用率 0-100
    GPU_MEMORY_USAGE=$(echo $GPU_info | awk -F ', ' '{print $4/$3 * 100.0}')
    # 4.写入 MySQL
    mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -P"$MYSQL_PORT" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" \
        -e "INSERT INTO gpu_usage (timestamp, gpu_usage, gpu_temperature, gpu_memory_usage, hostname, host_ip) \
        VALUES ('$TIMESTAMP', $GPU_USAGE, $GPU_TEMPERATURE, $GPU_MEMORY_USAGE, '$HOST_NAME', '$HOST_IP');"
else
    #echo 'nvidia-smi not exists'
    exit 0 #没有GPU也正常退出
fi



# how to use?
#1. in $ crontab -e # add line
# */6 * * * * /usr/bin/bash /datapool/wangjl/web/docs/code/system/monitor_CPU_RAM.sh
#2. in tmux, add
# $ watch -n 360 bash /datapool/wangjl/web/docs/code/system/monitor_CPU_RAM.sh
