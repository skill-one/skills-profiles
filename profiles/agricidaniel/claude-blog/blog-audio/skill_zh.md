# 博客音频：Gemini TTS 为博客文章朗读

使用 Google 的 Gemini TTS 生成专业音频朗读的博客内容。
三种模式：摘要（200-300 字的朗读概述）、全文朗读，
或双人播客对话模式。30 种声音，80 多种语言，HTML5 嵌入输出。

## 快速参考

| 命令 | 功能 |
|------|-------------|
| `/blog audio generate <file>` | 生成博客文章的音频朗读 |
| `/blog audio voices` | 显示可用声音及其特性 |
| `/blog audio setup` | 检查/配置 Gemini TTS 的 API 密钥 |

## 前置条件

- Python 3.11+（`run.py` 自动管理虚拟环境）
- `GOOGLE_AI_API_KEY` 环境变量（与 `blog-image` 使用的相同密钥）
- FFmpeg（用于 WAV 转 MP3 转换；若缺失则回退为 WAV）

## 始终使用 run.py 封装器

```bash
# 正确：
python3 scripts/run.py generate_audio.py --text "..." --voice Charon --json

# 错误：
python3 scripts/generate_audio.py --text "..."  # 没有 venv 会失败
```

## API 密钥检查（门禁模式）

在生成音频前，检查 API 密钥：

```bash
test -n "${GOOGLE_AI_API_KEY:-}" && echo "GOOGLE_AI_API_KEY 已设置" || echo "GOOGLE_AI_API_KEY 未设置"
```

- 如果已设置：继续生成
- 如果未设置：引导用户：
  "音频生成需要 Google AI API 密钥。免费获取一个：https://aistudio.google.com/apikey
   然后设置：`export GOOGLE_AI_API_KEY=your-key`
   这可以是 `/blog image` 使用的相同密钥，但必须在 shell 中导出。"
- **内部调用时**（从 blog-write）：如果密钥缺失则静默返回。
  永不阻塞写作流程。

## 配置

对于 `/blog audio setup`：

1. 检查 `GOOGLE_AI_API_KEY` 是否在环境中设置
2. 如果 blog-image 使用项目 `.mcp.json`，确认引用的环境变量已导出
3. 如果未设置，引导用户到 https://aistudio.google.com/apikey
4. 通过干运行验证：`python3 scripts/run.py generate_audio.py --text "Test" --dry-run --json`

## 声音选择

对于 `/blog audio voices`：

加载 `references/voices.md` 并向用户展示声音目录。

询问用户他们更喜欢哪种声音，或根据内容类型推荐：
- **文章朗读**：Charon（信息性）或 Sadaltager（知识性）
- **教程/指南**：Achird（友好）或 Sulafat（温暖）
- **新闻/分析**：Rasalgethi（信息性）或 Schedar（均衡）
- **生活方式/健康**：Aoede（轻快）或 Vindemiatrix（温和）
- **对话主持人**：Puck（活泼）或 Laomedeia（活泼）
- **对话专家**：Kore（坚定）或 Charon（信息性）

## 生成工作流程

对于 `/blog audio generate <file>`：

### 第 1 步：读取博客文章

读取文件并提取：
- 标题（来自 H1 或 frontmatter）
- 完整内容（markdown 正文）
- 大约字数

### 第 2 步：选择模式

询问用户（或如果指定了 `--mode` 则自动选择）：

| 模式 | 使用场景 | 输出 |
|------|-------------|--------|
| **摘要** | 快速音频概述（1-2 分钟） | 200-300 字的朗读摘要 |
| **全文** | 完整朗读（5-15 分钟） | 文章的自然语音 |
| **对话** | 播客风格（3-8 分钟） | 关于文章的双人对话 |

### 第 3 步：准备文本

Claude 准备文本；脚本仅执行 TTS。

**摘要模式：**
撰写 200-300 字的文章朗读摘要。规则：
- 以自然口语形式撰写，而非书面文本
- 以文章的关键发现或答案开头
- 涵盖 3-5 个主要要点
- 以可操作的建议结尾
- 无 markdown，无 "本文介绍了..."，无元评论
- 使用口语化过渡（"以下是重点..."，"关键发现是..."）

**全文模式：**
去除 markdown 内容以生成自然语音文本：
- 标题转为自然过渡（"接下来，我们来看..."）
- 链接转为纯文本（移除 URL，保留锚文本）
- 图片和图表：忽略或简要描述（"数据显示..."）
- 代码块：口头描述（"代码使用 for 循环..."）
- 列表：转为自然句子
- 移除 frontmatter、schema 标记、HTML 标签
- 添加简短引言："这是 [标题]，发布于 [日期]。"

