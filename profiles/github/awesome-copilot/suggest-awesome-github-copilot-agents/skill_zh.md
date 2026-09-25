# 建议优秀的 GitHub Copilot 自定义代理

分析当前仓库上下文，并从 [GitHub awesome-copilot 仓库](https://github.com/github/awesome-copilot/blob/main/docs/README.agents.md) 中建议相关的自定义代理文件，这些文件在当前仓库中尚未可用。自定义代理文件位于 awesome-copilot 仓库的 [agents](https://github.com/github/awesome-copilot/tree/main/agents) 文件夹中。

## 流程

1. **获取可用自定义代理**：从 [awesome-copilot README.agents.md](https://github.com/github/awesome-copilot/blob/main/docs/README.agents.md) 中提取自定义代理列表和描述。必须使用 `fetch` 工具。
2. **扫描本地自定义代理**：发现 `.github/agents/` 文件夹中现有的自定义代理文件
3. **提取描述**：从本地自定义代理文件中读取前端元数据以获取描述
4. **获取远程版本**：对于每个本地代理，使用原始 GitHub URL 从 awesome-copilot 仓库中获取相应版本（例如，`https://raw.githubusercontent.com/github/awesome-copilot/main/agents/<filename>`）
5. **比较版本**：比较本地代理内容与远程版本以识别：
   - 代理已更新（完全匹配）
   - 代理已过时（内容不同）
   - 过时代理中的关键差异（工具、描述、内容）
6. **分析上下文**：审查聊天历史记录、仓库文件和当前项目需求
7. **匹配相关性**：将可用自定义代理与识别的模式和需求进行比较
8. **展示选项**：显示相关的自定义代理及其描述、理由和可用状态，包括过时的代理
9. **验证**：确保建议的代理将增加现有代理未涵盖的价值
10. **输出**：提供结构化表格，包含建议、描述以及指向 awesome-copilot 自定义代理和类似本地自定义代理的链接
    **AWAIT** 用户请求安装或更新特定的自定义代理。除非得到指示，否则不要安装或更新。
11. **下载/更新资源**：对于请求的代理，自动：
    - 将新代理下载到 `.github/agents/` 文件夹
    - 通过用 awesome-copilot 中的最新版本替换来更新过时的代理
    - 不要调整文件内容
    - 使用 `#fetch` 工具下载资源，但可以使用 `#runInTerminal` 工具通过 `curl` 确保所有内容都检索到
    - 使用 `#todos` 工具跟踪进度

## 上下文分析标准

🔍 **仓库模式**：

- 使用的编程语言（.cs、.js、.py 等）
- 框架指示器（ASP.NET、React、Azure 等）
- 项目类型（Web 应用、API、库、工具）
- 文档需求（README、规范、ADR）

🗨️ **聊天历史上下文**：

- 近期讨论和痛点
- 功能请求或实施需求
- 代码审查模式
- 开发工作流需求

## 输出格式

以结构化表格形式显示分析结果，比较 awesome-copilot 自定义代理和现有仓库自定义代理：

| Awesome-Copilot 自定义代理                                                                                                                            | 描述                                                                                                                                                                | 已安装 | 相似的本地自定义代理         | 建议理由                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | -------------------------- | ------------------------------------------------- |
| [amplitude-experiment-implementation.agent.md](https://github.com/github/awesome-copilot/blob/main/agents/amplitude-experiment-implementation.agent.md) | 此自定义代理使用 Amplitude 的 MCP 工具在 Amplitude 内部部署新实验，启用无缝的变体测试功能并推出产品功能                                                                 | ❌ 否  | 无                         | 将增强产品中的实验能力                         |
| [launchdarkly-flag-cleanup.agent.md](https://github.com/github/awesome-copilot/blob/main/agents/launchdarkly-flag-cleanup.agent.md)                     | LaunchDarkly 功能标志清理代理                                                                                                                                            | ✅ 是  | launchdarkly-flag-cleanup.agent.md | 已由现有的 LaunchDarkly 自定义代理覆盖        |
| [principal-software-engineer.agent.md](https://github.com/github/awesome-copilot/blob/main/agents/principal-software-engineer.agent.md)                 | 提供首席软件工程师级别的指导，重点关注工程卓越、技术领导力和实用实施。                                                                                                      | ⚠️ 过时 | principal-software-engineer.agent.md | 工具配置不同：远程使用 `'web/fetch'` 而本地使用 `'fetch'` - 建议更新 |

## 本地代理发现流程

1. 列出 `.github/agents/` 目录中的所有 `*.agent.md` 文件
2. 对于每个发现的文件，读取前端元数据以提取 `description`
3. 构建现有代理的全面清单
4. 使用此清单以避免建议重复项

## 版本比较流程

1. 对于每个本地代理文件，构造用于获取远程版本的原始 GitHub URL：
   - 模式：`https://raw.githubusercontent.com/github/awesome-copilot/main/agents/<filename>`
2. 使用 `fetch` 工具获取远程版本
3. 比较整个文件内容（包括前端元数据、工具数组和正文）
4. 识别具体差异：
   - **前端元数据变化**（描述、工具）
   - **工具数组修改**（添加、删除或重命名工具）
   - **内容更新**（说明、示例、指南）
5. 记录过时代理的关键差异
6. 计算相似度以确定是否需要更新

## 要求

- 使用 `githubRepo` 工具从 awesome-copilot 仓库的 agents 文件夹中获取内容
- 扫描本地文件系统以查找 `.github/agents/` 目录中的现有代理
- 从本地代理文件中读取 YAML 前端元数据以提取描述
- 将本地代理与远程版本进行比较以检测过时的代理
- 与此仓库中的现有代理进行比较以避免重复
- 重点关注当前代理库覆盖的差距
- 验证建议的代理与仓库的目的和标准一致
- 为每个建议提供清晰的理由
- 包括指向 awesome-copilot 代理和类似本地代理的链接
- 清晰地标识过时的代理并注明具体差异
- 不要提供表格和分析之外的任何附加信息或上下文

## 图标参考

- ✅ 已安装且最新
- ⚠️ 已安装但过时（可更新）
- ❌ 仓库中未安装

## 更新处理

当识别到过时的代理时：
1. 将其包含在输出表格中，并标记为 ⚠️ 状态
2. 在“建议理由”列中记录具体差异
3. 提供更新建议并注明关键变化
4. 当用户请求更新时，用远程版本替换整个本地文件
5. 保留文件位置在 `.github/agents/` 目录中
