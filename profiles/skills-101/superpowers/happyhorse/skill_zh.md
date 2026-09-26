> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# HappyHorse 1.0 视频生成

通过 [inference.sh](https://inference.sh) CLI 使用阿里巴巴 HappyHorse 1.0 模型生成和编辑物理逼真的视频。

## 快速入门

> 需要 inference.sh CLI (`belt`)。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

belt app run alibaba/happyhorse-1-0-t2v --input '{"prompt": "一匹马在阳光明媚的草地上奔跑"}'
```

## HappyHorse 模型

| 模型 | 应用 ID | 最适合 |
|-------|--------|----------|
| T2V | `alibaba/happyhorse-1-0-t2v` | 文本到视频，物理逼真运动 |
| I2V | `alibaba/happyhorse-1-0-i2v` | 动画化单张图像 |
| R2V | `alibaba/happyhorse-1-0-r2v` | 保留最多 9 张参考图像中的角色 |
| 视频编辑 | `alibaba/happyhorse-1-0-video-edit` | 使用自然语言编辑现有视频 |

所有模型支持 720P/1080P 分辨率，最长 15 秒时长。

## 示例

### 文本到视频

```bash
belt app run alibaba/happyhorse-1-0-t2v --input '{
  "prompt": "一只金毛猎犬在公园里穿过秋天的落叶，慢动作",
  "duration": 10,
  "resolution": "1080P",
  "ratio": "16:9"
}'
```

### 图像到视频

动画化静态图像：

```bash
belt app run alibaba/happyhorse-1-0-i2v --input '{
  "first_frame": "https://your-image.jpg",
  "prompt": "轻柔的相机变焦，天空中的云彩移动",
  "duration": 8,
  "resolution": "720P"
}'
```

### 参考到视频（角色保留）

生成保留参考图像（最多 9 张）中角色的视频：

```bash
belt app run alibaba/happyhorse-1-0-r2v --input '{
  "prompt": "一位女士走过繁忙的市场街道",
  "reference_images": ["https://portrait.jpg"],
  "duration": 10,
  "resolution": "720P"
}'
```

### 多角色参考

```bash
belt app run alibaba/happyhorse-1-0-r2v --input '{
  "prompt": "两位朋友坐在咖啡馆里喝咖啡",
  "reference_images": ["https://person1.jpg", "https://person2.jpg"],
  "ratio": "16:9"
}'
```

### 视频编辑

使用自然语言指令编辑现有视频：

```bash
belt app run alibaba/happyhorse-1-0-video-edit --input '{
  "video": "https://your-video.mp4",
  "prompt": "将背景改为雪山的风景"
}'
```

### 带参考图像的视频编辑

```bash
belt app run alibaba/happyhorse-1-0-video-edit --input '{
  "video": "https://your-video.mp4",
  "prompt": "用参考图像中的角色替换人物",
  "reference_images": ["https://character.jpg"]
}'
```

### 带音频控制的视频编辑

```bash
belt app run alibaba/happyhorse-1-0-video-edit --input '{
  "video": "https://your-video.mp4",
  "prompt": "让场景看起来像雨天",
  "audio_setting": "generate"
}'
```

## 定价

| 分辨率 | 价格 |
|------------|-------|
| 720P | 每秒 0.14 美元 |
| 1080P | 每秒 0.24 美元 |

视频编辑按输入 + 输出时长计费。

## 参数（T2V）

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `prompt` | 字符串 | 必填 | 视频的文本描述 |
| `duration` | 整数 | 5 | 时长（秒）（3–15） |
| `resolution` | 枚举 | 720P | 720P 或 1080P |
| `ratio` | 枚举 | 16:9 | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 |
| `seed` | 整数 | 随机 | 可重复生成的 |
| `watermark` | 布尔值 | false | 添加 HappyHorse 水印 |

## 参数（I2V）

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `first_frame` | 文件 | 必填 | 第一帧图像（JPEG, PNG, WebP） |
| `prompt` | 字符串 | - | 可选的文本描述 |
| `duration` | 整数 | 5 | 时长（秒）（3–15） |
| `resolution` | 枚举 | 720P | 720P 或 1080P |
| `seed` | 整数 | 随机 | 可重复生成的 |

## 参数（R2V）

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `prompt` | 字符串 | 必填 | 场景的文本描述 |
| `reference_images` | 数组 | 必填 | 最多 9 张角色参考图像 |
| `duration` | 整数 | 5 | 时长（秒）（3–15） |
| `resolution` | 枚举 | 720P | 720P 或 1080P |
| `ratio` | 枚举 | 16:9 | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9 |
| `seed` | 整数 | 随机 | 可重复生成的 |

## 参数（视频编辑）

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `video` | 文件 | 必填 | 要编辑的视频（MP4/MOV, H.264） |
| `prompt` | 字符串 | 必填 | 编辑指令 |
| `reference_images` | 数组 | - | 最多 5 张参考图像 |
| `audio_setting` | 枚举 | auto | auto, generate, 或 keep_original |
| `resolution` | 枚举 | 720P | 720P 或 1080P |
| `seed` | 整数 | 随机 | 可重复生成的 |

## 搜索 HappyHorse 应用

```bash
belt app search "happyhorse"
```

## 相关技能

```bash
# 完整平台技能（所有应用）
npx skills add inference-sh/skills@infsh-cli

# 所有视频生成模型
npx skills add inference-sh/skills@ai-video-generation

# Seedance 2.0
npx skills add inference-sh/skills@seedance

# Google Veo
npx skills add inference-sh/skills@google-veo

# 图像生成（用于图像到视频）
npx skills add inference-sh/skills@ai-image-generation
```

浏览所有视频应用：`belt app list --category video`

## 文档

- [运行应用](https://inference.sh/docs/apps/running) - 如何通过 CLI 运行应用
- [流式传输结果](https://inference.sh/docs/api/sdk/streaming) - 实时进度更新
- [内容管道示例](https://inference.sh/docs/examples/content-pipeline) - 构建媒体工作流
