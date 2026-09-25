# ElevenLabs 音轨替换

将音频或视频翻译成其他语言，同时保留原始说话者的声音。从文件或 URL 创建项目，审阅和编辑源字幕，添加一个或多个目标语言，按片段细化翻译，并重新生成输出。

> **重要提示**：使用音轨替换项目 API — SDKs 中的 `elevenlabs.dubbing.project.*`，或 `/v1/dubbing/project` REST 端点。**不要**使用旧的 v1 音轨替换界面 (`client.dubbing.create()`、`client.dubbing.get()`、`client.dubbing.audio.get()` 或裸 `/v1/dubbing` 路径) — 那是旧的音轨替换 API，现在在 API 参考 中已归为遗留。

> **设置**：参见 [安装指南](references/installation.md)。`elevenlabs` CLI 和 SDKs 会自动读取 `ELEVENLABS_API_KEY`；REST 基础 URL 为 `https://api.elevenlabs.io`，API 密钥在 `xi-api-key` 头部。

## 概念

| 概念 | 含义 |
|------|------|
| **项目** | 一个媒体源（文件或 URL）及其源字幕。准备（转录）一次，然后处于 `ready` 状态，同时添加语言。 |
| **源字幕** | 可编辑的片段（文本、说话人、时间）从源转录而来。每个语言翻译的单一真实来源。 |
| **语言（目标）** | 一个音轨替换输出语言。每个都有自己的字幕（源片段 + 每个片段的翻译）和自己的音轨替换音频输出。 |
| **修订** | 独立的单调计数器。项目的 `revision` 在源字幕编辑时递增；语言的 `revision` 在翻译编辑或影响它的源编辑时递增。语言的 `output_revision` 是其当前音频生成的修订版本 — 当它落后于 `revision` 时，输出已过时。 |

**推荐操作顺序**：在添加任何语言之前**最终确定源字幕**。翻译是从源生成的，因此首先纠正源意味着每个语言都从正确的文本开始 — 在语言完成后编辑源会将其标记为 `stale` 并需要（付费）重新生成。

> **企业版**：字幕编辑和重新生成仅适用于企业工作区。创建项目、添加语言和下载音轨替换在所有计划中都适用。

## 工作流程

1. **创建** 从文件或 URL 创建项目 → `queued`
2. **轮询** 项目直到 `ready`
3. **审阅和最终确定源字幕**（编辑/添加/删除片段）
4. **添加** 每个目标一个语言 → `queued` → `processing` → `completed`
5. **下载** 每个语言的 `outputs.lossless_audio` 当 `completed` 时
6. **细化** 如有必要按片段翻译 → 语言变为 `stale`
7. **重新生成** 语言 → 再次 `completed` 并生成新输出

## 快速入门（Python）

```python
import os
import time
import requests
from elevenlabs.client import ElevenLabs

elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# 1. 从本地文件创建项目（或传递 source_url=... 代替 file）
with open("promo.mp4", "rb") as f:
    project = elevenlabs.dubbing.project.create(
        file=f,
        source_language="en",
        reference="Q3 营销视频",
    )

# 2. 等待源媒体转录完成
while True:
    project = elevenlabs.dubbing.project.get(project.project_id)
    if project.status == "ready":
        break
    if project.status == "failed":
        raise RuntimeError("项目准备失败")
    time.sleep(5)

# 3. 添加一个西班牙语目标语言
language = elevenlabs.dubbing.project.language.create(
    project.project_id,
    target_language="es",
)

# 4. 等待音轨替换生成完成
while True:
    language = elevenlabs.dubbing.project.language.get(
        project.project_id, language.language_id
    )
    if language.status == "completed":
        break
    if language.status == "failed":
        raise RuntimeError("音轨替换生成失败")
    time.sleep(5)

# 5. 下载音轨替换音频（签名 URL，有效约 1 小时 — 重新获取语言以获取新鲜 URL）
audio = requests.get(language.outputs.lossless_audio)
with open("promo_es.wav", "wb") as f:
    f.write(audio.content)
```

## 快速入门（JavaScript）

