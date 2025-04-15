#!/bin/bash

# Aim: get GPU useage and its meme usage. 
# This is a demo, in order to write in monitor_CPU_RAM.sh.

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
# Part II GPU
#######################

# 判断nvidia-smi命令是否存在
if command -v nvidia-smi &> /dev/null
then
    echo 'nvidia-smi check pass' `date` > /dev/null
else
    echo 'nvidia-smi not exists'
    exit 1
fi

# 没退出，表示存在该命令
GPU_info=`nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,memory.total,memory.used --format=csv,noheader,nounits`
#utilization.gpu [%], memory.total [MiB], memory.used [MiB]
#0 %, 81920 MiB, 51792 MiB

#$ nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,memory.total,memory.used --format=csv,noheader
#9 %, 33, 81920 MiB, 55760 MiB
#$ nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,memory.total,memory.used --format=csv,noheader,nounits
#0, 33, 81920, 53776
#GPU使用率，温度； 显存总量，已使用显存

#echo -e $GPU_info


# 1. 获取GPU使用率
GPU_USAGE=$(echo $GPU_info | awk -F ', ' '{print $1}')
# 2. 获取GPU温度
GPU_TEMPERATURE=$(echo $GPU_info | awk -F ', ' '{print $2}')
# 3. 获取GPU显存总量
#GPU_MEMORY_TOTAL=$(echo $GPU_info | awk -F ', ' '{print $3}')
# 4. 获取GPU已使用显存
#GPU_MEMORY_USED=$(echo $GPU_info | awk -F ', ' '{print $4}')
# 5. 获取GPU显存使用率 0-100
GPU_MEMORY_USAGE=$(echo $GPU_info | awk -F ', ' '{print $4/$3 * 100.0}')

#echo "$GPU_USAGE $GPU_TEMPERATURE $GPU_MEMORY_USAGE"

# 将结果写入 MySQL 数据库
mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -P"$MYSQL_PORT" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" \
    -e "INSERT INTO gpu_usage (timestamp, gpu_usage, gpu_temperature, gpu_memory_usage, hostname, host_ip) \
    VALUES ('$TIMESTAMP', $GPU_USAGE, $GPU_TEMPERATURE, $GPU_MEMORY_USAGE, '$HOST_NAME', '$HOST_IP');"
