# 每日新闻播报技能

该技能允许代理获取实时新闻，将其组织成对话式播客脚本，并生成朗读脚本的音频文件。

## 工作流程说明

当用户要求获取最新新闻并制作播客时，请严格遵循以下步骤：

### 第一步：确保所需技能存在
验证 `news-aggregator-skill` 和 `tts` 是否存在于工作区中（位于 `skills/` 或 `.cursor/skills/` 下）。如果其中任何一个缺失，请告知用户哪些技能未找到，并要求他们手动安装后再继续。**不要**尝试自动安装技能。

### 第二步：获取最新新闻
从 `news-aggregator-skill` 技能目录中定位 `fetch_news.py`（例如 `skills/news-aggregator-skill/scripts/fetch_news.py`）。如有需要，请阅读其 SKILL.md 了解用法。

运行脚本以获取实时新闻。您可以根据用户请求指定来源（例如 `hackernews`、`github`、`all`）或关键词。
示例命令：
```bash
python3 skills/news-aggregator-skill/scripts/fetch_news.py --source all --limit 10 --deep
```

### 第三步：草拟播客脚本（内部步骤）
读取获取的新闻数据，并将其改写成**Markdown 播客脚本**。
**关键在于优先采用双主持（两人）对话式格式**（例如主持 A 和主持 B），并采用**动态问答风格**。
脚本应满足以下要求：
- **双主持对话式且简洁**：编写两位主持人的互动内容。**主持 A 应提出有见地、高价值的问题**来引导对话，而**主持 B 应提供信息丰富、简洁的回答**。应感觉像一场智能、快节奏的问答对话。
- **避免冗余**：不要包含不必要的填充内容或过长的过渡。保持简洁（言简意赅），同时保留所有关键信息和事实。
- **明确标注发言人**：每行或段落开头应标注发言人姓名（例如 `Host A:` 或 `Host B:`）。
- **清晰的语音文本**：避免在口语文本中包含复杂的 URL、原始 Markdown 链接或难以发音的字符。

将此脚本保存为本地文件 `podcast_script.md`。

**示例 `podcast_script.md` 内容：**
```markdown
**Host A:** 欢迎收听今天的新闻盘点。今天有一些令人兴奋的技术更新。首先，来自 [公司名称] 的大更新。他们的新版本对普通用户的核心影响是什么？有什么重要意义？

**Host B:** 主要的收获是……[插入新闻项目 1 的简洁回答和摘要]。这完全改变了我们处理 [主题] 的方式。

**Host A:** 这很有趣。但这种方法是否引发了任何安全问题，特别是考虑到最近的数据泄露事件？

**Host B:** 正是如此。专家们指出……[插入分析或背景信息]。

**Host A:** 转到开源领域，GitHub 上今天有哪些开发者应该关注的热点趋势？

**Host B:** 一个突出的项目是……[插入新闻项目 2 的简洁总结]。

**Host A:** 很有见地的分享。今天的快速更新就到这里。感谢收听！
```

### 第四步：逐行生成播客音频
为了避免一次性将整个脚本发送到 API，您必须**逐句（一人一句地）生成**音频，然后将其连接起来。

使用本地 `tts` 技能中的 `tts.py`（`skills/tts/scripts/tts.py`）。如有需要，请阅读 tts 技能的 SKILL.md 了解完整用法和后端选项。

**1. 为每一行生成音频**：
对于脚本中的每一行对话内容，运行 `speak` 命令。使用适当的语音或参考音频来区分不同的主持人。如果用户为两个角色提供了参考音频文件，请通过 `--ref-audio` 标志使用它们（需要 noiz 后端和 `NOIZ_API_KEY`）。如果没有 API 密钥，则可以使用访客模式语音（请参阅 tts SKILL.md 中的语音列表）。
```bash
python3 skills/tts/scripts/tts.py -t "Welcome to today's news roundup..." --ref-audio host_A.wav -o line_01.wav

python3 skills/tts/scripts/tts.py -t "The main takeaway is that..." --ref-audio host_B.wav -o line_02.wav
```

**2. 连接音频文件**：
创建一个文本文件（例如 `list.txt`），按顺序列出所有生成的音频文件：
```text
file 'line_01.wav'
file 'line_02.wav'
```
然后使用 `ffmpeg` 将它们合并成一个播客音频文件：
```bash
ffmpeg -f concat -safe 0 -i list.txt -c copy podcast_output.wav
```

### 第五步：呈现最终结果
在生成并合并完整音频后，向用户呈现结果。您**必须**提供以下两项内容：
- 将完整的 **Markdown 播客脚本** 输出到聊天中，以便用户阅读。
- 提供最终 `podcast_output.wav` 文件的路径，以便他们可以收听音频。
- 简要总结播客中包含的新闻标题。

## 安全与数据披露

该技能仅包含指令，本身不包含可执行代码。在运行时，它会协调来自两个依赖技能的脚本：

- **执行的脚本**：`news-aggregator-skill/scripts/fetch_news.py`（从公共来源获取新闻）和 `tts/scripts/tts.py`（生成语音音频）。这两个脚本必须在技能运行前存在于本地；请查看它们的代码和 SKILL.md 了解其网络行为和凭据要求。
- **凭据**：该技能本身不直接需要任何 API 密钥或环境变量。`tts` 依赖项可能需要 `NOIZ_API_KEY` 以启用语音克隆功能（noiz 后端）；没有它，访客模式语音即可正常工作。请参阅 tts 技能的 SKILL.md 了解详细信息。
- **网络访问**：所有网络调用均由依赖技能执行，而不是由该技能的指令执行。新闻聚合器从公共新闻来源获取数据；tts 技能仅在使用 noiz 后端时才与 `noiz.ai` 通信。
- **写入的文件**：`podcast_script.md`、`line_*.wav`（逐句生成的临时音频）、`list.txt`（ffmpeg 连接列表）、`podcast_output.wav`（最终输出）。所有文件均写入当前工作目录。
- **无持久状态**：该技能不会写入配置文件、存储凭据或修改其他技能。
