# MetaClaw 进化代理

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能合集

MetaClaw 是一个兼容 OpenAI 的代理代理，它可以拦截对话，注入学习到的技能，并通过现实世界的交互不断改进自身。它支持三种模式：轻量级技能注入、即时 RL 训练以及一个智能的 "madmax" 调度器，该调度器将权重更新推迟到空闲/睡眠窗口。

---

## 安装

```bash
# 最小化 — 仅技能注入，无需 GPU
pip install -e .

# 完整 RL 训练支持 (torch, transformers, tinker)
pip install -e ".[rl]"

# 通过 LLM 摘要进行技能进化
pip install -e ".[evolve]"

# Google Calendar 调度器用于 madmax 模式
pip install -e ".[scheduler]"

# 推荐：全部
pip install -e ".[rl,evolve,scheduler]"
```

---

## 快速入门

```bash
# 一次性交互式配置向导
metaclaw setup

# 以默认 madmax 模式启动（技能 + RL + 智能调度器）
metaclaw start

# 仅技能 — 无需 GPU，无需 Tinker
metaclaw start --mode skills_only

# RL 模式 — 当批次满时立即训练
metaclaw start --mode rl

# 无调度器的 RL（与上述相同，显式指定）
metaclaw start --mode rl
```

启动 `metaclaw start` 后，将运行一个本地兼容 OpenAI 的代理。将您的客户端（OpenClaw 或任何 OpenAI SDK 客户端）指向 `http://localhost:<端口>` 而不是上游 LLM 端点。

---

## 配置

`metaclaw setup` 会写入一个配置文件（默认：`~/.metaclaw/config.yaml`）。您也可以直接编辑它：

```yaml
# ~/.metaclaw/config.yaml

proxy:
  host: 0.0.0.0
  port: 8080

llm:
  provider: kimi          # kimi | qwen | claude | minimax | openai | gemini
  base_url: https://api.moonshot.cn/v1
  model: moonshot-v1-8k
  # api_key 从环境变量加载：METACLAW_LLM_API_KEY

skills:
  enabled: true
  max_injected: 5         # 每次回合注入的最大技能数
  summarize_after_session: true

rl:
  enabled: true
  backend: auto           # auto | tinker | mint
  batch_size: 32
  algorithm: grpo
  opd_teacher: false      # 可选的教师蒸馏

scheduler:                # madmax 模式仅用
  enabled: true
  sleep_hours: [22, 7]    # 本地 22:00–07:00
  idle_timeout_minutes: 15
  google_calendar: false  # 设置为 true + 配置 OAuth 以检测会议

logging:
  level: info
  log_dir: ~/.metaclaw/logs
```

### 环境变量

```bash
export METACLAW_LLM_API_KEY="your-llm-api-key"
export METACLAW_TINKER_API_KEY="your-tinker-api-key"   # RL 模式
export METACLAW_MINT_API_KEY="your-mint-api-key"        # 如果 backend=mint
export GOOGLE_CALENDAR_CREDENTIALS_PATH="path/to/creds.json"  # 调度器
```

---

## 运行模式

| 模式 | 命令 | 需要 GPU | 描述 |
|------|---------|--------------|-------------|
| `skills_only` | `metaclaw start --mode skills_only` | 否 | 代理 + 技能注入 + 自动摘要 |
| `rl` | `metaclaw start --mode rl` | 通过 API | 技能 + GRPO 训练当批次满时 |
| `madmax` | `metaclaw start` | 通过 API | 技能 + RL + 调度器（仅在空闲/睡眠/会议期间训练） |

---

## Python API

### 程序化启动

```python
import asyncio
from metaclaw import MetaClawAgent, AgentConfig, Mode

async def main():
    config = AgentConfig.from_yaml("~/.metaclaw/config.yaml")
    agent = MetaClawAgent(config, mode=Mode.MADMAX)
    await agent.start()

asyncio.run(main())
```

### 手动技能注入

```python
from metaclaw.skills import SkillStore, SkillInjector

store = SkillStore(path="~/.metaclaw/skills")

# 手动添加一个技能
store.add(
    name="code-review-checklist",
    content="始终检查：1) 错误处理，2) 类型提示，3) 文档字符串。",
    tags=["code", "review"]
)

# 获取与查询最相关的技能
injector = SkillInjector(store)
relevant = injector.retrieve(query="review my Python function", top_k=3)
for skill in relevant:
    print(skill.name, skill.score)
```

### 拦截和记录对话

```python
from metaclaw.proxy import ConversationInterceptor
from metaclaw.memory import ExperienceBuffer

buffer = ExperienceBuffer(max_size=1000)

interceptor = ConversationInterceptor(
    upstream_url="https://api.moonshot.cn/v1",
    on_complete=buffer.record   # 每次回合后调用，参数为 (messages, response)
)

# buffer.record 签名：
async def on_complete(messages: list[dict], response: dict) -> None:
    ...
```

### 手动触发 RL 训练

```python
from metaclaw.training import RLTrainer, TrainingConfig

trainer = RLTrainer(
    config=TrainingConfig(
        backend="tinker",       # 或 "mint"
        algorithm="grpo",
        batch_size=32,
        lora_rank=16,
    )
)

# 从经验缓冲区收集一批数据并训练
async def run_training(buffer):
    batch = buffer.sample(n=32, split="support")   # 支持集/查询集分离
    result = await trainer.train(batch)
    print(f"训练完成。损失：{result.loss:.4f}，步数：{result.steps}")
```

### 奖励建模

