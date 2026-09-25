# Three.js 音频生成器

为 Three.js 项目提供游戏级音频：生成、语音工作、清理和运行时集成。提供方：ElevenLabs。

从实际加载的技能文件中解析 `<this-skill-dir>`。首先解析其相邻的兄弟技能，然后使用运行器发现的路径。不要混用已安装的版本或假设特定的家目录。

## 参考

`references/audio-workflows.md` — 音频矩阵、提示模式、生成和语音策略、Web Audio 管理器形状以及运行时失败模式。在规划游戏的音频、生成批量、连接运行时播放或转换语音之前，请阅读它。

## 何时使用

SFX（跳跃、撞击、武器、爆炸、拾取、碰撞、UI 点击） · 环境音（风、雨、城市背景、引擎嗡嗡声、房间音调、竞技场背景） · 语音（播音员吆喝、Boss 台词、教程提示、菜单旁白） · 从草稿表演进行语音转换，当时机和表演很重要时 · 在转换或最终使用前进行清理和隔离 · Web Audio 集成，包括加载、循环、清单、音量组、暂停/恢复和手势解锁。

对于高端游戏来说，音频不是装饰性的。根据游戏实际拥有的事件构建音频矩阵；不要只是为了填充类别而添加对话、武器或环境音层。尊重明确的静音、程序化音频、无障碍和外部服务限制。狭隘的音效修复不需要新的配乐。

## API 密钥

脚本读取 `--api-key` 或 `ELEVENLABS_API_KEY`。密钥永远不会放在技能文件、游戏代码或报告中。

```bash
python3 <this-skill-dir>/scripts/threejs_audio_asset.py probe   # ELEVENLABS_API_KEY=SET|MISSING
```

仅在 shell 配置文件中定义的密钥可能不在进程环境中；`threejs-game-director/scripts/probe_asset_credentials.sh` 会源取配置文件并探测所有三个提供方。

在存在密钥但生成失败时，添加 `--validate` 以调用 `GET /user` 并确认密钥确实有效（打印 `VALID_USER=...`）。有效的密钥仍可能因信用额度或计划限制而被阻止，这会从真实的生成尝试中表现为 `HTTP 4xx` — 将其报告为计划阻止而不是缺失的密钥。

## 命令

从游戏项目目录运行：

```bash
python3 <this-skill-dir>/scripts/threejs_audio_asset.py sfx \
  --prompt "紧凑的未来派加速拾取，明亮的瞬态，短促的闪烁尾迹，街机赛车游戏" \
  --duration 1.2 --prompt-influence 0.65 --out assets/audio/sfx/boost-pickup.mp3

python3 <this-skill-dir>/scripts/threejs_audio_asset.py sfx \
  --prompt "无缝的赛博度假村环境音，遥远的海浪声，柔和的霓虹转换器嗡嗡声，轻柔的人群背景" \
  --duration 12 --loop --prompt-influence 0.45 --out assets/audio/ambience/cyber-resort-loop.mp3

python3 <this-skill-dir>/scripts/threejs_audio_asset.py tts \
  --text "完美的射击。" --voice-id JBFqnCBsd6RMkjVDRZzb --out assets/audio/voice/perfect-shot.mp3

python3 <this-skill-dir>/scripts/threejs_audio_asset.py isolate \
  --input assets/audio/source/noisy-boss-line.wav --out assets/audio/voice/boss-line-clean.mp3

python3 <this-skill-dir>/scripts/threejs_audio_asset.py voice-change \
  --input assets/audio/source/scratch-boss-line.wav --voice-id JBFqnCBsd6RMkjVDRZzb \
  --remove-background-noise --out assets/audio/voice/boss-line-final.mp3
```

## 默认值

- SFX: `mp3_44100_128`, 0.5–2.5s, 提示影响 0.55–0.8。
- UI: 0.15–0.8s, 高提示影响，瞬态保持清晰。
- 环境音: 8–30s 并带 `--loop`, 提示影响 0.3–0.55。
- 语音: TTS 用于干净的生成台词；当从草稿表演中需要时机和表演时使用 `voice-change`。先隔离嘈杂的语音。
- 运行时: 生成到游戏项目并通过 Web Audio 加载。遵循项目的资产/版本控制策略；未经要求不要提交或发布。浏览器代码中不要包含 API 密钥。

## 恢复和协调

对于协调游戏，请使用导演的 `references/asset-recovery.md`。在重试工作之前保留输出和音频触发映射。区分缺失的凭证、权限、用尽的信用额度、无效输入和瞬时的服务故障。在重新提交不确定的付费请求之前进行协调；这些一次性命令不实现 Tripo 任务恢复。保持独立游戏工作进展，并在确实受阻时提供本地/合成的备用方案，并诚实地说明限制。

在批量生成之前，先听一个代表性的效果或台词。通过真实的游戏事件测试它，然后为一次集中的 QA 过程提供主要路径和本地播放发现。

## 报告

生成的和处理过的文件路径、提示、文本、源文件、语音 ID、持续时间、循环标志和格式、运行时触发映射和音频组，以及任何剩余的缺口或计划限制。
