# 请求代码评审

派遣代码评审子代理，在问题扩散前及时发现问题。评审者获得针对评估精心准备的上下文——绝不用你的会话历史。

**核心原则：** 尽早评审，经常评审。

## 何时请求评审

**必须：**
- 在子代理驱动开发的每个任务完成后
- 在完成重大功能后
- 在合并到 main 前

**可选但有价值：**
- 卡住时（获得新视角）
- 重构前（基线检查）
- 修复复杂缺陷后

## 如何请求

**1. 获取 git SHA：**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or: git merge-base origin/main HEAD
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 派遣代码评审子代理：**

派遣一个 `general-purpose` 子代理，填写 [code-reviewer.md](code-reviewer.md) 中的模板

**占位符：**
- `{DESCRIPTION}` - 你所构建内容的简要摘要
- `{PLAN_OR_REQUIREMENTS}` - 它应该实现的功能
- `{BASE_SHA}` - 起始提交
- `{HEAD_SHA}` - 结束提交

**3. 根据反馈采取行动：**
- 立即修复严重问题
- 在继续之前修复重要问题
- 将次要问题记下，稍后处理
- 如果评审者有误（附带理由）予以反驳

## 示例

```
[刚刚完成 Task 2：添加验证函数]

你：在继续之前，让我请求代码评审。

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[派遣代码评审子代理]
  DESCRIPTION: 添加了 verifyIndex() 和 repairIndex()，包含 4 种问题类型
  PLAN_OR_REQUIREMENTS: 来自 docs/superpowers/plans/deployment-plan.md 的 Task 2
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661

[子代理返回]:
  Strengths: 架构清晰，测试真实有效
  Issues:
    Important: 缺少进度指示器
    Minor: 报告间隔的魔数（100）
  Assessment: 可以继续

你：[修复进度指示器]
[继续到 Task 3]
```

## 常见开脱理由

 | 现实 |
|--------|---------|

 | 开脱理由 | 现实 |

"我会直接自己评审 diff，而不派遣评审者" | 你是协调者——内联评审 diff 会消耗你保持工作推进所需的上下文窗口。派遣评审子代理：diff 和评估在子代理的上下文中，只有结果会反馈给你。

"评审者需要我的整个会话历史才能理解改动" | 提供精心准备的上下文，绝不用你的会话历史。这能让评审者专注于工作产物，而非你的思考过程。

## 危险信号

**绝不：**
- 因为"简单"而跳过评审
- 忽略严重问题
- 在重要问题未修复的情况下继续
- 与合理的技术反馈争辩

**如果评审者有误：**
- 附带技术理由予以反驳
- 展示证明其可行的代码/测试
- 请求澄清

查看模板：[code-reviewer.md](code-reviewer.md)
