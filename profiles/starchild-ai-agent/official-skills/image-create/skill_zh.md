# image-create

使用此技能处理 Starchild 上的所有**纯文本到图像生成请求**。

涵盖：标志设计、海报设计、插画、表情包创建、游戏资源、社交媒体内容、3D 渲染、教育插画、时装设计、食品摄影、宠物插画、婚礼设计、节日营销和艺术风格创建。

**核心原则**：调用提供的脚本。不要重新实现代理/计费管道。

**何时使用 image-create 而不是 image-portrait**：
- **image-create** → 用户想从文本描述中**创建**某物（不需要面部/身份）
- **image-portrait** → 用户想从参考照片中生成带有其面部/身份的肖像

---

## 1. 快速入门 — 基本生成（最常见）

> **⚠️ 执行上下文 — 首先阅读此内容。**
> 以下代码块是 **Python**，不是 shell 命令。Starchild 的 `bash` 工具运行 `/bin/bash -c`，无法解析 `exec(open(...))` — 将它们直接粘贴到 bash 命令中会导致 `语法错误 near unexpected token 'open'`。此外，`python3 -c` 中的 `exec(open(...))` 会因脚本使用 `__file__` 进行路径解析而失败。
>
> **通过 bash 工具调用时使用 `python3 - <<'EOF'` 与 `from exports import`**：
>
> ```bash
> python3 - <<'EOF'
> import sys
> sys.path.insert(0, "skills/image-create")
> from exports import generate_image
> result = generate_image(
>     prompt="a futuristic city skyline at sunset with flying cars",
> )
> print(result)
> EOF
> ```
>
> 她源文档 (`<<'EOF'`) 保留了所有引号和换行符 — 无需转义。

```python
exec(open('skills/image-create/generate_image.py').read())
result = generate_image(
    prompt="a futuristic city skyline at sunset with flying cars",
)
# result -> {"success": True, "images": [{"local_path": "output/images/..."}], ...}
```

## 2. 快速入门 — 带有类别预设

```python
exec(open('skills/image-create/generate_image.py').read())
result = generate_image(
    prompt="StarChild AI platform",
    category="logo",
    style="tech",
)
```

## 3. 快速入门 — 仅类别（无自定义提示）

```python
exec(open('skills/image-create/generate_image.py').read())
result = generate_image(
    category="3d",
    style="diorama",
)
# 使用内置样式模板作为完整提示
```

### 将结果交付给用户 — 重要

**绝对不要将原始 fal.media URL 交给用户。** fal 使用具有限制性 CSP 头部来提供文件。唯一可靠的交付路径是**已下载的本地文件**：

1. 使用每个图像的 `local_path`（例如 `output/images/xxx.png`）— 脚本在成功时始终下载。
2. 告知用户文件保存在 `output/images/` 中，并在工作区文件面板中可见。
3. 在 Web 渠道中，内联嵌入以便用户可以在聊天中预览：
   ```markdown
   ![image](output/images/<filename>.png)
   ```
4. 在 Telegram / WeChat：通过 `send_to_telegram(file_path="output/images/...", message_type="image")` 或 `send_to_wechat(file_path="output/images/...", message_type="image")` 发送。

---

## 4. 参数

| 参数 | 必填 | 默认 | 描述 |
|-------|------|------|------|
| `prompt` | 是* | — | 所需图像的文本描述 |
| `category` | 是* | — | 预设类别（见 §5） |
| `style` | 否 | `"default"` | 类别内的子样式（见 §5） |
| `model` | 否 | `"nanopro"` | 模型：`"nano2"`（最快 ~15s）、`"nanopro"`（平衡 ~25s，默认）或 `"gpt"`（最佳质量 ~150s） |
| `count` | 否 | `1` | 要生成的图像数量（1–4） |
| `aspect_ratio` | 否 | auto | 输出比例：`1:1`、`2:3`、`3:2`、`3:4`、`4:3`、`4:5`、`5:4`、`9:16`、`16:9`、`21:9`。如果没有设置，则由类别自动选择。 |
| `image_path` | 否 | — | 可选的参考/灵感图像的本地文件路径 |
| `image_url` | 否 | — | 可选的参考/灵感图像的公共 URL |

