# 文本转语音（HeyGen Starfish）

使用HeyGen的内部Starfish TTS模型通过v3 API从文本生成语音音频文件。这项技能用于独立音频生成——与视频创建分开。

## 认证

所有请求都需要`X-Api-Key`头部。设置`HEYGEN_API_KEY`环境变量。

```bash
curl -X GET "https://api.heygen.com/v3/voices?engine=starfish" \
  -H "X-Api-Key: $HEYGEN_API_KEY"
```

## 工具选择

如果HeyGen MCP工具可用（`mcp__heygen__*`），**优先使用**它们，而不是直接HTTP API调用。

| 任务 | MCP工具 | 备用（直接API） |
|------|----------|----------------------|
| 列出TTS语音 | `mcp__heygen__list_audio_voices` | `GET /v3/voices?engine=starfish` |
| 生成语音音频 | `mcp__heygen__text_to_speech` | `POST /v3/voices/speech` |

## 默认工作流程

1. 使用`mcp__heygen__list_audio_voices`（或`GET /v3/voices?engine=starfish`）列出语音
2. 选择符合所需语言、性别和功能的语音
3. 调用`mcp__heygen__text_to_speech`（或`POST /v3/voices/speech`）并传入文本和voice_id
4. 使用返回的`audio_url`下载或播放音频

## 列出TTS语音

检索与Starfish TTS模型兼容的语音。

> **注意**：这使用统一的`GET /v3/voices`端点，并带有`engine=starfish`过滤器来仅返回TTS兼容的语音。并非所有视频语音都支持Starfish TTS。响应是分页的——使用`next_token`来获取附加页面。

### 查询参数

| 参数 | 类型 | 描述 |
|-------|------|-------------|
| `engine` | string | 按引擎筛选（使用`starfish`获取TTS语音） |
| `type` | string | `public`或`private` |
| `language` | string | 按语言筛选 |
| `gender` | string | 按性别筛选 |
| `limit` | integer | 每页结果，1-100 |
| `token` | string | 来自`next_token`的分页游标 |

### curl

```bash
curl -X GET "https://api.heygen.com/v3/voices?engine=starfish" \
  -H "X-Api-Key: $HEYGEN_API_KEY"
```

### TypeScript

```typescript
interface AudioVoiceItem {
  voice_id: string;
  name: string;
  language: string;
  gender: "female" | "male" | "unknown";
  preview_audio_url: string | null;
  support_pause: boolean;
  support_locale: boolean;
  type: string;
}

interface TTSVoicesResponse {
  error: null | string;
  data: AudioVoiceItem[];
  has_more: boolean;
  next_token: string | null;
}

async function listTTSVoices(): Promise<AudioVoiceItem[]> {
  const allVoices: AudioVoiceItem[] = [];
  let token: string | null = null;

  do {
    const url = new URL("https://api.heygen.com/v3/voices");
    url.searchParams.set("engine", "starfish");
    if (token) url.searchParams.set("token", token);

    const response = await fetch(url.toString(), {
      headers: { "X-Api-Key": process.env.HEYGEN_API_KEY! },
    });

    const json: TTSVoicesResponse = await response.json();

    if (json.error) {
      throw new Error(json.error);
    }

    allVoices.push(...json.data);
    token = json.next_token;
  } while (token);

  return allVoices;
}
```

### Python

```python
import requests
import os

def list_tts_voices() -> list:
    all_voices = []
    token = None

    while True:
        params = {"engine": "starfish"}
        if token:
            params["token"] = token

        response = requests.get(
            "https://api.heygen.com/v3/voices",
            headers={"X-Api-Key": os.environ["HEYGEN_API_KEY"]},
            params=params,
        )

        data = response.json()
        if data.get("error"):
            raise Exception(data["error"])

        all_voices.extend(data["data"])

        if not data.get("has_more"):
            break
        token = data.get("next_token")

    return all_voices
```

### 响应格式

```json
{
  "error": null,
  "data": [
    {
      "voice_id": "f38a635bee7a4d1f9b0a654a31d050d2",
      "name": "Chill Brian",
      "language": "English",
      "gender": "male",
      "preview_audio_url": "https://resource.heygen.ai/text_to_speech/WpSDQvmLGXEqXZVZQiVeg6.mp3",
      "support_pause": true,
      "support_locale": false,
      "type": "public"
    }
  ],
  "has_more": false,
  "next_token": null
}
```

## 生成语音音频

使用指定语音将文本转换为语音音频。

### 端点

`POST https://api.heygen.com/v3/voices/speech`

### 请求字段

| 字段 | 类型 | 必填 | 描述 |
|-------|------|:---:|-------------|
| `text` | string | Y | 要转换的文本内容（1-5000个字符） |
| `voice_id` | string | Y | 来自`GET /v3/voices?engine=starfish`的语音ID |
| `input_type` | string | | `"text"`（默认）或`"ssml"`用于完整SSML标记 |
| `speed` | number | | 语音速度，0.5-2.0（默认：1.0） |
| `language` | string | | 基础语言代码（例如，`"en"`，`"pt"`）。如果省略，则自动检测 |
| `locale` | string | | 多语言语音的BCP-47语言环境（例如，`"en-US"`，`"pt-BR"`） |

### curl

```bash
curl -X POST "https://api.heygen.com/v3/voices/speech" \
  -H "X-Api-Key: $HEYGEN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! Welcome to our product demo.",
    "voice_id": "YOUR_VOICE_ID",
    "speed": 1.0
  }'
```

