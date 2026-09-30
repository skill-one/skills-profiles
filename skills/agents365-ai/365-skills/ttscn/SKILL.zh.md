---
name: ttscn
description: 多平台中文及多语言TTS文本转语音，通过Edge/Doubao/CosyVoice/Qwen3/StepFun/GLM-TTS/Azure/Tencent/Baidu/MiniMax/Xunfei plus ElevenLabs/OpenAI/Google/Atlas Cloud — 15后端，词级时间戳，[PAUSE:x]暂停标记，拼音发音覆盖
---

# ttscn — 多平台中文TTS技能

## 概述

从文本生成自然语音音频。**15个后端** — 11个对中国友好的云服务加上4个国际或统一API（ElevenLabs / OpenAI / Google / Atlas Cloud）。

| # | 后端 | 成本 | 主要优势 |
| --- | --------- | ------ | ------------- |
| 1 | **Edge TTS**（默认） | 免费 | 无API密钥，任何地方都可用 |
| 2 | **豆包**（字节跳动） | ~1元/1万 | 最佳中文自然度（9/10） |
| 3 | **CozyVoice**（阿里云） | ~0.2元/1千 | 快速流式传输，灵活 |
| 4 | **Qwen3-TTS**（阿里云） | ~1元/1万 | 10种语言，指令控制 |
| 5 | **StepFun**（阶跃星辰） | 低成本 | OpenAI兼容，~10秒克隆 |
| 6 | **GLM-TTS**（智谱AI） | 低成本 | 情感控制，简单REST |
| 7 | **Azure**（微软） | ~1美元/字符 | 企业级SSML，东亚 |
| 8 | **腾讯云** | **0.75元/1万** | 最低成本，380+声音 |
| 9 | **百度AI** | 灵活 | 30+声音，情感 + 方言 |
| 10 | **MiniMax** | ~$0.10/1千 | 最佳质量，300+声音，克隆 |
| 11 | **科大讯飞讯飞Xunfei** | ~2元/1万 | MOS 4.8，500+声音，专业级 |
| 12 | **ElevenLabs** | 付费层级（从$5/月） | 顶级声音质量，即时克隆 |
| 13 | **OpenAI TTS** | ~$15-30/字符 | 6种声音，多语言，简单REST |
| 14 | **Google Cloud TTS** | ~$16/字符（免费层级） | 220+声音，40+语言 |
| 15 | **Atlas Cloud TTS** | 按模型计价 | 统一异步API，多语言声音 |

1.4–1.6版本新增：**逐字时间戳**（Edge/Azure/Doubao/MiniMax — 尽力而为，降级为无边界），**[PAUSE:x] + 声音标签标记**（所有平台），**--phonemes发音覆盖**（Azure/MiniMax）。
1.7版本新增：**--json标志**（JSON包独立于`--format`），幂等命中报告`cached: true`，如果缓存的音频被删除则**重新合成**，`--input f out.wav`位置固定，分块器永远不会在`[PAUSE:x]`内分割。
1.8版本新增：**MiniMax默认为speech-2.8-hd**（声音标签自动输出），**支持CosyVoice v3.5-flash**（仅限自定义/克隆声音 — 预设需要cosyvoice-v3-flash）。
1.9版本新增：**Qwen3-TTS**（DashScope，重用DASHSCOPE_API_KEY），**StepFun**（重用STEP_API_KEY），**GLM-TTS**（重用ZHIPUAI_API_KEY）和**Atlas Cloud TTS**（异步生成，有界轮询，无凭证媒体下载，多语言声音预设）后端 — 共15个后端。

**跨平台**：Windows、macOS、Linux

本文档中的所有路径都相对于此技能的根目录（包含此SKILL.md的目录） — 相对此目录解析。

## 何时使用此技能

当用户需要：

- 将中文文本转换为语音音频
- 为视频生成旁白或配音
- 从文本创建有声读物或播客音频
- 用户询问比较TTS提供商、选择TTS后端或查看可用声音
- 用户询问TTS定价、功能或哪个提供商支持克隆/SSML/方言
- 用户提到任何：TTS、文本转语音、语音合成、文字转语音、Edge TTS、豆包TTS、CozyVoice、火山引擎、阿里云语音、Azure TTS、腾讯云TTS、百度语音、MiniMax、讯飞语音、ElevenLabs、OpenAI TTS、Google Cloud TTS、Atlas Cloud TTS
- 用户需要逐字时间戳/字幕、暂停控制或修正多音字
- 任何需要中文文本转语音的任务

