#!/bin/bash
cd "$(dirname "$0")"
echo "=========================================="
echo "  广东省高校招聘信息 - 更新数据"
echo "=========================================="
echo ""
echo "1. 安装/检查依赖..."
pip3 install -q -r requirements.txt
echo "2. 抓取各校招聘页公告 → 更新 data/jobs.json"
python3 update_jobs.py
echo ""
echo "=========================================="
echo "更新完成。刷新页面即可看到最新下拉数据。"
echo "（若需从百度刷新招聘页链接，可再运行: python3 update_official_urls_from_baidu.py）"
echo "=========================================="
read -p "按回车键关闭..."
