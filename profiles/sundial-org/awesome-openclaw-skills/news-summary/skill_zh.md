# 新闻摘要

## 概述

通过 RSS 订阅从可靠的国际来源获取并摘要新闻。

## RSS 订阅源

### BBC（主要）
```bash
# 世界新闻
curl -s "https://feeds.bbci.co.uk/news/world/rss.xml"

# 重要新闻
curl -s "https://feeds.bbci.co.uk/news/rss.xml"

# 商业
curl -s "https://feeds.bbci.co.uk/news/business/rss.xml"

# 科技
curl -s "https://feeds.bbci.co.uk/news/technology/rss.xml"
```

### 路透社
```bash
# 世界新闻
curl -s "https://www.reutersagency.com/feed/?best-regions=world&post_type=best"
```

### NPR（美国视角）
```bash
curl -s "https://feeds.npr.org/1001/rss.xml"
```

### 阿拉比亚电视台（全球南方视角）
```bash
curl -s "https://www.aljazeera.com/xml/rss/all.xml"
```

## 解析 RSS

提取标题和描述：
```bash
curl -s "https://feeds.bbci.co.uk/news/world/rss.xml" | \
  grep -E "<title>|<description>" | \
  sed 's/<[^>]*>//g' | \
  sed 's/^[ \t]*//' | \
  head -30
```

## 工作流程

### 文字摘要
1. 获取 BBC 世界头条新闻
2. 可选地补充路透社/NPR
3. 摘要关键新闻
4. 按地区或主题分类

### 语音摘要
1. 创建文字摘要
2. 使用 OpenAI TTS 生成语音
3. 发送为音频消息

```bash
curl -s https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "<新闻摘要文本>",
    "voice": "onyx",
    "speed": 0.95
  }' \
  --output /tmp/news.mp3
```

## 示例输出格式

```
📰 新闻摘要 [日期]

🌍 世界
- [头条新闻 1]
- [头条新闻 2]

💼 商业
- [头条新闻 1]

💻 科技
- [头条新闻 1]
```

## 最佳实践

- 摘要简洁（5-8 个头条新闻）
- 优先处理突发新闻和重大事件
- 语音版：最长 2 分钟
- 平衡视角（西方 + 全球南方）
- 如被要求，需注明来源
