# 音频转写

使用 OpenAI 进行音频转写，根据需求可选择性启用说话人分割功能。推荐使用捆绑的 CLI 工具以获得确定性和可重复的运行结果。

## 工作流程
1. 收集输入：音频文件路径、期望的响应格式（text/json/diarized_json）、可选的语言提示以及任何已知的说话人参考信息。
2. 验证 `OPENAI_API_KEY` 是否已设置。如果缺失，提示用户在本地设置（不要要求用户粘贴密钥）。
3. 使用合理的默认值（快速文本转写）运行捆绑的 `transcribe_diarize.py` CLI。
4. 验证输出：转写质量、说话人标签和片段边界；如有需要，针对单个更改进行迭代。
5. 在此代码库中工作时，将输出保存到 `output/transcribe/` 下。

## 决策规则
- 默认使用 `gpt-4o-mini-transcribe` 并配合 `--response-format text` 进行快速转写。
- 如果用户需要说话人标签或分割，使用 `--model gpt-4o-transcribe-diarize --response-format diarized_json`。
- 如果音频超过 ~30 秒，保持 `--chunking-strategy auto`。
- `gpt-4o-transcribe-diarize` 不支持提示语。

## 输出规范
- 使用 `output/transcribe/<job-id>/` 进行评估运行。
- 使用 `--out-dir` 处理多个文件以避免覆盖。

## 依赖项（缺失时安装）
优先使用 `uv` 进行依赖管理。

```
uv pip install openai
```
如果 `uv` 不可用：
```
python3 -m pip install openai
```

## 环境
- `OPENAI_API_KEY` 必须设置以进行实时 API 调用。
- 如果密钥缺失，提示用户在 OpenAI 平台 UI 中创建并导出到其 shell 中。
- 不要要求用户在聊天中粘贴完整密钥。

## 技能路径（一次性设置）

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export TRANSCRIBE_CLI="$CODEX_HOME/skills/transcribe/scripts/transcribe_diarize.py"
```

用户范围的技能安装在 `$CODEX_HOME/skills` 下（默认：`~/.codex/skills`）。

## CLI 快速入门
单个文件（默认快速文本）：
```
python3 "$TRANSCRIBE_CLI" \
  path/to/audio.wav \
  --out transcript.txt
```

已知说话人的分割（最多 4 人）：
```
python3 "$TRANSCRIBE_CLI" \
  meeting.m4a \
  --model gpt-4o-transcribe-diarize \
  --known-speaker "Alice=refs/alice.wav" \
  --known-speaker "Bob=refs/bob.wav" \
  --response-format diarized_json \
  --out-dir output/transcribe/meeting
```

纯文本输出（显式）：
```
python3 "$TRANSCRIBE_CLI" \
  interview.mp3 \
  --response-format text \
  --out interview.txt
```

## 参考映射
- `references/api.md`：支持的格式、限制、响应格式和已知说话人说明。
