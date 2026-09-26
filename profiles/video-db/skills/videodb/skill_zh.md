# 视频数据库技能

**感知 + 记忆 + 行动，适用于视频、直播流和桌面会话。**

当你需要时，使用此技能：

## 1) 桌面感知
- 开始/停止捕获**桌面会话**的**屏幕、麦克风和系统音频**
- 流式传输**实时上下文**并存储**会话记忆**
- 对所说的和屏幕上发生的事情运行**实时警报/触发器**
- 生成**会话摘要**、可搜索的时间线以及**可播放的证据链接**

## 2) 视频摄取 + 流式传输
- 摄取**文件或 URL**，并返回**可播放的网页流链接**
- 转码/规范化：**编解码器、比特率、帧率、分辨率、宽高比**

## 3) 理解 + 索引 + 检索（时间戳 + 证据）
- **理解**：对语音、场景、对象、OCR、品牌、活动运行分析器
- **索引**：将分析器生成的数据转换为语义化、可过滤和可聚合的索引
- **检索**：搜索时刻、提问、精确过滤、计数和分组——带有**时间戳**和**可播放的证据**
- 从结果中自动创建**片段**

## 4) 时间线编辑 + 生成
- 字幕：**生成**、**翻译**、**嵌入**
- 覆盖层：**文本/图像/品牌**、动态字幕
- 音频：**背景音乐**、**旁白**、**配音**
- 通过**时间线操作**进行程序化合成和导出

## 5) 直播流（RTSP） + 监控
- 连接**RTSP/直播源**
- 运行**实时视觉和语音理解**，并为监控工作流程发出**事件/警报**

---

## 常见输入
- 本地**文件路径**、公共**URL**或**RTSP URL**
- 桌面捕获请求：**开始 / 停止 / 摘要会话**
- 期望操作：获取理解上下文、转码规格、索引规格、搜索查询、片段范围、时间线编辑、警报规则

## 常见输出
- **流 URL**——使其可播放：`https://console.videodb.io/player?url={STREAM_URL}`
- 带有**时间戳**和**证据链接**的搜索结果
- 生成的资源：字幕、音频、图像、片段
- 直播流的**事件/警报有效负载**
- 桌面**会话摘要**和记忆条目

---

## 通用提示（示例）
- “开始桌面捕获，并在密码字段出现时发出警报。”
- “记录我的会话，并在结束时生成可操作的摘要。”
- “摄取此文件并返回可播放的流链接。”
- “索引此文件夹并查找所有包含人物的场景，返回时间戳。”
- “生成字幕，嵌入它们，并添加轻柔的背景音乐。”
- “连接此 RTSP URL，并在有人进入区域时发出警报。”

## 运行 Python 代码

**关键**：在运行 Python 代码之前，始终使用 `cd` 切换到用户的项目目录。这确保 `load_dotenv(".env")` 找到正确的 `.env` 文件。

```python
from dotenv import load_dotenv
load_dotenv(".env")

import videodb
conn = videodb.connect()
```

这会从以下位置读取 `VIDEO_DB_API_KEY`：
1. 环境变量（如果已导出）
2. 当前目录中的项目 `.env` 文件

如果密钥缺失，`videodb.connect()` 会自动引发 `AuthenticationError`。

当简短的行内命令即可工作时，**不要**编写脚本文件。

在编写行内 Python (`python -c "..."`) 时，始终使用格式良好的代码——使用分号分隔语句并保持可读性。对于超过约 3 个语句的内容，使用 heredoc 代替：

```bash
python << 'EOF'
from dotenv import load_dotenv
load_dotenv(".env")

import videodb
conn = videodb.connect()
coll = conn.get_collection()
print(f"Videos: {len(coll.get_videos())}")
EOF
```

## 设置

当用户要求“设置 videodb”或类似操作时：

### 1. 安装 SDK

```bash
pip install "videodb[capture]>=0.5.0" python-dotenv
```

如果在 Linux 上 `videodb[capture]` 失败，则不安装捕获扩展：

```bash
pip install "videodb>=0.5.0" python-dotenv
```

`>=0.5.0` 的标记很重要——理解/索引/提问/聚合 API 在早期版本中不存在。

### 2. 配置 API 密钥

用户必须使用**任一**方法设置 `VIDEO_DB_API_KEY`：

- **终端中导出（推荐）**：`export VIDEO_DB_API_KEY=your-key`
- **项目 `.env` 文件**：在项目的 `.env` 文件中保存 `VIDEO_DB_API_KEY=your-key`

