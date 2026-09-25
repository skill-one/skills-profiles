# DuckDuckGo 搜索
执行 Shell 命令。

## 网络搜索
- `npx -y mcporter call --stdio 'uvx duckduckgo-mcp-server' search query="{keyword}" max_results=10`

## 网络获取
- `npx -y mcporter call --stdio 'uvx duckduckgo-mcp-server' fetch_content url="https://..."`
