# image-portrait

在 Starchild 上，使用此技能处理所有**身份一致性肖像生成请求**。

涵盖范围：专业头像、约会/社交照片、艺术风格转换、主题/节日肖像、照片系列、数字头像、儿童/家庭照片、身份证/护照照片。

**核心原则**：调用提供的脚本。不要重新实现代理/计费管道。

---

## 1. 快速入门 — 单个肖像（最常见）

> **⚠️ 执行上下文 — 首先阅读此内容。**
> 以下代码块是 **Python**，不是 shell 命令。Starchild 的 `bash` 工具
> 运行 `/bin/bash -c`，无法解析 `exec(open(...))` — 直接将它们粘贴到 bash 命令中会导致 `语法错误 near unexpected token 'open'`。
> 此外，`exec(open(...))` 在 `python3 -c` 中失败，因为脚本使用 `__file__` 进行路径解析。
>
> **通过 bash 工具调用时，使用 `python3 - <<'EOF'` 并配合 `from exports import`：**
>
> ```bash
> python3 - <<'EOF'
> import sys
> sys.path.insert(0, "skills/image-portrait")
> from exports import generate_portrait
> result = generate_portrait(
>     image_path="path/to/user/photo.jpg",
>     style="professional",
> )
> print(result)
> EOF
> ```
>
> 她源文档 (`<<'EOF'`) 保留了所有引号和换行符 — 无需转义。

```python
exec(open('skills/image-portrait/generate_portrait.py').read())
result = generate_portrait(
    image_path="path/to/user/photo.jpg",
    style="professional",
)
# result -> {"success": True, "images": [{"local_path": "output/images/..."}], ...}
```

脚本读取本地文件，将其 base64 编码，然后作为数据 URI 发送到 fal.ai — 无需手动发布 URL。

## 2. 快速入门 — 公开 URL

```python
exec(open('skills/image-portrait/generate_portrait.py').read())
result = generate_portrait(
    face_image_url="https://example.com/photo.jpg",
    style="anime",
)
```

## 3. 快速入门 — 文本到图像（无需参考照片）

```python
exec(open('skills/image-portrait/generate_portrait.py').read())
result = generate_portrait(
    prompt="a young woman in cyberpunk armor, neon city background, rain",
    model="nanopro",
)
```

当未提供 `image_path` 或 `face_image_url` 时，脚本使用文本到图像端点（无 `/edit` 后缀）。

### 将结果交付给用户 — 重要提示

**绝对不要直接将用户 fal.media URL。** fal 使用限制性 CSP 头部服务文件。唯一可靠的交付路径是**已下载的本地文件**：

1. 使用每个图像的 `local_path`（例如 `output/images/xxx.png`）— 脚本在成功时始终下载。
2. 告知用户文件保存在 `output/images/`，可在工作区文件面板中查看。
3. 在 Web 渠道中，内嵌以使用户可在聊天中预览：
   ```markdown
   ![photo](output/images/<filename>.png)
   ```
4. 在 Telegram / WeChat：通过 `send_to_telegram(file_path="output/images/...", message_type="image")` 或 `send_to_wechat(file_path="output/images/...", message_type="image")` 发送。

---

## 4. 参数

| 参数 | 必填 | 默认 | 描述 |
|-----------|----------|---------|-------------|
| `image_path` | 否 | — | 用户面部照片的本地工作区文件路径 |
| `face_image_url` | 否 | — | 用户面部照片的公共 HTTPS URL |
| `style` | 否 | `"professional"` | 预设风格键（见 §5） |
| `scene` | 否 | `None` | 自定义场景描述（附加到风格提示） |
| `prompt` | 否 | `None` | 完全自定义提示 — 设置时覆盖风格+场景 |
| `model` | 否 | `"nanopro"` | 模型：`"nano2"`（最快 ~15s）、`"nanopro"`（平衡 ~25s，默认）或 `"gpt"`（最佳质量 ~150s） |
| `count` | 否 | `1` | 生成的图像数量（1–8） |
| `aspect_ratio` | 否 | `"1:1"` | 输出比例：`1:1`、`3:4`、`4:3`、`9:16`、`16:9` |

**图像输入规则：**
- 提供 `image_path` OR `face_image_url` 以进行身份一致性生成（编辑模式）。
- 如果两者都提供，`image_path` 优先。
- 两者都省略，则为纯文本到图像生成（生成模式）。

