此技能的指南随 Diffusion Studio 应用程序一同提供，因此它始终与安装版本保持一致。从应用程序中阅读它并信任它胜过依赖记忆；它属于应用程序，因此切勿编辑它。

文档位于应用程序包内的 `Diffusion Studio.app/Contents/Resources/docs`（通常位于 `/Applications` 下）。从 `skills/watch.md` 开始，并按照它来继续本次会话。它将链接到同一文件夹中的媒体工具参考和提示指南。

应用程序通过 MCP 服务器 (`media_probe`, `media_transcribe`, …) 暴露其工具。`dapi` 命令行工具从 shell 中提供相同的工具：`dapi media grab` 对应于 `media_grab`。

如果 Diffusion Studio 工具和 `dapi` 都不可用，或者应用程序未安装，请阅读 [installation.md](references/installation.md)。
