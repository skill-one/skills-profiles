# 注意事项

> 首次使用或遇到认证错误（401 / token 过期 / `未登录`）时，请先阅读 [`../zsxq-shared/SKILL.md`](../zsxq-shared/SKILL.md) 了解登录与 API 调用规范。日常调用已登录账户时无需每次重读。

## 核心概念

- **笔记（Note）**：独立的内容单元，**不属于任何星球**。
- **可见性**：笔记是**公开内容**，任何持有链接的人都能访问 —— 不是私密备忘录。涉及隐私或敏感信息的内容不要写入笔记。

## 快捷操作（推荐优先使用）

| 快捷操作 | 说明 |
|----------|------|
| [`+create`](references/zsxq-note-create.md) | 创建一条公开笔记，支持文本和图片附件 |
| [`+list`](references/zsxq-note-list.md) | 查看自己的笔记列表，支持分页 |
| [`+detail`](references/zsxq-note-detail.md) | 查看单条笔记的完整详情 |
| [`+edit`](references/zsxq-note-edit.md) | 编辑笔记内容，需确认后执行 |
| [`+delete`](references/zsxq-note-delete.md) | 删除笔记（不可恢复），需确认后执行 |
