# MiniMax 音乐歌单 — 个性化歌单生成器

扫描用户的音乐品味，建立品味档案，生成个性化歌单，并制作专辑封面。此技能设计用于代理和直接用户调用 — 根据上下文调整交互方式。

## 前置条件

- **mmx CLI** — 音乐与图像生成。安装：`npm install -g mmx-cli`。认证：`mmx auth login --api-key <key>`。
- **Python 3** — 用于扫描您即时编写的脚本（仅使用标准库，无需 pip）。
- **音频播放器** — `mpv`、`ffplay` 或 `afplay`（macOS 内置）。

## 语言

从用户消息中检测用户的语言。**所有面向用户显示的文本必须与用户的提示使用相同的语言** — 不要混合语言。如果用户使用中文，所有输出（档案摘要、主题建议、歌单计划、播放信息）必须完全使用中文。如果使用英语，所有内容都使用英语。

所有 `mmx` 生成提示应使用英语以获得最佳质量。每首歌曲的歌词语言遵循其流派（K-pop → 韩语，J-pop → 日语等），**而不是用户的 UI 语言**。

---

## 工作流程

```
1. 扫描本地音乐应用 → 2. 建立品味档案 → 3. 规划歌单
→ 4. 生成歌曲 (mmx music) → 5. 生成封面 (mmx image) → 6. 播放 → 7. 保存与反馈
```

---

## 第 1 步：收集音乐收听数据

从可用来源收集用户的收听数据。

**支持的来源：**

