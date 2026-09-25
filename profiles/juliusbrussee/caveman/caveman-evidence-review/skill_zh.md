# 审查 Caveman 证据

以只读操作员的身份工作。基于当前的 Caveman 数据构建结论，而非基于仓库的猜测。切勿通过此技能启动、批准、取消或回滚实验。

## 硬性规则

1. 保持以下类别相互分离：
   - 已测量的供应商完整清单价成本；
   - `inferred` 每日余量；
   - `verified` 账本节省；
   - 证据成本。
   切勿新增或更改其标签。
2. 除非用户明确要求审查负载（payload），否则不要获取 prompt、completion、tool 或 artifact 的负载内容。对于默认审查而言，元数据、spans、时序、模型、token 计数、状态和优化器归属信息已足够。
3. 每次读取都限定在 Caveman 上下文所选定的项目范围内。切勿提供 organization id。
4. 空结果证明当前无信号，而非零成本或零风险。
5. 引用所使用的 trace id 和确切时间窗口。切勿仅依据聚合数据断言因果关系。

## 第 1 步 — 加载上下文

优先使用 MCP：

```text
caveman_context {}
```

CLI 回退方案：

```bash
caveman cloud whoami
caveman cloud projects list
```

如果登录或项目选择缺失，请停止。请用户运行 `caveman login` 或选择项目；切勿猜测。

## 第 2 步 — 建立基线

使用 `caveman_report` 获取：

- `overview`
- `costs`
- `score`
- `workflows`
- `verified_savings`

然后使用 `caveman_plan` 获取按排名排列的每日余量。若问题较窄，可跳过不相关报告。读取能够回答该问题所需的最短集合。

CLI 回退方案：

```bash
caveman cloud costs
caveman cloud score
caveman cloud plan --json
```

在解读方向变化前，需说明报告窗口和依据。

## 第 3 步 — 用追踪数据验证主导解释

使用 `caveman_trace_search`。选择一个有界时间窗口和封闭的过滤条件：workflow、agent、model、provider、error code、runtime mode、cache status、optimization id、status class、token/cost/latency bounds、compression，或 monitor verdict。

常用分组：

- `workflow` — 查找驱动成本或故障的任务；
- `model` — 对比模型组合；
- `session` — 隔离重试或循环行为；
- ungrouped — 识别确切的追踪数据。

将待排查的小组与控制小组或更早的有界时间窗口进行对比。切勿依据单条高成本追踪数据推断因果关系。

CLI 回退方案：

```bash
caveman cloud traces search \
  --workflow <slug>\
  --from <RFC3339>\
  --to <RFC3339>\
  --sort total_cost_usd \
  --dir desc \
  --limit 25
```

## 第 4 步 — 检查代表性追踪

对少量高信号 trace id 调用 `caveman_trace_get`。检查请求和 span 元数据、延迟、状态、token 计数、缓存状态、已应用的优化器和模型路由。保持负载获取处于关闭状态。

CLI 回退方案：

```bash
caveman cloud traces show <trace-id} --spans
```

## 第 5 步 — 报告

使用以下格式：

```text
## Caveman evidence review

Scope: <project} · <from} to <to}
Measured cost: <value and basis}
Verified savings: <ledger value, kept separate}
Inferred headroom: <per-day band, kept separate}

Findings:
1. <finding} — <aggregate evidence} — traces <ids}
2. <finding} — <aggregate evidence} — traces <ids}

Unproven:
- <plausible explanation lacking a control, trace, or eval}

Next read-only check:
- <one bounded query}

Possible action:
- <proposal only; use caveman-manage for read-only lifecycle review and safety gate}
```

若数据缺失，需指出缺失的信号，并停止于当前可支持的 strongest supported statement。切勿将目录小计变为发票，或把实验结果变为已验证节省。