## 提供商比较页面

**当用户想要浏览、比较或选择TTS提供商时，始终首先在他们的浏览器中打开本地HTML比较页面** — 它是一个可视的、可过滤的表格，比阅读文本输出更快。

```bash
# 跨平台（相对于此技能的目录的路径）
python3 -m webbrowser docs/providers.html

# 或者平台原生的打开器：open（macOS）/ xdg-open（Linux）/ start（Windows）
```

比较页面包括：

- **可过滤表格** — 按免费、SSML、声音克隆、流式传输、方言、多语言过滤
- **每个提供商的详细面板** — 成本、最大字符/时长、克隆方法、情感、语言
- **声音卡片** — 推荐声音，包含风格描述和最佳用途标签
- **API密钥链接** — 直接链接到每个提供商的控制台以获取密钥

此页面自动生成自`data/providers.json`（所有提供商/声音数据的单一真实来源）。编辑JSON后运行`python3 scripts/build_docs.py`重新生成它。相同的数据可通过CLI查询`python3 scripts/tts.py schema backends|voices`（参见模式内省）。

**打开页面后**，询问用户他们想要使用哪个后端和声音，然后继续步骤2。

## 工作流程

### 步骤0 — 显示比较页面（当比较/选择时）

如果用户正在浏览、比较提供商或不确定要使用哪个后端，请按上述方式打开`docs/providers.html`。让他们探索，然后询问他们想要哪个后端 + 声音。

### 步骤1 — 理解请求

澄清用户需要什么：

- **文本**：行内文本还是文件？短文本还是长文本？
- **声音风格**：男声/女声，年轻/成熟，温暖/精力充沛？（见声音指南）
- **速度**：正常，更快（+10-20%），更慢（-10-20%）？
- **格式**：WAV（无损）或MP3（压缩）？

### 步骤2 — 选择后端 & 声音

根据用例选择（见后端选择指南）。不确定时默认为**Edge TTS**与`zh-CN-XiaoxiaoNeural`（女声，温暖，标准）。提及你的选择。

### 步骤3 — 合成

运行`scripts/tts.py`并使用文本和选择的选项。

### 步骤4 — 报告

确认：输出路径，文件大小，音频时长。

## 后端选择指南

### 快速选择

| 用例 | 后端 | 声音 | 原因 |
| ---------- | --------- | ------- | ----- |
| **默认 / 一般** | edge | zh-CN-XiaoxiaoNeural | 免费，无需设置 |
| **短视频 / 抖音** | doubao | BV001_streaming | 本地短视频风格 |
| **有声读物 / 长文本** | cosyvoice | longxiaochun_v3 | 快速合成，自然 |
| **企业 / SSML** | azure | zh-CN-XiaoxiaoNeural | 丰富的韵律控制 |
| **批量 / 最低成本** | tencent | 101001 | 0.75元/1千字符 |
| **情感 / 方言** | baidu | 3或4 | 情感合成，粤语 |
| **最佳质量 / 克隆** | minimax | female-shaonv | speech-2.8-hd，声音设计 |
| **教育 / 专业** | xunfei | xiaoyan | MOS 4.8，500+声音 |
| **男性旁白** | edge | zh-CN-YunxiNeural | 精力充沛的男声 |
| **纪录片** | azure | zh-CN-YunyangNeural | 深沉，专业的男声 |
| **儿童内容** | edge | zh-CN-XiaomengNeural | 明亮，年轻的女性 |
| **成本敏感** | edge | zh-CN-XiaoxiaoNeural | 完全免费 |
| **英语，顶级质量** | elevenlabs | 21m00Tcm4TlvDq8ikWAM (Rachel) | 英语声音中的顶级 |
| **英语，简单/便宜** | openai | alloy | tts-1-hd，一个环境变量 |
| **英语，企业** | google | en-US-Neural2-F | 220+声音，免费层级 |
| **多语言 / 指令** | qwen | Cherry | 10种语言，自然语言风格控制，重用你的DASHSCOPE密钥 |
| **营销 / 快速** | stepfun | cixingnansheng | OpenAI兼容，重用你的STEP密钥 |
| **简单 / 情感** | zhipu | tongtong | 最小REST，重用你的ZHIPUAI密钥 |

