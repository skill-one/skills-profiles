# 🎬 VideoAgent 视频工作室

**使用场景：** 用户请求生成视频、从文本创建视频、为图像添加动画、制作短片或生成 AI 视频。

使用 7 种后端生成短 AI 视频。该技能会根据情况选择正确的模式（文本到视频或图像到视频），优化提示词以获得最佳效果，并返回视频链接。

---

## 快速参考

| 用户意图 | 模式 | 典型时长 |
|----------|------|----------|
| "制作一个..."（无图像） | `text-to-video` | 4–10 秒 |
| "让这张图像动起来" / "让这个动起来" | `image-to-video` | 4–6 秒 |
| "把这个变成一个..." | `image-to-video` | 4–6 秒 |
| 电影感、故事、广告 | 优先使用 `text-to-video` 并提供详细提示词 | 5–10 秒 |

### 生成模式

| 模式 | 描述 | 模型 |
|------|------|------|
| **文本到视频** | 仅文本提示词 → 视频 | minimax, kling, veo, hunyuan, grok, seedance |
| **图像到视频** | 单个图像 + 提示词 → 动画片段 | minimax, kling, veo, pixverse, grok, seedance |
| **参考模式** | 参考图像/视频 → 保持一致性输出 | minimax, kling, veo, hunyuan, grok, seedance |

### 模型（使用 `--model <id>`）

| 模型 ID | 文本到视频 | 图像到视频 | 参考模式 | 备注 |
|----------|------------|------------|----------|------|
| `minimax` | ✅ | ✅ | ✅ | 主体参考图像，角色一致性 |
| `kling` | ✅ | ✅ | ✅ | 多元素/角色/关键帧 (O3) |
| `veo` | ✅ | ✅ | ✅ | Google Veo 3.1，多个参考图像 |
| `hunyuan` | ✅ | — | ✅ | 视频到视频风格迁移 |
| `pixverse` | — | ✅ | — | 风格化图像到视频 |
| `grok` | ✅ | ✅ | ✅ | 通过参考视频进行视频编辑 |
| `seedance` | ✅ | ✅ | ✅ | Seedance 1.5 Pro，同步音频，4–12 秒 |

完整模型详情和端点参考：[references/models.md](references/models.md)。

---

## 如何生成视频

### 第 1 步 — 选择模式并优化提示词

- **文本到视频**：扩展主题、动作、摄像机运动、光照和风格。具体描述运动（例如 "摄像机缓慢缩放"，"角色从左向右行走"）。
- **图像到视频**：描述应用于图像的运动（例如 "头发中轻柔的风"，"摄像机扫过场景"）。参考 [references/prompt_guide.md](references/prompt_guide.md) 获取提示词模式。

### 第 2 步 — 运行脚本

**文本到视频：**
```bash
node {baseDir}/tools/generate.js \
  --mode text-to-video \
  --prompt "<优化后的提示词>" \
  --duration <秒数> \
  --aspect-ratio <比例>
```

**图像到视频：**
```bash
node {baseDir}/tools/generate.js \
  --mode image-to-video \
  --prompt "<运动描述>" \
  --image-url "<公开图像链接>" \
  --duration <秒数> \
  --aspect-ratio <比例>
```

**参数：**

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `--mode` | `text-to-video` | `text-to-video` 或 `image-to-video` |
| `--prompt` | *(必需)* | 场景或运动描述 |
| `--image-url` | — | `image-to-video` 必需；公开图像链接 |
| `--duration` | `5` | 时长（通常 4–10 秒） |
| `--aspect-ratio` | `16:9` | `16:9`、`9:16`、`1:1`、`4:3`、`3:4` |
| `--model` | `auto` | 模型 ID（例如 `kling`、`veo`、`grok`、`seedance`）；`auto` = 代理选择 |

**其他命令：**

| 命令 | 描述 |
|------|------|
| `node tools/generate.js --list-models` | 列出代理提供的可用模型 |
| `node tools/generate.js --status --job-id <id>` | 检查异步任务状态 |

### 第 3 步 — 返回结果

脚本返回 JSON：

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

**用户：** "生成一段猫在雨中行走的短片，电影感。"

```bash
node {baseDir}/tools/generate.js \
  --mode text-to-video \
  --prompt "一只猫在雨中行走，湿漉漉的街道，霓虹反射，电影感光照，慢动作，4K" \
  --duration 5 \
  --aspect-ratio 16:9
```

---

**用户：** "为这张照片添加动画" *(用户上传了一张风景照片)*

```bash
node {baseDir}/tools/generate.js \
  --mode image-to-video \
  --prompt "云朵缓缓移动，草地轻微摆动，电影感氛围" \
  --image-url "https://..." \
  --duration 5 \
  --aspect-ratio 16:9
```

---

**用户：** "制作一个 10 秒的竖屏视频，展示咖啡倒入过程，慢动作。"

```bash
node {baseDir}/tools/generate.js \
  --mode text-to-video \
  --prompt "特写咖啡倒入白色杯中，慢动作，蒸汽升起，柔和光照，产品拍摄" \
  --duration 10 \
  --aspect-ratio 9:16
```

---

**用户：** "使用 Google Veo 进行电影感拍摄。"

```bash
node {baseDir}/tools/generate.js \
  --mode text-to-video \
  --model veo \
  --prompt "一条龙在云层中飞翔，电影感光照，8 秒" \
  --duration 8 \
  --aspect-ratio 16:9
```

---

**用户：** "为这张肖像添加动画。"

```bash
node {baseDir}/tools/generate.js \
  --mode image-to-video \
  --model grok \
  --prompt "轻柔微笑，轻微转头" \
  --image-url "https://..." \
  --duration 5
```

---

## 配置

**默认情况下不使用 API 密钥。** 请求通过托管代理发送。设置自定义代理或令牌：

| 变量 | 必需 | 描述 |
|------|------|------|
| `VIDEO_STUDIO_PROXY_URL` | 否 | 代理基础 URL |
| `VIDEO_STUDIO_TOKEN` | 否 | 如果代理需要，则提供认证令牌 |

---

## 知识库

- **[references/prompt_guide.md](references/prompt_guide.md)** — 文本到视频和图像到视频的提示词模式。
- **[references/models.md](references/models.md)** — 模型列表、功能和选择指南。
- **[references/calling_guide.md](references/calling_guide.md)** — 每个模型的端点详情、输入参数和特殊处理。
