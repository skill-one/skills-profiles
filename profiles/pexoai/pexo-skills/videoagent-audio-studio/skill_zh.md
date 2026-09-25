# 🎙️ VideoAgent 音频工作室

**使用场景：** 用户请求生成语音、朗读文本、制作旁白、创作音乐或制作音效时使用。

VideoAgent 音频工作室是一个智能音频调度器。它会分析您的请求，并将其路由到最佳可用模型——ElevenLabs 用于语音和音乐，fal.ai 用于快速音效——然后返回一个可使用的音频 URL。

---

## 快速参考

| 请求类型 | 最佳模型 | 延迟 |
|---|---|---|
| 朗读文本 / 旁白 | `elevenlabs-tts-v3` | ~3秒 |
| 低延迟 TTS（实时） | `elevenlabs-tts-turbo` | <1秒 |
| 背景音乐 | `cassetteai-music` | ~15秒 |
| 音效 | `elevenlabs-sfx` | ~5秒 |
| 从音频克隆声音 | `elevenlabs-voice-clone` | ~10秒 |

---

## 使用方法

### 1. 启动 AudioMind 服务器（每会话启动一次）

```bash
bash {baseDir}/tools/start_server.sh
```

这会启动端口 8124 上的 ElevenLabs MCP 服务器。技能使用它进行所有音频生成。

### 2. 路由请求

分析用户的请求并通过 MCP 服务器调用相应的工具：

**文本转语音 (TTS)**

当用户请求“朗读”、“大声朗读”、“说”或“制作旁白”时：

```
使用 MCP 工具：text_to_speech
  text: "<要朗读的文本>"
  voice_id: "JBFqnCBsd6RMkjVDRZzb"   # 默认："George"（专业、中性）
  model_id: "eleven_multilingual_v2"   # 使用 "eleven_turbo_v2_5" 获取低延迟
```

**音乐生成**

当用户请求“创作”、“创建背景音乐”或“制作配乐”时：

```
使用 MCP 工具：text_to_sound_effects  (通过 cassetteai-music 在 fal.ai 上)
  prompt: "<音乐描述，例如 '欢快的低保真嘻哈，90秒'>""
  duration_seconds: <持续时间>
```

**音效 (SFX)**

当用户请求特定音效（例如，“门吱嘎作响”、“雨打窗户”）时：

```
使用 MCP 工具：text_to_sound_effects
  text: "<音效描述>"
  duration_seconds: <1-22>
```

**声音克隆**

当用户提供音频样本并希望克隆声音时：

```
使用 MCP 工具：voice_add
  name: "<声音名称>"
  files: ["<音频文件URL>"]
```

---

## 示例对话

**用户：** “为我朗读这段文本：欢迎参加我们的产品发布”

```
→ 路由到：text_to_speech
  text: "Welcome to our product launch"
  voice_id: "JBFqnCBsd6RMkjVDRZzb"
  model_id: "eleven_multilingual_v2"
```

> 🎙️ 旁白完成！[在此处收听](audio_url)

---

**用户：** “为播客生成 60 秒的放松背景音乐”

```
→ 路由到：cassetteai-music (fal.ai)
  prompt: "用于播客的放松低保真背景音乐，轻柔的钢琴和柔和的节拍，60秒"
  duration_seconds: 60
```

> 🎵 背景音乐已准备好！[在此处收听](audio_url)

---

**用户：** “生成科幻风格的门打开音效”

```
→ 路由到：text_to_sound_effects
  text: "一个未来派科幻门滑开的声音，带有液压嘶嘶声"
  duration_seconds: 3
```

---

## 安装

### 必需

在 `~/.openclaw/openclaw.json` 中设置 `ELEVENLABS_API_KEY`：

```json
{
  "skills": {
    "entries": {
      "videoagent-audio-studio": {
        "enabled": true,
        "env": {
          "ELEVENLABS_API_KEY": "your_elevenlabs_key_here"
        }
      }
    }
  }
}
```

在 [elevenlabs.io/app/settings/api-keys](https://elevenlabs.io/app/settings/api-keys) 获取您的密钥。

### 可选（用于 fal.ai 音乐 & 音效模型）

```json
"FAL_KEY": "your_fal_key_here"
```

在 [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys) 获取您的密钥。

---

## 自托管代理

`cli.js` 默认连接到托管的代理。如果您需要完全控制——或者需要在 `vercel.app` 被封锁的地区为用户服务——您可以从 `proxy/` 目录部署自己的实例。

### 快速部署（Vercel）

```bash
cd proxy
npm install
vercel --prod
```

### 环境变量

在您的 Vercel 项目中设置这些（控制台 → 设置 → 环境变量）：

| 变量 | 用于 | 获取方式 |
|---|---|---|
| `ELEVENLABS_API_KEY` | TTS、SFX、声音克隆 | [elevenlabs.io/app/settings/api-keys](https://elevenlabs.io/app/settings/api-keys) |
| `FAL_KEY` | 音乐生成 | [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys) |
| `VALID_PRO_KEYS` | (可选) 限制访问 | 允许的客户端密钥的逗号分隔列表 |

### 指定 cli.js 到您的代理

```bash
export AUDIOMIND_PROXY_URL="https://your-domain.com/api/audio"
```

或者设置在 `~/.openclaw/openclaw.json` 中：

```json
{
  "skills": {
    "entries": {
      "videoagent-audio-studio": {
        "env": {
          "AUDIOMIND_PROXY_URL": "https://your-domain.com/api/audio"
        }
      }
    }
  }
}
```

### 自定义域名（推荐）

如果您的用户在中国大陆，请在 Vercel 控制台 → 设置 → 域名中绑定自定义域名，以避免与 `vercel.app` 的 DNS 问题。

---

## 模型参考

| 模型 ID | 类型 | 提供商 | 备注 |
|---|---|---|---|
| `eleven_multilingual_v2` | TTS | ElevenLabs | 最佳质量，支持 29 种语言 |
| `eleven_turbo_v2_5` | TTS | ElevenLabs | 超低延迟，适合实时 |
| `eleven_monolingual_v1` | TTS | ElevenLabs | 仅英语，最快 |
| `cassetteai-music` | 音乐 | fal.ai | 可靠、快速的音乐生成 |
| `elevenlabs-sfx` | 音效 | ElevenLabs | 高质量音效（最长 22 秒） |
| `elevenlabs-voice-clone` | 克隆 | ElevenLabs | 从短音频样本克隆任何声音 |

---

## 更新日志

### v3.0.0
- **简化路由表**：从主参考中移除了不稳定的/离线模型。现在技能只会显示可靠工作的模型。
- **更清晰的用例触发**：添加了“使用场景”部分，以便代理在正确的时间激活此技能。
- **统一设置**：只需一个 `ELEVENLABS_API_KEY` 即可开始。`FAL_KEY` 现在是可选的。
- **移除轮询复杂性**：音乐生成现在默认使用 `cassetteai-music`，它同步完成。

### v2.1.0
- 添加了用于长时间运行音乐生成任务的异步工作流程。
- 添加了 `cassetteai-music` 作为音乐生成的稳定替代方案。

### v2.0.0
- 迁移到 ElevenLabs MCP 服务器架构。
- 添加了声音克隆支持。

### v1.0.0
- 初始版本，包含 TTS、音乐和音效路由。