**提示优先级：** `prompt` > `style + scene` > `style` > 默认 (`professional`)。

---

## 5. 风格预设

### A: 身份一致性角色风格

| 风格 | 键 | 最适合 |
|-------|-----|----------|
| 专业头像 | `professional` | LinkedIn、简历、企业 |
| 艺术肖像 | `artistic` | 创意作品集、画廊 |
| 动漫 | `anime` | 社交媒体、趣味头像 |
| 赛博朋克 | `cyberpunk` | 游戏资料、科幻爱好者 |
| 油画 | `oil_painting` | 艺术礼物、古典外观 |
| 水彩 | `watercolor` | 柔和艺术肖像 |
| 复古 | `vintage` | 复古美学、怀旧 |
| 休闲生活方式 | `casual` | 社交媒体、个人博客 |

### B: 个人展示 / 约会 / 社交

| 风格 | 键 | 最适合 |
|-------|-----|----------|
| 约会 — 咖啡馆 | `dating_cafe` | 约会应用、温暖氛围 |
| 约会 — 海滩 | `dating_beach` | 约会应用、夏季氛围 |
| 约会 — 城市 | `dating_city` | 约会应用、都市氛围 |
| 约会 — 餐厅 | `dating_restaurant` | 约会应用、优雅氛围 |
| 旅行 — 欧洲 | `travel_europe` | 旅行博客、社交媒体 |
| 旅行 — 日本 | `travel_japan` | 旅行博客、文化 |
| 旅行 — 热带 | `travel_tropical` | 度假、度假村 |
| 运动 — 健身房 | `sports_gym` | 健身资料 |
| 运动 — 跑步 | `sports_running` | 运动资料 |
| 社交媒体 | `social_media` | Instagram、TikTok |
| LinkedIn | `linkedin` | 职业社交 |
| 个人品牌 | `personal_brand` | 企业家、创作者 |

### D: 主题 / 场景肖像

| 风格 | 键 | 最适合 |
|-------|-----|----------|
| 圣诞节 | `christmas` | 节日问候、社交 |
| 万圣节 | `halloween` | 节日乐趣 |
| 毕业 | `graduation` | 里程碑庆祝 |
| 婚礼 | `wedding` | 婚礼策划、定情信 |
| 商业演讲 | `business_speech` | 演讲者资料 |
| 音乐家 | `musician` | 音乐推广 |
| 厨师 | `chef` | 食物博客、餐厅 |
| 户外探险 | `outdoor_adventure` | 探险博客 |
| 一起宠物 | `pet_together` | 宠物爱好者资料 |
| 阅读 | `reading` | 书友会、文学 |
| 夜城 | `night_city` | 都市生活方式 |
| 汉服（中国传统） | `hanfu` | 文化、角色扮演 |

### O: 数字头像

| 风格 | 键 | 最适合 |
|-------|-----|----------|
| 3D 卡通 | `avatar_3d` | 社交头像、皮克斯风格 |
| 游戏头像 | `avatar_gaming` | 游戏资料、RPG |
| VTuber | `avatar_vtuber` | 直播、VTuber |

### T: 儿童 & 家庭

| 风格 | 键 | 最适合 |
|-------|-----|----------|
| 儿童肖像 | `child_portrait` | 家庭纪念 |
| 家庭照片 | `family_photo` | 家庭肖像 |

### U: 身份证 / 护照照片

| 风格 | 键 | 最适合 |
|-------|-----|----------|
| 身份证照片（白色背景） | `id_photo_white` | 护照、驾照 |
| 身份证照片（蓝色背景） | `id_photo_blue` | 签证、工作许可 |

---

## 6. 模型选择指南

| 模型 | 键 | 速度 | 质量 | 最适合 |
|-------|-----|-------|---------|----------|
| Nano Banana 2 | `nano2` | ~15s | 良好 | 快速草稿、快速迭代、批量生成。 |
| NanoPro | `nanopro` | ~25s | 更好 | 所有请求的默认值。速度和质量平衡。 |
| GPT Image 2 | `gpt` | ~150s | 最佳 | 当用户明确要求“最高质量”或“最佳质量”时。复杂场景。 |

