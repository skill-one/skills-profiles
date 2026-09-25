# 海报设计生成

使用each::sense生成令人惊叹、专业的海报设计。这项技能为电影、活动、产品、旅行、体育、社会公益和各种创意应用创建高质量的海报艺术作品。

## 功能特性

- **电影海报**：具有戏剧性构图和排版空间的影视关键艺术
- **活动/音乐会海报**：引人注目的活动宣传材料
- **励志海报**：具有冲击力图像的鼓舞人心设计
- **产品发布海报**：用于产品发布的商业视觉效果
- **极简艺术海报**：简洁、现代美学设计
- **复古/怀旧海报**：来自不同时代的经典风格
- **旅行目的地海报**：旅游和旅行渴望激发的视觉效果
- **体育赛事海报**：动态的体育赛事宣传材料
- **教育/信息图表海报**：信息丰富的视觉设计
- **社会公益海报**：意识和倡导活动视觉效果

## 快速入门

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "创建一个科幻惊悚片的戏剧性电影海报，暗色调氛围，霓虹灯点缀，顶部留出空间用于标题"}],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

## 常见海报尺寸与格式

| 类型 | 宽高比 | 推荐尺寸 | 用途 |
|------|--------|----------|------|
| 电影海报 | 2:3 | 1080x1620 | 影院海报，关键艺术 |
| 活动海报 | 11:17 | 1100x1700 | 音乐会传单，活动宣传 |
| 方形海报 | 1:1 | 1080x1080 | 社交媒体，专辑封面 |
| 水平海报 | 16:9 | 1920x1080 | 数字显示屏，横幅 |
| 垂直海报 | 9:16 | 1080x1920 | 手机，数字标牌 |
| A系列 | ~1:1.414 | 2480x3508 (A4) | 打印海报 |

## 用例示例

### 1. 电影海报设计

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "创建一个2:3的心理惊悚片电影海报。一个男子剪影站在雾蒙蒙的悬崖边缘，阴郁的蓝灰色调，电影感光效与戏剧性阴影。在顶部三分之一处留出空间用于电影标题，在底部留出空间用于片尾字幕。好莱坞大片品质。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 2. 活动/音乐会海报

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "设计一个11:17的电子音乐节音乐会海报。鲜艳的霓虹色，抽象的几何形状，激光束和光效，赛博朋克美学。在顶部留出视觉空间用于艺术家名称，在底部留出空间用于活动详情。高能量，派对文化氛围。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 3. 励志海报

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "创建一个鼓舞人心的励志海报。一个孤独的登山者于日出时分登顶山峰，金色的阳光穿透云层，壮丽的景观视野。垂直2:3格式，底部留出空间用于励志语录。令人敬畏，充满胜利氛围。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 4. 产品发布海报

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "设计一张新智能手机的时尚产品发布海报。手机悬浮在中心，周围有动态光迹和粒子效果，深色高端背景带有微妙渐变。现代科技美学，苹果风格的极简主义。2:3垂直格式，留出空间用于产品名称和标语。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 5. 极简艺术海报

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "创建一张斯堪的纳维亚风格的极简艺术海报。简单的几何形状，陶土色、鼠尾草绿和奶油色的有限调色板。抽象构图暗示着风景。简洁的线条，适合家居装饰的现代美学。3:4垂直格式。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 6. 复古/怀旧海报

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "设计一张复古1950年代旅行海报风格的美术作品。经典的美国餐厅场景，霓虹灯招牌，铬细节和经典汽车。复古调色板，褪色的粉彩色，中世纪插画风格，可见的笔触。包含典型的装饰边框。2:3格式。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 7. 旅行目的地海报

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "创建一张关于东京，日本的旅行海报。前景有樱花，远处有富士山，传统寺庙与现代摩天大楼混合。温暖的日落色调，梦幻般的旅行渴望美学。装饰艺术旅行海报风格，形状大胆。2:3垂直格式，底部留出空间用于目的地名称。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 8. 体育赛事海报

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "设计一张动态的篮球锦标赛海报。球员在空中扣篮的动作镜头，爆炸性的能量，运动模糊和粒子效果，戏剧性的体育场灯光。深蓝和橙色的鲜艳色彩。高对比度，激烈的竞争精神。11:17格式，留出空间用于活动标题和日期。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 9. 教育/信息图表海报

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "创建一张关于太阳系的教育海报。太阳系行星围绕太阳运行的视觉震撼表现，准确的相对大小和颜色，太空背景带有星星和星云。科学但视觉吸引人，适合教室或博物馆。16:9水平格式，有区域用于行星标签。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