在 https://console.videodb.io 获取免费 API 密钥（50 次免费上传，无需信用卡）。

**不要**自己读取、写入或处理 API 密钥。始终让用户设置它。

### 3. 授权托管的 MCP 服务器（仅限 Claude Code 插件）

插件捆绑了托管的 MCP 服务器 `https://mcp.videodb.io/mcp`，其授权与上述 SDK 密钥分开。告诉用户运行 `/mcp`，选择**videodb**，并使用他们的 VideoDB 账户完成浏览器授权。使用“列出我的 VideoDB 集合”进行验证。

MCP 工具无需本地 Python 安装，也无需 API 密钥。当技能使用 `npx skills add` 安装或运行在 Claude Code 之外时，跳过此步骤——在这种情况下，没有 MCP 服务器，上述 SDK 路径是唯一可用的。

## 快速参考

### 上传媒体

```python
# URL
video = coll.upload(url="https://example.com/video.mp4")

# YouTube
video = coll.upload(url="https://www.youtube.com/watch?v=VIDEO_ID")

# 本地文件
video = coll.upload(file_path="/path/to/video.mp4")
```

### 理解 → 索引 → 检索（默认路径）

三个阶段。运行分析器以生成**生成物**，索引每个生成物，然后检索。

```python
import time

# 1. 理解。为每个分析器命名，以保持 `analyzer.name` 在下游具有意义。
understanding = video.understand(
    analyzers=[
        {"type": "spoken_words", "name": "transcript"},
        {"type": "vlm", "name": "scene",
         "config": {"prompt": "描述场景以及屏幕上的任何文本."}},
    ],
    segmentation={"type": "shot", "threshold": 30},
)

# 一个包含失败或跳过分析器的运行以 `partial` 结束，SDK 不将其视为终止——等待 `wait_until_complete()` 会轮询 TimeoutError。轮询分析器。`analyzers and` 守卫是关键的：刷新可能会暂时返回空列表，而 all([]) 为 True，这会导致在运行仍在进行时退出循环。
deadline = time.time() + 3600
while time.time() < deadline:
    analyzers = understanding.refresh().list_analyzers()
    if analyzers and all(a.is_complete for a in analyzers):
        break
    time.sleep(15)

# 2. 索引每个成功的生成物。
for analyzer in understanding.list_analyzers():
    if analyzer.is_successful:
        video.index(source=analyzer, name=analyzer.name).wait_until_complete()

# 3. 检索。
response = video.search("关于价格的讨论")
for shot in response.shots:
    print(f"[{shot.start:.1f}s - {shot.end:.1f}s] {shot.text}")
if response.response_type in ("shots", "deepsearch") and len(response):
    stream_url = response.compile()   # 否则引发 SearchError
```

分析器类型：`spoken_words`（→ 生成物 `transcript`）、`vlm`（→ `scene`）、`object_detection`（→ `objects`）、`ocr`、`brand_detection`（→ `brands`）、`activity_recognition`（→ `activity`）、`location_detection`（→ `location`）、`faces`、`audio_event_detection`。它们是普通字符串——没有 SDK 枚举。

有关分段、采样、字段配置和成本调整，请参阅 [reference/indexing.md](reference/indexing.md)。

### 检索

`search(query)` 是默认的——它规划检索并自行选择索引。当你需要特定内容时，可以超越它：

```python
# 针对特定索引，并设置相关性下限
video.semantic_search("一个客户拿着产品", index_names=["scene"], score_threshold=0.7)

# 精确过滤，无自然语言解释
video.query(index_name="objects",
            filter=[{"field": "frames.detections.label", "op": "contains", "value": "car"}])

# 计数和维度——返回原始服务器有效负载，而不是 SearchResult
video.aggregate(index_name="objects", group_by="frames.detections.label", metric="count")

# 书面答案以及它来自的时刻
answer = video.ask("他们说了什么关于价格？", include_sources=True)
```

所有五个都在 `Collection` 上，跨越每个索引的视频。请参阅 [reference/search.md](reference/search.md)。

**`search()` 现在返回 `SearchResponse`，而不是 `SearchResult`。** `get_shots()`、`compile()`、`play()` 和迭代都有效，但没有 `.stream_url`——使用 `.compile()`。

### 字幕 + 字幕

```python
# force=True 跳过错误，如果视频已经索引
video.index_spoken_words(force=True)
text = video.get_transcript_text()
stream_url = video.add_subtitle()
```

