# Voicebox 语音合成工作室

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

Voicebox 是一个本地优先、开源的语音克隆和TTS工作室 — 是ElevenLabs的自托管替代品。它完全在您的机器上运行（macOS MLX/Metal、Windows/Linux CUDA、CPU回退），在 `localhost:17493` 上公开REST API，并附带5个TTS引擎、23种语言、后期处理效果和多轨Stories编辑器。

---

## 安装

### 预构建的二进制文件（推荐）

| 平台        | 链接                                       |
|-------------|------------------------------------------|
| macOS Apple Silicon | https://voicebox.sh/download/mac-arm |
| macOS Intel   | https://voicebox.sh/download/mac-intel |
| Windows     | https://voicebox.sh/download/windows   |
| Docker      | `docker compose up`                     |

Linux需要从源代码构建：https://voicebox.sh/linux-install

### 从源代码构建

**先决条件：** [Bun](https://bun.sh)、[Rust](https://rustup.rs)、[Python 3.11+](https://python.org)、Tauri先决条件

```bash
git clone https://github.com/jamiepine/voicebox.git
cd voicebox

# 安装仅任务运行器
brew install just        # macOS
cargo install just       # 任何平台

# 设置Python venv + 所有依赖项
just setup

# 以开发模式启动后端 + 桌面应用程序
just dev
```

```bash
# 列出所有可用命令
just --list
```

---

## 架构

| 层级        | 技术                 |
|-------------|----------------------|
| 桌面应用程序 | Tauri (Rust)        |
| 前端        | React + TypeScript + Tailwind CSS |
| 状态        | Zustand + React Query |
| 后端        | FastAPI (Python) 在端口 17493 |
| TTS引擎     | Qwen3-TTS、LuxTTS、Chatterbox、Chatterbox Turbo、TADA |
| 效果        | Pedalboard (Spotify) |
| 转录        | Whisper / Whisper Turbo |
| 推理        | MLX (Apple Silicon) / PyTorch (CUDA/ROCm/XPU/CPU) |
| 数据库      | SQLite              |

Python FastAPI后端处理所有ML推理。Tauri Rust外壳包装前端并管理后端进程生命周期。即使在使用桌面应用程序时，API也可直接访问 `http://localhost:17493`。

---

## REST API参考

基础URL：`http://localhost:17493`  
交互式文档：`http://localhost:17493/docs`

### 生成语音

```bash
# 基本生成
curl -X POST http://localhost:17493/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world, this is a voice clone.",
    "profile_id": "abc123",
    "language": "en"
  }'

# 选择引擎
curl -X POST http://localhost:17493/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Speak slowly and with gravitas.",
    "profile_id": "abc123",
    "language": "en",
    "engine": "qwen3-tts"
  }'

# 带有副语言标签（仅Chatterbox Turbo）
curl -X POST http://localhost:17493/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "That is absolutely hilarious! [laugh] I cannot believe it.",
    "profile_id": "abc123",
    "engine": "chatterbox-turbo",
    "language": "en"
  }'
```

### 语音配置文件

```bash
# 列出所有配置文件
curl http://localhost:17493/profiles

# 创建新配置文件
curl -X POST http://localhost:17493/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Narrator",
    "language": "en",
    "description": "Deep narrative voice"
  }'

# 上传音频样本到配置文件
curl -X POST http://localhost:17493/profiles/{profile_id}/samples \
  -F "file=@/path/to/voice-sample.wav"

# 导出配置文件
curl http://localhost:17493/profiles/{profile_id}/export \
  --output narrator-profile.zip

# 导入配置文件
curl -X POST http://localhost:17493/profiles/import \
  -F "file=@narrator-profile.zip"
```

### 生成队列和状态

```bash
# 获取生成状态（SSE流）
curl -N http://localhost:17493/generate/{generation_id}/status

# 列出最近生成
curl http://localhost:17493/generations

# 重试失败的生成
curl -X POST http://localhost:17493/generations/{generation_id}/retry

# 下载生成音频
curl http://localhost:17493/generations/{generation_id}/audio \
  --output output.wav
```

### 模型

```bash
# 列出可用模型和下载状态
curl http://localhost:17493/models

# 从GPU内存卸载模型（不删除）
curl -X POST http://localhost:17493/models/{model_id}/unload
```

---

## TypeScript/JavaScript集成

### 基本TTS客户端

```typescript
const VOICEBOX_URL = process.env.VOICEBOX_API_URL ?? "http://localhost:17493";

interface GenerateRequest {
  text: string;
  profile_id: string;
  language?: string;
  engine?: "qwen3-tts" | "luxtts" | "chatterbox" | "chatterbox-turbo" | "tada";
}

interface GenerateResponse {
  generation_id: string;
  status: "queued" | "processing" | "complete" | "failed";
  audio_url?: string;
}

async function generateSpeech(req: GenerateRequest): Promise<GenerateResponse> {
  const response = await fetch(`${VOICEBOX_URL}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    throw new Error(`Voicebox API错误: ${response.status} ${await response.text()}`);
  }

  return response.json();
}

