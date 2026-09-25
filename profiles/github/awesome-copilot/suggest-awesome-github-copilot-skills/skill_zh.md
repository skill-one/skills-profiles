# 建议酷炫的 GitHub Copilot 技能

分析当前仓库上下文，并从 [GitHub awesome-copilot 仓库](https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md) 中建议相关的 Agent 技能，这些技能在此仓库中尚未可用。Agent 技能是位于 awesome-copilot 仓库 [skills](https://github.com/github/awesome-copilot/tree/main/skills) 文件夹中的自包含文件夹，每个文件夹包含一个 `SKILL.md` 文件，其中包含说明和可选捆绑资源。

## 流程

1. **获取可用技能**：从 [awesome-copilot README.skills.md](https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md) 中提取技能列表和描述。必须使用 `#fetch` 工具。
2. **扫描本地技能**：发现 `.github/skills/` 文件夹中的现有技能文件夹
3. **提取描述**：从本地 `SKILL.md` 文件中读取前端元数据以获取 `name` 和 `description`
4. **获取远程版本**：对于每个本地技能，使用原始 GitHub URL 从 awesome-copilot 仓库获取相应的 `SKILL.md`（例如，`https://raw.githubusercontent.com/github/awesome-copilot/main/skills/<skill-name>/SKILL.md`）
5. **比较版本**：比较本地技能内容与远程版本以识别：
   - 已更新的技能（完全匹配）
   - 已过时的技能（内容不同）
   - 过时技能中的关键差异（描述、说明、捆绑资源）
6. **分析上下文**：审查聊天历史记录、仓库文件和当前项目需求
7. **比较现有技能**：检查此仓库中已可用的技能
8. **匹配相关性**：将可用技能与识别出的模式和需求进行比较
9. **展示选项**：显示相关技能及其描述、理由和可用状态，包括过时技能
10. **验证**：确保建议的技能将增加现有技能未覆盖的价值
11. **输出**：提供包含建议、描述以及指向 awesome-copilot 技能和类似本地技能的链接的结构化表格
    **AWAIT** 用户请求安装或更新特定技能。除非得到指示，否则不要安装或更新。
12. **下载/更新资源**：对于请求的技能，自动：
    - 将新技能下载到 `.github/skills/` 文件夹，保留文件夹结构
    - 通过用 awesome-copilot 的最新版本替换来更新过时技能
    - 下载 `SKILL.md` 和任何捆绑资源（脚本、模板、数据文件）
    - 不要调整文件内容
    - 使用 `#fetch` 工具下载资源，但可以使用 `#runInTerminal` 工具使用 `curl` 确保所有内容都检索到
    - 使用 `#todos` 工具跟踪进度

## 上下文分析标准

🔍 **仓库模式**：
- 使用的编程语言（.cs、.js、.py、.ts 等）
- 框架指示器（ASP.NET、React、Azure、Next.js 等）
- 项目类型（Web 应用、API、库、工具、基础设施）
- 开发工作流需求（测试、CI/CD、部署）
- 基础设施和云提供商（Azure、AWS、GCP）

🗨️ **聊天历史上下文**：
- 近期讨论和痛点
- 功能请求或实施需求
- 代码审查模式
- 开发工作流需求
- 专用任务需求（绘图、评估、部署）

## 输出格式

以结构化表格形式显示分析结果，比较 awesome-copilot 技能与现有仓库技能：

| Awesome-Copilot 技能 | 描述 | 捆绑资源 | 已安装 | 相似本地技能 | 建议理由 |
|-----------------------|-------------|----------------|-------------------|---------------------|---------------------|
| [gh-cli](https://github.com/github/awesome-copilot/tree/main/skills/gh-cli) | GitHub CLI 技能，用于管理仓库和工作流 | 无 | ❌ 未安装 | 无 | 将增强 GitHub 工作流自动化能力 |
| [aspire](https://github.com/github/awesome-copilot/tree/main/skills/aspire) | Aspire 技能，用于分布式应用开发 | 9 个参考文件 | ✅ 已安装 | aspire | 已由现有 Aspire 技能覆盖 |
| [terraform-azurerm-set-diff-analyzer](https://github.com/github/awesome-copilot/tree/main/skills/terraform-azurerm-set-diff-analyzer) | 分析 Terraform AzureRM 提供商变更 | 参考文件 | ⚠️ 过时 | terraform-azurerm-set-diff-analyzer | 说明已更新新的验证模式 - 建议更新 |

## 本地技能发现流程

1. 列出 `.github/skills/` 目录中的所有文件夹
2. 对于每个文件夹，读取 `SKILL.md` 前端元数据以提取 `name` 和 `description`
3. 列出每个技能文件夹中的捆绑资源
4. 构建现有技能的全面清单及其功能
5. 使用此清单以避免建议重复项

## 版本比较流程

1. 对于每个本地技能文件夹，构造获取远程 `SKILL.md` 的原始 GitHub URL：
   - 模式：`https://raw.githubusercontent.com/github/awesome-copilot/main/skills/<skill-name>/SKILL.md`
2. 使用 `#fetch` 工具获取远程版本
3. 比较整个文件内容（包括前端元数据和正文）
4. 识别具体差异：
   - **前端元数据变化**（名称、描述）
   - **说明更新**（指南、示例、最佳实践）
   - **捆绑资源变化**（新增、移除或修改的资源）
5. 记录过时技能的关键差异
6. 计算相似度以确定是否需要更新

## 技能结构要求

根据 Agent 技能规范，每个技能是一个包含以下内容的文件夹：
- **`SKILL.md`**：主说明文件，包含前端元数据（`name`、`description`）和详细说明
- **可选捆绑资源**：脚本、模板、参考数据和其他从 `SKILL.md` 引用的文件
- **文件夹命名**：小写并用连字符（例如，`azure-deployment-preflight`）
- **名称匹配**：`SKILL.md` 前端元数据中的 `name` 字段必须与文件夹名称匹配

## 前端元数据结构

awesome-copilot 中的技能在 `SKILL.md` 中使用以下前端元数据格式：

```markdown
---
name: 'skill-name'
description: '简要描述此技能提供的内容及其使用场景'
---
```

## 要求

- 使用 `fetch` 工具从 awesome-copilot 仓库技能文档获取内容
- 使用 `githubRepo` 工具获取单个技能内容以供下载
- 扫描本地文件系统以查找 `.github/skills/` 目录中的现有技能
- 从本地 `SKILL.md` 文件中读取 YAML 前端元数据以提取名称和描述
- 比较本地技能与远程版本以检测过时技能
- 与此仓库中现有的技能进行比较以避免重复
- 专注于当前技能库覆盖的空白
- 验证建议的技能与仓库的目的和技术栈一致
- 为每个建议提供清晰的理由
- 包括指向 awesome-copilot 技能和类似本地技能的链接
- 清晰地标识过时技能并注明具体差异
- 考虑捆绑资源要求和兼容性
- 不要提供表格和分析之外的任何附加信息或上下文

## 图标参考

- ✅ 已安装且最新
- ⚠️ 已安装但过时（可更新）
- ❌ 仓库中未安装

## 更新处理

当识别出过时技能时：
1. 在输出表格中包含 ⚠️ 状态
2. 在“建议理由”列中记录具体差异
3. 提供更新建议并注明关键变化
4. 当用户请求更新时，用远程版本替换整个本地技能文件夹
5. 保留 `.github/skills/` 目录中的文件夹位置
6. 确保在更新 `SKILL.md` 时下载所有捆绑资源
