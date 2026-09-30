---
name: site-specification
description: 从简单的描述中提取全面的网站规格。在分析用户的主题请求时使用，以确定网站类型、受众、语气、布局要求和排版。
---

# 网站规格技能

从用户描述中提取详细的网站规格，以指导主题生成。如果用户提供了图片、图片链接或其他文档，请分析它们以获取有关品牌和设计偏好的额外线索——显然，诸如现有标志图像之类的东西可以非常有效地提供有关品牌的审美、语气和价值观的信息，而任何书面文档都可能包含有关品牌身份或设计偏好的明确声明。

## 网站规格模式

一个完整的网站规格使用此 JSON 结构：

```json
{
  "siteBrief": {
    "siteName": "网站/业务的名称",
    "siteType": "网站类型（例如，电子商务、作品集、博客、SaaS、餐厅）",
    "primaryGoal": "网站的主要目的或转化目标",
    "audience": "目标受众描述",
    "tone": "内容的语气和风格",
    "brandKeywords": "描述品牌审美和价值观的关键词"
  },
  "layoutNotes": [
    "每个布局要求作为一个单独的字符串",
    "部分、功能和视觉元素"
  ],
  "typography": {
    "primaryFont": "标题的主要字体",
    "secondaryFont": "正文使用的字体",
    "usage": "字体的应用方式",
    "fontImport": "Google Fonts 导入 URL"
  }
}
```

所有字段都是可选的——仅包括可以从用户的描述中合理推断出的内容。

## 按网站类型进行推断模式

### SaaS / 技术

**推断：**
- 主要目标：推动注册或演示请求
- 目标受众：技术决策者、开发人员或业务用户
- 语气：专业、创新、值得信赖
- 品牌关键词：现代、高效、强大、无缝

**典型布局：**
- 带有价值主张和行动号召的英雄区域
- 功能网格或比较
- 社会证明（标志、客户评价）
- 定价部分
- 常见问题解答
- 最终行动号召

**字体趋势：**
- 干净的几何无衬线字体
- 强大的层次结构以供扫描
- 考虑：Satoshi、Plus Jakarta Sans、Outfit

### 电子商务 / 零售

**推断：**
- 主要目标：推动购买
- 目标受众：具有特定兴趣的消费者
- 语气：因品牌而异（奢华与休闲与价值）
- 品牌关键词：取决于定位

**典型布局：**
- 带有特色产品或促销的英雄区域
- 分类导航
- 特色产品网格
- 信任信号（评价、保证）
- 订阅通讯

**字体趋势：**
- 与品牌定位相匹配
- 奢华：精致衬线字体
- 现代：几何无衬线字体
- 活泼：展示字体

### 专业服务（法律、金融、咨询）

**推断：**
- 主要目标：产生询问或建立信誉
- 目标受众：业务决策者、寻求专业知识的个人
- 语气：专业、权威、值得信赖
- 品牌关键词：专业知识、诚信、成熟、可靠

**典型布局：**
- 带有资质或价值声明的英雄区域
- 服务/业务领域
- 团队简介
- 案例研究或成果
- 客户评价
- 联系/咨询行动号召

**字体趋势：**
- 标题使用传统衬线字体（信誉）
- 正文使用干净的无衬线字体（可读性）
- 考虑：Cormorant Garamond、DM Serif Display、Source Sans Pro

### 餐厅 / 食品服务

**推断：**
- 主要目标：推动预订或访问
- 目标受众：当地食客、美食爱好者
- 语气：温暖、邀请、刺激食欲
- 品牌关键词：新鲜、手工制作、舒适、正宗

**典型布局：**
- 带有诱人食物图像的英雄区域
- 菜单部分
- 关于/故事
- 地址和营业时间
- 预订行动号召
- Instagram 或画廊

**字体趋势：**
- 用于个性展示的展示字体
- 菜单使用可读的衬线或无衬线字体
- 考虑：Playfair Display、Lora、Josefin Sans

### 创意 / 作品集

**推断：**
- 主要目标：展示作品并吸引客户
- 目标受众：潜在客户、艺术总监、合作者
- 语气：创意、独特、以个性驱动
- 品牌关键词：原创、制作、艺术、独特

**典型布局：**
- 全出血作品集英雄区域
- 项目画廊或案例研究
- 关于/简介部分
- 提供的服务
- 联系或询问表单

**字体趋势：**
- 独特的展示字体
- 与创作者风格个性化
- 考虑：Clash Display、Fraunces、Syne

### 博客 / 媒体

**推断：**
- 主要目标：吸引读者并建立受众
- 目标受众：具有特定兴趣的读者
- 语气：因细分领域而异（权威、休闲、娱乐）
- 品牌关键词：信息量、吸引人、可信

**典型布局：**
- 精选文章英雄区域
- 最近文章网格或列表
- 分类导航
- 关于作者
- 订阅通讯
- 热门/趋势部分

**字体趋势：**
- 可读的正文字体（对长格式至关重要）
- 干净的标题字体
- 考虑：Merriweather、Source Serif Pro、DM Sans

### 非营利组织 / 组织

**推断：**
- 主要目标：推动捐赠、志愿者或意识
- 目标受众：支持者、潜在捐赠者、社区居民
- 语气：富有同情心、紧迫、值得信赖
- 品牌关键词：影响、社区、改变、希望

**典型布局：**
- 带有使命声明和行动号召的英雄区域
- 影响统计数据
- 项目/计划
- 影响故事
- 帮助方式（捐赠、志愿者）
- 订阅通讯/更新

**字体趋势：**
- 温暖、友好的字体
- 避免冷冰冰的企业感
- 考虑：Lato、Open Sans、PT Serif

