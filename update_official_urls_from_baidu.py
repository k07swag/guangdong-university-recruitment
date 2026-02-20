#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从百度搜索「校名 人事 招聘」结果页中提取【官方】或第一条人事/招聘相关结果的真实 URL，
写回 data/universities_guangdong.json 的 recruitment_url。不再使用推测的人事处域名。
"""
import json
import re
import time
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
UNIV_JSON = DATA_DIR / "universities_guangdong.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def get_baidu_search_url(school_name: str) -> str:
    q = school_name.strip() + " 人事 招聘"
    return "https://www.baidu.com/s?" + urlencode({"wd": q})


def resolve_baidu_link(baidu_link: str, session: requests.Session) -> str | None:
    """把百度 /link?url=xxx 解析为真实 URL。只取 url 参数，避免 eqid 等干扰。"""
    if not baidu_link or "baidu.com/link" not in baidu_link:
        return None
    try:
        parsed = urlparse(baidu_link)
        qs = parse_qs(parsed.query)
        raw = qs.get("url", [None])[0]
        if not raw:
            return None
        # 只保留 url 参数，去掉 wd/eqid（不再 encode，避免二次编码）
        clean_link = "https://www.baidu.com/link?url=" + raw
        r = session.get(clean_link, headers=HEADERS, allow_redirects=True, timeout=15)
        return r.url if r.ok else None
    except Exception:
        return None


def extract_first_result_url(html: str, school_name: str, session: requests.Session) -> str | None:
    """
    从百度搜索结果 HTML 中提取：优先带「官方」的结果，否则第一条人事/招聘相关结果的真实 URL。
    """
    soup = BeautifulSoup(html, "lxml")
    # 百度结果链接：通常在 content_left 下的 a[href*='baidu.com/link?url']
    content_left = soup.find(id="content_left")
    if not content_left:
        content_left = soup
    links = content_left.find_all("a", href=re.compile(r"baidu\.com/link\?url="))
    seen_href = set()
    official_url = None
    first_result_url = None
    for a in links:
        href = a.get("href")
        if not href or href in seen_href:
            continue
        seen_href.add(href)
        # 同一块内是否带「官方」
        block = a.find_parent(["div", "table"])
        block_text = (block.get_text() if block else "") + (a.get_text() or "")
        is_official = "官方" in block_text
        real = resolve_baidu_link(href, session)
        if not real:
            continue
        # 排除百度自家
        if "baidu.com" in real.replace("www.baidu.com/link", ""):
            continue
        if is_official:
            official_url = real
            break
        if first_result_url is None:
            # 优先标题里含校名或人事/招聘
            title = (a.get_text() or "").strip()
            if school_name in title or "人事" in title or "招聘" in title:
                first_result_url = real
    return official_url or first_result_url


def main():
    if not UNIV_JSON.exists():
        print("未找到", UNIV_JSON)
        return
    with open(UNIV_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    universities = data.get("universities", [])
    if not universities:
        print("院校列表为空")
        return

    session = requests.Session()
    session.headers.update(HEADERS)
    updated = 0
    failed = []
    for i, u in enumerate(universities):
        name = u.get("name", "").strip()
        if not name:
            continue
        search_url = get_baidu_search_url(name)
        try:
            r = session.get(search_url, timeout=15)
            r.raise_for_status()
            real_url = extract_first_result_url(r.text, name, session)
            if real_url:
                u["recruitment_url"] = real_url
                updated += 1
                print(f"[{i+1}/{len(universities)}] {name} -> {real_url[:60]}...")
            else:
                u["recruitment_url"] = ""
                failed.append(name)
                print(f"[{i+1}/{len(universities)}] {name} -> 未解析到结果，已清空 recruitment_url")
        except Exception as e:
            u["recruitment_url"] = ""
            failed.append(name)
            print(f"[{i+1}/{len(universities)}] {name} -> 请求异常: {e}，已清空 recruitment_url")
        time.sleep(1.2)

    data["updated"] = time.strftime("%Y-%m-%d")
    data["description"] = "广东省本科、专科院校名单，招聘页链接来自百度搜索「校名 人事 招聘」结果（官方或第一条人事/招聘相关）。"
    with open(UNIV_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n已写回", UNIV_JSON)
    print("成功:", updated, "未解析:", len(failed))
    if failed:
        print("未解析到 URL 的学校（招聘页将显示为百度搜索）:", failed[:20], "..." if len(failed) > 20 else "")


if __name__ == "__main__":
    main()
