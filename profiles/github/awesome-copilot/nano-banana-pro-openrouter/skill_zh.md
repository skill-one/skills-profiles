# Nano Banana Pro OpenRouter

## 概述

使用 `google/gemini-3-pro-image-preview` 模型通过 OpenRouter 生成或编辑图像。支持仅提示词生成、单图编辑和多图合成。

### 仅提示词生成

```
uv run {baseDir}/scripts/generate_image.py \
  --prompt "雪山顶上的电影感日落" \
  --filename sunset.png
```

### 编辑单图

```
uv run {baseDir}/scripts/generate_image.py \
  --prompt "将天空替换为戏剧性的极光" \
  --input-image input.jpg \
  --filename aurora.png
```

### 合成多图

```
uv run {baseDir}/scripts/generate_image.py \
  --prompt "将主体合成单张工作室肖像" \
  --input-image face1.jpg \
  --input-image face2.jpg \
  --filename composite.png
```

## 分辨率

- 使用 `--resolution` 配合 `1K`、`2K` 或 `4K`。
- 未指定时默认为 `1K`。

## 系统提示词自定义

该技能会从 `assets/SYSTEM_TEMPLATE` 读取可选的系统提示词。这允许您在不修改代码的情况下自定义图像生成行为。

## 行为与限制

- 通过重复 `--input-image` 接受最多 3 张输入图像。
- `--filename` 接受相对路径（保存到当前目录）或绝对路径。
- 如果返回多张图像，则文件名追加 `-1`、`-2` 等。
- 为每张保存的图像打印 `MEDIA: <路径>`。不要将图像读回响应中。

## 故障排除

如果脚本以非零状态退出，请对照以下常见问题检查 stderr：

| 症状 | 解决方案 |
|------|----------|
| `OPENROUTER_API_KEY is not set` | 提示用户设置它。PowerShell: `$env:OPENROUTER_API_KEY = "sk-or-..."` / bash: `export OPENROUTER_API_KEY="sk-or-..."` |
| `uv: command not found` 或未识别 | macOS/Linux: <code>curl -LsSf https://astral.sh/uv/install.sh &#124; sh</code>。Windows: <code>powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 &#124; iex"</code>。然后重启终端。 |
| `AuthenticationError` / HTTP 401 | 密钥无效或没有积分。在 <https://openrouter.ai/settings/keys> 中验证。 |

对于临时错误（HTTP 429、网络超时），30 秒后重试一次。不要重复尝试超过两次——直接向用户展示问题。
