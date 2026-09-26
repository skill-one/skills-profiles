# CoPaw AI 助手技能

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能集合。

CoPaw 是一个个人 AI 助手框架，您可以在自己的机器或云中部署它。它通过单个代理连接到多个聊天平台（钉钉、飞书、QQ、Discord、iMessage、Telegram、Mattermost、Matrix、MQTT），支持自定义 Python 技能、计划任务（cron）、本地和云端的 LLM，并在 `http://127.0.0.1:8088/` 提供一个 Web 控制台。

---

## 安装

### pip（如果可用 Python 3.10–3.13，推荐使用）

```bash
pip install copaw
copaw init --defaults    # 使用合理默认值的非交互式设置
copaw app                # 启动 Web 控制台 + 后端
```

### 脚本安装（无需 Python 设置）

**macOS / Linux:**
```bash
curl -fsSL https://copaw.agentscope.io/install.sh | bash
# 支持使用 Ollama:
curl -fsSL https://copaw.agentscope.io/install.sh | bash -s -- --extras ollama
# 多个附加功能:
curl -fsSL https://copaw.agentscope.io/install.sh | bash -s -- --extras ollama,llamacpp
```

**Windows CMD:**
```cmd
curl -fsSL https://copaw.agentscope.io/install.bat -o install.bat && install.bat
```

**Windows PowerShell:**
```powershell
irm https://copaw.agentscope.io/install.ps1 | iex
```

脚本安装后，打开一个新终端：
```bash
copaw init --defaults
copaw app
```

### 从源代码安装

```bash
git clone https://github.com/agentscope-ai/CoPaw.git
cd CoPaw
pip install -e ".[dev]"
copaw init --defaults
copaw app
```

---

## CLI 参考

```bash
copaw init                  # 交互式工作区设置
copaw init --defaults       # 非交互式设置
copaw app                   # 启动控制台 (http://127.0.0.1:8088/)
copaw app --port 8090       # 使用自定义端口
copaw --help                # 列出所有命令
```

---

## 工作区结构

`copaw init` 创建工作区后（默认：`~/.copaw/workspace/`）：

```
~/.copaw/workspace/
├── config.yaml          # 代理、提供者、通道配置
├── skills/              # 自定义技能文件（自动加载）
│   └── my_skill.py
├── memory/              # 对话记忆存储
└── logs/                # 运行时日志
```

---

## 配置 (`config.yaml`)

`copaw init` 生成此文件。直接编辑它或使用控制台 UI。

### LLM 提供者（兼容 OpenAI）

```yaml
providers:
  - id: openai-main
    type: openai
    api_key: ${OPENAI_API_KEY}        # 使用环境变量引用
    model: gpt-4o
    base_url: https://api.openai.com/v1

  - id: local-ollama
    type: ollama
    model: llama3.2
    base_url: http://localhost:11434
```

### 代理设置

```yaml
agent:
  name: CoPaw
  language: en                        # en, zh, ja, 等。
  provider_id: openai-main
  context_limit: 8000
```

### 通道：钉钉

```yaml
channels:
  - type: dingtalk
    app_key: ${DINGTALK_APP_KEY}
    app_secret: ${DINGTALK_APP_SECRET}
    agent_id: ${DINGTALK_AGENT_ID}
    mention_only: true                # 仅在群组中 @ 提及时响应
```

### 通道：飞书（Lark）

```yaml
channels:
  - type: feishu
    app_id: ${FEISHU_APP_ID}
    app_secret: ${FEISHU_APP_SECRET}
    mention_only: false
```

### 通道：Discord

```yaml
channels:
  - type: discord
    token: ${DISCORD_BOT_TOKEN}
    mention_only: true
```

### 通道：Telegram

```yaml
channels:
  - type: telegram
    token: ${TELEGRAM_BOT_TOKEN}
```

### 通道：QQ

```yaml
channels:
  - type: qq
    uin: ${QQ_UIN}
    password: ${QQ_PASSWORD}
```

### 通道：Mattermost

```yaml
channels:
  - type: mattermost
    url: ${MATTERMOST_URL}
    token: ${MATTERMOST_TOKEN}
    team: my-team
```

### 通道：Matrix

```yaml
channels:
  - type: matrix
    homeserver: ${MATRIX_HOMESERVER}
    user_id: ${MATRIX_USER_ID}
    access_token: ${MATRIX_ACCESS_TOKEN}
```

---

## 自定义技能

技能是放置在 `~/.copaw/workspace/skills/` 中的 Python 文件。它们在 CoPaw 启动时**自动加载** — 无需注册步骤。

### 最小技能结构

