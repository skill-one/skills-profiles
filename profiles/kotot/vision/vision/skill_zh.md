# 视觉（委托图像理解）

你没有原生视觉能力，但仍然可以通过运行捆绑脚本来“看见”图像，该脚本将图像发送到可配置的 OpenAI 兼容视觉模型，并返回文本答案。

## 使用场景

当任务需要理解图像内容而无法直接查看图像时，请使用此技能，例如：

- 用户上传或指向图像/截图/照片并询问其中内容。
- 需要在图像中读取文本（OCR）。
- 需要根据截图诊断错误。
- 需要理解 UI 原型、图表、图表或扫描文档。
- 需要比较图像显示的内容与代码或预期输出。

## 使用方法

使用 Bash 工具运行脚本。传入图像（本地路径或 http(s) URL）以及一个清晰、具体的指令，描述你需要了解的内容：

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/see.py" <image_path_or_url> "你的问题"
```

如果 `$CLAUDE_SKILL_DIR` 在你的环境中未设置，请使用此技能文件夹的相对路径，例如从技能目录运行 `python3 scripts/see.py ...`，或使用技能安装位置的绝对路径。

示例：

```bash
# 描述图像
python3 scripts/see.py ./photo.jpg "详细描述此图像"

# OCR — 提取文本
python3 scripts/see.py ./receipt.png "精确转录所有文本，保留布局"

# 诊断错误截图
python3 scripts/see.py ./error.png "显示的错误是什么？可能的原因是什么？"

# 将图表读取为结构化数据
python3 scripts/see.py ./chart.png "将每个序列、标签和值作为 markdown 表格提取"

# 远程图像
python3 scripts/see.py "https://example.com/diagram.png" "解释此架构图表"
```

脚本将模型的答案打印到标准输出。读取该答案并使用它来继续任务。当你需要特定内容（值、状态、错误消息）时，请提出一个专注的问题，而不是通用的“描述”——你会得到更好的结果并节省更多代币。

## 配置（必需，只需设置一次）

脚本从环境变量**或**`.claude/settings.json`的`env`块读取其配置（与视觉-mcp-server MCP 的变量名相同，因此配置可以继承）。解析顺序：显式的环境变量优先；否则脚本会读取`.claude/settings.json`，从当前目录向上搜索，然后搜索`~/.claude/`。

| 变量 | 必需 | 示例 |
| --- | --- | --- |
| `VISION_BASE_URL` | 是 | `http://localhost:1234/v1/chat/completions` |
| `VISION_MODEL` | 是 | `Qwen3-VL-32B`, `gpt-4o`, `glm-4v`, ... |
| `VISION_API_KEY` | 否* | 你的 API 密钥 (*本地服务器可选) |
| `VISION_MAX_TOKENS` | 否 | `4096` |
| `VISION_TEMPERATURE` | 否 | `0.2` |
| `VISION_DETAIL` | 否 | `auto` \| `low` \| `high` |
| `VISION_TIMEOUT` | 否 | `120` |

> `VISION_BASE_URL` 必须是**完整**的 chat-completions 端点 (`.../v1/chat/completions`)，而不仅仅是基本 URL。

在你的 shell 配置文件中设置它们，或在 MCP/agent 的 `env` 块中设置，或内联设置：

```bash
export VISION_BASE_URL=http://localhost:1234/v1/chat/completions
export VISION_MODEL=Qwen3-VL-32B
export VISION_API_KEY=sk-...        # 本地服务器可选
```

或者将它们放在`.claude/settings.json`（项目级，或全局`~/.claude/`）：

```jsonc
{
  "env": {
    "VISION_BASE_URL": "http://localhost:1234/v1/chat/completions",
    "VISION_MODEL": "Qwen3-VL-32B",
    "VISION_API_KEY": "sk-..."
  }
}
```

## 注意事项

- 纯 Python 标准库——无需 `pip install`。
- 本地文件会自动转换为 base64 数据 URL；http(s) URL 会直接传递。
- 如果脚本报告缺少变量或无法访问的端点，请修复上述配置并重试。添加 `--dry-run` 以在不发送请求的情况下检查请求：`python3 scripts/see.py --dry-run img.png "test"`。
