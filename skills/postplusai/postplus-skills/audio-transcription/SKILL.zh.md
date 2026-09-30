---
name: audio-transcription
description: 将本地或远程音频转录为文本和时间戳。无需另一次转录工作，即可将现有的带时间戳的转录本本地转换为SRT或ASS格式。
---

# 音频转写

## 适用场景
- 输入为音频，主要工作为语音转文字、字幕时间戳、粗略语音搜索、多语言转写或持久化转写结果。
- 使用 `video-transcription` 处理视频输入，使用 `media-analysis` 进行语义视频理解。

如果已存在时间戳转写结果且仅请求字幕输出，则跳过转写并读取本地字幕转换参考。

## 不适用场景
- 任务需要新的创意生成或视觉分析，而非语音或字幕。
- 所需输入缺失，猜测会改变结果。

## 执行边界
- 主机转写通过公共 `postplus media transcribe` 动词执行，为异步操作。提交记录运行句柄、当前状态和完成后的结果。
- 将本地路径、HTTPS URL、现有 PostPlus 媒体引用或数据 URI 直接传递给 `--audio`。CLI 在单次主机提交前验证并准备本地媒体。
- 提供更高质量的默认模型和更快、更便宜的变体；当字幕质量重要时优先使用默认模型，使用更便宜的变体进行显式粗略转写。下方生成的示例显示了默认端点密钥。

## 源与路径
- 提供媒体时长，以便 PostPlus 在运行前验证请求；缺失时长会导致提交前失败。
- 请求输出字幕或编辑决策的时间戳。
- 从单个源文件或音频 URL 开始，再处理大批量文件。
- 将内部请求、响应、清单、标准化转写结果和下载结果保存在 `.postplus/audio-transcription` 下；将最终用户面转写导出保存在 `.postplus` 外部。

## 交接
- 如果状态为待处理，保留结果路径并遵循 CLI 返回的操作或恢复命令执行相同操作。不要提交另一个任务。当 CLI 等待/恢复边界达到时停止并报告。
- 当请求 SRT/ASS 时，使用实际时间戳转写结果并读取 [本地字幕转换](references/subtitles.md)。本地转换，不要进行另一个主机请求；不要编造 CLI 导出命令。

## 停止条件
- 当所需用户意图、源证据或拥有输入结果缺失且猜测会改变结果时停止。

## 公共命令边界

- 从用户输入中选择最小匹配命令或工作流并直接运行。
- 准备状态诊断：`postplus doctor --skill audio-transcription`。

- 仅在需要完整端点、标志和枚举契约或修复未知请求形状时使用 `postplus media schema --json`。
- 使用下方生成的命令运行主机转写任务；不要使用其他执行界面。
- 直接通过 `--audio` 传递源；不要预先上传或构建手动请求对象。

<!-- BEGIN GENERATED EXECUTION EXAMPLE -->
```bash
postplus media transcribe transcription \
  --audio ./reference.wav \
  --duration-seconds 1 \
  --wait \
  --output ./result.json
```

遵循 CLI 的结构化结果和报告的下一步操作；不要从自由文本消息中推断恢复。
当请求时等待明确用户批准；操作不会授权支出、发布或覆盖。
通过返回的检查点或操作恢复相同操作；永远不要重新提交不确定的工作，重复耗尽的恢复，或切换供应商以绕过失败。
<!-- END GENERATED EXECUTION EXAMPLE -->

- 如果 CLI 返回引用确认挑战，在运行 `postplus quote confirm --json --challenge-file <challenge.json>` 并使用返回的令牌重试前，获取用户对其范围和成本的批准。
