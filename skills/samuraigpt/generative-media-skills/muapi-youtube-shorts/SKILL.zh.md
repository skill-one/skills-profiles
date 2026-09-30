---
name: muapi-youtube-shorts
description: 自动从长视频生成病毒式传播的 9:16 YouTube Shorts（或 TikTok/Reels 短片）。这是一个围绕 AI 剪辑技能的轻量级平台感知包装器——为短视频社交平台（9:16 比例，30-60 秒黄金时长）选择合理的默认设置，并将实际的高亮提取和裁剪工作委托给 muapi.ai 的 `/ai-clipping` 端点。
---

# YouTube Shorts 生成器

**长视频 → 排名竖屏短片，针对短形式社交进行优化。**

这项技能是 [AI 剪辑](../../edit/ai-clipping/) 基础原语的平台感知预设。它会为目标平台选择正确的宽高比和剪辑数量，并将高亮提取、去重和面部跟踪自动裁剪委托给 muapi.ai 的 `/ai-clipping` 管理端点。

参考实现：https://github.com/SamurAIGPT/AI-Youtube-Shorts-Generator
底层 API：https://muapi.ai/playground/ai-clipping

---

## 何时使用此功能与 AI 剪辑

| 使用此技能时… | 直接使用 [AI 剪辑](../../edit/ai-clipping/) 时… |
|:---|:---|
| 目标是 YouTube Shorts / TikTok / Reels | 你想完全控制宽高比 / 数量 |
| 你想要平台优化的默认值 | 你想要原始时间戳 (`--coords-only`) |
| 你宁愿传递 `--platform tiktok` 而不是思考宽高比 | 你正在集成到自定义渲染器 |

---

## 代理执行协议

### 第 1 步 — 收集输入

| 输入 | 默认值 | 备注 |
|:---|:---|:---|
| `--source` | — | YouTube URL、托管 mp4 URL 或本地文件 |
| `--platform` | `shorts` | `shorts` \| `tiktok` \| `reels` \| `feed` (设置宽高比 + 默认数量) |
| `--num-clips` | 平台默认值 | 覆盖剪辑数量 |
| `--aspect-ratio` | 平台默认值 | 覆盖宽高比 |

如果用户只提供了一个 URL，则使用平台默认值运行——不要阻塞。

---

### 第 2 步 — 验证前提条件

- `muapi-cli` 安装并认证 (`muapi auth configure`)
- `MUAPI_API_KEY` 可用

就这样。转录、高亮排名、去重和裁剪都在服务器端运行——不需要 `ffmpeg`、不需要 Python、不需要 Whisper、不需要本地 LLM 密钥。

---

### 第 3 步 — 运行管道

```bash
bash library/social/youtube-shorts/scripts/run-youtube-shorts.sh \
  --source "<YOUTUBE_URL>" \
  --platform shorts \
  --num-clips 5 \
  --view
```

该脚本：
1. 解析源（如果需要，将本地文件上传到 muapi CDN）。
2. 如果未传递 `--aspect-ratio` / `--num-clips`，则选择平台默认值。
3. 调用 `muapi edit clipping`（即 `/ai-clipping` 端点）并使用所选参数。
4. 循环查询直到完成，打印排名摘要，可选下载 / 打开剪辑。

---

## 服务器端发生的情况

`/ai-clipping` 端点运行完整管道：

- **转录**音频。
- 通过病毒性框架**排名高亮**——钩子时刻、情感高峰、观点炸弹、揭示时刻、冲突、可引用的台词、故事高峰、实用价值。
- **去重**通过分数重叠候选者。
- **选择 Top-N** 并 **面部跟踪**竖向裁剪。

每个剪辑都附带分数（0–100）、开篇钩子句和一句“为什么有效”的理由。

---

## 平台默认值

| 平台 | 标志 | 宽高比 | 默认剪辑 | 备注 |
|:---|:---|:---|:---|:---|
| YouTube Shorts | `--platform shorts` | `9:16` | 3 | 在前 1 秒内钩子 |
| TikTok | `--platform tiktok` | `9:16` | 5 | 更高能量，时间可以稍长 |
| Instagram Reels | `--platform reels` | `9:16` | 3 | 在前 1 秒内钩子 |
| Instagram Feed | `--platform feed` | `1:1` | 3 | 静态感效果很好 |

使用 `--aspect-ratio` / `--num-clips` 覆盖任何默认值。

---

## 快速调用模式

**单个视频，默认值：**
```bash
bash run-youtube-shorts.sh --source "https://youtube.com/watch?v=VIDEO_ID"
```

**TikTok 预设——5 个剪辑，在播放器中查看：**
```bash
bash run-youtube-shorts.sh --source "<URL>" --platform tiktok --view
```

**方形 Instagram feed 剪辑：**
```bash
bash run-youtube-shorts.sh --source "<URL>" --platform feed --num-clips 3
```

**批量——`urls.txt` 每行一个 URL：**
```bash
xargs -a urls.txt -I{} bash run-youtube-shorts.sh --source "{}"
```

**异步提交（返回 request_id，稍后查询）：**
```bash
REQUEST_ID=$(bash run-youtube-shorts.sh --source "<URL>" --async --output-json - | jq -r '.request_id')
muapi predict wait "$REQUEST_ID" --download ./outputs
```

---

## 输出模式

```json
{
  "source_video_url": "...",
  "shorts": [
    {
      "title": "The one mistake that cost me $50K",
      "start_time": 124.3,
      "end_time": 187.6,
      "score": 92,
      "hook_sentence": "Nobody talks about this, but it killed my first startup...",
      "virality_reason": "Opens with a number + regret, peaks on a contrarian lesson",
      "clip_url": "https://.../short_1.mp4"
    }
  ]
}
```

报告时，为每个剪辑展示：排名、分数、时间范围、标题、钩子、剪辑 URL。

---

## 常见错误避免

1. **平台宽高比错误**——Shorts / TikTok / Reels 是 `9:16`。平台预设会处理这个问题；除非你知道原因，否则不要覆盖。
2. **填充以匹配 `--num-clips`**——如果 API 返回的幸存者较少，则返回你拥有的。不要发送低分数的填充。
3. **在 404 的剪辑 URL 上重新运行**——使用 `muapi predict wait <id>` 重新获取相同的 `request_id`，而不是重新剪辑。

---

## 失败模式

- **API 密钥丢失或被拒绝**——显示错误；不要编造密钥。
- **作业超时**——增加 `--poll-timeout` 并重试。
- **源 URL 不可达**——通过 `muapi upload file` 上传文件，并传递返回的 URL。
- **返回的剪辑数量少于请求**——源中可排名的高亮较少。返回返回的内容并附带说明。

---

## 完成标准

当以下条件满足时，技能完成：
1. `result.shorts` 包含最多 `num_clips` 条目，每个条目都有一个可用的 `clip_url`。
2. 用户已看到排名列表（分数、时间范围、标题、钩子、URL）。
3. 如果设置了 `--output-json`，则文件存在并可解析。