`index_spoken_words()` 即使在 0.5.0 上也是正确的调用——`add_subtitle()` 和 `CaptionAsset(src="auto")` 读取 v1 语音词索引。v2 `spoken_words` 生成物不能替代它。这是 v1 索引仍然是正确答案的唯一地方。

### 遗留索引（现有代码库）

```python
# v1 API — 在 0.5.0 中仍然支持，未弃用。新代码应使用上面的 v2 路径。
from videodb import IndexType

video.index_spoken_words(force=True)
scene_index_id = video.index_scenes(prompt="描述视觉内容。")
results = video.legacy_search(
    "一个人在白板上写字",
    index_type=IndexType.scene,
    scene_index_id=scene_index_id,
)
```

在现有存储库中识别此模式并保持原样，除非要求迁移——它仍然有效。请参阅 [reference/migration.md](reference/migration.md) 以将其移植，或 [reference/legacy/search.md](reference/legacy/search.md) 以维护它。

### 时间线编辑

使用编辑器 API 组合视频、图像、音频和文本。请参阅 [reference/editor.md](reference/editor.md) 了解完整工作流程。

```python
from videodb.editor import Timeline, Track, Clip, VideoAsset, ImageAsset, AudioAsset, Fit

timeline = Timeline(conn)
timeline.resolution = "1280x720"

video_track = Track()
video_track.add_clip(0, Clip(asset=VideoAsset(id=video.id, start=10), duration=20))

audio_track = Track()
audio_track.add_clip(0, Clip(asset=AudioAsset(id=music.id, volume=0.2), duration=20))

timeline.add_track(video_track)
timeline.add_track(audio_track)
stream_url = timeline.generate_stream()
```

### 转码视频（分辨率/质量更改）

```python
from videodb import TranscodeMode, VideoConfig, AudioConfig

# 在服务器端更改分辨率、质量或宽高比
job_id = conn.transcode(
    source="https://example.com/video.mp4",
    callback_url="https://example.com/webhook",
    mode=TranscodeMode.economy,
    video_config=VideoConfig(resolution=720, quality=23, aspect_ratio="16:9"),
    audio_config=AudioConfig(mute=False),
)
```

### 调整宽高比（用于社交平台）

**警告**：`reframe()` 是一个慢速的-server 端操作。对于长视频，它可能需要几分钟，并且可能会超时。最佳实践：
- 尽可能使用 `start`/`end` 限制到短片段
- 对于全长视频，使用 `callback_url` 进行异步处理
- 首先在 `Timeline` 上修剪视频，然后重新调整较短结果

```python
from videodb import ReframeMode

# 总是优先重新调整短片段：
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)

# 全长视频的异步重新调整（返回 None，结果通过 webhook 返回）：
video.reframe(target="vertical", callback_url="https://example.com/webhook")

# 预设："vertical" (9:16)、"square" (1:1)、"landscape" (16:9)
reframed = video.reframe(start=0, end=60, target="square")

# 自定义尺寸
reframed = video.reframe(start=0, end=60, target={"width": 1280, "height": 720})
```

### 生成式媒体

```python
image = coll.generate_image(
    prompt="山脉日落",
    aspect_ratio="16:9",
)
```

### 沙盒计算（自托管/开放权重模型）

通过创建沙盒并将 `sandbox_id` 传递给支持的工作来运行开放权重模型（Gemma、Qwen、Whisper、OmniVoice、FLUX、RT-DETR）。需要 `videodb>=0.5.1`。

```python
from videodb import SandboxTier, SandboxModel

# 1. 创建一个适合最大模型的沙盒，然后等待其激活。
sandbox = conn.create_sandbox(
    tier=SandboxTier.medium,
    models=[SandboxModel.GEMMA_4_31B.value],   # 精确 ID，无 -FP8 后缀
)
sandbox.wait_for_ready(timeout=300, interval=5)

# 2. 理解：在分析器上设置 `config.model + config.sandbox_id`。
understanding = video.understand(analyzers=[{
    "type": "vlm", "name": "scene",
    "config": {"model": "google/gemma-4-31B-it", "sandbox_id": sandbox.id,
               "prompt": "描述场景。"},
}])

# 2b. 生成：传递 `model_name + sandbox_id`（工作返回 GenerationJob → .wait()）。
response = coll.generate_text(prompt="总结一下。", model_name="Qwen/Qwen3.5-9B",
                             sandbox_id=sandbox.id, max_tokens=300)
job = coll.generate_image(prompt="日落时的城市", model_name="black-forest-labs/FLUX.1-dev",
                          sandbox_id=sandbox.id)
image = job.wait(timeout=900, interval=5)

# 3. 完成时停止——预配/激活/警报都计入层级限制。
sandbox.stop(); sandbox.wait_for_stop()
```

