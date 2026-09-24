# 市场卡片

使用 `higgsfield marketplace-cards create` 创建市场就绪的产品视觉素材。
CLI 首先调用后端增强器，市场规则和模板保存在其中，随后创建 `nano_banana_2` 任务并打印结果 URL。

## 引导

1. 如果 `higgsfield` 不在 `$PATH` 中，请通过 Bash 运行官方安装程序进行安装：`curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`。
2. 如果 `higgsfield account status` 因认证错误而失败，请引导用户运行 `higgsfield auth login`。

## UX 规则

1. 以用户的语言进行回复。
2. 在执行前，最多询问一个问题以获取简洁的确认。
3. 优先使用产品图片。如果用户仅提供文本或 URL，仅在产品信息清晰时继续执行。
4. 不要自行编写最终的图片生成提示词，由后端增强负责该工作。
5. 最终回答应仅包含就绪的图片 URL 和简短标签。

## 范围选择

当用户请求获取常用组合包时，使用 `--scope`：

| 范围 | 创建内容 |
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

根据用户请求构建并运行一条 `higgsfield marketplace-cards create` 命令。

对于常用组合包，使用 `--scope <main|product-images|aplus|full-set>`、`--prompt "<简短的产品及上架意图>"`，可选重复的 `--image <path-or-upload-id>`，以及可选的上下文参数：`--product_context`、`--brand_context`、`--category`、`--visual_style`。

选择参数时，可参考以下示例：

- 产品图片：`higgsfield marketplace-cards create --scope product-images --prompt "用于市场上架的冒泡桃子柠檬汁罐" --image ./can.png --category "饮品"`
- 完整套装：`higgsfield marketplace-cards create --scope full-set --prompt "高端护肤精华液，简洁的临床市场视觉体系" --image ./serum.jpg --brand_context "极简白与鼠尾草色调"`
- 自定义子集：重复使用 `--asset`，例如 `--asset main_image --asset infographic --asset lifestyle`。
- 使用已完成的表面主图任务：使用 `--main-job <completed_main_job_id>`，并配合所请求的次要图片或 A+ 的 `--asset` 值。

## 交付

使用标签打印 URL：

```text
Marketplace cards ready:
- Main image: https://...
- Infographic: https://...
- Lifestyle: https://...
```

除非用户明确要求，否则避免输出 JSON、任务 ID、内部模型名称或增强后的提示文本。
