"""
Summarizer Module
调用 DeepSeek / OpenAI 兼容接口，根据热榜数据和用户偏好生成高水准简报
"""

import os
import json
from typing import List, Dict, Optional


def build_fallback_summary(
    new_repos: List[Dict],
    retained_repos: List[Dict],
    last_date_str: str,
    recipient_name: str = "嘉贤",
) -> str:
    """当未配置 API Key 时提供的格式化降级简报"""
    date_marker = f"（自 {last_date_str} 以来）" if last_date_str else "（本期）"
    lines = [f"{recipient_name}，这周 GitHub 热榜的简报来了。🆕 表示{date_marker}新上榜的项目：\n"]

    for repo in new_repos[:10]:
        stars = repo.get("stars_added", "")
        desc = repo.get("description", "暂无简介")
        lines.append(f"🆕 {repo['name']}，本周 {stars}。{desc}")

    if retained_repos:
        retained_names = [r["name"] for r in retained_repos]
        lines.append(f"\n上次就在、这次还在榜上的有：{'、'.join(retained_names)}。")

    lines.append("\n💡 提示：当前使用本地离线模板生成。在 .env 中配置 DEEPSEEK_API_KEY 即可获得深度个性化提炼与场景点评！")
    return "\n".join(lines)


def generate_weekly_digest(
    new_repos: List[Dict],
    retained_repos: List[Dict],
    last_date_str: str = "",
    recipient_name: str = "嘉贤",
    user_interests: str = "AI Agent、游戏开发/Unity、音色克隆与多模态、代码辅助工具与架构",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """
    生成个性化周报
    """
    api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    model = model or os.getenv("OPENAI_MODEL", "deepseek-chat")

    if not api_key:
        print("[提示] 未检测到 DEEPSEEK_API_KEY / OPENAI_API_KEY，使用基础模板生成预览。")
        return build_fallback_summary(new_repos, retained_repos, last_date_str, recipient_name)

    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)

    date_desc = f"{last_date_str} 那次简报之后" if last_date_str else "上次简报之后"

    system_prompt = f"""你是一个技术嗅觉极其敏锐的资深开发者朋友，每周给好友【{recipient_name}】发一份精炼、接地气的 GitHub 热榜周报。

【好友关注的领域偏好】：
{user_interests}

【写作风格与格式要求】：
1. 称呼开篇："{recipient_name}，这周 GitHub 热榜的简报来了。🆕 表示 {date_desc} 新上榜的项目："
2. 新上榜项目格式：
   🆕 仓库全名，本周 +新增Star数。一两句口语化讲清核心亮点，并点出在实际业务/个人项目中的落地场景（例如“宠物 agent 的记忆设计很值得参考它”、“Unity 项目变大可以用它来管理代码”、“专门用来去掉界面上的 AI 味”）。
3. 真实与客观：
   - 如果项目没有写描述，直接吐槽“热度不低，但仓库没写简介”；
   - 如果是模型越狱或高风险项目，提醒“看看就好，不建议用”；
   - 如果有重点突出项目（即使上次在榜），可以单独拎出来讲一两句点评；
4. 持续在榜项目归纳：
   - 格式：“上次就在、这次还在榜上的有：xxx、xxx、xxx（加上关键定位括号注记）。”
5. 趋势总结：
   - 结尾必须有一句简练的技术趋势洞察，例如“这周还是 coding agent 的 skill 最多，直接跟小模型训练或游戏 AI 相关的新项目不多，最值得看的是 xxx 和 xxx。”
6. 语气：像朋友私信发微信一样自然、直切要害、绝对不能有公文感或生硬的机器翻译腔。
"""

    payload = {
        "新上榜项目列表": [
            {
                "name": r["name"],
                "stars_added": r["stars_added"],
                "language": r["language"],
                "description": r["description"],
                "total_stars": r["total_stars"],
            }
            for r in new_repos
        ],
        "持续在榜项目列表": [
            {
                "name": r["name"],
                "stars_added": r["stars_added"],
                "language": r["language"],
                "description": r["description"],
            }
            for r in retained_repos
        ],
    }

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"以下是本期 GitHub 热榜数据，请生成简报：\n{json.dumps(payload, ensure_ascii=False, indent=2)}"},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[错误] 调用大模型失败: {e}，启用降级方案生成。")
        return build_fallback_summary(new_repos, retained_repos, last_date_str, recipient_name)
