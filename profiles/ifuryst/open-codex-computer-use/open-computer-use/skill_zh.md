# 开放式计算机使用

## 概述

开放式计算机使用将计算机使用作为本地CLI和stdio MCP服务器进行暴露。它并非Codex.app专属；请根据您所运行的代理运行时环境调整命令和MCP配置。

macOS运行时需要macOS 14.0或更高版本。Windows和Linux使用各自的平台运行时，不受此macOS最低版本限制。

它支持跨macOS、Linux和Windows的核心工具界面：
`list_apps`、`get_app_state`、`click`、`perform_secondary_action`、`scroll`、
`drag`、`type_text`、`press_key`和`set_value`。

## 核心工作流程

1. 在macOS上，在调用CLI之前运行`sw_vers -productVersion`，并要求macOS 14.0或更高版本。对于旧版本，解释运行时无法启动；不要将`doctor`或权限更改作为二进制不兼容的修复建议。
2. 使用`open-computer-use -h`或`ocu -h`检查CLI是否已安装。如果安装或设置缺失，请阅读[参考资料/安装.md](references/installation.md)。
3. 在支持的macOS版本上，在首次执行GUI任务之前运行`open-computer-use doctor`。如果权限缺失，请要求用户在引导UI中批准辅助功能访问和屏幕录制。
4. 在执行操作前检查可用应用：`open-computer-use call list_apps`。
5. 使用`open-computer-use call get_app_state --args '{"app":"TextEdit"}'`捕获当前UI状态。默认状态通常足以进行UI操作。
6. 当任务需要较长的语义文本，如聊天历史记录、邮件正文、文档文本或长格式内容时，使用`get_app_state`并设置`text_limit: 1000`或`text_limit: "max"`。
7. 当可见的长页面或列表在滚动后仍不完整时，使用更大的`max_tree_nodes`或`max_tree_depth`调用`get_app_state`。
8. 优先使用最新`get_app_state`结果中的`element_index`进行元素目标操作。
9. 对于多步CLI工作，使用`open-computer-use call --calls '<json-array>'`，以便一个进程可以重用最新的元素索引映射。
10. 对于支持本地MCP服务器的代理运行时，配置`open-computer-use mcp`或`ocu mcp`，并直接调用暴露的计算机使用工具。请阅读[参考资料/使用.md](references/usage.md)。
11. 对于直接代码优先的编排，运行`ocu capabilities`，然后使用一次性`ocu js`或持久`ocu repl`。请阅读[参考资料/使用.md](references/usage.md)。
12. 如果通信、权限或桌面会话访问失败，请阅读[参考资料/故障排除.md](references/troubleshooting.md)。

## 操作规则

- 将目标桌面视为用户的实际会话。除非用户明确要求执行该任务，否则不要检查密码管理器、无关的私人内容或敏感应用。
- 在发送、删除、购买、批准、上传或进行其他外部可见更改之前请求确认。
- 不要假设Codex.app插件助手可用。使用安装的`open-computer-use` / `ocu` CLI或显式的MCP配置。
- 在使用`element_index`之前，始终运行`get_app_state`；不要跨会话或在大规模UI更改后猜测索引。
- 优先使用语义操作和`set_value`进行可编辑控件。仅在元素树未提供更安全的操作目标时，使用坐标`click`、`scroll`和`drag`。
- 在macOS上，除非用户明确请求`click_method: "global"`、必须驱动窗口服务器拖会话的`drag`（窗口移动、拖选文本、Finder拖放）或其他可能移动真实指针的诊断行为，否则不要启用`OPEN_COMPUTER_USE_ALLOW_GLOBAL_POINTER_FALLBACKS=1`。如果没有它，`drag`报告`Drag delivered via app_post`，这些操作无效；请参阅`参考资料/使用.md`了解替代方案。
- 在Windows和Linux上，在假设GUI自动化可用之前，确认命令正在登录的桌面会话中运行。

## 常见CLI操作

```sh
open-computer-use -h
ocu -h
ocu capabilities --json
ocu js 'nodeRepl.write(6 * 7)'
ocu repl
open-computer-use doctor
open-computer-use call list_apps
ocu call list_apps
open-computer-use call get_app_state --args '{"app":"TextEdit"}'
open-computer-use call get_app_state --args '{"app":"TextEdit","text_limit":1000}'
open-computer-use call get_app_state --args '{"app":"TextEdit","text_limit":"max"}'
open-computer-use call get_app_state --args '{"app":"Google Chrome","max_tree_nodes":3000,"max_tree_depth":96}'
open-computer-use call click --args '{"app":"TextEdit","element_index":"0"}'
open-computer-use call type_text --args '{"app":"TextEdit","text":"Hello from Open Computer Use"}'
```

对于在一个进程中重用状态的短序列：

```sh
open-computer-use call --calls '[
  {"tool":"get_app_state","args":{"app":"TextEdit"}},
  {"tool":"press_key","args":{"app":"TextEdit","key":"Return"}}
]'
```

## MCP使用

对于可以通过stdio启动本地MCP服务器的运行时，使用：

```toml
[mcp_servers.open_computer_use]
command = "open-computer-use"
args = ["mcp"]
```

请阅读[参考资料/使用.md](references/usage.md)了解JSON配置示例、直接工具调用模式以及平台说明。

## 参考资料

- [参考资料/安装.md](references/installation.md)：一次性CLI安装、代理MCP安装命令和macOS权限。
- [参考资料/使用.md](references/usage.md)：MCP配置、直接CLI调用、编排和平台行为。
- [参考资料/故障排除.md](references/troubleshooting.md)：权限、桌面会话、应用发现和操作失败。