```python
# ~/.copaw/workspace/skills/weather.py

SKILL_NAME = "get_weather"
SKILL_DESCRIPTION = "获取指定城市的当前天气"

# 工具模式（OpenAI 函数调用格式）
SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": SKILL_NAME,
        "description": SKILL_DESCRIPTION,
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如 'Tokyo'"
                }
            },
            "required": ["city"]
        }
    }
}


def get_weather(city: str) -> str:
    """获取给定城市的天气数据。"""
    import os
    import requests

    api_key = os.environ["OPENWEATHER_API_KEY"]
    url = f"https://api.openweathermap.org/data/2.5/weather"
    resp = requests.get(url, params={"q": city, "appid": api_key, "units": "metric"})
    resp.raise_for_status()
    data = resp.json()
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    return f"{city}: {temp}°C, {desc}"
```

### 支持异步的技能

```python
# ~/.copaw/workspace/skills/summarize_url.py

SKILL_NAME = "summarize_url"
SKILL_DESCRIPTION = "获取并总结 URL 的内容"

SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": SKILL_NAME,
        "description": SKILL_DESCRIPTION,
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "要总结的 URL"}
            },
            "required": ["url"]
        }
    }
}


async def summarize_url(url: str) -> str:
    import httpx

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url)
        text = resp.text[:4000]   # 截断以适应上下文限制
    return f"来自 {url} 的内容预览:\n{text}"
```

### 返回结构化数据的技能

```python
# ~/.copaw/workspace/skills/list_files.py

import os
import json

SKILL_NAME = "list_files"
SKILL_DESCRIPTION = "列出目录中的文件"

SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": SKILL_NAME,
        "description": SKILL_DESCRIPTION,
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "绝对或相对目录路径"
                },
                "extension": {
                    "type": "string",
                    "description": "按扩展名过滤，例如 '.py'. 可选。"
                }
            },
            "required": ["path"]
        }
    }
}


def list_files(path: str, extension: str = "") -> str:
    entries = os.listdir(os.path.expanduser(path))
    if extension:
        entries = [e for e in entries if e.endswith(extension)]
    return json.dumps(sorted(entries))
```

---

## Cron / 计划任务

在 `config.yaml` 中定义 cron 任务，以便按计划运行技能并将结果推送到通道：

```yaml
cron:
  - id: daily-digest
    schedule: "0 8 * * *"            # 每天在 08:00
    skill: get_weather
    skill_args:
      city: "Tokyo"
    channel_id: dingtalk-main         # 匹配下方的一个通道 ID
    message_template: "早上好！今天的天气: {result}"

  - id: hourly-news
    schedule: "0 * * * *"
    skill: fetch_tech_news
    channel_id: discord-main
```

---

## 本地模型设置

### Ollama

```bash
# 安装 Ollama: https://ollama.ai
ollama pull llama3.2
ollama serve   # 在 http://localhost:11434 上启动
```

```yaml
# config.yaml
providers:
  - id: ollama-local
    type: ollama
    model: llama3.2
    base_url: http://localhost:11434
```

### LM Studio

```yaml
providers:
  - id: lmstudio-local
    type: lmstudio
    model: lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF
    base_url: http://localhost:1234/v1
```

### llama.cpp（需要附加功能）

```bash
pip install "copaw[llamacpp]"
```

```yaml
providers:
  - id: llamacpp-local
    type: llamacpp
    model_path: /path/to/model.gguf
```

---

## 工具防护（安全）

工具防护会阻止有风险的工具调用，并在执行前需要用户批准。在 `config.yaml` 中配置：

```yaml
agent:
  tool_guard:
    enabled: true
    risk_patterns:
      - "rm -rf"
      - "DROP TABLE"
      - "os.system"
    auto_approve_low_risk: true
```

当调用被阻止时，控制台会显示一个批准提示。用户可以在工具运行前批准或拒绝。

---

## 令牌使用跟踪

令牌使用会自动跟踪并在控制台仪表板中可见。程序化访问：

```python
# 在技能或调试脚本中
from copaw.telemetry import get_usage_summary

summary = get_usage_summary()
print(summary)
# {'total_tokens': 142300, 'prompt_tokens': 98200, 'completion_tokens': 44100, 'by_provider': {...}}
```

---

## 环境变量

在运行 `copaw app` 前设置这些，或在 `config.yaml` 中引用它们为 `${VAR_NAME}`：

```bash
# LLM 提供者
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...

# 通道
export DINGTALK_APP_KEY=...
export DINGTALK_APP_SECRET=...
export DINGTALK_AGENT_ID=...

export FEISHU_APP_ID=...
export FEISHU_APP_SECRET=...

export DISCORD_BOT_TOKEN=...
export TELEGRAM_BOT_TOKEN=...

export QQ_UIN=...
export QQ_PASSWORD=...

export MATTERMOST_URL=...
export MATTERMOST_TOKEN=...

export MATRIX_HOMESERVER=...
export MATRIX_USER_ID=...
export MATRIX_ACCESS_TOKEN=...

# 自定义技能密钥
export OPENWEATHER_API_KEY=...
```

---