```typescript
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";
import { writeFile } from "fs/promises";

const elevenlabs = new ElevenLabsClient();

// 1. 创建项目（显示 sourceUrl；也支持文件上传）
let project = await elevenlabs.dubbing.project.create({
  sourceUrl: "https://example.com/promo.mp4",
  sourceLanguage: "en",
  reference: "Q3 营销视频",
});

// 2. 等待源媒体转录完成
while (true) {
  project = await elevenlabs.dubbing.project.get(project.projectId);
  if (project.status === "ready") break;
  if (project.status === "failed") throw new Error("项目准备失败");
  await new Promise((resolve) => setTimeout(resolve, 5000));
}

// 3. 添加一个西班牙语目标语言
let language = await elevenlabs.dubbing.project.language.create(project.projectId, {
  targetLanguage: "es",
});

// 4. 等待音轨替换生成完成
while (true) {
  language = await elevenlabs.dubbing.project.language.get(project.projectId, language.languageId);
  if (language.status === "completed") break;
  if (language.status === "failed") throw new Error("音轨替换生成失败");
  await new Promise((resolve) => setTimeout(resolve, 5000));
}

// 5. 从签名 URL 下载音轨替换音频
const response = await fetch(language.outputs!.losslessAudio!);
await writeFile("promo_es.wav", Buffer.from(await response.arrayBuffer()));
```

## 快速入门（CLI）

`elevenlabs` CLI 会自动从环境变量读取 `ELEVENLABS_API_KEY`。

```bash
# 1. 创建项目（使用 --source-url "https://..." 代替 --file 从 URL 音轨替换）
elevenlabs dubbing project create --file promo.mp4 --source-language en
# → {"project_id": "proj_...", "status": "queued", ...}

# 2. 轮询直到状态为 "ready"
elevenlabs dubbing project get --project-id proj_...

# 3. 添加目标语言
elevenlabs dubbing project language create --project-id proj_... --target-language es

# 4. 轮询语言直到 "completed"，然后下载 outputs.lossless_audio
elevenlabs dubbing project language get --project-id proj_... --language-id lang_...
```

## 创建选项

`elevenlabs dubbing project create`（REST: `POST /v1/dubbing/project`，`multipart/form-data`）接受**要么** `file` **要么** `source_url`（不能同时使用）：

| 字段 | 必填 | 备注 |
|------|------|------|
| `file` | `file`/`source_url` 其中之一 | 音轨替换的源媒体（音频或视频），最大 3 GiB |
| `source_url` | `file`/`source_url` 其中之一 | 获取源媒体的公共 URL |
| `source_language` | 否 | ISO 639 代码（例如 `en`）。省略将自动检测 — 检测到的语言会在源字幕的 `language` 字段中报告 |
| `reference` | 否 | 用于在您端识别项目的自由形式标签（最多 500 个字符） |
| `model_id` | 否 | `dubbing_v2`（默认） |
| `target_language` | 否 | 可选地在创建时排队第一个语言目标；使用 `language.create` 添加更多 |
| `keyterms` | 否 | 偏向转录/翻译的术语（产品/品牌名称）。最多 1000 个术语；每个最多 50 个字符和 5 个词；`<>{}[]\` 不允许。在 multipart 中对每个术语重复该字段 |

## 编辑源字幕

项目处于 `ready` 后，读取字幕，然后在添加语言之前进行纠正。每次编辑都会增加项目的 `revision`。每个片段都有一个稳定的 `id` 用于编辑或删除它。（仅限企业工作区。）

```python
# 读取源字幕
transcript = elevenlabs.dubbing.project.transcript.get(project_id)

# 纠正片段的文本 — 仅发送要更改的字段（text、speaker_id、start_s、end_s）
elevenlabs.dubbing.project.transcript.update_segment(
    project_id,
    segment_id=transcript.segments[0].id,
    text="欢迎来到我们最新的产品演示。",
)

# 添加片段（重用现有的 speaker_id 以使用该说话人的声音进行音轨替换）
added = elevenlabs.dubbing.project.transcript.create_segment(
    project_id,
    text="感谢观看。",
    speaker_id=transcript.segments[0].speaker_id,
    start_s=40.0,
    end_s=42.0,
)

