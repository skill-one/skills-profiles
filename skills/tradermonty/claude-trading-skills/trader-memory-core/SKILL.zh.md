---
name: trader-memory-core
description: 跟踪投资策略在其生命周期中的进展——从筛选想法到关闭仓位并进行事后分析。从筛选器输出中注册策略，管理状态转换，附加仓位规模，审查截止日期，并生成包含盈亏（P&L）和平均绝对误差（MAE）/平均方向误差（MFE）分析的事后分析报告。当用户说“注册策略”、“跟踪这个想法”、“策略状态”、“审查截止日期”、“关闭仓位”、“事后分析”或“交易日记”时触发。
---

# 交易记忆核心

## 概述

持久化状态层，将筛选 → 分析 → 仓位规模 → 投资组合管理输出捆绑为每个投资想法的单一"论点对象"。跨对话跟踪你的想法、发生的事情以及你学到的知识。

第一阶段支持单一股票论点：dividend_income（股息收入）、growth_momentum（增长动量）、mean_reversion（均值回归）、earnings_drift（盈利漂移）、pivot_breakout（枢轴突破）。

## 使用场景

- 筛选器（kanchi、earnings-trade-analyzer、vcp、pead、canslim、edge-candidate-agent）产生候选对象后
- 当论点从 IDEA → ENTRY_READY → ACTIVE → CLOSED 过渡时
- 当将仓位规模输出附加到论点时
- 当检查哪些论点需要审查时
- 当关闭仓位并生成包含经验教训的事后分析时

## 前置条件

- Python 3.10+
- `pyyaml`（已在项目依赖中）
- `jsonschema`（已在 `pyproject.toml` 中；由 `thesis_store.py` 和所有导入它的命令（包括 `thesis_ingest.py` 和 `thesis_review.py`）要求）
- FMP API 密钥（可选，仅用于事后分析中的 MAE/MFE 计算）

### 如何调用 CLI

使用仅使用标准库的启动器 `trader_memory_cli.py` 进行所有 CLI 工作。当 `uv` 可用时，它会透明地通过 `uv run --project <repo>` 进行路由，因此即使从外部 cwd 或从没有全局 `jsonschema` 的 `python3`（例如 cron / Hermes 配置文件运行）中，也可以访问项目的固定 `jsonschema`：

```bash
# 在仓库内部
python3 skills/trader-memory-core/scripts/trader_memory_cli.py store --state-dir state/theses list

# 在任何其他 cwd（cron、配置文件、发行版运行器）中 — 将启动器指向仓库
export CLAUDE_TRADING_SKILLS_REPO=/path/to/claude-trading-skills
python3 "$CLAUDE_TRADING_SKILLS_REPO/skills/trader-memory-core/scripts/trader_memory_cli.py" \
  store --state-dir /path/to/state/theses list
```

子命令：`store` → `thesis_store.py`，`ingest` → `thesis_ingest.py`，`review` → `thesis_review.py`。子命令之后的所有内容都将原样转发，因此现有的参数标志（`--state-dir`、`transition`、`open-position` 等）可以保持不变。

如果启动器报告 `jsonschema` 不可导入并且 `uv` 不在 `PATH` 中，可操作的修复措施（按优先级排序）是：

1. 安装 `uv`（https://docs.astral.sh/uv/）并重新运行启动器。
2. 将项目的依赖项安装到当前解释器：
   ```bash
   uv pip install -e /path/to/claude-trading-skills
   # 或者，作为最后的手段：
   python3 -m pip install jsonschema
   ```

**不要**将论点存储视为不可用，**不要**手动修改 `state/theses/*.yaml` 以绕过缺失的依赖项——模式验证是论点状态完整性的组成部分。

## 工作流程

### 1. 注册 — 将筛选器输出作为论点摄取

读取筛选器的 JSON 输出并使用适当的适配器转换为论点。

```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py ingest \
  --source kanchi-dividend-sop \
  --input reports/kanchi_entry_signals_2026-03-14.json \
  --state-dir state/theses/
```

支持的来源：`kanchi-dividend-sop`、`earnings-trade-analyzer`、`vcp-screener`、`pead-screener`、`canslim-screener`、`edge-candidate-agent`、`manual`。

每个论点都以 `IDEA` 状态开始。

对于 `kanchi-dividend-sop`，注册是失败关闭的：每一行必须包含 `CLEAN-PASS`、`PASS-CAUTION` 或 `CONDITIONAL-PASS` 在 `verdict` 中。缺失的 `verdict` 和 `HOLD-REVIEW` / `STEP1-RECHECK` / `FAIL` 行将被跳过，并且永远不会写入论点状态。

#### 手动经纪入口（分数股）

