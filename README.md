# 🤖 Weekly GitHub Trending Digest（每周 GitHub 热榜简报）

自动抓取 GitHub Trending 周榜，利用 **增量历史追踪** 标记 🆕 新晋项目与持续在榜项目，配合 **DeepSeek / OpenAI 大模型** 进行地道、敏锐的业务场景点评，并于 **每周六早晨 9:00 自动推送到你的微信**。

---

## ✨ 核心特性

- 🎯 **增量历史比对**：自动维护 `history.json`，精准区分「🆕 本周新上榜」与「持续在榜」项目。
- 🧠 **大模型深度点评**：杜绝机械翻译腔，像技术朋友聊天一样指出在实际业务（如 Agent 记忆、Unity 开发、代码重构等）中的落地点与避坑提示。
- 📲 **多通道微信直达**：原生支持 **PushPlus（推送加）**、**Server酱**、**企业微信机器人**，手机微信随时随地查阅。
- ⏰ **完全零成本免服务器**：基于 **GitHub Actions** 定时调度运行，无需个人购买云服务器。
- 🛠 **高可定制**：称呼、技术兴趣领域、过滤编程语言、榜单周期（周榜/日榜/月榜）均可随心配置。

---

## 📂 项目结构

```text
├── .github/
│   └── workflows/
│       └── weekly_digest.yml     # GitHub Actions 定时工作流 (每周六 09:00 自动运行)
├── scraper.py                    # GitHub Trending 页面抓取与数据清洗
├── history.py                    # 历史记录管理与增量比对 (标记 🆕 与持续在榜)
├── summarizer.py                 # 大模型 Prompt 组装与个性化点评生成 (支持 DeepSeek/OpenAI)
├── notifier.py                   # 多通道微信推送 (PushPlus / Server酱 / 企业微信)
├── main.py                       # 主流程控制脚本
├── history.json                  # 历史快照数据文件 (自动更新)
├── latest_report.md              # 最新一期简报存档
├── requirements.txt              # Python 依赖项
├── .env.example                  # 环境变量模板
└── README.md                     # 说明文档
```

---

## 🚀 极速上手

### 1. 本地运行体验

```bash
# 1. 克隆代码或进入项目目录
cd default-workspace

# 2. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 DEEPSEEK_API_KEY 与 PUSHPLUS_TOKEN

# 5. 试运行 (Dry Run 模式，仅生成预览，不推送微信)
python main.py --dry-run

# 6. 正式运行 (生成简报、推送到微信、并更新 history.json)
python main.py
```

---

## 🔑 密钥获取指南

### 1. 微信推送密钥（推荐 PushPlus，完全免费）
1. 微信搜索公众号 **pushplus推送加**（或访问 [pushplus.plus](https://www.pushplus.plus/)）微信扫码登录。
2. 在「个人中心」复制你的 **Token**。
3. 填入 `.env` 的 `PUSHPLUS_TOKEN` 或 GitHub Secrets。

### 2. 大模型 API Key（推荐 DeepSeek）
1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/) 注册并获取 API Key。
2. 费用说明：每周运行一次仅消耗数千 tokens，调用一次成本约 **0.005 元人民币**，5 元充值可使用数年。
3. 填入 `.env` 的 `DEEPSEEK_API_KEY` 或 GitHub Secrets。

---

## ☁️ 部署到 GitHub Actions（全自动运行）

无需本地电脑开机，交给 GitHub 托管运行：

### 第一步：推送到你的 GitHub 仓库
```bash
git init
git add .
git commit -m "feat: initial weekly github digest"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<你的仓库名>.git
git push -u origin main
```

### 第二步：在 GitHub 仓库添加 Secrets
进入 GitHub 仓库页面：
1. 点击 **Settings** -> **Secrets and variables** -> **Actions**。
2. 点击 **New repository secret**，添加以下密钥：
   - `DEEPSEEK_API_KEY`：你的 DeepSeek API Key。
   - `PUSHPLUS_TOKEN`：你的 PushPlus Token。

### 第三步：手动测试运行
1. 进入仓库的 **Actions** 标签页。
2. 在左侧选择 **Weekly GitHub Trending Digest**。
3. 点击右侧 **Run workflow** 下拉按钮，点击绿色的 **Run workflow**。
4. 运行成功后，查看你的微信，即可收到最新一期 GitHub 热榜简报！

---

## 🎨 个性化定制参数

在 `.env` 或 GitHub 仓库的 **Settings -> Secrets and variables -> Actions -> Variables** 中配置：

| 变量名 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `RECIPIENT_NAME` | 嘉贤 | 简报开头的问候称呼 |
| `USER_INTERESTS` | AI Agent、游戏开发/Unity、音色克隆与多模态、代码辅助工具与架构 | 大模型在点评项目时重点切入的业务领域 |
| `TRENDING_SINCE` | `weekly` | 榜单周期：`weekly` (周榜)、`daily` (日榜)、`monthly` (月榜) |
| `TRENDING_LANGUAGE` | 空（全部） | 可限定语言，如 `python`、`rust`、`typescript`、`go` 等 |