**决策规则：**
1. **默认：** 除非用户明确要求，否则始终使用 `nanopro`。
2. **使用 `nano2` 当：** 用户想要最快结果、正在迭代风格、生成许多图像，或说“快速”、“草稿”、“快”。
3. **使用 `gpt` 当：** 用户说“最高质量”、“最佳质量”、“高级”，或场景非常复杂且有许多特定细节。

```python
# 默认（快速）
result = generate_portrait(image_path="photo.jpg", style="anime")

# 高质量（用户请求）
result = generate_portrait(image_path="photo.jpg", style="anime", model="gpt")
```

---

## 7. 自定义场景示例

```python
# 风格 + 自定义场景
result = generate_portrait(
    image_path="uploads/my_photo.jpg",
    style="professional",
    scene="in a modern office with city skyline view",
)

# 仅自定义场景（默认为专业风格基础）
result = generate_portrait(
    image_path="uploads/my_photo.jpg",
    scene="standing on a beach at sunset, golden hour lighting",
)

# 完全自定义提示（覆盖所有）
result = generate_portrait(
    image_path="uploads/my_photo.jpg",
    prompt="portrait of a person as a medieval knight, full plate armor, castle background, dramatic lighting, oil painting style",
)

# 不同宽高比
result = generate_portrait(
    image_path="uploads/my_photo.jpg",
    style="cyberpunk",
    aspect_ratio="9:16",
)

# 多个图像
result = generate_portrait(
    image_path="uploads/my_photo.jpg",
    style="dating_cafe",
    count=4,
)
```

---

## 8. 提示工程最佳实践

当用户的请求不匹配任何预设风格，或需要构建自定义 `prompt` 时，请遵循以下指南（源自参考技能：ai-headshot-generation、ai-avatar-generation、style-transfer、portrait-enhancement、character-design-sheet、avatar-portrait、nano-banana-pro、pet-portrait-generation）。

### 自动相似度保留

当提供参考图像时（编辑模式），脚本**自动添加**相似度保留指令到每个提示。这确保生成的肖像保留主体的面部身份。您**不需要**手动添加相似度指令 — 脚本会处理。

例外：头像风格 (`avatar_3d`、`avatar_gaming`、`avatar_vtuber`) 跳过相似度前缀，因为风格化优先于照片相似度。

### 7 元素提示结构

每个有效的肖像提示都应包含这些元素（来自 nano-banana-pro 技能）：

```
[主体], [服装/装扮], [姿势/动作], [表情], [背景/场景], [光线], [风格/质量修饰符]
```

### 关键原则

1. **相似度与风格平衡**（来自 avatar-portrait 技能）：
   - 过于逼真 = 忽略请求的风格
   - 过于风格化 = 失去与源人物的相似度
   - 对于风格化肖像：强调“风格化但保留个体特征”
   - 对于逼真肖像：强调“保留面部特征可识别”

2. **光线至关重要** — 始终指定光线类型：
   - 工作室：`"soft diffused studio lighting"`, `"Rembrandt chiaroscuro lighting"`
   - 自然：`"golden hour warm light"`, `"dappled sunlight through trees"`
   - 戏剧性：`"dramatic rim lighting"`, `"volumetric light beams"`, `"neon glow"`
   - 平面：`"even flat lighting with no shadows"`（用于身份证照片）

3. **背景具体性** — 模糊的背景会导致糟糕的结果：
   - ❌ "nice background"
   - ✅ "blurred modern office with glass windows and city view"
   - ✅ "clean neutral gray gradient studio background"
   - ✅ "background style should match the character style"（用于头像）

4. **镜头/相机提示** — 帮助模型理解构图：
   - "85mm lens look, shallow depth of field"（肖像）
   - "head and shoulders framing"（头像）
   - "full body, clean white background"（角色设计）
   - "close-up face, portrait orientation"（表情/头像）

5. **质量锚点** — 添加风格质量参考：
   - "professional photography quality", "magazine cover quality"
   - "National Geographic photography style"（冒险）
   - "League of Legends splash art style"（游戏）
   - "Pixar and Disney animation style"（3D 头像）
   - "Studio Ghibli inspired"（动漫）
   - "fine art watercolor painting look"（水彩）

