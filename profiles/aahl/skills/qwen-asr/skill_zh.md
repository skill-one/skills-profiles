# Qwen ASR
使用 Qwen ASR 将音频文件（wav/mp3/ogg...）转录为文本。无需配置或 API 密钥。

## 使用方法
```shell
uv run scripts/main.py -f audio.wav

cat audio.mp3 | uv run scripts/main.py > transcript.txt

curl https://example.com/audio.ogg | uv run scripts/main.py
```
