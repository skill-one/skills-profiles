# /hub:eval — 评估代理结果

对会话中的所有代理结果进行排名。支持基于指标的评估（运行命令）、大型语言模型（LLM）评判（比较差异）或混合模式。

## 使用方法

```
/hub:eval                           # 使用配置的标准对最新会话进行评估
/hub:eval 20260317-143022           # 对特定会话进行评估
/hub:eval --judge                   # 强制使用LLM评判模式（忽略指标配置）
```

## 功能说明

### 指标模式（已配置eval命令）

在每个代理的工作区中运行评估命令：

```bash
python {skill_path}/scripts/result_ranker.py \
  --session {session-id} \
  --eval-cmd "{eval_cmd}" \
  --metric {metric} --direction {direction}
```

输出：

```
排名  代理       指标      差值      文件数
1     agent-2     142ms       -38ms      2
2     agent-1     165ms       -15ms      3
3     agent-3     190ms       +10ms      1

获胜者：agent-2 (142ms)
```

### LLM评判模式（无eval命令，或--judge标志）

对每个代理：
1. 获取差异：`git diff {base_branch}...{agent_branch}`
2. 从`.agenthub/board/results/agent-{i}-result.md`读取代理的结果帖子
3. 通过以下标准比较所有差异并进行排名：
   - **正确性** — 是否解决了任务？
   - **简洁性** — 改变的行数越少越好（当正确性相同时）
   - **质量** — 清晰的执行、良好的结构、无回归问题

展示排名并说明理由。

内容任务的一个LLM评判输出示例：

```
排名  代理    判定                               字数
1     agent-1  故事性强，CTA清晰            1480
2     agent-3  数据点好，引言弱            1520
3     agent-2  语气通用，无区分度           1350

获胜者：agent-1 (最强的故事弧和号召性用语)
```

### 混合模式

1. 首先运行指标评估
2. 如果顶尖代理彼此差距在10%以内，使用LLM评判来打破平局
3. 展示指标和定性排名

## 评估后

1. 更新会话状态：

```bash
python {skill_path}/scripts/session_manager.py --update {session-id} --state evaluating
```

2. 告知用户：
   - 排名结果，并突出显示获胜者
   - 下一步：`/hub:merge` 合并获胜者
   - 或 `/hub:merge {session-id} --agent {winner}` 明确指定
