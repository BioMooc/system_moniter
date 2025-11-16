#!/bin/bash
#
# Aim: get disk size occupied by each user, order: DESC;
# How to use: $ sudo bash path/to/this/script/monitor_DiskSizeByUser.sh /datapool/ 40 /home/wangjl/tmp/report/
# By wangjl
# v0.1
# v0.2

# 0 检查参数个数是否为3
if [ $# -ne 3 ]; then
    echo "错误：脚本需要 exactly 3 个参数" >&2
    echo "用法: $0 <calcPath> <coreNumber> <outputDir>" >&2
    exit 1
fi

# I 设置参数默认值
echo "-->[`date`]Step1: get and set params"
TARGET_DIR=${1:-/datapool/}
MAX_PROCESSES=${2:-40}
OUTPUT_DIR=${3:-/home/$USER/}

filename=${OUTPUT_DIR}/"diskUsedSize.$(date +%Y%m%d-%H%M%S)"
echo $filename

# 显示实际使用的值
echo "统计目录: $TARGET_DIR"
echo "最大进程数: $MAX_PROCESSES"
echo "输出目录: $OUTPUT_DIR"

# II 多进程统计每个子目录的大小
echo "-->[`date`]Step2: calc subdir size"
find "$TARGET_DIR" -maxdepth 1 -type d ! -path "$TARGET_DIR" | \
	xargs -I {} -P $MAX_PROCESSES du -sh {} 2>/dev/null | \
	tee ${filename}.txt

# III 排序
echo "-->[`date`]Step3: order by size DESC"
echo -e "<pre>`date`\n" > ${filename}.html
cat ${filename}.txt | sort -hr >> ${filename}.html
echo "-->Done! Output: ${filename}.html"