### TypeScript

```typescript
interface TTSRequest {
  text: string;
  voice_id: string;
  input_type?: "text" | "ssml";
  speed?: number;
  language?: string;
  locale?: string;
}

interface WordTimestamp {
  word: string;
  start: number;
  end: number;
}

interface TTSResponse {
  error: null | string;
  data: {
    audio_url: string;
    duration: number;
    request_id?: string;
    word_timestamps?: WordTimestamp[];
  };
}

async function textToSpeech(request: TTSRequest): Promise<TTSResponse["data"]> {
  const response = await fetch(
    "https://api.heygen.com/v3/voices/speech",
    {
      method: "POST",
      headers: {
        "X-Api-Key": process.env.HEYGEN_API_KEY!,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    }
  );

  const json: TTSResponse = await response.json();

  if (json.error) {
    throw new Error(json.error);
  }

  return json.data;
}
```

### Python

```python
import requests
import os

def text_to_speech(
    text: str,
    voice_id: str,
    input_type: str = "text",
    speed: float = 1.0,
    language: str | None = None,
    locale: str | None = None,
) -> dict:
    payload = {
        "text": text,
        "voice_id": voice_id,
        "speed": speed,
    }

    if input_type != "text":
        payload["input_type"] = input_type

    if language:
        payload["language"] = language

    if locale:
        payload["locale"] = locale

    response = requests.post(
        "https://api.heygen.com/v3/voices/speech",
        headers={
            "X-Api-Key": os.environ["HEYGEN_API_KEY"],
            "Content-Type": "application/json",
        },
        json=payload,
    )

    data = response.json()
    if data.get("error"):
        raise Exception(data["error"])

    return data["data"]
```

### 响应格式

```json
{
  "error": null,
  "data": {
    "audio_url": "https://resource2.heygen.ai/text_to_speech/.../id=365d46bb.wav",
    "duration": 5.526,
    "request_id": "p38QJ52hfgNlsYKZZmd9",
    "word_timestamps": [
      { "word": "<start>", "start": 0.0, "end": 0.0 },
      { "word": "Hey", "start": 0.079, "end": 0.219 },
      { "word": "there,", "start": 0.239, "end": 0.459 },
      { "word": "<end>", "start": 5.526, "end": 5.526 }
    ]
  }
}
```

## 使用示例

### 基本TTS

```typescript
const result = await textToSpeech({
  text: "Welcome to our quarterly earnings call.",
  voice_id: "YOUR_VOICE_ID",
});

console.log(`Audio URL: ${result.audio_url}`);
console.log(`Duration: ${result.duration}s`);
```

### 调整速度

```typescript
const result = await textToSpeech({
  text: "We're thrilled to announce our newest feature!",
  voice_id: "YOUR_VOICE_ID",
  speed: 1.1,
});
```

### 为多语言语音设置语言和区域

```typescript
const result = await textToSpeech({
  text: "Bem-vindo ao nosso produto.",
  voice_id: "MULTILINGUAL_VOICE_ID",
  language: "pt",
  locale: "pt-BR",
});
```

### 使用SSML输入

```typescript
const result = await textToSpeech({
  text: '<speak>Hello <break time="1s"/> and welcome!</speak>',
  voice_id: "YOUR_VOICE_ID",
  input_type: "ssml",
});
```

### 查找语音并生成音频

```typescript
async function generateSpeech(text: string, language: string): Promise<string> {
  const voices = await listTTSVoices();
  const voice = voices.find(
    (v) => v.language.toLowerCase().includes(language.toLowerCase())
  );

  if (!voice) {
    throw new Error(`No TTS voice found for language: ${language}`);
  }

  const result = await textToSpeech({
    text,
    voice_id: voice.voice_id,
  });

  return result.audio_url;
}

const audioUrl = await generateSpeech("Hello and welcome!", "english");
```

## 停顿使用Break标签

在文本中使用SSML风格的break标签进行停顿：

```
word <break time="1s"/> word
```

规则：
- 使用秒数和`s`后缀：`<break time="1.5s"/>`
- 标签前后必须有空格
- 自闭合标签格式

通过v3，您还可以使用`input_type: "ssml"`获取完整SSML支持，允许更丰富的标记而不仅仅是break标签：

```json
{
  "text": "<speak>Welcome! <break time=\"1s\"/> Let's get started.</speak>",
  "voice_id": "YOUR_VOICE_ID",
  "input_type": "ssml"
}
```

## 最佳实践

1. **使用`GET /v3/voices?engine=starfish`** 来查找兼容的语音——统一的`/v3/voices`端点提供所有语音类型，因此`engine=starfish`过滤器对于TTS至关重要
2. **在设置`locale`之前检查`support_locale`**——只有多语言语音支持区域选择
3. **保持速度在0.8-1.2** 以获得自然的声音输出
4. **在生成之前预览语音** 使用`preview_audio_url`（某些语音可能为null）
5. **使用`word_timestamps`** 在响应中进行字幕同步或定时文本叠加
6. **在文本中使用SSML break标签** 进行停顿：`word <break time="1s"/> word`
7. **使用`input_type: "ssml"`** 当您需要完整SSML标记控制时（超出简单的break标签）
8. **分页列出语音**——v3端点返回分页结果；使用`has_more`和`next_token`来获取所有语音
