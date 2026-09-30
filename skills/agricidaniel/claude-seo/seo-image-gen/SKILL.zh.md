---
name: seo-image-gen
description: 用于SEO资产的AI图像生成：OG/社交预览图像、博客主图像、模式图像、产品摄影、信息图表。由Gemini通过nanobanana-mcp提供支持。需要安装banana扩展。当用户说“生成图像”、“OG图像”、“社交预览”、“主图像”、“博客图像”、“产品照片”、“信息图表”、“SEO图像”、“创建视觉”、“图像生成”、“favicon”、“模式图像”、“pinterest pin”、“生成视觉”、“横幅”或“缩略图”时使用。
---

# SEO 图片生成：用于 SEO 资产的 AI 图片生成（扩展）

使用 Gemini 的图片生成功能，通过 banana 创意总监管道生成适用于 SEO 的生产就绪图片。将 SEO 需求映射到优化的域名模式、宽高比和分辨率默认值。

## 架构说明

此扩展基于 [Claude Banana](https://github.com/AgriciDaniel/banana-claude)，是 Claude Code 的独立 AI 图片生成技能。

该技能包含两个具有不同角色的组件：
- **SKILL.md**（此文件）：处理交互式 `/seo image-gen` 命令以生成图片
- **代理** (`agents/seo-image-gen.md`)：在 `/seo audit` 过程中仅用于审计的分析员，用于评估现有的 OG/社交图片并生成生成计划（从不自动生成）

## 前置条件

此技能需要安装 banana 扩展：
```bash
./extensions/banana/install.sh
```

**检查可用性**：在使用任何图片生成工具之前，通过检查 `gemini_generate_image` 或 `set_aspect_ratio` 工具是否可用来验证 MCP 服务器是否已连接。如果工具不可用，请告知用户扩展未安装并提供安装说明。

## 快速参考

| 命令 | 它的作用 |
|------|---------|
| `/seo image-gen og <描述>` | 生成 OG/社交预览图片（1200x630 感觉） |
| `/seo image-gen hero <描述>` | 博客英雄图片（宽屏，戏剧性） |
| `/seo image-gen product <描述>` | 产品摄影（干净，白色背景） |
| `/seo image-gen infographic <描述>` | 信息图表视觉（垂直，数据密集） |
| `/seo image-gen custom <描述>` | 使用完整的创意总监管道生成自定义图片 |
| `/seo image-gen batch <描述> [N]` | 生成 N 个变体（默认：3 个） |

## SEO 图片使用案例

每个使用案例映射到预配置的 banana 参数：

| 使用案例 | 宽高比 | 分辨率 | 域名模式 | 备注 |
|---------|--------|--------|---------|------|
| **OG/社交预览** | `16:9` | `1K` | 产品或 UI/Web | 干净，专业，文本友好 |
| **博客英雄** | `16:9` | `2K` | 电影或编辑 | 戏剧性，氛围，编辑质量 |
| **模式图片** | `4:3` | `1K` | 产品 | 干净，描述性，模式 ImageObject |
| **社交方形** | `1:1` | `1K` | UI/Web | 平台优化的方形 |
| **产品照片** | `4:3` | `2K` | 产品 | 白色背景，工作室灯光 |
| **信息图表** | `2:3` | `4K` | 信息图表 | 数据密集，垂直布局 |
| **favicon/图标** | `1:1` | `512` | Logo | 最小化，可缩放，可识别 |
| **Pinterest 钉子** | `2:3` | `2K` | 编辑 | 高垂直卡片 |

## 生成管道

对于每个生成请求：

1. **从命令或上下文识别使用案例**（og，hero，product 等）
2. **应用 SEO 默认值** 从上表中的使用案例
3. **通过 `set_aspect_ratio` MCP 工具设置宽高比**
4. **使用 banana 创意总监管道构建推理摘要**：
   - 使用 `${CLAUDE_SKILL_DIR}` 作为已安装技能的根目录
   - 加载 `${CLAUDE_SKILL_DIR}/references/prompt-engineering.md` 用于 6 组件系统
   - 应用域名模式强调（主题 30%，风格 25%，上下文 15% 等）
   - 具体且直观：描述相机看到的内容
5. **通过 `gemini_generate_image` MCP 工具生成**
6. **生成后的 SEO 检查清单**（见下文）

### 检查预设

如果用户提到品牌或已配置 SEO 预设：
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run --extension banana presets.py list
```
加载匹配的预设并作为默认值应用。还检查 `${CLAUDE_SKILL_DIR}/references/seo-image-presets.md` 以获取 SEO 特定的预设模板。

## 生成后 SEO 检查清单

每次成功生成后，指导用户：

1. **替代文本**：为生成的图片编写描述性、关键词丰富的替代文本
2. **文件命名**：重命名为 SEO 友好的格式：`keyword-description-widthxheight.webp`
3. **WebP 转换**：转换为 WebP 以优化页面速度：
   ```bash
   magick output.png -quality 85 output.webp
   ```
4. **文件大小**：目标为英雄图片小于 200KB，缩略图小于 100KB
5. **模式标记**：建议为生成的图片使用 `ImageObject` 模式：
   ```json
   {
     "@type": "ImageObject",
     "url": "https://example.com/images/keyword-description.webp",
     "width": 1200,
     "height": 630,
     "caption": "描述性标题，包含目标关键词"
   }
   ```
6. **OG 元标记**：对于社交预览图片，提醒关于：
   ```html
   <meta property="og:image" content="https://example.com/images/og-image.webp" />
   <meta property="og:image:width" content="1200" />
   <meta property="og:image:height" content="630" />
   <meta property="og:image:alt" content="描述性替代文本" />
   ```

## 成本意识

图片生成需要花钱。保持透明：
- 在生成之前显示估计成本（尤其是批量生成时）
- 记录每次生成：`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run --extension banana cost_tracker.py log --model MODEL --resolution RES --prompt "brief"`
- 如果用户询问使用情况，运行 `cost_tracker.py summary`

定价不是硬编码的。检查当前 Google 定价：[https://ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing)，将日期值存储在 `~/.banana/pricing.json` 中，并将估计值视为近似值。

## 模型路由

| 场景 | 模型 | 原因 |
|------|------|------|
| OG 图片，社交预览 | 验证的 `NANOBANANA_MODEL` @ 1K | 快速，成本意识 |
| 英雄图片，产品照片 | 如果支持，验证 `NANOBANANA_MODEL` @ 2K | 质量 + 细节 |
| 带文本的信息图表 | 如果支持，验证 `NANOBANANA_MODEL` @ 2K，思考：高 | 更好的文本渲染 |
| 快速草稿 | 如果支持，验证 `NANOBANANA_MODEL` @ 512 | 快速迭代 |

## 错误处理

| 错误 | 解决方案 |
|------|---------|
| MCP 未配置 | 运行 `./extensions/banana/install.sh` 或 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run --extension banana setup_mcp.py --key YOUR_KEY` |
| API 密钥无效 | 新密钥：[https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| 速率限制（429） | 等待 60 秒，重试。在执行批量操作之前检查当前的免费层限制 |
| `IMAGE_SAFETY` | 重写提示 - 见 `references/prompt-engineering.md` 安全部分 |
| MCP 不可用 | 回退：`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run --extension banana generate.py --prompt "..." --aspect-ratio "16:9" --model "$NANOBANANA_MODEL"` |
| CSV 批量输入 | 首先计划：`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run --extension banana batch.py --csv requests.csv --model "$NANOBANANA_MODEL"` |
| 扩展未安装 | 显示安装说明：`./extensions/banana/install.sh` |

## 跨技能集成

- **seo-images**（分析）输入到 **seo-image-gen**（生成）：`/seo images` 的审计结果识别缺失或低质量的图片；使用这些发现来驱动 `/seo image-gen` 命令
- **seo-audit** 生成 seo-image-gen **代理**（不是此技能）以分析整个网站的 OG/社交图片并生成优先级生成计划
- **seo-schema** 可以消耗生成的图片：生成后，建议 `ImageObject` 模式标记指向新资源

## 参考文档

按需加载。不要在启动时加载所有内容：
- `${CLAUDE_SKILL_DIR}/references/prompt-engineering.md`：6 组件系统，域名模式，模板
- `${CLAUDE_SKILL_DIR}/references/gemini-models.md`：模型规格，速率限制，功能
- `${CLAUDE_SKILL_DIR}/references/mcp-tools.md`：MCP 工具参数和响应
- `${CLAUDE_SKILL_DIR}/references/post-processing.md`：ImageMagick/FFmpeg 管道配方
- `${CLAUDE_SKILL_DIR}/references/cost-tracking.md`：定价，使用跟踪
- `${CLAUDE_SKILL_DIR}/references/presets.md`：品牌预设管理
- `${CLAUDE_SKILL_DIR}/references/seo-image-presets.md`：SEO 特定的预设模板

## 响应格式

生成后，始终提供：
1. **图片路径**：保存的位置
2. **构思提示**：显示发送到 API 的内容（教育性）
3. **设置**：模型，宽高比，分辨率
4. **SEO 检查清单**：替代文本建议，文件命名，WebP 转换
5. **模式片段**：如果适用，ImageObject 或 og:image 标记