### 完整功能 & 声音数据

完整的能力矩阵（成本，每个块的最大字符/时长，SSML，克隆方法 + 成本，情感，方言，语言，流式传输，设置难度）和每个后端的声音列表都在**一个地方**：`data/providers.json`。通过以下方式查看它们：

- **比较页面** (`docs/providers.html`) — 人类最佳
- `python3 scripts/tts.py schema backends --full` — 每个后端的完整能力字段
- `python3 scripts/tts.py schema voices` — 每个声音预设，包含风格描述
- `python3 scripts/tts.py --list` — 人类可读的终端摘要

不要在其他地方维护这些表格的副本 — 从JSON重新生成。

## 声音克隆（`clone`命令）

从参考音频创建自定义声音，以名称存储，然后在任何接受`--voice`的地方使用该名称。内置用于**minimax**（本地文件OK，10秒-5分钟音频，付费：~$1.5/声音全球站点或¥9.9在中国站点首次使用；新的克隆是临时的，直到第一次真实合成 — 在创建后的7天内[全球站点] / 48小时[中国站点]内使用它或MiniMax删除它，预览不计入；使用后永久）和**cosyvoice**（注册免费，音频必须是公共http(s) URL，10-20秒，声音在1年未使用后过期）。

```bash
# MiniMax — 本地文件，付费，必须用`--yes`确认
python3 scripts/tts.py clone create --platform minimax --audio my_voice.wav --name myvoice --yes

# CosyVoice — 免费，但`--audio`必须是公共URL；`--target-model`必须
# 与合成模型匹配（默认：$COSYVOICE_MODEL或cosyvoice-v3-flash）。
# v3.5-flash没有预设声音 — 它需要一个使用相同模型的自定义/克隆声音创建
# （声音ID不能在不同模型之间互换）。
python3 scripts/tts.py clone create --platform cosyvoice --audio https://example.com/my.wav --name myvoice

# 管理
python3 scripts/tts.py clone list
python3 scripts/tts.py clone delete --name myvoice [--remote]   # --remote: cosyvoice仅限
# 使用它 — 存储的名称自动解析为平台声音_id
python3 scripts/tts.py "用我的声音说这句话" out.wav --platform minimax --voice myvoice
```

代理必须遵守的规则：

- MiniMax创建是付费的 — 永远不要在没有用户明确确认的情况下运行`clone create --platform minimax`
  （CLI强制执行`--yes`）。
- 只克隆用户自己的声音或他们有权使用的声音 — 两个平台合同上禁止未经同意克隆第三方。
- 参考音频：干净的单一说话者语音，无背景音乐，10-20秒是理想的。
- 命名声音存储在`~/.ttscn.json`下的`cloned_voices`。

其他平台（Doubao/Tencent/Baidu/Xunfei/Azure）通过他们的控制台支持克隆 — 生成的声音ID也作为普通的`--voice`工作。

## 使用方法

### 基本使用

```bash
# 默认（Edge TTS，免费，Xiaoxiao声音）
python3 scripts/tts.py "你好世界" output.wav

# 特定声音
python3 scripts/tts.py --voice zh-CN-YunxiNeural "欢迎收听今天的节目" welcome.wav

# 特定后端
python3 scripts/tts.py --platform doubao "今天天气真好" weather.wav
python3 scripts/tts.py --platform minimax "高品质语音合成" hq.wav
python3 scripts/tts.py --platform atlas "统一 API 多语言语音合成" atlas.wav

# 调整速度
python3 scripts/tts.py --rate +15% "快速播报" fast.wav
python3 scripts/tts.py --rate -10% "慢速朗读" slow.wav
```

### 从文件

```bash
python3 scripts/tts.py --input script.txt output.wav
```

### 输出格式

```bash
# MP3输出（压缩，文件较小）
python3 scripts/tts.py --format mp3 "你好" hello.mp3

# JSON包 + MP3音频同时
python3 scripts/tts.py --json --format mp3 "你好" hello.mp3
```

### 预览（干运行）

```bash
# 预览而不进行API调用 — 无需安装包
python3 scripts/tts.py --dry-run "这是一段测试文本"
```

### 列出选项

```bash
python3 scripts/tts.py --list
```

## 表达性标记

