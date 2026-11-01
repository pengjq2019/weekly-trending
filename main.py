"""
GitHub Trending Weekly Digest Generator
主入口脚本：负责整体流水线调度
"""

import os
import argparse
from dotenv import load_dotenv

from scraper import fetch_trending
from history import diff_trending, save_history
from summarizer import generate_weekly_digest
from notifier import notify


def main():
    # 自动加载本地 .env 文件
    load_dotenv()

    parser = argparse.ArgumentParser(description="GitHub Trending 每周热榜简报生成器")
    parser.add_argument(
        "--since",
        choices=["daily", "weekly", "monthly"],
        default=os.getenv("TRENDING_SINCE", "weekly"),
        help="榜单周期 (默认: weekly)",
    )
    parser.add_argument(
        "--lang",
        default=os.getenv("TRENDING_LANGUAGE", None),
        help="过滤指定语言 (如 python, rust, typescript)",
    )
    parser.add_argument(
        "--name",
        default=os.getenv("RECIPIENT_NAME", "嘉贤"),
        help="简报收件人称呼 (默认: 嘉贤)",
    )
    parser.add_argument(
        "--interests",
        default=os.getenv(
            "USER_INTERESTS",
            "AI Agent、游戏开发/Unity、音色克隆与多模态、代码辅助工具与架构、开源工具生态",
        ),
        help="个人关注偏好描述",
    )
    parser.add_argument(
        "--history-file",
        default=os.getenv("HISTORY_FILE", "history.json"),
        help="历史记录文件路径",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式：仅打印生成内容，不写回历史、不发起微信推送",
    )

    args = parser.parse_args()

    print("========================================")
    print("🚀 启动 GitHub 热榜简报生成流水线")
    print(f"📌 周期: {args.since} | 语言: {args.lang or '全部'}")
    print(f"👤 收件人: {args.name}")
    print("========================================\n")

    # 1. 抓取热榜
    print("[1/4] 正在抓取 GitHub Trending 榜单...")
    repos = fetch_trending(since=args.since, language=args.lang)
    print(f"-> 成功抓取到 {len(repos)} 个项目。")

    # 2. 历史比对
    print("\n[2/4] 正在比对历史快照...")
    new_repos, retained_repos, last_date = diff_trending(repos, history_file=args.history_file)
    print(f"-> 新上榜项目 (🆕): {len(new_repos)} 个")
    print(f"-> 持续在榜项目: {len(retained_repos)} 个")
    if last_date:
        print(f"-> 上次运行记录日期: {last_date}")

    # 3. 智能提炼与简报生成
    print("\n[3/4] 正在提炼要点并生成个性化简报...")
    digest_content = generate_weekly_digest(
        new_repos=new_repos,
        retained_repos=retained_repos,
        last_date_str=last_date,
        recipient_name=args.name,
        user_interests=args.interests,
    )

    print("\n---------------- 生成的简报内容 ----------------")
    print(digest_content)
    print("------------------------------------------------\n")

    if args.dry_run:
        print("💡 [Dry Run 模式] 已跳过保存历史与推送通知。")
        return

    # 4. 推送通知
    print("[4/4] 正在推送到已配置的通知渠道...")
    notify(digest_content, title=f"每周 GitHub 热榜简报 ({args.name})")

    # 5. 更新并持久化历史记录
    save_history(repos, history_file=args.history_file)
    print(f"-> 历史记录已更新并保存至 {args.history_file}")
    print("\n✅ 流水线执行完毕！")


if __name__ == "__main__":
    main()