模型 ID 必须与目录完全匹配（**无 `-FP8` 后缀**），否则 `create_sandbox` 会引发 `Unsupported sandbox model`。有关完整模型目录、层级、类别、定价和陷阱，请参阅 [reference/sandbox.md](reference/sandbox.md)。

## 错误处理

```python
from videodb.exceptions import AuthenticationError, InvalidRequestError

try:
    conn = videodb.connect()
except AuthenticationError:
    print("检查你的 VIDEO_DB_API_KEY")

try:
    video = coll.upload(url="https://example.com/video.mp4")
except InvalidRequestError as e:
    print(f"上传失败：{e}")
```

### 常见陷阱

| 情景 | 错误消息 | 解决方案 |
|------|----------|----------|
| 搜索结果没有流 URL | `AttributeError: 'SearchResponse' object has no attribute 'stream_url'` | 0.5.0 中 `search()` 返回 `SearchResponse`。使用 `results.compile()` |
| `search(score_threshold=)` 搜索了错误的索引 | 无错误，结果意外 | `score_threshold` 没有路由到遗留。使用 `semantic_search(score_threshold=)`，或 `legacy_search()` 用于 v1 索引 |
| 对象检测上的语义索引 | `use_for includes semantic but no scene has embeddable text` | 对象生成物没有顶层文本。省略 `use_for`（它会自动降级），或传递 `["query", "aggregate"]` |
| 索引一个不存在的字段 | `fields.filter names not present in any scene's data` | 错误列出了可用的字段名——读取它。或者检查 `index.field_schema` |
| 搜索未找到匹配项 | v2 返回空的 `SearchResponse`；只有 `legacy_search()` 引发 `InvalidRequestError: No results found` | 检查 `len(response)`。仅将遗留调用包装在 try/except 中 |
| 索引一个已索引的视频（v1） | `Spoken word index for video already exists` | 使用 `video.index_spoken_words(force=True)` 跳过如果已索引 |
| 调整超时 | 在长视频上无限期阻塞 | 使用 `start`/`end` 限制片段，或传递 `callback_url` 进行异步处理 |
| 时间线上的负时间戳 | 静默生成损坏的流 | 始终在创建 `VideoAsset` 之前验证 `start >= 0` |
| `generate_video()` / `create_collection()` 失败 | `Operation not allowed` 或 `maximum limit` | 计划限制功能——告知用户关于计划限制 |

## 其他文档

参考文档位于 `${CLAUDE_SKILL_DIR}/reference/`。使用前缀读取那里的文件；下面的链接相对于此 SKILL.md。

- [reference/api-reference.md](reference/api-reference.md) - 完整 VideoDB Python SDK API 参考
- [reference/indexing.md](reference/indexing.md) - 理解 → 索引管道：分析器、生成物、分段、字段配置
- [reference/indexing-reference.md](reference/indexing-reference.md) - 分析器目录和 Understanding/Index 类参考
- [reference/search.md](reference/search.md) - 检索指南：search、ask、semantic_search、query、aggregate
- [reference/search-reference.md](reference/search-reference.md) - 检索签名、过滤语法、响应对象
- [reference/migration.md](reference/migration.md) - v1 → v2 映射和 SDK 0.5.0 的破坏性更改。当你找到 v1 代码时阅读
- [reference/editor.md](reference/editor.md) - 时间线编辑工作流程指南（4 层模型、用例、示例）
- [reference/editor-reference.md](reference/editor-reference.md) - 编辑器代码参考（构造函数、参数、枚举）
- [reference/streaming.md](reference/streaming.md) - HLS 流式传输和即时播放
- [reference/generative.md](reference/generative.md) - AI 驱动的媒体生成（图像、视频、音频）
- [reference/sandbox.md](reference/sandbox.md) - 沙盒计算工作流程（运行开放权重模型：Gemma、Qwen、Whisper、OmniVoice、FLUX、RT-DETR）
- [reference/sandbox-reference.md](reference/sandbox-reference.md) - 沙盒代码参考（创建/获取/列出/停止、层级、模型目录、沙盒感知生成）
- [reference/rtstream.md](reference/rtstream.md) - 直播流摄取工作流程（RTSP/RTMP）
- [reference/rtstream-reference.md](reference/rtstream-reference.md) - RTStream SDK 方法和 AI 管道
- [reference/capture.md](reference/capture.md) - 桌面捕获工作流程
- [reference/capture-reference.md](reference/capture-reference.md) - 捕获 SDK 和 WebSocket 事件
- [reference/use-cases.md](reference/use-cases.md) - 常见的视频处理模式和示例

