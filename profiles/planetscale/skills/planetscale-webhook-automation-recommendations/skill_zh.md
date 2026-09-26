# Webhook自动化建议

## 目的

审核并推荐PlanetScale webhook，用于通知人员并触发安全自动化。未经批准，不得创建或更新webhook。

## webhook设计原则

Webhook可能触发自动化，但自动化操作必须默认生成建议、问题、分支或pull请求。未经明确人员批准，不得直接修改生产数据库或生产应用程序行为。

## 需要评估的事件

### 通用和Postgres

- `branch.anomaly`：新的Insights异常。
- `branch.out_of_memory`：Postgres内存溢出事件。
- `branch.primary_promoted`：主故障转移/提升。
- `branch.ready`：分支创建并就绪。
- `branch.sleeping`：分支休眠。
- `branch.start_maintenance`：维护开始。
- `cluster.storage`：存储阈值或增长事件。
- `database.access_request`：访问请求。
- `branch.schema_recommendation`：可用时的模式推荐事件。
- `webhook.test`：测试事件。

### Vitess部署生命周期

- `deploy_request.opened`
- `deploy_request.queued`
- `deploy_request.in_progress`
- `deploy_request.pending_cutover`
- `deploy_request.schema_applied`
- `deploy_request.errored`
- `deploy_request.reverted`
- `deploy_request.closed`
- `keyspace.storage`

## 推荐的路由

### 人员告警

将这些事件发送到事件或运维渠道：

- `branch.anomaly`
- `branch.out_of_memory`
- `branch.primary_promoted`
- `branch.start_maintenance`
- `cluster.storage`
- `keyspace.storage`
- `deploy_request.errored`
- `deploy_request.reverted`

### 工程通知

将这些事件发送到Slack、Linear/Jira或部署渠道：

- `deploy_request.opened`
- `deploy_request.queued`
- `deploy_request.in_progress`
- `deploy_request.pending_cutover`
- `deploy_request.schema_applied`
- `deploy_request.closed`
- `branch.schema_recommendation`

### 代理摄入队列

将这些事件发送到安全的代理工作流：

- `branch.anomaly`
- `branch.schema_recommendation`
- `deploy_request.errored`
- `cluster.storage`
- `keyspace.storage`

代理输出可在无需批准的情况下包括：

- 评估摘要、可能原因、关联的Insights/查询模式。
- 推荐模式、代码、Traffic Control或操作变更。
- 针对应用程序代码的pull请求。
- 应用DDL或迁移的开发分支。
- 在受保护审查的分支中打开部署请求。
- 问题或工单。

代理输出必须自行通过审查门禁：不进行生产部署、PR合并、Traffic Control执行、凭证轮换或网络变更——这些需要人员操作或`../planetscale-autonomous-execution-mode/SKILL.md`中的授权。

## webhook接收器要求

仅推荐符合以下要求的接收器：

- HTTPS端点。
- 快速2xx响应；昂贵的工作异步排队。
- 不依赖重定向。
- 使用PlanetScale webhook签名头和webhook密钥进行签名验证。
- 通过事件ID或时间戳/资源元组实现幂等性。
- 死信队列或重试安全的日志记录。
- 人类可读的审计记录。
- 明确的所有者和升级路径。
- 密钥轮换程序。

## 推荐的自动化流程

### 异常到PR流程

1. 接收`branch.anomaly`。
2. 验证签名。
3. 排队任务。
4. 获取异常详情和相关Insights查询模式。
5. 通过SQLCommenter标签和仓库搜索定位代码路径。
6. 分类为模式、代码、Traffic Control或未知。
7. 生成报告和可选的PR。
8. 要求人员批准影响数据库的工作。

### 模式推荐到分支/部署流程

对于Vitess：

1. 接收`branch.schema_recommendation`。
2. 获取推荐详情。
3. 将DDL应用到开发分支。
4. 打开pull请求，包含指纹、指标和预期效果。
5. 打开部署请求——DR和PR共同构成可审查单元；打开它们无需批准。
6. 在人员批准下部署，或在允许此部署类别的授权下自主执行
   (`../planetscale-autonomous-execution-mode/SKILL.md`)。

对于Postgres：

1. 接收`branch.schema_recommendation`。
2. 获取推荐详情。
3. 将DDL转换为应用程序迁移。
4. 在非生产分支上测试并记录结果到PR中。
5. 打开PR。
6. 通过部署管道合并到生产，或在无管道的情况下经明确批准应用。

### Vitess部署请求生命周期流程

- 打开时通知。
- 验证所有者和关联的应用程序PR。
- 队列或进行中时告警。
- 出错或回滚时强烈告警。
- 通知待切换并要求所有者对受门禁保护的部署进行确认。
- 记录已应用的模式并与应用程序部署关联。

## 需要阻止的反模式

不推荐：

- webhook直接运行生产DDL，绕过PR/部署请求工作流。（通过分支、PR和部署请求驱动DDL是支持模式，不是反模式。）
- webhook直接在生产上应用模式推荐，无可审查的工件。
- webhook直接执行Traffic Control。
- webhook直接更改IP限制。
- webhook直接轮换凭证。
- webhook将密钥或原始SQL带字面量发布到公共Slack频道。
- webhook接收器忽略签名验证。
- webhook接收器在返回2xx之前执行长时间运行的工作。

## 输出

返回：

- 现有webhook清单。
- 缺少的推荐订阅。
- 目标质量审查。
- 签名验证状态。
- 自动化机会。
- 不安全自动化风险。
- 需要批准的webhook变更建议。

结尾：

“未创建、更新或删除任何webhooks或自动化端点。”
