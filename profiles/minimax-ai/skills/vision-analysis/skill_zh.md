# 视觉分析

使用 MiniMax `MiniMax_understand_image` MCP 工具（可在 MiniMax 令牌计划中获取）分析图像。

## 前置条件

- 已订阅 MiniMax 令牌计划，并拥有有效的 `MINIMAX_API_KEY`
- MiniMax MCP 已配置（`MiniMax_understand_image` 工具可用）

### 如果 MCP 工具未配置

**步骤 1：** 代理应从以下地址获取设置说明：
**https://platform.minimaxi.com/docs/token-plan/mcp-guide**

**步骤 2：** 检测用户的环境（OpenCode、Cursor、Claude Code 等），并输出所需的精确命令。常见示例：

**OpenCode** — 添加到 `~/.config/opencode/opencode.json` 或 `package.json`：
```json
{
  "mcp": {
    "MiniMax": {
      "type": "local",
      "command": ["uvx", "minimax-coding-plan-mcp", "-y"],
      "environment": {
        "MINIMAX_API_KEY": "YOUR_TOKEN_PLAN_KEY",
        "MINIMAX_API_HOST": "https://api.minimaxi.com"
      },
      "enabled": true
    }
  }
}
```

**Claude Code**：
```bash
claude mcp add -s user MiniMax --env MINIMAX_API_KEY=your-key --env MINIMAX_API_HOST=https://api.minimaxi.com -- uvx minimax-coding-plan-mcp -y
```

**Cursor** — 添加到 MCP 设置：
```json
{
  "mcpServers": {
    "MiniMax": {
      "command": "uvx",
      "args": ["minimax-coding-plan-mcp"],
      "env": {
        "MINIMAX_API_KEY": "your-key",
        "MINIMAX_API_HOST": "https://api.minimaxi.com"
      }
    }
  }
}
```

**步骤 3：** 配置完成后，告知用户重启其应用程序并通过 `/mcp` 进行验证。

**重要提示：** 如果用户没有 MiniMax 令牌计划订阅，应告知他们 `understand_image` 工具需要订阅——它不能与免费或其他级别的 API 密钥一起使用。

## 分析模式

| 模式 | 使用场景 | 提示策略 |
|---|---|---|
| `describe` | 一般图像理解 | 请求详细描述 |
| `ocr` | 从截图、文档中提取文本 | 请求逐字提取所有文本 |
| `ui-review` | UI 模板、线框图、设计文件 | 请求设计评论及建议 |
| `chart-data` | 图表、图形、数据可视化 | 请求提取数据点和趋势 |
| `object-detect` | 识别物体、人物、活动 | 请求列出并定位所有元素 |

## 工作流程

### 步骤 1：自动检测图像

当消息包含具有以下扩展名的图像文件路径或 URL 时，技能将自动触发：
`.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, `.svg`

从消息中提取图像路径。

### 步骤 2：选择分析模式并调用 MCP 工具

使用 `MiniMax_understand_image` 工具，并根据特定模式提供提示：

**describe:**
```
提供此图像的详细描述。包括：主要主题、场景/背景、颜色/风格、可见的任何文本、值得注意的物体以及整体构图。
```

**ocr:**
```
逐字提取此图像中可见的所有文本。保留结构和格式（标题、列表、列）。如果未找到文本，请说明。
```

**ui-review:**
```
您是一位 UI/UX 设计评论员。分析此界面模板或设计。提供：
(1) 优势——哪些方面做得好，
(2) 问题——可用性或设计问题，
(3) 具体可行的改进建议。要建设性且详细。
```

**chart-data:**
```
从此图表或图形中提取所有数据。列出：图表标题、轴标签、所有可读的数据点/系列及其值，以及趋势的简要总结。
```

**object-detect:**
```
列出所有可识别的独立物体、人物和活动。对于每个，描述其是什么及其在图像中的大致位置。
```

### 步骤 3：展示结果

清晰返回分析结果。对于 `describe`，使用可读的散文。对于 `ocr`，保留结构。对于 `ui-review`，使用结构化的评论格式。

## 输出格式示例

对于 describe 模式：
```
## 图像描述

[图像内容的详细描述...]
```

对于 ocr 模式：
```
## 提取的文本

[保留的图像文本结构]
```

对于 ui-review 模式：
```
## UI 设计评论

### 优势
- ...

### 问题
- ...

### 建议
- ...
```

## 注意事项

- 支持 20MB 以内的图像（JPEG、PNG、GIF、WebP）
- 如果 MiniMax MCP 配置了文件访问权限，本地文件路径可用
- `MiniMax_understand_image` 工具由 `minimax-coding-plan-mcp` 包提供
