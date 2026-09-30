---
name: openai-whisper
description: 使用 Whisper 命令行工具实现本地语音转文字（无需 API 密钥）。
---

# Whisper (命令行界面)

使用 `whisper` 命令在本地转录音频。

快速入门

- `whisper /path/audio.mp3 --model medium --output_format txt --output_dir .`
- `whisper /path/audio.m4a --task translate --output_format srt`

注意事项

- 首次运行时，模型将下载到 `~/.cache/whisper`。
- 在此安装中，`--model` 默认为 `turbo`。
- 使用较小的模型以提高速度，使用较大的模型以提高准确性。