*至少需要提供 `prompt` 或 `category` 中的一个。

**提示优先级**：`prompt + category/style`（增强）> `prompt` 仅 > `category + style` > `category` 默认。

**宽高比自动选择**：如果没有显式设置，脚本将为类别选择最佳比例（例如，`1:1` 用于标志，`3:4` 用于海报，`16:9` 用于横幅）。

---

## 5. 类别和样式预设

### E: 设计 — 标志 (`category="logo"`)

> ⚠️ **AI 无法可靠地渲染文本。** 仅生成图标/符号；在 Figma、Canva 或 Illustrator 中添加文本/标志。

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 抽象几何 | `abstract` | 科技、概念品牌（Nike swoosh 风格） |
| 图形图标 | `pictorial` | 通用品牌、无需文本即可使用（Apple 风格） |
| 恶魔角色 | `mascot` | 友好的品牌、食品、体育（KFC 风格） |
| 科技公司 | `tech` | SaaS、AI、金融科技初创公司 |
| 食品品牌 | `food` | 餐厅、面包店、有机食品 |
| 时尚品牌 | `fashion` | 奢侈品、服装、美容 |
| 游戏 | `gaming` | 电子竞技、游戏工作室 |
| 一般 | `default` | 任何专业标志 |

**标志提示反模式（避免）**：
- ❌ `"标志带有文本 'Company Name'"` — 文本将被混乱
- ❌ `"照片级真实标志"` — 标志不是照片
- ❌ `"3D 渲染标志"` — 太复杂，无法缩小
- ✅ `"扁平矢量标志 of [主题]，极简几何风格，单色，白色背景"`

### E: 设计 — 海报 (`category="poster"`)

| 样式 | 关键 | 最佳用途 | 推荐宽高比 |
|------|------|----------|------------|
| 电影海报 | `movie` | 电影宣传、电影感 | 3:4 |
| 音乐节 | `music_festival` | 音乐会、节日 | 3:4 |
| 科技会议 | `tech_conference` | 科技活动、黑客马拉松 | 3:4 |
| 旅游目的地 | `travel` | 旅游、旅行渴望 | 3:4 |
| 产品发布 | `product_launch` | 产品公告 | 3:4 |
| 极简艺术 | `minimalist` | 家居装饰、画廊 | 3:4 |
| 体育赛事 | `sports` | 体育活动 | 3:4 |
| 一般 | `default` | 任何海报 | 3:4 |

### E: 设计 — 插画 (`category="illustration"`)

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 奇幻 | `fantasy` | 奇幻世界、魔法、龙 |
| 科幻 | `scifi` | 未来场景、太空 |
| 儿童书籍 | `children` | 儿童内容、故事书（3-5岁） |
| 编辑 | `editorial` | 杂志、文章标题 |
| 植物学 | `botanical` | 科学植物插图 |
| 一般 | `default` | 任何插图 |

### E: 设计 — 表情包 (`category="meme"`)

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 动物表情包 | `animal` | 可爱/搞笑的动物表情包 |
| 反应 | `reaction` | 反应模板 |
| 超现实 | `surreal` | 超现实主义互联网幽默 |
| 一般 | `default` | 任何表情包 |

### K: 游戏资源 (`category="game_asset"`)

| 样式 | 关键 | 最佳用途 | 常见尺寸 |
|------|------|----------|----------|
| 角色概念 | `character` | RPG 角色、英雄 | 1024x1024 |
| 环境 | `environment` | 游戏世界、关卡 | 1920x1080 |
| 武器/道具 | `weapon` | 道具、武器、神器 | 1024x1024 |
| UI 图标 | `ui_icon` | 游戏UI、移动图标 | 32x32 至 128x128 |
| 像素精灵 | `pixel_sprite` | 复古游戏角色 | 32x32 至 64x64 |
| 图案集 | `tileset` | 无缝环境瓦片 | 256x256 至 512x512 |
| 一般 | `default` | 任何游戏资源 | 1024x1024 |

