# Seedance 2.0 故事板与视频生成

从概念到最终视频的端到端工作流程：故事板 → 参考图片 → 提交视频任务 → 获取结果。

## 第 0 步：确定执行模式（MCP 或脚本）

**首先检查 MCP 是否可用：**

- 检查 `xskill-ai` MCP 服务状态（读取 `mcps/user-xskill-ai/STATUS.md`）
- 如果 MCP 可用 → 使用 `submit_task` / `get_task` 和其他 MCP 工具
- 如果 MCP 不可用或返回错误 → 切换到脚本模式

**脚本模式前提条件：**

- 验证 `XSKILL_API_KEY` 环境变量是否已设置（运行 `echo $XSKILL_API_KEY | head -c 10`）
- 如果未设置，提示用户：
  ```
  export XSKILL_API_KEY=sk-your-api-key
  ```
  获取您的 API Key：https://www.xskill.ai/#/v2/api-keys
- 验证 `requests` 是否已安装 (`pip install requests`)

**脚本路径：** 位于此技能目录下的 `scripts/seedance_api.py`：

```
# 通过 Glob 工具查找
glob: .cursor/skills/seedance2-api/scripts/seedance_api.py
```

在以下步骤中，每个 API 调用都提供 MCP 方法和脚本方法。根据第 0 步的结果选择其中一种。

## 第 1 步：理解用户的想法

收集以下信息（如果缺少任何内容，请主动询问）：

- **故事概念**：视频的简短一句话总结
- **时长**：4–15 秒
- **宽高比**：16:9 / 9:16 / 1:1 / 21:9 / 4:3 / 3:4
- **视觉风格**：写实 / 动画 / 墨水 / 科幻 / 赛博朋克等
- **素材**：现有图片/视频/音频，或需要 AI 生成
- **功能模式**：首尾帧控制 (`first_last_frames`) 或默认全息模式 (`omni_reference`)

## 第 2 步：深入探索（五个维度）

引导用户逐个维度进行更丰富的细节：

- **内容** – 谁是主体？他们在做什么？在哪里？
- **视觉效果** – 光照、调色板、纹理、氛围
- **摄像机** – 推入 / 拉出 / 摇移 / 倾斜 / 跟踪 / 轨道 / 俯仰
- **动作** – 主体动作和节奏
- **音频** – 音乐风格、音效、对话

## 第 3 步：构建故事板结构

使用此公式沿时间轴分解镜头：

```
[风格] _____ 风格，_____ 秒，_____ 宽高比，_____ 氛围

0-Xs: [摄像机运动] + [视觉内容] + [动作描述]
X-Ys: [摄像机运动] + [视觉内容] + [动作描述]
...

[音频] _____ 音乐 + _____ SFX + _____ 对话
[参考] @image_file_1 _____, @video_file_1 _____
```

有关详细模板和示例，请参阅 `reference.md`。

## 第 4 步：生成参考图片（如果需要）

如果用户没有现有素材，使用 Seedream 4.5 生成角色艺术、场景、首尾帧等。

### 文本到图片

调用 `submit_task` 工具：

- `model_id`: `fal-ai/bytedance/seedream/v4.5/text-to-image`
- `参数`:
  - `prompt`: 详细图片描述（英文效果最佳）
  - `image_size`: 根据视频宽高比选择
  - `num_images`: 需要的数量（1–6）

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "fal-ai/bytedance/seedream/v4.5/text-to-image" \
  --params '{"prompt":"An astronaut in a white spacesuit...","image_size":"landscape_16_9","num_images":1}'
```

### 图片编辑（修改现有图片）

调用 `submit_task` 工具：

- `model_id`: `fal-ai/bytedance/seedream/v4.5/edit`
- `参数`:
  - `prompt`: 编辑指令（使用 Figure 1/2/3 引用图片）
  - `image_urls`: 输入图片 URL 数组
  - `image_size`: 输出大小

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "fal-ai/bytedance/seedream/v4.5/edit" \
  --params '{"prompt":"Change the background to a forest","image_urls":["https://..."],"image_size":"landscape_16_9"}'
```

### 查询图片结果

图片通常在 1–2 分钟内完成。

调用 `get_task` 工具检查状态：

- 首次查询在 30 秒后
- 然后每 30 秒查询一次
- 状态为 `completed` 时提取图片 URL

单次查询：

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py query \
  --task-id "TASK_ID_HERE"
```

自动轮询（推荐用于图片，间隔 10 秒，超时 180 秒）：

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py poll \
  --task-id "TASK_ID_HERE" --interval 10 --timeout 180
```

### `image_size` 参考

| 宽高比 | 推荐的 `image_size` | 备注 |
|---|---|---|
| 16:9 | `landscape_16_9` | 横屏 |
| 9:16 | `portrait_16_9` | 竖屏 |
| 4:3 | `landscape_4_3` | 横屏 |
| 3:4 | `portrait_4_3` | 竖屏 |
| 1:1 | `square_hd` | 正方形 |
| 21:9 | `landscape_16_9` | 近似超宽屏 |

