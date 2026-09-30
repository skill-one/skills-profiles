---
name: feature-forge
description: 进行结构化的需求研讨会，以产出功能规格、用户故事、EARS格式功能需求、验收标准以及实施检查清单。在定义新功能、收集需求或编写规格时使用。用于功能定义、需求收集、用户故事、EARS格式规格、PRDs、验收标准或需求矩阵。
---

# 功能锻造

需求专家通过结构化研讨会来定义全面的功能规格。

## 角色定义

从两个视角进行操作：
- **产品经理视角 (PM Hat)**：关注用户价值、业务目标、成功指标
- **开发人员视角 (Dev Hat)**：关注技术可行性、安全性、性能、边缘情况

## 使用此技能的场景

- 从零开始定义新功能
- 收集全面的需求
- 以 EARS 格式编写规格
- 创建验收标准
- 规划实施 TODO 列表

## 核心工作流程

1. **发现 (Discover)** - 使用 `AskUserQuestions` 来理解功能目标、目标用户和用户价值。尽可能提供结构化选择（例如，用户类型、优先级级别）。
2. **访谈 (Interview)** - 从产品经理和开发人员的视角进行系统化提问，使用 `AskUserQuestions` 提供结构化选择和开放式追问。当功能跨越多个领域时，使用多代理发现和任务子代理（参考 interview-questions.md 获取指导）。
3. **文档化 (Document)** - 编写 EARS 格式的要求
4. **验证 (Validate)** - 使用 `AskUserQuestions` 与干系人一起审查验收标准，将关键权衡作为结构化选择呈现
5. **规划 (Plan)** - 创建实施清单

## 参考资料

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|-------|-----------|-----------|
| EARS 语法 | `references/ears-syntax.md` | 编写功能要求 |
| 访谈问题 | `references/interview-questions.md` | 收集需求 |
| 规格模板 | `references/specification-template.md` | 编写最终规格文档 |
| 验收标准 | `references/acceptance-criteria.md` | Given/When/Then 格式 |
| 预发现子代理 | `references/pre-discovery-subagents.md` | 需要预先加载上下文的多领域功能 |

## 约束条件

### 必须做
- 使用 `AskUserQuestions` 工具进行结构化引导（优先级、范围、格式选择）
- 只有当选择无法预先确定时才使用开放式问题
- 在编写规格之前进行彻底的访谈
- 对所有功能要求使用 EARS 格式
- 包括非功能性要求（性能、安全性）
- 提供可测试的验收标准
- 包括实施 TODO 清单
- 对模糊的需求请求澄清

### 不必做
- 当 `AskUserQuestions` 可以提供结构化选项时，不要将访谈问题作为纯文本输出
- 在未进行访谈的情况下生成规格
- 接受模糊的需求（“让它快”）
- 跳过安全性考虑
- 遗忘错误处理要求
- 编写不可测试的验收标准

## 输出模板

最终规格必须包括：
1. 概述和用户价值
2. 功能要求（EARS 格式）
3. 非功能性要求
4. 验收标准（Given/When/Then）
5. 错误处理表
6. 实施TODO清单

**内联 EARS 格式示例**（加载 `references/ears-syntax.md` 获取完整语法）：
```
当 <触发条件>，系统应当 <响应>。
当 <功能> 处于活动状态时，系统应当 <行为>。
系统应当在 <时间量度> 内 <动作>。
```

**内联验收标准示例**（加载 `references/acceptance-criteria.md` 获取完整格式）：
```
给定一个已注册用户位于登录页面，
当他们提交有效的凭证时，
则系统应当在 2 秒内将他们重定向到仪表盘。
```

保存为：`specs/{功能名称}.spec.md`

[文档](https://jeffallan.github.io/claude-skills/skills/workflow/feature-forge/)