对于没有来自筛选器的交易——例如分数股经纪商（IBKR、Robinhood、IBI Smart、Alpaca、eToro）或手动日记——使用 `manual` 来源和一个自由形式的 JSON 文件（单个对象或数组）：

```json
{
  "ticker": "AMD",
  "thesis_statement": "AMD AI 加速器动量，分数 IBI Smart 仓位",
  "thesis_type": "growth_momentum",
  "entry_price": 142.10,
  "entry_date": "2026-05-02",
  "shares": 7.86,
  "stop_price": 128.00
}
```

```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py ingest \
  --source manual --input amd.json --state-dir state/theses/
```

必需：`ticker`、`thesis_statement`、`thesis_type`（`dividend_income`、`growth_momentum`、`mean_reversion`、`earnings_drift`、`pivot_breakout` 之一）。`stop_price`/`stop_loss` 和 `target_price`/`take_profit` 映射到 `exit.stop_loss`/`exit.take_profit`；`entry_price`/`entry_date`/`shares` 保留在 `origin.raw_provenance` 中——权威的入口价格/日期和股份数量是在你打开仓位时（如下所述）设置的。`shares` 可能是**分数**（模式接受任何正数）。像每个适配器一样，手动摄取只创建 `IDEA` 论点——它从不直接修改状态。

要记录一个**已打开的经纪仓位**，运行显式生命周期序列（`--event-date` 标志将历史记录回溯，以保持时间顺序）：

```bash
# 1. ingest → IDEA（标记在 entry_date）
python3 .../trader_memory_cli.py ingest --source manual --input amd.json --state-dir state/theses/
# 2. IDEA → ENTRY_READY（回溯）
python3 .../trader_memory_cli.py store --state-dir state/theses/ transition <id> ENTRY_READY \
  --reason "现有的 IBI Smart 仓位" --event-date 2026-05-02
# 3. ENTRY_READY → ACTIVE（分数股，回溯）
python3 .../trader_memory_cli.py store --state-dir state/theses/ open-position <id> \
  --actual-price 142.10 --actual-date 2026-05-02 --shares 7.86 --event-date 2026-05-02
```

### 2. 查询 — 搜索和列出论点

```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py store \
  --state-dir state/theses/ list --ticker AAPL --status ACTIVE
```

按 `--ticker`、`--status` 或 `--type` 过滤。

### 3. 更新 — 过渡、附加仓位、链接报告

每个生命周期操作都可用作 Python 函数和 `thesis_store.py` CLI 子命令。`--event-date` / `--actual-date` 接受纯 `YYYY-MM-DD`（扩展到 UTC 午夜）或完整的 ISO 时间戳。

**状态过渡**（IDEA → ENTRY_READY 仅限）：

```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py store --state-dir state/theses/ \
  transition <id> ENTRY_READY --reason "已验证" [--event-date YYYY-MM-DD]
```

`--event-date` 回溯 `status_history.at`（用于回填现有仓位，以便较后的回溯 `open-position` 保持时间顺序）。Python：`thesis_store.transition(state_dir, thesis_id, "ENTRY_READY", reason, event_date=...)`。

**打开仓位**（ENTRY_READY → ACTIVE — 唯一进入 ACTIVE 的路径）：

```bash
python3 .../trader_memory_cli.py store --state-dir state/theses/ open-position <id> \
  --actual-price 142.10 --actual-date 2026-05-02 [--shares 7.86] [--event-date 2026-05-02]
```

`--shares` 接受**分数**数量。Python：
`thesis_store.open_position(state_dir, thesis_id, actual_price, actual_date, shares=..., event_date=...)`。
`shares`（和 `shares_remaining`，当存在时）必须是一个**有限的、正数，不超过 10<sup>12</sup>**（一个理智限制，不是一个经济限制——分数股低于上限的保持无限制）。NaN、±Infinity 以及荒谬大的值（例如一个格式错误的仓位规模报告）在保存时以干净的错误被拒绝，在 `open-position`、`attach-position` 和 `trim` 中一样。

对于**期货**论点，使用 `--contracts` 而不是 `--shares`（见下文“期货仓位”）——如果 `attach-futures-position` 已经填充了仓位，则省略 `--contracts`，并且只传递 `--actual-price`/`--actual-date`。

**Trim — 部分关闭**（ACTIVE/PARTIALLY_CLOSED → PARTIALLY_CLOSED，或 →
CLOSED 当整个剩余部分被卖出时）：

```bash
python3 .../trader_memory_cli.py store --state-dir state/theses/ trim <id> \
  --shares-sold 4 --price 120.00 --date 2026-05-10
```

