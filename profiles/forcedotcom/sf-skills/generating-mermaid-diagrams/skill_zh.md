# generating-mermaid-diagrams：Salesforce 图表生成

当用户需要**基于文本的图表**时使用此技能：用于架构、OAuth、集成流程、ERD（实体关系图）或Agentforce结构的Mermaid图表，并在纯文本兼容性重要时提供ASCII后备方案。

## 范围

### 在范围内
当用户需要时，使用`generating-mermaid-diagrams`：
- Mermaid输出
- ASCII后备图表
- 以markdown友好的形式呈现的架构、序列、流程图或ERD视图
- 可以直接放入文档、README或问题中的图表

### 不在范围内——当用户需要时，将其委托给其他技能：
- 渲染的PNG/SVG图像或精制模型 → [generating-visual-diagrams](../generating-visual-diagrams/SKILL.md)
- 仅针对非Salesforce系统 → 使用更通用的图表绘制技能
- ERD之前的对象发现 → [generating-custom-object](../generating-custom-object/SKILL.md) 或 [generating-custom-field](../generating-custom-field/SKILL.md)

---

## 支持的图表系列

| 类型 | 优选的Mermaid形式 | 典型用途 |
|---|---|---|
| OAuth / 认证流程 | `sequenceDiagram` | 授权码、JWT、PKCE、设备流程 |
| ERD / 数据模型 | `flowchart LR` | 对象关系和共享上下文 |
| 集成序列 | `sequenceDiagram` | 请求/响应或事件编排 |
| 系统景观 | `flowchart` | 高级架构 |
| 角色 / 访问层次结构 | `flowchart` | 用户、配置文件、权限 |
| Agentforce行为映射 | `flowchart` | agent → 主题 → 行为关系 |

---

## 首先收集必要的上下文

请求或推断：
- 图表类型
- 范围和涉及的实体/系统
- 输出偏好：仅Mermaid、仅ASCII或两者
- 是否应采用极简、文档优先或演示友好的样式
- 对于ERD：是否提供组织元数据以作为基础

---

## 推荐的工作流程

### 1. 选择正确的图表结构
- 使用`sequenceDiagram`表示按时间顺序的交互
- 使用`flowchart LR`表示ERD和能力映射
- 尽可能每个图表保持一个主要故事

### 2. 收集数据
对于ERD和有基础的图表：
- 当需要实际模式发现时，使用 [generating-custom-object](../generating-custom-object/SKILL.md) 或 [generating-custom-field](../generating-custom-field/SKILL.md)
- 在适当的情况下，可选地使用本地元数据辅助脚本以获取计数/关系上下文

### 3. 首先生成Mermaid
应用：
- 准确的标签
- 简洁易读的节点文本
- 一致的关系符号
- 受约束的样式，在markdown查看器中清晰渲染

### 4. 在需要时添加ASCII后备方案
当用户需要终端兼容性或纯文本文档时，提供ASCII版本。

### 5. 简要解释图表
指出关键关系、流程方向和任何假设。

---

## 高信号规则

### 对于序列图表
- 当步骤顺序重要时，使用`autonumber`
- 清晰区分请求和响应
- 仅在必要时使用注释表示协议细节

### 对于ERD
- 优先使用`flowchart LR`
- 保持对象卡片简洁
- 使用清晰的关系箭头
- 除非用户明确要求字段级详细信息，否则避免字段过载
- 仅在提高可读性时对对象类型进行着色

### 对于ASCII输出
- 保持宽度合理
- 一致地对齐箭头和框
- 优先考虑可读性而非装饰

---

## 输出格式

````markdown
## <图表标题>

### Mermaid图表
```mermaid
<diagram>
```

### ASCII后备方案
```text
<ascii>
```

### 备注
- <关键点>
- <假设或限制>
````

---

## 跨技能集成

| 需要 | 委托给 | 原因 |
|---|---|---|
| 实际对象/字段定义 | [generating-custom-object](../generating-custom-object/SKILL.md) / [generating-custom-field](../generating-custom-field/SKILL.md) | 基于ERD的生成 |
| 渲染图表/图像输出 | [generating-visual-diagrams](../generating-visual-diagrams/SKILL.md) | 超越Mermaid的视觉润色 |
| 连接应用认证设置上下文 | [configuring-connected-apps](../configuring-connected-apps/SKILL.md) | 准确的OAuth流程 |
| Agentforce逻辑可视化 | [developing-agentforce](../developing-agentforce/SKILL.md) | 源行为细节 |
| Flow行为图表 | [generating-flow](../generating-flow/SKILL.md) | 实际Flow逻辑基础 |

---

## 注意事项

| 问题 | 解决方案 |
|---|---|
| Mermaid渲染器不可用 | 自动提供ASCII后备方案；注意Mermaid块仍然包含图表，可用于复制粘贴到渲染器 |
| ERD因对象过多而难以阅读 | 按领域（Sales、Service等）拆分为子图表，并在正文中链接它们 |
| 序列图表步骤顺序不明确 | 使用`autonumber`指令使步骤顺序明确 |
| OAuth流程参与者因授权类型而异 | 在生成前先阅读相关资产模板，以避免参与者不匹配 |

---

## 参考文件索引

