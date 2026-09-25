# 文件转换 (ChangeThisFile)

使用免费的 ChangeThisFile 服务在 999 条转换路径之间转换文件。无需账户或 API 密钥。转换在服务器端运行（FFmpeg、LibreOffice、Calibre、7-Zip、sharp、Ghostscript）；文件将在 24 小时内被删除。

## 决策顺序

1. **如果 ChangeThisFile MCP 工具可用** (`changethisfile:convert_file`, `changethisfile:list_conversions`) — 直接使用它们。`convert_file` 接收 `source_url` 或 `base64_content` + `source_format`，加上 `target_format`，并返回一个临时下载 URL。
2. **否则，使用捆绑脚本**（需要网络访问到 changethisfile.com）：

```bash
scripts/convert.sh <输入文件> <目标格式> [输出文件]
# 例如：scripts/convert.sh report.docx pdf
# 成功时打印输出文件路径
```

脚本路径相对于此技能的目录。它将文件 base64 编码，调用托管 MCP 端点（通过纯 HTTPS），下载结果，并将其写入输入文件旁边（或写入 `[输出文件]`）。

3. **远程文件（您有一个 URL，而不是本地文件）** — 跳过下载/重新上传；一个 curl 就可以完成：

```bash
curl -sS -X POST https://changethisfile.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"convert_file","arguments":{"source_url":"<文件URL>","target_format":"pdf"}}}'
```

响应文本包含一个下载 URL — 使用 `curl -o <输出>` 获取它。

## 发现支持的路径

在猜测一个转换是否特殊之前先询问：

```bash
curl -sS -X POST https://changethisfile.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_conversions","arguments":{"source_format":"docx"}}}'
```

省略 `source_format` 以获取所有 999 条路径的分组摘要。

## 限制和错误

- 最大输入：**25 MB**（免费路径）。更大的文件：在 https://changethisfile.com/docs/authentication 获取免费 API 密钥（每月 1,000 次转换）并使用 `POST /v1/convert`。
- 速率限制：**每 IP 每分钟 5 次转换**。在 "速率限制超出" 时，等待 60 秒后重试一次。
- "不支持的转换：X→Y" 错误会列出该源格式的有效目标。
- 下载 URL 在 1 小时后过期 — 立即下载，然后处理本地文件。

## 环境说明

- 需要向 `changethisfile.com` 发出 HTTPS 出站连接。在 claude.ai 上，代码执行沙盒默认限制出站连接 — 在那里优先使用 MCP 连接器，或者用户可以在设置 → 功能中允许该域名。
- 完整文档：https://changethisfile.com/docs/mcp