// 使用示例
const result = await generateSpeech({
  text: "Welcome to our application.",
  profile_id: "abc123",
  language: "en",
  engine: "qwen3-tts",
});

console.log("生成ID:", result.generation_id);
```

### 等待完成

```typescript
async function waitForGeneration(
  generationId: string,
  timeoutMs = 60_000
): Promise<string> {
  const start = Date.now();

  while (Date.now() - start < timeoutMs) {
    const res = await fetch(`${VOICEBOX_URL}/generations/${generationId}`);
    const data = await res.json();

    if (data.status === "complete") {
      return `${VOICEBOX_URL}/generations/${generationId}/audio`;
    }
    if (data.status === "failed") {
      throw new Error(`生成失败: ${data.error}`);
    }

    await new Promise((r) => setTimeout(r, 1000));
  }

  throw new Error("生成超时");
}
```

### 使用SSE流状态

```typescript
function streamGenerationStatus(
  generationId: string,
  onStatus: (status: string) => void
): () => void {
  const eventSource = new EventSource(
    `${VOICEBOX_URL}/generate/${generationId}/status`
  );

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onStatus(data.status);

    if (data.status === "complete" || data.status === "failed") {
      eventSource.close();
    }
  };

  eventSource.onerror = () => eventSource.close();

  // 返回清理函数
  return () => eventSource.close();
}

// 使用示例
const cleanup = streamGenerationStatus("gen_abc123", (status) => {
  console.log("状态更新:", status);
});
```

### 下载音频为Blob

```typescript
async function downloadAudio(generationId: string): Promise<Blob> {
  const response = await fetch(
    `${VOICEBOX_URL}/generations/${generationId}/audio`
  );

  if (!response.ok) {
    throw new Error(`下载音频失败: ${response.status}`);
  }

  return response.blob();
}

// 在浏览器中播放
async function playGeneratedAudio(generationId: string): Promise<void> {
  const blob = await downloadAudio(generationId);
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.play();
  audio.onended = () => URL.revokeObjectURL(url);
}
```

---

## Python集成

```python
import httpx
import asyncio

VOICEBOX_URL = "http://localhost:17493"

async def generate_speech(
    text: str,
    profile_id: str,
    language: str = "en",
    engine: str = "qwen3-tts"
) -> bytes:
    async with httpx.AsyncClient(timeout=120.0) as client:
        # 提交生成
        resp = await client.post(
            f"{VOICEBOX_URL}/generate",
            json={
                "text": text,
                "profile_id": profile_id,
                "language": language,
                "engine": engine,
            }
        )
        resp.raise_for_status()
        generation_id = resp.json()["generation_id"]

        # 等待完成
        for _ in range(120):
            status_resp = await client.get(
                f"{VOICEBOX_URL}/generations/{generation_id}"
            )
            status_data = status_resp.json()

            if status_data["status"] == "complete":
                audio_resp = await client.get(
                    f"{VOICEBOX_URL}/generations/{generation_id}/audio"
                )
                return audio_resp.content

            if status_data["status"] == "failed":
                raise RuntimeError(f"生成失败: {status_data.get('error')}")

            await asyncio.sleep(1.0)

        raise TimeoutError("生成超时")

# 使用示例
audio_bytes = asyncio.run(
    generate_speech(
        text="The quick brown fox jumps over the lazy dog.",
        profile_id="your-profile-id",
        language="en",
        engine="chatterbox",
    )
)

with open("output.wav", "wb") as f:
    f.write(audio_bytes)
```

---

## TTS引擎选择指南

| 引擎         | 适用场景     | 语言     | VRAM   | 备注         |
|--------------|--------------|----------|--------|--------------|
| `qwen3-tts` (0.6B/1.7B) | 质量 + 指令 | 10       | 中等   | 支持文本中的交付指令 |
| `luxtts`     | 快速CPU生成 | 仅英语   | ~1GB   | 150倍实时，48kHz |
| `chatterbox` | 多语言覆盖   | 23       | 中等   | 阿拉伯语、印地语、斯瓦希里语、CJK等更多语言 |
| `chatterbox-turbo` | 表达/情感   | 仅英语   | 低 (350M) | 使用 `[laugh]`、`[sigh]`、`[gasp]` 标签 |
| `tada` (1B/3B) | 长文本连贯性 | 10       | 高     | 700秒+音频，HumeAI模型 |

### 交付指令（Qwen3-TTS）

直接在文本中嵌入自然语言指令：

```typescript
await generateSpeech({
  text: "(whisper) I have a secret to tell you.",
  profile_id: "abc123",
  engine: "qwen3-tts",
});

await generateSpeech({
  text: "(speak slowly and clearly) Step one: open the application.",
  profile_id: "abc123",
  engine: "qwen3-tts",
});
```

### 副语言标签（Chatterbox Turbo）

```typescript
const tags = [
  "[laugh]", "[chuckle]", "[gasp]", "[cough]",
  "[sigh]", "[groan]", "[sniff]", "[shush]", "[clear throat]"
];

