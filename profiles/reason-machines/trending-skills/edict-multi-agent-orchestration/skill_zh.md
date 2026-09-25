# Edict (三省六部) 多智能体编排

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能合集。

Edict 实现了 1400 多年前的唐朝治理模型作为 AI 多智能体架构。十二个专业智能体形成一个制衡流程：皇太子（分诊）→ 中书省（规划）→ 门下省（审核/否决）→ 尚书省（调度）→ 六部（并行执行）。基于 [OpenClaw](https://openclaw.ai) 构建，它提供实时 React 看板仪表板、完整审计追踪和每个智能体的 LLM 配置。

---

## 架构概述

```
你（皇帝）→ taizi（分诊）→ zhongshu（规划）→ menxia（审核/否决）
             → shangshu（调度）→ [hubu|libu|bingbu|xingbu|gongbu|libu2]（执行）
             → memorial（结果存档）
```

**与 CrewAI/AutoGen 的关键区别**：门下省（Menxia）是一个强制性的质量关卡 — 它可以否决并强制返工，任务在到达执行者之前。

---

## 前置条件

- 安装并运行 [OpenClaw](https://openclaw.ai)
- Python 3.9+
- Node.js 18+（用于 React 仪表板构建）
- macOS 或 Linux

---

## 安装

### 快速演示（Docker — 无需 OpenClaw）

```bash
# x86/amd64 (Ubuntu, WSL2)
docker run --platform linux/amd64 -p 7891:7891 cft0808/sansheng-demo

# Apple Silicon / ARM
docker run -p 7891:7891 cft0808/sansheng-demo

# 或使用 docker-compose（平台已设置）
docker compose up
```

打开 http://localhost:7891

### 完整安装

```bash
git clone https://github.com/cft0808/edict.git
cd edict
chmod +x install.sh && ./install.sh
```

安装脚本自动：
- 创建所有 12 个智能体工作区（taizi、zhongshu、menxia、shangshu、hubu、libu、bingbu、xingbu、gongbu、libu2、zaochao、legacy-compat）
- 将 SOUL.md 角色定义写入每个智能体工作区
- 在 `openclaw.json` 中注册智能体和权限矩阵
- 在所有智能体工作区之间创建共享数据目录的符号链接
- 设置 `sessions.visibility all` 用于智能体间消息路由
- 在所有智能体间同步 API 密钥
- 构建 React 前端
- 初始化数据目录并同步官方统计数据

### 首次 API 密钥设置

```bash
# 在第一个智能体上配置 API 密钥
openclaw agents add taizi
# 然后重新运行 install 来传播到所有智能体
./install.sh
```

---

## 运行系统

```bash
# 终端 1：数据刷新循环（保持看板数据最新）
bash scripts/run_loop.sh

# 终端 2：仪表板服务器
python3 dashboard/server.py

# 打开仪表板
open http://127.0.0.1:7891
```

---

## 关键命令

### OpenClaw 智能体管理

```bash
# 列出所有注册的智能体
openclaw agents list

# 添加/配置一个智能体
openclaw agents add <agent-name>

# 检查智能体状态
openclaw agents status

# 重启网关（配置更改后需要）
openclaw gateway restart

# 向系统发送消息/法令
openclaw send taizi "帮我分析一下竞争对手的产品策略"
```

### 仪表板服务器

```python
# dashboard/server.py — 在端口 7891 上提供服务
# 内置：React 前端 + REST API + WebSocket 更新
python3 dashboard/server.py

# 自定义端口
PORT=8080 python3 dashboard/server.py
```

### 数据脚本

```bash
# 同步官方（智能体）统计数据
python3 scripts/sync_officials.py

# 更新看板任务状态
python3 scripts/kanban_update.py

# 运行新闻聚合
python3 scripts/fetch_news.py

# 全部刷新循环（按顺序运行所有脚本）
bash scripts/run_loop.sh
```

---

## 配置

### 智能体模型配置 (`openclaw.json`)

```json
{
  "agents": {
    "taizi": {
      "model": "claude-3-5-sonnet-20241022",
      "workspace": "~/.openclaw/workspaces/taizi"
    },
    "zhongshu": {
      "model": "gpt-4o",
      "workspace": "~/.openclaw/workspaces/zhongshu"
    },
    "menxia": {
      "model": "claude-3-5-sonnet-20241022",
      "workspace": "~/.openclaw/workspaces/menxia"
    },
    "shangshu": {
      "model": "gpt-4o-mini",
      "workspace": "~/.openclaw/workspaces/shangshu"
    }
  },
  "gateway": {
    "port": 7891,
    "sessions": {
      "visibility": "all"
    }
  }
}
```

### 每个智能体模型热切换（通过仪表板）

导航到 **⚙️ 模型** 面板 → 选择智能体 → 选择 LLM → 应用。网关会自动重启（约 5 秒）。

### 环境变量

```bash
# API 密钥（在运行 install.sh 或 openclaw 之前设置）
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# 可选：飞书/钉钉 webhook 用于通知
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/..."

# 可选：新闻聚合
export NEWS_API_KEY="..."

# 仪表板端口覆盖
export DASHBOARD_PORT=7891
```

---

## 智能体角色参考

| 智能体 | 角色 | 职责 |
|-------|------|------|
| `taizi` | 太子 | 分诊：聊天 → 自动回复，法令 → 创建任务 |
| `zhongshu` | 中书省 | 规划：将法令分解为子任务 |
| `menxia` | 门下省 | **审核/否决**：质量关卡，可以拒绝并强制返工 |
| `shangshu` | 尚书省 | 调度：将子任务分配给部门 |
| `hubu` | 户部 | 财政、数据分析任务 |
| `libu` | 礼部 | 沟通、文档任务 |
| `bingbu` | 兵部 | 战略、安全任务 |
| `xingbu` | 刑部 | 审核、合规任务 |
| `gongbu` | 工部 | 工程、技术任务 |
| `libu2` | 吏部 | 人力资源、智能体管理任务 |
| `zaochao` | 早朝官 | 早晨简报聚合 |

### 权限矩阵（谁可以向谁发送消息）

```python
# 定义在 openclaw.json 中 — 由网关强制执行
PERMISSIONS = {
    "taizi":    ["zhongshu"],
    "zhongshu": ["menxia"],
    "menxia":   ["zhongshu", "shangshu"],  # 可以否决回中书省
    "shangshu": ["hubu", "libu", "bingbu", "xingbu", "gongbu", "libu2"],
    # 部门向上级汇报
    "hubu":     ["shangshu"],
    "libu":     ["shangshu"],
    "bingbu":   ["shangshu"],
    "xingbu":   ["shangshu"],
    "gongbu":   ["shangshu"],
    "libu2":    ["shangshu"],
}
```

---

## 任务状态机

```python
# scripts/kanban_update.py 强制执行有效转换
VALID_TRANSITIONS = {
    "pending":     ["planning"],
    "planning":    ["reviewing", "pending"],      # zhongshu → menxia
    "reviewing":   ["dispatching", "planning"],   # menxia 批准或否决
    "dispatching": ["executing"],
    "executing":   ["completed", "failed"],
    "completed":   [],
    "failed":      ["pending"],  # 重试
}

# 无效转换会被拒绝 — 无状态损坏的静默错误
```

---

## 实际代码示例

### 编程发送法令

```python
import subprocess
import json

def send_edict(message: str, agent: str = "taizi") -> dict:
    """向皇太子发送法令进行分诊。"""
    result = subprocess.run(
        ["openclaw", "send", agent, message],
        capture_output=True,
        text=True
    )
    return {"stdout": result.stdout, "returncode": result.returncode}

# 示例法令
send_edict("分析本季度用户增长数据，找出关键驱动因素")
send_edict("起草一份关于产品路线图的对外公告")
send_edict("审查现有代码库的安全漏洞")
```

### 读取看板状态

```python
import json
from pathlib import Path

def get_kanban_tasks(data_dir: str = "data") -> list[dict]:
    """读取当前看板任务状态。"""
    tasks_file = Path(data_dir) / "tasks.json"
    if not tasks_file.exists():
        return []
    with open(tasks_file) as f:
        return json.load(f)

def get_tasks_by_status(status: str) -> list[dict]:
    tasks = get_kanban_tasks()
    return [t for t in tasks if t.get("status") == status]

# 使用
executing = get_tasks_by_status("executing")
completed = get_tasks_by_status("completed")
print(f"进行中：{len(executing)}，已完成：{len(completed)}")
```

### 更新任务状态（带验证）

```python
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

VALID_TRANSITIONS = {
    "pending":     ["planning"],
    "planning":    ["reviewing", "pending"],
    "reviewing":   ["dispatching", "planning"],
    "dispatching": ["executing"],
    "executing":   ["completed", "failed"],
    "completed":   [],
    "failed":      ["pending"],
}

def update_task_status(task_id: str, new_status: str, data_dir: str = "data") -> bool:
    """使用状态机验证更新任务状态。"""
    tasks_file = Path(data_dir) / "tasks.json"
    tasks = json.loads(tasks_file.read_text())

    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    current = task["status"]
    allowed = VALID_TRANSITIONS.get(current, [])

    if new_status not in allowed:
        raise ValueError(
            f"无效转换：{current} → {new_status}. "
            f"允许的：{allowed}"
        )

    task["status"] = new_status
    task["updated_at"] = datetime.now(timezone.utc).isoformat()
    task.setdefault("history", []).append({
        "from": current,
        "to": new_status,
        "timestamp": task["updated_at"]
    })

    tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))
    return True
```

### 仪表板 REST API 客户端

```python
import urllib.request
import json

BASE_URL = "http://127.0.0.1:7891/api"

def api_get(endpoint: str) -> dict:
    with urllib.request.urlopen(f"{BASE_URL}{endpoint}") as resp:
        return json.loads(resp.read())

def api_post(endpoint: str, data: dict) -> dict:
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# 读取仪表板数据
tasks    = api_get("/tasks")
agents   = api_get("/agents")
sessions = api_get("/sessions")
news     = api_get("/news")

# 触发任务操作
api_post("/tasks/pause",  {"task_id": "task-123"})
api_post("/tasks/cancel", {"task_id": "task-123"})
api_post("/tasks/resume", {"task_id": "task-123"})

# 切换智能体模型
api_post("/agents/model", {
    "agent": "zhongshu",
    "model": "gpt-4o-2024-11-20"
})
```

### 智能体健康检查

```python
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

def check_agent_health(data_dir: str = "data") -> dict[str, str]:
    """
    返回每个智能体的健康状态。
    🟢 active   = 2 分钟内的心跳
    🟡 stale    = 2-10 分钟前的心跳
    🔴 offline  = 10 分钟前或缺失的心跳
    """
    heartbeats_file = Path(data_dir) / "heartbeats.json"
    if not heartbeats_file.exists():
        return {}

    heartbeats = json.loads(heartbeats_file.read_text())
    now = datetime.now(timezone.utc)
    status = {}

    for agent, last_beat in heartbeats.items():
        last = datetime.fromisoformat(last_beat)
        delta = now - last
        if delta < timedelta(minutes=2):
            status[agent] = "🟢 active"
        elif delta < timedelta(minutes=10):
            status[agent] = "🟡 stale"
        else:
            status[agent] = "🔴 offline"

    return status

# 使用
health = check_agent_health()
for agent, s in health.items():
    print(f"{agent:12} {s}")
```

### 自定义 SOUL.md（智能体个性）

```markdown
<!-- ~/.openclaw/workspaces/gongbu/SOUL.md -->
# 工部尚书 · Minister of Works

## 角色
你是工部尚书。你处理尚书省分配的所有技术、工程和基础设施任务。

## 规则
1. 始终将技术任务分解为具体、可验证的步骤
2. 返回结构化结果：{ "status": "...", "output": "...", "artifacts": [] }
3. 立即标记阻塞项 — 不要静默失败
4. 在开始前估算复杂度：S/M/L/XL

## 输出格式
始终以有效 JSON 响应。包含 ≤ 50 字符的 `summary` 字段用于看板显示。
```

---

## 仪表板面板

| 面板 | URL 片段 | 关键功能 |
|------|----------|----------|
| 看板 | `#kanban` | 任务列、心跳徽章、筛选/搜索、暂停/取消/恢复 |
| 监控 | `#monitor` | 智能体健康卡片、任务分布图表 |
| 纪要 | `#memorials` | 已完成任务存档、5 阶段时间线、Markdown 导出 |
| 模板 | `#templates` | 9 个预设法令模板带参数表单 |
| 官员 | `#officials` | 令牌使用排名、活动统计 |
| 新闻 | `#news` | 每日科技/财经简报、飞书推送 |
| 模型 | `#models` | 每个智能体 LLM 切换器（热加载 ~5s） |
| 技能 | `#skills` | 查看添加智能体技能 |
| 会话 | `#sessions` | 实时 OC-* 会话监控 |
| 朝廷 | `#court` | 围绕主题的多智能体讨论 |

---

## 常见模式

### 模式 1：并行部门执行

```python
# 尚书省同时调度到多个部门
# 每个部门独立工作；尚书省汇总结果
edict = "竞品分析：研究 TOP3 竞争对手的产品、定价、市场策略"

# Zhongshu 分解为子任务：
# hubu  → 定价分析
# libu  → 市场沟通分析
# bingbu → 竞争策略分析
# gongbu → 技术功能比较

# 所有并行执行；尚书省等待所有 4 个，然后汇总
```

### 模式 2：门下省否决循环

```python
# 如果门下省否决中书省的计划：
# menxia → zhongshu: "子任务拆解不完整，缺少风险评估维度，请补充"
# zhongshu 修订并重新提交给门下省
# 循环继续直到门下省批准
# openclaw.json 中可配置最大审核轮次："max_review_cycles": 3
```

### 模式 3：新闻聚合 + 推送

```python
# scripts/fetch_news.py → data/news.json → dashboard #news 面板
# 可选：飞书推送：
import os, json, urllib.request

def push_to_feishu(summary: str):
    webhook = os.environ["FEISHU_WEBHOOK_URL"]
    payload = json.dumps({
        "msg_type": "text",
        "content": {"text": f"📰 天下要闻\n{summary}"}
    }).encode()
    req = urllib.request.Request(
        webhook, data=payload,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)
```

---

## 故障排除

### Docker 中的 `exec format error`

```bash
# 强制 x86/amd64 平台
docker run --platform linux/amd64 -p 7891:7891 cft0808/sansheng-demo
```

### 智能体未接收消息

```bash
# 确保会话可见性设置为 "all"
openclaw config set sessions.visibility all
openclaw gateway restart
# 或重新运行 install.sh — 它会自动设置此值
./install.sh
```

### API 密钥未传播到所有智能体

```bash
# 在第一个智能体上配置密钥后重新运行 install
openclaw agents add taizi  # 在此处配置密钥
./install.sh               # 传播到所有智能体
```

### 仪表板显示陈旧数据

```bash
# 确保 run_loop.sh 正在运行
bash scripts/run_loop.sh

# 或触发手动刷新
python3 scripts/sync_officials.py
python3 scripts/kanban_update.py
```

### React 前端未构建

```bash
# 需要 Node.js 18+
cd dashboard/frontend
npm install && npm run build
# server.py 将提供构建的静态资源
```

### 无效状态转换错误

```python
# kanban_update.py 强制状态机
# 更新前检查当前状态：
tasks = get_kanban_tasks()
task = next(t for t in tasks if t["id"] == "your-task-id")
print(f"当前：{task['status']}")
print(f"允许的下一步：{VALID_TRANSITIONS[task['status']]}")
```

### 模型更改后的网关重启

```bash
# 编辑 openclaw.json 模型部分后
openclaw gateway restart
# 等待 ~5 秒让智能体重新连接
```

---

## 项目结构

```
edict/
├── install.sh              # 一键安装
├── openclaw.json           # 智能体注册 + 权限 + 模型配置
├── scripts/
│   ├── run_loop.sh         # 持续数据刷新守护进程
│   ├── kanban_update.py    # 状态机强制执行
│   ├── sync_officials.py   # 智能体统计数据聚合
│   └── fetch_news.py       # 新闻聚合
├── dashboard/
│   ├── server.py           # 仅使用标准库的 HTTP + WebSocket 服务器（端口 7891）
│   ├── dashboard.html      # 降级单文件仪表板
│   └── frontend/           # React 18 源代码（构建为 server.py 资源）
├── data/                   # 共享数据（符号链接到所有智能体工作区）
│   ├── tasks.json
│   ├── heartbeats.json
│   ├── news.json
│   └── officials.json
├── workspaces/             # 每个智能体工作区根目录
│   ├── taizi/SOUL.md
│   ├── zhongshu/SOUL.md
│   └── ...
└── docs/
    ├── task-dispatch-architecture.md
    └── getting-started.md
```
