此技能的指南随 Diffusion Studio 应用程序一同提供，因此它始终与安装的版本保持一致。从应用程序中阅读它并信任它胜过依赖记忆；它属于应用程序，因此切勿编辑它。

文档位于应用程序包内的 `Diffusion Studio.app/Contents/Resources/docs`（通常位于 `/Applications` 下）。从 `skills/editor.md` 开始，并在整个会话中遵循它。它链接到同一文件夹中的工具和 JSX 参考、指南、可运行示例以及品牌工具包。

应用程序通过 MCP 服务器 (`media_probe`, `capture`, `check`, …) 暴露其工具。`dapi` 命令行工具从 shell 提供相同的功能：`dapi media grab` 对应于 `media_grab`。

如果 Diffusion Studio 工具和 `dapi` 都不可用，或者应用程序未安装，请阅读 [installation.md](references/installation.md)。
