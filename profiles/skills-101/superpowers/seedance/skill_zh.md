> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# Seedance 2.0 视频生成

使用 ByteDance 的 Seedance 2.0 通过 [inference.sh](https://inference.sh) CLI 生成带同步音频的视频。

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

belt app run bytedance/seedance-2-0 --input '{
  "prompt": "一个爵士乐队在昏暗的俱乐部里表演",
  "generate_audio": true
}'
```

## 模型

| 模型 | 应用 ID | 最佳用途 |
|------|--------|----------|
| Seedance 2.0 | `bytedance/seedance-2-0` | 最佳质量，最高 1080p |
| Seedance 2.0 快速 | `bytedance/seedance-2-0-fast` | 更快生成，最高 720p |
| Seedance 2.0 工作室 | `bytedance/seedance-2-0-studio` | 质量 + 私有资产库用于肖像一致性 |
| Seedance 2.0 工作室 快速 | `bytedance/seedance-2-0-studio-fast` | 快速 + 私有资产库用于肖像一致性 |

所有模型都支持文本到视频、图像到视频、多模态参考到视频以及同步音频生成。工作室变体会自动将参考图像上传到 BytePlus 的私有虚拟肖像库以增强角色一致性 - 特别适用于面部和品牌角色。

## 模式

模型根据您的输入确定生成模式。这些模式是**互斥的** - 要么使用第一帧/最后一帧，要么使用参考输入，不能同时使用。

| 模式 | 输入 | 描述 |
|------|--------|-------------|
| 文本到视频 | `prompt` 仅 | 从文本描述生成视频 |
| 图像到视频 | `prompt` + `image` | 动画化静态图像（第一帧） |
| 第一帧+最后一帧 | `prompt` + `image` + `end_image` | 控制起始和结束帧 |
| 多模态参考 | `prompt` + `reference_images`/`reference_videos`/`reference_audios` | 使用参考材料指导生成 |

## 示例

### 带音频的文本到视频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "风暴中海水拍打岩石，戏剧性电影镜头",
  "generate_audio": true,
  "duration": 10,
  "ratio": "16:9"
}'
```

### 快速模式（更便宜）

```bash
belt app run bytedance/seedance-2-0-fast --input '{
  "prompt": "蝴蝶在慢动作中落在花朵上",
  "generate_audio": true
}'
```

### 图像到视频

将静态图像动画化为视频：

```bash
belt app run bytedance/seedance-2-0 --input '{
  "image": "https://your-image.jpg",
  "prompt": "轻柔的相机运动，树叶在风中沙沙作响",
  "generate_audio": true
}'
```

### 带起始和结束帧的图像到视频

```bash
belt app run bytedance/seedance-2-0 --input '{
  "image": "https://start-frame.jpg",
  "end_image": "https://end-frame.jpg",
  "prompt": "场景之间的平滑过渡",
  "generate_audio": true
}'
```

### 多图像参考

使用多个参考图像来指导角色外观、服装和场景元素：

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "Image 1 中的女孩穿着 Image 2 中的服装走过 Image 3 中的咖啡馆",
  "reference_images": [
    "https://character-portrait.jpg",
    "https://outfit-reference.jpg",
    "https://cafe-scene.jpg"
  ],
  "generate_audio": true,
  "duration": 8
}'
```

### 视频编辑（替换元素）

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "将 Video 1 中的香水替换为 Image 1 中的面霜，保留所有原始动作和相机工作",
  "reference_images": ["https://face-cream.jpg"],
  "reference_videos": ["https://original-video.mp4"],
  "generate_audio": true
}'
```

### 视频扩展（拼接片段）

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "Video 1 平滑过渡到 Video 2，然后相机进入 Video 3 中的画作",
  "reference_videos": [
    "https://clip1.mp4",
    "https://clip2.mp4",
    "https://clip3.mp4"
  ],
  "generate_audio": true,
  "duration": 8
}'
```

### 带音频的参考

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "Image 1 中的音乐家表演 Audio 1 中的歌曲，声音风格参考自 Audio 1",
  "reference_images": ["https://musician.jpg"],
  "reference_audios": ["https://music.mp3"],
  "generate_audio": true
}'
```

### 工作室模式（肖像一致性）

工作室变体会将图像上传到 BytePlus 的私有资产库以增强面部/角色一致性：

