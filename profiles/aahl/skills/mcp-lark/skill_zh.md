# MCP Lark / 飞书
需要登录 Lark MCP 配置平台来添加 MCP 服务、获取 MCP URL 并将其配置到环境变量中。
- Lark MCP 文档：https://open.larksuite.com/document/mcp_open_tools/call-feishu-mcp-server-in-remote-mode
- 飞书 MCP 文档：https://open.feishu.cn/document/mcp_open_tools/end-user-call-remote-mcp-server

## 环境变量
优先从工作区下的 `.env` 文件中获取，然后使用系统环境变量。如果未配置，则提示用户输入并更新到 `.env` 文件。
```shell
# 在环境变量中配置多个 MCP 服务 URL 及使用场景
LARK_MCP_SERVERS='
open.larksuite.com/mcp/stream/xxx:聊天和邮件;
open.larksuite.com/mcp/stream/yyy:云文档;
'
```

## 可用工具列表
```shell
npx -y mcporter list 'open.larksuite.com/mcp/stream/<token>' --all-parameters

# 获取指定工具的架构
npx -y mcporter list 'open.larksuite.com/mcp/stream/<token>' --json | jq '.tools[] | select(.name == "<tool_name>")'
```

## 调用指定工具
```shell
npx -y mcporter call 'open.larksuite.com/mcp/stream/<token>.<tool_name>' param1:"value1" foo:"bar"
```

## 参考
- 发送消息内容：references/message_create.md

## 关于 `mcporter`
为了提高兼容性，执行命令时请使用 `npx -y mcporter` 而不是 `mcporter`。
