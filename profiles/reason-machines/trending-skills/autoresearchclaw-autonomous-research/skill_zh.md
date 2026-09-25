# AutoResearchClaw — 自主研究流程

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能合集。

AutoResearchClaw 是一个完全自主的23阶段研究流程，它将自然语言主题转化为一篇完整的学术论文：真实的arXiv/Semantic Scholar引用、沙盒化实验、统计分析、多智能体同行评审，以及适用于会议的LaTeX（NeurIPS/ICML/ICLR）。没有幻觉的参考文献。无需人工监督。

---

## 安装

```bash
# 克隆并安装
git clone https://github.com/aiming-lab/AutoResearchClaw.git
cd AutoResearchClaw
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# 验证CLI是否可用
researchclaw --help
```

**要求：** Python 3.11+

---

## 配置

```bash
cp config.researchclaw.example.yaml config.arc.yaml
```

### 最小配置 (`config.arc.yaml`)

```yaml
project:
  name: "my-research"

research:
  topic: "您的科研主题"

llm:
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  api_key_env: "OPENAI_API_KEY"
  primary_model: "gpt-4o"
  fallback_models: ["gpt-4o-mini"]

experiment:
  mode: "sandbox"
  sandbox:
    python_path: ".venv/bin/python"
```

```bash
export OPENAI_API_KEY="$YOUR_OPENAI_KEY"
```

### OpenRouter配置（200+模型）

```yaml
llm:
  provider: "openrouter"
  api_key_env: "OPENROUTER_API_KEY"
  primary_model: "anthropic/claude-3.5-sonnet"
  fallback_models:
    - "google/gemini-pro-1.5"
    - "meta-llama/llama-3.1-70b-instruct"
```

```bash
export OPENROUTER_API_KEY="$YOUR_OPENROUTER_KEY"
```

### ACP（智能体客户端协议）— 无需API密钥

```yaml
llm:
  provider: "acp"
  acp:
    agent: "claude"   # 或: codex, gemini, opencode, kimi
    cwd: "."
```

智能体CLI（例如 `claude`）自行处理其认证。

### OpenClaw桥接（可选高级功能）

```yaml
openclaw_bridge:
  use_cron: true              # 定时研究运行
  use_message: true           # 进度通知
  use_memory: true            # 跨会话知识持久化
  use_sessions_spawn: true    # 并行子会话
  use_web_fetch: true         # 文献综述中的实时网络搜索
  use_browser: false          # 基于浏览器的论文收集
```

---

## 关键CLI命令

```bash
# 基本运行 — 完全自主，无需提示
researchclaw run --topic "您的科研想法" --auto-approve

# 使用显式配置文件运行
researchclaw run --config config.arc.yaml --topic "专家混合路由效率" --auto-approve

# 在配置文件中定义主题运行（省略 --topic 标志）
researchclaw run --config config.arc.yaml --auto-approve

# 交互模式 — 在门控阶段暂停以获取批准
researchclaw run --config config.arc.yaml --topic "您的主题"

# 检查流程状态 / 恢复运行
researchclaw status --run-id rc-20260315-120000-abc123

# 列出历史运行
researchclaw list
```

**门控阶段**（5, 9, 20）在交互模式下暂停以获取人工批准。传递 `--auto-approve` 跳过所有门控。

---

## Python API

```python
from researchclaw.pipeline import Runner
from researchclaw.config import load_config

# 加载配置并运行
config = load_config("config.arc.yaml")
config.research.topic = "长上下文LLM的高效注意力机制"
config.auto_approve = True

runner = Runner(config)
result = runner.run()

# 访问输出
print(result.artifact_dir)          # artifacts/rc-YYYYMMDD-HHMMSS-<hash>/
print(result.deliverables_dir)      # .../deliverables/
print(result.paper_draft_path)      # .../deliverables/paper_draft.md
print(result.latex_path)            # .../deliverables/paper.tex
print(result.bibtex_path)           # .../deliverables/references.bib
print(result.verification_report)  # .../deliverables/verification_report.json
```

```python
# 仅运行特定阶段
from researchclaw.pipeline import Runner, StageRange

runner = Runner(config)
result = runner.run(stages=StageRange(start="LITERATURE_COLLECT", end="KNOWLEDGE_EXTRACT"))
```

