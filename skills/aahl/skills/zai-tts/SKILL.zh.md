---
name: zai-tts
description: 使用 `uvx zai-tts` 命令通过 GLM-TTS 服务将文本转换为语音，用于从文本生成音频。在以下情况使用：(1) 用户使用 "tts" 触发器或关键词请求音频/语音输出。(2) 内容需要被朗读而不是阅读（多任务处理、无障碍访问、播客、驾驶、烹饪等）。(3) 使用预先克隆的语音进行语音合成。
---

# Zai-TTS

使用 `uvx zai-tts` 命令通过 GLM-TTS 服务生成高质量的语音合成音频。
在使用此功能前，您需要配置环境变量 `ZAI_AUDIO_USERID` 和 `ZAI_AUDIO_TOKEN`，这些可以通过登录 `audio.z.ai` 并在 F12 开发者工具的浏览器控制台中执行 `localStorage['auth-storage']` 获取。

## 使用方法
```shell
uvx zai-tts -t "{msg}" -o {tempdir}/{filename}.wav
uvx zai-tts -f path/to/file.txt -o {tempdir}/{filename}.wav
```

## 调整语速、音量
```shell
uvx zai-tts -t "{msg}" -o {tempdir}/{filename}.wav --speed 1.5
uvx zai-tts -t "{msg}" -o {tempdir}/{filename}.wav --speed 1.5 --volume 2
```

## 更换声音
```shell
uvx zai-tts -t "{msg}" -o {tempdir}/{filename}.wav --voice system_002
```

## 可用声音
`system_001`：莉拉。一个愉快、标准发音的女性声音
`system_002`：克洛伊。一个温柔、优雅、聪明的女性声音
`system_003`：伊森。一个阳光、标准发音的男性声音

使用 Shell 命令获取所有可用声音：
```shell
uvx zai-tts -l
```
如果您想使用自定义声音，请先在网站 `audio.z.ai` 上完成声音克隆。
