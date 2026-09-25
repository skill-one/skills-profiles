# 产品拍摄

通过 `higgsfield product-photoshoot create` 命令生成品牌图像。CLI 调用后端提示词增强器，该增强器包含特定模式的摄影词汇和结构模板，随后提交至 `gpt_image_2` 并返回图像 URL。

## 步骤 0 — 引导

在任何其他命令之前：

1. 如果 `higgsfield` 不在 `$PATH` 中，请安装它：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```
2. 如果 `higgsfield account status` 以 `Session expired` / `Not authenticated` 失败，请引导用户运行 `higgsfield auth login`（交互式）并等待确认。

## 用户体验规则

1. 保持简洁。最终回复中仅打印图像 URL。
2. 检测语言，以相应语言回复。模式名称和 CLI 标志保持英文。
3. 提交前最多询问 4 个简短问题。使用带标签的选项，绝不使用开放式问题。
4. 跳过根据上下文（已上传图像、上一轮对话、品牌记忆）显而易见答案的问题。
5. 绝不自行编写 `gpt_image_2` 提示词——由后端组装。
6. 轮询期间保持静默。待 URL 准备就绪后再交付。

## 模式

| 模式 | 用户想要…… |
|---|---|
| `product_shot` | 产品在中性/摄影棚/目录背景上 |
| `lifestyle_scene` | 产品在实际环境、手部、动作、氛围中 |
| `closeup_product_with_person` | 紧凑裁剪，包含手部/半张面部——美妆应用、手持、演示 |
| `moodboard_pin` | 垂直 2:3 的 Pinterest 原生美学，moodboard 质感 |
| `hero_banner` | 宽幅网页/邮件/活动页眉 |
| `social_carousel` | 为 IG / LinkedIn / Facebook 提供 3–10 个关联幻灯片 |
| `ad_creative_pack` | 用于 Meta / TikTok / Pinterest / Google Ads 的协调式静态广告变体组合 |
| `virtual_model_tryout` | 产品由 AI 渲染模型穿戴或使用 |
| `conceptual_product` | 超现实/CGI 风格/悬浮/飞溅/雕塑感产品 |
| `restyle` | 改变现有图像的审美、氛围或季节背景 |

## 模式选择

根据意图选择，而非表面关键词。当两种模式均可适用时，优先选择更具体的一种。

- 产品 + 中性/干净/白色/摄影棚/目录/ Shopify → `product_shot`
- 产品 + 场景/使用中/厨房/户外/咖啡店/健身房 → `lifestyle_scene`
- 手持/面部带产品/美妆应用/演示 → `closeup_product_with_person`
- Pinterest、pin、垂直 pin → `moodboard_pin`
- hero、banner、网页页眉、落地页、邮件页眉、宽幅格式 → `hero_banner`
- carousel、幻灯片帖子、多幻灯片、可滑动 → `social_carousel`
- 广告、广告组合、付费社交、Meta / TikTok / Pinterest 广告 → `ad_creative_pack`
- 模特穿戴、虚拟试穿、上身、时装拍摄、画册 → `virtual_model_tryout`
- 悬浮、漂浮、飞溅、凝固动态、超现实、CGI、雕塑感 → `conceptual_product`
- 修改现有图像的审美、氛围、季节——且不改变主体 → `restyle`

决胜规则：
- "我产品放在厨房台面上的 Pinterest 笔记" → `moodboard_pin`（Pinterest 为平台）
- "展示我产品在使用的 Hero banner" → `hero_banner`（banner 格式优先）
- "产品在不同场景中的轮播" → `social_carousel`（多幻灯片优先）
- "人使用我精华液的特写" → `closeup_product_with_person`（具体类型优先）

## 生成前访谈

提交前询问 3–4 个简短问题。始终使用带标签的选项，绝不使用开放式问题。跳过根据上下文（已上传图像、上一轮对话、品牌记忆）显而易见答案的问题。

### 类型 A — 已上传产品照片，要求“生成图像/拍摄”

1. 数量？ `[1 / 3 / 5]`
2. 什么风格/氛围？ `[Clean studio / Lifestyle / Conceptual / With a model / Other]`
3. 将在何处使用？ `[Shopify / Instagram / Pinterest / 付费广告 / 网站主图]`
4. 需匹配的品牌色？（若显而易见则跳过）

### 类型 B — 已上传产品照片，指明使用场景

例如“为我产品制作广告”、“制作 Pinterest 笔记”、“制作 Hero banner”。模式显而易见。仅询问缺失信息：

1. 数量？（若为多输出模式）
2. 有何卖点/氛围/吸引点？
3. 需特别强调的内容？

### 类型 C — 仅有文字，无产品照片

1. 能否上传产品照片？（优先——保真度更高）
2. 如果不能，请描述产品——类别、包装、颜色、显著特征。
3. 什么风格？（与类型 A 相同选项）
4. 将在何处使用？

### 类型 D — 已上传现有图像，要求“重做/改变氛围/不同版本”

→ `restyle`

1. 什么审美？ `[Clean girl / Cottagecore / Quiet luxury / Dark academia / Y2K / Other]`
2. 季节背景？ `[圣诞节 / 情人节 / 万圣节 / 黑色星期五 / 无]`
3. 需保留什么、改变什么？（仅当存在歧义时）

### 类型 E — 模特穿戴产品（时尚、配饰）

→ `virtual_model_tryout`

1. 模特原型？ （根据品牌受众建议 2–3 个）
2. 环境？ `[干净摄影棚 / 户外自然 / 街头风格 / 编辑风 / 居家舒适]`
3. 取景？ `[全身 / 七分身 / 腰部以上 / 产品区域特写]`

### 类型 F — 模糊请求，主体不明确

例如“为我品牌制作酷炫内容”。

1. 什么产品或主题？
2. 目标？ `[在平台上架销售 / 建立认知 / 投放付费广告 / 更新网站]`
3. 上传参考图像？

回答后 → 返回至相关的类型 A–E。

## 生成

单条命令。后端组装最终提示词并提交至 `gpt_image_2`。URL 打印在标准输出上。

```bash
higgsfield product-photoshoot create \
  --mode <mode> \
  --prompt "<short user-intent description from interview answers>" \
  [--image <path-or-upload-id>]... \
  [--count <1-10>] \
  [--aspect_ratio <override>]
