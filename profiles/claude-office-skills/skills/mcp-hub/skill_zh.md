# Mcp Hub 技能

## 概述

该技能可访问 1200+ MCP（模型上下文协议）服务器——这些标准化的工具可扩展 AI 能力。将 Claude 连接到文件系统、数据库、API 和文档处理工具。

## 如何使用

1. 描述您想要完成的工作
2. 提供所需的输入数据或文件
3. 我将执行相应的操作

**示例提示：**
- "访问本地文件系统以读取/写入文档"
- "查询数据库进行数据分析"
- "与 GitHub、Slack、Google Drive 集成"
- "运行文档处理工具"

## 领域知识


### MCP 架构

```
Claude ←→ MCP 服务器 ←→ 外部资源
        (协议)      (文件、API、数据库)
```

### 热门文档 MCP 服务器

| 服务器 | 功能 | 星标 |
|--------|----------|-------|
| **filesystem** | 读取/写入本地文件 | 官方 |
| **google-drive** | 访问 Google Docs/Sheets | 5k+ |
| **puppeteer** | 浏览器自动化、PDF 生成 | 10k+ |
| **sqlite** | 数据库查询 | 官方 |

### 配置示例

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/documents"
      ]
    },
    "google-drive": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-google-drive"]
    }
  }
}
```

### MCP 工具发现

浏览可用服务器：
- [mcp.run](https://mcp.run) - MCP 市场place
- [awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers)
- [mcp-awesome.com](https://mcp-awesome.com)

### 在技能中使用 MCP

```python
# MCP 工具将自动对 Claude 可用
# 示例：filesystem MCP 提供以下工具：

# read_file(path) - 读取文件内容
# write_file(path, content) - 写入文件
# list_directory(path) - 列出目录内容
# search_files(query) - 搜索文件
```


## 最佳实践

1. **仅启用您需要的 MCP 服务器（安全）**
2. **在可用时使用官方服务器**
3. **启用前检查服务器权限**
4. **组合多个服务器以实现复杂工作流**

## 安装

```bash
# 安装所需依赖
pip install python-docx openpyxl python-pptx reportlab jinja2
```

## 资源

- [MCP 服务器仓库](https://github.com/modelcontextprotocol/servers)
- [Claude 办公技能中心](https://github.com/claude-office-skills/skills)