```python
# 运行后访问知识库
from researchclaw.knowledge import KnowledgeBase

kb = KnowledgeBase.load(result.artifact_dir)
findings = kb.get("findings")
literature = kb.get("literature")
decisions = kb.get("decisions")
```

---

## 输出结构

运行后，所有输出将位于 `artifacts/rc-YYYYMMDD-HHMMSS-<hash>/`：

```
artifacts/rc-20260315-120000-abc123/
├── deliverables/
│   ├── paper_draft.md          # 完整学术论文（Markdown）
│   ├── paper.tex               # 会议准备好的LaTeX
│   ├── references.bib          # 真实BibTeX — 自动修剪为内联引用
│   ├── verification_report.json # 4层引用完整性报告
│   └── reviews.md              # 多智能体同行评审
├── experiment_runs/
│   ├── run_001/
│   │   ├── code/               # 生成的实验代码
│   │   ├── results.json        # 结构化指标
│   │   └── sandbox_output.txt  # 执行日志
├── charts/
│   └── *.png                   # 自动生成的比较图表
├── evolution/
│   └── lessons.json            # 用于未来运行的自我学习经验
└── knowledge_base/
    ├── decisions.json
    ├── experiments.json
    ├── findings.json
    ├── literature.json
    ├── questions.json
    └── reviews.json
```

---

## 流程阶段参考

| 阶段 | 阶段编号 | 名称 | 备注 |
|------|---------|------|------|
| A | 1 | TOPIC_INIT | 解析和界定研究主题 |
| A | 2 | PROBLEM_DECOMPOSE | 将问题分解为子问题 |
| B | 3 | SEARCH_STRATEGY | 构建搜索查询 |
| B | 4 | LITERATURE_COLLECT | 真实API调用至arXiv + Semantic Scholar |
| B | 5 | LITERATURE_SCREEN | **门控** — 批准/拒绝文献 |
| B | 6 | KNOWLEDGE_EXTRACT | 提取结构化知识 |
| C | 7 | SYNTHESIS | 综合研究结果 |
| C | 8 | HYPOTHESIS_GEN | 多智能体辩论形成假设 |
| D | 9 | EXPERIMENT_DESIGN | **门控** — 批准/拒绝设计 |
| D | 10 | CODE_GENERATION | 生成实验代码 |
| D | 11 | RESOURCE_PLANNING | GPU/MPS/CPU自动检测 |
| E | 12 | EXPERIMENT_RUN | 沙盒化执行 |
| E | 13 | ITERATIVE_REFINE | 失败时自我修复 |
| F | 14 | RESULT_ANALYSIS | 多智能体分析 |
| F | 15 | RESEARCH_DECISION | PROCEED / REFINE / PIVOT |
| G | 16 | PAPER_OUTLINE | 构建论文结构 |
| G | 17 | PAPER_DRAFT | 撰写完整论文 |
| G | 18 | PEER_REVIEW | 证据一致性检查 |
| G | 19 | PAPER_REVISION | 结合评审反馈修改论文 |
| H | 20 | QUALITY_GATE | **门控** — 最终批准 |
| H | 21 | KNOWLEDGE_ARCHIVE | 保存经验至知识库 |
| H | 22 | EXPORT_PUBLISH | 输出LaTeX + BibTeX |
| H | 23 | CITATION_VERIFY | 4层反幻觉检查 |

---

## 常见模式

### 模式：快速研究主题论文

```bash
export OPENAI_API_KEY="$OPENAI_API_KEY"
researchclaw run \
  --topic "蛋白质结构预测的自监督学习" \
  --auto-approve
```

### 模式：使用完整配置的可复现运行

```yaml
# config.arc.yaml
project:
  name: "protein-ssl-research"

research:
  topic: "蛋白质结构预测的自监督学习"

llm:
  provider: "openai"
  api_key_env: "OPENAI_API_KEY"
  primary_model: "gpt-4o"
  fallback_models: ["gpt-4o-mini"]

experiment:
  mode: "sandbox"
  sandbox:
    python_path: ".venv/bin/python"
  max_iterations: 3
  timeout_seconds: 300
```