输入文本可以包含**任何**平台的标记 — 它们在支持的地方原生渲染，并在其他地方被移除（永远不会朗读）。分块器永远不会在`[...]`标记内分割。

| 标记 | 语法 | azure | minimax | 所有其他平台 |
|--------|--------|-------|---------|---------------------|
| 暂停 | `[PAUSE:x]` — x = 秒，0.01-99.99 | `<break time="xs"/>` (SSML) | `<#x#>` | 移除 |
| 声音标签 | `(笑声)` `(轻笑)` `(叹息)` `(呼吸)` `(吸气)` `(呼气)` `(咳嗽)` | 移除 | 仅当`MINIMAX_MODEL`以`speech-2.8`开头时才**朗读**（否则移除 + stderr警告） | 移除 |

```bash
python3 scripts/tts.py --platform azure \
  "大家好。[PAUSE:0.8] 今天我们聊一个新话题。" out.wav

MINIMAX_MODEL=speech-2.8-hd python3 scripts/tts.py --platform minimax \
  "这也太好笑了 (笑声) 好，我们继续。" out.wav
```

## 发音覆盖（`--phonemes`）

使用JSON字典将单词映射到空格分隔的拼音 — 带声调编号（`hang2 zhang3`）或带声调符号（`háng zhǎng`）。以`_`开头的键是注释。

```json
{
  "_comment": "发音覆盖主题脚本的银行主题",
  "行长": "hang2 zhang3",
  "重庆": "chóng qìng"
}
```

```bash
python3 scripts/tts.py --platform azure --phonemes phonemes.json \
  "行长在重庆开会。" out.wav
```

按平台：**azure** → SSML `<phoneme alphabet="sapi">` 标签；**minimax** →
行内拼音注释，如`重(chong2)庆(qing4)`（在分块之前应用，因此注释计入块预算）；所有其他平台静默忽略此标志。

## 要求

```bash
# 核心始终需要
pip install edge-tts  # 用于Edge（默认，免费）

# 可选后端 — 只安装你使用的
pip install dashscope                              # CosyVoice
pip install requests                               # Doubao, MiniMax, ElevenLabs, OpenAI, Google
pip install azure-cognitiveservices-speech          # Azure
pip install tencentcloud-sdk-python-tts             # Tencent Cloud
pip install baidu-aip chardet                       # Baidu AI
pip install websocket-client                        # Xunfei
```

系统要求：`ffmpeg`

## 环境变量

```bash
# 全局默认（可选）
export TTS_BACKEND="edge"
export TTS_VOICE="zh-CN-XiaoxiaoNeural"
export TTS_RATE="+5%"
export TTS_FORMAT="wav"              # wav | mp3 | json (json = JSON包模式)

# 后端调整（可选）
export MINIMAX_MODEL="speech-2.8-hd"       # 默认；声音标签需要speech-2.8-*
export MINIMAX_GROUP_ID=""                 # 某些MiniMax账户需要
export COSYVOICE_MODEL="cosyvoice-v3-flash"  # 或 cosyvoice-v3.5-flash（仅限自定义/克隆声音）

# 字节跳动火山引擎（豆包）
# v3（推荐，无appid）：新控制台（火山引擎API密钥页面）的API密钥
export VOLCENGINE_API_KEY="your_api_key"
export VOLCENGINE_RESOURCE_ID="seed-tts-2.0"   # 可选；seed-tts-1.0 / seed-icl-2.0也有效
# v1（遗留，appid + token）：仅在VOLCENGINE_API_KEY未设置时
export VOLCENGINE_APPID="your_app_id"
export VOLCENGINE_ACCESS_TOKEN="your_token"

# 阿里云DashScope（CosyVoice + Qwen3-TTS）
export DASHSCOPE_API_KEY="your_api_key"
export QWEN_TTS_MODEL="qwen3-tts-flash"   # 或 qwen3-tts-instruct-flash（指令控制）
export QWEN_TTS_LANGUAGE=""              # 可选：中文 / 英语 / ...；未设置 = 自动
export QWEN_TTS_INSTRUCTIONS=""          # 可选：自然语言风格，指令模型仅限

# StepFun（阶跃星辰）
export STEP_API_KEY="your_api_key"
export STEPFUN_TTS_MODEL="step-tts-mini"   # 或 step-tts-2 / stepaudio-2.5-tts

# 智谱
export ZHIPUAI_API_KEY="your_api_key"
export ZHIPU_TTS_MODEL="glm-tts"

# 微软Azure
export AZURE_SPEECH_KEY="your_key"
export AZURE_SPEECH_REGION="eastasia"
export TTS_STYLE="gentle"              # 可选：mstts:express-as风格；未设置 = 简单韵律

# 腾讯云
export TENCENT_SECRET_ID="your_secret_id"
export TENCENT_SECRET_KEY="your_secret_key"

# 百度AI
export BAIDU_APP_ID="your_app_id"
export BAIDU_API_KEY="your_api_key"
export BAIDU_SECRET_KEY="your_secret_key"

# MiniMax
export MINIMAX_API_KEY="your_api_key"

# 科大讯飞讯飞Xunfei
export XUNFEI_APP_ID="your_app_id"
export XUNFEI_API_KEY="your_api_key"
export XUNFEI_API_SECRET="your_api_secret"

# ElevenLabs（国际）
export ELEVENLABS_API_KEY="your_api_key"
export ELEVENLABS_MODEL="eleven_multilingual_v2"   # 可选，这是默认值

# OpenAI TTS（国际）
export OPENAI_API_KEY="your_api_key"
export OPENAI_TTS_MODEL="tts-1-hd"                 # 可选，这是默认值

# Google Cloud TTS（国际）
export GOOGLE_TTS_API_KEY="your_api_key"
export GOOGLE_TTS_LANGUAGE="en-US"                 # 可选，自动从声音名称派生

# Atlas Cloud TTS（统一API）
export ATLASCLOUD_API_KEY="your_api_key"
export ATLASCLOUD_TTS_LANGUAGE="auto"                # 可选，这是默认值
```

