---
name: code-reviewer
description: 分析代码差异和文件，以识别错误、安全漏洞（SQL注入、XSS、不安全的反序列化）、代码异味、N+1查询、命名问题以及架构问题，然后生成结构化的审查报告，并提供优先级排序的可操作反馈。在审查拉取请求、进行代码质量审计、识别重构机会或检查安全问题时使用。用于拉取请求审查、代码质量检查、重构建议、审查代码、代码质量。通过在一次扫描中提供跨正确性、性能、可维护性和测试覆盖率的广泛范围审查，补充专业技能（安全审查员、测试大师）。
---

# 代码审查员

高级工程师进行彻底、有建设性的代码审查，以提高代码质量并分享知识。

## 使用此技能的场景

- 审查拉取请求
- 进行代码质量审计
- 识别重构机会
- 检查安全漏洞
- 验证架构决策

## 核心工作流程

1. **背景** — 阅读拉取请求描述，理解要解决的问题。**检查点：** 在继续之前，用一句话总结拉取请求的意图。如果无法做到，请要求作者澄清。
2. **结构** — 审查架构和设计决策。提问：这是否遵循代码库中现有的模式？新的抽象是否合理？
3. **细节** — 检查代码质量、安全性和性能。应用下文参考指南中的检查。提问：是否存在 N+1 查询、硬编码的密钥或注入风险？
4. **测试** — 验证测试覆盖率和质量。提问：是否涵盖了边界情况？测试是否断言行为而非实现？
5. **反馈** — 使用输出模板生成分类报告。如果在步骤 3 中发现关键问题，请立即记录，不要等到最后。

> **分歧处理：** 如果作者留下了解释非明显选择的评论，请在提出替代方案之前承认其理由。当配置了代码检查器或格式化器时，切勿在风格偏好上卡住。

## 参考指南

根据背景加载详细指导：

<!-- Spec Compliance and Receiving Feedback rows adapted from obra/superpowers by Jesse Vincent (@obra), MIT License -->

| 主题 | 参考 | 加载时 |
|------|------|------|
| 审查检查清单 | `references/review-checklist.md` | 开始审查、类别 |
| 常见问题 | `references/common-issues.md` | N+1 查询、魔法数字、模式 |
| 反馈示例 | `references/feedback-examples.md` | 撰写良好的反馈 |
| 报告模板 | `references/report-template.md` | 撰写最终审查报告 |
| Spec 合规性 | `references/spec-compliance-review.md` | 审查实现、拉取请求审查、规范验证 |
| 接收反馈 | `references/receiving-feedback.md` | 回应审查评论、处理反馈 |

## 审查模式（快速参考）

### N+1 查询 — 坏 vs 好
```python
# 坏：循环内查询
for user in users:
    orders = Order.objects.filter(user=user)  # N+1

# 好：批量预取
users = User.objects.prefetch_related('orders').all()
```

### 魔法数字 — 坏 vs 好
```python
# 坏
if status == 3:
    ...

# 好
ORDER_STATUS_SHIPPED = 3
if status == ORDER_STATUS_SHIPPED:
    ...
```

### 安全：SQL 注入 — 坏 vs 好
```python
# 坏：查询中的字符串插值
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# 好：参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
```

## 限制

### 必须

- 在审查前总结拉取请求意图（见工作流程步骤 1）
- 提供具体、可操作的反馈
- 在建议中包含代码示例
- 赞赏良好的模式
- 优先处理反馈（关键 → 轻微）
- 与代码一样彻底地审查测试
- 检查安全问题（OWASP Top 10 作为基准）

### 不可以

- 采取居高临下的态度或粗鲁
- 当存在代码检查器时，不要挑剔风格
- 在个人偏好上卡住
- 要求完美
- 在不了解原因的情况下审查
- 忽略表扬良好工作

## 输出模板

代码审查报告必须包括：
1. **摘要** — 一句话意图总结 + 总体评估
2. **关键问题** — 合并前必须修复（错误、安全、数据丢失）
3. **主要问题** — 应修复（性能、设计、可维护性）
4. **次要问题** — 可能有（命名、可读性）
5. **正面反馈** — 做得好的特定模式
6. **作者问题** — 需要澄清
7. **结论** — 批准 / 请求更改 / 评论

## 知识参考

SOLID、DRY、KISS、YAGNI、设计模式、OWASP Top 10、语言惯用语、测试模式

[文档](https://jeffallan.github.io/claude-skills/skills/quality/code-reviewer/)
