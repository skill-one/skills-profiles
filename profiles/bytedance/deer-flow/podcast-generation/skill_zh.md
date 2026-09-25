# 播客生成技能

## 概述

该技能可从文本内容生成高质量的播客音频。工作流程包括创建结构化的JSON脚本（对话式对话）以及通过文本到语音合成执行音频生成。

## 核心功能

- 将任何文本内容（文章、报告、文档）转换为播客脚本
- 生成自然的双主持对话（男主持人和女主持人）
- 使用文本到语音合成语音音频
- 将音频片段混合为最终的播客MP3文件
- 支持英文和中文内容

## 工作流程

### 第一步：理解需求

当用户请求播客生成时，需要识别：

- 源内容：要转换为播客的文本/文章/报告
- 语言：英文或中文（根据内容）
- 输出位置：保存生成的播客的位置
- 无需检查`/mnt/user-data`下的文件夹

### 第二步：创建结构化脚本JSON

在`/mnt/user-data/workspace/`生成结构化的JSON脚本文件，命名模式：`{描述性名称}-script.json`

JSON结构：
```json
{
  "locale": "en",
  "lines": [
    {"speaker": "male", "paragraph": "对话文本"},
    {"speaker": "female", "paragraph": "对话文本"}
  ]
}
```

### 第三步：执行生成

调用Python脚本：
```bash
python /mnt/skills/public/podcast-generation/scripts/generate.py \
  --script-file /mnt/user-data/workspace/script-file.json \
  --output-file /mnt/user-data/outputs/generated-podcast.mp3 \
  --transcript-file /mnt/user-data/outputs/generated-podcast-transcript.md
```

参数：

- `--script-file`：JSON脚本文件的绝对路径（必需）
- `--output-file`：输出MP3文件的绝对路径（必需）
- `--transcript-file`：输出转录Markdown文件的绝对路径（可选，但推荐）

> [!IMPORTANT]
> - 必须一次性完整调用脚本。不要将工作流程拆分为单独步骤。
> - 脚本内部处理所有TTS API调用和音频生成。
> - 不要读取Python文件，只需带参数调用即可。
> - 始终包含`--transcript-file`为用户提供可读的转录文本。
> - TTS提供者和其并发性从环境变量中自动选择——你无需选择或调整它们。

## 脚本JSON格式

脚本JSON文件必须遵循此结构：

```json
{
  "title": "人工智能的历史",
  "locale": "en",
  "lines": [
    {"speaker": "male", "paragraph": "你好Deer！欢迎回到另一期节目。"},
    {"speaker": "female", "paragraph": "大家好！今天我们有一个激动人心的主题要讨论。"},
    {"speaker": "male", "paragraph": "没错！我们要谈论的是..."}
  ]
}
```

字段：
- `title`：播客节目的标题（可选，用于转录中的标题）
- `locale`：语言代码——"en"为英文或"zh"为中文
- `lines`：对话行数组
  - `speaker`：要么是"male"或"female"
  - `paragraph`：该主持人的对话文本

## 脚本编写指南

创建脚本JSON时，请遵循以下指南：

### 格式要求
- 只有两位主持人：男性和女性，自然交替
- 目标时长：约10分钟的对话（约40-60行）
- 以男性主持人说包含"你好Deer"的问候语开始

### 语气和风格
- 自然、对话式的对话——像两个朋友聊天
- 使用口语表达和对话过渡
- 避免过于正式的语言或学术语气
- 包括反应、后续问题和非正式插入语

### 内容指南
- 主持人间频繁互动
- 保持句子简短，易于口语表达
- 纯文本——输出中无Markdown格式
- 将技术概念翻译成易于理解的语言
- 无数学公式、代码或复杂符号
- 使内容对仅听音频的听众有吸引力
- 排除元信息，如日期、作者姓名或文档结构

## 播客生成示例

用户请求："生成一个关于人工智能历史的播客"