### M: 社交媒体 (`category="social_media"`)

| 样式 | 关键 | 最佳用途 | 推荐宽高比 | 分辨率 |
|------|------|----------|------------|--------|
| Instagram 帖子 | `instagram` | IG 信息流帖子 | 1:1 | 1080x1080 |
| 小红书 | `xiaohongshu` | 小红书帖子 | 3:4 | 1080x1440 |
| TikTok 封面 | `tiktok_cover` | TikTok 缩略图 | 9:16 | 1080x1920 |
| YouTube 缩略图 | `youtube_thumbnail` | YT 缩略图 | 16:9 | 1280x720 |
| 横幅 | `banner` | Twitter/YouTube 横幅 | 16:9 | 1920x1080 |
| 故事 | `story` | IG/FB 故事 | 9:16 | 1080x1920 |
| 一般 | `default` | 任何社交内容 | 1:1 | 1024x1024 |

### N: 3D (`category="3d"`)

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 3D 角色 | `character` | 皮克斯风格角色 |
| 产品渲染 | `product` | 产品可视化 |
| 场景 | `diorama` | 微缩场景、等距 |
| 应用图标 | `icon` | iOS/Android 应用图标 |
| 3D 文本 | `text` | 豆沙/金属文本 |
| 3D 场景 | `scene` | 低多边形环境 |
| 一般 | `default` | 任何 3D 渲染 |

### P: 教育 (`category="education"`)

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 教科书 | `textbook` | 教科书插图 |
| 信息图表 | `infographic` | 数据可视化 |
| 科学 | `science` | 科学图表、解剖学 |
| 历史 | `history` | 历史场景重建 |
| 图表 | `diagram` | 技术流程图表 |
| 一般 | `default` | 任何教育内容 |

### Q: 时尚 (`category="fashion"`)

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 服装设计 | `clothing` | 衣物草图、时装图 |
| 配饰 | `accessory` | 珠宝、包、鞋 |
| 指甲艺术 | `nail_art` | 指甲设计 |
| 织物图案 | `textile` | 布料图案、表面设计 |
| 一般 | `default` | 任何时尚设计 |

### R: 食品 (`category="food"`)

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 菜品照片 | `dish` | 食品摄影、编辑 |
| 菜单设计 | `menu` | 餐厅菜单 |
| 包装 | `packaging` | 食品包装设计 |
| 食谱卡片 | `recipe_card` | 食谱插图 |
| 一般 | `default` | 任何食品内容 |

### S: 宠物 (`category="pet"`)

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 拟人宠物 | `humanized` | 穿衣服的宠物 |
| 文艺复兴 | `renaissance` | 皇家/贵族宠物肖像 |
| 卡通 | `cartoon` | 迪士尼/皮克斯风格的宠物 |
| 商品 | `merchandise` | 宠物主题产品图案 |
| 纪念 | `memorial` | 宠物纪念艺术品 |
| 一般 | `default` | 可爱的宠物插图 |

### I: 产品摄影 (`category="product"`)

> 源自产品摄影技能最佳实践。

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 主角照片 | `hero` | 主要产品图像、杂志广告 |
| 产品拍摄 | `packshot` | 电商列表、亚马逊（纯白色背景） |
| 生活方式 | `lifestyle` | 产品在环境中、编辑 |
| 扁平布局 | `flat_lay` | Instagram、自上而下排列 |
| 一般 | `default` | 任何产品照片 |

**产品摄影技巧**：
- 主角照片：产品占画面的 80%，轻微 15-30° 角度以增加维度
- 产品拍摄（亚马逊）：纯白色背景，产品占 85%+，无道具/文本/水印
- 始终指定照明：`"soft studio lighting"`、`"dramatic rim lighting"`
- 对于电商：`"sharp focus"`、`"no shadows"` 或 `"subtle shadow only"`

### Y: 婚礼 (`category="wedding"`)