```bash
researchclaw run --config config.arc.yaml --auto-approve
```

### 模式：使用OpenRouter的Claude以最佳推理

```bash
export OPENROUTER_API_KEY="$OPENROUTER_API_KEY"

cat > config.arc.yaml << 'EOF'
project:
  name: "my-research"
llm:
  provider: "openrouter"
  api_key_env: "OPENROUTER_API_KEY"
  primary_model: "anthropic/claude-3.5-sonnet"
  fallback_models: ["google/gemini-pro-1.5"]
experiment:
  mode: "sandbox"
  sandbox:
    python_path: ".venv/bin/python"
EOF

researchclaw run --config config.arc.yaml \
  --topic "Transformer推理的高效KV缓存压缩" \
  --auto-approve
```

### 模式：失败运行后恢复

```bash
# 列出运行以找到运行ID
researchclaw list

# 从最后一个完成阶段恢复
researchclaw run --resume rc-20260315-120000-abc123
```

### 模式：程序化批量研究

```python
import asyncio
from researchclaw.pipeline import Runner
from researchclaw.config import load_config

topics = [
    "有限硬件上的LoRA微调",
    "LLM推理的推测解码",
    "Flash attention变体比较",
]

config = load_config("config.arc.yaml")
config.auto_approve = True

for topic in topics:
    config.research.topic = topic
    runner = Runner(config)
    result = runner.run()
    print(f"[{topic}] → {result.deliverables_dir}")
```

### 模式：OpenClaw单行（如果使用OpenClaw智能体）

```
分享仓库URL给OpenClaw，然后说：
"研究专家混合路由效率"
```

OpenClaw自动读取 `RESEARCHCLAW_AGENTS.md`，克隆、安装、配置并运行完整流程。

---

## 编译LaTeX输出

```bash
# 导航至deliverables
cd artifacts/rc-*/deliverables/

# 编译（需要LaTeX发行版）
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex

# 或直接上传 paper.tex + references.bib 至Overleaf
```

---

## 故障排除

### `researchclaw: command not found`
```bash
# 确保venv已激活且包已安装
source .venv/bin/activate
pip install -e .
which researchclaw
```

### API密钥错误
```bash
# 验证环境变量是否设置
echo $OPENAI_API_KEY
# 应打印您的密钥（非空）

# 为当前会话显式设置
export OPENAI_API_KEY="sk-..."
```

### 实验沙盒失败
流程在Stage 13（ITERATIVE_REFINE）处自我修复。如果持续失败：
```yaml
# 在配置中增加超时和迭代次数
experiment:
  max_iterations: 5
  timeout_seconds: 600
  sandbox:
    python_path: ".venv/bin/python"
```

### 引用幻觉警告
Stage 23（CITATION_VERIFY）运行4层检查。如果引用被修剪：
- 这是**预期行为** — 自动移除虚假引用
- 查看 `verification_report.json` 了解被拒绝引用的详细信息及原因

### PIVOT循环无限运行
Stage 15（RESEARCH_DECISION）可能多次PIVOT。为限制迭代：
```yaml
research:
  max_pivots: 2
  max_refines: 3
```

### LaTeX编译错误
```bash
# 检查缺失的包
pdflatex paper.tex 2>&1 | grep "File.*not found"

# 安装缺失的包（TeX Live）
tlmgr install <package-name>
```

### 实验期间内存不足
```yaml
# 在配置中强制CPU模式
experiment:
  sandbox:
    device: "cpu"
    max_memory_gb: 4
```

---

## 关键概念

- **PIVOT/REFINE循环**：Stage 15自主决定PROCEED、REFINE（调整参数）或PIVOT（新假设方向）。所有输出均版本化。
- **多智能体辩论**：Stage 8、14、18使用结构化多视角辩论 — 非单一LLM调用。
- **自我学习**：每次运行提取带30天时间衰减的经验。相似主题的未来运行可受益于过去的错误。
- **哨兵监控**：后台监控检测结果中的NaN/Inf、检查论文证据一致性、评分引用相关性，并在整个运行中防止伪造。
- **4层引用验证**：arXiv查询 → CrossRef查询 → DataCite查询 → LLM相关性评分。引用必须通过所有层才能存活。
