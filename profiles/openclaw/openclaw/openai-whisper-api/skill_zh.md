# OpenAI 转录 API

通过 `/v1/audio/transcriptions` 进行音频转录。设置 `OPENAI_BASE_URL` 以使用 OpenAI 兼容的代理或本地网关。

## 快速入门

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a
```

默认设置：

- 模型：`gpt-4o-transcribe`
- 输出：`<input>.txt`

## 有用的标志

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model gpt-4o-transcribe --out /tmp/transcript.txt
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model gpt-4o-mini-transcribe
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model gpt-4o-transcribe-diarize --json
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model whisper-1
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --language en
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --prompt "说话者姓名：Peter, Daniel"
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --json --out /tmp/transcript.json
```

注意：

- 支持的上传格式包括 `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, `webm`。
- 主机 API 的上传限制为 25 MB。
- 使用 diarize 进行说话者标签；脚本发送 `chunking_strategy=auto` 并拒绝 `--prompt`。

## API 密钥

设置 `OPENAI_API_KEY`，或在活动的 OpenClaw 配置文件（`$OPENCLAW_CONFIG_PATH`，默认 `~/.openclaw/openclaw.json`）中配置它。可选地设置 `OPENAI_BASE_URL`：

```json5
{
  skills: {
    "openai-whisper-api": {
      apiKey: "OPENAI_KEY_HERE",
    },
  },
}
```
