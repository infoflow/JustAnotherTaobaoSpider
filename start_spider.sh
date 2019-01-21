#!/bin/bash
# 启动mitmproxy
nohub python3 taobao_mitm_proxy.py &
# 启动taobao spider
nohub python3 taobao_spider.py &
