# debugging-apex-logs：Salesforce调试日志分析与故障排除

当用户需要从调试日志中进行**根本原因分析**时使用此技能：治理器限制诊断、堆栈跟踪解释、慢查询调查、堆/ CPU压力分析，或基于日志证据的基于日志证据的重复修复循环。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `debugging-apex-logs`：
- Salesforce 的 `.log` 文件
- 堆栈跟踪和异常分析
- 治理器限制
- SOQL / DML / CPU / 堆故障排除
- 从日志中提取的查询计划或性能证据

当用户处于以下情况时，将其委托给其他技能：
- 运行或修复 Apex 测试 → [running-apex-tests](../running-apex-tests/SKILL.md)
- 生成或实施代码修复 → [generating-apex](../generating-apex/SKILL.md)
- 调试 Agentforce 会话跟踪 / parquet 远程监测 → [observing-agentforce](../observing-agentforce/SKILL.md)

---

## 首先收集所需的上下文

请求或推断：
- 组织别名
- 失败的交易 / 用户流程 / 测试名称
- 大约的时间戳或交易窗口
- 如果已知，用户 / 记录 / 请求 ID
- 目标是仅诊断还是诊断 + 修复循环

---

## 推荐的工作流程

### 1. 检索日志

使用 [references/cli-commands.md](references/cli-commands.md) 中的命令列出、下载或流式传输目标组织的日志。

### 2. 按顺序分析
1. 入口点和交易类型
2. 异常 / 致命错误
3. 治理器限制
4. 重复的 SOQL / DML 模式
5. CPU / 堆热点
6. 调用时间外部故障

### 3. 分类严重性
- **关键** — 运行时失败、硬限制、损坏风险
- **警告** — 接近限制、非选择查询、慢路径
- **信息** — 优化机会或卫生问题

### 4. 推荐最小的正确修复
优先考虑以下修复：
- 以根本原因为导向
- 批量安全
- 可测试
- 易于通过重新运行进行验证

扩展工作流程：[references/analysis-playbook.md](references/analysis-playbook.md)

---

## 高信号问题模式

| 问题 | 主要信号 | 默认修复方向 |
|---|---|---|
| 循环中的 SOQL | 重复的 `SOQL_EXECUTE_BEGIN` 在重复的调用路径中 | 一次查询，使用映射 / 分组集合 |
| 循环中的 DML | 重复的 `DML_BEGIN` 模式 | 收集行，一次批量 DML |
| 非选择查询 | 高行扫描 / 选择性差 | 添加索引过滤器，减少范围 |
| CPU 压力 | CPU 使用接近同步限制 | 减少算法复杂性，缓存，有效时异步 |
| 堆压力 | 堆使用接近同步限制 | 使用 SOQL 循环流式传输，减少内存数据 |
| 空指针 / 致命错误 | `EXCEPTION_THROWN` / `FATAL_ERROR` | 防御空假设，修复空查询处理 |

扩展示例：[references/common-issues.md](references/common-issues.md)

---

## 输出格式

完成分析后，按顺序报告：

1. **失败的内容**
2. **失败的位置**（类 / 方法 / 行 / 交易阶段）
3. **失败的原因**（根本原因，而不仅仅是症状）
4. **严重程度**
5. **推荐的修复**
6. **验证步骤**

建议的格式：

```text
问题： <摘要>
位置： <类 / 行 / 交易>
根本原因： <解释>
严重性： 关键 | 警告 | 信息
修复： <具体操作>
验证： <测试或重新运行步骤>
```

---

## 规则 / 限制

| 规则 | 理由 |
|------|-----------|
| 始终基于日志证据推荐修复 | 避免推测性诊断 — 根本原因必须在日志中可追踪 |
| 为每个发现的问题报告所有六个输出字段 | 确保对每个问题都有可操作的、完整的发现 |
| 将每个发现分类为关键、警告或信息 | 帮助用户优先处理哪些问题 |
| 将代码生成委托给 `generating-apex` | 此技能进行诊断；它不会重写 Apex 代码 |
| 将测试执行委托给 `running-apex-tests` | 此技能不运行或修复测试类 |
| 在未读取 `LIMIT_USAGE` 事件之前，永远不要假设限制是安全的 | 限制可能被失败点之前的操作消耗，而在失败点不可见 |

---

## 注意事项

| 陷阱 | 解决方案 |
|---------|------------|
| 日志在 2 MB 处被截断 | 降低调试级别（例如，`ApexCode: INFO`，`ApexProfiling: FINE`）并重新捕获 |
| 相同的问题同时表现为 SOQL 和 CPU 问题 | 首先修复循环中的 SOQL — 它通常作为次要效应驱动 CPU 峰值 |
| 设置跟踪标志后没有日志出现 | 验证跟踪标志 `ExpirationDate` 是否在未来，并且跟踪了正确的用户 |
| 异步上下文更改限制值 | CPU 限制是 60,000 毫秒异步 vs 10,000 毫秒同步 — 在标记限制之前检查交易类型 |
| 堆栈跟踪指向框架行，而不是用户代码 | 沿调用堆栈向上，越过触发处理程序，以找到原始用户代码 |

---

## 跨技能集成

| 需要 | 委托给 | 理由 |
|---|---|---|
| 实现 Apex 修复 | [generating-apex](../generating-apex/SKILL.md) | 代码更改生成 / 审查 |
| 通过测试重现 | [running-apex-tests](../running-apex-tests/SKILL.md) | 测试执行和覆盖循环 |
| 部署修复 | [deploying-metadata](../deploying-metadata/SKILL.md) | 部署编排 |
| 创建调试数据 | [handling-sf-data](../handling-sf-data/SKILL.md) | 针对性种子 / 重现数据 |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/analysis-playbook.md` | 从这里开始 — 任何调试会话的扩展分步工作流程 |
| `references/common-issues.md` | 快速查找 SOQL 在循环中、DML 在循环中、CPU/堆压力、空指针模式 |
| `references/cli-commands.md` | Salesforce CLI 命令，用于检索、流式传输和管理调试日志 |
| `references/debug-log-reference.md` | 完整的事件类型目录、日志级别和治理器限制参考值 |
| `references/log-analysis-tools.md` | 工具指南：Apex 日志分析器、开发者控制台、CLI grep 模式 |
| `references/benchmarking-guide.md` | 性能基准测试技术、基准数据和非模式 |
| `references/scoring-rubric.md` | 100 分评分标准，用于评估分析质量 |
| `assets/benchmarking-template.cls` | 复制粘贴匿名 Apex 模板，用于运行性能基准测试 |
| `assets/cpu-heap-optimization.cls` | 用于减少 CPU 时间和堆分配的 Apex 模式 |
| `assets/dml-in-loop-fix.cls` | 解决 DML 在循环中违规的示例 |
| `assets/soql-in-loop-fix.cls` | 解决 SOQL 在循环中违规的示例 |
| `assets/null-pointer-fix.cls` | 防御空指针异常的模式 |

---

## 评分指南

| 分数 | 含义 |
|---|---|
| 90+ | 专家分析，具有强大的修复指导 |
| 80–89 | 良好分析，有轻微差距 |
| 70–79 | 可接受，但可能会遗漏次要问题 |
| 60–69 | 仅部分诊断 |
| < 60 | 不完整分析 |
