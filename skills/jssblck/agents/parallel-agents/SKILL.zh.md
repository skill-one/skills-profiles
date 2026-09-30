---
name: parallel-agents
description: 当代理在代码库中并发工作时，共享文件频繁出现合并冲突，或需要维护 AGENTS.md 或 CLAUDE.md 文件时使用。
---

# 并行代理

保持独立拥有的工作在共享文件中不发生冲突。当并发工作或观察到的冲突历史证明有必要时，应用结构变更。

- 当这能创建有用的所有权边界时，将独立行为放在自己的文件中。保持对共享注册表的编辑尽可能小。不要仅仅为了实现单行注册而拆分一个连贯的模块。
- 将共享列表调整为便于合并：每行一个项目，稳定的插入顺序，并且不进行无关的重格式化。重新生成生成文件和锁定文件。
- 在拆分之前调查重复的冲突热点。当两者都被请求时，保持结构变更与行为变更分离。
- 保持代理文档简洁：工作协议、不明显约束以及有用的设置/检查入口点。保持模块细节靠近其所有者。

## 参考文献

只阅读与任务相关的参考文献：

- [one-feature-one-file.md](references/one-feature-one-file.md)：为并发功能工作选择文件边界。
- [mergeable-edits.md](references/mergeable-edits.md)：编辑共享注册表、生成文件或冲突分支。
- [hotspot-audit.md](references/hotspot-audit.md)：在请求审计或结构修复时测量冲突热点。
- [doc-gardening.md](references/doc-gardening.md)：维护代理指令或减少重复文档。
