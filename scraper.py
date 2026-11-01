"""
GitHub Trending Scraper
抓取 GitHub Trending 榜单并解析为结构化数据
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


def fetch_trending(
    since: str = "weekly",
    language: Optional[str] = None,
    max_retries: int = 3,
    timeout: int = 20,
) -> List[Dict]:
    """
    抓取 GitHub Trending 榜单
    :param since: 'daily', 'weekly', 'monthly'
    :param language: 编程语言，如 'python', 'rust', None 为全部
    :param max_retries: 最大重试次数
    :param timeout: 请求超时时间
    :return: 包含项目信息的字典列表
    """
    base_url = "https://github.com/trending"
    if language:
        url = f"{base_url}/{language}?since={since}"
    else:
        url = f"{base_url}?since={since}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    }

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return parse_trending_html(resp.text)
            elif resp.status_code == 429:
                time.sleep(attempt * 2)
            else:
                resp.raise_for_status()
        except Exception as e:
            last_error = e
            time.sleep(attempt * 2)

    raise RuntimeError(f"抓取 GitHub Trending 失败 ({url}): {last_error}")


def parse_trending_html(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.find_all("article", class_="Box-row")
    results = []

    for article in articles:
        # 1. 仓库名称与链接
        h2 = article.find("h2")
        if not h2:
            continue
        a_tag = h2.find("a")
        if not a_tag:
            continue
        repo_path = a_tag.get("href", "").strip("/")
        repo_name = "".join(repo_path.split())
        repo_url = f"https://github.com/{repo_name}"

        # 2. 项目描述
        p_tag = article.find("p")
        desc = p_tag.text.strip() if p_tag else "暂无项目描述"

        # 3. 编程语言
        lang_span = article.find("span", itemprop="programmingLanguage")
        language = lang_span.text.strip() if lang_span else "Unknown"

        # 4. 周期新增 star 数
        stars_added_span = article.find("span", class_="float-sm-right")
        stars_added_text = stars_added_span.text.strip() if stars_added_span else ""
        # 提取形如 '12,062' 的纯数字
        match = re.search(r"([\d,]+)\s+stars", stars_added_text)
        if match:
            stars_added = f"+{match.group(1)}⭐"
            stars_added_num = int(match.group(1).replace(",", ""))
        else:
            stars_added = stars_added_text
            stars_added_num = 0

        # 5. 总 Star 与 Fork
        muted_links = article.find_all("a", class_="Link--muted")
        total_stars = ""
        forks = ""
        for m_link in muted_links:
            href = m_link.get("href", "")
            if href.endswith("/stargazers"):
                total_stars = m_link.text.strip()
            elif href.endswith("/forks"):
                forks = m_link.text.strip()

        results.append({
            "name": repo_name,
            "url": repo_url,
            "description": desc,
            "language": language,
            "stars_added": stars_added,
            "stars_added_num": stars_added_num,
            "total_stars": total_stars,
            "forks": forks,
        })

    return results


if __name__ == "__main__":
    repos = fetch_trending(since="weekly")
    print(f"成功抓取到 {len(repos)} 个周榜项目：")
    for r in repos[:3]:
        print(f"- {r['name']} ({r['stars_added']}): {r['description']}")
