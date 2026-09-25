# UI Bundle 功能特性

## 安装预构建功能

在从零开始构建之前，始终检查是否已存在该功能。功能 CLI 会将预构建、经过测试的包安装到 Salesforce UI bundle 中——从基础 UI 库（shadcn/ui）到全栈功能（身份验证、搜索、导航、GraphQL、Agentforce AI）。

### 工作流程

1. **首先搜索项目代码** — 在安装任何内容之前，检查 `src/` 目录下是否已有实现。将搜索范围限制在 `src/` 目录内，以避免匹配 `node_modules/` 或 `dist/` 目录。

2. **搜索可用功能** — 使用 `npx @salesforce/ui-bundle-features list` 并配合 `--search <query>` 参数按关键词过滤。使用 `--verbose` 参数获取完整描述。

3. **描述功能** — 使用 `npx @salesforce/ui-bundle-features describe <feature>` 查看组件、依赖项、复制操作和示例文件。

4. **安装** — 使用 `npx @salesforce/ui-bundle-features install <feature> --ui-bundle-dir <name>`。关键选项：
   - `--dry-run` 用于预览变更
   - `--yes` 用于非交互模式（跳过冲突检测）
   - `--on-conflict error` 用于检测冲突，然后使用 `--conflict-resolution <file>` 解决冲突

如果找不到匹配的功能，在构建自定义实现前询问用户——可能存在名称不同的相关功能。

### 冲突处理

在非交互式环境中，使用两步法：首先运行 `--on-conflict error` 检测冲突，然后创建一个解决方案 JSON 文件（`{ "path": "skip" | "overwrite" }`）并重新运行 `--conflict-resolution`。

### 安装后：集成示例文件

功能可能包含 `__example__` 文件，展示集成模式。对于每个文件：

1. 阅读示例文件以理解模式
2. 阅读目标文件（在 `describe` 输出中显示）
3. 将示例文件中的模式应用到目标文件
4. 成功集成后删除示例文件

### 提示占位符

某些复制路径使用 `<descriptive-name>` 占位符（例如 `<desired-page-with-search-input>`），CLI 不会解析这些占位符。安装后，将文件重命名或移动到目标位置，或将它们的模式集成到现有文件中。
