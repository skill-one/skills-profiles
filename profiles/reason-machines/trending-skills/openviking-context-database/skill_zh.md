# OpenViking 上下文数据库

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能合集。

OpenViking 是一个用于 AI 代理的开源**上下文数据库**，它用统一的**文件系统范式**取代了碎片化的向量存储。它以 L0/L1/L2 的分层结构管理代理内存、资源和技能，实现分层上下文交付、可观察的检索轨迹以及自演化的会话记忆。

---

## 安装

### Python 包

```bash
pip install openviking --upgrade --force-reinstall
```

### 可选的 Rust CLI

```bash
# 通过脚本安装
curl -fsSL https://raw.githubusercontent.com/volcengine/OpenViking/main/crates/ov_cli/install.sh | bash

# 或从源代码构建（需要 Rust 工具链）
cargo install --git https://github.com/volcengine/OpenViking ov_cli
```

### 先决条件

- Python 3.10+
- Go 1.22+（用于 AGFS 组件）
- GCC 9+ 或 Clang 11+（用于核心扩展）

---

## 配置

创建 `~/.openviking/ov.conf`：

```json
{
  "storage": {
    "workspace": "/home/user/openviking_workspace"
  },
  "log": {
    "level": "INFO",
    "output": "stdout"
  },
  "embedding": {
    "dense": {
      "api_base": "https://api.openai.com/v1",
      "api_key": "$OPENAI_API_KEY",
      "provider": "openai",
      "dimension": 1536,
      "model": "text-embedding-3-large"
    },
    "max_concurrent": 10
  },
  "vlm": {
    "api_base": "https://api.openai.com/v1",
    "api_key": "$OPENAI_API_KEY",
    "provider": "openai",
    "model": "gpt-4o",
    "max_concurrent": 100
  }
}
```

> **注意**：OpenViking 将 `api_key` 值作为字符串读取；请在启动时使用环境变量注入，而不是字面量密钥。

### 提供商选项

| 角色 | 提供商值 | 示例模型 |
|------|----------|----------|
| VLM | `openai` | `gpt-4o` |
| VLM | `volcengine` | `doubao-seed-2-0-pro-260215` |
| VLM | `litellm` | `claude-3-5-sonnet-20240620`, `ollama/llama3.1` |
| 嵌入 | `openai` | `text-embedding-3-large` |
| 嵌入 | `volcengine` | `doubao-embedding-vision-250615` |
| 嵌入 | `jina` | `jina-embeddings-v3` |

### LiteLLM VLM 示例

```json
{
  "vlm": {
    "provider": "litellm",
    "model": "claude-3-5-sonnet-20240620",
    "api_key": "$ANTHROPIC_API_KEY"
  }
}
```

```json
{
  "vlm": {
    "provider": "litellm",
    "model": "ollama/llama3.1",
    "api_base": "http://localhost:11434"
  }
}
```

```json
{
  "vlm": {
    "provider": "litellm",
    "model": "deepseek-chat",
    "api_key": "$DEEPSEEK_API_KEY"
  }
}
```

---

## 核心概念

### 文件系统范式

OpenViking 将代理上下文组织得像文件系统：

```
workspace/
├── memories/          # 长期代理记忆（L0 始终加载）
│   ├── user_prefs/
│   └── task_history/
├── resources/         # 外部知识、文档（L1 按需加载）
│   ├── codebase/
│   └── docs/
└── skills/            # 可复用的代理能力（L2 检索）
    ├── coding/
    └── analysis/
```

### 分层上下文加载（L0/L1/L2）

- **L0**：始终加载 — 核心身份、持久化偏好
- **L1**：按需加载 — 每个任务检索相关资源
- **L2**：语义检索 — 通过相似性搜索拉取技能

这种分层方法在最小化 token 消耗的同时最大化上下文相关性。

---

## Python API 使用

### 基本设置

```python
import os
from openviking import OpenViking

# 使用配置文件初始化
ov = OpenViking(config_path="~/.openviking/ov.conf")

# 或程序化初始化
ov = OpenViking(
    workspace="/home/user/openviking_workspace",
    vlm_provider="openai",
    vlm_model="gpt-4o",
    vlm_api_key=os.environ["OPENAI_API_KEY"],
    embedding_provider="openai",
    embedding_model="text-embedding-3-large",
    embedding_api_key=os.environ["OPENAI_API_KEY"],
    embedding_dimension=1536,
)
```