`position.shares` 是**原始**打开的数量（不可变）；
`position.shares_remaining` 跟踪仍然开放的量。每次 trim 都会追加一个 `status_history` 分类账条目（`shares_sold` / `price` / `proceeds` /
`realized_pnl`）。`outcome.pnl_dollars` 是**累积**已实现 P&L（Σ 所有 trims + 最终关闭）；`outcome.pnl_pct = pnl_dollars / (entry_price ×
original_shares) × 100`。一个 trim 卖出整个剩余部分将关闭论点（默认 `exit_reason: manual`，可覆盖 `--exit-reason`）。
`--date` 是分类账时间戳（可覆盖 `--event-date`）。Python：
`thesis_store.trim(state_dir, thesis_id, shares_sold, price, date, ...)`。

状态不变量：`ACTIVE` ⇒ `shares_remaining == shares`；
`PARTIALLY_CLOSED` ⇒ `0 < shares_remaining < shares`；
`CLOSED` ⇒ `shares_remaining == 0`。遗留论点（没有 `shares_remaining`）在运行时被视为完全开放。

对于**期货**论点，使用 `--contracts-sold` 而不是 `--shares-sold`——`close`/`terminate` 无需更改标志；它们读取 `position.asset_type` 并自动分派（见下文“期货仓位”）。

**关闭或使无效**（→ CLOSED 或 INVALIDATED）：

```bash
python3 .../trader_memory_cli.py store --state-dir state/theses/ close <id> \
  --exit-reason target_hit --actual-price 165.00 --actual-date 2026-06-01
python3 .../trader_memory_cli.py store --state-dir state/theses/ terminate <id> \
  --terminal-status INVALIDATED --exit-reason "论点出问题"
```

`close` 接受 `ACTIVE` **或** `PARTIALLY_CLOSED` 论点；从 PARTIALLY_CLOSED 它会添加最终环节并报告累积结果。

Python：`thesis_store.terminate(state_dir, thesis_id, terminal_status, exit_reason, actual_price, actual_date)`。对于 CLOSED，委托给 `close()` 计算 P&L（分数股感知）。对于 INVALIDATED，如果入口/出口价格可用，则计算 P&L。

**记录审查**（任何非终端）：

使用 `thesis_store.mark_reviewed(state_dir, thesis_id, review_date=..., outcome="OK"|"WARN"|"REVIEW")` 推进 next_review_date 并记录警报。

**附加仓位规模输出：**

```bash
python3 .../trader_memory_cli.py store --state-dir state/theses/ attach-position <id> \
  --report reports/position_report.json
```

Python：`thesis_store.attach_position(state_dir, thesis_id, report_path)` 以链接仓位规模数据。验证报告模式为 "shares"（不是预算）。

#### 期货仓位（合约 / 多头 / 方向）

一个 `position.asset_type == "futures"`（或 `quantity_unit == "contracts"）的论点是**期货**论点。期货论点使用 `quantity` /
`quantity_remaining`（整合约——没有分数合约）而不是 `shares` /
`shares_remaining`，携带一个 `direction`（`LONG` 或 `SHORT`）和一个 `multiplier`，并且每个 P&L 计算（`close`、`terminate`、`trim`）应用 `(exit_price - entry_price) × multiplier × quantity × sign`（sign = +1 LONG, −1 SHORT）而不是每单位股票的公式。`close` / `terminate` / `trim` / `open-position` 都根据 `position.asset_type` 自动分派——这四个操作没有单独的期货子命令。**仅限美元计价的合约**——P&L 路径中没有 FX 转换，因此非美元的 `contract_spec.currency` 将被直接拒绝，而不是以错误货币的幅度计算 P&L。

**附加期货仓位规模 SIZED 报告**（Shapiro 反向管道的步骤 6 — futures-position-sizer → trader-memory-core）：

```bash
python3 .../trader_memory_cli.py store --state-dir state/theses/ \
  attach-futures-position <id> --report reports/futures_position_es_2026-05-10.json
```

拒绝 `NO_TRADE` 报告（`sizing_status != "SIZED"`）、无效的 `direction`、非正/分数的 `contracts` 计数、非有限/正的 `contract_spec.multiplier` 或非美元的 `contract_spec.currency`。
重新附加状态守卫是 `IDEA`/`ENTRY_READY` **仅限**——比股票的 `attach-position` 严格（它还允许 `ACTIVE`）：在 `ACTIVE` 上重新附加期货仓位将静默覆盖整个仓位字典，包括 `direction`，反转每个后续 P&L 计算的符号。纠正已打开的期货仓位需要一个新论点（或一个未来的“修正”操作）——而不是重新附加。

**直接打开，无附加**（从 CLI 标志而不是 SIZED 报告构建仓位——`--contract-currency` 在这里**必需**，因为没有 `contract_spec` 可以从中读取货币，并且必须是 `USD`）：

```bash
python3 .../trader_memory_cli.py store --state-dir state/theses/ open-position <id> \
  --actual-price 5000 --actual-date 2026-05-10 \
  --contracts 2 --multiplier 50 --direction SHORT --contract-symbol ES \
  --contract-currency USD