### 惯例和规则——生成前阅读
- [references/diagram-conventions.md](references/diagram-conventions.md) — 所有图表类型的兼容性规则
- [references/mermaid-reference.md](references/mermaid-reference.md) — Mermaid语法快速参考
- [references/usage-examples.md](references/usage-examples.md) — 每种图表类型的实例

### 样式
- [references/mermaid-styling.md](references/mermaid-styling.md) — 主题和注释模式
- [references/color-palette.md](references/color-palette.md) — 色盲友好的调色板，包含十六进制值
- [references/erd-conventions.md](references/erd-conventions.md) — ERD特定的布局和符号规则

### 预览
- [references/preview-guide.md](references/preview-guide.md) — 如何本地渲染Mermaid
- [scripts/README.md](scripts/README.md) — 本技能中所有脚本设置和使用说明
- [scripts/mermaid_preview.py](scripts/mermaid_preview.py) — 实时预览服务器；运行以在浏览器中预览图表
- [scripts/query-org-metadata.py](scripts/query-org-metadata.py) — 查询组织模式以作为ERD生成的基础

### OAuth流程模板——生成OAuth图表时加载匹配的模板
- [assets/oauth/authorization-code.md](assets/oauth/authorization-code.md) — 授权码授权
- [assets/oauth/authorization-code-pkce.md](assets/oauth/authorization-code-pkce.md) — PKCE变体用于移动/SPA
- [assets/oauth/jwt-bearer.md](assets/oauth/jwt-bearer.md) — JWT Bearer服务器到服务器
- [assets/oauth/client-credentials.md](assets/oauth/client-credentials.md) — 客户端凭证服务帐户
- [assets/oauth/device-authorization.md](assets/oauth/device-authorization.md) — 设备流程用于CLI/IoT
- [assets/oauth/refresh-token.md](assets/oauth/refresh-token.md) — 刷新令牌续期流程
- [assets/oauth/user-agent-social-sign-on.md](assets/oauth/user-agent-social-sign-on.md) — User-Agent / 社交登录

### 数据模型ERD模板——生成ERD时加载匹配的模板
- [assets/datamodel/salesforce-erd.md](assets/datamodel/salesforce-erd.md) — 核心Salesforce对象
- [assets/datamodel/sales-cloud-erd.md](assets/datamodel/sales-cloud-erd.md) — Sales Cloud对象
- [assets/datamodel/service-cloud-erd.md](assets/datamodel/service-cloud-erd.md) — Service Cloud对象
- [assets/datamodel/b2b-commerce-erd.md](assets/datamodel/b2b-commerce-erd.md) — B2B Commerce对象
- [assets/datamodel/campaigns-erd.md](assets/datamodel/campaigns-erd.md) — Campaigns和Campaign Member模型
- [assets/datamodel/consent-erd.md](assets/datamodel/consent-erd.md) — 同意和隐私对象
- [assets/datamodel/files-erd.md](assets/datamodel/files-erd.md) — 文件和ContentDocument模型
- [assets/datamodel/forecasting-erd.md](assets/datamodel/forecasting-erd.md) — 预测对象
- [assets/datamodel/fsl-erd.md](assets/datamodel/fsl-erd.md) — Field Service Lightning对象
- [assets/datamodel/party-model-erd.md](assets/datamodel/party-model-erd.md) — Party模型对象
- [assets/datamodel/quote-order-erd.md](assets/datamodel/quote-order-erd.md) — Quote和Order对象
- [assets/datamodel/revenue-cloud-erd.md](assets/datamodel/revenue-cloud-erd.md) — Revenue Cloud对象
- [assets/datamodel/scheduler-erd.md](assets/datamodel/scheduler-erd.md) — Scheduler对象
- [assets/datamodel/territory-management-erd.md](assets/datamodel/territory-management-erd.md) — Territory Management对象

### 其他图表模板
- [assets/architecture/system-landscape.md](assets/architecture/system-landscape.md) — 系统景观概述模板
- [assets/integration/api-sequence.md](assets/integration/api-sequence.md) — API调用序列模板
- [assets/agentforce/agent-flow.md](assets/agentforce/agent-flow.md) — Agentforce agent → 主题 → 行为流
- [assets/role-hierarchy/user-hierarchy.md](assets/role-hierarchy/user-hierarchy.md) — 角色和权限层次结构模板

---

## 输出预期

此技能针对每个请求生成的交付物：

- **Mermaid代码块** — 准备好粘贴到GitHub、Confluence或任何Mermaid支持渲染器的fenced ` ```mermaid ` 块
- **ASCII后备方案**（当请求或Mermaid渲染器不可用时）— 使用框/箭头字符的纯文本图表
- **简要解释** — 2-5个要点，指出关键关系、流程方向以及图表中的任何假设或限制
- 对于ERD：带有字段标签和关系类型注释的对象卡片
- 对于序列图表：带有序号步骤（`autonumber`）和清晰演员标签

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 72–80 | 生产就绪的图表 |
| 60–71 | 清晰且有用，但仍有轻微润色空间 |
| 48–59 | 功能性，但可能不够清晰 |
| 35–47 | 需要结构改进 |
| < 35 | 不准确或不完整 |
