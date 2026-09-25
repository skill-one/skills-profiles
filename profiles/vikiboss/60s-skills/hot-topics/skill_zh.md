# 热点话题与流行内容技能

此技能帮助AI代理从中国主要社交媒体和内容平台获取流行话题和热门搜索。

## 使用场景

当用户需要：
- 了解社交媒体上的热门话题
- 询问热点话题或病毒式内容
- 了解当前流行讨论
- 跨平台追踪流行话题
- 研究社交媒体趋势

时，可以使用此技能。

## 支持平台

1. **微博 (Weibo)** - 中国版Twitter
2. **知乎 (Zhihu)** - 中国版Quora
3. **百度 (Baidu)** - 中国最大搜索引擎
4. **抖音 (Douyin)** - 中国版TikTok
5. **今日头条 (Toutiao)** - 字节跳动新闻聚合平台
6. **哔哩哔哩 (Bilibili)** - 中国版YouTube

## API接口

| 平台 | 接口 | 描述 |
|------|------|------|
| 微博 | `/v2/weibo` | 微博热搜话题 |
| 知乎 | `/v2/zhihu` | 知乎流行问题 |
| 百度 | `/v2/baidu/hot` | 百度热搜 |
| 抖音 | `/v2/douyin` | 抖音流行视频 |
| 今日头条 | `/v2/toutiao` | 今日头条热新闻 |
| 哔哩哔哩 | `/v2/bili` | 哔哩哔哩流行视频 |

所有接口使用**GET**方法，基础URL为：`https://60s.viki.moe/v2`

## 使用方法

### 获取微博热搜

```python
import requests

def get_weibo_hot():
    response = requests.get('https://60s.viki.moe/v2/weibo')
    return response.json()

hot_topics = get_weibo_hot()
print("🔥 微博热搜：")
for i, topic in enumerate(hot_topics['data'][:10], 1):
    print(f"{i}. {topic['title']} - 热度: {topic['热度']}")
```

### 获取知乎热榜

```python
def get_zhihu_hot():
    response = requests.get('https://60s.viki.moe/v2/zhihu')
    return response.json()

topics = get_zhihu_hot()
print("💡 知乎热榜：")
for topic in topics['data'][:10]:
    print(f"· {topic['title']}")
```

### 获取多平台趋势

```python
def get_all_hot_topics():
    platforms = {
        'weibo': 'https://60s.viki.moe/v2/weibo',
        'zhihu': 'https://60s.viki.moe/v2/zhihu',
        'baidu': 'https://60s.viki.moe/v2/baidu/hot',
        'douyin': 'https://60s.viki.moe/v2/douyin',
        'bili': 'https://60s.viki.moe/v2/bili'
    }
    
    results = {}
    for name, url in platforms.items():
        try:
            response = requests.get(url)
            results[name] = response.json()
        except:
            results[name] = None
    
    return results

# 使用示例
all_topics = get_all_hot_topics()
```

### 简单bash示例

```bash
# 微博热搜
curl "https://60s.viki.moe/v2/weibo"

# 知乎流行
curl "https://60s.viki.moe/v2/zhihu"

# 百度热搜
curl "https://60s.viki.moe/v2/baidu/hot"

# 抖音流行
curl "https://60s.viki.moe/v2/douyin"

# 哔哩哔哩流行
curl "https://60s.viki.moe/v2/bili"
```

## 响应格式

响应通常包含：

```json
{
  "data": [
    {
      "title": "话题标题",
      "url": "https://...",
      "热度": "1234567",
      "rank": 1
    },
    ...
  ],
  "update_time": "2024-01-15 14:00:00"
}
```

## 示例交互

### 用户："现在微博上什么最火？"

```python
hot = get_weibo_hot()
top_5 = hot['data'][:5]

response = "🔥 微博热搜 TOP 5：\n\n"
for i, topic in enumerate(top_5, 1):
    response += f"{i}. {topic['title']}\n"
    response += f"   热度：{topic.get('热度', 'N/A')}\n\n"
```

### 用户："知乎上大家在讨论什么？"

```python
zhihu = get_zhihu_hot()
response = "💡 知乎当前热门话题：\n\n"
for topic in zhihu['data'][:8]:
    response += f"· {topic['title']}\n"
```

### 用户："对比各平台热点"

