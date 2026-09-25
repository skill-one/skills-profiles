# building-sf-integrations：Salesforce 集成模式专家

在用户需要**集成架构和运行时管道**时使用此技能：命名凭证、外部凭证、外部服务、REST/SOAP 调用模式、平台事件、CDC（变更数据捕获）以及事件驱动集成设计。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `building-sf-integrations`：
- `.namedCredential-meta.xml` 或外部凭证元数据
- 外发 REST/SOAP 调用
- 从 OpenAPI 规范中注册外部服务
- 平台事件、CDC 和事件驱动架构
- 选择同步与异步集成模式

当用户处于以下情况时，应将任务委托给其他技能：
- 配置 OAuth 应用本身 → [configuring-connected-apps](../configuring-connected-apps/SKILL.md)
- 仅编写 Apex 业务逻辑 → [generating-apex](../generating-apex/SKILL.md)
- 部署元数据 → [deploying-metadata](../deploying-metadata/SKILL.md)
- 导入/导出数据 → [handling-sf-data](../handling-sf-data/SKILL.md)

---

## 首先收集的必要上下文

请求或推断：
- 集成风格：外发调用、传入事件、外部服务、CDC、平台事件
- 认证方法
- 同步与异步需求
- 系统端点/规范细节
- 速率限制、重试预期和容错能力
- 这是全新设计还是现有集成的修复

---

## 推荐的工作流程

### 1. 选择集成模式
| 需求 | 默认模式 |
|---|---|
| 经过认证的外发 API 调用 | 命名凭证/外部凭证 + Apex 或 Flow |
| 规范驱动 API 客户端 | 外部服务 |
| 触发器发起的调用 | 异步调用模式 |
| 解耦事件发布 | 平台事件 |
| 变更流消费 | CDC |

### 2. 选择认证模型
优先选择安全的运行时管理认证：
- 命名凭证/外部凭证
- 通过正确的凭证模型进行 OAuth 或 JWT 认证
- 代码中不硬编码密钥

### 3. 从正确的模板生成
使用提供的资源，位于以下路径：
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
- [deploying-metadata](../deploying-metadata/SKILL.md) 用于部署
- [generating-apex](../generating-apex/SKILL.md) 用于更深入的服务/重试代码
- [generating-flow](../generating-flow/SKILL.md) 用于声明式 HTTP 调用编排

---

## 高信号规则

- 永不硬编码凭证
- 触发器中不进行同步调用
- 明确定义超时行为
- 为瞬态故障计划重试
- 当外发量高时使用中间件/事件驱动模式
- 当支持时，优先为全新开发选择外部凭证架构

常见反模式：
- 同步触发器调用
- 无重试或死信策略
- 无请求/响应日志记录
- 将认证设置责任与运行时集成设计混合

---

## 输出格式

完成任务后，按以下顺序报告：
1. **选择的集成模式**
2. **选择的认证模型**
3. **创建或更新的文件**
4. **运行时安全措施**
5. **部署/测试下一步**

建议格式：

```text
集成： <摘要>
模式： <命名凭证 / 外部服务 / 事件 / CDC / 调用>
文件： <路径>
安全： <超时、重试、异步、日志记录>
下一步： <部署、注册、测试或实现>
```

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| OAuth 应用设置 | [configuring-connected-apps](../configuring-connected-apps/SKILL.md) | 消费者密钥/证书/应用配置 |
| 高级调用服务代码 | [generating-apex](../generating-apex/SKILL.md) | Apex 实现 |
| 声明式 HTTP 调用/Flow 包装器 | [generating-flow](../generating-flow/SKILL.md) | Flow 编排 |
| 部署集成元数据 | [deploying-metadata](../deploying-metadata/SKILL.md) | 验证和发布 |
| 从 Agentforce 使用集成 | [developing-agentforce](../developing-agentforce/SKILL.md) | agent 行为组合 |

---

## 参考地图

### 从这里开始
- [references/named-credentials-guide.md](references/named-credentials-guide.md)
- [references/external-services-guide.md](references/external-services-guide.md)
- [references/callout-patterns.md](references/callout-patterns.md)
- [references/rest-callout-patterns.md](references/rest-callout-patterns.md)
- [references/security-best-practices.md](references/security-best-practices.md)

### 事件驱动/平台模式
- [references/event-patterns.md](references/event-patterns.md)
- [references/platform-events-guide.md](references/platform-events-guide.md)
- [references/cdc-guide.md](references/cdc-guide.md)
- [references/event-driven-architecture-guide.md](references/event-driven-architecture-guide.md)
- [references/messaging-api-v2.md](references/messaging-api-v2.md)

### CLI / 自动化 / 评分
- [references/cli-reference.md](references/cli-reference.md)
- [references/named-credentials-automation.md](references/named-credentials-automation.md)
- [references/scoring-rubric.md](references/scoring-rubric.md)
- [scripts/README.md](scripts/README.md) — 自动化脚本概述 (configure-named-credential.sh, set-api-credential.sh)

### 资源模板
- `assets/named-credentials/` — 命名凭证 XML 模板（OAuth、JWT、证书、自定义认证）
- `assets/external-credentials/` — 外部凭证 XML 模板（OAuth、JWT）
- `assets/external-services/` — 外部服务注册模板和操作指南
- `assets/callouts/` — REST 同步、可排队、重试处理和 HTTP 响应处理 Apex 模板
- `assets/platform-events/` — 平台事件定义、发布者和订阅者模板
- `assets/cdc/` — CDC 处理器和订阅者触发器模板
- `assets/soap/` — SOAP 调用服务模板和 wsdl2apex 指南
- `assets/endpoint-security/` — 远程站点设置和 CSP 受信任站点 XML 模板

### 自动化钩子
- `hooks/scripts/suggest_credential_setup.py` — 检测集成文件时自动建议凭证配置步骤
- `hooks/scripts/validate_integration.py` — 在 agent 响应前验证集成模式

---

## 输出预期

当此技能完成集成任务时，它将生成：

1. **凭证元数据** — 一个或多个位于 `assets/named-credentials/` 或 `assets/external-credentials/` 的文件，填充了组织特定的值
2. **调用 Apex 类** — 一个 `.cls` 文件，使用命名凭证模式，根据上下文选择异步/同步模式
3. **事件/CDC 产物** — 平台事件 `.object-meta.xml`、订阅者触发器或 CDC 配置（当选择事件驱动模式时）
4. **端点安全元数据** — 远程站点设置和/或 CSP 受信任站点 XML 文件
5. **评分报告** — 跨 6 个类别（安全、错误处理、批量化、架构、最佳实践、文档）的 120 分评分
6. **下一步** — 为生成的资源提供的部署或测试说明

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 108+ | 强大的生产就绪集成设计 |
| 90–107 | 良好设计，但仍有加固空间 |
| 72–89 | 可用但需要架构审查 |
| < 72 | 不安全/不完整，不适合部署 |
