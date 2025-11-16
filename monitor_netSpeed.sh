#!/bin/bash

# 获取当前时间
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 初始化接收和发送字节数
TOTAL_RX=0
TOTAL_TX=0

# 读取 /proc/net/dev 并汇总所有网卡的接收和发送字节数
while read -r line; do
    # 过滤出有效的行，检查是否包含冒号
    if [[ $line == *:* ]]; then
        RX_BYTES=$(echo "$line" | awk '{print $2}')  # 接收字节数
        TX_BYTES=$(echo "$line" | awk '{print $10}') # 发送字节数

        # 累加接收和发送字节数
        TOTAL_RX=$((TOTAL_RX + RX_BYTES))
        TOTAL_TX=$((TOTAL_TX + TX_BYTES))
    fi
done < /proc/net/dev

# 输出结果
echo -e "$TIMESTAMP\nNet Speed: Receive: $TOTAL_RX Transmit: $TOTAL_TX" #>> /path/to/your/net_speed.log

# 硬盘读写速度
iostat -d -k 1 2 | awk '/^[^ ]/ {if ($1 != "Device:") { read += $3; write += $4 }} END {print "Total Read KB: " read, "Total Write KB: " write}'