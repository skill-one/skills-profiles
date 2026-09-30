---
name: skill-idea-miner
description: 搜索我的Claude代码会话日志以查找技能想法候选。在运行每周技能生成管道时使用，用于从最近的编码会话中提取、评分和积累新的技能想法。
---

# 技能点挖掘器

自动从Claude Code会话日志中提取技能点候选，对其新颖性、可行性和交易价值进行评分，并维护一个用于下游技能生成的优先级待办事项列表。

## 使用场景

- 每周自动运行流程（周六 06:00 通过 launchd 运行）
- 手动刷新待办事项列表：`python3 scripts/run_skill_generation_pipeline.py --mode weekly`
- 不进行LLM评分的干运行预览候选

## 前置条件

- **Python 3.10+** 及 `pyyaml` 包
- **Claude CLI** 已安装并认证（使用 `claude --version` 验证）
- **会话日志** 位于 `~/.claude/projects/<项目>/`（由 Claude Code 自动创建）
- 无需API密钥（使用 Claude CLI 进行LLM调用）

## 工作流程

### 快速入门

```bash
# 干运行：预览挖掘的候选而不进行LLM评分
python3 scripts/mine_session_logs.py --dry-run --output-dir reports/

# 带评分的完整挖掘（需要 Claude CLI）
python3 scripts/mine_session_logs.py --output-dir reports/

# 评分现有候选
python3 scripts/score_ideas.py \
  --candidates reports/raw_candidates.yaml \
  --output-dir logs/
```

### 阶段1：会话日志挖掘

1. 列举 `~/.claude/projects/` 中允许列表项目的会话日志
2. 通过文件修改时间过滤过去7天，使用 `timestamp` 字段确认
3. 提取用户消息（`type: "user"`, `userType: "external"`）
4. 从助手消息中提取工具使用模式
5. 运行确定性信号检测：
   - 技能使用频率（`skills/*/` 路径引用）
   - 错误模式（非零退出码、`is_error` 标志、异常关键词）
   - 重复工具序列（3个以上工具重复3次以上）
   - 自动化请求关键词（英文和日文）
   - 未解决的请求（用户消息后5分钟以上间隔）
6. 调用 Claude CLI 头部模式进行想法抽象
7. 输出 `raw_candidates.yaml`

### 阶段2：评分和去重

1. 从 `skills/*/SKILL.md` 的frontmatter加载现有技能
2. 通过杰卡德相似度（阈值 > 0.5）进行去重，对比：
   - 现有技能名称和描述
   - 现有待办事项列表中的想法
3. 使用 Claude CLI 对非重复候选进行评分：
   - 新颖性（0-100）：与现有技能的差异度
   - 可行性（0-100）：技术可实施性
   - 交易价值（0-100）：对投资者/交易者的实际价值
   - 综合评分 = 0.3 * 新颖性 + 0.3 * 可行性 + 0.4 * 交易价值
4. 将评分后的候选合并到 `logs/.skill_generation_backlog.yaml`

## 输出格式

### raw_candidates.yaml

```yaml
generated_at_utc: "2026-03-08T06:00:00Z"
period: {from: "2026-03-01", to: "2026-03-07"}
projects_scanned: ["claude-trading-skills"]
sessions_scanned: 12
candidates:
  - id: "raw_2026w10_001"
    title: "Earnings Whispers Image Parser"
    source_project: "claude-trading-skills"
    evidence:
      user_requests: ["从截图提取收益日期"]
      pain_points: ["手动读取图像"]
      frequency: 3
    raw_description: "解析 Earnings Whispers 截图以提取日期。"
    category: "数据提取"
```

### 待办事项列表（logs/.skill_generation_backlog.yaml）

```yaml
updated_at_utc: "2026-03-08T06:15:00Z"
ideas:
  - id: "idea_2026w10_001"
    title: "Earnings Whispers Image Parser"
    description: "解析 Earnings Whispers 截图的技能..."
    category: "数据提取"
    scores: {novelty: 75, feasibility: 60, trading_value: 80, composite: 73}
    status: "pending"
```

## 资源

- `references/idea_extraction_rubric.md` — 信号检测标准和评分标准
- `scripts/mine_session_logs.py` — 会话日志解析器
- `scripts/score_ideas.py` — 评分器和去重器
