# 建议优秀的 GitHub Copilot 提示

分析当前仓库上下文，并从 [GitHub awesome-copilot 仓库](https://github.com/github/awesome-copilot/blob/main/docs/README.prompts.md) 中建议相关的提示文件，这些文件在当前仓库中尚未可用。

## 流程

1. **获取可用提示**：从 [awesome-copilot README.prompts.md](https://github.com/github/awesome-copilot/blob/main/docs/README.prompts.md) 中提取提示列表和描述。必须使用 `#fetch` 工具。
2. **扫描本地提示**：发现 `.github/prompts/` 文件夹中的现有提示文件
3. **提取描述**：从本地提示文件中读取前文以获取描述
4. **获取远程版本**：对于每个本地提示，使用原始 GitHub URL 从 awesome-copilot 仓库中获取对应的版本（例如，`https://raw.githubusercontent.com/github/awesome-copilot/main/prompts/<filename>`）
5. **比较版本**：比较本地提示内容与远程版本，以识别：
   - 保持在最新状态的提示（完全匹配）
   - 过期的提示（内容不同）
   - 过期提示中的关键差异（工具、描述、内容）
6. **分析上下文**：审查聊天历史记录、仓库文件和当前项目需求
7. **对比现有**：检查此仓库中已可用的提示
8. **匹配相关性**：将可用提示与识别出的模式和需求进行比较
9. **展示选项**：显示相关提示及其描述、理由和可用状态，包括过期的提示
10. **验证**：确保建议的提示能补充现有提示未覆盖的价值
11. **输出**：提供结构化表格，包含建议、描述以及指向 awesome-copilot 提示和类似本地提示的链接
    **AWAIT** 用户请求进行特定提示的安装或更新。除非得到指示，否则不要安装或更新。
12. **下载/更新资源**：对于请求的提示，自动：
    - 将新提示下载到 `.github/prompts/` 文件夹
    - 通过用 awesome-copilot 中的最新版本替换来更新过期的提示
    - 不要调整文件内容
    - 使用 `#fetch` 工具下载资源，但可以使用 `#runInTerminal` 工具通过 `curl` 确保所有内容都被检索
    - 使用 `#todos` 工具跟踪进度

## 上下文分析标准

🔍 **仓库模式**：
- 使用的编程语言（.cs、.js、.py 等）
- 框架指示器（ASP.NET、React、Azure 等）
- 项目类型（Web 应用、API、库、工具）
- 文档需求（README、规范、ADR）

🗨️ **聊天历史上下文**：
- 近期讨论和痛点
- 功能请求或实现需求
- 代码审查模式
- 开发工作流要求

## 输出格式

以结构化表格形式显示分析结果，比较 awesome-copilot 提示和现有仓库提示：

| Awesome-Copilot Prompt | Description | 已安装 | 相似本地提示 | 建议理由 |
|-------------------------|-------------|--------|--------------|----------|
| [code-review.prompt.md](https://github.com/github/awesome-copilot/blob/main/prompts/code-review.prompt.md) | 自动化代码审查提示 | ❌ 未安装 | 无 | 将通过标准化的代码审查流程增强开发工作流 |
| [documentation.prompt.md](https://github.com/github/awesome-copilot/blob/main/prompts/documentation.prompt.md) | 生成项目文档 | ✅ 已安装且最新 | create_oo_component_documentation.prompt.md | 已由现有文档提示覆盖 |
| [debugging.prompt.md](https://github.com/github/awesome-copilot/blob/main/prompts/debugging.prompt.md) | 调试辅助提示 | ⚠️ 过期 | debugging.prompt.md | 工具配置不同：远程使用 `'codebase'` 而本地缺失 - 建议更新 |

## 本地提示发现流程

1. 列出 `.github/prompts/` 目录中的所有 `*.prompt.md` 文件
2. 对于每个发现的文件，读取前文以提取 `description`
3. 构建现有提示的全面清单
4. 使用此清单以避免建议重复项

## 版本比较流程

1. 对于每个本地提示文件，构造获取远程版本的原始 GitHub URL：
   - 模式：`https://raw.githubusercontent.com/github/awesome-copilot/main/prompts/<filename>`
2. 使用 `#fetch` 工具获取远程版本
3. 比较整个文件内容（包括前文和正文）
4. 识别具体差异：
   - **前文变化**（描述、工具、模式）
   - **工具数组修改**（添加、删除或重命名工具）
   - **内容更新**（说明、示例、指南）
5. 记录过期提示的关键差异
6. 计算相似度以确定是否需要更新

## 要求

- 使用 `githubRepo` 工具从 awesome-copilot 仓库的提示文件夹中获取内容
- 扫描本地文件系统以查找 `.github/prompts/` 目录中的现有提示
- 从本地提示文件中读取 YAML 前文以提取描述
- 比较本地提示与远程版本以检测过期提示
- 与此仓库中现有的提示进行比较以避免重复
- 专注于当前提示库覆盖的空白
- 验证建议的提示与仓库的目的和标准一致
- 为每个建议提供清晰的理由
- 包含指向 awesome-copilot 提示和类似本地提示的链接
- 清晰标识过期提示并注明具体差异
- 不要提供表格和分析之外的任何附加信息或上下文

## 图标参考

- ✅ 已安装且最新
- ⚠️ 已安装但过期（可更新）
- ❌ 未在仓库中安装

## 更新处理

当识别出过期提示时：
1. 在输出表格中包含它们并标记为 ⚠️ 状态
2. 在“建议理由”列中记录具体差异
3. 提供更新建议并注明关键变化
4. 当用户请求更新时，用远程版本替换整个本地文件
5. 保留文件位置在 `.github/prompts/` 目录中