### 管理上下文命名空间（代理大脑）

```python
# 创建或打开命名空间（像代理的文件系统根目录）
brain = ov.namespace("my_agent")

# 添加记忆文件
brain.write("memories/user_prefs.md", """
# 用户偏好
- 语言：Python
- 代码风格：PEP8
- 优先框架：FastAPI
""")

# 添加资源文档
brain.write("resources/api_docs/stripe.md", open("stripe_docs.md").read())

# 添加技能
brain.write("skills/coding/write_tests.md", """
# 技能：编写单元测试
当被要求编写测试时，使用 pytest 并配合 fixtures。
始终模拟外部 API 调用。目标覆盖率 80%+。
""")
```

### 查询上下文

```python
# 跨命名空间语义搜索
results = brain.search("用户如何偏好代码格式？")
for result in results:
    print(result.path, result.score, result.content[:200])

# 目录范围检索（递归）
skill_results = brain.search(
    query="为 FastAPI 端点编写单元测试",
    directory="skills/",
    top_k=3,
)

# 直接路径读取（L0 始终可用）
prefs = brain.read("memories/user_prefs.md")
print(prefs.content)
```

### 会话记忆与自动压缩

```python
# 开始会话 — OpenViking 跟踪回合并自动压缩
session = brain.session("task_build_api")

# 添加对话回合
session.add_turn(role="user", content="为我构建一个用于待办事项的 REST API")
session.add_turn(role="assistant", content="我会创建一个带有 CRUD 操作的 FastAPI 应用...")

# 在许多回合后，触发压缩以提取长期记忆
summary = session.compress()
# 压缩后的见解会自动写入 memories/

# 结束会话 — 持久化提取的记忆
session.close()
```

### 检索轨迹（可观察的 RAG）

```python
# 启用轨迹跟踪以观察检索决策
with brain.observe() as tracker:
    results = brain.search("认证最佳实践")

trajectory = tracker.trajectory()
for step in trajectory.steps:
    print(f"[{step.level}] {step.path} → score={step.score:.3f}")
    # 输出：
    # [L0] memories/user_prefs.md → score=0.82
    # [L1] resources/security/auth.md → score=0.91
    # [L2] skills/coding/jwt_auth.md → score=0.88
```

---

## 常见模式

### 模式 1：具有持久记忆的代理

```python
import os
from openviking import OpenViking

ov = OpenViking(config_path="~/.openviking/ov.conf")
brain = ov.namespace("coding_agent")

def agent_respond(user_message: str, conversation_history: list) -> str:
    # 检索相关上下文
    context_results = brain.search(user_message, top_k=5)
    context_text = "\n\n".join(r.content for r in context_results)
    
    # 使用检索到的上下文构建提示
    system_prompt = f"""你是一个代码助手。

## 相关上下文
{context_text}
"""
    # ... 在这里调用你的 LLM，使用 system_prompt + conversation_history
    response = call_llm(system_prompt, conversation_history, user_message)
    
    # 存储交互以供未来记忆
    brain.session("current").add_turn("user", user_message)
    brain.session("current").add_turn("assistant", response)
    
    return response
```

### 模式 2：分层技能加载

```python
# 从目录结构注册技能
import pathlib

skills_dir = pathlib.Path("./agent_skills")
for skill_file in skills_dir.rglob("*.md"):
    relative = skill_file.relative_to(skills_dir)
    brain.write(f"skills/{relative}", skill_file.read_text())

# 运行时仅检索相关技能
def get_relevant_skills(task: str) -> list[str]:
    results = brain.search(task, directory="skills/", top_k=3)
    return [r.content for r in results]

task = "重构这个类以使用依赖注入"
skills = get_relevant_skills(task)
# 仅返回与 DI 相关的技能，而不是所有注册的技能
```

### 模式 3：代码库上的 RAG

```python
import subprocess
import pathlib

brain = ov.namespace("codebase_agent")

# 索引代码库
def index_codebase(repo_path: str):
    for f in pathlib.Path(repo_path).rglob("*.py"):
        content = f.read_text(errors="ignore")
        # 使用相对路径作为键存储
        rel = f.relative_to(repo_path)
        brain.write(f"resources/codebase/{rel}", content)

index_codebase("/home/user/myproject")

# 使用目录范围查询
def find_relevant_code(query: str) -> list:
    return brain.search(
        query=query,
        directory="resources/codebase/",
        top_k=5,
    )

hits = find_relevant_code("数据库连接池")
for h in hits:
    print(h.path, "\n", h.content[:300])
```