遗留 v1 索引和搜索。这些 API 仍然有效且未被弃用，但仅在维护现有 v1 代码时才阅读：

- [reference/legacy/index.md](reference/legacy/index.md) - v1 场景索引和帧提取工作流程
- [reference/legacy/index-reference.md](reference/legacy/index-reference.md) - v1 场景索引代码参考（SceneCollection/Scene/Frame）
- [reference/legacy/search.md](reference/legacy/search.md) - v1 语音词和场景搜索

## 屏幕录制（桌面捕获）

使用 `ws_listener.py` 在录制会话期间捕获 WebSocket 事件。桌面捕获仅支持 **macOS**。

`${CLAUDE_SKILL_DIR}` 是此技能的安装目录，由 Claude Code 设置。在未设置它的代理上，用包含此 SKILL.md 的目录替换它。

### 快速入门

1. **启动监听器**：`python "${CLAUDE_SKILL_DIR}/scripts/ws_listener.py" --cwd=<PROJECT_ROOT> &`
2. **获取 WebSocket ID**：`cat /tmp/videodb_ws_id`
3. **运行捕获代码**（有关完整工作流程，请参阅 reference/capture.md）
4. **事件写入**：`/tmp/videodb_events.jsonl`

### 查询事件

```python
import json
events = [json.loads(l) for l in open("/tmp/videodb_events.jsonl")]

# 获取所有字幕
transcripts = [e["data"]["text"] for e in events if e.get("channel") == "transcript"]

# 获取最近 5 分钟的视觉描述
import time
cutoff = time.time() - 300
recent_visual = [e for e in events 
                 if e.get("channel") == "visual_index" and e["unix_ts"] > cutoff]
```

### 实用脚本

- `${CLAUDE_SKILL_DIR}/scripts/ws_listener.py` - WebSocket 事件监听器（输出为 JSONL）

有关完整捕获工作流程，请参阅 [reference/capture.md](reference/capture.md).


**当 VideoDB 支持操作时，不要使用 ffmpeg、moviepy 或本地编码工具**。以下所有操作都由 VideoDB 在服务器端处理——修剪、组合片段、覆盖音频或音乐、添加字幕、文本/图像覆盖层、转码、分辨率更改、宽高比转换、为平台要求调整大小、转录、音量控制、淡入淡出过渡和媒体生成。仅在 reference/editor.md 中列出的操作下回退到本地工具（速度变化、裁剪/缩放、色彩校正、关键帧动画）。

### 何时使用什么

| 问题 | VideoDB 解决方案 |
|------|-----------------|
| 使视频可搜索 | `video.understand(analyzers=[...])` 然后 `video.index(source=analyzer)` |
| 通过所说或所见查找时刻 | `video.search(query)`，或 `semantic_search(index_names=[...])` 以针对索引进行操作 |
| 回答有关视频的问题 | `video.ask(question, include_sources=True)` |
| 计数或分组视频中出现的对象 | `video.aggregate(index_name=..., group_by=..., metric="count")` |
| 根据确切字段值过滤时刻 | `video.query(index_name=..., filter={...})` |
| 平台拒绝视频宽高比或分辨率 | `video.reframe()` 或 `conn.transcode()` 使用 `VideoConfig` |
| 需要调整视频宽高比或分辨率以适应 Twitter/Instagram/TikTok | `video.reframe(target="vertical")` 或 `target="square"` |
| 需要更改分辨率（例如 1080p → 720p） | `conn.transcode()` 使用 `VideoConfig(resolution=720)` |
| 需要在视频中覆盖音频/音乐 | `AudioAsset` 在编辑器 `Timeline` 上，并控制音量 |
| 需要添加字幕 | `video.add_subtitle()` 或 `CaptionAsset` 在编辑器 `Timeline` 上 |
| 需要组合/修剪片段 | `VideoAsset` 在编辑器 `Timeline` 上 |
| 需要组合图像并添加旁白 | `ImageAsset` + `AudioAsset` 在单独的编辑器轨道上 |
| 需要生成旁白、音乐或音效 | `coll.generate_voice()`, `generate_music()`, `generate_sound_effect()` |
