---
name: editor
description: 理解、生成和编辑视频片段：使用Diffusion Studio分析视频/音频/图像，利用AI生成它们，并组合视频创作。适用于任何媒体分析、媒体生成或视频编辑任务。
---

此技能的指南随 Diffusion Studio 应用程序一同提供，因此它始终与安装版本保持一致。请从该应用程序中阅读并信任它，而不是依赖记忆；它属于应用程序，因此切勿编辑它。

文档位于应用程序包内的 `Diffusion Studio.app/Contents/Resources/docs`（通常位于 `/Applications` 下）。从 `skills/editor.md` 开始，并在整个会话中遵循它。它链接到同一文件夹中的工具、JSX 参考、指南、可运行示例和品牌工具包。

应用程序通过 MCP 服务器 (`media_probe`, `capture`, `check`, …) 暴露其工具。`diffusion` CLI (`dapi` 也是别名，可用于相同功能) 从 Shell 提供相同工具：`diffusion media grab` 对应于 `media_grab`。

如果 Diffusion Studio 工具和 `diffusion` 都不可用，或者应用程序未安装，请阅读 [installation.md](references/installation.md)。