6. **纹理和材质** — 对于艺术风格，指定媒介：
   - "visible impasto brushstrokes, canvas texture"（油画）
   - "loose expressive watercolor style, soft edges, beautiful color bleeds and washes"（水彩）
   - "natural film grain, Kodak Portra 模拟"（复古）
   - "cel-shaded, clean line art, bold outlines"（动漫）
   - "visible pixels but NOT a pixelated photo filter"（像素艺术）

7. **表情指导** — 具体说明情绪：
   - ❌ "smiling"
   - ✅ "warm genuine smile, confident approachable expression"
   - ✅ "neutral calm expression with mouth closed"（身份证照片）
   - ✅ "passionate expression, energetic"（音乐家）

### 示例：构建自定义提示

用户："我想拍一张我作为巫师在魔法森林的照片"

```python
result = generate_portrait(
    image_path="uploads/photo.jpg",
    prompt=(
        "fantasy wizard portrait, wearing mystical purple robes with glowing runes, "
        "ancient wooden staff with crystal orb, wise powerful expression, "
        "enchanted forest background with bioluminescent plants and floating particles, "
        "dramatic magical lighting with ethereal glow, "
        "high fantasy art style, detailed digital painting quality"
    ),
)
# 注意：由于提供了 image_path，相似度前缀会自动添加
```

### 示例：像素艺术头像（来自 avatar-portrait 技能）

用户："给我做一个复古像素艺术头像"

```python
result = generate_portrait(
    image_path="uploads/photo.jpg",
    prompt=(
        "retro 16-bit pixel art portrait, visible pixels with clean lines, "
        "rich colors, consistent shading, stylized but maintains individual features, "
        "warm sunset cityscape background in matching pixel art style, "
        "head and shoulders, square format"
    ),
)
```

---

## 9. 照片系列

一次调用中生成一组主题协调的肖像。传递自定义风格/场景列表 — 代理会根据用户请求组装列表。

```python
exec(open('skills/image-portrait/generate_portrait.py').read())
result = generate_series(
    image_path="uploads/my_photo.jpg",
    series=[
        {"style": "professional"},
        {"style": "casual", "scene": "at a rooftop bar, sunset"},
        {"style": "anime"},
        {"prompt": "portrait as a superhero, cape flowing, city skyline"},
    ],
)
# result -> {"success": True, "images": [...4 images...], "series": "custom"}
```

列表中的每个项目都是一个包含可选键的字典：
- `style` — §7 中的任何风格键（例如 `"professional"`、`"anime"`、`"cyberpunk"`）
- `scene` — 覆盖场景描述（与风格模板组合）
- `prompt` — 完全自定义提示（忽略风格/场景）

---

## 10. 意图识别指南

使用此表格将用户请求映射到正确的风格/参数：

| 用户说 | 风格 | 备注 |
|-----------|-------|-------|
| "专业照片", "头像", "LinkedIn 照片" | `professional` 或 `linkedin` | |
| "约会照片", "约会应用", "Tinder 照片" | `dating_cafe` / `dating_beach` / `dating_city` | 询问哪种氛围 |
| "动漫我", "动漫版本", "卡通我" | `anime` | |
| "赛博朋克", "科幻肖像" | `cyberpunk` | |
| "油画", "古典肖像" | `oil_painting` | |
| "水彩肖像" | `watercolor` | |
| "复古照片", "复古" | `vintage` | |
| "休闲照片", "生活方式" | `casual` | |
| "在巴黎/欧洲旅行照片" | `travel_europe` | |
| "在东京/京都/日本旅行照片" | `travel_japan` | |
| "海滩照片", "热带" | `travel_tropical` 或 `dating_beach` | |
| "健身房照片", "健身" | `sports_gym` | |
| "圣诞节照片" | `christmas` | |
| "万圣节照片" | `halloween` | |
| "毕业照片" | `graduation` | |
| "婚礼照片" | `wedding` | |
| "厨师照片", "烹饪" | `chef` | |
| "音乐家", "在舞台上" | `musician` | |
| "和我家狗/宠物在一起" | `pet_together` | |
| "阅读", "书呆子" | `reading` | |
| "夜城", "都市夜晚" | `night_city` | |
| "汉服", "中国传统" | `hanfu` | |
| "3D 头像", "皮克斯风格" | `avatar_3d` | |
| "游戏头像", "RPG 角色" | `avatar_gaming` | |
| "VTuber 头像" | `avatar_vtuber` | |
| "儿童照片", "儿童肖像" | `child_portrait` | |
| "家庭照片" | `family_photo` | |
| "护照照片", "身份证照片" | `id_photo_white` | 白色背景默认 |
| "签证照片" | `id_photo_blue` | 蓝色背景 |
| "照片系列", "一组照片" | 使用 `generate_series()` | 从风格组装自定义列表 |
| "最高质量", "最佳质量" | 任何风格 + `model="gpt"` | |