## 第 5 步：组合最终提示

将故事板结构和参考图片合并到最终提示中：

- 使用 `@image_file_1`、`@image_file_2` 等引用 `image_files` 数组中的图片
- 使用 `@video_file_1` 等引用 `video_files` 数组中的视频
- 使用 `@audio_file_1` 等引用 `audio_files` 数组中的音频

参考语法示例：

```
@image_file_1 作为角色参考，跟随 @video_file_1 摄像机运动，使用 @audio_file_1 作为背景音乐
```

**重要提示：** `image_files` 中的第 N 个 URL 映射到 `@image_file_N`。`video_files` 和 `audio_files` 独立编号。

## 第 6 步：提交视频任务

**处理素材 URL：**

- Seedream 生成的图片：URL 已可用，直接使用
- 用户提供的网络图片：直接使用
- 用户提供的本地图片：先上传获取 URL（见下文上传方法）

### 上传本地图片

调用 `upload_image` 工具：`image_url` 或 `image_data`

```bash
# 从 URL 上传
python .cursor/skills/seedance2-api/scripts/seedance_api.py upload \
  --image-url "https://example.com/image.png"

# 上传本地文件
python .cursor/skills/seedance2-api/scripts/seedance_api.py upload \
  --image-path "/path/to/local/image.png"
```

### 提交 Seedance 2.0 任务（全息参考模式）

调用 `submit_task` 工具：

- `model_id`: `st-ai/super-seed2`
- `参数`:
  - `prompt`: 第 5 步的完整提示
  - `functionMode`: `omni_reference`（默认，可省略）
  - `image_files`: 参考图片 URL 数组（最多 9 个，顺序匹配 `@image_file_1/2/3...`）
  - `video_files`: 参考视频 URL 数组（最多 3 个，总时长 ≤ 15 秒）
  - `audio_files`: 参考音频 URL 数组（最多 3 个）
  - `ratio`: 宽高比 (`16:9` / `9:16` / `1:1` / `21:9` / `4:3` / `3:4`)
  - `duration`: 整数长度（4–15）
  - `model`: `seedance_2.0_fast`（默认，更快）或 `seedance_2.0`（标准质量）

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "st-ai/super-seed2" \
  --params '{
    "prompt": "Cinematic realistic sci-fi style, 15 seconds, 16:9...",
    "functionMode": "omni_reference",
    "image_files": ["https://img1.png", "https://img2.png"],
    "ratio": "16:9",
    "duration": 15,
    "model": "seedance_2.0_fast"
  }'
```

### 提交 Seedance 2.0 任务（首尾帧模式）

调用 `submit_task` 工具：

- `model_id`: `st-ai/super-seed2`
- `参数`:
  - `prompt`: 视频描述提示
  - `functionMode`: `first_last_frames`
  - `filePaths`: 图片 URL 数组（0 = 文本到视频，1 = 首帧，2 = 首尾帧）
  - `ratio`: 宽高比
  - `duration`: 整数长度
  - `model`: `seedance_2.0_fast` 或 `seedance_2.0`

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py submit \
  --model "st-ai/super-seed2" \
  --params '{
    "prompt": "Camera smoothly transitions from first frame to last frame, fluid motion",
    "functionMode": "first_last_frames",
    "filePaths": ["https://first-frame.png", "https://last-frame.png"],
    "ratio": "16:9",
    "duration": 5,
    "model": "seedance_2.0_fast"
  }'
```

## 第 7 步：轮询视频结果

视频生成大约需要 10 分钟。

**轮询策略：**

- 提交后，告知用户："视频正在生成，预计 ~10 分钟"
- 首次查询在 60 秒后通过 `get_task`
- 然后每 90 秒查询一次
- 每次查询后向用户报告状态

推荐：自动轮询（前台运行，间隔 30 秒，超时 600 秒）：

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py poll \
  --task-id "TASK_ID_HERE" --interval 30 --timeout 600
```

进度打印到 stderr；完成时最终 JSON 结果打印到 stdout。

手动单次查询：

```bash
python .cursor/skills/seedance2-api/scripts/seedance_api.py query \
  --task-id "TASK_ID_HERE"
```

**状态参考：**

- `pending` → "排队中..."
- `processing` → "生成中..."
- `completed` → 提取视频 URL 并呈现给用户
- `failed` → 报告错误；建议调整提示并重试

## 完整工作流程示例

用户说：*"制作一个宇航员在火星上行走视频"*

### 当 MCP 可用时

```
1. 收集信息 → 15s, 16:9, 电影级科幻风格, 无现有素材

2. 使用 Seedream 4.5 生成宇航员 + 火星场景图片
   submit_task("fal-ai/bytedance/seedream/v4.5/text-to-image", {...})
   → poll get_task → 获取图片 URL

3. 组合提示 → 提交视频任务
   submit_task("st-ai/super-seed2", {...})

4. 轮询 get_task, ~10 分钟后 → 获取视频 URL
```

### 当 MCP 不可用（脚本模式）

```
1. 收集信息 → 15s, 16:9, 电影级科幻风格

