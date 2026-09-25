<!-- GENERATED from convex-agents content/capabilities/convex-advisor.json — do not edit by hand. -->

# 部署顾问

静态审查的猜测；部署本身知道。官方 Convex MCP 会附带一个 `insights` 工具，为每个函数提供类型的 72 小时健康事件——documentsReadLimit / bytesReadLimit（硬限制命中）、documentsReadThreshold / bytesReadThreshold（接近）、occFailedPermanently / occRetried（写竞争）——每个事件都附带证据（table_name、bytes_read、documents_read、occ 文档 ID + 重试次数）。顾问通过读取被标记函数的实际代码，将每个事件转化为根本原因发现，并通过发现总线（specs/finding.schema.json）发出发现，以便分配修复者并评估启动就绪情况。

## 工作流程

1.  **GUARD：** 运行部署-guard 步骤 0-1 —— 识别并宣布正在读取的部署。在生产环境中读取 insights/日志是允许的只读操作；永远不要为建议性检查启用生产环境的修改权限。
2.  **GATHER（确定性，通过官方 Convex MCP）：** `status` → 部署选择器；`insights` → 类型的 72 小时事件；`tables` → 模式 + 行计数；`functionSpec` → 公开/内部接口。`insights` 工具仅在登录用户身份下（不在预览或部署密钥作用范围内）且需要约 72 小时的流量时才可用；如果它返回空或不可用，请说明并回退到提供 convex-reviewer —— 不要编造发现。
3.  **ROOT-CAUSE 每个洞察事件，通过读取被标记函数的代码：**
    -  bytesReadThreshold/Limit 或 documentsReadThreshold/Limit → 查找 `.collect()` / 未索引的 `.filter()` / 缺少分页的命名表；修复方法是索引 + `.withIndex`、`.take(n)` 或 `.paginate`（convex-expert 模式），或使用聚合组件进行计数形状。
    -  occRetried / occFailedPermanently → 查找命名文档上的读-改-写热点（共享计数器、状态切换）；修复方法是 @convex-dev/sharded-counter、缩小读集，或将竞争移至工作池。
    -  `logs` 中重复失败（状态：失败）→ 分类：cron 中的崩溃循环、验证器拒绝、未处理的错误形状。
4.  **EMIT 发现，遵循 specs/finding.schema.json：** 类别 perf/correctness/cost，严重性来自洞察类型（限制命中 = 高，阈值 = 中，重试 = 中，永久 OCC 失败 = 高），位置 {kind: deployment, functionId, tableName}，证据 {kind: insight-event, detail: 原始事件}，置信度：确认（事件已发生——它不是假设），修复能力 + 可自动修复，其中修复是机械的。
5.  **REPORT：** 发现按严重性排序，每个发现包含 (a) 单行中的运行时证据（'messages:list 昨天 31 次从 messages 读取 4.2MB'），(b) 代码级别的根本原因（文件:行），(c) 具体修复和适用能力。提供应用修复的选项；仅在确认后应用，然后在流量后重新运行 `insights` 以验证趋势，或立即重新运行静态检查。
6.  **范围规范：** 这是一个健康/性能/成本检查。将授权发现路由到 convex-authz，代码习惯发现路由到 convex-reviewer，错误分派路由到 sentinel —— 发出一个指针发现而不是重复他们的工作。

## 规则

- 证据而非感觉：每个发现都引用一个真实的洞察事件、日志行或表统计信息——如果部署没有证据，顾问就没有发现（改为提供 convex-reviewer）。
- 构造时只读：建议性检查永远不会修改任何部署，也永远不会启用生产环境修改标志（deploy-guard 规范适用）。
- 报告前代码中的根本原因：洞察事件命名症状；发现必须命名行和机制。
- 在发现总线（specs/finding.schema.json）上发出，置信度：确认——运行时事件是事实，不是假设。
- 严重性来自事件类型：限制命中 / 永久 OCC 失败 = 高；阈值 / 重试 = 中。
- 保持在自己的范围内：仅限 perf/cost/health —— 授权交给 convex-authz，风格交给 convex-reviewer，错误分派交给 sentinel。
- 优先选择组件修复而不是手写，当它们匹配时（sharded-counter 用于 OCC 在计数器上，聚合用于计数扫描）——与 suggest 相同的偏好。
