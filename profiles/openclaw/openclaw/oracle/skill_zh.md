# Oracle

Oracle 将提示词和选定的文件捆绑在一起进行一次二模型传递。将输出视为建议性；与代码和测试进行验证。

## 主要路径

当前 CLI 默认模型：`gpt-5.5-pro`。浏览器引擎适用于长时间运行的 ChatGPT Pro；API 引擎适用于 `OPENAI_API_KEY` 或 Azure 配置就绪时。

推荐默认设置：

- 首先预览：`--dry-run summary --files-report`
- 浏览器长时间运行：`--engine browser --model gpt-5.5-pro`
- API 显式：`--engine api --model gpt-5.5`

## 黄金路径

1. 选择一个紧凑的文件集（包含真相的最少文件）。
2. 预览有效负载和令牌消耗 (`--dry-run` + `--files-report`)。
3. 使用浏览器模式进行长时间 Pro 思考；API 模式进行显式 API 调用。
4. 如果运行脱离/超时：重新连接到存储的会话。不要盲目重新运行。

## 命令（推荐）

- 帮助：
  - `oracle --help`
  - 如果二进制文件未安装：`npx -y @steipete/oracle --help`（此处避免使用 `pnpx`；sqlite 绑定）。

- 预览（无令牌）：
  - `oracle --dry-run summary -p "<任务>" --file "src/**" --file "!**/*.test.*"`
  - `oracle --dry-run full -p "<任务>" --file "src/**"`

- 令牌状态检查：
  - `oracle --dry-run summary --files-report -p "<任务>" --file "src/**"`

- 浏览器运行（主要路径；长时间运行是正常的）：
  - `oracle --engine browser --model gpt-5.5-pro -p "<任务>" --file "src/**"`

- 手动粘贴回退：
  - `oracle --render --copy -p "<任务>" --file "src/**"`
  - 注意：`--copy` 是 `--copy-markdown` 的隐藏别名。

## 附着文件 (`--file`)

`--file` 接受文件、目录和通配符。您可以多次传递它；条目可以逗号分隔。

- 包含：
  - `--file "src/**"`
  - `--file src/index.ts`
  - `--file docs --file README.md`

- 排除：
  - `--file "src/**" --file "!src/**/*.test.ts" --file "!**/*.snap"`

- 默认值（实现行为）：
  - 默认忽略的目录：`node_modules`、`dist`、`coverage`、`.git`、`.turbo`、`.next`、`build`、`tmp`（除非明确传递为字面目录/文件则跳过）。
  - 扩展通配符时尊重 `.gitignore`。
  - 不跟踪符号链接。
  - 隐藏文件（除非通过模式选择加入，例如 `--file ".github/**"`）。
  - 文件大于 1 MB 被拒绝。

## 引擎（API 与浏览器）

- 自动选择：`api` 当 `OPENAI_API_KEY` 设置时；否则 `browser`。
- 浏览器支持 GPT + Gemini 仅限；使用 `--engine api` 进行 Claude/Grok/Codex 或多模型运行。
- 浏览器附件：
  - `--browser-attachments auto|never|always`（自动粘贴内联高达 ~60k 字符然后上传）。
- 远程浏览器主机：
  - 主机：`oracle serve --host 0.0.0.0 --port 9473 --token <秘密>`
  - 客户端：`oracle --engine browser --remote-host <主机:端口> --remote-token <秘密> -p "<任务>" --file "src/**"`

## 会话 + 缩写

- 存储在 `~/.oracle/sessions` 下（使用 `ORACLE_HOME_DIR` 覆盖）。
- 运行可能会脱离或耗时很长（浏览器 + Pro 常常如此）。如果 CLI 超时：不要重新运行；重新连接。
  - 列出：`oracle status --hours 72`
  - 附着：`oracle session <id> --render`
- 使用 `--slug "<3-5 个词>"` 使会话 ID 更易读。
- 存在重复提示保护；仅在您确实想要全新运行时使用 `--force`。

## 提示模板（高信号）

Oracle 从**零**开始没有项目知识。假设模型无法推断您的堆栈、构建工具、约定或“明显”的路径。包括：

- 项目简报（堆栈 + 构建测试命令 + 平台限制）。
- “事物所在的位置”（关键目录、入口点、配置文件、边界）。
- 精确的问题 + 您尝试过什么 + 错误文本（逐字）。
- 限制（“不要更改 X”、“必须保留公共 API”等）。
- 期望输出（“返回补丁计划 + 测试”、“给出 3 个选项并权衡”）。

## 安全性

- 默认情况下不要附加秘密（`.env`、密钥文件、认证令牌）。积极编辑；仅共享所需内容。

## “彻底提示”恢复模式

对于长时间调查，编写一个独立的提示词 + 文件集，以便几天后可以重新运行：

- 6-30 个句子的项目简报 + 目标。
- 重现步骤 + 精确错误 + 您尝试过什么。
- 附着所有需要的上下文文件（入口点、配置、关键模块、文档）。

Oracle 运行是一次性的；模型不记得之前的运行。“恢复上下文”意味着使用相同的提示词 + `--file …` 设置重新运行（或重新连接一个仍在运行的存储会话）。
