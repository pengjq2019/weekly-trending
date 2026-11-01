"""
Notifier Module
支持多种微信推送渠道：PushPlus、Server酱、企业微信群机器人，以及本地归档
"""

import os
import requests
from typing import Optional, Dict


def send_pushplus(content: str, token: str, title: str = "每周 GitHub 热榜简报") -> bool:
    """通过 PushPlus 推送到微信"""
    url = "http://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown",
    }
    try:
        resp = requests.post(url, json=data, timeout=15)
        res_json = resp.json()
        if res_json.get("code") == 200:
            print("[PushPlus] 微信推送成功！")
            return True
        else:
            print(f"[PushPlus] 推送返回错误: {res_json.get('msg')}")
            return False
    except Exception as e:
        print(f"[PushPlus] 发送异常: {e}")
        return False


def send_serverchan(content: str, sendkey: str, title: str = "每周 GitHub 热榜简报") -> bool:
    """通过 Server酱 (Turbo版) 推送到微信"""
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    data = {
        "title": title,
        "desp": content,
    }
    try:
        resp = requests.post(url, data=data, timeout=15)
        res_json = resp.json()
        if res_json.get("code") == 0:
            print("[Server酱] 微信推送成功！")
            return True
        else:
            print(f"[Server酱] 推送返回错误: {res_json.get('message')}")
            return False
    except Exception as e:
        print(f"[Server酱] 发送异常: {e}")
        return False


def send_wechat_work_webhook(content: str, webhook_key: str) -> bool:
    """通过企业微信机器人 Webhook 推送"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={webhook_key}"
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        },
    }
    try:
        resp = requests.post(url, json=data, timeout=15)
        res_json = resp.json()
        if res_json.get("errcode") == 0:
            print("[企业微信机器人] 推送成功！")
            return True
        else:
            print(f"[企业微信机器人] 推送失败: {res_json.get('errmsg')}")
            return False
    except Exception as e:
        print(f"[企业微信机器人] 发送异常: {e}")
        return False


def save_local_archive(content: str, filepath: str = "latest_report.md") -> None:
    """保存最新一期简报到本地文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[本地归档] 已成功保存简报至 {filepath}")


def notify(content: str, title: str = "每周 GitHub 热榜简报") -> Dict[str, bool]:
    """
    统一推送入口：根据配置的环境变量自动尝试可用的通知通道
    """
    results = {}
    pushed = False

    # 1. 本地始终保存一份
    save_local_archive(content)

    # 2. PushPlus
    pushplus_token = os.getenv("PUSHPLUS_TOKEN")
    if pushplus_token:
        results["pushplus"] = send_pushplus(content, pushplus_token, title)
        pushed = True

    # 3. Server酱
    serverchan_key = os.getenv("SERVERCHAN_KEY")
    if serverchan_key:
        results["serverchan"] = send_serverchan(content, serverchan_key, title)
        pushed = True

    # 4. 企业微信机器人
    wechat_work_key = os.getenv("WECHAT_WORK_KEY")
    if wechat_work_key:
        results["wechat_work"] = send_wechat_work_webhook(content, wechat_work_key)
        pushed = True

    if not pushed:
        print("[提示] 未检测到推送密钥（PUSHPLUS_TOKEN / SERVERCHAN_KEY / WECHAT_WORK_KEY）。")
        print("简报已保存至 latest_report.md，配置密钥后即可自动推送到微信。")

    return results
