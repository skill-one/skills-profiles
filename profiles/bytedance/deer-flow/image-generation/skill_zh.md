# 图像生成技能

## 概述

该技能使用结构化提示和 Python 脚本生成高质量图像。工作流程包括创建 JSON 格式的提示，并执行带可选参考图像的图像生成。

## 核心功能

- 创建用于 AIGC 图像生成的结构化 JSON 提示
- 支持多个参考图像以指导风格/构图
- 通过自动化 Python 脚本执行图像生成
- 处理各种图像生成场景（角色设计、场景、产品等）

## 工作流程

### 第 1 步：理解需求

当用户请求图像生成时，识别：

- 主题/内容：图像中应包含什么
- 风格偏好：艺术风格、情绪、调色板
- 技术规格：宽高比、构图、光照
- 参考图像：任何用于指导生成的图像
- 无需检查 `/mnt/user-data` 下面的文件夹

### 第 2 步：创建结构化提示

在 `/mnt/user-data/workspace/` 生成结构化 JSON 文件，命名模式：`{描述性名称}.json`

### 第 3 步：执行生成

调用 Python 脚本：
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/prompt-file.json \
  --reference-images /path/to/ref1.jpg /path/to/ref2.png \
  --output-file /mnt/user-data/outputs/generated-image.jpg
  --aspect-ratio 16:9
```

参数：

- `--prompt-file`：JSON 提示文件的绝对路径（必需）
- `--reference-images`：参考图像的绝对路径（可选，空格分隔）
- `--output-file`：输出图像文件的绝对路径（必需）
- `--aspect-ratio`：生成图像的宽高比（可选，默认：16:9）

[!NOTE]
不要读取 python 文件，只需用参数调用它。

## 角色生成示例

用户请求："创建一个 1990 年代的东京街头风格女性角色"

创建提示文件：`/mnt/user-data/workspace/asian-woman.json`
```json
{
  "characters": [{
    "gender": "female",
    "age": "二十多岁",
    "ethnicity": "Japanese",
    "body_type": "苗条、优雅",
    "facial_features": "精致的面容、富有表现力的眼睛、淡雅的妆容，强调嘴唇，部分湿透的雨发长黑发",
    "clothing": "时尚的雨衣、设计师手提包、高跟鞋、当代东京街头时尚",
    "accessories": "极简珠宝、醒目耳环、皮手提包",
    "era": "1990s"
  }],
  "negative_prompt": "模糊的面部、变形、低质量、过于锐利的数字外观、饱和度过高、人工光照、工作室环境、摆姿势、自拍角度",
  "style": "Leica M11 街头摄影美学、电影感渲染、自然调色板带轻微暖色调、背景虚化、模拟摄影感",
  "composition": "中景、三分法、主体略微偏离中心、可见东京街头的环境背景、浅景深突出主体",
  "lighting": "招牌和店铺的霓虹灯、湿漉漉的路面反射、柔和的城市环境光、自然街道照明、背景霓虹灯的轮廓光",
  "color_palette": "柔和的自然主义色调、温暖的肤色、冷蓝色和品红色霓虹点缀、与数字摄影相比饱和度较低、胶片颗粒纹理"
}
```

执行生成：
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/cyberpunk-hacker.json \
  --output-file /mnt/user-data/outputs/cyberpunk-hacker-01.jpg \
  --aspect-ratio 2:3
```

带参考图像：
```json
{
  "characters": [{
    "gender": "基于 [Image 1]",
    "age": "基于 [Image 1]",
    "ethnicity": "来自 [Image 1] 的人类改编至星球大战宇宙",
    "body_type": "基于 [Image 1]",
    "facial_features": "与 [Image 1] 相匹配，略带太空旅行的风霜感",
    "clothing": "星球大战风格服装 - 磨损的皮夹克配多功能背心、战术裤配装袋、破旧靴子、带枪套的腰带",
    "accessories": "臀部挂一把爆能枪、手腕戴通讯器、额头推起护目镜、装物资的背包、基于 [Image 2] 的个人载具",
    "era": "星球大战宇宙，帝国时代之后"
  }],
  "prompt": "受 [Image 1] 启发的角色站在星球大战宇宙美学中繁忙外星星球街道旁的载具 [Image 2] 旁边。角色穿着磨损的皮夹克配多功能背心、战术裤配装袋、破旧靴子、带爆能枪的腰带。载具改编至星球大战美学，磨损的金属面板、反重力引擎、覆盖着沙漠尘埃，停放在街道上。外星市集街道有多层建筑、磨损的金属结构、挂着彩色遮阳篷的市场摊位、背景中走过各种外星物种。双太阳投下温暖的金色光线，空气中弥漫着大气尘埃，远处可见蒸汽发生器。粗粝的、充满生活气息的星球大战美学、实用特效外观、胶片感纹理、电影感构图。",
  "negative_prompt": "干净的未来感外观、无菌环境、过于 CGI 的外观、奇幻中世纪元素、地球建筑、现代城市",
  "style": "星球大战原三部曲美学、充满生活气息的宇宙、受实用特效启发的、电影感外观、略微去饱和带暖色调",
  "composition": "中景宽拍、前景角色与延伸至背景的外星街道、环境叙事、三分法",
  "lighting": "双太阳的温暖黄昏光照、角色轮廓光、大气雾霾、市场摊位的实用光源",
  "color_palette": "温暖的沙色调、赭石和赭色、尘埃蓝色、磨损金属色、柔和的地球色带外星市场颜色点缀",
  "technical": {
    "aspect_ratio": "9:16",
    "quality": "高",
    "detail_level": "高度详细带电影感纹理"
  }
}
```
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/star-wars-scene.json \
  --reference-images /mnt/user-data/uploads/character-ref.jpg /mnt/user-data/uploads/vehicle-ref.jpg \
  --output-file /mnt/user-data/outputs/star-wars-scene-01.jpg \
  --aspect-ratio 16:9
