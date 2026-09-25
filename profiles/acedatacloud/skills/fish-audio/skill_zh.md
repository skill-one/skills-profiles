# Fish Audio — 文本转语音

通过 AceDataCloud 的 Fish Audio API 生成旁白/配音。

> **设置：** 请参考 [认证](../_shared/authentication.md) 了解令牌设置方法。

## 快速入门

```bash
curl -X POST https://api.acedata.cloud/fish/tts \
  -H "Authorization: ******ACEDATACLOUD_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "model: s2-pro" \
  -d '{"text":"你好，欢迎使用 AceData Cloud。","reference_id":"d7900c21663f485ab63ebdb7e5905036","format":"mp3"}'
```

同步响应将返回直接音频链接：

```json
{"audio_url":"https://platform.r2.fish.audio/task/8a72ff9840234006a9f74cb2fa04f978.mp3"}
```

## 端点

| 端点 | 用途 |
|----------|---------|
| `POST /fish/tts` | 文本转语音生成 |
| `GET /fish/model` | 浏览/搜索公共 Fish 参考语音 |
| `GET /fish/model/{id}` | 通过 ID 获取单个参考语音 |
| `POST /fish/tasks` | 当 `async: true` 时轮询异步 TTS 任务 |

## 工作流

### 1. 查找参考语音

```bash
curl "https://api.acedata.cloud/fish/model?page_size=10&page_number=1&title=Marcus" \
  -H "Authorization: ******ACEDATACLOUD_API_TOKEN"
```

响应包含 `items[]`，其中包含公共语音元数据，例如 `_id`、`title`、`languages`、`tags`、`visibility` 和 `state`。使用项目 `_id` 作为 TTS 请求中的 `reference_id`。

### 2. 文本转语音

```json
POST /fish/tts
Headers:
  model: s2-pro

{
  "text": "您的旁白文本。",
  "reference_id": "d7900c21663f485ab63ebdb7e5905036",
  "format": "mp3"
}
```

### 3. 单次语音克隆

使用临时参考语音而不创建持久模型：

```json
POST /fish/tts
Headers:
  model: s2-pro

{
  "text": "在参考语音中生成的新语音。",
  "format": "mp3",
  "references": [{
    "audio": "https://cdn.acedata.cloud/reference.mp3",
    "text": "参考音频中讲的确切文字。"
  }]
}
```

`audio` 必须是公共的 HTTPS MP3/WAV 链接，`text` 必须是确切的文本稿。使用一个持续 10–270 秒的参考。不要将 `references` 与 `reference_id` 结合使用；当相同的保存/公共语音将被重复使用时，请使用 `reference_id`。AceDataCloud 端点不接受原始字节、Base64、数据 URI 和 MessagePack。

### 4. 异步 TTS

```json
POST /fish/tts
Headers:
  model: s1

{
  "text": "用于后台处理的较长旁白。",
  "async": true,
  "callback_url": "https://api.acedata.cloud/health"
}
```

> **异步：** 请参考 [异步任务轮询](../_shared/async-tasks.md)。通过 `POST /fish/tasks` 使用 `{"id":"..."}` 进行轮询。

## 参数 — `/fish/tts`

### 头部

| 参数 | 值 | 描述 |
|-----------|--------|-------|
| `model` | `"s1"`, `"s2-pro"`, `"s2.1-pro"` | Fish TTS 引擎选择 |

### JSON 正文

| 参数 | 类型/值 | 描述 |
|-----------|----------|-------|
| `text` | 字符串 | 要合成的文本（必填） |
| `reference_id` | 字符串 | 来自 `GET /fish/model` 的公共/参考语音 ID |
| `format` | `"mp3"`, `"wav"`, `"pcm"` | 输出格式 |
| `sample_rate` | 整数 | 可选输出采样率 |
| `mp3_bitrate` | `64`, `128`, `192` | MP3 速率 |
| `latency` | `"normal"`, `"balanced"` | TTS 延迟模式 |
| `chunk_length` / `min_chunk_length` | 整数 | 分块控制 |
| `temperature`, `top_p`, `repetition_penalty` | 数字 | 采样控制 |
| `max_new_tokens` | 整数 | 最大生成令牌数 |
| `normalize` | 布尔值 | 规范化生成音频 |
| `prosody` | 对象 | 语音语调调整 |
| `references` | 数组 | 用于单次语音克隆的 `{audio, text}` 对象；与 `reference_id` 互斥 |
| `callback_url` | 字符串 | 异步回调 URL |
| `async` | 布尔值 | 异步运行并通过 `/fish/tasks` 轮询 |

## 注意事项

- 文档中的 TTS 端点是 `POST /fish/tts` — 不是 `/fish/audios`。
- 使用 **`model` 请求头部** 选择 Fish 引擎，而不是 JSON `model` 字段。
- 使用来自 `GET /fish/model` 的 `reference_id` — 不是 `voice_id`。
- 使用 `references` 进行单次克隆，该克隆不会保存为模型。
- 计费基于目标文本的 UTF-8 字节数；参考音频不会增加单独的克隆费。
- 同步请求直接返回 `audio_url`；异步任务应通过 `/fish/tasks` 进行轮询。
