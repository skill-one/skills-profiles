# sherpa-onnx-tts

使用 sherpa-onnx 离线 CLI 进行本地 TTS。

## 安装

1. 下载适用于您操作系统的运行时环境（解压到 `$OPENCLAW_STATE_DIR/tools/sherpa-onnx-tts/runtime`，默认 `~/.openclaw/tools/sherpa-onnx-tts/runtime`）
2. 下载一个语音模型（解压到 `$OPENCLAW_STATE_DIR/tools/sherpa-onnx-tts/models`，默认 `~/.openclaw/tools/sherpa-onnx-tts/models`）

首先确定活动状态目录：

```bash
STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
```

然后将这些解析后的路径写入活动 OpenClaw 配置文件（`$OPENCLAW_CONFIG_PATH`，默认 `~/.openclaw/openclaw.json`）：

```json5
{
  skills: {
    entries: {
      "sherpa-onnx-tts": {
        env: {
          SHERPA_ONNX_RUNTIME_DIR: "/path/to/your/state-dir/tools/sherpa-onnx-tts/runtime",
          SHERPA_ONNX_MODEL_DIR: "/path/to/your/state-dir/tools/sherpa-onnx-tts/models/vits-piper-en_US-lessac-high",
        },
      },
    },
  },
}
```

包装器位于此技能文件夹中。直接运行它，或将其添加到 PATH：

```bash
export PATH="{baseDir}/bin:$PATH"
```

## 使用

```bash
{baseDir}/bin/sherpa-onnx-tts -o ./tts.wav "Hello from local TTS."
```

注意：

- 如果您想使用其他语音，请从 sherpa-onnx `tts-models` 发布中选择不同的模型。
- 如果模型目录中有多个 `.onnx` 文件，请设置 `SHERPA_ONNX_MODEL_FILE` 或传递 `--model-file`。
- 您还可以传递 `--tokens-file` 或 `--data-dir` 来覆盖默认值。
- Windows：运行 `node {baseDir}\\bin\\sherpa-onnx-tts -o tts.wav "Hello from local TTS."`