### 10. 社会公益/意识海报

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "设计一张关于海洋保护的环境意识海报。一只美丽的海龟在清澈的水中游泳，但背景中有微妙的污染暗示。情感丰富，引人深思的图像，激发行动。蓝绿色调。2:3垂直格式，留出空间用于活动信息。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max"
  }'
```

## 最佳实践

### 构图与布局

- **排版空间**：始终请求为标题、副标题和文本叠加留出空间
- **安全区域**：为打印出血和重要内容留出边距
- **焦点**：定义清晰的可视层次结构和视觉中心
- **平衡**：指定您想要对称或不对称的构图

### 视觉风格

- **调色板**：提及特定颜色或基于情绪的调色板（温暖、冷色、鲜艳、柔和）
- **光照**：描述光照方向、质量和氛围
- **风格参考**：参考艺术运动、时代或特定设计风格
- **纹理**：请求特定纹理（颗粒、噪声、纸张、数字干净）

### 格式指南

- **宽高比**：始终指定您所需的宽高比（2:3、11:17、1:1等）
- **分辨率**：打印需要更高分辨率，标准分辨率用于数字
- **方向**：垂直（肖像）是大多数海报的标准

## 海报设计提示

在创建海报设计时，请在提示中包含以下详细信息：

1. **目的**：海报用于什么？（电影、活动、产品等）
2. **格式**：指定宽高比（2:3、11:17、1:1等）
3. **风格**：艺术风格或时代（极简主义、复古、现代等）
4. **主题**：主要视觉元素和构图
5. **调色板**：特定颜色或基于情绪的调色板
6. **排版空间**：文本将放置的位置
7. **情绪/氛围**：设计的情绪基调

### 示例提示结构

```
"创建一个[格式/宽高比][类型]海报用于[目的]。
[主要主题和构图的视觉描述]。
[风格和美学参考]。
[调色板和光照]。
在[位置]留出空间用于[文本元素]。"
```

## 模式选择

在生成前询问用户：

**"您想要快速且便宜，还是高质量？"**

| 模式 | 适合 | 速度 | 质量 |
|------|------|------|------|
| `max` | 最终海报设计，印刷准备好的艺术作品 | 较慢 | 最高 |
| `eco` | 快速草稿，概念探索，风格测试 | 较快 | 良好 |

## 多轮创意迭代

使用`session_id`迭代海报设计：

```bash
# 初始概念
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "创建一个恐怖电影的 movie poster，暗色调森林环境，有雾"}],
    "model": "eachsense/beta",
    "stream": true,
    "session_id": "horror-poster-001",
    "mode": "max"
  }'

# 优化设计
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "在背景中添加一座阴森的废弃房屋，并将调色板改为红色和黑色"}],
    "model": "eachsense/beta",
    "stream": true,
    "session_id": "horror-poster-001"
  }'

# 请求变体
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "创建2个不同的构图变体 - 一个更极简，一个更强烈"}],
    "model": "eachsense/beta",
    "stream": true,
    "session_id": "horror-poster-001"
  }'
```

## 海报系列生成

为活动生成一致的海报系列：

```bash
# 系列海报1
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "创建4张海报中的第1张，用于夏季音乐节系列。海滩日落主题，鲜艳的橙色和粉色。展示DJ剪影。" }],
    "model": "eachsense/beta",
    "stream": true,
    "session_id": "festival-series-2024",
    "mode": "max"
  }'

# 系列海报2（保持一致性）
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "创建4张海报中的第2张，使用相同的系列。相同的调色板和风格，但舞台上有乐队。" }],
    "model": "eachsense/beta",
    "stream": true,
    "session_id": "festival-series-2024"
  }'
```

## 使用参考图像

使用参考图像增强海报生成：

```bash
curl -X POST https://eachsense-agent.core.eachlabs.run/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EACHLABS_API_KEY" \
  -H "Accept: text/event-stream" \
  -d '{
    "messages": [{"role": "user", "content": "使用这张演员照片作为主要角色创建一个 movie poster。黑色电影风格，高对比度黑白，带有一个强调色（红色）。添加雨效和背景城市剪影。" }],
    "model": "eachsense/beta",
    "stream": true,
    "mode": "max",
    "image_urls": ["https://example.com/actor-portrait.jpg"]
  }'
```

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `Failed to create prediction: HTTP 422` | 余额不足 | 在 eachlabs.ai 充值 |
| 内容政策违规 | 限制内容 | 调整提示以符合内容政策 |
| 超时 | 复杂生成 | 将客户端超时设置为至少10分钟 |

## 相关技能

- `each-sense` - 核心API文档
- `meta-ad-creative-generation` - 社交媒体广告创意
- `product-photo-generation` - 电商产品照片
- `image-generation` - 一般图像生成