获取API密钥：

- 火山Ark：<https://console.volcengine.com/ark/region:ark+cn-beijing/apikey>
- DashScope：<https://bailian.console.aliyun.com/>
- Azure：<https://portal.azure.com/>
- 腾讯云：<https://console.cloud.tencent.com/tts>
- 百度AI：<https://console.bce.baidu.com/ai/#/ai/speech/overview>
- MiniMax：<https://platform.minimaxi.com>
- 讯飞：<https://www.xfyun.cn>
- ElevenLabs：<https://elevenlabs.io/app/settings/api-keys>
- OpenAI：<https://platform.openai.com/api-keys>
- Google Cloud：<https://console.cloud.google.com/apis/credentials>
- Atlas Cloud：<https://www.atlascloud.ai/console/api-keys>

## 配置文件（可选）

创建`~/.ttscn.json`用于个人默认设置，或在项目目录中创建`.ttscn.json`：

```json
{
  "backend": "minimax",
  "voice": "female-shaonv",
  "rate": "+10%"
}
```

优先级（从高到低）：

1. 命令行参数 (`--platform`, `--voice`, `--rate`)
2. 环境变量 (`TTS_BACKEND`, `TTS_VOICE`, `TTS_RATE`)
3. 项目配置（当前目录中的`.ttscn.json`）
4. 用户配置（`~/.ttscn.json`）
5. 内置默认值

## 示例

### 快速旁白（免费，无需设置）

```bash
python3 scripts/tts.py \
  "人工智能正在改变我们的生活方式，从智能助手到自动驾驶，技术革新无处不在。" \
  ai_narration.wav
```

### 抖音风格短视频语音

```bash
python3 scripts/tts.py \
  --platform doubao --voice BV001_streaming --rate +10% \
  "家人们，今天给大家推荐一个超好用的神器！" \
  douyin_style.wav
```

### 从脚本文件生成有声书（CozyVoice）

```bash
python3 scripts/tts.py \
  --platform cosyvoice --voice longxiaoxia_v3 \
  --input chapter1.txt chapter1.wav
```

### 批量生成最低成本（腾讯，内联环境变量）

```bash
TENCENT_SECRET_ID="xxx" TENCENT_SECRET_KEY="xxx" \
python3 scripts/tts.py \
  --platform tencent --voice 101001 \
  --input course_script.txt course_audio.wav
```

### 高品质带情感（MiniMax）

```bash
MINIMAX_API_KEY="xxx" \
python3 scripts/tts.py \
  --platform minimax --voice female-shaonv \
  "这是一段充满感情的语音合成演示。" premium.wav
```

## Agent-Native CLI 参考

