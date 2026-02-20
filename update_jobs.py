#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广东省高校教师岗、行政岗招聘信息更新脚本。
从各校人事处/招聘页抓取链接，提取可能与教师、行政招聘相关的条目，并更新 data/jobs.json。
可定期运行（如 crontab 每日一次）以保持信息更新。
"""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("请先安装依赖: pip install -r requirements.txt")
    raise

# 招聘关键词（用于在页面链接/文本中识别教师岗、行政岗）
KEYWORDS_TEACHER = ["教师", "教师岗", "教学", "师资", "博士", "硕士招聘", "专任教师", "辅导员"]
KEYWORDS_ADMIN = ["行政", "管理岗", "职员", "人事", "招聘", "人才引进", "公开招聘"]
KEYWORDS_COMMON = ["招聘", "人才", "应聘", "招录", "公告"]

# 栏目/导航类短标题，不当作具体文章收集（避免“人事政策”“人事改革”等）
NAV_BLOCKLIST = frozenset([
    "人事政策", "人事改革", "工作流程", "办事指南", "机构设置", "规章制度",
    "下载专区", "通知公告", "招聘信息", "首页", "更多", "列表", "栏目",
    "政策法规", "师资队伍", "部门介绍", "联系我们", "人才招聘",
])
# 具体文章/制度常见特征（标题含这些或含年份则视为“具体条目”）
ARTICLE_INDICATORS = ("公告", "通知", "办法", "条例", "启事", "公示", "简章", "计划", "规定", "意见")

DATA_DIR = Path(__file__).resolve().parent / "data"
UNIVERSITIES_JSON = DATA_DIR / "universities_guangdong.json"
JOBS_JSON = DATA_DIR / "jobs.json"
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
REQUEST_TIMEOUT = 15
DELAY_BETWEEN_REQUESTS = 1.5  # 礼貌爬取间隔（秒）


def load_universities():
    with open(UNIVERSITIES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("universities", [])


def load_jobs():
    if not JOBS_JSON.exists():
        return {"last_updated": "", "jobs": [], "sources": []}
    with open(JOBS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_jobs(data):
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(JOBS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def classify_job_type(title: str, href: str) -> str:
    """判断岗位类型：教师岗 / 行政岗 / 其他"""
    text = (title + " " + href).lower()
    teacher_score = sum(1 for k in KEYWORDS_TEACHER if k in title or k in href)
    admin_score = sum(1 for k in KEYWORDS_ADMIN if k in title or k in href)
    if teacher_score > admin_score:
        return "教师岗"
    if admin_score > 0:
        return "行政岗"
    return "其他"


def is_likely_job_link(a_tag, base_url: str) -> bool:
    """判断链接是否可能是招聘公告/列表页"""
    href = a_tag.get("href") or ""
    if not href or href.startswith("#") or href.startswith("javascript:"):
        return False
    try:
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.path.endswith((".pdf", ".doc", ".docx", ".jpg", ".png", ".zip")):
            return False
    except Exception:
        return False
    text = (a_tag.get_text() or "").strip()
    combined = text + " " + href
    return any(k in combined for k in KEYWORDS_COMMON + KEYWORDS_TEACHER + KEYWORDS_ADMIN)


def is_nav_or_category(title: str) -> bool:
    """短标题且为栏目/导航名则排除，不当作具体文章"""
    t = (title or "").strip()
    if len(t) <= 2:
        return True
    if t in NAV_BLOCKLIST:
        return True
    for nav in NAV_BLOCKLIST:
        if nav in t and len(t) <= len(nav) + 4:  # 如“人事政策一览”
            return True
    return False


def is_article_like(title: str) -> bool:
    """标题像具体文章/制度（含公告、通知、年份等）"""
    t = (title or "").strip()
    if is_nav_or_category(t):
        return False
    if any(k in t for k in ARTICLE_INDICATORS):
        return True
    import re
    if re.search(r"20\d{2}", t):  # 含年份
        return True
    return len(t) >= 12  # 较长标题多为具体文章（栏目名通常较短）


def fetch_page(url: str) -> Optional[str]:
    try:
        r = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except Exception as e:
        print(f"  请求失败: {url} -> {e}")
        return None


def extract_job_links(html: str, base_url: str, school_name: str) -> List[dict]:
    """从人事处/招聘页 HTML 中提取可能为教师/行政招聘的链接"""
    soup = BeautifulSoup(html, "lxml")
    jobs = []
    seen_urls = set()

    for a in soup.find_all("a", href=True):
        if not is_likely_job_link(a, base_url):
            continue
        try:
            full_url = urljoin(base_url, a.get("href", ""))
        except Exception:
            continue
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)
        title = (a.get_text() or "").strip()
        if len(title) < 2 or len(title) > 120:
            continue
        if is_nav_or_category(title):
            continue
        job_type = classify_job_type(title, full_url)
        jobs.append({
            "school": school_name,
            "title": title,
            "url": full_url,
            "type": job_type,
            "fetched_at": datetime.now().strftime("%Y-%m-%d"),
        })
    return jobs


def update_sources(universities: List[dict], data: dict) -> None:
    """更新 sources：每所学校的招聘页入口及最后检查时间"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sources = []
    for u in universities:
        sources.append({
            "name": u["name"],
            "city": u.get("city", ""),
            "type": u.get("type", ""),
            "recruitment_url": u.get("recruitment_url", ""),
            "recruitment_name": u.get("recruitment_name", "招聘/人事"),
            "last_checked": now,
        })
    data["sources"] = sources


def main():
    os.chdir(Path(__file__).resolve().parent)
    print("加载院校列表...")
    universities = load_universities()
    data = load_jobs()
    all_jobs = []

    update_sources(universities, data)

    for i, u in enumerate(universities):
        url = (u.get("recruitment_url") or "").strip()
        name = u.get("name", "")
        if not url or not url.startswith("http"):
            continue
        print(f"[{i+1}/{len(universities)}] {name} ...")
        html = fetch_page(url)
        time.sleep(DELAY_BETWEEN_REQUESTS)
        if html:
            jobs = extract_job_links(html, url, name)
            all_jobs.extend(jobs)
            if jobs:
                print(f"  发现 {len(jobs)} 条可能招聘信息")

    data["jobs"] = all_jobs
    save_jobs(data)
    print(f"已更新 {JOBS_JSON}，共 {len(all_jobs)} 条，时间 {data['last_updated']}")


if __name__ == "__main__":
    main()
