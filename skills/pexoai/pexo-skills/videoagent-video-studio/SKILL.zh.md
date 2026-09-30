---
name: videoagent-video-studio
description: 从文本或图像生成简短的AI视频——包括文本转视频、图像转视频和基于参考的生成——无需设置API密钥。当用户想要创建视频片段、动画化图像或根据描述生成视频时使用。
---

# 🎬 视频助手视频工作室

**使用场景：** 用户请求生成视频、从文本创建视频、动画化图像、制作短片或生成AI视频。

使用7种后端生成短AI视频。该技能选择正确的模式（文本到视频或图像到视频），增强提示以获得最佳效果，并返回视频URL。

---

## 快速参考

| 用户意图 | 模式 | 典型时长 |
|-------------|------|------------------|
| "制作一个..."（无图像） | `text-to-video` | 4–10秒 |
| "动画化这张图像" / "让这个动起来" | `image-to-video` | 4–6秒 |
| "把这个变成一个..." | `image-to-video` | 4–6秒 |
| 电影感、故事、广告 | 优先使用带有详细提示的`text-to-video` | 5–10秒 |

### 生成模式

| 模式 | 描述 | 模型 |
|------|-------------|--------|
| **文本到视频** | 仅文本提示 → 视频 | minimax, kling, veo, hunyuan, grok, seedance |
| **图像到视频** | 单个图像 + 提示 → 动画片段 | minimax, kling, veo, pixverse, grok, seedance |
| **参考基于** | 参考图像/视频 → 一致输出 | minimax, kling, veo, hunyuan, grok, seedance |

### 模型（使用`--model <id>`）

| 模型ID | 文本到视频 | 图像到视频 | 参考基于 | 备注 |
|----------|-----|-----|-----------|-------|
| `minimax` | ✅ | ✅ | ✅ | 主体参考图像，角色一致性 |
| `kling` | ✅ | ✅ | ✅ | 多元素/角色/关键帧（O3） |
| `veo` | ✅ | ✅ | ✅ | Google Veo 3.1，多个参考图像 |
| `hunyuan` | ✅ | — | ✅ | 视频到视频风格迁移 |
| `pixverse` | — | ✅ | — | 风格化图像到视频 |
| `grok` | ✅ | ✅ | ✅ | 通过参考视频进行视频编辑 |
| `seedance` | ✅ | ✅ | ✅ | Seedance 1.5 Pro，同步音频，4–12秒 |

完整模型详情和端点参考：[references/models.md](references/models.md)。

---

## 如何生成视频

### 第1步 — 选择模式并增强提示

- **文本到视频**：扩展主题、动作、摄像机运动、光照和风格。具体描述运动（例如："摄像机缓慢缩放"，"角色从左向右走"）。
- **图像到视频**：描述应用于图像的运动（例如："头发中轻柔的风"，"摄像机扫过场景"）。参考 [references/prompt_guide.md](references/prompt_guide.md) 获取模式。

### 第2步 — 运行脚本

**文本到视频：**
```bash
node {baseDir}/tools/generate.js \
  --mode text-to-video \
  --prompt "<增强提示>" \
  --duration <秒数> \
  --aspect-ratio <比例>
```

**图像到视频：**
```bash
node {baseDir}/tools/generate.js \
  --mode image-to-video \
  --prompt "<运动描述>" \
  --image-url "<公开图像URL>" \
  --duration <秒数> \
  --aspect-ratio <比例>
```

**参数：**

| 参数 | 默认 | 描述 |
|-----------|---------|-------------|
| `--mode` | `text-to-video` | `text-to-video` 或 `image-to-video` |
| `--prompt` | *(必需)* | 场景或运动描述 |
| `--image-url` | — | `image-to-video` 必需；公开图像URL |
| `--duration` | `5` | 长度（秒）（通常4–10） |
| `--aspect-ratio` | `16:9` | `16:9`，`9:16`，`1:1`，`4:3`，`3:4` |
| `--model` | `auto` | 模型ID（例如 `kling`，`veo`，`grok`，`seedance`）；`auto` = 代理选择 |

**其他命令：**

| 命令 | 描述 |
|---------|-------------|
| `node tools/generate.js --list-models` | 列出代理提供的可用模型 |
| `node tools/generate.js --status --job-id <id>` | 检查异步任务状态 |

### 第3步 — 返回结果

脚本返回JSON：

```json
{
  "success": true,
  "mode": "text-to-video",
  "videoUrl": "https://...",
  "duration": 5,
  "aspectRatio": "16:9"
}
```

将 `videoUrl` 发送给用户。

---

## 示例对话

**用户：** "生成一个雨中猫走的短片，电影感。"

```bash
node {baseDir}/tools/generate.js \
  --mode text-to-video \
  --prompt "一只猫在雨中行走，湿漉漉的街道，霓虹反射，电影感光照，慢动作，4K" \
  --duration 5 \
  --aspect-ratio 16:9
```

---

**用户：** "动画化这张照片" *(用户上传了一张风景照片)*

```bash
node {baseDir}/tools/generate.js \
  --mode image-to-video \
  --prompt "云朵轻轻掠过天空，草叶轻微摆动，电影感氛围" \
  --image-url "https://..." \
  --duration 5 \
  --aspect-ratio 16:9
```

---

**用户：** "制作一个10秒竖屏视频，展示咖啡倒入过程，慢动作。"

```bash
node {baseDir}/tools/generate.js \
  --mode text-to-video \
  --prompt "特写咖啡倒入白色杯中，慢动作，蒸汽升起，柔和光照，产品拍摄" \
  --duration 10 \
  --aspect-ratio 9:16
```

---

**用户：** "使用Google Veo制作电影感镜头。"

```bash
node {baseDir}/tools/generate.js \
  --mode text-to-video \
  --model veo \
  --prompt "一条龙在云中飞翔，电影感光照，8秒" \
  --duration 8 \
  --aspect-ratio 16:9
```

---

**用户：** "动画化这张肖像。"

```bash
node {baseDir}/tools/generate.js \
  --mode image-to-video \
  --model grok \
  --prompt "轻柔微笑，轻微转头" \
  --image-url "https://..." \
  --duration 5
```

---

## 设置

**默认情况下不使用API密钥。** 请求通过托管代理发送。设置自定义代理或令牌：

| 变量 | 必需 | 描述 |
|----------|----------|-------------|
| `VIDEO_STUDIO_PROXY_URL` | 否 | 代理基础URL |
| `VIDEO_STUDIO_TOKEN` | 否 | 如果代理需要，则为认证令牌 |

---

## 知识库

- **[references/prompt_guide.md](references/prompt_guide.md)** — 文本到视频和图像到视频的提示模式。
- **[references/models.md](references/models.md)** — 模型列表、功能和选择指南。
- **[references/calling_guide.md](references/calling_guide.md)** — 每个模型的端点详情、输入参数和特殊处理。