```

## 常见场景

使用不同的 JSON 模式用于不同场景。

**角色设计**：
- 身体属性（性别、年龄、种族、体型）
- 脸部特征和表情
- 衣物和配饰
- 历史时代或设定
- 姿势和背景

**场景生成**：
- 环境描述
- 时间、天气
- 氛围和情绪
- 焦点和构图

**产品可视化**：
- 产品细节和材质
- 光照设置
- 背景和环境
- 展示角度

## 特定模板

仅当匹配用户请求时才读取以下模板文件。

- [哆啦A梦漫画](templates/doraemon.md)

## 输出处理

生成后：

- 图像通常保存在 `/mnt/user-data/outputs/`
- 使用 present_files 工具与用户分享生成的图像
- 提供生成结果的简要描述
- 如需调整，提供迭代机会

## 提示：使用参考图像增强生成效果

对于视觉准确性至关重要的场景，**在使用生成前先调用 `image_search` 工具** 找到参考图像。

**推荐使用 `image_search` 工具的场景**：
- **角色/肖像生成**：搜索相似的姿势、表情或风格以指导面部特征和身体比例
- **特定物体或产品**：查找真实物体的参考图像以确保准确呈现
- **建筑或环境场景**：搜索位置参考以捕捉真实细节
- **时尚和服装**：查找风格参考以确保准确的服装细节和造型

**示例工作流程**：
1. 调用 `image_search` 工具找到合适的参考图像：
   ```
   image_search(query="日本女性街头摄影 1990年代", size="Large")
   ```
2. 下载返回的图像 URL 到本地文件
3. 将下载的图像用作生成脚本中的 `--reference-images` 参数

这种方法通过为模型提供具体的视觉指导，而不是完全依赖文本描述，显著提高了生成质量。

## 提供商（Gemini / MiniMax / OpenAI 兼容）

该技能通过环境变量自动选择提供商（无需 CLI 修改）：

- `GEMINI_API_KEY` 设置 → 使用 Gemini（默认，不变）。
- 否则，`MINIMAX_API_KEY` 设置 → 使用 MiniMax (`/v1/image_generation`, 模型 `image-01`)。
- 否则，`IMAGE_GENERATION_API_KEY` 设置 → 使用 OpenAI 兼容的图像 API。
- 明确强制使用 `IMAGE_GENERATION_PROVIDER=gemini|minimax|openai`。
  `openai-compatible` 也接受作为 `openai` 的别名。

OpenAI 兼容设置：

- `IMAGE_GENERATION_API_KEY`（必需）
- `IMAGE_GENERATION_BASE_URL`（默认 `https://api.openai.com/v1`)
- `IMAGE_GENERATION_MODEL`（默认 `gpt-image-2.5-flare`)
- `IMAGE_GENERATION_SIZE`（可选固定尺寸覆盖）

文本到图像调用使用 `POST {base_url}/images/generations`。参考图像调用使用多部分 `POST {base_url}/images/edits`；中继可能支持生成而不支持编辑。响应可能包含 base64 图像数据、数据 URL 或可下载 URL。宽高比映射到 `1024x1024`、`1536x1024` 或 `1024x1536`，除非 `IMAGE_GENERATION_SIZE` 设置。输出扩展选择 API `output_format`：
`.jpg`/`.jpeg` 使用 `jpeg`，`.webp` 使用 `webp`，所有其他扩展使用 `png`。
当配置为 `dall-e-2` 或 `dall-e-3` 时，请求使用模型的支持尺寸和 `response_format=b64_json`；DALL-E 输出文件必须使用 `.png` 扩展。使用 DALL-E 模型进行参考图像编辑不受此技能支持；使用默认的 GPT 图像模型进行编辑。

MiniMax 可选覆盖：`MINIMAX_API_HOST`（默认 `https://api.minimaxi.com`），`MINIMAX_IMAGE_MODEL`（默认 `image-01`)。参考图像作为 MiniMax 的 `subject_reference` 角色图像发送。CLI 和 `--prompt-file` / `--reference-images` / `--output-file` / `--aspect-ratio` 参数对两个提供商都相同。

**MiniMax 提示处理（提供商内部）**。 编写与提供商无关——无论哪个提供商激活，都编写相同的结构化 JSON。MiniMax `image-01` 消费单个文本字符串，因此 MiniMax 路径本身只发送 JSON `prompt` 字段（其他字段如 `style` / `composition` / `negative_prompt` 适用于 Gemini 路径），并启用 `prompt_optimizer` 以便 MiniMax 在服务器端扩展。MiniMax 将提示限制为 1500 个字符；如果 `prompt` 字段更长，脚本会返回错误而不是调用 API。Gemini 路径接收完整的结构化 JSON。

## 注意事项

- 无论用户语言如何，始终使用英语编写提示
- JSON 格式确保结构化、可解析的提示
- 参考图像显著提升生成质量
- 迭代优化是获得最佳结果的正常过程
- 对于角色生成，包含详细的角色对象和整合的提示字段