| 样式 | 关键 | 最佳用途 | 格式 |
|------|------|----------|------|
| 经典邀请函 | `invitation` | 花哨优雅邀请函 | 5x7 英寸 |
| 现代邀请函 | `invitation_modern` | 极简邀请函 | 5x7 英寸 |
| 乡村邀请函 | `invitation_rustic` | 波西米亚邀请函 | 5x7 英寸 |
| 场地预览 | `venue` | 婚礼装饰预览 | — |
| 保存日期 | `save_the_date` | 预告卡片 | 4x6 英寸 |
| 一般 | `default` | 任何婚礼设计 | — |

### Z: 节日营销 (`category="holiday"`)

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 圣诞卡 | `christmas_card` | 圣诞祝福 |
| 春节 | `chinese_new_year` | 春节设计 |
| 新年 | `new_year` | 新年庆祝活动 |
| 情人节 | `valentines` | 情人节 |
| 万圣节 | `halloween` | 万圣节设计 |
| 促销 | `promotional` | 销售横幅、促销 |
| 中秋节 | `mid_autumn` | 中秋节设计 |
| 一般 | `default` | 任何节日内容 |

**主要节日日历用于活动规划**：

| 节日 | 时间 | 最佳用途 |
|------|------|----------|
| 春节 | 1 月-2 月 | 礼物、家庭、食品 |
| 情人节 | 2 月 14 日 | 浪漫、礼物 |
| 妇女节 | 3 月 8 日 | 权力、礼物 |
| 520 (5 月 20 日) | 5 月 20 日 | 浪漫（中国情人节） |
| 618 电商 | 6 月 | 重大销售 |
| 七夕 | 7 月-8 月 | 浪漫 |
| 中秋节 | 9 月 | 家庭、月饼 |
| 国庆节 | 10 月 1 日 | 旅行、购物 |
| 11.11 单身节 | 11 月 11 日 | 重大销售 |
| 12.12 双 12 | 12 月 12 日 | 年终销售 |
| 圣诞节 | 12 月 25 日 | 礼物、冬季 |

### C: 艺术风格 (`category="art_style"`)

| 样式 | 关键 | 最佳用途 |
|------|------|----------|
| 吉卜力 | `ghibli` | 吉卜力风格场景 |
| 美国漫画 | `american_comic` | 漫威/DC 风格 |
| 日本漫画 | `manga` | 漫画插图 |
| 像素艺术 | `pixel_art` | 复古游戏风格 |
| 铅笔素描 | `pencil_sketch` | 手绘外观 |
| 3D 卡通 | `3d_cartoon` | 皮克斯/迪士尼风格 |
| 蒸汽朋克 | `steampunk` | 维多利亚科幻 |
| 奇幻魔法 | `fantasy_magic` | 魔法场景 |
| 武侠/仙侠 | `wuxia` | 中国武术 |
| 太空/科幻 | `scifi_space` | 太空场景 |
| 波普艺术 | `pop_art` | 波普风格 |
| 浮世绘 | `ukiyo_e` | 日本木版画 |
| 印象派 | `impressionist` | 梵高/莫奈风格 |
| 新艺术运动 | `art_nouveau` | 新艺术风格 |
| 最高质量 | any | any + `model="gpt"` |
| 预设之外的描述 | — | — | 使用 `prompt=` 直接 |

---

## 6. 模型选择指南

| 模型 | 关键 | 速度 | 质量 | 最佳用途 |
|------|------|------|------|----------|
| NanoPro | `nanopro` | ~25s | 良好 | 默认所有请求。快速迭代。 |
| GPT Image 2 | `gpt` | ~150s | 最佳 | 用户明确要求“最高质量”或“最佳质量”。文本密集型设计。 |

**决策规则**：
1. **默认**：除非用户明确要求更高质量，否则始终使用 `nanopro`。
2. **使用 `gpt` 当**：用户说“最高质量”、“最佳质量”、“premium”，或设计需要精确文本渲染（带有特定文本的标志、带有排版的海报）。
3. **使用 `nanopro` 当**：用户想要快速结果，正在迭代设计，或生成多个变体。

