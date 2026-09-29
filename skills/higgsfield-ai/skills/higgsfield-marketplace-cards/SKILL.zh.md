---
name: higgsfield-marketplace-cards
description: '通过 Higgsfield 生成市场产品图片卡片：符合规范的

  主图、次要产品图片以及 A+ 风格内容模块。当用户需要市场列表图片、产品详情卡片、次要产品图片、产品信息图表、生活方式列表照片、A+ 风格内容、市场图片集或销售就绪的产品视觉时使用。

  后端负责市场合规参考和提示模板；此技能仅将用户意图路由到 CLI。

  不适用于无市场/列表上下文的通用品牌产品摄影（使用 higgsfield-product-photoshoot）、视频生成或 UGC 广告（使用 higgsfield-generate），或 Soul Character 训练（使用 higgsfield-soul-id）。'
---

# 市场卡片

使用 `higgsfield marketplace-cards create` 创建适用于市场平台的商品视觉效果。CLI 首先调用后端增强器，其中包含市场规则和模板，这些内容是私有的，然后创建 `nano_banana_2` 任务并打印结果 URL。

## 初始化

1. 如果 `higgsfield` 不在 `$PATH` 中，请通过运行官方安装器（使用 Bash）来安装它：`curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`。
2. 如果 `higgsfield account status` 因身份验证错误而失败，请要求用户运行 `higgsfield auth login`。

## 用户体验规则

1. 使用用户的语言进行响应。
2. 在执行之前，最多只问一个简洁的确认问题。
3. 优先使用产品图片。如果用户只提供文本或 URL，只有在产品细节清晰的情况下才进行操作。
4. 不要自己编写最终的图像生成提示。后端增强器负责这部分。
5. 最终答案应只包含准备好的图像 URL 和简短标签。

## 范围选择

当用户要求常见捆绑包时，使用 `--scope`：

| 范围 | 创建 |
|---|---|
| `main` | 1 张市场主图 |
| `product-images` | 主图 + 5 张次要图片 |
| `aplus` | 主图 + 7 个 A+ 模块 |
| `full-set` | 主图 + 5 张次要图片 + 7 个 A+ 模块 |

仅用于自定义子集时，使用重复的 `--asset`：

- `main_image`
- `infographic`
- `multi_angle`
- `detail_shot`
- `lifestyle`
- `whats_in_box`
- `aplus_hero_banner`
- `aplus_pain_points`
- `aplus_features`
- `aplus_ingredients`
- `aplus_efficacy`
- `aplus_how_to_use`
- `aplus_endorsement`

## 命令

根据用户的请求构建并运行一个 `higgsfield marketplace-cards create` 命令。

对于常见捆绑包，使用 `--scope <main|product-images|aplus|full-set>`，`--prompt "<简短的产品和列表意图>"`，可选的重复 `--image <路径或上传 ID>`，以及可选的上下文标志：`--product_context`，`--brand_context`，`--category`，`--visual_style`。

选择参数时，参考以下示例：

- 产品图片：`higgsfield marketplace-cards create --scope product-images --prompt "闪亮的桃子柠檬水罐，用于市场列表" --image ./can.png --category "饮料"`
- 完整套装：`higgsfield marketplace-cards create --scope full-set --prompt "高端护肤精华，干净的 临床市场视觉效果系统" --image ./serum.jpg --brand_context "极简白色和鼠尾草调色板"`
- 自定义子集：重复 `--asset`，例如 `--asset main_image --asset infographic --asset lifestyle`。
- 已完成的 main 图像任务：使用 `--main-job <completed_main_job_id>` 并带有请求的次要或 A+ `--asset` 值。

## 交付

打印带标签的 URL：

```text
市场卡片已准备就绪：
- 主图：https://...
- 信息图：https://...
- 生活方式：https://...
```

除非用户明确要求，否则避免使用 JSON、任务 ID、内部模型名称或增强提示文本。