## 常见模式

### 模式：向钉钉发送每日简报

```yaml
# config.yaml 示例
channels:
  - id: dingtalk-main
    type: dingtalk
    app_key: ${DINGTALK_APP_KEY}
    app_secret: ${DINGTALK_APP_SECRET}
    agent_id: ${DINGTALK_AGENT_ID}

cron:
  - id: morning-brief
    schedule: "30 7 * * 1-5"         # 工作日 07:30
    skill: daily_briefing
    channel_id: dingtalk-main
```

```python
# skills/daily_briefing.py
SKILL_NAME = "daily_briefing"
SKILL_DESCRIPTION = "编译包含天气和新闻的每日简报"

SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": SKILL_NAME,
        "description": SKILL_DESCRIPTION,
        "parameters": {"type": "object", "properties": {}, "required": []}
    }
}

def daily_briefing() -> str:
    import os, requests, datetime

    today = datetime.date.today().strftime("%A, %B %d")
    # 在这里添加您自己的数据源
    return f"早上好！今天是 {today}。祝您工作高效！"
```

### 模式：多通道广播

```python
# skills/broadcast.py
SKILL_NAME = "broadcast_message"
SKILL_DESCRIPTION = "向所有配置的通道发送消息"

SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": SKILL_NAME,
        "description": SKILL_DESCRIPTION,
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "要广播的消息"}
            },
            "required": ["message"]
        }
    }
}

def broadcast_message(message: str) -> str:
    # CoPaw 处理路由；返回消息并让代理发送
    return f"[BROADCAST] {message}"
```

### 模式：文件总结技能

```python
# skills/summarize_file.py
SKILL_NAME = "summarize_file"
SKILL_DESCRIPTION = "读取并总结本地文件"

SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": SKILL_NAME,
        "description": SKILL_DESCRIPTION,
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "文件的绝对路径"}
            },
            "required": ["file_path"]
        }
    }
}

def summarize_file(file_path: str) -> str:
    import os

    path = os.path.expanduser(file_path)
    if not os.path.exists(path):
        return f"文件未找到: {path}"

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read(8000)

    return f"文件: {path}\n大小: {os.path.getsize(path)} 字节\n内容预览:\n{content}"
```

---

## 故障排除

### 控制台在端口 8088 上无法访问

```bash
# 使用不同端口
copaw app --port 8090

# 检查是否有其他进程使用 8088
lsof -i :8088    # macOS/Linux
netstat -ano | findstr :8088   # Windows
```

### 技能未加载

- 确认技能文件位于 `~/.copaw/workspace/skills/`
- 确认 `SKILL_NAME`、`SKILL_DESCRIPTION`、`SKILL_SCHEMA` 和处理函数都在模块级别定义
- 查看 `~/.copaw/workspace/logs/` 中的导入错误
- 添加新技能文件后重启 `copaw app`

### 通道未接收消息

1. 验证凭证设置正确（环境变量或 `config.yaml`）
2. 检查控制台 → 通道页面中的连接状态
3. 对于钉钉/飞书/Discord 的 `mention_only: true`，机器人必须被 @ 提及
4. Discord 消息超过 2000 个字符会自动拆分 — 确保机器人具有“发送消息”权限

### LLM 提供者连接失败

```bash
# 从 CLI 测试提供者（控制台 → 提供者 → 测试连接）
# 或查看日志:
tail -f ~/.copaw/workspace/logs/copaw.log
```

- 对于 Ollama：确认 `ollama serve` 正在运行且 `base_url` 匹配
- 对于兼容 OpenAI 的 API：验证 `base_url` 以 `/v1` 结尾
- LLM 调用会自动使用指数退避重试 — 暂时性故障会自动解决

### Windows 编码问题

```cmd
# 为 CMD 设置 UTF-8 编码
chcp 65001
```

或设置环境变量：
```bash
export PYTHONIOENCODING=utf-8
```

### 工作区重置

```bash
# 重新初始化工作区（保留技能/）
copaw init

# 完全重置（破坏性）
rm -rf ~/.copaw/workspace
copaw init --defaults
```

---

## ModelScope 云部署

对于无需本地设置的单击云部署：

1. 访问 [ModelScope CoPaw Studio](https://modelscope.cn/studios/fork?target=AgentScope/CoPaw)
2. 将工作室 fork 到您的账户
3. 在工作室设置中设置环境变量
4. 启动工作室 — 控制台可通过工作室 URL 访问

---

## 关键链接

- **文档**: https://copaw.agentscope.io/
- **通道设置指南**: https://copaw.agentscope.io/docs/channels
- **版本说明**: https://agentscope-ai.github.io/CoPaw/release-notes
- **GitHub**: https://github.com/agentscope-ai/CoPaw
- **PyPI**: https://pypi.org/project/copaw/
- **Discord 社区**: https://discord.gg/eYMpfnkG8h