```python
# 默认（快速）
result = generate_image(prompt="cute cat logo", category="logo")

# 高质量（用户要求）
result = generate_image(prompt="cute cat logo", category="logo", model="gpt")
```

---

## 7. 宽高比指南

| 类别 | 默认宽高比 | 备注 |
|------|------------|-------|
| 标志 | 1:1 | 方形，可缩放 |
| 海报 | 3:4 | 竖屏方向 |
| 插画 | 4:3 | 横屏，宽场景 |
| 表情包 | 1:1 | 方形，可分享 |
| 游戏资源 | 1:1 | 方形，一致 |
| 社交媒体 | 1:1 | 各平台不同 |
| 3D | 1:1 | 方形渲染 |
| 教育 | 4:3 | 横屏，可读 |
| 时尚 | 3:4 | 竖屏，完整服装 |
| 食品 | 4:3 | 横屏，诱人 |
| 宠物 | 1:1 | 方形，可爱 |
| 产品 | 1:1 | 方形，电商 |
| 婚礼 | 3:4 | 竖屏，优雅 |
| 节日 | 4:3 | 横屏，节日气氛 |
| 艺术风格 | 4:3 | 横屏，风景 |

**平台特定覆盖（自动应用）**：
- TikTok 封面 → `9:16` (1080x1920)
- Instagram 故事 → `9:16` (1080x1920)
- YouTube 缩略图 → `16:9` (1280x720)
- 社交媒体横幅 → `16:9` (1920x1080)
- 小红书 → `3:4` (1080x1440)

当 `aspect_ratio` 未显式设置时，脚本将选择类别的最佳比例。

---

## 8. 提示工程最佳实践

### 5 元素提示结构

每个有效的图像提示都应包括：

```
[主题/内容], [风格/美学], [构图/布局], [照明/氛围], [质量修饰符]
```

### 关键原则

1. **具体说明主题**：
   - ❌ "一个标志"
   - ✅ "为宠物美容店 Bean Dream 设计极简猫形标志，干净矢量风格"

2. **指定视觉风格**：
   - "扁平设计", "3D 渲染", "水彩画", "照片级真实"
   - "极简", "详细", "抽象", "几何"

3. **包含构图指导**：
   - "居中构图", "三分法", "对称布局"
   - "特写", "广角", "等距视图", "鸟瞰视图"

4. **照明很重要**：
   - 工作室：`"soft diffused studio lighting"`, `"Rembrandt chiaroscuro"`
   - 自然：`"golden hour warm light"`, `"dappled sunlight through trees"`
   - 戏剧性：`"dramatic rim lighting"`, `"volumetric light beams"`, `"neon glow"`
   - 扁平：`"even flat lighting with no shadows"`（用于图标/图表）

5. **质量锚点**：
   - "专业质量", "可打印", "4K 分辨率"
   - "octane render", "Unreal Engine 质量", "杂志质量"

6. **图像中的文本（使用 `gpt` 模型）**：
   - 明确声明文本：`text reading "SALE 50% OFF"`
   - 指定字体样式：`"bold sans-serif typography"`, `"elegant script font"`
   - GPT 模型比 `nanopro` 更好地处理文本渲染

### 标志特定提示技巧（来自 logo-design-guide）

**有效关键词**：
```
flat vector logo, simple minimal icon, single color silhouette,
geometric logo mark, clean lines, negative space design,
line art logo, flat design icon, minimalist symbol
```

**无效关键词**：
```
❌ 照片级真实标志（矛盾 — 标志不是照片）
❌ 3D 渲染标志（太复杂，无法缩小）
❌ 渐变标志（结果不一致，难以重现）
❌ 带有文本 "Company Name" 的标志（文本渲染失败）
```

**标志提示结构**：
```
flat vector logo of [主题], [风格], [颜色限制], [背景], [附加细节]
```

### 儿童插画技巧（来自 book-illustrator）

