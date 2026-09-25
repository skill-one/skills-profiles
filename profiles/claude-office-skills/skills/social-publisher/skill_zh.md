# 社交媒体发布工具

通过智能调度、平台特定优化和集中式内容管理，实现多平台社交媒体发布的自动化。基于n8n工作流，如PostPulse。

## 概述

此技能可支持：
- 一键发布到多个平台
- 平台特定标题优化
- 自动化调度工作流
- 内容跟踪和分析
- AI驱动的标题生成

---

## 支持的平台

| 平台 | 内容类型 | 最佳发布时间 |
|------|----------|--------------|
| TikTok | 视频 (9:16) | 早上7点, 下午12点, 晚上7点 |
| Instagram | Reels, 文章, 故事 | 上午11点-下午1点, 晚上7-9点 |
| YouTube | Shorts, 视频 | 星期四至星期六下午2-4点 |
| LinkedIn | 文章, Posts, 视频 | 星期二至星期四上午8-10点 |
| Twitter/X | 文本, 图片, 视频 | 上午9点, 下午12点, 下午5点 |
| Facebook | Posts, Reels, 故事 | 下午1-4点 |
| Threads | 文本, 图片 | 早上7点-早上9点 |
| Pinterest | Pins, Idea Pins | 星期六晚上8-11点 |

---

## 发布工作流

### 工作流：Google Drive → 多平台

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Google Drive │───▶│ Detect New   │───▶│ Generate     │
│ (视频)      │    │ File         │    │ AI Captions  │
└──────────────┘    └──────────────┘    └──────────────┘
                                               │
         ┌─────────────────────────────────────┼─────────────────────────────────────┐
         │                                     │                                     │
         ▼                                     ▼                                     ▼
┌──────────────┐                    ┌──────────────┐                    ┌──────────────┐
│ TikTok       │                    │ Instagram    │                    │ YouTube      │
│ (休闲)      │                    │ (精致)      │                    │ (SEO优化)    │
└──────────────┘                    └──────────────┐                    └──────────────┘
         │                                     │                                     │
         └─────────────────────────────────────┼─────────────────────────────────────┘
                                               │
                                               ▼
                                    ┌──────────────┐
                                    │ Track in     │
                                    │ Airtable     │
                                    └──────────────┘
```

### n8n配置

```yaml
workflow: "多平台视频发布者"

trigger:
  type: google_drive
  event: file_created
  folder: "/待发布"
  file_types: [mp4, mov]

steps:
  1. get_video_metadata:
      extract: [filename, duration, size]
      
  2. generate_captions:
      provider: openai
      model: gpt-4
      prompts:
        tiktok: |
          为视频{filename}创建TikTok标题
          风格：休闲、流行、适合表情符号
          包含：3-5个标签
          最大：100个字符
          
        instagram: |
          为{filename}创建Instagram Reels标题
          风格：吸引人、稍长
          包含：故事元素，5-10个标签
          最大：150个字符（第一行钩子）
          
        youtube: |
          创建YouTube Shorts标题和描述
          标题：SEO优化、吸引人（60个字符）
          描述：关键词，2-3句话
          
        linkedin: |
          为{filename}创建专业的LinkedIn文章
          风格：专业、思想领导力
          包含：行业洞察，行动号召
          
  3. publish_parallel:
      tiktok:
        caption: "{tiktok_caption}"
        schedule: optimal_time
        
      instagram:
        type: reel
        caption: "{instagram_caption}"
        cover_image: auto_detect
        
      youtube:
        type: short
        title: "{youtube_title}"
        description: "{youtube_description}"
        visibility: public
        
      linkedin:
        content: "{linkedin_caption}"
        visibility: public
        
  4. track_results:
      platform: airtable
      base: "内容追踪器"
      record:
        video_name: "{filename}"
        platforms: [tiktok, instagram, youtube, linkedin]
        publish_time: "{timestamp}"
        status: "已发布"
        links: ["{tiktok_url}", "{ig_url}", "{yt_url}", "{li_url}"]
        
  5. notify:
      slack:
        channel: "#内容已发布"
        message: |
          ✅ 视频已发布到所有平台！
          📹 {filename}
          🔗 TikTok: {tiktok_url}
          🔗 Instagram: {ig_url}
          🔗 YouTube: {yt_url}
          🔗 LinkedIn: {li_url}
