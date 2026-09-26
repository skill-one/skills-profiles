# sf-diagram-mermaid：Salesforce 图表生成

当用户需要**基于文本的图表**时使用此技能：用于架构、OAuth、集成流程、ERD（实体关系图）或Agentforce结构的Mermaid图表，并在纯文本兼容性重要时提供ASCII后备方案。

## 此技能负责任务的情况

当用户需要以下内容时，使用 `sf-diagram-mermaid`：
- Mermaid输出
- ASCII后备图表
- 以Markdown友好形式呈现的架构、时序图、流程图或ERD视图
- 可以直接放入文档、README或问题中的图表

当用户需要以下内容时，将任务委托给其他技能：
- 渲染的PNG/SVG图像或精良的模型 → [sf-diagram-nanobananapro](../sf-diagram-nanobananapro/SKILL.md)
- 仅针对非Salesforce系统 → 使用更通用的图表绘制技能
- ERD之前的对象发现 → [sf-metadata](../sf-metadata/SKILL.md)

---

## 支持的图表系列

| 类型 | 推荐的Mermaid形式 | 典型用途 |
|---|---|---|
| OAuth / 认证流程 | `sequenceDiagram` | 授权码、JWT、PKCE、设备流程 |
| ERD / 数据模型 | `flowchart LR` | 对象关系和共享上下文 |
| 集成时序图 | `sequenceDiagram` | 请求/响应或事件编排 |
| 系统景观 | `flowchart` | 高级架构 |
| 角色/访问层次结构 | `flowchart` | 用户、配置文件、权限 |
| Agentforce行为映射 | `flowchart` | 代理→主题→动作关系 |

---

## 首先收集的必要上下文

询问或推断：
- 图表类型
- 范围和实体/系统涉及
- 输出偏好：仅Mermaid、仅ASCII或两者
- 是否需要极简、文档优先或演示友好的样式
- 对于ERD：是否提供组织元数据以作为基础

---

## 推荐的工作流程

### 1. 选择合适的图表结构
- 使用 `sequenceDiagram` 表示按时间顺序的交互
- 使用 `flowchart LR` 表示ERD和能力映射
- 尽可能每个图表保持一个主要故事

### 2. 收集数据
对于ERD和有基础的图表：
- 当需要真实模式发现时，使用 [sf-metadata](../sf-metadata/SKILL.md)
- 在适当的情况下，可选使用本地元数据辅助脚本获取计数/关系上下文

### 3. 首先生成Mermaid
应用：
- 准确的标签
- 简洁易读的节点文本
- 一致的关系符号
- 受控的样式，在Markdown查看器中清晰渲染

### 4. 在需要时添加ASCII后备方案
当用户需要终端兼容性或纯文本文档时，提供ASCII版本。

### 5. 简要解释图表
指出关键关系、流程方向和任何假设。

---

## 高信号规则

### 对于时序图
- 当步骤顺序重要时，使用 `autonumber`
- 清晰区分请求和响应
- 仅在需要协议细节时少量使用注释

### 对于ERD
- 优先使用 `flowchart LR`
- 保持对象卡片简洁
- 使用清晰的关联箭头
- 除非用户明确要求字段级细节，否则避免字段过载
- 仅在提高可读性时对对象类型进行着色

### 对于ASCII输出
- 保持宽度合理
- 一致对齐箭头和方框
- 优先考虑可读性而非装饰

---

## 输出格式

````markdown
## <图表标题>

### Mermaid图表
```mermaid
<图表>
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

| 需求 | 委托给 | 原因 |
|---|---|---|
| 真实对象/字段定义 | [sf-metadata](../sf-metadata/SKILL.md) | 基于ERD生成 |
| 渲染的图表/图像输出 | [sf-diagram-nanobananapro](../sf-diagram-nanobananapro/SKILL.md) | 超越Mermaid的视觉美化 |
| 连接应用认证设置上下文 | [sf-connected-apps](../sf-connected-apps/SKILL.md) | 准确的OAuth流程 |
| Agentforce逻辑可视化 | [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md) | 源头行为细节 |
| Flow行为图表 | [sf-flow](../sf-flow/SKILL.md) | 实际Flow逻辑基础 |

---

## 参考图

### 从这里开始
- [references/diagram-conventions.md](references/diagram-conventions.md)
- [references/mermaid-reference.md](references/mermaid-reference.md)
- [references/usage-examples.md](references/usage-examples.md)

### 样式 / ERD特定
- [references/mermaid-styling.md](references/mermaid-styling.md)
- [references/color-palette.md](references/color-palette.md)
- [references/erd-conventions.md](references/erd-conventions.md)

### 预览
- [references/preview-guide.md](references/preview-guide.md)
- [scripts/mermaid_preview.py](scripts/mermaid_preview.py)
- [scripts/query-org-metadata.py](scripts/query-org-metadata.py)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 72–80 | 生产就绪的图表 |
| 60–71 | 清晰有用，但仍有少量润色空间 |
| 48–59 | 功能性，但可以更清晰 |
| 35–47 | 需要结构改进 |
| < 35 | 不准确或不完整 |
