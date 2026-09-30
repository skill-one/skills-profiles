---
name: nemo-rl-docs
description: NeMo-RL的文档规范。涵盖docs/index.md的更新和docstring格式。不应用于：修复bug、修复测试、依赖版本更新、重构、CI/CD变更、性能调优或任何不涉及编写或更新文档的任务。
---

# 文档规范

## 保持 docs/index.md 更新

当在 `docs/**/*.md` 下添加新的 markdown 文档或重命名 markdown 文件时，确保 @docs/index.md 被更新，并且文档出现在最合适的章节中。

## 文档字符串格式

为类和函数使用 [Google 风格](https://google.github.io/styleguide/pyguide.html) 的文档字符串。这些文档字符串可以被 Sphinx 解析。

对于可能在文件外部使用的接口，优先使用文档字符串而不是注释。注释应保留在函数内或文件本地接口的代码中。

## 记录新功能

当添加新功能时，更新或创建与功能最匹配的 `docs/` 目录中的文档。查看现有文档以找到最佳匹配——如果没有，则创建新文档并将其添加到 @docs/index.md。

对于 bug 修复或 CI 相关的更改，**不需要**进行文档更改。
