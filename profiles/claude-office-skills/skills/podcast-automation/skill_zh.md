# 节目自动化

全面的技能，用于自动化节目制作和分发。

## 核心工作流程

### 1. 制作流程

```
节目制作流程：
┌─────────────────┐
│    规划     │
│  - 主题       │
│  - 嘉宾       │
│  - 时间安排     │
└────────┬────────┘
         ▼
┌─────────────────┐
│   录制     │
│  - 音频       │
│  - 视频（可选）  │
└────────┬────────┘
         ▼
┌─────────────────┐
│    编辑      │
│  - 清理音频  │
│  - 添加开场白    │
│  - 母带处理    │
└────────┬────────┘
         ▼
┌─────────────────┐
│   制作      │
│  - 节目笔记   │
│  - 文字稿   │
│  - 章节     │
└────────┬────────┘
         ▼
┌─────────────────┐
│  分发      │
│  - RSS      │
│  - 平台    │
│  - 社交    │
└─────────────────┘
```

### 2. 章节配置

```yaml
chapter_config:
  metadata:
    title: "{{chapter_title}}"
    chapter_number: "{{number}}"
    season: "{{season}}"
    description: "{{description}}"
    
  audio:
    file: "chapter_{{number}}.mp3"
    format: mp3
    bitrate: 128kbps
    sample_rate: 44100
    
  settings:
    explicit: false
    chapter_type: full  # full, trailer, bonus
    
  links:
    - title: "Chapter Notes"
      url: "{{chapter_notes_url}}"
    - title: "Guest's Website"
      url: "{{guest_url}}"
```

## 音频处理

### 处理流程

```yaml
audio_processing:
  input:
    format: wav
    channels: 立体声
    
  处理:
    - 步骤: 噪音抑制
      阈值: -30db
      
    - 步骤: 归一化
      目标_lufs: -16
      
    - 步骤: 压缩
      比率: 4:1
      阈值: -20db
      
    - 步骤: 均衡器
      预设: 人声增强
      
    - 步骤: 添加开场白
      文件: "intro.mp3"
      淡入: 2s
      
    - 步骤: 添加结尾
      文件: "outro.mp3"
      淡出: 3s
      
  输出:
    format: mp3
    bitrate: 128kbps
    文件名: "{{show}}_C{{number}}.mp3"
```

### 母带处理模板

```yaml
mastering_config:
  动态范围:
    目标: -16 LUFS
    范围: 8 LU
    真实峰值: -1 dBTP
    
  均衡器设置:
    高通滤波: 80Hz
    人声增强: +2dB @ 3kHz
    空气感: +1dB @ 12kHz
    
  动态控制:
    压缩器:
      比率: 3:1
      攻击时间: 10ms
      释放时间: 100ms
    限制器:
      上限: -1dB
```

## 节目笔记模板

### 章节笔记

```yaml
chapter_notes_template:
  format: markdown
  
  结构: |
    # {{chapter_title}}
    
    ## 章节 {{number}} | 季节 {{season}}
    
    **发布日期:** {{publish_date}}
    **时长:** {{duration}}
    
    ## 摘要
    {{summary}}
    
    ## 嘉宾
    {{#if guest}}
    **{{guest.name}}** - {{guest.title}}
    - 网站: {{guest.website}}
    - Twitter: {{guest.twitter}}
    - LinkedIn: {{guest.linkedin}}
    {{/if}}
    
    ## 时间戳
    {{#each timestamps}}
    - {{this.start}} - {{this.title}}
    {{/each}}
    
    ## 关键要点
    {{#each takeaways}}
    - {{this}}
    {{/each}}
    
    ## 提及的资源
    {{#each resources}}
    - [{{this.title}}]({{this.url}})
    {{/each}}
    
    ## 订阅
    - [Apple Podcasts]({{apple_url}})
    - [Spotify]({{spotify_url}})
    - [RSS Feed]({{rss_url}})
```

## RSS Feed 管理

### Feed 配置

```yaml
rss_feed:
  channel:
    title: "{{podcast_name}}"
    description: "{{podcast_description}}"
    语言: "zh-cn"
    版权: "© 2024 {{company}}"
    作者: "{{host_name}}"
    所有者:
      name: "{{owner_name}}"
      email: "{{owner_email}}"
    图片:
      url: "{{artwork_url}}"
      宽度: 3000
      高度: 3000
    分类:
      - "商业"
      - "科技"
    显著性: false
    
  itunes:
    类型: 章节式  # 或连续式
    完整: false
    
  项目:
    - title: "{{chapter.title}}"
      description: "{{chapter.description}}"
      封装:
        url: "{{audio_url}}"
        长度: "{{file_size}}"
        类型: "audio/mpeg"
      发布日期: "{{publish_date}}"
      时长: "{{duration}}"
      显著性: false
      章节: "{{number}}"
      季节: "{{season}}"
```

