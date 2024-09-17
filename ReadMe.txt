1. Aim
监控局域网内的若干台服务器的CPU和内存使用情况

2. 整体设计
(1) 一台服务器作为主程序，下载本项目
安装mysql5.7，推荐docker版
配置mysql数据库登录方式、创建表结构
(2) 每个服务器通过crontab 运行定时脚本 monitor_CPU_RAM.sh，比如每6分钟发送数据到mysql。
(3) 主服务器依赖Flask提供REST API，依赖 Chart.js 绘制折线图。


3. 端口
需要至少2个端口：
- mysql: 8070
- Flask: 8071

