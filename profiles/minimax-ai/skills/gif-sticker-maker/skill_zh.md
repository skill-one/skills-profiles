# GIF贴纸制作器

将用户照片转换为4个动画GIF贴纸（Funko Pop / Pop Mart风格）。

## 风格规范

- Funko Pop / Pop Mart盲盒3D人偶
- C4D / Octane渲染质量
- 白色背景，柔和的影棚灯光
- 标题：黑色文字+白色轮廓，位于图片底部

## 前置条件

在开始任何生成步骤之前，请确保：

1. **Python venv**已激活，并安装了[requirements.txt](references/requirements.txt)中的依赖项
2. **`MINIMAX_API_KEY`**已导出（例如 `export MINIMAX_API_KEY='your-key'`）
3. **`ffmpeg`**已存在于PATH中（用于步骤3的GIF转换）

如果缺少任何前置条件，请先设置它。在未全部设置完成前，请勿继续生成。

## 工作流程

### 步骤0：收集标题

向用户（使用他们的语言）询问：
> "您希望自定义贴纸的标题，还是使用默认值？"

- **自定义**：收集4个简短标题（1-3个词）。动作将自动匹配标题含义。
- **默认**：根据**检测到的用户语言**查找[captions table](references/captions.md)。**切勿混合语言。**

### 步骤1：生成4个静态贴纸图片

**工具**：`scripts/minimax_image.py`

1. 分析用户的照片——识别主题类型（人物 / 动物 / 物体 / 标志）。
2. 对于4个贴纸中的每一个，根据[assets/image-prompt-template.txt](assets/image-prompt-template.txt)模板填充`{action}`和`{caption}`来构建提示。
3. **如果主题是人物**：传递`--subject-ref <user_photo_path>`，以便生成的人偶保留人物的真正面部特征。
4. 生成（所有4个都是独立的——**并行运行**）：

```bash
python3 scripts/minimax_image.py "<prompt>" -o output/sticker_hi.png --ratio 1:1 --subject-ref <photo>
python3 scripts/minimax_image.py "<prompt>" -o output/sticker_laugh.png --ratio 1:1 --subject-ref <photo>
python3 scripts/minimax_image.py "<prompt>" -o output/sticker_cry.png --ratio 1:1 --subject-ref <photo>
python3 scripts/minimax_image.py "<prompt>" -o output/sticker_love.png --ratio 1:1 --subject-ref <photo>
```

> `--subject-ref` 仅适用于人物主题（API限制：类型=character）。
> 对于动物/物体/标志，请省略该标志并依赖文本描述。

### 步骤2：为每张图片制作动画→视频

**工具**：`scripts/minimax_video.py`配合`--image`标志（图片转视频模式）

对于每个贴纸图片，根据[assets/video-prompt-template.txt](assets/video-prompt-template.txt)模板构建提示，然后：

```bash
python3 scripts/minimax_video.py "<prompt>" --image output/sticker_hi.png -o output/sticker_hi.mp4
python3 scripts/minimax_video.py "<prompt>" --image output/sticker_laugh.png -o output/sticker_laugh.mp4
python3 scripts/minimax_video.py "<prompt>" --image output/sticker_cry.png -o output/sticker_cry.mp4
python3 scripts/minimax_video.py "<prompt>" --image output/sticker_love.png -o output/sticker_love.mp4
```

所有4个调用都是独立的——**并行运行**。

### 步骤3：将视频→GIF转换

**工具**：`scripts/convert_mp4_to_gif.py`

```bash
python3 scripts/convert_mp4_to_gif.py output/sticker_hi.mp4 output/sticker_laugh.mp4 output/sticker_cry.mp4 output/sticker_love.mp4
```

输出GIF文件与每个MP4文件一起（例如 `sticker_hi.gif`）。

### 步骤4：交付

输出格式（严格顺序）：
1. 简要状态行（例如 "已创建4个贴纸："）
2. `<deliver_assets>`块，包含所有GIF文件
3. **交付assets后无任何文本**

```xml
<deliver_assets>
<item><path>output/sticker_hi.gif</path></item>
<item><path>output/sticker_laugh.gif</path></item>
<item><path>output/sticker_cry.gif</path></item>
<item><path>output/sticker_love.gif</path></item>
</deliver_assets>
```

## 默认动作

| # | 动作 | 文件名ID | 动画 |
|---|------|----------|------|
| 1 | 欢快挥手 | hi | 挥手，轻微点头 |
| 2 | 大笑 | laugh | 挥舞大笑，眯眼 |
| 3 | 哭泣流泪 | cry | 流泪，身体颤抖 |
| 4 | 心形手势 | love | 心形手，眼睛闪亮 |

参见[references/captions.md](references/captions.md)获取多语言默认标题。

## 规则

- 检测用户语言，所有输出均遵循该语言
- 标题必须来自[references/captions.md](references/captions.md)中与用户语言列匹配的标题——切勿混合语言
- 所有图片提示必须使用**英语**，无论用户语言如何（仅标题文本本地化）
- `<deliver_assets>`必须在响应中最后出现，之后无任何文本
