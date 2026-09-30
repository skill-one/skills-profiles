---
name: watch
description: 使用Diffusion Studio观看和理解视频片段：回答有关视频或音频文件的问题、进行总结、查找场景和时刻、提取引语，并描述发生了什么以及何时发生的。当用户询问某个片段的内容、需要总结或回顾、想要定位某个时刻（“X发生在哪里”、“找到...的场景”）或需要核实视频或音频文件中的声明时，都可以使用。
---

这个技能的指南随 Diffusion Studio 应用程序一同提供，因此它始终与安装的版本保持一致。从那里阅读它并信任它胜过依赖记忆；它属于应用程序，所以永远不要编辑它。

文档位于应用程序包内的 `Diffusion Studio.app/Contents/Resources/docs`（通常在 `/Applications` 下）。从 `skills/watch.md` 开始，并按照它来了解本次会话的其余部分。它链接到同一文件夹中的媒体工具参考和提示指南。

应用程序通过 MCP 服务器 (`media_probe`, `media_transcribe`, …) 暴露其工具。`diffusion` CLI (`dapi` 也作为别名工作) 从 shell 提供相同的工具：`diffusion media grab` 对应于 `media_grab`。

如果 Diffusion Studio 工具和 `diffusion` 都不可用，或者应用程序未安装，请阅读 [installation.md](references/installation.md)。
