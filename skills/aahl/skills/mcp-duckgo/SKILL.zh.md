---
name: mcp-duckgo
description: 通过DuckDuckGo MCP服务器进行网络搜索和内容抓取的技能。当用户需要在线搜索和网页抓取时使用。
---

# DuckDuckGo 搜索
执行 Shell 命令。

## 网络搜索
- `npx -y mcporter call --stdio 'uvx duckduckgo-mcp-server' search query="{keyword}" max_results=10`

## 网络获取
- `npx -y mcporter call --stdio 'uvx duckduckgo-mcp-server' fetch_content url="https://..."`