2. 生成参考图片:
   python scripts/seedance_api.py submit \
     --model "fal-ai/bytedance/seedream/v4.5/text-to-image" \
     --params '{"prompt":"An astronaut in white spacesuit on Mars...","image_size":"landscape_16_9"}'
   → 获取 task_id

3. 轮询图片结果:
   python scripts/seedance_api.py poll --task-id "xxx" --interval 10 --timeout 180
   → 获取图片 URL

4. 提交视频任务:
   python scripts/seedance_api.py submit \
     --model "st-ai/super-seed2" \
     --params '{"prompt":"...故事板提示...","functionMode":"omni_reference","image_files":["IMAGE_URL"],"ratio":"16:9","duration":15,"model":"seedance_2.0_fast"}'
   → 获取 task_id

5. 轮询视频结果:
   python scripts/seedance_api.py poll --task-id "xxx" --interval 30 --timeout 600
   → 获取视频 URL
```

## 模型参数快速参考

### Seedream 4.5 文本到图片

| 参数 | 类型 | 必填 | 描述 |
|---|---|---|---|
| `prompt` | string | 是 | 图片描述 |
| `image_size` | string | 否 | `auto_2K` / `auto_4K` / `square_hd` / `portrait_4_3` / `portrait_16_9` / `landscape_4_3` / `landscape_16_9` |
| `num_images` | int | 否 | 1–6, 默认 1 |

### Seedream 4.5 图片编辑

| 参数 | 类型 | 必填 | 描述 |
|---|---|---|---|
| `prompt` | string | 是 | 编辑指令，使用 Figure 1/2/3 引用图片 |
| `image_urls` | array | 是 | 输入图片 URL 列表 |
| `image_size` | string | 否 | 与上述相同 |
| `num_images` | int | 否 | 1–6, 默认 1 |

### Seedance 2.0 视频（全息参考模式）

| 参数 | 类型 | 必填 | 描述 |
|---|---|---|---|
| `prompt` | string | 是 | 故事板提示，使用 `@image_file_N` / `@video_file_N` / `@audio_file_N` |
| `functionMode` | string | 否 | `omni_reference`（默认） |
| `image_files` | array | 否 | 参考图片 URL 数组（最多 9 个） |
| `video_files` | array | 否 | 参考视频 URL 数组（最多 3 个，总时长 ≤ 15 秒） |
| `audio_files` | array | 否 | 参考音频 URL 数组（最多 3 个） |
| `ratio` | string | 否 | `21:9` / `16:9` / `4:3` / `1:1` / `3:4` / `9:16` |
| `duration` | integer | 否 | 4–15, 默认 5 |
| `model` | string | 否 | `seedance_2.0_fast`（默认） / `seedance_2.0` |

### Seedance 2.0 视频（首尾帧模式）

| 参数 | 类型 | 必填 | 描述 |
|---|---|---|---|
| `prompt` | string | 是 | 视频描述提示 |
| `functionMode` | string | 是 | `first_last_frames` |
| `filePaths` | array | 否 | 图片 URL 数组（0 = 文本到视频，1 = 首帧，2 = 首尾帧） |
| `ratio` | string | 否 | `21:9` / `16:9` / `4:3` / `1:1` / `3:4` / `9:16` |
| `duration` | integer | 否 | 4–15, 默认 5 |
| `model` | string | 否 | `seedance_2.0_fast`（默认） / `seedance_2.0` |

## 工具快速参考

### MCP 工具

| 操作 | 工具 | 关键参数 |
|---|---|---|
| 提交任务 | `submit_task` | `model_id`, `parameters` |
| 查询结果 | `get_task` | `task_id` |
| 上传图片 | `upload_image` | `image_url` 或 `image_data` |
| 查询余额 | `get_balance` | (无) |

### 脚本命令（当 MCP 不可用时）

| 操作 | 命令 | 描述 |
|---|---|---|
| 提交任务 | `python scripts/seedance_api.py submit --model MODEL --params '{...}'` | 返回 `task_id` |
| 单次查询 | `python scripts/seedance_api.py query --task-id ID` | 返回当前状态 |
| 自动轮询 | `python scripts/seedance_api.py poll --task-id ID --interval N --timeout N` | 阻塞直到完成 |
| 查询余额 | `python scripts/seedance_api.py balance` | 返回账户余额 |
| 上传图片 | `python scripts/seedance_api.py upload --image-url URL or --image-path PATH` | 返回图片 URL |

**脚本路径说明：** 上述 `scripts/seedance_api.py` 路径相对于 `.cursor/skills/seedance2-api/`。执行时使用完整路径 `.cursor/skills/seedance2-api/scripts/seedance_api.py`，或先 `cd` 进入技能目录。

## Seedance 2.0 限制

- 不支持上传写实人脸
- 最大 12 个文件：图片 ≤ 9 + 视频 ≤ 3 + 音频 ≤ 3
- 视频音频参考总时长 ≤ 15 秒
- 视频参考消耗更多积分

## 更多资源

有关详细故事板模板、完整示例和摄像机运动术语表，请参阅 `reference.md`。
