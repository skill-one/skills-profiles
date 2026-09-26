# sf-flow：Salesforce 流程创建与验证

当用户需要**流程设计或流程 XML 工作**时使用此技能：记录触发、屏幕、自动启动、计划或平台事件流程，包括验证、架构选择和安全部署顺序。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `sf-flow`：
- `.flow-meta.xml` 文件
- 流程构建器架构和 XML 生成
- 记录触发、屏幕、计划、自动启动或平台事件流程
- 流程特定的批量安全、错误路径和子流程编排

当用户处于以下情况时，将任务委托给其他技能：
- 首先编写 Apex 自动化 → [sf-apex](../sf-apex/SKILL.md)
- 首先创建对象/字段 → [sf-metadata](../sf-metadata/SKILL.md)
- 部署元数据 → [sf-deploy](../sf-deploy/SKILL.md)
- 种子部署后测试数据 → [sf-data](../sf-data/SKILL.md)

---

## 首先收集的必要上下文

询问或推断：
- 流程类型
- 触发对象/入口条件
- 核心业务目标
- 这是新建、重构还是修复
- 如果需要部署或验证，请提供目标组织别名
- 相关对象/字段是否已存在

---

## 推荐的工作流程

### 1. 选择合适的自动化工具
在构建之前，确认流程是正确的答案，而不是：
- 公式字段
- 验证规则
- 汇总字段
- Apex

### 2. 选择合适的流程类型
| 需求 | 默认流程类型 |
|---|---|
| 保存前更新同一记录 | 保存前记录触发 |
| 相关记录工作/邮件/调用 | 保存后记录触发 |
| 引导式 UI | 屏幕流程 |
| 可重用后台逻辑 | 自动启动/子流程 |
| 计划处理 | 计划流程 |
| 事件驱动声明式响应 | 平台事件流程 |
| AI 评估的路由（情感、意图、语气） | 带有 AI 决策元素的自动启动 |

### 3. 从模板开始
优先使用提供的资源：
- `assets/record-triggered-before-save.xml`
- `assets/record-triggered-after-save.xml`
- `assets/screen-flow-template.xml`
- `assets/autolaunched-flow-template.xml`
- `assets/scheduled-flow-template.xml`
- `assets/platform-event-flow-template.xml`
- `assets/ai-decision-template.xml`
- `assets/subflows/`

### 4. 针对流程约束进行验证
关注：
- 循环中无 DML
- 循环内无获取记录
- 正确的错误路径
- 正确的触发条件
- 安全的子流程组合
- AI 决策元素不在循环内（每次迭代产生信用成本）
- AI 决策提示包含合并字段引用以提供数据上下文

### 5. 接管部署和测试
使用：
- [sf-deploy](../sf-deploy/SKILL.md) 用于部署/干运行
- [sf-data](../sf-data/SKILL.md) 用于高容量测试数据

---

## 高信号规则

### 流程架构
- 同一记录字段更新使用保存前
- 保存后用于相关记录、邮件和调用
- 不要循环遍历 `$Record`
- 当逻辑变得宽泛或重复时使用子流程

### 批量安全
- 循环中无 DML
- 循环中无获取记录
- 当批量行为重要时，使用 **251+ 记录**进行测试
- 当工作是在塑造数据而不是逐记录分支时，优先使用转换

### 错误处理
- 每个更改数据的路径应有错误处理
- 避免自引用的错误连接器
- 当激活风险非 trivial 时，首先以草稿形式部署流程

---

## 输出格式

完成时按以下顺序报告：
1. **流程类型和目标**
2. **创建或更新的文件**
3. **架构选择**
4. **批量/错误处理备注**
5. **部署/测试下一步**

建议格式：

```text
流程： <名称>
类型： <流程类型>
文件： <路径>
设计： <触发选择、子流程、关键决策>
风险： <批量安全、错误路径、依赖关系>
下一步： <干运行部署、激活或测试>
```

---

## 流程测试（CLI）

从命令行（无需 VS Code）运行流程测试：

```bash
# 运行所有流程测试
sf flow run test --target-org <别名> --json

# 运行特定流程的测试
sf flow run test --class-names MyFlow --target-org <别名> --json

# 获取异步运行的结果
sf flow get test --test-run-id <id> --target-org <别名> --json
```

流程测试在组织中执行，可能需要 1-5 分钟。`sf flow run test` 返回异步运行的测试运行 ID；使用 `sf flow get test` 检索后续结果。始终使用 `--json` 并对较长的运行使用后台执行。

---

## 跨技能集成

| 需求 | 委托给 | 原因 |
|---|---|---|
| 首先创建对象/字段 | [sf-metadata](../sf-metadata/SKILL.md) | 模式准备 |
| 部署/激活流程 | [sf-deploy](../sf-deploy/SKILL.md) | 安全部署顺序 |
| 创建逼真的批量测试数据 | [sf-data](../sf-data/SKILL.md) | 部署后验证 |
| 创建 Apex 动作/可调用项 | [sf-apex](../sf-apex/SKILL.md) | 命令式逻辑 |
| 在屏幕流程中嵌入 LWC | [sf-lwc](../sf-lwc/SKILL.md) | 自定义 UI 组件 |
| 将流程暴露给 Agentforce | [sf-ai-agentscript](../sf-ai-agentscript/SKILL.md) | 代理操作编排 |

---

## 参考地图

### 从这里开始
- [references/flow-best-practices.md](references/flow-best-practices.md)
- [references/flow-quick-reference.md](references/flow-quick-reference.md)
- [references/orchestration.md](references/orchestration.md)
- [references/testing-guide.md](references/testing-guide.md)

### 设计/编排
- [references/subflow-library.md](references/subflow-library.md)
- [references/governance-checklist.md](references/governance-checklist.md)
- [references/transform-vs-loop-guide.md](references/transform-vs-loop-guide.md)
- [references/orchestration-guide.md](references/orchestration-guide.md)
- [references/orchestration-parent-child.md](references/orchestration-parent-child.md)
- [references/orchestration-sequential.md](references/orchestration-sequential.md)
- [references/orchestration-conditional.md](references/orchestration-conditional.md)

### AI 决策
- [references/ai-decision-guide.md](references/ai-decision-guide.md)

### 屏幕/集成/故障排除
- [references/form-building-guide.md](references/form-building-guide.md)
- [references/integration-patterns.md](references/integration-patterns.md)
- [references/lwc-integration-guide.md](references/lwc-integration-guide.md)
- [references/agentforce-flow-integration.md](references/agentforce-flow-integration.md)
- [references/xml-gotchas.md](references/xml-gotchas.md)
- [references/testing-checklist.md](references/testing-checklist.md)
- [references/wait-patterns.md](references/wait-patterns.md)
- [assets/](assets/)

---

## 评分指南

| 评分 | 含义 |
|---|---|
| 88+ | 生产就绪的流程 |
| 75–87 | 良好流程，但有部分待审核项 |
| 60–74 | 功能性但需要更强的约束 |
| < 60 | 不安全/不完整，不适合部署 |