```

**Trim / close / terminate** — 与股票相同的子命令，`--contracts-sold` 替换 `--shares-sold`：

```bash
python3 .../trader_memory_cli.py store --state-dir state/theses/ trim <id> \
  --contracts-sold 1 --price 4950.00 --date 2026-05-12
python3 .../trader_memory_cli.py store --state-dir state/theses/ close <id> \
  --exit-reason target_hit --actual-price 4900.00 --actual-date 2026-05-15
```

Python：`thesis_store.attach_futures_position(state_dir, thesis_id, report_path)`，
`thesis_store.open_position(state_dir, thesis_id, actual_price, actual_date, contracts=..., multiplier=..., direction=...)`。

**链接相关报告：**

使用 `thesis_store.link_report(state_dir, thesis_id, skill, file, date)` 交叉引用分析文档。

### 4. 审查 — 检查到期日期和监控状态

```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py review \
  --state-dir state/theses/ review-due --as-of 2026-04-15
```

列出 `next_review_date <= as_of` 的论点。与 kanchi-dividend-review-monitor 触发器（T1-T5）一起使用，以进行系统化审查。

### 5. 事后分析 — 关闭并反思

```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py review \
  --state-dir state/theses/ postmortem th_aapl_div_20260314_a3f1
```

在 `state/journal/` 中生成结构化的事后分析。如果 FMP API 密钥可用，则包括 MAE/MFE（最大不利/有利偏差）指标。

**摘要统计：**

```bash
python3 skills/trader-memory-core/scripts/trader_memory_cli.py review \
  --state-dir state/theses/ summary
```

显示所有已关闭论点的胜率、平均 P&L% 和按类型细分。

## 输出格式

### 论点 YAML（state/theses/）

每个论点是一个 YAML 文件，包含：
- 身份：thesis_id、ticker、created_at
- 分类：thesis_type、setup_type、catalyst
- 生命周期：status、status_history
- 入口/出口：目标价格、实际价格、条件
- 仓位：shares（支持分数）、价值、风险（来自仓位规模或 `open-position --shares`）；或，对于期货，quantity/multiplier/direction/contract_spec（来自 futures-position-sizer 或 `open-position --contracts`）
- 监控：审查日期、触发器、警报
- 来源：来源技能、筛选等级、原始来源
- 结果：P&L、持有天数、MAE/MFE、经验教训

### 索引（state/theses/_index.json）

用于快速查询而无需加载完整 YAML 文件的轻量级索引。

### 日志（state/journal/）

事后分析 Markdown 报告：`pm_{thesis_id}.md`。

## 支持的 Python 读取和验证 API

使用 `scripts/thesis_store.py` 中的这些公共函数进行重放和其他 Python 消费者：

```python
from pathlib import Path
import thesis_store

thesis = thesis_store.get(Path("state/theses"), thesis_id)
thesis_store.validate_thesis(thesis)
```

- `get(state_dir, thesis_id)` 加载新的 YAML 数据，而不会修改论文文件或索引。它不会验证加载的内容。缺失的文件会引发 `FileNotFoundError`；格式错误的 YAML 会引发 `yaml.YAMLError`。
- `validate_thesis(thesis)` 检查 JSON Schema 和业务不变量，成功时返回 `None`，验证失败时引发 `ValueError`。它不会修改输入或写入状态。
- 在依赖其模式和业务不变量之前，显式地验证加载或规范化记录。保持对这些支持函数的消费者；下划线前缀的辅助函数是内部实现细节。

## 关键原则

- **单向转换**：IDEA → ENTRY_READY → ACTIVE → CLOSED（不允许回溯）
- **原始溯源**：所有原始筛选器数据保存在 `origin.raw_provenance` 中
- **原子写入**：所有文件操作使用 tempfile + os.replace
- **Git 跟踪状态**：`state/` 目录被提交，提供审计追踪
- **第一阶段范围**：仅限单支票论文（配对交易和期权在第二阶段）

## 资源

- `references/thesis_lifecycle.md` — 状态状态和有效转换
- `references/field_mapping.md` — 源技能 → 标准字段映射
- `schemas/thesis.schema.json` — 论文验证的 JSON Schema
- `../../examples/workflows/trade-memory-loop/sample-run-full-path/` — 工作端到端 Plan → Trade → Record → Postmortem → Backtest → Journal 示例