```

---

## 平台特定优化

### 标题适配

```yaml
caption_templates:
  original: "5个改变我生活的生产力技巧"
  
  tiktok:
    style: 休闲、流行
    output: "POV：你发现了这些5个技巧 🤯 #生产力 #生活技巧 #fyp"
    
  instagram:
    style: 吸引人、故事驱动
    output: |
      这些5个技巧彻底改变了我的工作方式 💡
      
      保存以供以后使用 ⬇️
      
      #生产力 #生活技巧 #更高效地工作 #动力 #技巧
    
  youtube:
    title: "5个改变你生活的生产力技巧"
    description: |
      了解成功专业人士使用的前沿生产力技巧。
      
      在这个视频中：
      00:00 简介
      00:15 技巧#1
      ...
      
      订阅获取更多生产力技巧！
      
  linkedin:
    style: 专业、有见地
    output: |
      在我优化工作流多年后，这些5个策略始终能带来结果：
      
      1. [具有专业背景的技巧]
      2. [具有商业应用的技巧]
      ...
      
      哪个生产力策略对你影响最大？
      
  twitter:
    style: 简洁、有力
    output: "5个真正有效的生产力技巧 (线程 🧵)"
```

### 各平台的标签策略

```yaml
hashtags:
  tiktok:
    count: 3-5
    mix: [流行、细分、品牌]
    placement: 标题末尾
    examples: ["#fyp", "#viral", "#生产力"]
    
  instagram:
    count: 5-15
    mix: [高流量、中等、细分]
    placement: 标题或评论中
    examples: ["#生产力", "#工作生活", "#技巧"]
    
  youtube:
    count: 标题区域3-5个
    placement: 描述中
    style: 关键词聚焦
    
  linkedin:
    count: 3-5
    placement: 文章末尾
    style: 专业
    examples: ["#领导力", "#生产力", "#职业建议"]
    
  twitter:
    count: 1-2
    placement: 行文中或末尾
    examples: ["#生产力"]
```

---

## 调度策略

### 内容日历模板

```yaml
weekly_schedule:
  周一:
    - platform: linkedin
      time: 上午8:00
      content_type: 思想领导力
      
    - platform: tiktok
      time: 晚上7:00
      content_type: 教育性
      
  周二:
    - platform: instagram
      time: 下午12:00
      content_type: reel
      
    - platform: twitter
      time: 上午9:00
      content_type: 线程
      
  周三:
    - platform: youtube
      time: 下午3:00
      content_type: short
      
    - platform: linkedin
      time: 上午10:00
      content_type: 文章
      
  周四:
    - platform: tiktok
      time: 下午12:00
      content_type: 流行
      
    - platform: instagram
      time: 晚上7:00
      content_type: 轮播图
      
  周五:
    - platform: all
      time: 不固定
      content_type: 互动性文章
```

### 批量发布

```yaml
batch_workflow:
  name: "每周内容批量"
  
  input:
    folder: "/内容/第{week_number}周"
    videos: 7
    
  process:
    1. sort_by_type:
        教育性: [mon, wed, fri]
        娱乐性: [tue, thu]
        推广性: [sat]
        社区性: [sun]
        
    2. assign_platforms:
        each_video:
          primary: auto_detect_best_fit
          secondary: [remaining_platforms]
          
    3. generate_all_captions:
        batch_size: 7
        parallel: true
        
    4. schedule:
        distribution: 最佳时间
        gap_between: 最少4小时
        
    5. queue_for_review:
        send_to: 内容管理
        deadline: 首次发布前24小时