- **0-2 岁**：简单，粗体，高对比度，清晰形状
- **3-5 岁**：多彩，表达，吸引人的角色，有动作
- **6-8 岁**：更详细的场景，有视觉故事讲述
- **9-12 岁**：复杂的插图，支持文本
- **3 色规则**：每个角色限制为 3-4 种主要颜色，以便视觉清晰

### 游戏资源技巧（来自 game-asset-generation）

- 始终指定像素尺寸对于精灵：`"32x32"`, `"64x64"`, `"128x128"`
- 对于无缝纹理：`"must tile perfectly with no visible seams when repeated"`
- 对于精灵表：指定网格布局 "4x2 grid (256x64 total)"
- 对于图标：`"clear silhouette readable at 32x32 pixels"`

### 示例：构建自定义提示

用户：为我的咖啡店 Bean Dream 设计一个标志

```python
result = generate_image(
    prompt=(
        "flat vector logo of a coffee bean morphing into a crescent moon, "
        "minimalist design, warm brown and cream color palette, "
        "clean lines, white background, "
        "professional branding quality, works at any size"
    ),
    category="logo",
    model="gpt",  # GPT for better detail
)
```

### 示例：游戏角色概念

用户：为我的 RPG 游戏创建一个战士角色

```python
result = generate_image(
    prompt=(
        "female warrior character, ornate golden armor with dragon motifs, "
        "flowing red cape, wielding a glowing enchanted sword, "
        "determined fierce expression, battle-ready stance, "
        "front view T-pose, clean white background"
    ),
    category="game_asset",
    style="character",
)
```

### 示例：社交媒体内容

用户：制作关于烹饪技巧的 TikTok 封面

```python
result = generate_image(
    prompt=(
        "cooking tips video thumbnail, colorful kitchen scene, "
        "fresh ingredients flying in the air, chef's hands visible, "
        "fun energetic vibe, bold visual impact"
    ),
    category="social_media",
    style="tiktok_cover",
    # aspect_ratio auto-set to 9:16
)
```

---

## 9. 意图识别指南

使用此表格将用户请求映射到正确的类别/样式/参数：

| 用户说 | 类别 | 样式 | 备注 |
|--------|------|------|------|
| "设计一个标志", "制作一个标志" | `logo` | auto-detect | 询问行业以确定样式 |
| "创建一个海报", "活动海报" | `poster` | auto-detect | |
| "绘制一个插画", "插画" | `illustration` | auto-detect | |
| "制作一个表情包", "搞笑图像" | `meme` | auto-detect | |
| "游戏角色", "RPG 资源" | `game_asset` | `character` | |
| "游戏环境", "关卡设计" | `game_asset` | `environment` | |
| "武器设计", "剑/盾" | `game_asset` | `weapon` | |
| "游戏图标", "UI 图标" | `game_asset` | `ui_icon` | |
| "像素精灵" | `game_asset` | `pixel_sprite` | |
| "图集" | `game_asset` | `tileset` | |
| 一般 | `default` | 任何游戏资源 | |

**平台特定覆盖（自动应用）**：
- TikTok 封面 → `9:16` (1080x1920)
- Instagram 故事 → `9:16` (1080x1920)
- YouTube 缩略图 → `16:9` (1280x720)
- 社交媒体横幅 → `16:9` (1920x1080)
- 小红书 → `3:4` (1080x1440)

当参考图像提供时，脚本使用 `/edit` 端点而不是生成端点。

---

## 10. 使用参考图像（可选）

虽然此技能主要是文本到图像，但您可以提供一个参考图像以获取设计灵感：

```python
# 参考图像用于设计指导
result = generate_image(
    prompt="redesign this logo in a modern minimalist style",
    category="logo",
    image_path="uploads/old_logo.png",
)

# 参考图像 URL
result = generate_image(
    prompt="创建一个类似风格的插图，但主题为森林",
    image_url="https://example.com/reference.jpg",
)
```

当提供参考图像时，脚本使用 `/edit` 端点而不是生成端点。

---

## 11. 多个图像

```python
# 生成 4 个标志变体
result = generate_image(
    prompt="极简山脉标志，户外品牌",
    category="logo",
    count=4,
)
# result["images"] -> list of 4 image dicts
```

