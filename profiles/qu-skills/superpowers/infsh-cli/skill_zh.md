> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# [inference.sh](https://inference.sh)

使用简单的 CLI 在云端运行 AI 应用。无需 GPU。

![[inference.sh](https://inference.sh)](https://cloud.inference.sh/app/files/u/4mg21r6ta37mpaz6ktzwtt8krr/01kgjw8atdxgkrsr8a2t5peq7b.jpeg)

## 安装 CLI

```bash
curl -fsSL https://cli.inference.sh | sh
belt login
```

> **安装程序的作用是什么？** [安装脚本](https://cli.inference.sh) 会检测您的操作系统和架构，从 `dist.inference.sh` 下载正确的二进制文件，验证其 SHA-256 校验和，并将其放置在您的 PATH 中。就是这样——无需提升权限、无需后台进程、无需遥测数据。如果您安装了 [cosign](https://docs.sigstore.dev/cosign/system_config/installation/)，安装程序会自动验证 Sigstore 签名。
>
> **手动安装**（如果您不想将内容管道到 sh）：
> ```bash
> # 下载二进制文件和校验和
> curl -LO https://dist.inference.sh/cli/checksums.txt
> curl -LO $(curl -fsSL https://dist.inference.sh/cli/manifest.json | grep -o '"url":"[^"]*"' | grep $(uname -s | tr A-Z a-z)-$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/') | head -1 | cut -d'"' -f4)
> # 验证校验和
> sha256sum -c checksums.txt --ignore-missing
> # 解压并安装
> tar -xzf inferencesh-cli-*.tar.gz
> mv inferencesh-cli-* ~/.local/bin/inferencesh
> ```

## 快速示例

```bash
# 生成图像
belt app run falai/flux-dev-lora --input '{"prompt": "一只宇航员猫"}'

# 生成视频
belt app run google/veo-3-1-fast --input '{"prompt": "无人机飞过山脉"}'

# 调用 Claude
belt app run openrouter/claude-sonnet-45 --input '{"prompt": "解释量子计算"}'

# 网络搜索
belt app run tavily/search-assistant --input '{"query": "最新的 AI 新闻"}'

# 发布到 Twitter
belt app run x/post-tweet --input '{"text": "来自 AI 的问候！"}'

# 生成 3D 模型
belt app run infsh/rodin-3d-generator --input '{"prompt": "一把木制椅子"}'
```

## 本地文件上传

当您提供路径而不是 URL 时，CLI 会自动上传本地文件：

```bash
# 放大本地图像
belt app run falai/topaz-image-upscaler --input '{"image": "/path/to/photo.jpg", "upscale_factor": 2}'

# 从本地文件生成图像到视频
belt app run falai/wan-2-5-i2v --input '{"image": "./my-image.png", "prompt": "让它动起来"}'

# 使用本地音频和图像生成头像
belt app run bytedance/omnihuman-1-5 --input '{"audio": "/path/to/speech.mp3", "image": "/path/to/face.jpg"}'

# 使用本地媒体发布推文
belt app run x/post-create --input '{"text": "看看这个！", "media": "./screenshot.png"}'
```

## 命令

| 任务 | 命令 |
|------|---------|
| 浏览应用商店 | `belt app list` |
| 搜索商店 | `belt app search "flux"` |
| 按类别筛选 | `belt app list --category image` |
| 列出您的应用 | `belt app list` |
| 获取应用详情 | `belt app get google/veo-3-1-fast` |
| 生成示例输入 | `belt app sample google/veo-3-1-fast --save input.json` |
| 运行应用 | `belt app run google/veo-3-1-fast --input input.json` |
| 不等待直接运行 | `belt app run <app> --input input.json --no-wait` |
| 检查任务状态 | `belt task get <task-id>` |

## 可用资源

| 类别 | 示例 |
|----------|----------|
| **图像** | FLUX, Gemini 3 Pro, Grok Imagine, Seedream 4.5, Reve, Topaz Upscaler |
| **视频** | Veo 3.1, Seedance 2.0, Wan 2.5, OmniHuman, Fabric, HunyuanVideo Foley |
| **LLMs** | Claude Opus/Sonnet/Haiku, Gemini 3 Pro, Kimi K2, GLM-4, 任何 OpenRouter 模型 |
| **搜索** | Tavily Search, Tavily Extract, Exa Search, Exa Answer, Exa Extract |
| **3D** | Rodin 3D Generator |
| **Twitter/X** | post-tweet, post-create, dm-send, user-follow, post-like, post-retweet |
| **工具** | 媒体合并, 视频字幕, 图像拼接, 音频提取 |

## 相关技能

```bash
# 图像生成 (FLUX, Gemini, Grok, Seedream)
npx skills add inference-sh/skills@ai-image-generation

# 视频生成 (Veo, Seedance, Wan, OmniHuman)
npx skills add inference-sh/skills@ai-video-generation

# LLMs (Claude, Gemini, Kimi, GLM via OpenRouter)
npx skills add inference-sh/skills@llm-models

# 网络搜索 (Tavily, Exa)
npx skills add inference-sh/skills@web-search

# AI 头像 & 唇形同步 (OmniHuman, Fabric, PixVerse)
npx skills add inference-sh/skills@ai-avatar-video

# Twitter/X 自动化
npx skills add inference-sh/skills@twitter-automation

# 模型特定
npx skills add inference-sh/skills@flux-image
npx skills add inference-sh/skills@google-veo

# 工具
npx skills add inference-sh/skills@image-upscaling
npx skills add inference-sh/skills@background-removal
```

## 参考文件

- [认证 & 设置](references/authentication.md)
- [发现应用](references/app-discovery.md)
- [运行应用](references/running-apps.md)
- [CLI 参考](references/cli-reference.md)

## 文档

- [Agent 技能概述](https://inference.sh/blog/skills/skills-overview) - AI 能力的开放标准
- [入门指南](https://inference.sh/docs/getting-started/introduction) - inference.sh 简介
- [什么是 inference.sh？](https://inference.sh/docs/getting-started/what-is-inference) - 平台概述
- [应用概述](https://inference.sh/docs/apps/overview) - 理解应用生态系统
- [CLI 设置](https://inference.sh/docs/extend/cli-setup) - 安装 CLI
- [工作流 vs Agent](https://inference.sh/blog/concepts/workflows-vs-agents) - 何时使用每个
- [为什么 Agent 运行时很重要](https://inference.sh/blog/agent-runtime/why-runtimes-matter) - 运行时优势