await generateSpeech({
  text: "Oh really? [gasp] I had no idea! [laugh] That's incredible.",
  profile_id: "abc123",
  engine: "chatterbox-turbo",
});
```

---

## 环境与配置

```bash
# 自定义模型目录（启动前设置）
export VOICEBOX_MODELS_DIR=/path/to/models

# AMD ROCm GPU（自动配置，但可以覆盖）
export HSA_OVERRIDE_GFX_VERSION=11.0.0
```

Docker配置（`docker-compose.yml`覆盖）：

```yaml
services:
  voicebox:
    environment:
      - VOICEBOX_MODELS_DIR=/models
    volumes:
      - /host/models:/models
    ports:
      - "17493:17493"
    # 用于NVIDIA GPU直通：
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 常见模式

### 语音配置文件创建流程

```typescript
// 1. 创建配置文件
const profile = await fetch(`${VOICEBOX_URL}/profiles`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "My Voice", language: "en" }),
}).then((r) => r.json());

// 2. 上传音频样本（WAV/MP3，最好是5-30秒的干净语音）
const formData = new FormData();
formData.append("file", audioBlob, "sample.wav");

await fetch(`${VOICEBOX_URL}/profiles/${profile.id}/samples`, {
  method: "POST",
  body: formData,
});

// 3. 使用新配置文件生成
const gen = await generateSpeech({
  text: "Testing my cloned voice.",
  profile_id: profile.id,
});
```

### 批量生成与队列

```typescript
async function batchGenerate(
  items: Array<{ text: string; profileId: string }>,
  engine = "qwen3-tts"
): Promise<string[]> {
  // 提交所有 — Voicebox串行排队以避免GPU竞争
  const submissions = await Promise.all(
    items.map((item) =>
      generateSpeech({ text: item.text, profile_id: item.profileId, engine })
    )
  );

  // 等待所有完成
  const audioUrls = await Promise.all(
    submissions.map((s) => waitForGeneration(s.generation_id))
  );

  return audioUrls;
}
```

### 长文本（自动分块）

Voicebox自动在句子边界分块 — 只需发送完整文本：

```typescript
const longScript = `
  Chapter one. The morning fog rolled across the valley floor...
  // 支持最多50,000个字符
`;

await generateSpeech({
  text: longScript,
  profile_id: "narrator-profile-id",
  engine: "tada", // 长文本连贯性最佳
  language: "en",
});
```

---

## 故障排除

### API无响应

```bash
# 检查后端是否运行
curl http://localhost:17493/health

# 仅重启后端（开发模式）
just backend

# 查看日志
just logs
```

### GPU未检测到

```bash
# 检查检测到的后端
curl http://localhost:17493/system/info

# 强制CPU模式（启动前设置）
export VOICEBOX_FORCE_CPU=1
```

### 模型下载失败/缓慢

```bash
# 设置自定义模型目录（更多空间）
export VOICEBOX_MODELS_DIR=/path/with/space
just dev

# 通过API取消卡住的下载
curl -X DELETE http://localhost:17493/models/{model_id}/download
```

### VRAM不足 — 卸载模型

```bash
# 列出已加载模型
curl http://localhost:17493/models | jq '.[] | select(.loaded == true)'

# 卸载特定模型
curl -X POST http://localhost:17493/models/{model_id}/unload
```

### 音质问题

- 使用5-30秒的干净、无噪声语音作为语音样本
- 多个样本提高克隆质量 — 上传3-5个不同的句子
- 对于多语言克隆，使用 `chatterbox` 引擎
- 确保样本音频为16kHz+单声道WAV以获得最佳结果
- 使用 `luxtts` 获取最高输出质量（48kHz）的英语

### 生成卡在队列中后崩溃

Voicebox在启动时自动恢复过时的生成。如果问题仍然存在：

```bash
curl -X POST http://localhost:17493/generations/{generation_id}/retry
```

---

## 前端集成（React示例）

```tsx
import { useState } from "react";

const VOICEBOX_URL = import.meta.env.VITE_VOICEBOX_URL ?? "http://localhost:17493";

export function VoiceGenerator({ profileId }: { profileId: string }) {
  const [text, setText] = useState("");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${VOICEBOX_URL}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, profile_id: profileId, language: "en" }),
      });
      const { generation_id } = await res.json();

      // 等待完成
      let done = false;
      while (!done) {
        await new Promise((r) => setTimeout(r, 1000));
        const statusRes = await fetch(`${VOICEBOX_URL}/generations/${generation_id}`);
        const { status } = await statusRes.json();
        if (status === "complete") {
          setAudioUrl(`${VOICEBOX_URL}/generations/${generation_id}/audio`);
          done = true;
        } else if (status === "failed") {
          throw new Error("生成失败");
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <textarea value={text} onChange={(e) => setText(e.target.value)} />
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? "生成中..." : "生成语音"}
      </button>
      {audioUrl && <audio controls src={audioUrl} />}
    </div>
  );
}
```