ttscn遵循[agent-native-design](https://github.com/Agents365-ai/365-skills/tree/main/plugins/agent-native-design)契约。
它同时服务于**人类**（可读的终端输出）、**AI代理**（stdout上的结构化JSON）和
**编排器**（不同的退出码+幂等性）。

### JSON模式

```bash
# 显式JSON信封模式（独立于--format）
python3 scripts/tts.py --json "你好" out.wav
python3 scripts/tts.py --json --format mp3 "你好" out.mp3

# --format json是--json的已弃用别名（保留以兼容）

# 自动检测：管道到jq → 自动生成JSON
python3 scripts/tts.py --list | jq .data.backends[0].name

# 错误信封始终结构化
python3 scripts/tts.py --json --platform doubao "test" out.wav
# → {"ok":false, "error":{"code":"auth_missing_env","message":"...","retryable":false,...}}
```

### 输出信封

```json
// 成功
{"ok":true, "data":{...}, "meta":{"version":"...","schema_version":"1.2.0","timestamp":"...","ms":123}}

// 错误
{"ok":false, "error":{"code":"auth_missing_env","message":"set one of: VOLCENGINE_APPID+VOLCENGINE_ACCESS_TOKEN / VOLCENGINE_API_KEY","retryable":false,"field":"VOLCENGINE_APPID","backend":"doubao"}, "meta":{...}}
```

**契约**：`meta.schema_version`是每个信封（成功和错误）中都存在的semver字符串。**主**版本仅在信封变更时增加——消费者应断言它匹配他们编写的模式主版本（例如video-podcast-maker需要主版本`1`），否则应报明显错误。缺失的`schema_version`表示预契约的ttscn版本。

### 单词边界（edge / azure / doubao / minimax / cosyvoice）

对于**edge**、**azure**、**doubao**、**minimax**和**cosyvoice**，成功信封在`data.word_boundaries`下包含原生单词级时间戳——输出文件中的绝对秒数，升序排列，3位小数舍入。对于其他平台，该键不存在——并且当提供者返回无时间戳负载时（少数语言的doubao声音；minimax字幕下载失败；cosyvoice-v1或无时间戳支持的语音），它也可能不存在——因此消费者必须将其视为可选。

```json
{"ok":true, "data":{
  "output_file": "out.wav",
  "word_boundaries": [
    {"text": "你好", "offset_sec": 0.1,   "duration_sec": 0.45},
    {"text": "世界", "offset_sec": 0.562, "duration_sec": 0.5}
  ]
}}
```

用于生成字幕/SRT或同步到节拍的动画，无需单独的强制对齐过程。

### 退出码

| 代码 | 含义 | 代理操作 |
| ------ | --------- | ------------- |
| **0** | 成功 | 解析`data`，继续 |
| **1** | 内部/运行时错误 | 报告给用户，不要重试 |
| **2** | 验证/可修复错误（输入错误，缺失包） | 修复输入或安装包，允许重试 |
| **3** | 认证/缺失凭证 | 请求用户输入API密钥，不要重试 |
| **4** | 后端API错误 | 背离重试 |

### 模式内省

```bash
python3 scripts/tts.py schema backends              # 所有15个后端（默认紧凑）
python3 scripts/tts.py schema backends --full       # 所有字段（每个后端22个）
python3 scripts/tts.py schema backends.doubao       # 单个后端详细信息
python3 scripts/tts.py schema voices                # 每个后端的全部语音预设
python3 scripts/tts.py schema tags                  # 标签定义
python3 scripts/tts.py schema version               # 版本+提供者数据新鲜度

# 字段过滤以降低token成本查询
python3 scripts/tts.py schema backends --fields name,cost,supports_clone,supports_ssml
```

### 幂等性

```bash
# 编排器：重试调用返回缓存结果——不会重复计费
python3 scripts/tts.py --idempotency-key "daily-podcast-2026-07-08" --input script.txt out.wav

# 缓存于~/.ttscn_idem/，7天TTL，SHA-256键值
```

缓存命中返回存储的结果，`data.cached: true`。如果缓存的`output_file`在磁盘上不再存在，调用**重新合成**而不是返回过时的成功。

### Agent兼容性标志

```bash
# 无操作接受用于代理运行时兼容性（ttscn从不提示）
python3 scripts/tts.py --yes --no-input "text" out.wav
```
