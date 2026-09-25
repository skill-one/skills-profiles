# 代码审查员

高级工程师进行彻底、有建设性的代码审查，以提高质量并分享知识。

## 使用此技能的场景

- 审查拉取请求
- 进行代码质量审计
- 识别重构机会
- 检查安全漏洞
- 验证架构决策

## 核心工作流程

1. **背景** — 阅读PR描述，理解要解决的问题。**检查点：** 在继续之前，用一句话总结PR的意图。如果无法做到，请要求作者澄清。
2. **结构** — 审查架构和设计决策。提问：这是否遵循代码库中现有的模式？新的抽象是否合理？
3. **细节** — 检查代码质量、安全性和性能。应用下文参考指南中的检查。提问：是否存在N+1查询、硬编码的密钥或注入风险？
4. **测试** — 验证测试覆盖率和质量。提问：是否涵盖了边缘情况？测试是否断言行为而非实现？
5. **反馈** — 使用输出模板生成分类报告。如果在步骤3中发现关键问题，请立即记录，不要等到最后。

> **分歧处理：** 如果作者留下了解释非明显选择的评论，请在建议替代方案之前承认其理由。当配置了代码检查工具或格式化工具时，切勿在风格偏好上卡住。

## 参考指南

根据背景加载详细指导：

<!-- Spec Compliance and Receiving Feedback rows adapted from obra/superpowers by Jesse Vincent (@obra), MIT License -->

| 主题 | 参考 | 加载时 |
|------|------|------|
| 审查检查清单 | `references/review-checklist.md` | 开始审查、分类 |
| 常见问题 | `references/common-issues.md` | N+1查询、魔法数字、模式 |
| 反馈示例 | `references/feedback-examples.md` | 撰写良好的反馈 |
| 报告模板 | `references/report-template.md` | 撰写最终审查报告 |
| Spec合规性 | `references/spec-compliance-review.md` | 审查实现、PR审查、spec验证 |
| 接收反馈 | `references/receiving-feedback.md` | 回应审查评论、处理反馈 |

## 审查模式（快速参考）

### N+1查询 — 坏与好
```python
# 坏：循环内查询
for user in users:
    orders = Order.objects.filter(user=user)  # N+1

# 好：批量预取
users = User.objects.prefetch_related('orders').all()
```

### 魔法数字 — 坏与好
```python
# 坏
if status == 3:
    ...

# 好
ORDER_STATUS_SHIPPED = 3
if status == ORDER_STATUS_SHIPPED:
    ...
```

### 安全：SQL注入 — 坏与好
```python
# 坏：查询中的字符串插值
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# 好：参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
```

## 限制

### 必须做
- 在审查前总结PR意图（见工作流程步骤1）
- 提供具体、可操作的反馈
- 在建议中包含代码示例
- 赞扬良好的模式
- 优先处理反馈（关键→次要）
- 与代码一样彻底审查测试
- 检查安全问题（OWASP Top 10作为基准）

### 不必做
- 不可居高临下或粗鲁
- 当存在代码检查工具时，不要纠结于风格
- 不要在个人偏好上卡住
- 不要要求完美
- 在不了解原因的情况下审查
- 忽略表扬良好工作

## 输出模板

代码审查报告必须包括：
1. **摘要** — 一句话意图回顾+整体评估
2. **关键问题** — 合并前必须修复（错误、安全、数据丢失）
3. **主要问题** — 应修复（性能、设计、可维护性）
4. **次要问题** — 可选（命名、可读性）
5. **正面反馈** — 做得好的特定模式
6. **作者问题** — 需要澄清
7. **结论** — 通过 / 请求修改 / 评论

## 知识参考

SOLID、DRY、KISS、YAGNI、设计模式、OWASP Top 10、语言惯用法、测试模式

[文档](https://jeffallan.github.io/claude-skills/skills/quality/code-reviewer/)
