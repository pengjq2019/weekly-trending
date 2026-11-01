"""
History Tracker
追踪历史榜单，比对计算本期新上榜 (🆕) 与持续在榜项目
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional


DEFAULT_HISTORY_FILE = "history.json"


def load_history(history_file: str = DEFAULT_HISTORY_FILE) -> Dict:
    """读取历史快照"""
    if not os.path.exists(history_file):
        return {
            "last_run_date": "",
            "last_repos": [],
            "history_archive": {},
        }

    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # 兼容旧格式（如果是纯列表）
                return {
                    "last_run_date": "",
                    "last_repos": data,
                    "history_archive": {},
                }
            return data
    except Exception as e:
        print(f"[警告] 读取历史记录失败，使用空历史: {e}")
        return {
            "last_run_date": "",
            "last_repos": [],
            "history_archive": {},
        }


def diff_trending(
    current_repos: List[Dict],
    history_file: str = DEFAULT_HISTORY_FILE,
) -> Tuple[List[Dict], List[Dict], str]:
    """
    比对当前榜单与上期榜单
    :return: (new_repos, retained_repos, last_date_str)
    """
    history = load_history(history_file)
    last_repos = set(history.get("last_repos", []))
    last_date = history.get("last_run_date", "")

    new_repos = []
    retained_repos = []

    for repo in current_repos:
        repo_name = repo["name"]
        if repo_name in last_repos:
            retained_repos.append(repo)
        else:
            new_repos.append(repo)

    return new_repos, retained_repos, last_date


def save_history(
    current_repos: List[Dict],
    history_file: str = DEFAULT_HISTORY_FILE,
    run_date_format: str = "%m/%d",
) -> None:
    """
    将当前榜单保存为最新历史快照
    """
    history = load_history(history_file)
    today_str = datetime.now().strftime(run_date_format)

    current_repo_names = [r["name"] for r in current_repos]
    archive = history.get("history_archive", {})

    # 更新每个项目的历史记录
    for repo in current_repos:
        name = repo["name"]
        if name not in archive:
            archive[name] = {
                "first_seen": today_str,
                "times_seen": 1,
            }
        else:
            archive[name]["times_seen"] = archive[name].get("times_seen", 1) + 1
            archive[name]["last_seen"] = today_str

    updated_history = {
        "last_run_date": today_str,
        "last_run_iso": datetime.now().isoformat(),
        "last_repos": current_repo_names,
        "history_archive": archive,
    }

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(updated_history, f, ensure_ascii=False, indent=2)
