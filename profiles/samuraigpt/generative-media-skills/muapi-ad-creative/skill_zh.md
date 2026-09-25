# 广告创意套件

**生成高转化率的广告创意套件——主视觉图、广告文案变体以及针对Meta、Google Display和LinkedIn的平台优化裁剪。**

## 输入

| 名称 | 类型 | 必填 | 默认值 | 描述 |
|:---|:---|:---|:---|:---|
| `product_or_service` | 文本 | 是 | — | 正在推广的产品或服务（例如："适用于远程团队的SaaS项目管理工具"）。 |
| `target_audience` | 文本 | 是 | — | 广告的目标受众（例如："25-40岁的科技达人型初创公司创始人"）。 |
| `campaign_goal` | 文本 | 否 | awareness | 营销目标——"awareness"、"consideration"或"conversion"。 |
| `tone` | 文本 | 否 | professional, clean, modern | 创意语气和视觉风格（例如："大胆且颠覆性"、"奢华极简"、"友好且易接近"）。 |
| `product_image` | 图片URL | 否 | — | 会话中已有的可选产品或品牌图片URL。 |


## 步骤

此技能分为两个阶段。阶段A创建主视觉概念以供审批；阶段B扩展到平台格式。

### 阶段A — 主视觉图 + 广告文案

提交一个计划，包含：

1. **主视觉图** — 使用`muapi image generate`（模型=nano-banana-pro）或如果提供了`{{product_image}}`，则使用`muapi image edit`（模型=nano-banana-pro-edit）：
   - 纵横比：1:1（通用起始点）。
   - 提示必须捕捉：产品/服务利益点、目标受众生活方式线索、营销语气。
   - 风格：`{{tone}}, 广告摄影, 干净背景, 产品聚焦, 超级精细, 商业品质`。
   - 等级：质量。

执行计划后，展示主视觉素材和3个广告文案变体：
- **变体A** — 问题导向钩子："厌倦了X？[产品]解决这些问题。"
- **变体B** — 利益导向："功能 → [结果]为[受众]。"
- **变体C** — 社会证明/紧迫性："已有X个团队使用[产品]。"
每个变体包含：标题（最多6个字）、正文（20-30字）、CTA按钮文本。

询问用户选择哪个文案变体用于阶段B。等待用户确认。

### 阶段B — 平台裁剪

一旦用户选择文案方向，提交第二个计划，包含平行裁剪：

1. `muapi image edit` → 1:1（Facebook/Instagram信息流，1080×1080）
2. `muapi image edit` → 9:16（故事/Reels，1080×1920）
3. `muapi image edit` → 1.91:1（Facebook宽信息流，1200×628）
4. `muapi image edit` → 1:1（LinkedIn信息流，与Facebook相同）

对于每个裁剪：
- 提示："为[平台]广告格式重新构图。保持产品/主体居中且未裁剪。保持原始调色板和语气。为文本叠加留出头部/尾部空间。"
- 所有裁剪并行运行。

以每个格式返回一个资产，并推荐每个格式的文案叠加位置。

## 注意事项
- 如果`campaign_goal`是"conversion"，文案中强调紧迫性和直接CTA。
- 如果`campaign_goal`是"awareness"，优先考虑视觉冲击力而非文本密度。
- 通过`$nX.url`语法在阶段B节点中引用`product_image`，确保一致性。
- 不要在用户选择文案变体前自动确认阶段B。

## 触发关键词

`ad creative`, `advertisement`, `facebook ad`, `meta ad`, `google ad`, `linkedin ad`, `paid ad`, `ad banner`, `display ad`


---

## 执行代理注意事项

- 此配方由LLM编排：读取每个阶段，从用户那里收集任何缺失的输入，然后调用`muapi` CLI命令。如果`MUAPI_API_KEY`未设置，首先使用`muapi auth configure`。
- 对于还没有CLI别名的模型ID，通过`curl -X POST https://api.muapi.ai/api/v1/<endpoint> -H "x-api-key: $MUAPI_API_KEY" -H 'content-type: application/json' -d '{...}'`回退到原始端点，并使用`muapi predict wait <request_id>`轮询。
- 在发出每个调用之前，用用户的实际输入替换`{{input_name}}`占位符。
