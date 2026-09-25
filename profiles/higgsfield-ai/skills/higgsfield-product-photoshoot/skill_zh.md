# 产品照片拍摄

通过 `higgsfield product-photoshoot create` 命令生成品牌形象。CLI 调用后端提示增强器，该增强器包含特定模式的摄影词汇和结构模板，然后提交给 `gpt_image_2` 并返回图像 URL。

## 第 0 步 — 初始化

在任何其他命令之前：

1. 如果 `higgsfield` 不在 `$PATH` 中，请安装它：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. 如果 `higgsfield account status` 失败并显示 `Session expired` / `Not authenticated`，请提示用户运行 `higgsfield auth login`（交互式）并等待确认。

## 用户体验规则

1. 保持简洁。仅在最终回复中打印图像 URL。
2. 检测语言，用该语言回复。模式名称和 CLI 标志保持英文。
3. 提交前最多问 4 个简短问题。使用标记选项，不要开放式问题。
4. 跳过从上下文（上传的图像、先前的回合、品牌记忆）中可以明显得出答案的问题。
5. 不要自己编写 gpt_image_2 提示——后端会自动组装。
6. 轮询是静默的。等待 URL 准备好，然后交付。

## 模式

| 模式 | 用户想要… |
|---|---|
| `product_shot` | 产品在中性 / 工作室 / 目录背景上 |
| `lifestyle_scene` | 产品在现实世界环境中，手部，动作，氛围 |
| `closeup_product_with_person` | 紧凑裁剪，手部 / 部分面部——美妆应用，手持，展示 |
| `moodboard_pin` | 垂直 2:3 Pinterest 原生美学，情绪板感觉 |
| `hero_banner` | 宽格式网站 / 邮件 / 活动页眉 |
| `social_carousel` | 3–10 个连接的幻灯片，用于 IG / LinkedIn / Facebook |
| `ad_creative_pack` | Meta / TikTok / Pinterest / Google Ads 的协调静态广告变体包 |
| `virtual_model_tryout` | 由 AI 渲染的模特穿着或使用的产品 |
| `conceptual_product` | 超现实 / CGI 风格 / 飘浮 / 溅射 / 雕塑产品 |
| `restyle` | 转换现有图像的审美，情绪或季节性背景 |

## 模式选择

按意图选择，而不是表面关键词。当两个模式适用时，优先选择更具体的一个。

- 产品 + 中性 / 干净 / 白色 / 工作室 / 目录 / Shopify → `product_shot`
- 产品 + 场景 / 使用中 / 厨房 / 户外 / 咖啡馆 / 健身房 → `lifestyle_scene`
- 手持 / 面部与产品 / 美妆应用 / 展示 → `closeup_product_with_person`
- Pinterest，图钉，垂直图钉 → `moodboard_pin`
- 英雄，横幅，网站页眉，着陆页，邮件页眉，宽格式 → `hero_banner`
- 轮播，幻灯片帖子，多幻灯片，可滑动 → `social_carousel`
- 广告，广告包，付费社交，Meta / TikTok / Pinterest 广告 → `ad_creative_pack`
- 模特穿着 / 虚拟试穿 / 身体上 / 时尚拍摄 / 画册 → `virtual_model_tryout`
- 飘浮，漂浮，溅射，冻结动作，超现实，CGI，雕塑 → `conceptual_product`
- 修改现有图像的审美，情绪，季节——不改变主体 → `restyle`

平局规则：
- "厨房台面上我的产品的 Pinterest 图钉" → `moodboard_pin`（Pinterest 是平台）
- "展示我产品使用的英雄横幅" → `hero_banner`（横幅格式获胜）
- "我产品在不同场景中的轮播" → `social_carousel`（多幻灯片获胜）
- "正在使用我的血清的人的特写" → `closeup_product_with_person`（特定类型获胜）

## 生成前访谈

提交前问 3–4 个简短问题。始终使用标记选项，不要开放式问题。从上下文中可以明显得出答案的问题可以跳过。

### 类型 A — 上传了产品照片，"让我生成图像 / 拍摄"

1. 需要多少？ `[1 / 3 / 5]`
2. 什么风格/情绪？ `[干净工作室 / 生活方式 / 概念性 / 带模特 / 其他]`
3. 将要在哪里使用它们？ `[Shopify / Instagram / Pinterest / 付费广告 / 网站英雄]`
4. 品牌颜色匹配？（如果明显则跳过）

### 类型 B — 上传了产品照片，命名了使用案例

例如："为我产品制作广告"，"为我制作 Pinterest 图钉"，"为我制作英雄横幅"。模式是明显的。只问差距：

