# AI 剪辑

**一个 API 调用：长视频输入 → 排序的竖屏短视频输出。**

每个剪辑片段都附带一个病毒评分（0-100）、一个开场钩子句、一个“为什么有效”的简短理由，以及一个托管的 mp4 URL。

底层 API：https://muapi.ai/playground/ai-clipping
参考实现（开源）：https://github.com/SamurAIGPT/AI-Youtube-Shorts-Generator

---

## 使用场景

- 自动剪辑播客、访谈、讲座、博客或直播到 TikTok / Reels / Shorts。
- 从任何托管视频 URL 中提取最佳的 30-75 秒时刻。
- 获取人脸跟踪的竖屏（9:16）、方形（1:1）或肖像（4:5）裁剪，无需在本地运行 ffmpeg。

如果你只需要原始时间戳用于自己的渲染器，设置 `--coords-only` 以跳过裁剪，只需获取高亮时间范围。

---

## 代理执行协议

### 第 1 步 — 收集输入

| 输入 | 必填 | 默认 | 备注 |
|:---|:---|:---|:---|
| `--video` | 是 | — | 托管的 mp4 URL，或本地文件路径（自动上传），或 YouTube URL（如果后端支持） |
| `--num-clips` | 否 | `3` | 提取的高亮数量 |
| `--aspect-ratio` | 否 | `9:16` | `9:16` \| `1:1` \| `4:5` |
| `--coords-only` | 否 | 关闭 | 仅返回高亮时间范围，跳过裁剪 |

如果用户只提供了一个视频 URL，使用默认值运行——不要等待提问。

---

### 第 2 步 — 验证前提条件

- `muapi-cli` 安装并认证 (`muapi auth configure`)
- `MUAPI_API_KEY` 可用（环境变量或 `muapi auth status` 通过）

就这样。不需要 `ffmpeg`、不需要 Python、不需要 Whisper 安装、不需要 LLM 密钥。所有操作都在服务器端运行。

---

### 第 3 步 — 运行技能

```bash
bash library/edit/ai-clipping/scripts/run-ai-clipping.sh \
  --video "https://example.com/podcast.mp4" \
  --num-clips 5 \
  --aspect-ratio 9:16 \
  --view
```

脚本：
1. 解析 `--video` 为托管 URL（如果需要，通过 `muapi upload file` 上传本地文件）。
2. 调用 `muapi edit clipping` 并使用支持的参数。
3. 循环查询直到任务完成（或在 `--async` 下立即返回 `request_id`）。
4. 打印排序摘要，如果 `--output-json` 设置，则写入完整结果。

---

## 服务器端发生的事情

`/ai-clipping` 端点内部运行完整的工作流程，因此代理无需执行：

- **转录** 使用 Whisper。
- **分类内容类型**（播客 / 访谈 / 教程 / 博客 / 讲座 / 独白）。
- **通过病毒性框架排序高亮**：
  - **钩子时刻** — 强有力的开场白，阻止滚动
  - **情感高峰** — 笑声、愤怒、脆弱、敬畏
  - **观点炸弹** — 挑战性、反主流、辩论诱饵观点
  - **揭示时刻** — “等等，什么？”重新框架
  - **冲突** — 不同意、紧张、指责
  - **引用佳句** — 紧凑、值得截图的措辞
  - **故事高峰** — 叙事弧的顶点
  - **实用价值** — 观众会保存的行动指南
- **按分数去重** 重叠的候选者。
- **选择 Top-N** 并 **人脸跟踪自动裁剪** 到请求的宽高比。

这就是为什么技能很小：繁重的工作在 API 上。

---

## 快速调用模式

**默认值 — 三个 9:16 剪辑：**
```bash
bash run-ai-clipping.sh --video "https://example.com/long.mp4"
```

**播客 — 更多剪辑，在播放器中查看：**
```bash
bash run-ai-clipping.sh --video "<URL>" --num-clips 8 --view
```

**方形剪辑用于 Instagram 信息流：**
```bash
bash run-ai-clipping.sh --video "<URL>" --aspect-ratio 1:1 --num-clips 3
```

**仅时间戳（自己构建渲染器）：**
```bash
bash run-ai-clipping.sh --video "<URL>" --coords-only --output-json result.json
```

**异步提交（返回 request_id，稍后查询）：**
```bash
REQUEST_ID=$(bash run-ai-clipping.sh --video "<URL>" --async --output-json - | jq -r '.request_id')
muapi predict wait "$REQUEST_ID" --download ./outputs
```

**本地文件：**
```bash
bash run-ai-clipping.sh --video ./recording.mp4 --num-clips 5 --view
```

**批量 — `urls.txt` 每行一个 URL：**
```bash
xargs -a urls.txt -I{} bash run-ai-clipping.sh --video "{}"
```

---

## 宽高比选择器

| 平台 | 比例 | 最佳时长 |
|:---|:---|:---|
| TikTok / Reels / YouTube Shorts | `9:16` | 30-75 秒 |
| Instagram 信息流 | `1:1` | 15-45 秒 |
| Pinterest / 肖像 | `4:5` | 30-60 秒 |

除非指定平台，否则默认为 `9:16`。

---

## 输出模式

```json
{
  "source_video_url": "...",
  "shorts": [
    {
      "title": "我损失 5 万美元的一个错误",
      "start_time": 124.3,
      "end_time": 187.6,
      "score": 92,
      "hook_sentence": "没人谈论这个，但它毁了我的第一家创业公司...",
      "virality_reason": "以数字开头 + 后悔，在反主流教训上达到高峰",
      "clip_url": "https://.../short_1.mp4"
    }
  ]
}
```

当 `--coords-only` 设置时，每个条目有 `start_time`/`end_time` 但没有 `clip_url` — 使用 ffmpeg 本地渲染。

当向用户报告时，为每个剪辑展示：排名、分数、时间范围、标题、钩子和剪辑 URL。

---

## 常见错误避免

1. **平台宽高比错误** — Shorts / TikTok / Reels 是 `9:16`。默认使用这个。
2. **填充以匹配 `num_clips`** — 如果 API 返回的幸存者少于请求的数量，返回你拥有的。不要假装。
3. **在 404 的剪辑 URL 上重新运行** — 相同的 `request_id` 可以通过 `muapi predict wait <id>` 重新获取，而不是重新剪辑。
4. **尝试调整 Whisper / 分块大小 / LLM 提示** — 这些旋钮没有暴露；端点处理它们。

---

## 失败模式

- **API 密钥缺失或被拒绝** — 显示确切错误；永远不要编造密钥。
- **任务超时** — 增加轮询超时 (`--poll-timeout`) 并重试。
- **源 URL 从后端无法访问** — 首先使用 `muapi upload file <path>` 本地上传，然后传递返回的 URL。
- **返回的剪辑少于请求** — 源视频的高亮可排序数量较少。返回返回的内容并附上说明。

---

## 完成标准

技能完成时：
1. `result.shorts` 包含最多 `num_clips` 条目，每个条目都有一个可用的 `clip_url`（或在 `--coords-only` 下有 `start_time`/`end_time`）。
2. 向用户展示了排序列表（分数、时间范围、标题、钩子、URL）。
3. 如果 `--output-json` 设置，文件存在且可解析。
