# 请求代码审查

派遣代码审查子代理以在问题级联之前捕获问题。审查者获得精确定制的上下文进行评估——永远不会是您的会话历史记录。

**核心原则：** 早期审查，频繁审查。

## 何时请求审查

**强制要求：**
- 子代理驱动开发中的每个任务后
- 完成主要功能后
- 合并到主分支前

**可选但有价值：**
- 卡壳时（获得新视角）
- 重构前（基线检查）
- 修复复杂 Bug 后

## 如何请求

**1. 获取 git SHAs：**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # 或: git merge-base origin/main HEAD
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 派遣代码审查子代理：**

派遣一个 `general-purpose` 子代理，填写模板 [code-reviewer.md](code-reviewer.md)

**占位符：**
- `{DESCRIPTION}` - 您所构建的简要摘要
- `{PLAN_OR_REQUIREMENTS}` - 它应该做什么
- `{BASE_SHA}` - 起始提交
- `{HEAD_SHA}` - 结束提交

**3. 根据反馈采取行动：**
- 立即修复严重问题
- 在继续前修复重要问题
- 记录轻微问题以备后用
- 如果审查者错误，则提出异议（并说明理由）

## 示例

```
[刚刚完成任务 2：添加验证函数]

您：让我在继续前请求代码审查。

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[派遣代码审查子代理]
  DESCRIPTION: 添加了 verifyIndex() 和 repairIndex() 以及 4 种问题类型
  PLAN_OR_REQUIREMENTS: 来自 docs/superpowers/plans/deployment-plan.md 的任务 2
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661

[子代理返回]:
  优点：清晰的架构，真实的测试
  问题：
    重要：缺少进度指示器
    轻微：报告间隔的魔法数字 (100)
  评估：可以继续

您：[修复进度指示器]
[继续到任务 3]
```

## 常见借口

| 借口 | 现实 |
|------|------|
| "我宁愿自己审查 diff 而不是派遣审查者" | 您是协调者——在行内审查 diff 会消耗您需要保持工作推进的上下文窗口。派遣代码审查子代理：diff 和评估都存在于其上下文中，只有结果会返回给您。 |
| "审查者需要我的整个会话历史记录来理解变更" | 提供精确定制的上下文，永远不会提供您的会话历史记录。这能让审查者专注于工作产品，而不是您的思维过程。 |

## 严重警告

**永远不要：**
- 因为“很简单”而跳过审查
- 忽略严重问题
- 在未修复的重要问题前继续
- 与有效的技术反馈争论

**如果审查者错误：**
- 提出技术理由进行异议
- 展示代码/测试来证明它有效
- 请求澄清

参考模板：[code-reviewer.md](code-reviewer.md)