```bash
belt app run bytedance/seedance-2-0-studio --input '{
  "prompt": "Image 1 中的人对着镜头微笑，黄金时刻光照，电影感",
  "reference_images": ["https://portrait.jpg"],
  "safety_identifier": "user-abc123",
  "generate_audio": true
}'
```

### 带多个参考的产品广告

```bash
belt app run bytedance/seedance-2-0 --input '{
  "prompt": "第一人称视角产品广告。开帧是 Image 1，手拿起产品。相机推近显示细节。使用 Video 1 的相机运动风格。背景音乐来自 Audio 1。",
  "reference_images": ["https://product-hero.jpg", "https://product-detail.jpg"],
  "reference_videos": ["https://camera-style.mp4"],
  "reference_audios": ["https://bgm.mp3"],
  "generate_audio": true,
  "ratio": "9:16",
  "duration": 11
}'
```

## 提示指南

在提示中引用参考资产，使用**类型 + 索引**：`Image 1`，`Image 2`，`Video 1`，`Audio 1`。索引是您提供的数组中该类型的顺序位置。**不要**在提示中使用资产 ID。

**多模态参考公式：**
- 图像参考：`参考 Image N 中的 [主体] 生成 [场景]，保持 [主体] 一致`
- 视频参考：`参考 Video N 中的 [相机运动/动作]`
- 音频参考：`[角色] 说：[对话]，声音风格参考自 Audio N]`

**视频编辑公式：**
- 添加：`在 [Video N] 的 [时间] 添加 [元素]`
- 删除：`从 [Video N] 删除 [元素]，保持其余部分不变`
- 修改：`在 [Video N] 中将 [元素] 替换为 [新元素]`

**视频扩展公式：**
- 前进：`生成 [Video N] 之后的内容：[描述]`
- 后退：`扩展 [Video N] 的开头：[描述]`
- 拼接：`[Video 1] + [过渡] + 然后是 [Video 2]`

## 参数

| 参数 | 类型 | 默认值 | 描述 |
|------|--------|---------|-------------|
| `prompt` | string | required | 视频的文本描述 |
| `generate_audio` | boolean | true | 生成同步音频 |
| `duration` | integer | 5 | 持续时间（秒）（4-15），或 -1 为自动 |
| `ratio` | enum | adaptive | 21:9, 16:9, 4:3, 1:1, 3:4, 9:16，或 adaptive |
| `resolution` | enum | 720p | 480p, 720p, 1080p（Fast：仅 480p, 720p） |
| `seed` | integer | -1 | 用于可重复性的种子（-1 为随机） |
| `watermark` | boolean | false | 在输出中添加水印 |
| `safety_identifier` | string | - | 用于安全策略的唯一最终用户标识符（最多 64 个字符，推荐为用户 ID 的哈希值） |
| `image` | file | - | 第一帧图像（与参考输入互斥） |
| `end_image` | file | - | 最后一帧图像（需要 `image`） |
| `reference_images` | file[] | - | 参考图像，最多 9 个（与图像/`end_image` 互斥） |
| `reference_videos` | file[] | - | 参考视频，最多 3 个。每个最长 15 秒，总最长 15 秒。mp4/mov |
| `reference_audios` | file[] | - | 参考音频，最多 3 个。每个最长 15 秒，总最长 15 秒。wav/mp3。至少需要一个图像或视频 |

## 定价

| 模型 | 定价 |
|------|---------|
| Seedance 2.0 | $4.30-$7.70/M 令牌（根据分辨率和输入类型变化） |
| Seedance 2.0 快速 | $3.30-$5.60/M 令牌 |

令牌公式：`(宽度 x 高度 x 帧率 x 持续时间) / 1024`

## 搜索 Seedance 应用

```bash
belt app search "seedance"
```

## 相关技能

```bash
# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# 所有视频生成模型
npx skills add inference-sh/skills@ai-video-generation

# Google Veo
npx skills add inference-sh/skills@google-veo

# 图像生成（用于图像到视频）
npx skills add inference-sh/skills@ai-image-generation

# AI 虚拟形象 & 嘴型同步
npx skills add inference-sh/skills@ai-avatar-video
```

浏览所有视频应用：`belt app list --category video`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 通过 CLI 运行应用
- [流式传输结果](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
- [内容管道示例](https://inference.sh/docs/examples/content-pipeline) - 构建媒体工作流
