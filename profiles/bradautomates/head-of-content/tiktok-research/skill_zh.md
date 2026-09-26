# TikTok 研究

研究表现优异的 TikTok 视频，识别异常值，并分析顶级视频内容以提取钩子（Hook）和结构。

## 前置条件

- `APIFY_TOKEN` 环境变量或存在于 `.env` 文件中
- `GEMINI_API_KEY` 环境变量或存在于 `.env` 文件中
- `apify-client` 和 `google-genai` Python 包
- 在 `.claude/context/tiktok-accounts.md` 中配置的账户

验证设置：
```bash
python3 -c "
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from apify_client import ApifyClient
from google import genai
assert os.environ.get('APIFY_TOKEN'), 'APIFY_TOKEN 未设置'
assert os.environ.get('GEMINI_API_KEY'), 'GEMINI_API_KEY 未设置'
" && echo "前置条件正常"
```

## 工作流程

### 1. 创建运行文件夹

```bash
RUN_FOLDER="tiktok-research/$(date +%Y-%m-%d_%H%M%S)" && mkdir -p "$RUN_FOLDER" && echo "$RUN_FOLDER"
```

### 2. 获取内容

```bash
python3 .claude/skills/tiktok-research/scripts/fetch_tiktok.py \
  --days 30 \
  --limit 50 \
  --sorting latest \
  --output {RUN_FOLDER}/raw.json
```

参数：
- `--days`: 搜索的过去天数（默认：30）
- `--limit`: 每个账户的最大视频数（默认：50）
- `--sorting`: "latest"（最新）、"popular"（热门）或 "oldest"（最早）（默认：latest）
- `--usernames`: 使用特定用户名覆盖账户文件

### 3. 识别异常值

```bash
python3 .claude/skills/tiktok-research/scripts/analyze_posts.py \
  --input {RUN_FOLDER}/raw.json \
  --output {RUN_FOLDER}/outliers.json \
  --threshold 2.0
```

输出 JSON 包含：
- `total_videos`: 分析的视频数量
- `outlier_count`: 发现的异常值数量
- `topics`: 顶级标签、音效和关键词
- `accounts`: 分析的账户列表
- `outliers`: 异常值视频及其互动指标数组

### 4. 使用 AI 分析顶级视频

```bash
python3 .claude/skills/video-content-analyzer/scripts/analyze_videos.py \
  --input {RUN_FOLDER}/outliers.json \
  --output {RUN_FOLDER}/video-analysis.json \
  --platform tiktok \
  --max-videos 5
```

从每个视频中提取：
- 钩子技巧和可复制的公式
- 内容结构和部分
- 保留技巧
- CTA 策略

参考 `video-content-analyzer` 技能获取完整的输出模式（schema）和钩子/格式类型。

### 5. 生成报告

读取 `{RUN_FOLDER}/outliers.json` 和 `{RUN_FOLDER}/video-analysis.json`，然后生成 `{RUN_FOLDER}/report.md`。

**报告结构：**

```markdown
# TikTok 研究报告

生成时间：{date}

## 顶级钩子（Hook）

按互动量排名。使用这些公式为你的内容创作。

### 钩子 1：{technique} - @{username}
- **开场白**："{opening_line}"
- **为何有效**：{attention_grab}
- **可复制的公式**：{replicable_formula}
- **互动量**：{diggCount} 点赞，{commentCount} 评论，{playCount} 播放
- [观看视频]({webVideoUrl})

[重复每个分析视频]

## 内容结构模式

| 视频 | 格式 | 节奏 | 关键保留技巧 |
|-------|--------|--------|--------------------------|
| @username | {format} | {pacing} | {techniques} |

## CTA 策略

| 视频 | CTA 类型 | CTA 文本 | 位置 |
|-------|----------|----------|-----------|
| @username | {type} | "{cta_text}" | {placement} |

## 所有异常值

| 排名 | 用户名 | 点赞 | 评论 | 分享 | 播放 | 互动率 |
|------|----------|-------|----------|--------|-------|-----------------|
[列出所有异常值及其指标和链接]

## 热门趋势

### 顶级标签
[来自 outliers.json topics.hashtags]

### 顶级音效
[来自 outliers.json topics.sounds]

### 顶级关键词
[来自 outliers.json topics.keywords]

## 可操作的启示

[将模式综合为 4-6 条具体建议]

## 分析的账户

[列出账户]
```

重点关注可操作的洞察。带有可复制公式的“顶级钩子”部分应突出显示。

## 快速参考

完整流程：
```bash
RUN_FOLDER="tiktok-research/$(date +%Y-%m-%d_%H%M%S)" && mkdir -p "$RUN_FOLDER" && \
python3 .claude/skills/tiktok-research/scripts/fetch_tiktok.py -o "$RUN_FOLDER/raw.json" && \
python3 .claude/skills/tiktok-research/scripts/analyze_posts.py -i "$RUN_FOLDER/raw.json" -o "$RUN_FOLDER/outliers.json" && \
python3 .claude/skills/video-content-analyzer/scripts/analyze_videos.py -i "$RUN_FOLDER/outliers.json" -o "$RUN_FOLDER/video-analysis.json" -p tiktok
```

然后读取两个 JSON 文件并生成报告。

## 互动指标

**互动分数**：`likes + (3 x comments) + (2 x shares) + (2 x saves) + (0.05 x views)`

**异常值检测**：互动率 > 平均值 + (阈值 x 标准差)

**互动率**： (分数 / 粉丝数) x 100

## TikTok 特定字段

- `diggCount`：点赞/爱心
- `shareCount`：分享
- `playCount`：视频播放量
- `commentCount`：评论
- `collectCount`：保存/收藏
- `authorFollowers`：创作者的粉丝数
- `musicName`：视频使用的音效
- `musicOriginal`：音效是否原创