## 示例

### 示例 1：咖啡店

**用户提示：** "为我的咖啡店 Bean & Brew 创建一个主题"

```json
{
  "siteBrief": {
    "siteName": "Bean & Brew",
    "siteType": "咖啡店",
    "primaryGoal": "吸引当地顾客并展示菜单",
    "audience": "咖啡爱好者、当地社区居民、寻找舒适工作空间的远程工作者",
    "tone": "温暖、邀请、手工艺、以社区为中心",
    "brandKeywords": "舒适、手工制作、芳香、原木色、暖棕色、奶油色点缀"
  },
  "layoutNotes": [
    "带有邀请性咖啡店内部或特色饮品的英雄区域",
    "菜单部分，包含类别（浓缩咖啡、特色饮品、糕点）",
    "关于部分，包含故事和价值观",
    "地址和营业时间，嵌入地图",
    "Instagram 画廊集成",
    "暖色调调色板（棕色、奶油色、咖啡色调）"
  ],
  "typography": {
    "primaryFont": "\"Playfair Display\", serif",
    "secondaryFont": "\"Lato\", sans-serif",
    "usage": "Playfair Display 用于优雅的标题，Lato 用于可读的正文",
    "fontImport": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap"
  }
}
```

### 示例 2：律师事务所

**用户提示：** "为我的律师事务所 Harrison & Associates 创建一个主题。我们专注于公司法和并购。非常专业、值得信赖的氛围。"

```json
{
  "siteBrief": {
    "siteName": "Harrison & Associates",
    "siteType": "律师事务所",
    "primaryGoal": "建立信誉并产生公司法服务的客户询问",
    "audience": "商业高管、公司决策者、寻求并购法律咨询的公司",
    "tone": "专业、权威、值得信赖、精致",
    "brandKeywords": "企业卓越、诚信、深蓝色、金色点缀、大理石纹理、简洁线条"
  },
  "layoutNotes": [
    "带有专业办公室图像或抽象企业图形的英雄区域",
    "业务领域部分，突出公司法和并购专业知识",
    "律师简介，包含资质和专长",
    "案例研究或知名交易（匿名化）",
    "来自商业领袖的客户评价",
    "联系部分，包含咨询预订",
    "色调调色板：深蓝色、白色、金色点缀"
  ],
  "typography": {
    "primaryFont": "\"Cormorant Garamond\", serif",
    "secondaryFont": "\"Source Sans Pro\", sans-serif",
    "usage": "Cormorant Garamond 用于声望显赫的标题，Source Sans Pro 用于专业的正文",
    "fontImport": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Source+Sans+Pro:wght@300;400;600&display=swap"
  }
}
```

### 示例 3：电子竞技团队

**用户提示：** "为 NeonPulse Gaming 创建一个主题——一个电子竞技团队。我们参加 FPS 游戏，想要一些边缘化和快速的风格。"

```json
{
  "siteBrief": {
    "siteName": "NeonPulse Gaming",
    "siteType": "电子竞技团队",
    "primaryGoal": "建立粉丝社区、吸引赞助商和招募有才华的选手",
    "audience": "游戏爱好者、电子竞技粉丝、潜在赞助商、有志成为职业游戏玩家的个人",
    "tone": "边缘化、高能量、竞争性、大胆",
    "brandKeywords": "霓虹光芒、赛博朋克、电光紫、亮粉色、深色背景、故障效果、速度线条"
  },
  "layoutNotes": [
    "带有团队动作照片或动态游戏视频背景的英雄区域",
    "选手名单，包含统计数据和社交链接",
    "比赛日程和直播集成",
    "比赛成绩和奖杯",
    "赞助商展示",
    "商品商店链接",
    "新闻/博客用于团队更新",
    "深色主题，带霓虹点缀（紫色、粉色、青色）"
  ],
  "typography": {
    "primaryFont": "\"Rajdhani\", sans-serif",
    "secondaryFont": "\"DM Sans\", sans-serif",
    "usage": "Rajdhani 用于侵略性技术标题，DM Sans 用于干净的阅读内容",
    "fontImport": "https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=DM+Sans:wght@300;400;600&display=swap"
  }
}
```

### 示例 4：最小请求

**用户提示：** "为我的博客构建一个自定义主题"

```json
{
  "siteBrief": {
    "siteType": "个人博客",
    "primaryGoal": "分享内容并建立读者群",
    "tone": "个人、友好"
  },
  "layoutNotes": [
    "带有精选文章或欢迎信息的英雄区域",
    "最近文章网格或列表",
    "关于作者部分",
    "分类/标签导航",
    "订阅通讯"
  ],
  "typography": {
    "primaryFont": "\"Outfit\", sans-serif",
    "secondaryFont": "\"Merriweather\", serif",
    "usage": "Outfit 用于干净的标题，Merriweather 用于舒适的阅读长格式",
    "fontImport": "https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Merriweather:wght@300;400;700&display=swap"
  }
}
```

## 展示格式

向用户展示提取的规格以供确认。除非调用命令指定不同的展示格式，否则使用以下表格格式：

| 字段 | 值 |
|-------|-------|
| 网站名称 | [名称] |
| 网站类型 | [类型] |
| 主要目标 | [目标] |
| 目标受众 | [受众] |
| 语气 | [语气] |
| 品牌关键词 | [关键词] |
| 关键部分 | [来自 layoutNotes 的逗号分隔列表] |
| 字体 | [primaryFont] + [secondaryFont] |

然后询问： "这捕捉到您的愿景了吗？在继续设计选项之前，请告诉我您是否希望调整任何内容。"