### 不应使用此技能的情况（路由）

此技能的核心契约是**身份保留**：每当提供参考照片时，脚本**会自动添加**一个相似度保留指令到每个提示（除了 3 个 `avatar_*` 风格）。这意味着：

- **用户想要彻底改变面部/身份或完全重新想象人物**（例如 "让我看起来像另一个人"，重角色设计）→ 路由到 **image-create**（文本到图像）。相似度前缀会对抗风格化，迭代不会收敛。
- **用户想要强风格化但仍然可识别** → 保持在此；使用 `anime` / `avatar_3d` 等。
- **用户想要编辑非人物照片** → **image-edit**。

如果请求在 2 次以上迭代后仍无法摆脱参考照片的外观，那是相似度契约按设计工作 — 切换技能，而不是重新提示。

---

## 11. 提供的脚本

| 文件 | 目的 |
|------|---------|
| `generate_portrait.py` | 核心脚本：提交 → 汇报 → 下载。处理本地文件（base64）和 URL、所有风格、自定义场景、三个模型（nano2/nanopro/gpt）。 |
| `exports.py` | 重新导出 `generate_portrait`、`generate_series`、`STYLE_PROMPTS` 以供其他技能程序化使用。 |
| `_cost_track.py` | 成本跟踪辅助程序 — 通过 sc-proxy 头部记录每次调用成本。 |

---

## 12. 本地测试

设置 `FAL_KEY` 环境变量以直接调用 fal.ai（绕过 sc-proxy）：

```bash
# 单个肖像
FAL_KEY=your-fal-key python3 skills/image-portrait/generate_portrait.py photo.jpg anime 1 nanopro

# 参数：<image_path_or_url> [style] [count] [model]
```

---

## 13. 故障排除

| 问题 | 解决方法 |
|---------|-----|
| `File not found: ...` | 检查工作区路径；文件必须存在 |
| `Unsupported image format` | 使用 `.jpg`、`.jpeg`、`.png`、`.webp` 或 `.bmp` |
| `Image too large` | 调整到小于 10 MB 再上传 |
| `face_image_url must be a public HTTP(S) URL` | 使用 `image_path` 用于本地文件，或提供有效的 `https://` URL |
| `HTTP 402 insufficient_credits` | 充值余额；成本在提交时预扣 |
| `HTTP 403 endpoint_not_allowed` | sc-proxy 仅允许批准的 fal 端点；联系管理员 |
| 生成 `FAILED` 上游 | 简化提示，确保面部照片清晰且光线良好，重试 |
| 任务卡在 `IN_PROGRESS` >10 分钟 | 保存 `request_id`，稍后重试 |
| 负面面部一致性 | 使用清晰、正面、光线良好的照片；避免合影 |
| `gpt` 模型太慢 | 切换到 `nanopro`（默认）以获得更快的结果 |

---

## 14. 基础设施（参考）

- 调用者 → `sc-proxy` → `queue.fal.run/{model}` → fal 模型提供者
- 所有请求都必须包含 `Authorization: Key fake-falai-key-12345`（代理注入真实的 `FAL_KEY`）
- 提交时发生预扣。汇报/结果调用免费。
- 本地文件作为数据 URI base64 编码 — 无需单独上传步骤。
- 最终图像位于 `https://*.fal.media/...` — 公共 CDN，下载无需认证。
- 成本跟踪 via `_cost_track.py` — 记录 `X-Credits-Used` 从 sc-proxy 响应头部。

### 模型端点

| 模型 | 编辑（带参考图像） | 生成（仅文本） |
|-------|----------------------|---------------------|
| nano2 | `fal-ai/nano-banana-2/edit` | `fal-ai/nano-banana-2` |
| nanopro | `fal-ai/nano-banana-pro/edit` | `fal-ai/nano-banana-pro` |
| gpt | `openai/gpt-image-2/edit` | `openai/gpt-image-2` |
