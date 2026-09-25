# 🎨 VideoAgent 图像工作室

**使用场景：** 当用户要求生成、绘制、创建任何类型的图像、照片、插图、图标、标志或艺术作品时使用。

使用 8 种最先进的 AI 模型生成图像。此技能会自动选择最适合任务的模型，并处理所有复杂性（包括 Midjourney 的异步轮询），让您专注于对话。

---

## 快速参考

| 用户意图 | 模型 | 速度 |
|---|---|---|
| 艺术性、电影感、绘画风格 | `midjourney` | ~15s |
| 照片级真实感、肖像、产品 | `flux-pro` | ~8s |
| 通用、平衡 | `flux-dev` | ~10s |
| 快速草稿、快速迭代 | `flux-schnell` | ~2s |
| 带文字的图像、标志、海报 | `ideogram` | ~10s |
| 矢量艺术、图标、扁平化设计 | `recraft` | ~8s |
| 动画、风格化插图 | `sdxl` | ~5s |
| Gemini 驱动、一致性风格 | `nano-banana` | ~12s |

---

## 如何生成图像

### 第 1 步 — 增强提示

在调用脚本之前，根据所选模型添加适当的风格、光照和质量描述符来扩展用户的提示。

- **Midjourney**：添加 `cinematic lighting`（电影感光照）、`ultra detailed`（超精细）、`--v 7`、`--style raw`
- **Flux**：添加 `masterpiece`（杰作）、`highly detailed`（高度精细）、`sharp focus`（锐利对焦）、`professional photography`（专业摄影）
- **Ideogram**：明确说明文字内容、字体风格和布局
- **Recraft**：指定 `vector illustration`（矢量插图）、`flat design`（扁平化设计）、`icon style`（图标风格）

### 第 2 步 — 运行脚本

```bash
node {baseDir}/tools/generate.js \
  --model <model_id> \
  --prompt "<enhanced prompt>" \
  --aspect-ratio <ratio>
```

**所有参数：**

| 参数 | 默认值 | 描述 |
|---|---|---|
| `--model` | `flux-dev` | 上表中列出的模型 ID |
| `--prompt` | *(必需)* | 图像生成提示 |
| `--aspect-ratio` | `1:1` | `1:1`、`16:9`、`9:16`、`4:3`、`3:4`、`3:2`、`21:9` |
| `--num-images` | `1` | 图像数量（1–4；Midjourney 始终返回 4 张） |
| `--negative-prompt` | — | 要避免的内容（Midjourney 不支持） |
| `--seed` | — | 用于可重复性的种子 |

### 第 3 步 — 返回结果

脚本始终等待并返回最终图像 URL。无需轮询。

```json
{
  "success": true,
  "model": "flux-pro",
  "imageUrl": "https://...",
  "images": ["https://..."]
}
```

将 `imageUrl` 发送给用户。

---

## Midjourney 操作

在 Midjourney 生成 4 图网格后，向用户提供以下选项：

```bash
# 放大图像 #2（微妙，保留细节）
node {baseDir}/tools/generate.js \
  --model midjourney \
  --action upscale \
  --index 2 \
  --job-id <job_id>

# 创建图像 #3 的强烈变体
node {baseDir}/tools/generate.js \
  --model midjourney \
  --action variation \
  --index 3 \
  --job-id <job_id> \
  --variation-type 1

# 使用相同提示重新生成
node {baseDir}/tools/generate.js \
  --model midjourney \
  --action reroll \
  --job-id <job_id>
```

**放大类型：** `0` = 微妙（默认，适合照片）、`1` = 创意（适合插图）

**变体类型：** `0` = 微妙（默认）、`1` = 强烈（戏剧性变化）

---

## 示例对话

**用户：** "绘制一只雪豹在雪山上的场景，带有电影感光照"

```bash
# 选择 midjourney 以获得艺术质量
node {baseDir}/tools/generate.js \
  --model midjourney \
  --prompt "一只雄伟的雪豹在雪山之巅，电影感光照，戏剧性氛围，超精细 --ar 16:9 --v 7" \
  --aspect-ratio 16:9
```

> 🎨 完成！要放大哪一张？（U1-U4）还是创建变体？（V1-V4）

---

**用户：** "使用 Flux 生成香水产品海报，白色背景"

```bash
# 选择 flux-pro 以获得照片级的产品拍摄效果
node {baseDir}/tools/generate.js \
  --model flux-pro \
  --prompt "一瓶奢华香水在干净的白色背景下，专业产品摄影，柔和阴影，8k，高度精细" \
  --aspect-ratio 3:4
```

---

**用户：** "给我一个快速草稿"

```bash
# flux-schnell 用于即时预览
node {baseDir}/tools/generate.js \
  --model flux-schnell \
  --prompt "..." \
  --aspect-ratio 1:1
```

---

**用户：** "为我制作一个 App 图标，扁平化风格，蓝色主题"

```bash
# recraft 用于矢量/图标风格
node {baseDir}/tools/generate.js \
  --model recraft \
  --prompt "一个极简的扁平化设计 App 图标，蓝色配色方案，简单的几何形状，矢量风格，白色背景"
```

---

## 安装

**无需 API 密钥！** 所有请求都通过一个托管代理，该代理在服务器端处理身份验证。

该技能即用即装——只需安装并使用。

### 高级：自定义代理或令牌

如果您想使用自己的代理或持久令牌，请设置以下环境变量：

```json
{
  "skills": {
    "entries": {
      "videoagent-image-studio": {
        "enabled": true,
        "env": {
          "IMAGE_STUDIO_PROXY_URL": "https://your-proxy.vercel.app",
          "IMAGE_STUDIO_TOKEN": "your_token_here"
        }
      }
    }
  }
}
```

| 变量 | 必需 | 描述 |
|---|---|---|
| `IMAGE_STUDIO_PROXY_URL` | 否 | 自定义代理基础 URL（默认：`https://image-gen-proxy.vercel.app`） |
| `IMAGE_STUDIO_TOKEN` | 否 | 持久令牌（如果未设置，将自动获取，每个令牌 100 次免费使用） |

要部署自己的代理，请参考 [videoagent-audio-studio 代理](../videoagent-audio-studio/proxy/) 作为参考实现。您需要 `FAL_KEY` 和 `LEGNEXT_KEY` 作为 Vercel 环境变量。

---

## 更新日志

### v2.0.0
- **简化异步**：脚本现在会阻塞直到 Midjourney 完成。SKILL.md 说明中不再需要 `--async` / `--poll` 标志。
- **统一输出格式**：所有模型都返回相同的 `{ success, imageUrl, images }` 结构。
- **Nano Banana 的参考图像**：传递 `--reference-images "url1,url2"` 以在生成过程中保持角色/风格一致性。

### v1.3.0
- 添加了 Midjourney 的非阻塞异步模式 (`--async` + `--poll`)。

### v1.2.0
- Midjourney 快速模式默认启用（~10-20s）。

### v1.1.0
- Midjourney 提供商从 TTAPI 切换到 Legnext.ai 以获得更好的稳定性。

### v1.0.0
- 初始发布，支持 Midjourney、Flux、SDXL、Nano Banana、Ideogram、Recraft。