---

## 12. 反模式（避免这些）

| 避免 | 原因 | 替代方案 |
|------|------|---------|
| `"logo with text 'My Brand'"` | AI 混乱文本 | 生成图标仅，在 Figma/Canva 中添加文本/标志 |
| `"photorealistic logo"` | 标志不是照片 | 使用 "flat vector logo" |
| `"3D rendered logo"` | 无法缩小到 favicons | 使用 "flat minimal icon" |
| 模糊的提示 | 结果很差 | 具体说明主题、样式、颜色、照明 |
| 在一个提示中包含太多概念 | 输出混乱 | 专注于一个清晰的概念 |
| 请求精确像素尺寸 | 不支持 | 使用 `aspect_ratio` 参数 |
| 使用 `nanopro` 进行文本密集型设计 | 文本渲染差 | 切换到 `model="gpt"` — GPT 处理文本更好 |

---

## 13. 提供的脚本

| 文件 | 目的 |
|------|------|
| `generate_image.py` | 核心脚本：提示构建 → 提交 → 汇报 → 下载。处理所有类别、样式、两个模型。 |
| `exports.py` | 重新导出 `generate_image`, `CATEGORY_STYLES`, `MODELS` 以便程序使用。 |
| `_cost_track.py` | 成本跟踪辅助程序 — 通过 sc-proxy 头部记录每次调用的成本。自包含，无外部依赖。 |

---

## 14. 本地测试

设置 `FAL_KEY` 环境变量以直接调用 fal.ai（绕过 sc-proxy）：

```bash
# 基本生成
FAL_KEY=your-fal-key-12345 python3 skills/image-create/generate_image.py "a cute robot" illustration fantasy 1 nanopro

# 参数：<提示> [类别] [样式] [数量] [模型]
```

---

## 15. 故障排除

| 问题 | 修复 |
|------|------|
| `Either 'prompt' or 'category' must be provided` | 提供 `prompt` 或 `category` 中至少一个 |
| `File not found: ...` | 检查工作区路径以获取参考图像 |
| `Unsupported image format` | 使用 `.jpg`, `.jpeg`, `.png`, `.webp`, 或 `.bmp` |
| `Image too large` | 调整参考图像以小于 10 MB |
| `HTTP 402 insufficient_credits` | 充值余额；成本在提交时预扣 |
| `HTTP 403 endpoint_not_allowed` | sc-proxy 仅允许批准的 fal 端点；请联系管理员 |
| 上游生成失败 | 简化提示，重试 |
| 任务卡 `IN_PROGRESS` >10 分钟 | 保存 `request_id`，稍后重试 |
| 文本渲染不佳 | 切换到 `model="gpt"` — GPT 处理文本更好 |
| `gpt` 模型太慢 | 切换到 `nanopro`（默认）以获得更快的结果 |
| 标志过于复杂无法缩放 | 使用 "flat vector", "minimal", "single color" 在提示中 |
| 无缝纹理有可见接缝 | 添加 "must tile perfectly with no visible seams" 到提示 |

---

## 16. 基础设施（参考）

- 调用者 → `sc-proxy` → `queue.fal.run/{model}` → fal 模型提供者
- 所有请求都必须包含 `Authorization: Key fake-falai-key-12345`（代理注入真实的 `FAL_KEY`）
- 提交时发生预扣。轮询/结果调用是免费的。
- 最终图像位于 `https://*.fal.media/...` — 公共 CDN，下载时无需身份验证。
- 成本跟踪通过 `_cost_track.py` — 记录 `X-Credits-Used` 从 sc-proxy 响应头部。
- 每个技能都包含自己的 `_cost_track.py` 副本（技能独立部署）。

### 模型端点

| 模型 | 生成（仅文本） | 编辑（带有参考图像） |
|------|----------------|----------------------|
| nanopro | `fal-ai/nano-banana-pro` | `fal-ai/nano-banana-pro/edit` |
| gpt | `openai/gpt-image-2` | `openai/gpt-image-2/edit` |

---
