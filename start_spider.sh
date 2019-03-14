#!/bin/bash
# 启动mitmproxy
nohup mitmdump taobao_mitm_proxy.py &
# 启动taobao spider
nohup python3 taobao_spider.py &
