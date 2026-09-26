# sf-integration：Salesforce 集成模式专家

当用户需要**集成架构和运行时管道**时，请使用此技能：命名凭证、外部凭证、外部服务、REST/SOAP 调用模式、平台事件、CDC（变更数据捕获）以及事件驱动集成设计。

## 此技能负责任务的情况

当工作涉及以下内容时，请使用 `sf-integration`：
- `.namedCredential-meta.xml` 或外部凭证元数据
- 外部 REST/SOAP 调用
- 从 OpenAPI 规范中注册外部服务
- 平台事件、CDC 和事件驱动架构
- 选择同步与异步集成模式

当用户需要以下内容时，请委派给其他技能：
- 配置 OAuth 应用本身 → [sf-connected-apps](../sf-connected-apps/SKILL.md)
- 仅编写 Apex 业务逻辑 → [sf-apex](../sf-apex/SKILL.md)
- 部署元数据 → [sf-deploy](../sf-deploy/SKILL.md)
- 导入/导出数据 → [sf-data](../sf-data/SKILL.md)

---

## 首先收集必要的上下文

询问或推断：
- 集成风格：外部调用、内部事件、外部服务、CDC、平台事件
- 认证方法
- 同步与异步需求
- 系统端点/规范细节
- 速率限制、重试预期和容错能力
- 这是全新的设计还是修复现有集成

---

## 推荐的工作流程

### 1. 选择集成模式
| 需求 | 默认模式 |
|---|---|
| 带认证的外部 API 调用 | 命名凭证/外部凭证 + Apex 或 Flow |
| 规范驱动的 API 客户端 | 外部服务 |
| 触发器发起的调用 | 异步调用模式 |
| 解耦的事件发布 | 平台事件 |
| 变更流消费 | CDC |

### 2. 选择认证模型
优先选择安全的运行时管理认证：
- 命名凭证/外部凭证
- 通过正确的凭证模型进行 OAuth 或 JWT 认证
- 代码中不硬编码密钥

### 3. 从正确的模板生成
使用提供的资源，位于：
- `assets/named-credentials/`
- `assets/external-credentials/`
- `assets/external-services/`
- `assets/callouts/`
- `assets/platform-events/`
- `assets/cdc/`
- `assets/soap/`

### 4. 验证运行时安全性
检查：
- 超时和重试处理
- 触发器发起工作的异步策略
- 日志记录/可观察性
- 事件保留和订阅者影响

### 5. 移交部署或实现细节
使用：
- [sf-deploy](../sf-deploy/SKILL.md) 进行部署
- [sf-apex](../sf-apex/SKILL.md) 进行更深入的服务/重试代码
- [sf-flow](../sf-flow/SKILL.md) 进行声明式 HTTP 调用编排

---

## 高信号规则

- 永不硬编码凭证
- 触发器中不要进行同步调用
- 明确定义超时行为
- 为瞬态故障计划重试
- 当外部调用量高时，使用中间件/事件驱动模式
- 当支持时，优先为新的开发使用外部凭证架构

常见反模式：
- 同步触发器调用
- 无重试或死信策略
- 无请求/响应日志记录
- 将认证设置责任与运行时集成设计混合

---

## 输出格式

完成时，按以下顺序报告：
1. **选择的集成模式**
2. **选择的认证模型**
3. **创建或更新的文件**
4. **运行时安全措施**
5. **部署/测试下一步**

建议格式：

```text
集成： <摘要>
模式： <命名凭证/外部服务/事件/CDC/调用>
文件： <路径>
安全： <超时、重试、异步、日志记录>
下一步： <部署、注册、测试或实现>
```

---

## 跨技能集成

| 需求 | 委派给 | 原因 |
|---|---|---|
| OAuth 应用设置 | [sf-connected-apps](../sf-connected-apps/SKILL.md) | 消费者密钥/证书/应用配置 |
| 高级调用服务代码 | [sf-apex](../sf-apex/SKILL.md) | Apex 实现 |
| 声明式 HTTP 调用/Flow 包装器 | [sf-flow](../sf-flow/SKILL.md) | Flow 编排 |
| 部署集成元数据 | [sf-deploy](../sf-deploy/SKILL.md) | 验证和发布 |
| 从 Agentforce 使用集成 | [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md) | 代理操作组合 |

---

## 参考地图

### 从这里开始
- [references/named-credentials-guide.md](references/named-credentials-guide.md)
- [references/external-services-guide.md](references/external-services-guide.md)
- [references/callout-patterns.md](references/callout-patterns.md)
- [references/security-best-practices.md](references/security-best-practices.md)

### 事件驱动/平台模式
- [references/event-patterns.md](references/event-patterns.md)
- [references/platform-events-guide.md](references/platform-events-guide.md)
- [references/cdc-guide.md](references/cdc-guide.md)
- [references/event-driven-architecture-guide.md](references/event-driven-architecture-guide.md)
- [references/messaging-api-v2.md](references/messaging-api-v2.md)

### CLI/自动化/评分
- [references/cli-reference.md](references/cli-reference.md)
- [references/named-credentials-automation.md](references/named-credentials-automation.md)
- [references/scoring-rubric.md](references/scoring-rubric.md)
- [assets/](assets/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 108+ | 强大的生产就绪集成设计 |
| 90–107 | 良好设计，但仍有加固空间 |
| 72–89 | 可用但需要架构审查 |
| < 72 | 不安全/不完整，不适合部署 |