```

示例：

```bash
higgsfield product-photoshoot create \
  --mode lifestyle_scene \
  --prompt "bottle of cold-brew on a sunlit kitchen counter, IG feed" \
  --image bottle.jpg \
  --count 3
```

```bash
higgsfield product-photoshoot create \
  --mode moodboard_pin \
  --prompt "vertical pin for my candle brand, cottagecore mood" \
  --image candle.jpg
```

```bash
higgsfield product-photoshoot create \
  --mode restyle \
  --prompt "Christmas version, quiet-luxury aesthetic" \
  --image existing-shot.jpg
```

## 图像输入

`--image` 接受本地文件路径（自动上传）或已存在的上传 UUID。对于多个引用，重复使用该标志。

## 多变体

`--count 3` 返回 3 个不同的图像 URL。后台要求增强器在不同变体中变化预设、灯光、角度和调色板——它们不会是彼此的改写副本。

对于 `social_carousel` 和 `ad_creative_pack`，count 等于打包中的幻灯片/变体数量。后台会自动在所有幻灯片间锁定视觉系统。

## 宽高比

后台根据每种模式选择合理的默认值。仅当用户明确要求不同值时，才使用 `--aspect_ratio` 进行覆盖。允许的值：`1:1`，`4:5`，`5:4`，`3:4`，`4:3`，`2:3`，`3:2`，`9:16`，`16:9`。

## 分辨率

所有产品拍摄任务均使用 `2k`。

## 交付结果

将图像 URL 作为简短的带项目符号列表打印。不包含 JSON、ID、内部模型名称或增强提示词文本。如果任务失败，请简要提及并附上失败状态。

```
3 lifestyle shots ready:
- https://cdn.higgsfield.ai/.../job_abc.jpg
- https://cdn.higgsfield.ai/.../job_def.jpg
- https://cdn.higgsfield.ai/.../job_ghi.jpg
```

## 本技能不包含的功能

- 不直接编写 `gpt_image_2` 提示词。提示词组装由后端负责。
- 不自动选择不同的图像生成模型。始终使用 `gpt_image_2`。
- 不替代 `higgsfield-generate` 营销工作室用于品牌视频/头像工作流。
- 不替代 `higgsfield-generate` 用于无产品或品牌背景的纯文本转图像。

## 需避免的常见错误

- 单条消息中询问超过 4 个访谈问题。
- 选择错误模式（例如用户想要 Pinterest 笔记时选择了 `product_shot`）。
- 直接调用 `higgsfield generate create gpt_image_2 --prompt ...` 而非 `higgsfield product-photoshoot create` ——绕过了提示词增强器，输出效果会明显变差。
- 将组装好的提示词粘贴回用户——用户需要的是 URL。
- 使用表格中未列出的 `--mode` 值。