| 来源 | 方法 | 数据格式 |
|------|------|----------|
| Apple Music | 使用 `osascript` 查询 Music.app（官方 AppleScript 接口） | 曲目名称、艺术家、专辑、流派、播放次数 |
| Spotify | 用户通过 [Spotify 隐私设置](https://www.spotify.com/account/privacy/) 导出自己的数据 | ZIP 格式的 JSON 文件 (`Streaming_History_Audio_*.json`) |
| 手动输入 | 用户直接描述他们的品味 | 自由文本 |

**Spotify 数据导出流程：**
Spotify 本地不存储有用数据。要包含 Spotify 收听历史，首先检查用户是否已有 Spotify 数据导出：

1. 搜索现有导出：`find ~ -maxdepth 4 -name "my_spotify_data.zip" -o -name "Streaming_History_Audio_*.json" 2>/dev/null`
2. 如果找到，询问用户是否要使用它
3. 如果是 ZIP，解压并定位 `Spotify Extended Streaming History/Streaming_History_Audio_*.json`
4. 如果未找到，打开 Spotify 隐私页面：`open https://www.spotify.com/account/privacy/`
5. 告知用户登录，滚动到“下载您的数据”，并点击“请求数据”
6. 暂时跳过 Spotify，继续使用其他来源 — 告知用户数据导出到达后（通常几天）可以重新运行歌单技能

**Spotify 数据格式：**
导出包含 `Streaming_History_Audio_YYYY.json` 文件（每年一个），每个文件是收听事件的 JSON 数组。要提取的关键字段：
- `master_metadata_album_artist_name` — 艺术家名称
- `master_metadata_track_name` — 曲目名称
- `master_metadata_album_album_name` — 专辑名称
- `ms_played` — 播放时长（毫秒）（用作权重：更长 = 更强的信号）
- `ts` — 时间戳

过滤掉 `ms_played < 30000` 的条目（少于 30 秒，可能跳过）。**不要使用或存储 `ip_addr` 或其他敏感字段**。

**从每个来源提取的内容：**
- 曲目名称 + 艺术家名称（主要信号）
- 播放列表名称和成员资格（例如，名为“中国传统”的播放列表告诉您流派偏好）
- 播放次数或流媒体时长（如果可用）（提高频繁播放的曲目权重）
- 场景/心情标签（如果可用）

**方法：**
1. 检查 Apple Music 是否可用（尝试 `osascript` 查询）
2. 询问用户是否有 Spotify 数据导出 ZIP 文件要提供
3. 如果没有来源可用，请用户手动描述他们的品味

**隐私规则：** 永远不要向用户显示原始曲目列表。仅显示汇总统计数据。

---

## 第 2 步：建立品味档案

从扫描的数据中建立涵盖以下内容的品味档案：

- **流派分布** — 用户收听的风格（例如，J-pop 20%，R&B 15%，古典 10%）
- **心情倾向** — 情绪基调偏好（忧郁、活力、平静、浪漫等）
- **人声偏好** — 男声与女声比例
- **节奏偏好** — 慢 / 中速 / 活力 / 快速分布
- **语言分布** — zh、en、ja、ko 等
- **顶级艺术家** — 最常收听的艺术家

**如何从艺术家名称推断流派/心情：**
大多数原始数据只有艺术家 + 曲目名称，没有流派标签。为丰富这些数据：
1. 在 `<SKILL_DIR>/data/artist_genre_map.json` 中的本地映射表中查找艺术家
   — 该表涵盖 20,000 位流行艺术家，具有预映射的流派、人声类型和语言
2. 对于映射表中的艺术家，查询 MusicBrainz API：
   `https://musicbrainz.org/ws/2/artist/?query=artist:<name>&fmt=json`
   — 从响应中提取流派标签；尊重速率限制（每秒 1 个请求）
   — 将结果缓存到 `<SKILL_DIR>/data/artist_cache.json` 以避免重新查询
3. 如果 MusicBrainz 没有返回结果，跳过该艺术家

**档案缓存：**
- 将档案保存到 `<SKILL_DIR>/data/taste_profile.json`
- 如果存在少于 7 天的档案，则重用它（提供重新扫描选项）
- 如果较旧或缺失，则重建

**向用户显示摘要：**
```
您的音乐档案：
  来源：Apple Music 230 | Spotify 140
  流派：J-pop 20% | R&B 15% | 古典 10% | 独立流行 9%
  心情：忧郁 25% | 平静 20% | 浪漫 18%
  人声：女声 65% | 男声 35%
  顶级艺术家：王菲、久石让、泰勒·斯威夫特、周杰伦、小室哲哉
```

如果由代理提供明确参数调用，则跳过确认并继续。
如果由用户直接调用，则在继续之前询问档案是否正确。

---

## 第 3 步：规划歌单

**在生成之前，向用户询问主题/场景。** 这是工作流程中唯一交互步骤。所有其他步骤自动运行。

如果主题已在调用中提供（例如，代理或用户说“生成深夜放松歌单”），则直接使用它并跳过问题。
否则，询问：

```
您希望为歌单选择什么主题？以下是一些建议：

- “深夜放松” — 放松的慢速歌曲
- “通勤” — 活力四射
- “雨天” — 忧郁 & 舒适
- “随机” — 根据您的品味随机
- 或告诉我您自己的感觉！
```

一旦用户选择主题，自动通过生成、封面、播放和保存进行 — 无需进一步确认。
确定歌单参数：
- **主题/心情** — 来自用户输入，或默认为档案中的顶级心情
- **歌曲数量** — 来自用户输入，或默认为 5
- **流派混合** — 根据档案加权，并保持多样性

**每首歌曲的歌词语言** 遵循流派：

| 流派 | 歌词语言 |
|------|----------|
| K-pop、韩国 R&B/抒情 | 韩语 |
| J-pop、城市流行、J-rock | 日语 |
| C-pop、中国风格、华语流行 | 中文 |
| 西方流行/独立/摇滚/爵士/R&B | 英语 |
| 拉丁流行、Bossanova | 西班牙语/葡萄牙语 |
| 乐器、Lo-fi、环境音乐 | 无歌词 (`--instrumental`) |

通过人声描述自然地将语言嵌入 mmx 提示：
- 好：`"一首忧郁的中国 R&B 抒情，温柔内省的男声，电钢琴，贝斯，慢节奏"`
- 不好：`"R&B 抒情，忧郁...用中文演唱"`

**在生成之前显示歌单计划。** 显示每首歌曲两行：
第一行显示流派、心情和人声/语言标签；第二行显示歌曲的简短描述。**所有面向用户显示的文本（计划、描述、心情、标签）必须与用户的提示使用相同的语言。** 实际传递给 `mmx` 的 `--prompt` 应使用英语 — 这是内部且不应显示给用户。示例：

```
歌单计划：深夜放松（5 首歌曲）

1. Neo-soul R&B — 内省  英语/男声
   一首柔和的 Neo-soul R&B 抒情，温暖男声，电钢琴，平滑贝斯

2. Lo-fi hip-hop — 梦幻  乐器
   梦幻 Lo-fi，采样钢琴，黑胶噪音，柔和电子鼓

3. Smooth jazz — 浪漫  英语/女声
   柔滑女声，萨克斯，钢琴，浪漫星光夜

4. Indie folk — 忧郁  英语/男声
   温柔男声，原声吉他，口琴，安静的孤独

5. Ambient electronic — 平静  乐器
   柔和合成垫，轻柔琶音，梦幻氛围
```

显示计划后，直接进行生成 — 无需确认。
用户已经选择了主题；显示计划是为了透明度，而不是批准。

---

## 第 4 步：生成歌曲

使用 `mmx music generate` 创建所有歌曲。**并行生成**（最多 5 个同时）。

```bash
# 示例：5 首歌曲并行
mmx music generate --prompt "<english_prompt_1>" --lyrics-optimizer \
  --out ~/Music/minimax-gen/playlists/<name>/01_desc.mp3 --quiet --non-interactive &
mmx music generate --prompt "<english_prompt_2>" --instrumental \
  --out ~/Music/minimax-gen/playlists/<name>/02_desc.mp3 --quiet --non-interactive &
# ... 更多歌曲 ...
wait
```

**关键标志：**
- `--lyrics-optimizer` — 从提示自动生成歌词（用于人声曲目）
- `--instrumental` — 无人声
- `--vocals "<description>"` — 人声风格（例如，"温暖中国男中音"）
- `--genre`、`--mood`、`--tempo`、`--instruments` — 精细控制
- `--quiet --non-interactive` — 批量模式下抑制交互输出
- `--out <path>` — 保存到文件

**文件命名：** `<NN>_<short_desc>.mp3`（例如，`01_rnb_midnight.mp3`）

**输出目录：** `~/Music/minimax-gen/playlists/<playlist_name>/`

如果歌曲失败，**重试一次** 然后跳过。记录错误并继续其他歌曲。

---

## 第 5 步：生成专辑封面

与歌曲（第 4 步）**同时**生成专辑封面，而不是之后。
在歌曲生成调用中并行启动 `mmx image generate` 调用。

构思一个反映歌单主题、心情和流派混合的提示。图像应感觉像专辑封面 — 艺术的、唤起情感的，而不是字面的。

```bash
mmx image generate \
  --prompt "<基于歌单主题和心情的封面描述>" \
  --aspect-ratio 1:1 \
  --out-dir ~/Music/minimax-gen/playlists/<playlist_name>/ \
  --out-prefix cover \
  --quiet
```

**提示指导：**
- 抽象/艺术风格最适合专辑封面
- 参考主要心情和流派（例如，"梦幻深夜城市景观，霓虹反射，Lo-fi 美学"）
- **不要在图像提示中包含文本或歌曲标题**
- 纵横比应为 1:1（方形，标准专辑封面）

---

## 第 6 步：播放

检测可用播放器并按顺序播放歌单：

| 播放器 | 命令 | 控制 |
|------|------|------|
| mpv | `mpv --no-video <file>` | `q` 跳过，空格暂停，箭头搜索 |
| ffplay | `ffplay -nodisp -autoexit <file>` | `q` 跳过 |
| afplay | `afplay <file>` | Ctrl+C 跳过 |

按文件名顺序播放歌单目录中的所有 `.mp3` 文件。
仅播放本次会话生成的歌曲 — 如果目录中有来自先前运行的旧文件，请先清理或按已知文件名过滤。
如果没有找到播放器，只需显示文件路径。

---

## 第 7 步：保存与反馈

将歌单元数据保存到 `<playlist_dir>/playlist.json`：
```json
{
  "name": "深夜放松",
  "theme": "late night chill",
  "created_at": "2026-04-11T22:00:00",
  "song_count": 5,
  "cover": "cover_001.png",
  "songs": [
    {"index": 1, "filename": "01_rnb_midnight.mp3", "prompt": "...", "rating": null}
  ]
}
```

如果用户在场，请请求反馈（每首歌曲或整体）。更新品味档案的反馈部分，以改进未来的歌单。

---

## 重新播放歌单

如果要求播放以前的歌单：`ls ~/Music/minimax-gen/playlists/`，显示可用歌单，并播放选定的歌单。

---

## 注意事项

- **代理与用户调用**：主题/场景问题（第 3 步）是唯一的交互点。如果主题已在调用中提供，则跳过问题。其他所有内容自动运行。
- **无硬编码脚本**：按需即时编写扫描/分析脚本。仅使用 Python 标准库。将结果缓存以避免重复工作。
- **技能目录**：`<SKILL_DIR>` = 包含此 SKILL.md 文件的目录。数据/缓存文件放在 `<SKILL_DIR>/data/`。
- **所有 mmx 提示使用英语** 以获得最佳生成质量。