```python
def compare_platform_trends():
    all_topics = get_all_hot_topics()
    
    summary = "📊 各平台热点概览\n\n"
    
    platforms = {
        'weibo': '微博',
        'zhihu': '知乎',
        'baidu': '百度',
        'douyin': '抖音',
        'bili': 'B站'
    }
    
    for key, name in platforms.items():
        if all_topics.get(key):
            top_topic = all_topics[key]['data'][0]
            summary += f"{name}：{top_topic['title']}\n"
    
    return summary
```

## 最佳实践

1. **速率限制**：不要频繁调用API，数据每几分钟更新一次
2. **错误处理**：始终处理网络错误和无效响应
3. **缓存**：结果缓存5-10分钟以减少API调用
4. **Top N**：通常显示前5-10项就足够
5. **上下文**：展示流行话题时提供平台上下文

## 常见用例

### 1. 每日热点摘要

```python
def get_daily_trending_summary():
    weibo = get_weibo_hot()
    zhihu = get_zhihu_hot()
    
    summary = "📱 今日热点速览\n\n"
    summary += "【微博热搜】\n"
    summary += "\n".join([f"{i}. {t['title']}" 
                          for i, t in enumerate(weibo['data'][:3], 1)])
    summary += "\n\n【知乎热榜】\n"
    summary += "\n".join([f"{i}. {t['title']}" 
                          for i, t in enumerate(zhihu['data'][:3], 1)])
    
    return summary
```

### 2. 跨平台查找共同话题

```python
def find_common_topics():
    all_topics = get_all_hot_topics()
    
    # 从所有平台提取标题
    all_titles = []
    for platform_data in all_topics.values():
        if platform_data and 'data' in platform_data:
            all_titles.extend([t['title'] for t in platform_data['data']])
    
    # 简单关键词匹配（可改进）
    from collections import Counter
    keywords = []
    for title in all_titles:
        keywords.extend(title.split())
    
    common = Counter(keywords).most_common(10)
    return f"🔍 热门关键词：{', '.join([k for k, _ in common])}"
```

### 3. 平台特定趋势警报

```python
def check_trending_topic(keyword):
    platforms = ['weibo', 'zhihu', 'baidu']
    found_in = []
    
    for platform in platforms:
        url = f'https://60s.viki.moe/v2/{platform}' if platform != 'baidu' else 'https://60s.viki.moe/v2/baidu/hot'
        data = requests.get(url).json()
        
        for topic in data['data']:
            if keyword.lower() in topic['title'].lower():
                found_in.append(platform)
                break
    
    if found_in:
        return f"✅ 话题 '{keyword}' 正在以下平台trending: {', '.join(found_in)}"
    return f"❌ 话题 '{keyword}' 未在主流平台trending"
```

### 4. 趋势内容推荐

```python
def recommend_content_by_interest(interest):
    """根据用户兴趣推荐趋势内容"""
    all_topics = get_all_hot_topics()
    
    recommendations = []
    for platform, data in all_topics.items():
        if data and 'data' in data:
            for topic in data['data']:
                if interest.lower() in topic['title'].lower():
                    recommendations.append({
                        'platform': platform,
                        'title': topic['title'],
                        'url': topic.get('url', '')
                    })
    
    return recommendations
```

## 平台特定说明

### 微博 (Weibo)
- 频繁更新（几分钟一次）
- 包含"热度"（热度值）
- 部分话题可能带有"热"或"新"标签

### 知乎 (Zhihu)
- 专注于问题和讨论
- 通常话题更深入
- 适合了解人们的好奇心所在

### 百度 (Baidu)
- 反映搜索趋势
- 良好反映主流兴趣
- 包含各种分类

### 抖音 (Douyin)
- 视频导向的趋势
- 娱乐和生活方式内容
- 年轻受众兴趣

### 哔哩哔哩 (Bilibili)
- 视频平台趋势
- ACG（动漫、漫画、游戏）文化
- 创意内容焦点

## 故障排除

### 问题：空或null数据
- **解决方案**：API可能正在更新，几秒后重试
- 检查网络连接

### 问题：时间戳过旧
- **解决方案**：数据已缓存，这是正常的
- 大多数平台每5-15分钟更新一次

### 问题：缺少平台
- **解决方案**：确保正确的接口URL
- 检查API文档的变更

## 相关资源

- [60s API文档](https://docs.60s-api.viki.moe)
- [GitHub仓库](https://github.com/vikiboss/60s)