```python
from metaclaw.rewards import RewardModel

reward_model = RewardModel(provider="llm")  # 使用配置的 LLM 进行评分

async def score_turn(prompt: str, response: str) -> float:
    score = await reward_model.score(prompt=prompt, response=response)
    return score  # 分数范围 [-1.0, 1.0]
```

---

## 技能生命周期

```
对话回合
       │
       ▼
 SkillInjector.retrieve()   ← 在 SkillStore 上进行向量搜索
       │  将 top-k 技能注入系统提示
       ▼
 LLM 响应
       │
       ▼
 ExperienceBuffer.record()  ← 存储 (上下文, 响应, 元数据)
       │
       ▼ (会话结束)
 SkillSummarizer.run()      ← LLM 提取可重用模式
       │
       ▼
 SkillStore.upsert()        ← 新/更新的技能持久化到磁盘
```

---

## 集成：OpenAI SDK 作为客户端

将任何 OpenAI SDK 客户端指向 MetaClaw 代理：

```python
from openai import OpenAI

# MetaClaw 代理运行在 localhost:8080
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-used-but-required-by-sdk"
)

response = client.chat.completions.create(
    model="moonshot-v1-8k",   # 传递给上游
    messages=[
        {"role": "user", "content": "Review my pull request strategy."}
    ]
)
print(response.choices[0].message.content)
```

技能透明注入 — 客户端代码无需更改。

---

## 调度器（MadMax 模式）

调度器确保 RL 权重更新不会中断活动使用：

```python
from metaclaw.scheduler import MadMaxScheduler, SchedulerConfig

scheduler = MadMaxScheduler(
    config=SchedulerConfig(
        sleep_hours=(22, 7),          # 本地时间 22:00–07:00 间训练
        idle_timeout_minutes=15,      # 无对话 15 分钟后训练
        google_calendar=True,         # 也在日历会议期间训练
        credentials_path="creds.json"
    )
)

# 检查是否可以安全训练
if await scheduler.is_training_window():
    await trainer.train(batch)
```

### Google Calendar 设置

```bash
# 1. 在 Google Cloud Console 中启用 Google Calendar API
# 2. 下载 OAuth2 凭证作为 creds.json
# 3. 在配置或环境变量中设置路径
export GOOGLE_CALENDAR_CREDENTIALS_PATH="/path/to/creds.json"

# 4. 首次运行将打开浏览器进行 OAuth 同意
metaclaw start
```

---

## 支持集/查询集分离

MetaClaw 将经验分为支持和查询集，以防止过时的奖励污染更新：

```python
from metaclaw.memory import ExperienceBuffer

buffer = ExperienceBuffer(
    max_size=2000,
    support_ratio=0.5   # 50% 支持，50% 查询
)

# 训练期间：
support_batch = buffer.sample(n=16, split="support")  # 用于计算奖励信号
query_batch   = buffer.sample(n=16, split="query")    # 用于梯度更新

await trainer.train_meta(support=support_batch, query=query_batch)
```

---

## RL 后端

### Tinker（默认）

```yaml
rl:
  backend: tinker
  tinker_project: my-metaclaw-project
  lora_rank: 16
  learning_rate: 1e-4
```

### MinT

```bash
# 单独安装 MinT 兼容层
pip install metaclaw-mint
```

```yaml
rl:
  backend: mint
  mint_endpoint: https://your-mint-endpoint
```

### 自动检测

```yaml
rl:
  backend: auto   # 首先尝试 Tinker，如果不可用则回退到 Mint，如果两者都不可用则报错
```

---

## 故障排除

**启动 `metaclaw start` 后代理无法访问**
- 检查端口冲突：`lsof -i :8080`
- 修改 `proxy.port` 在配置中并重启

**`rl` 模式："没有可用的训练后端"**
- 确保 `pip install -e ".[rl]"` 成功完成
- 验证 `METACLAW_TINKER_API_KEY` 或 `METACLAW_MINT_API_KEY` 是否已设置
- 尝试显式指定 `rl.backend: tinker` 而不是 `auto`

**技能在会话之间不持久化**
- 确认 `skills.summarize_after_session: true` 在配置中
- 检查 `~/.metaclaw/skills/` 的写权限
- 运行 `metaclaw skills list` 检查存储的技能

**Madmax 模式从未训练**
- 验证 `scheduler.sleep_hours` 是否覆盖您的时区的夜间时间
- 降低 `scheduler.idle_timeout_minutes` 进行测试（例如，`1`）
- 检查调度器日志：`~/.metaclaw/logs/scheduler.log`

**Google Calendar 集成失败**
- 重新运行 OAuth 流程：删除 `~/.metaclaw/token.json` 并重启
- 确保在您的 Google Cloud 项目中启用了日历 API

**OPD 教师蒸馏错误**
- 仅支持 `rl.backend: tinker`
- 需要在配置中设置一个单独的教师模型端点：
  ```yaml
  rl:
    opd_teacher: true
    teacher_base_url: https://api.openai.com/v1
    teacher_model: gpt-4o
  ```

---

## CLI 参考

```bash
metaclaw setup                   # 交互式配置向导
metaclaw start                   # 以 madmax 模式启动
metaclaw start --mode skills_only
metaclaw start --mode rl
metaclaw start --config path/to/config.yaml

metaclaw skills list             # 显示所有存储的技能
metaclaw skills delete <name>    # 删除一个技能
metaclaw skills export skills.json

metaclaw status                  # 显示代理、调度器、训练状态
metaclaw logs                    # 尾部所有日志
metaclaw logs --component scheduler
```
