# sf-ai-agentforce-observability：Agentforce会话追踪提取与分析

当用户需要**基于追踪的观测性**，而不仅仅是测试时，请使用此技能：提取会话追踪数据模型（STDM）记录，处理Parquet数据集，重建会话时间线，分析主题/操作延迟，或从Data 360遥测数据中调试代理行为。

## 此技能负责的任务场景

当工作涉及以下内容时，使用 `sf-ai-agentforce-observability`：
- Data 360 / 会话追踪提取
- Agentforce遥测产生的 `.parquet` 文件
- 会话时间线重建
- 基于追踪的主题路由、操作失败或延迟调试
- 基于Polars / PyArrow的大规模遥测数据集分析

当用户处于以下情况时，应将任务委托给其他技能：
- 正式测试代理 → [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md)
- 调试Apex日志 → [sf-debug](../sf-debug/SKILL.md)
- 编写或重新配置代理本身 → [sf-ai-agentforce](../sf-ai-agentforce/SKILL.md) 或 [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md)

---

## 必须存在的先决条件

提取之前，请验证：
- Data 360已启用
- 会话追踪已启用
- Salesforce标准数据模型版本足够
- 组织中已启用Einstein / Agentforce功能
- 已配置JWT / ECA认证以访问Data 360

如果认证缺失，请转交给：
- [sf-connected-apps](../sf-connected-apps/SKILL.md)

深度设置指南：
- [references/auth-setup.md](references/auth-setup.md)

---

## 此技能适用的内容

### 核心存储/分析模型
- 通过Data 360 API进行提取
- 使用Parquet提高存储效率
- 使用Polars进行大规模惰性分析

### 核心STDM实体
至少需要围绕以下内容进行工作：
- 会话
- 交互 / 轮次
- 交互步骤
- 瞬间
- 消息

GenAI信任层/审计记录也可能与内容质量和生成调试相关。

完整模式：
- [references/data-model-reference.md](references/data-model-reference.md)

---

## 首先收集所需的上下文

请求或推断：
- 目标组织别名
- 时间窗口或日期范围
- 代理过滤器（如果有）
- 目标是提取、摘要分析还是单会话调试
- 提取数据的输出位置
- 用户是否已在磁盘上拥有Parquet文件

---

## 推荐的工作流程

### 1. 验证设置和认证
确认Data 360追踪存在且JWT/ECA认证正常工作。

### 2. 选择提取模式
| 需求 | 默认方法 |
|---|---|
| 最近遥测快照 | 提取最近N天 |
| 聚焦调查 | 按日期和代理进行过滤提取 |
| 单个故障对话 | 提取或调试单个会话树 |
| 持续使用分析 | 增量提取 |

### 3. 提取到Parquet
使用`scripts/`目录下的提供脚本，而不是重新实现提取逻辑。

### 4. 使用Polars进行分析
常见分析目标：
- 会话量和持续时间
- 主题分布
- 操作步骤失败
- 延迟热点
- 放弃/升级模式
- 会话级时间线重建

### 5. 将发现转化为后续行动
典型结果：
- 主题不匹配 → 改进路由或描述
- 操作失败 → 检查Flow / Apex实现
- 延迟问题 → 优化下游操作路径
- 测试差距 → 添加目标代理测试

---

## 高信号操作规则

- 将STDM视为**只读遥测数据**
- 预期存在摄入延迟；这不是完美的实时调试
- 使用日期过滤器和聚焦提取以避免不必要的量/查询成本
- 优先选择Parquet而不是临时JSON进行持久分析
- 使用惰性Polars模式处理大数据集

常见陷阱：
- 假设缺失数据意味着没有问题，而实际上追踪可能未启用
- 无日期或代理过滤器运行巨大泛查询
- 在此技能中尝试修复代理，而不是转交给编写/测试技能

---

## 输出格式

完成任务时，按以下顺序报告：
1. **提取或分析了哪些数据**
2. **范围**（组织、日期、代理过滤器、会话ID）
3. **关键发现**
4. **可能的原因**
5. **推荐的后续技能/行动**

建议格式：

```text
观测性任务：<提取 / 分析 / 调试会话>
范围：<组织、日期、代理、会话ID>
工件：<目录 / Parquet文件>
发现：<延迟、路由、操作、质量、放弃模式>
原因：<当前最佳解释>
下一步：<测试、代理修复、Flow修复、Apex修复>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 认证/JWT设置 | [sf-connected-apps](../sf-connected-apps/SKILL.md) | Data 360访问 |
| 修复代理路由/行为 | [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md) | 编写修正 |
| 正式回归/覆盖测试 | [sf-ai-agentforce-testing](../sf-ai-agentforce-testing/SKILL.md) | 可重复的测试循环 |
| Flow支持的行动调试 | [sf-flow](../sf-flow/SKILL.md) | 声明式修复 |
| Apex支持的行动调试 | [sf-debug](../sf-debug/SKILL.md) 或 [sf-apex](../sf-apex/SKILL.md) | 代码/日志调查 |

---

## 参考地图

### 从这里开始
- [README.md](README.md)
- [references/basic-extraction.md](references/basic-extraction.md)
- [references/filtered-extraction.md](references/filtered-extraction.md)
- [references/cli-reference.md](references/cli-reference.md)

### 数据模型/查询
- [references/data-model-reference.md](references/data-model-reference.md)
- [references/query-patterns.md](references/query-patterns.md)
- [references/client-demo-queries.md](references/client-demo-queries.md)

### 分析/调试
- [references/analysis-cookbook.md](references/analysis-cookbook.md)
- [references/analysis-examples.md](references/analysis-examples.md)
- [references/debugging-sessions.md](references/debugging-sessions.md)
- [references/polars-cheatsheet.md](references/polars-cheatsheet.md)
- [references/agent-execution-lifecycle.md](references/agent-execution-lifecycle.md)

### 认证/故障排除
- [references/auth-setup.md](references/auth-setup.md)
- [references/troubleshooting.md](references/troubleshooting.md)
- [references/billing-and-troubleshooting.md](references/billing-and-troubleshooting.md)
- [references/builder-trace-api.md](references/builder-trace-api.md)
- [scripts/](scripts/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 90+ | 强大的遥测数据支持诊断 |
| 75–89 | 有用的分析，但存在轻微差距 |
| 60–74 | 仅部分可见性 |
| < 60 | 证据不足；收集更多遥测数据 |