第一步：创建脚本文件`/mnt/user-data/workspace/ai-history-script.json`：
```json
{
  "title": "人工智能的历史",
  "locale": "en",
  "lines": [
    {"speaker": "male", "paragraph": "你好Deer！欢迎回到另一期节目。今天我们要深入探讨的是正在塑造我们未来的事物——人工智能的历史。"},
    {"speaker": "female", "paragraph": "哦，我超喜欢这个话题！你知道，人工智能感觉非常现代，但它实际上有超过七十年的历史。"},
    {"speaker": "male", "paragraph": "没错！它始于20世纪50年代。实际上，'人工智能'这个术语是由约翰·麦卡锡在1956年一个著名的达特茅斯会议上提出的。"},
    {"speaker": "female", "paragraph": "等等，所以那时候他们就已经在思考能够思考的机器了？太不可思议了！"},
    {"speaker": "male", "paragraph": "没错？早期的先驱者非常乐观。他们认为我们会在一代之内实现人类水平的AI。"},
    {"speaker": "female", "paragraph": "但事情并没有按预期发展，对吧？"},
    {"speaker": "male", "paragraph": "完全不是。20世纪70年代带来了所谓的第一次AI寒冬..."}
  ]
}
```

第二步：执行生成：
```bash
python /mnt/skills/public/podcast-generation/scripts/generate.py \
  --script-file /mnt/user-data/workspace/ai-history-script.json \
  --output-file /mnt/user-data/outputs/ai-history-podcast.mp3 \
  --transcript-file /mnt/user-data/outputs/ai-history-transcript.md
```

这将生成：
- `ai-history-podcast.mp3`：音频播客文件
- `ai-history-transcript.md`：播客的可读Markdown转录文本

## 特定模板

仅当匹配用户请求时才读取以下模板文件。

- [技术解释](templates/tech-explainer.md) - 用于转换技术文档和教程

## 输出格式

生成的播客遵循"你好Deer"格式：
- 两位主持人：一位男性，一位女性
- 自然对话式
- 以"你好Deer"问候语开始
- 目标时长：约10分钟
- 交替发言人以保持吸引人的流程

## 输出处理

生成后：

- 播客和转录文本保存在`/mnt/user-data/outputs/`
- 使用`present_files`工具与用户分享播客MP3和转录MD
- 提供简要的生成结果描述（主题、时长、主持人）
- 如需调整，可提供重新生成选项

## 要求

必须设置以下环境变量：
- 对于Volcengine：`VOLCENGINE_TTS_APPID`和`VOLCENGINE_TTS_ACCESS_TOKEN`
- 对于MiniMax：`MINIMAX_API_KEY`
- `VOLCENGINE_TTS_CLUSTER`：Volcengine TTS集群（可选，默认为"volcano_tts")
- `VOLCENGINE_TTS_VOICE_TYPE_MALE`：Volcengine男性声音类型（可选，默认为`zh_male_yangguangqingnian_moon_bigtts`)
- `VOLCENGINE_TTS_VOICE_TYPE_FEMALE`：Volcengine女性声音类型（可选，默认为`zh_female_sajiaonvyou_moon_bigtts`)

声音类型覆盖会被修剪；未设置或空白值使用列出的默认值。

## 注意事项

- **始终一次性执行完整的工作流程**——无需测试单个步骤或担心超时
- 脚本JSON应与内容语言（en或zh）匹配
- 技术内容应在脚本中简化以适应音频可访问性
- 复杂符号（公式、代码）应在脚本中翻译为平实语言
- 长内容可能导致播客时长更长

## 提供商（Volcengine / MiniMax）

由环境变量自动选择：

- 设置`VOLCENGINE_TTS_APPID` + `VOLCENGINE_TTS_ACCESS_TOKEN` → Volcengine TTS（默认）。
- 仅设置`MINIMAX_API_KEY` → MiniMax TTS（`/v1/t2a_v2`）。
- 强制使用`PODCAST_GENERATION_PROVIDER=volcengine|minimax`。

MiniMax覆盖：`MINIMAX_API_HOST`（默认`https://api.minimaxi.com`）、
`MINIMAX_TTS_MODEL`（默认`speech-2.6-hd`）、`MINIMAX_TTS_VOICE_MALE`
（默认`male-qn-qingse`）、`MINIMAX_TTS_VOICE_FEMALE`（默认`female-tianmei`）。

并发性由每个提供商内部管理——MiniMax单线程运行以减少速率限制失败，
Volcengine使用4个工作线程。没有面向调用者的并发调节旋钮；暂时的速率限制由自动重试和退避处理。
