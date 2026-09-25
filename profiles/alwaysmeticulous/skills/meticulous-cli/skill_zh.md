# 精细命令行界面

`meticulous` 命令行界面记录用户会话并回放它们以捕获视觉回归。它作为 `@alwaysmeticulous/cli` 的一部分进行安装。

> 开始之前，运行 `meticulous-cli-update` 命令以确保 Meticulous 命令行界面和技能是最新版本——除非它已经在此对话早期运行过，在这种情况下可以跳过。

## 调用方式

```bash
meticulous <命令> [选项]
```

技能假定 `meticulous` 在 `PATH` 中。如果缺失，`meticulous-cli-update` 命令会通过 `npm install --global @alwaysmeticulous/cli@latest` 全局安装它。当按项目本地安装时，它也可以作为 `npx @alwaysmeticulous/cli` 被调用。

## 命令组

| 命令               | 目的                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| `agent`               | 读取、分析并触发测试运行——面向代理的命令，也暴露在 MCP 服务器上                                     |
| `auth`                | 使用 Meticulous 进行身份验证（登录、whoami、注销、项目选择）                                        |
| `debug`               | 设置 AI 就绪的调试工作区，用于调查回放差异和回放                                               |
| `download`            | 将会话、回放和测试运行下载到本地                                                           |
| `local`               | 查找与当前分支代码变更相关的会话                                                              |
| `project`             | 检查您已通过身份验证的项目                                                                   |
| `simulate` / `replay` | 对 URL 回放录制的会话                                                                      |
| `schema`              | 以 JSON 格式输出 CLI 命令模式（用于代理/程序化使用）                                             |

有关每个组的完整选项详情，请参阅参考：

- [references/agent.md](references/agent.md)
- [references/auth.md](references/auth.md)
- [references/debug.md](references/debug.md)
- [references/download.md](references/download.md)
- [references/local.md](references/local.md)
- [references/project.md](references/project.md)
- [references/simulate.md](references/simulate.md)
- [references/schema.md](references/schema.md)

## 全局选项

这些选项被每个命令接受：

| 选项       | 类型   | 默认         | 描述                                                                  |
| ------------ | ------ | --------------- | ---------------------------------------------------------------------------- |
| `--logLevel` | 字符串 | `info`          | 日志详细程度：`trace`, `debug`, `info`, `warn`, `error`, `silent`           |
| `--dataDir`  | 字符串 | `~/.meticulous` | 存储会话、回放和其他数据的目录                                         |
| `--jsonArgs` | 字符串 | —               | 将所有选项作为 JSON 字符串传递（用于程序化/代理调用）                     |

`--rawJson` 是 `--jsonArgs` 的已弃用别名。`--dryRun` 不是全局的——它仅在执行操作的命令上可用（例如 `ci` / `agent` 运行触发和上传命令，以及 `simulate`）；检查命令的参考或 `meticulous schema <命令>`。

## 身份验证

命令通过 OAuth 进行身份验证。登录令牌存储在磁盘上并在会话之间重用——在交互式终端中，需要身份验证的命令会自动打开浏览器登录；在没有 TTY（通常是代理的情况）时，它会失败并告诉您运行 `meticulous auth login`。运行 `meticulous auth whoami` 查看当前状态。作用域为特定项目的命令还需要默认项目，在登录时设置或使用 `meticulous auth set-project`。参见 [references/auth.md](references/auth.md)。

API 令牌（通过 `--apiToken` 或 `METICULOUS_API_TOKEN` 环境变量，作用域为特定组织/项目）也受支持，并且是非交互式环境（如 CI）中身份验证的方式。一些代理平台会向 `app.meticulous.ai` 的出站请求中注入一个访问令牌；这也有效，并且 `auth whoami` 将其报告为 `credentials injected at request time`。

## MCP 服务器

`agent` 命令也作为工具在托管于 `https://app.meticulous.ai/api/mcp` 的 **MCP 服务器**上公开，因此支持 MCP 的客户端（Claude Code、Cursor、Codex）可以直接调用它们，而不是调用 CLI。大多数读取/分析命令映射到返回与 CLI 命令的 `--json` 输出相同数据的 `get_<command>` 工具——例如 `agent test-run-diffs` ⇄ `get_test_run_diffs`, `agent dom-diff` ⇄ `get_dom_diff`，以及 `download session` ⇄ `get_session_data`。两个可变命令（`upload-build`, `trigger-test-run`）也有 MCP 工具，但不是 1:1 映射——参见 [references/agent.md](references/agent.md) 了解完整映射，包括这个重要区别。只需使用端点 URL 连接（首次使用时浏览器 OAuth）。技能是用 CLI 编写的；如果您连接了 MCP 服务器，请替换相应的工具（但请注意 MCP 工具从不推断 git 上下文（`commitSha`/`baseSha`/diff），这与 CLI 不同，因此在使用 MCP 时始终显式传递这些值）。

## 示例

```bash
# 打印所有命令的模式（代理使用）
meticulous schema

# 在本地运行单个回放
meticulous simulate --sessionId=<id> --appUrl=http://localhost:3000
```