### 模式 4：多代理共享上下文

```python
# 代理 1 写入发现
agent1_brain = ov.namespace("researcher_agent")
agent1_brain.write("memories/findings/api_rate_limits.md", """
# 发现的 API 速率限制
- Stripe：在线模式 100 req/s
- SendGrid：600 req/min
""")

# 代理 2 读取共享工作区发现
agent2_brain = ov.namespace("coder_agent")
# 跨命名空间读取（如果允许）
shared = ov.namespace("shared_knowledge")
rate_limits = shared.read("memories/findings/api_rate_limits.md")
```

---

## CLI 命令（ov_cli）

```bash
# 检查版本
ov --version

# 列出命名空间
ov namespace list

# 创建命名空间
ov namespace create my_agent

# 写入上下文文件
ov write my_agent/memories/prefs.md --file ./prefs.md

# 读取文件
ov read my_agent/memories/prefs.md

# 搜索上下文
ov search my_agent "如何处理认证" --top-k 5

# 显示查询的检索轨迹
ov search my_agent "数据库迁移" --trace

# 压缩会话
ov session compress my_agent/task_build_api

# 列出命名空间中的文件
ov ls my_agent/skills/

# 删除上下文文件
ov rm my_agent/resources/outdated_docs.md

# 将命名空间导出到本地目录
ov export my_agent ./exported_brain/

# 从本地目录导入
ov import ./exported_brain/ my_agent_restored
```

---

## 故障排除

### 配置未找到

```bash
# 验证配置位置
ls -la ~/.openviking/ov.conf

# OpenViking 也检查 OV_CONFIG 环境变量
export OV_CONFIG=/path/to/custom/ov.conf
```

### 嵌入维度不匹配

如果你切换嵌入模型，存储的向量维度将发生冲突：

```python
# 检查当前维度设置与存储索引
# 解决方案：模型更改后重新索引
brain.reindex(force=True)
```

### 工作区权限错误

```bash
# 确保工作区目录可写
chmod -R 755 /home/user/openviking_workspace

# 检查磁盘空间（嵌入索引可能很大）
df -h /home/user/openviking_workspace
```

### LiteLLM 提供商未检测到

```python
# 使用明确的前缀以避免歧义
{
  "vlm": {
    "provider": "litellm",
    "model": "openrouter/anthropic/claude-3-5-sonnet",  # 需要完整前缀
    "api_key": "$OPENROUTER_API_KEY",
    "api_base": "https://openrouter.ai/api/v1"
  }
}
```

### 高 token 使用量

启用分层加载以减少 L1/L2 获取：

```python
# 紧密范围搜索以避免过度获取
results = brain.search(
    query=user_message,
    directory="skills/relevant_domain/",  # 狭窄范围
    top_k=2,                               # 更少的结果
    min_score=0.75,                        # 质量阈值
)
```

### 大型代码库索引缓慢

```python
# 在配置中增加并发
{
  "embedding": {
    "max_concurrent": 20  # 从默认 10 增加到
  },
  "vlm": {
    "max_concurrent": 50
  }
}

# 或使用异步批量写入
import asyncio

async def index_async(files):
    tasks = [brain.awrite(f"resources/{p}", c) for p, c in files]
    await asyncio.gather(*tasks)
```

---

## 环境变量参考

| 变量 | 目的 |
|------|------|
| `OV_CONFIG` | `ov.conf` 路径覆盖 |
| `OPENAI_API_KEY` | OpenAI API 密钥（用于 VLM/嵌入） |
| `ANTHROPIC_API_KEY` | 通过 LiteLLM 的 Anthropic Claude |
| `DEEPSEEK_API_KEY` | 通过 LiteLLM 的 DeepSeek |
| `GEMINI_API_KEY` | 通过 LiteLLM 的 Google Gemini |
| `OV_LOG_LEVEL` | 覆盖日志级别（`DEBUG`, `INFO`, `WARN`） |
| `OV_WORKSPACE` | 覆盖工作区路径 |

---

## 资源

- **网站**：https://openviking.ai
- **文档**：https://www.openviking.ai/docs
- **GitHub**：https://github.com/volcengine/OpenViking
- **问题**：https://github.com/volcengine/OpenViking/issues
- **Discord**：https://discord.com/invite/eHvx8E9XF3
- **LiteLLM 提供商**：https://docs.litellm.ai/docs/providers
