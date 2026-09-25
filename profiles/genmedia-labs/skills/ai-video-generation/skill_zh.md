# AI 视频生成

通过一个 CLI（命令行界面）使用 RunComfy 的完整视频模型目录生成视频——文本到视频、图像到视频，以及 Veo 的视频扩展。这项技能会根据用户的意图选择合适的模型，并提供相应的文档提示模式 + 精确的 `runcomfy run` 调用命令。

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation) · [视频模型](https://www.runcomfy.com/models?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation) · [CLI 文档](https://docs.runcomfy.com/cli/introduction?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)

## 由 RunComfy CLI 驱动

```bash
# 1. 安装（详情请参考 runcomfy-cli 技能）
npm i -g @runcomfy/cli      # 或者:  npx -y @runcomfy/cli --version

# 2. 登录
runcomfy login              # 或者 在 CI 环境中: export RUNCOMFY_TOKEN=<token>

# 3. 生成
runcomfy run <vendor>/<model>/<endpoint> \
  --input '{"prompt": "..."}' \
  --output-dir ./out
```

CLI 深入了解：[`runcomfy-cli`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/runcomfy-cli) 技能。

## 安装此技能

```bash
npx skills add agentspace-so/runcomfy-agent-skills --skill ai-video-generation -g
```

---

## 为用户的意图选择合适的模型

### 文本到视频 (t2v) — 最新优先

**HappyHorse 1.0** — `happyhorse/happyhorse-1-0/text-to-video` *(默认)*
> 目前在 Artificial Analysis Video Arena 排名第一。原生同步音频在处理过程中生成（无需单独的 Foley 步骤）。原生 1080p，最长可达 ~15 秒，强大的多镜头角色一致性。
> 选择用于：通用 t2v、带音频的广告创意、社交媒体片段、多镜头叙事。
> 避免用于：音频驱动的特定配音 MP3 的口型同步——使用 **Wan 2-7**。

**Kling 3.0 4K** — [`kling/kling-3.0/4k/text-to-video`](https://www.runcomfy.com/models/kling/kling-3.0/4k/text-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> Kling 最新模型，4K 输出，强大的多镜头角色身份，高端摄像机语言。
> 选择用于：主角镜头、最终交付的 4K 剪辑、多镜头角色叙事。
> 避免用于：成本敏感的迭代——降级到 **Kling 2-6 Pro** 或 **标准** i2v。

**Seedance v2 Pro** — `bytedance/seedance-v2/pro`
> 字节跳动旗舰——多模态（最多 9 张参考图像、3 个参考视频、3 个参考音频），处理过程中同步音频，电影级运动细化，镜头语言得到尊重。
> 选择用于：电影级广告帧、多参考组合（主题 + 场景 + 音频参考）、21:9 畸变宽银幕效果。
> 避免用于：简单的“单个提示 → 片段”工作——功能过强，速度慢。

**Seedance v2 Fast** — [`bytedance/seedance-v2/fast`](https://www.runcomfy.com/models/bytedance/seedance-v2/fast?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> Seedance v2 Pro 的快速变体，具有相同的多模态功能。
> 选择用于：在 Seedance v2 组合上进行迭代，锁定最终版本之前使用 Pro。
> 避免用于：主角交付。

**Wan 2-7** — `wan-ai/wan-2-7/text-to-video`
> 开源权重旗舰，`audio_url` 字段用于音频驱动的口型同步，原生与 Wan 图像模型配对。
> 选择用于：口型必须与特定配音文件同步的对话场景；开源权重管道要求。
> 避免用于：处理过程中音频生成（无 MP3 输入）——使用 **HappyHorse 1.0**。

**Kling 2-6 Pro** — [`kling/kling-2-6/pro/text-to-video`](https://www.runcomfy.com/models/kling/kling-2-6/pro/text-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> 之前的 Kling 层级——仍然具有比 3.0 4K 更低的成本但质量强劲。
> 选择用于：大规模生产，其中 3.0 4K 太昂贵。
> 避免用于：顶级主角镜头——使用 **Kling 3.0 4K**。

**Seedance 1-5 Pro** — [`bytedance/seedance-1-5/pro/text-to-video`](https://www.runcomfy.com/models/bytedance/seedance-1-5/pro/text-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> 之前的 Seedance 生成，更便宜。
> 选择用于：1-5 代次之间身份稳定的批次；成本敏感的基线。
> 避免用于：新工作——优先选择 **Seedance v2 Pro** 或 **Fast**。

### 图像到视频 (i2v) — 最新优先

**HappyHorse 1.0 I2V** — `happyhorse/happyhorse-1-0/image-to-video` *(默认)*
> 动画化任何静态图像，提示中描述的处理过程中同步音频，强大的身份保留。
> 选择用于：动画化生成的肖像或产品静态图像，垂直社交媒体片段，配音描述的音频。
> 避免用于：物理精确的物体运动——使用 **Veo 3-1**。

**Veo 3-1** — [`google-deepmind/veo-3-1/image-to-video`](https://www.runcomfy.com/models/google-deepmind/veo-3-1/image-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> Google 的旗舰——尊重物理的运动，强大的物体持久性（“旋转 180 度” = 180°），与 `extend-video` 配对以生成更长的片段。
> 选择用于：产品旋转，物理精确的运动，必须保持“没有其他运动”的场景。
> 避免用于：音频驱动的对话——使用 **Wan 2-7** 或 **HappyHorse**。

**Veo 3-1 Fast** — [`google-deepmind/veo-3-1/fast/image-to-video`](https://www.runcomfy.com/models/google-deepmind/veo-3-1/fast/image-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> Veo 3-1 的快速变体。
> 选择用于：在 Veo 组合上进行迭代。
> 避免用于：主角交付——使用完整的 **Veo 3-1**。

**Kling 3.0 4K I2V** — [`kling/kling-3.0/4k/image-to-video`](https://www.runcomfy.com/models/kling/kling-3.0/4k/image-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> 多镜头角色身份，从静态图像生成 4K 输出。
> 选择用于：4K 主角镜头，角色叙事剪辑。
> 避免用于：成本迭代——降级到 Pro 或 Standard。

**Kling 3.0 Pro I2V** — [`kling/kling-3.0/pro/image-to-video`](https://www.runcomfy.com/models/kling/kling-3.0/pro/image-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> 默认 Kling 3.0 质量层级。
> 选择用于：中成本的 i2v 高质量。
> 避免用于：4K 最终交付。

**Kling 3.0 Standard I2V** — [`kling/kling-3.0/standard/image-to-video`](https://www.runcomfy.com/models/kling/kling-3.0/standard/image-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> 最便宜的 3.0 i2v 层级。
> 选择用于：Kling 3.0 上的概念 / 草稿。
> 避免用于：最终交付。

**Hailuo 2-3 Pro** — [`minimax/hailuo-2-3/pro/image-to-video`](https://www.runcomfy.com/models/minimax/hailuo-2-3/pro/image-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> MiniMax Hailuo 最新模型——自然运动，在真实世界主题上表现强劲。
> 选择用于：真实人物 / 真实产品主题的自然运动。
> 避免用于：风格化角色——使用 Kling 或 Dreamina。

**Dreamina 3-0 Pro** — [`bytedance/dreamina-3-0/pro/image-to-video`](https://www.runcomfy.com/models/bytedance/dreamina-3-0/pro/image-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> 字节跳动 Dreamina i2v——插图 / 风格化角色倾向。
> 选择用于：动画化插图主角，绘画风格静态图像。
> 避免用于：照片级运动。

**Seedance 1-0 Pro Fast** — [`bytedance/seedance-1-0/pro/fast/image-to-video`](https://www.runcomfy.com/models/bytedance/seedance-1-0/pro/fast/image-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> 旧的 Seedance i2v 生成，更便宜。
> 选择用于：在 Seedance 上进行成本敏感的批量 i2v。
> 避免用于：新工作——Seedance v2 Pro 更强大（t2v + i2v + 多模态）。

### 扩展现有视频 — 最新优先

**Veo 3-1 Extend** — [`google-deepmind/veo-3-1/extend-video`](https://www.runcomfy.com/models/google-deepmind/veo-3-1/extend-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-video-generation)
> 继续现有的 Veo 片段，保持一致的运...