1. 需要多少？（如果是多输出模式）
2. 什么优惠 / 情绪 / 钩子？
3. 有什么特别强调的？

### 类型 C — 只有文本，没有产品照片

1. 你能上传产品照片吗？（首选——分辨率更高）
2. 如果不能，请描述产品——类别，包装，颜色，独特特征。
3. 什么风格？（与类型 A 相同的选项）
4. 将要在哪里使用它？

### 类型 D — 上传了现有图像，"重新制作 / 改变氛围 / 不同版本"

→ `restyle`

1. 什么审美？ `[干净女孩 / Cottagecore / 安静奢华 / 黑暗学院 / Y2K / 其他]`
2. 季节性背景？ `[圣诞节 / 情人节 / 万圣节 / 黑色星期五 / 无]`
3. 保留什么，改变什么？（如果模糊）

### 类型 E — 模特穿着产品（时尚，配饰）

→ `virtual_model_tryout`

1. 模特原型？（根据品牌受众建议 2–3 个）
2. 环境？ `[工作室干净 / 户外自然 / 街头风格 / 编辑室 / 家里舒适]`
3. 构图？ `[全身 / 三分之二 / 上半身 / 产品区域特写]`

### 类型 F — 模糊请求，主题不明确

例如："为我品牌制作一些酷的东西"。

1. 什么产品或主题？
2. 目标？ `[在市场上销售 / 建立知名度 / 运行付费广告 / 更新网站]`
3. 上传参考图像？

回答后→返回相关的类型 A–E。

## 生成

单个命令。后端组装最终提示并提交给 `gpt_image_2`。URL 打印在标准输出上。

```bash
higgsfield product-photoshoot create \
  --mode <mode> \
  --prompt "<从访谈答案中获取的简短用户意图描述>" \
  [--image <路径或上传 ID>]... \
  [--count <1-10>] \
  [--aspect_ratio <覆盖>]
```

示例：

```bash
higgsfield product-photoshoot create \
  --mode lifestyle_scene \
  --prompt "阳光明媚的厨房台面上的冷泡咖啡瓶，IG 信息流" \
  --image bottle.jpg \
  --count 3
```

```bash
higgsfield product-photoshoot create \
  --mode moodboard_pin \
  --prompt "为我蜡烛品牌制作的垂直图钉，Cottagecore 氛围" \
  --image candle.jpg
```

```bash
higgsfield product-photoshoot create \
  --mode restyle \
  --prompt "圣诞节版本，安静奢华审美" \
  --image existing-shot.jpg
```

## 图像输入

`--image` 接受本地文件路径（自动上传）或现有的上传 UUID。重复标志以提供多个参考。

## 多变体

`--count 3` 返回 3 个不同的图像 URL。后端要求增强器在变体之间变化预设、光照、角度和调色板——它们不会是彼此的释义副本。

对于 `social_carousel` 和 `ad_creative_pack`，计数 = 幻灯片数量 / 包中的变体数量。后端会自动锁定所有幻灯片的视觉系统。

## 纵横比

后端根据每个模式选择一个合理的默认值。仅在用户明确要求不同时使用 `--aspect_ratio` 覆盖。允许的值：`1:1`，`4:5`，`5:4`，`3:4`，`4:3`，`2:3`，`3:2`，`9:16`，`16:9`。

## 分辨率

每个产品-照片拍摄任务使用 `2k`。

## 交付结果

将图像 URL 作为简短的圆点列表打印。不要 JSON，不要 ID，不要内部模型名称，不要增强的提示文本。如果任务失败，简要提及失败状态。

```
3 张生活方式照片已准备好：
- https://cdn.higgsfield.ai/.../job_abc.jpg
- https://cdn.higgsfield.ai/.../job_def.jpg
- https://cdn.higgsfield.ai/.../job_ghi.jpg
```

## 这项技能不做什么

- 不直接编写 gpt_image_2 提示。后端负责提示组装。
- 不自动选择不同的图像生成模型。始终使用 `gpt_image_2`。
- 不取代 `higgsfield-generate` 营销工作室，用于品牌视频 / 头像工作流程。
- 不取代 `higgsfield-generate`，用于没有产品或品牌背景的原始文本到图像。

## 常见错误

- 在单个消息中问超过 4 个访谈问题。
- 选择错误的模式（例如，用户想要 Pinterest 图钉时使用 `product_shot`）。
- 直接调用 `higgsfield generate create gpt_image_2 --prompt ...` 而不是 `higgsfield product-photoshoot create`——绕过后端提示增强器，输出明显更差。
- 将组装好的提示粘贴回用户——他们想要 URL。
- 使用上表中不存在的 `--mode` 值。
