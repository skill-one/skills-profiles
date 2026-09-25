# 摘要

用于摘要 URL、本地文件和 YouTube 链接的快速命令行工具。

## 使用场景（触发短语）

当用户询问以下任何内容时，立即使用此技能：

- "使用 summarize.sh"
- "这个链接/视频是关于什么的？"
- "摘要这个 URL/文章"
- "转录这个 YouTube/视频"（最佳努力转录提取；无需 `yt-dlp`）

## 快速入门

```bash
summarize "https://example.com"
summarize "/path/to/file.pdf"
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto
```

## YouTube：摘要与转录

最佳努力转录（仅限 URL）：

```bash
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto --extract
```

如果用户要求转录但内容巨大，先返回简洁摘要，然后询问要扩展哪个部分/时间范围。

## 模型 + 密钥

设置您选择的提供者的 API 密钥：

- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- xAI: `XAI_API_KEY`
- Google: `GEMINI_API_KEY`（别名：`GOOGLE_GENERATIVE_AI_API_KEY`, `GOOGLE_API_KEY`）

默认模型为 `auto`；配置可能选择提供者/模型。

## 有用的标志

- `--length short|medium|long|xl|xxl|<字符数>`
- `--max-output-tokens <数量>`
- `--extract`（打印提取内容，无 LLM 摘要）
- `--json`（机器可读）
- `--firecrawl auto|off|always`（备用提取）
- `--youtube auto`（如果设置了 `APIFY_API_TOKEN`，则 Apify 备用）

## 配置

可选配置文件：`~/.summarize/config.json`

```json
{ "model": "openai/gpt-5.2" }
```

可选服务：

- `FIRECRAWL_API_KEY` 用于被屏蔽的网站
- `APIFY_API_TOKEN` 用于 YouTube 备用
