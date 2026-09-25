# Instagram 研究

研究表现优异的 Instagram 文章和 Reels，识别异常值，并分析顶级视频内容以获取钩子点和结构。

## 前置条件

- `APIFY_TOKEN` 环境变量或位于 `.env` 文件中
- `GEMINI_API_KEY` 环境变量或位于 `.env` 文件中
- `apify-client` 和 `google-genai` Python 包
- 在 `.claude/context/instagram-accounts.md` 中配置的账户

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
" && echo "前置条件 OK"
```

## 工作流程

### 1. 创建运行文件夹

```bash
RUN_FOLDER="instagram-research/$(date +%Y-%m-%d_%H%M%S)" && mkdir -p "$RUN_FOLDER" && echo "$RUN_FOLDER"
```

### 2. 获取内容

```bash
python3 .claude/skills/instagram-research/scripts/fetch_instagram.py \
  --type reels \
  --days 30 \
  --limit 50 \
  --output {RUN_FOLDER}/raw.json
```

参数：
- `--type`: "posts", "reels" 或 "stories"
- `--days`: 搜索的过去天数（默认：30）
- `--limit`: 每个账户的最大项目数（默认：50）

### 3. 识别异常值

```bash
python3 .claude/skills/instagram-research/scripts/analyze_posts.py \
  --input {RUN_FOLDER}/raw.json \
  --output {RUN_FOLDER}/outliers.json \
  --threshold 2.0
```

输出 JSON 包含：
- `total_posts`: 分析的文章数量
- `outlier_count`: 发现的异常值数量
- `topics`: 顶级标签和关键词
- `accounts`: 分析的账户列表
- `outliers`: 异常值文章及其参与度指标的数组

### 4. 使用 AI 分析顶级视频

```bash
python3 .claude/skills/video-content-analyzer/scripts/analyze_videos.py \
  --input {RUN_FOLDER}/outliers.json \
  --output {RUN_FOLDER}/video-analysis.json \
  --platform instagram \
  --max-videos 5
```

从每个视频中提取：
- 钩子技巧和可复制的公式
- 内容结构和部分
- 保持技术
- CTA 策略

参考 `video-content-analyzer` 技能获取完整输出模式和钩子/格式类型。

### 5. 生成报告

读取 `{RUN_FOLDER}/outliers.json` 和 `{RUN_FOLDER}/video-analysis.json`，然后生成 `{RUN_FOLDER}/report.md`。

**报告结构：**

```markdown
# Instagram 研究报告

生成时间：{date}

## 顶级表现钩子

按参与度排序。使用这些公式为您的内容。

### 钩子 1：{technique} - @{username}
- **开头**："{opening_line}"
- **为什么有效**：{attention_grab}
- **可复制的公式**：{replicable_formula}
- **参与度**：{likes} 个赞，{comments} 条评论，{views} 次观看
- [观看视频]({url})

[重复每个分析的视频]

## 内容结构模式

| 视频 | 格式 | 节奏 | 关键保持技术 |
|-------|--------|--------|--------------------------|
| @username | {format} | {pacing} | {techniques} |

## CTA 策略

| 视频 | CTA 类型 | CTA 文本 | 位置 |
|-------|----------|----------|-----------|
| @username | {type} | "{cta_text}" | {placement} |

## 所有异常值

| 排名 | 用户名 | 赞 | 评论 | 观看 | 参与度 |
|------|----------|-------|----------|-------|-----------------|
[List 所有异常值及其指标和链接]

## 热门话题

### 顶级标签
[从 outliers.json topics.hashtags]

### 顶级关键词
[从 outliers.json topics.keywords]

## 可操作的要点

[将模式综合为 4-6 项具体建议]

## 分析的账户
[List 账户]
```

专注于可操作的见解。"顶级表现钩子" 部分应突出显示可复制的公式。

## 快速参考

完整流程：
```bash
RUN_FOLDER="instagram-research/$(date +%Y-%m-%d_%H%M%S)" && mkdir -p "$RUN_FOLDER" && \
python3 .claude/skills/instagram-research/scripts/fetch_instagram.py --type reels -o "$RUN_FOLDER/raw.json" && \
python3 .claude/skills/instagram-research/scripts/analyze_posts.py -i "$RUN_FOLDER/raw.json" -o "$RUN_FOLDER/outliers.json" && \
python3 .claude/skills/video-content-analyzer/scripts/analyze_videos.py -i "$RUN_FOLDER/outliers.json" -o "$RUN_FOLDER/video-analysis.json" -p instagram
```

然后读取两个 JSON 文件并生成报告。

## 参与度指标

**参与度分数**：`likes + (3 × comments) + (0.1 × views)`

**异常值检测**：参与度 > mean + (threshold × std_dev) 的文章

**参与度**： (score / followers) × 100
