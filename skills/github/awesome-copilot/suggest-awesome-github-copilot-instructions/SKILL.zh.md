---
name: suggest-awesome-github-copilot-instructions
description: 根据当前仓库上下文和聊天历史，从 awesome-copilot 仓库中推荐相关的 GitHub Copilot 指令文件，避免与该仓库中现有的指令重复，并识别需要更新的过时指令。
---

# 建议优秀的 GitHub Copilot 指令

分析当前仓库上下文，并从 [GitHub awesome-copilot 仓库](https://github.com/github/awesome-copilot/blob/main/docs/README.instructions.md) 中建议相关的 copilot-instruction 文件，这些文件尚未在此仓库中可用。

## 流程

1. **获取可用指令**：从 [awesome-copilot README.instructions.md](https://github.com/github/awesome-copilot/blob/main/docs/README.instructions.md) 中提取指令列表和描述。必须使用 `#fetch` 工具。
2. **扫描本地指令**：发现 `.github/instructions/` 文件夹中现有的指令文件
3. **提取描述**：从本地指令文件中读取前端元数据，以获取描述和 `applyTo` 模式
4. **获取远程版本**：对于每个本地指令，使用原始 GitHub URL 从 awesome-copilot 仓库中获取相应的版本（例如，`https://raw.githubusercontent.com/github/awesome-copilot/main/instructions/<filename>`）
5. **比较版本**：比较本地指令内容与远程版本，以识别：
   - 日期最新的指令（完全匹配）
   - 过期的指令（内容不同）
   - 过期指令中的关键差异（描述、applyTo 模式、内容）
6. **分析上下文**：审查聊天历史记录、仓库文件和当前项目需求
7. **比较现有指令**：检查此仓库中已可用的指令
8. **匹配相关性**：将可用指令与识别的模式和需求进行比较
9. **展示选项**：显示相关指令及其描述、理由和可用状态，包括过期的指令
10. **验证**：确保建议的指令将增加现有指令未涵盖的价值
11. **输出**：提供结构化表格，包含建议、描述以及指向 awesome-copilot 指令和类似本地指令的链接
    **AWAIT** 用户请求进行特定指令的安装或更新。除非得到指示，否则不要安装或更新。
12. **下载/更新资源**：对于请求的指令，自动：
    - 将新指令下载到 `.github/instructions/` 文件夹
    - 通过用 awesome-copilot 中的最新版本替换来更新过期的指令
    - 不要调整文件内容
    - 使用 `#fetch` 工具下载资源，但可以使用 `#runInTerminal` 工具通过 `curl` 确保所有内容都被检索
    - 使用 `#todos` 工具跟踪进度

## 上下文分析标准

🔍 **仓库模式**：
- 使用的编程语言（.cs、.js、.py、.ts 等）
- 框架指示器（ASP.NET、React、Azure、Next.js 等）
- 项目类型（Web 应用、API、库、工具）
- 开发工作流需求（测试、CI/CD、部署）

🗨️ **聊天历史上下文**：
- 近期讨论和痛点
- 特定技术的提问
- 编码标准讨论
- 开发工作流需求

## 输出格式

以结构化表格形式显示分析结果，比较 awesome-copilot 指令和现有仓库指令：

| Awesome-Copilot 指令 | 描述 | 已安装 | 相似的本地指令 | 建议理由 |
|----------------------|------|--------|----------------|----------|
| [blazor.instructions.md](https://github.com/github/awesome-copilot/blob/main/instructions/blazor.instructions.md) | Blazor 开发指南 | ✅ 是 | blazor.instructions.md | 已由现有 Blazor 指令覆盖 |
| [reactjs.instructions.md](https://github.com/github/awesome-copilot/blob/main/instructions/reactjs.instructions.md) | ReactJS 开发标准 | ❌ 否 | 无 | 将通过成熟模式增强 React 开发 |
| [java.instructions.md](https://github.com/github/awesome-copilot/blob/main/instructions/java.instructions.md) | Java 开发最佳实践 | ⚠️ 过期 | java.instructions.md | applyTo 模式不同：远程使用 `'**/*.java'` 而本地使用 `'*.java'` - 建议更新 |

## 本地指令发现流程

1. 列出 `instructions/` 目录中的所有 `*.instructions.md` 文件
2. 对于每个发现的文件，读取前端元数据以提取 `description` 和 `applyTo` 模式
3. 构建现有指令的全面清单及其适用的文件模式
4. 使用此清单以避免建议重复项

## 版本比较流程

1. 对于每个本地指令文件，构造用于获取远程版本的原始 GitHub URL：
   - 模式：`https://raw.githubusercontent.com/github/awesome-copilot/main/instructions/<filename>`
2. 使用 `#fetch` 工具获取远程版本
3. 比较整个文件内容（包括前端元数据和正文）
4. 识别具体差异：
   - **前端元数据变化**（描述、applyTo 模式）
   - **内容更新**（指南、示例、最佳实践）
5. 记录过期指令的关键差异
6. 计算相似度以确定是否需要更新

## 文件结构要求

根据 GitHub 文档，copilot-instructions 文件应满足以下要求：
- **仓库级指令**：`.github/copilot-instructions.md`（适用于整个仓库）
- **路径特定指令**：`.github/instructions/NAME.instructions.md`（通过 `applyTo` 前端元数据适用于特定文件模式）
- **社区指令**：`instructions/NAME.instructions.md`（用于共享和分发）

## 前端元数据结构

awesome-copilot 中的指令文件使用以下前端元数据格式：
```markdown
---
description: '简要描述此指令提供的功能'
applyTo: '**/*.js,**/*.ts' # 可选：用于文件匹配的 glob 模式
---
```

## 要求

- 使用 `githubRepo` 工具获取 awesome-copilot 仓库指令文件夹的内容
- 扫描本地文件系统以查找 `.github/instructions/` 目录中的现有指令
- 从本地指令文件中读取 YAML 前端元数据以提取描述和 `applyTo` 模式
- 比较本地指令与远程版本以检测过期指令
- 与此仓库中现有的指令进行比较以避免重复
- 专注于当前指令库覆盖的空白
- 验证建议的指令与仓库的目的和标准一致
- 为每个建议提供清晰的理由
- 包括指向 awesome-copilot 指令和类似本地指令的链接
- 清晰地标识过期的指令并注明具体差异
- 考虑技术栈兼容性和项目特定需求
- 不要提供表格和分析之外的任何附加信息或上下文

## 图标参考

- ✅ 已安装且最新
- ⚠️ 已安装但过期（可更新）
- ❌ 仓库中未安装

## 更新处理

当识别到过期指令时：
1. 在输出表格中包含它们并标记为 ⚠️ 状态
2. 在“建议理由”列中记录具体差异
3. 提供更新建议并注明关键变化
4. 当用户请求更新时，用远程版本替换整个本地文件
5. 保留文件位置在 `.github/instructions/` 目录中