**对话模式：**
撰写关于文章的双人对话脚本：
- Speaker1 = 主持人（好奇，提出好问题）
- Speaker2 = 专家（知识渊博，给出清晰答案）
- 每行格式为：`Speaker1: 这里的关键要点是什么？`
- 口语化涵盖文章要点
- 15-25 次对话（生成 ~3-8 分钟）
- 自然，非生硬（"这是个很好的观点" 而非 "确实，如研究所示"）

### 第 4 步：选择声音

如果用户选择了声音，则使用它。否则，根据模式推荐：
- 摘要/全文：默认 Charon（信息性）
- 对话：默认 Puck（主持人）+ Kore（专家）

### 第 5 步：生成音频

将准备好的文本写入工作目录下的文件，然后调用：

```bash
# 单人声音（摘要或全文模式）
python3 scripts/run.py generate_audio.py \
  --text-file blog_audio_prepared.txt \
  --voice Charon \
  --model flash \
  --output audio/post-slug.mp3 \
  --json

# 双人声音（对话模式）
python3 scripts/run.py generate_audio.py \
  --text-file blog_audio_dialogue.txt \
  --voice Puck \
  --voice2 Kore \
  --model pro \
  --output audio/post-slug-dialogue.mp3 \
  --json
```

**模型选择：**
- `flash`（默认）：映射到 `gemini-3.1-flash-tts-preview`，适用于摘要和标准朗读。
- `flash31`：明确别名 `gemini-3.1-flash-tts-preview`。
- `legacy-flash25`：仅保留以兼容旧版本。
- `pro` 或 `legacy-pro25`：映射到 `gemini-2.5-pro-preview-tts`，仅在必要时使用。

### 第 6 步：交付

向用户展示结果：
1. **文件路径**：音频保存位置
2. **时长**：人类可读（例如，"3:42"）
3. **嵌入代码**：可直接粘贴的 HTML5 音频标签
4. **成本**：预估 API 费用
5. **放置建议**：在博客文章中插入嵌入的位置

## 嵌入指南

### 标准 HTML (Hugo, Jekyll, 静态网站)
```html
<audio controls preload="metadata">
  <source src="audio/post-slug.mp3" type="audio/mpeg">
  您的浏览器不支持音频元素。
</audio>
```

### MDX (Next.js, Gatsby)
```jsx
<audio controls preload="metadata">
  <source src="/audio/post-slug.mp3" type="audio/mpeg" />
</audio>
```

### WordPress
```
[audio src="audio/post-slug.mp3"]
```

### 放置
在引言（第一个 H2 下方）或文章顶部插入音频播放器，并添加标签："收听这篇文章"或"音频版本"。

## 内部 API（用于 blog-write）

从 blog-write 内部调用时：

**输入：**
- `text`：准备好的文本（Claude 已清理）
- `voice`：声音名称（默认：Charon）
- `voice2`：对话的第二声音（可选）
- `model`：flash 或 pro
- `output_path`：保存文件位置

**输出：**
```markdown
### 音频朗读
- **路径**：/path/to/audio/post-slug.mp3
- **时长**：3:42
- **声音**：Charon
- **嵌入**：`<audio controls preload="metadata"><source src="audio/post-slug.mp3" type="audio/mpeg"></audio>`
```

**优雅回退**：如果 `GOOGLE_AI_API_KEY` 未设置，立即返回无错误。
写作流程继续，不生成音频。永不因音频生成不可用而阻塞 blog-write。

## 错误处理

| 错误 | 解决方案 |
|-------|-----------|
| GOOGLE_AI_API_KEY 未设置 | 在 https://aistudio.google.com/apikey 获取密钥 |
| FFmpeg 未找到 | 安装：`sudo apt install ffmpeg`。回退为 WAV 输出。 |
| 被限流 | 等待并重试。在 https://aistudio.google.com/rate-limit 查看限制 |
| 文本过长（>8,192 输入 token） | 分割为约 7,800 token 的部分；脚本会分块并拼接准备好的文本 |
| 声音名称未知 | 运行 `/blog audio voices` 查看有效选项 |
| API 错误 | 检查密钥有效性及模型可用性 |
| 内部调用时密钥缺失 | 静默返回：写作流程继续 |

## 参考文档

按需加载：切勿在启动时加载全部：
- `references/voices.md`：完整的 30 声音目录，按内容类型推荐，对话配对