# 删除片段
elevenlabs.dubbing.project.transcript.delete_segment(project_id, segment_id=added.segment.id)
```

通过 CLI：`elevenlabs dubbing project transcript get --project-id proj_...`，然后仅更新更改的字段（`--text`、`--speaker-id`、`--start-s`、`--end-s`）：

```bash
elevenlabs dubbing project transcript update_segment \
  --project-id proj_... --segment-id seg_... \
  --text "欢迎来到我们最新的产品演示。"
```

## 细化翻译和重新生成

语言的字幕将每个源片段与其 `translation`（`null` = 尚未翻译；片段 ID 与源匹配）配对。编辑单个翻译，然后重新生成。（仅限企业工作区。）

```python
# 读取语言的翻译
target = elevenlabs.dubbing.project.language.transcript.get(project_id, language_id)

# 细化单个翻译（传递 translation=None 以清除它并标记为重新翻译）
elevenlabs.dubbing.project.language.transcript.update_segment(
    project_id,
    language_id,
    segment_id=target.segments[0].id,
    translation="Bienvenido a nuestra última demostración de producto.",
)

# 从当前字幕重新生成音轨替换（付费，如生成）
elevenlabs.dubbing.project.language.transcript.regenerate(project_id, language_id)
```

通过 CLI：`elevenlabs dubbing project language transcript update_segment --project-id proj_... --language-id lang_... --segment-id seg_... --translation "..."`，然后 `elevenlabs dubbing project language transcript regenerate --project-id proj_... --language-id lang_...`（返回 `202 Accepted`）。

翻译编辑仅影响该语言。编辑后，`completed` 语言变为 `stale` — 它会保留其上一个输出，直到您重新生成。轮询直到 `completed`；`output_revision` 然后等于 `revision`，`outputs.lossless_audio` 反映当前字幕。

## 多语言音轨替换

每个语言目标添加一个语言 — 每个独立生成。使用 `language.list` 跟踪所有目标，而不是逐个轮询：

```python
for lang in ["es", "fr", "de", "ja"]:
    elevenlabs.dubbing.project.language.create(project_id, target_language=lang)

while True:
    result = elevenlabs.dubbing.project.language.list(project_id)
    if not any(l.status in ("queued", "processing") for l in result.languages):
        break
    time.sleep(5)
```

## 状态

**项目：**

| 状态 | 含义 |
|------|------|
| `queued` | 创建；源获取 + 准备排队 |
| `preparing` | 准备（转录）运行中 |
| `ready` | 源字幕可用；添加/生成语言。项目 **保持** `ready` — 每个语言的进度在语言上 |
| `failed` | 准备失败（例如，源无法获取或解码） |

**语言：**

| 状态 | 含义 |
|------|------|
| `queued` | 等待项目变为 `ready`，或等待生成工作线程 |
| `processing` | 音轨替换正在生成 |
| `completed` | 完成；`outputs` 包含签名下载 URL（有效约 1 小时 — 重新获取以获取新鲜 URL） |
| `stale` | 之前完成，但字幕已更改；保留最后一个输出，直到重新生成 |
| `failed` | 生成失败 |

您可以添加语言，而项目尚未 `ready` — 它会保持 `queued`，一旦项目变为 `ready` 就会自动开始。添加语言接受可选的 `model_id`（默认为项目的）和 `voice_settings`（例如 `{"cloning_strength": 7}`，范围 0–10，默认 7 — 控制音轨替换说话人克隆源声音的强度）。

## 错误处理

- **401**：无效的 API 密钥
- **409 冲突** 在重新生成时：项目未 `ready` 或语言未稳定（例如，正在生成） — 等待并重试
- **过期的下载 URL**：`outputs.lossless_audio` 签名且有效约 1 小时；重新获取语言以获取新鲜 URL
- **字幕编辑 / 重新生成不可用**：这些端点仅适用于企业 — 在其他计划中，使用最终确定的源创建项目，并直接添加语言

## 参考

- [安装指南](references/installation.md)
- [API 参考](references/api-reference.md) — 每个端点的完整请求/响应模式和 SDK 方法名称