## 分发

### 平台分发

```yaml
distribution_platforms:
  主要:
    - 平台: apple_podcasts
      api: podcasts_connect
      自动发布: true
      
    - 平台: spotify
      api: spotify_for_podcasters
      自动发布: true
      
  次要:
    - google_podcasts
    - amazon_music
    - stitcher
    - overcast
    - pocket_casts
    - castbox
    
  视频:
    - 平台: youtube
      类型: 完整章节
      缩略图: 自动生成
      
    - 平台: youtube
      类型: 片段
      数量: 3-5
      时长: 60s
```

### 社交媒体分发

```yaml
social_promotion:
  发布时:
    - 平台: twitter
      发布:
        - 类型: 公告
          文本: |
            🎙️ 新章节发布！
            
            {{chapter.title}}
            
            {{teaser}}
            
            立即收听: {{link}}
            
        - 类型: 片段
          音频片段: 60s
          时间戳: 最佳时刻
          
    - 平台: linkedin
      文本: |
        很高兴分享我们最新的章节！
        
        {{chapter.title}}
        
        关键要点:
        {{takeaways}}
        
        评论中见链接 👇
        
    - 平台: instagram
      类型: 轮播
      幻灯片:
        - 封面图片
        - 引用1
        - 引用2
        - 行动号召
```

## 分析仪表盘

```
节目分析 - 过去30天
═══════════════════════════════════════

下载量: 45,230 (+12%)
独立听众: 28,450

按章节:
┌─────────────────────────────────────┬───────────┐
│ 章节                              │ 下载量 │
├─────────────────────────────────────┼───────────┤
│ E45: CEO 采访                     │ 8,450     │
│ E44: 2024行业趋势                 │ 6,230     │
│ E43: 幕后故事                    │ 5,890     │
└─────────────────────────────────────┴───────────┘

按平台:
Apple Podcasts  ████████████████ 52%
Spotify         ██████████░░░░░░ 32%
Google          ████░░░░░░░░░░░░ 8%
其他           ███░░░░░░░░░░░░░ 8%

听众留存率:
0-25%    ████████████████████ 100%
25-50%   ██████████████████░░ 89%
50-75%   ██████████████░░░░░░ 72%
75-100%  ████████████░░░░░░░░ 58%

地理分布:
美国       ████████████████ 65%
英国      ████░░░░░░░░░░░░ 12%
加拿大     ███░░░░░░░░░░░░░ 8%
澳大利亚    ██░░░░░░░░░░░░░░ 5%
```

## 嘉宾管理

### 嘉宾工作流程

```yaml
guest_workflow:
  联系:
    模板: |
      你好 {{guest_name}},
      
      我是 {{podcast_name}} 的主持人，这是一个关于 {{topic}} 的节目。
      
      我想邀请你讨论 {{proposed_topic}}。
      
      我们的听众是 {{audience_description}}。
      
      你有兴趣吗？
      
  安排:
    工具: calendly
    时长: 60分钟
    间隙: 15分钟
    
  采访前:
    提前发送天数: 3
    包含:
      - 录音指南
      - 主题大纲
      - 技术要求
      - 同意书
      
  采访后:
    - 发送感谢信
    - 分享发布日期
    - 提供宣传素材
    - 请求分享
```

## 盈利

### 收入来源

```yaml
monetization:
  赞助:
    位置:
      - 预加载: 15-30s
      - 中加载: 60s
      - 后加载: 15s
    定价:
      cpm: 25  # 每千次下载
      
  精华内容:
    平台: patreon
    层级:
      - 名称: "支持者"
        价格: 5
        奖励:
          - 无广告章节
          - 精华内容
      - 名称: "精华"
        价格: 15
        奖励:
          - 所有支持者
          - 独家章节
          - 社区访问
          
  联盟营销:
    项目:
      - amazon_associates
      - 产品合作
    披露: 需要
```

## 最佳实践

1. **固定时间表**: 每周同一时间
2. **高质量音频**: 投资良好设备
3. **节目笔记**: 详细且SEO优化
4. **文字稿**: 可访问性和SEO
5. **推广**: 多平台营销
6. **互动听众**: 回应反馈
7. **分析**: 跟踪和改进
8. **嘉宾准备**: 充分准备的采访
