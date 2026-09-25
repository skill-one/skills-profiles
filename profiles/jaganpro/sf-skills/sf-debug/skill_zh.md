# sf-debug：Salesforce调试日志分析与故障排除

当用户需要从调试日志中进行**根本原因分析**时使用此技能：治理器限制诊断、堆栈跟踪解释、慢查询调查、堆/ CPU 压力分析，或基于日志证据的基于日志进行复现和修复的循环。

## 此技能负责任务的条件

当工作涉及以下内容时，使用 `sf-debug`：
- Salesforce 的 `.log` 文件
- 堆栈跟踪和异常分析
- 治理器限制
- SOQL / DML / CPU / 堆故障排除
- 从日志中提取的查询计划或性能证据

当用户处于以下情况时，将其委托给其他技能：
- 运行或修复 Apex 测试 → [sf-testing](../sf-testing/SKILL.md)
- 实现代码修复 → [sf-apex](../sf-apex/SKILL.md)
- 调试 Agentforce 会话跟踪 / parquet 远程遥测 → [sf-ai-agentforce-observability](../sf-ai-agentforce-observability/SKILL.md)

---

## 收集初始所需上下文

请求或推断：
- org 别名
- 失败的交易 / 用户流程 / 测试名称
- 大约的时间戳或交易窗口
- 如果已知，用户 / 记录 / 请求 ID
- 目标是仅诊断还是诊断 + 修复循环

---

## 推荐的工作流程

### 1. 检索日志
```bash
sf apex list log --target-org <别名> --json
sf apex get log --log-id <id> --target-org <别名>
sf apex tail log --target-org <别名> --color
```

### 2. 按顺序分析
1. 入口点和交易类型
2. 异常 / 致命错误
3. 治理器限制
4. 重复的 SOQL / DML 模式
5. CPU / 堆热点
6. 调用时间点和外部故障

### 3. 分类严重性
- **严重** — 运行时失败、硬限制、损坏风险
- **警告** — 接近限制、非选择查询、慢路径
- **信息** — 优化机会或卫生问题

### 4. 推荐最小的正确修复
优先选择以下修复：
- 以根本原因为导向
- 批量安全
- 可测试
- 易于通过重新运行进行验证

扩展工作流程：[references/analysis-playbook.md](references/analysis-playbook.md)

---

## 高信号问题模式

| 问题 | 主要信号 | 默认修复方向 |
|---|---|---|
| SOQL 在循环中 | 在重复的调用路径中重复 `SOQL_EXECUTE_BEGIN` | 一次性查询，使用映射 / 分组集合 |
| DML 在循环中 | 重复的 `DML_BEGIN` 模式 | 收集行，一次性批量 DML |
| 非选择查询 | 扫描行数高 / 选择性差 | 添加索引过滤器，减少范围 |
| CPU 压力 | CPU 使用接近同步限制 | 降低算法复杂度，缓存，在有效的情况下异步 |
| 堆压力 | 堆使用接近同步限制 | 使用 SOQL for 循环流，减少内存数据 |
| 空指针 / 致命错误 | `EXCEPTION_THROWN` / `FATAL_ERROR` | 保护和修复空假设，处理空查询 |

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
严重性： 严重 | 警告 | 信息
修复： <具体操作>
验证： <测试或重新运行步骤>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 实现Apex修复 | [sf-apex](../sf-apex/SKILL.md) | 代码更改生成 / 审查 |
| 通过测试进行复现 | [sf-testing](../sf-testing/SKILL.md) | 测试执行和覆盖循环 |
| 部署修复 | [sf-deploy](../sf-deploy/SKILL.md) | 部署编排 |
| 创建调试数据 | [sf-data](../sf-data/SKILL.md) | 针对性种子 / 复现数据 |

---

## 参考地图

### 从这里开始
- [references/analysis-playbook.md](references/analysis-playbook.md)
- [references/common-issues.md](references/common-issues.md)
- [references/cli-commands.md](references/cli-commands.md)

### 深入参考
- [references/debug-log-reference.md](references/debug-log-reference.md)
- [references/log-analysis-tools.md](references/log-analysis-tools.md)
- [references/benchmarking-guide.md](references/benchmarking-guide.md)

### 评分标准
- [references/scoring-rubric.md](references/scoring-rubric.md)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 90+ | 专家分析，具有强大的修复指导 |
| 80–89 | 良好分析，存在轻微差距 |
| 70–79 | 可接受，但可能遗漏次要问题 |
| 60–69 | 仅部分诊断 |
| < 60 | 不完整分析 |