```

---

## 分析集成

### 跨平台跟踪

```yaml
tracking_fields:
  per_post:
    - post_id
    - 平台
    - 发布时间
    - 内容类型
    - 标题
    - 标签
    - 浏览量 (24h, 48h, 7d)
    - 点赞
    - 评论
    - 分享
    - 收藏
    - 个人资料访问量
    - 粉丝变化
    
  汇总:
    - 总触达
    - 参与率
    - 最佳内容
    - 最佳发布时间
    - 受众增长
```

### 性能仪表盘

```markdown
# 每周社交媒体报告

## 概述
| 平台 | 发布数量 | 触达 | 参与度 | 粉丝 |
|------|----------|------|--------|------|
| TikTok | 7 | 15K | 8.5% | +500 |
| Instagram | 5 | 45K | 4.2% | +200 |
| YouTube | 3 | 25K | 6.1% | +150 |
| LinkedIn | 5 | 15K | 3.8% | +75 |

## 最佳表现内容
1. TikTok: "5个生产力技巧" - 45K浏览量，12%参与度
2. Instagram: "我的一天" - 18K浏览量，5.5%参与度
3. YouTube: "教程视频" - 12K浏览量，8%参与度

## 洞察
- 最佳日期：星期四（参与度平均2倍）
- 最佳时间：晚上7点（最高触达）
- 最佳内容类型：教育性（分享量3倍）

## 下周建议
- 创建更多教育性内容
- 星期四发布2倍内容
- 在所有平台测试晚上7点发布时间
```

---

## 输出示例

**请求**: "我有一个关于远程工作技巧的视频。为所有平台创建标题。"

**输出**:

```markdown
# 多平台标题：远程工作技巧

## TikTok
```
POV：你终于掌握了在家工作 🏠💻

这些3个技巧彻底改变了一切 ⬇️

#远程工作 #在家工作 #生产力技巧 #在家工作 #fyp
```

## Instagram Reel
```
3年的远程工作教会了我这些改变游戏规则的技巧 🚀

假装通勤的那个？实际上会改变生活。

保存以供以后在家工作使用 📌

.
.
.
#远程工作 #在家工作 #生产力技巧 #在家工作生活 #职业建议 #工作生活平衡 #家庭办公室 #远程工作者 #数字游民 #生产力
```

## YouTube Short
**标题**: "3个真正有效的远程工作技巧"

**描述**:
```
通过这些经过验证的生产力技巧掌握在家工作。

3年的远程工作后，这些策略在我的日常例行公事和产出中带来了最大的变化。

⏰ 时间戳：
0:00 - 简介
0:05 - 技巧#1
0:20 - 技巧#2
0:35 - 技巧#3

订阅获取更多生产力内容！

#shorts #远程工作 #生产力
```

## LinkedIn
```
3年的远程工作。这些才是真正起作用的东西：

1️⃣ 假装通勤
一个10分钟的散步在开始工作前告诉你的大脑该专注了。听起来很简单，但它对我的早晨生产力产生了革命性的影响。

2️⃣ 时间分段（带缓冲）
安排专注时间+缓冲时间。没有休息的连续通话是导致倦怠的公式。

3️⃣ 关闭仪式
当你关闭笔记本电脑时，用语言说"关闭完成"。这种认知边界有助于区分工作与个人时间。

你最好的远程工作技巧是什么？

#远程工作 #生产力 #工作生活平衡 #领导力
```

## Twitter/X
```
3个真正有效的远程工作技巧：

1. 假装通勤 - 在开始前散步一小段
2. 时间分段带15分钟缓冲
3. 当你关闭笔记本电脑时说"关闭完成"

最后一个听起来很奇怪，但它是一个改变游戏规则的技巧。
```

---

**推荐发布时间**：
- TikTok：星期四晚上7点
- Instagram：星期五下午12点
- YouTube：星期六下午3点
- LinkedIn：星期二上午9点
- Twitter：星期三下午12点

---

*社交媒体发布工具 - 隶属于Claude办公技能*
