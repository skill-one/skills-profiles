# UGC视频工厂

**将人物照片 + 产品照片 (+可选脚本 & 环境) 转换为带有原生对话音频的垂直9:16 UGC风格视频广告。**

一个三阶段流程：
1. **GPT** 根据您的输入撰写导演级超逼真生活方式摄影提示。
2. **Nano-Banana Pro Edit** 将人物 + 产品融合为单个主角照片（1K，9:16）。
3. **Seedance 2.0 VIP 图像转视频** 将主角照片动画化为10秒垂直UGC片段，并同步语音音频。

## 输入

| 名称 | 类型 | 必填 | 默认值 | 描述 |
|:---|:---|:---|:---|:---|
| `person` | image_url | 是 | — | 广告中将出现的人物照片（面部+上半身效果最佳）。 |
| `product` | image_url | 是 | — | 产品清晰照片（最好在浅色背景下，标志/文字清晰可辨）。 |
| `script` | text | 否 | `Okay… first of all, ship happens. And this hat is honestly my favorite. It also comes in navy and black, so you can pick your vibe.` | 屏幕上人物将说的确切台词（保持简短——1-2句话适合10秒）。 |
| `environment` | text | 否 | `study room, laptop in front of it` | 人物使用产品的场景/环境（例如："bathroom mirror, morning routine", "coffee shop window seat"）。 |

如果 `person` 或 `product` 缺失，提示用户上传（`muapi upload file <path>`）或提供生成占位符再继续。

## 步骤

按顺序运行三个步骤——每个步骤的输出将作为下一个步骤的输入。

### 步骤1 — 导演提示（GPT）

使用GPT模型（`gpt-5.1` 或执行代理可用的任何聊天模型）并设置**温度0**和**最大约200个token**来生成主角图像提示。

**系统提示：** `You are a helpful assistant.`

**用户提示**（替换 `{{person}}`，`{{product}}`，`{{environment}}`）：

```
正在分析上传的图像。超逼真生活方式摄影，包含 {{person}}，{{product}} 和 {{environment}}。

如果产品是可穿戴的（例如，帽子、眼镜、连帽衫），人物自然佩戴产品。

如果产品是手持的（例如，乳液、瓶子、保温瓶），人物自然手持产品。

产品清晰可见，是图像的主要焦点。产品上的标志或文字必须清晰可辨。

人物具有自然且现代的外观，风格简约。

场景与产品的使用背景一致：{{environment}}。

光线：柔和的自然日光。
背景：干净、美观、轻微模糊（浅景深）。
风格：高端商业生活方式摄影，逼真纹理，4K质量，垂直9:16构图，社交媒体广告风格。背景和环境应适合产品（例如，使用精华的女人可以在家里）。人物的面部细节和产品必须保持不变。
```

将GPT的响应捕获为 `{{step1_prompt}}`。

### 步骤2 — 主角图像（Nano-Banana Pro Edit）

对 `nano-banana-pro-edit` 模型提交 `muapi image edit` 调用：

- **参考图像** (`image_urls`)：`[ {{person}}, {{product}} ]` — 顺序很重要；人物优先。
- **提示**：`{{step1_prompt}}` 来自步骤1。
- **宽高比**：`9:16`
- **图像数量**：`1`
- **分辨率**：`1K`
- **输出格式**：`jpeg`

将生成的图像URL捕获为 `{{hero_image}}`。在启动视频步骤之前，向用户展示图像以供批准。

### 步骤3 — UGC视频（Seedance 2.0 VIP 图像转视频）

对 **`seedance-2-vip-image-to-video`**（如果执行代理希望更低延迟，则使用 `-fast` 变体）提交 `muapi video from-image` 调用。

- **起始图像**：`{{hero_image}}` 来自步骤2。
- **宽高比**：`9:16`
- **时长**：`10` 秒。
- **生成音频**：`true`（原生对话）。
- **CFG scale**：`0.5`
- **负面提示**：`模糊，扭曲，低质量`
- **提示**（替换 `{{script}}`）：

```
创建一个10秒的垂直UGC风格视频（9:16）。

人物自然地与其环境和产品互动。

产品自然使用：
- 如果可穿戴 → 人物佩戴。
- 如果手持 → 人物手持或使用。

视频是单个、不间断的镜头。无剪辑。无颜色变化。屏幕上无文字。

人物直视镜头，表情放松自然。
他们用手舒适地与产品互动（调整、手持、指向）。

他们用自然、对话的语气说：

"{{script}}"

说话时带有微小的手势。
以微笑或点头结束。

风格：真实UGC，手持手机感，轻柔自然运动，柔和日光，浅景深，TikTok/Reels美学。
```

使用 `muapi predict wait <request_id>` 汇报结果，并下载到用户的输出目录。

## 注意事项

- VIP等级支持9:16宽高比和4-15秒时长；10秒是1-2句脚本的最佳时长。
- 保持脚本简短——Seedance 2.0会压缩较长的脚本并剪辑单词。
- Seedance VIP容忍参考图像中的逼真人脸（与中国等级不同），使其成为UGC的正确选择。
- 如果您希望以相同质量获得更低延迟，则切换到 `seedance-2-vip-image-to-video-fast`。
- 对于多镜头广告，在步骤2中生成多个 `{{hero_image}}` 变体，并独立动画化每个——Seedance VIP不支持9:16 + 音频的多图像i2v。

## 触发关键词

`ugc video factory`, `ugc video ad`, `person plus product video`, `talking product ad`, `ugc reel`, `lifestyle product video`, `vertical ugc video`


---

## 执行代理注意事项

- 此配方由LLM编排：读取每个阶段，从用户那里收集任何缺失的输入，然后调用 `muapi` CLI命令。如果 `MUAPI_API_KEY` 未设置，请先运行 `muapi auth configure`。
- 对于用户提供的本地文件，请先上传它们：`muapi upload file <path> --output-json --jq '.url'`。
- 在发出每个调用之前，用用户的实际输入替换 `{{input_name}}` 占位符。
- 如果 `muapi` CLI尚未为 `nano-banana-pro-edit` 或 `seedance-2-vip-image-to-video` 创建别名，则回退到原始API：`curl -X POST https://api.muapi.ai/api/v1/<endpoint> -H "x-api-key: $MUAPI_API_KEY" -H 'content-type: application/json' -d '{...}'`，然后使用 `muapi predict wait <request_id>` 汇报。
