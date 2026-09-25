# sf-apex：Salesforce Apex 代码生成与审查

当用户需要**生产 Apex**时（例如新类、触发器、选择器、服务、异步作业、可调用方法、测试类，或基于证据的现有 `.cls` / `.trigger` 代码的审查），请使用此技能。

## 此技能负责任务的条件

当工作涉及以下内容时，请使用 `sf-apex`：
- Apex 类生成或重构
- 触发器设计和触发器框架决策
- `@InvocableMethod`、Queueable、Batch、Schedulable 或测试类工作
- 批量化、共享、安全性、测试或可维护性的审查

当用户处于以下情况时，请委派给其他技能：
- 编辑 LWC JavaScript / HTML / CSS → [sf-lwc](../sf-lwc/SKILL.md)
- 构建Flow XML或Flow编排 → [sf-flow](../sf-flow/SKILL.md)
- 仅编写SOQL → [sf-soql](../sf-soql/SKILL.md)
- 部署或验证元数据到组织 → [sf-deploy](../sf-deploy/SKILL.md)

---

## 首先收集必要的上下文

请求或推断：
- 类类型：触发器、服务、选择器、批处理、Queueable、Schedulable、Invocable、测试
- 目标对象和业务目标
- 代码是全新、重构还是修复
- 组织 / API 限制（如果已知）
- 预期的测试覆盖率或部署目标

在编写之前，检查项目结构：
- 现有类 / 触发器
- 当前触发器框架或处理模式
- 相关的测试、流程和选择器
- 是否已使用 TAF

---

## 推荐的工作流程

### 1. 发现本地架构
检查：
- 现有的触发器处理程序 / 框架
- 服务选择器域约定
- 相关的测试和数据工厂
- 仓库中已使用的可调用或异步模式

### 2. 选择最小的正确模式
| 需求 | 推荐模式 |
|---|---|
| 简单可重用逻辑 | 服务类 |
| 查询密集型数据访问 | 选择器 |
| 单个对象触发器行为 | 一个触发器 + 处理程序 / TAF操作 |
| Flow需要复杂逻辑 | `@InvocableMethod` |
| 后台处理 | 默认Queueable |
| 非常大的数据集 | Batch Apex或`Database.Cursor`模式 |
| 可重复的验证 | 专用测试类 + 测试数据工厂 |

### 3. 带有约束条件的编写
生成符合以下条件的代码：
- 批量安全
- 意识到共享
- 在适用情况下CRUD/FLS安全
- 可独立测试
- 与项目命名和分层一致

### 4. 验证和评分
在交接之前，根据150分评分标准进行评估。

### 5. 交接部署/测试下一步
当需要组织验证时，交接给：
- [sf-testing](../sf-testing/SKILL.md) 用于测试执行循环
- [sf-deploy](../sf-deploy/SKILL.md) 用于部署 / 模拟运行 / 验证

---

## 生成约束条件

未经明确停止和解释问题，永远不要生成以下内容：

| 反模式 | 原因 |
|---|---|
| 循环中的SOQL | 限制失败 |
| 循环中的DML | 限制失败 |
| 缺少共享模型 | 安全性 / 数据暴露风险 |
| 硬编码ID | 部署和可移植性失败 |
| 空的`catch`块 | 静默失败 / 差的观察性 |
| 基于用户输入构建的SOQL | 注入风险 |
| 没有断言的测试 | 假阳性测试套件 |

默认修复方向：
- 一次查询，对集合进行操作
- 除非另有理由，否则使用`with sharing`
- 在适当的地方使用绑定变量和`WITH USER_MODE`
- 为正面、负面和批量情况创建断言

参见 [references/anti-patterns.md](references/anti-patterns.md) 和 [references/security-guide.md](references/security-guide.md)。

---

## 高信号构建规则

### 触发器架构
- 优先**每个对象一个触发器**。
- 如果TAF已经安装并使用，请扩展它而不是发明第二个触发器模式。
- 触发器应委托逻辑；避免在触发器体中直接放置重业务逻辑。

### 异步选择
| 场景 | 默认 |
|---|---|
| 标准异步工作 | Queueable |
| 非常大的记录处理 | Batch Apex |
| 定期计划 | Scheduled Flow或Schedulable |
| 作业后清理 | Finalizer |
| 长时间运行的Lightning调用 | `Continuation` |

### 测试最小值
对每个功能使用**PNB**模式：
- **正面**路径
- **负面** / 错误路径
- **批量**路径（相关情况下251+记录）

### 现代Apex期望
在可用时优先使用当前惯用法：
- 安全导航：`obj?.Field__c`
- 空值合并：`value ?? fallback`
- `Assert.*` 覆盖旧断言风格
- `WITH USER_MODE` 和相关显式安全处理

---

## 输出格式

完成时，按以下顺序报告：
1. **创建或审查的内容**
2. **更改的文件**
3. **关键设计决策**
4. **风险 / 约束条件注释**
5. **测试指南**
6. **部署指南**

建议格式：

```text
Apex工作：<摘要>
文件：<路径>
设计：<模式 / 框架选择>
风险：<安全性、批量化、异步、依赖性注释>
测试：<运行 / 添加什么>
部署：<模拟运行或下一步>
```

---

## LSP验证说明

此技能支持`.cls`和`.trigger`文件的LSP辅助编写循环：
- 语法问题可以在写入/编辑后立即检测到
- 技能可以在短时间内自动修复常见语法错误
- 语义质量仍然取决于150分审查评分标准

完整指南：[references/troubleshooting.md](references/troubleshooting.md#lsp-based-validation-auto-fix-loop)

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 首先描述对象 / 字段 | [sf-metadata](../sf-metadata/SKILL.md) | 避免针对错误模式编码 |
| 种子批量或边缘情况数据 | [sf-data](../sf-data/SKILL.md) | 创建现实的测试数据集 |
| 运行Apex测试 / 修复失败的测试 | [sf-testing](../sf-testing/SKILL.md) | 执行和迭代失败 |
| 部署到组织 | [sf-deploy](../sf-deploy/SKILL.md) | 验证和部署编排 |
| 构建调用Apex的Flow | [sf-flow](../sf-flow/SKILL.md) | 声明性编排 |
| 构建调用Apex的LWC | [sf-lwc](../sf-lwc/SKILL.md) | UI/控制器集成 |

---

## 参考地图

### 从这里开始
- [references/patterns-deep-dive.md](references/patterns-deep-dive.md)
- [references/security-guide.md](references/security-guide.md)
- [references/bulkification-guide.md](references/bulkification-guide.md)
- [references/testing-patterns.md](references/testing-patterns.md)

### 高信号检查清单
- [references/code-review-checklist.md](references/code-review-checklist.md)
- [references/anti-patterns.md](references/anti-patterns.md)
- [references/naming-conventions.md](references/naming-conventions.md)

### 专用模式
- [references/trigger-actions-framework.md](references/trigger-actions-framework.md)
- [references/automation-density-guide.md](references/automation-density-guide.md)
- [references/flow-integration.md](references/flow-integration.md)
- [references/triangle-pattern.md](references/triangle-pattern.md)
- [references/design-patterns.md](references/design-patterns.md)
- [references/solid-principles.md](references/solid-principles.md)

### 故障排除 / 验证
- [references/troubleshooting.md](references/troubleshooting.md)
- [references/llm-anti-patterns.md](references/llm-anti-patterns.md)
- [references/testing-guide.md](references/testing-guide.md)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 120+ | 强大的生产就绪Apex |
| 90–119 | 良好实现，部署前审查 |
| 67–89 | 可接受但需要改进 |
| < 67 | 阻止部署 |
