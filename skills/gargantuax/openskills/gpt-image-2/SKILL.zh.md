---
name: gpt-image-2
description: 全功能 OpenAI 兼容 GPT 图像 2 覆盖范围，包括图像/生成、图像/编辑以及使用 image_generation 工具的响应。当单次图像辅助工具不足以满足需求时使用 - 文本到图像、掩码编辑、多图像批处理、流式传输、部分图像和混合文本+图像响应流程。读取 .env 文件并尊重进程环境变量；可与任何 OpenAI 兼容网关协同工作。
---

# GPT 图像 2

一个单一的 Python 入口点，涵盖所有 GPT 图像 2 路由，并对模型的尺寸、宽高比和功能约束进行严格的预飞行验证。

## 工作流程

1. 打开 `[参考资料/config.md](./references/config.md)` 来选择环境变量和默认值。
2. 打开 `[参考资料/api-surface.md](./references/api-surface.md)` 来在 `generations`、`edits` 和 `responses` 之间进行选择。
3. 除非用户要求不同的 OpenAI 兼容端点，否则优先使用 `OPENAI_BASE_URL=https://api.openai.com/v1`。
4. 使用 `gpt-image-2` 进行 `generations` 和 `edits`；使用 `gpt-5.4` 等文本功能响应模型进行 `responses`。
5. 使用三个子命令之一运行 `scripts/gpt_image.py`。
6. 当负载形状是主要风险时，首先添加 `--dry-run`。
7. 当原始 JSON 正文或 SSE 事件流需要保留以用于调试时，添加 `--save-response <路径>`。

## 命令

通过公共图像 API 进行文本到图像：

```powershell
python .\skills\gpt-image-2\scripts\gpt_image.py generations `
  --prompt "为开发者工具主页设计一张大胆的产品英雄图像" `
  --output .\out\hero.png `
  --size 1536x1024 `
  --quality 高 `
  --format png
```

使用文件名模式的多个图像批量：

```powershell
python .\skills\gpt-image-2\scripts\gpt_image.py generations `
  --prompt "夜晚的戏剧性城市天际线" `
  --output .\out\skyline-{index}.webp `
  --n 3 `
  --format webp `
  --compression 90
```

使用两个输入和蒙版进行图像编辑：

```powershell
python .\skills\gpt-image-2\scripts\gpt_image.py edits `
  --prompt "将两个参考图像融合成一个干净的营销插图" `
  --image .\refs\subject.png `
  --image .\refs\background.png `
  --mask .\refs\mask.png `
  --output .\out\edit-{index}.png `
  --image-field-style brackets `
  --n 2
```

使用流式传输和部分预览的响应 API：

```powershell
python .\skills\gpt-image-2\scripts\gpt_image.py responses `
  --input-text "为 AI 开发者峰会生成海报" `
  --model gpt-5.4 `
  --output .\out\poster-{index}.png `
  --stream `
  --partial-images 2 `
  --save-response .\out\poster-events.json
```

使用本地图像和蒙版的响应 API 编辑：

```powershell
python .\skills\gpt-image-2\scripts\gpt_image.py responses `
  --input-text "将产品照片转换为干净的摄影棚广告" `
  --model gpt-5.4 `
  --input-image .\refs\product.png `
  --mask .\refs\mask.png `
  --output .\out\studio.png `
  --action edit
```

在不发送的情况下检查构建的请求：

```powershell
python .\skills\gpt-image-2\scripts\gpt_image.py generations `
  --prompt "一个极简的封面图像" `
  --output .\out\cover.png `
  --dry-run
```

## 规则

- 使用 `generations` 进行公共文本到图像调用。
- 使用 `edits` 进行多部分图像编辑和蒙版上传。
- 使用 `responses` 进行高级流程：流式传输、混合文本 + 图像输入、`previous_response_id`、`tool_choice`、`action` 和可选的 `tool_model`。
- 环境变量优先于 `.env`；CLI 标志优先于两者。
- 不要打印秘密。
- `--output` 接受单个路径或模式，例如 `image-{index}.png`，用于多图像或流式传输。
- `responses` 使用与图像模型分离的顶层响应模型；默认为 `gpt-5.4`，除非需要其他文本功能模型。
- `Responses` 工具流程中的 `quality` 会被传递，但最终行为仍取决于托管的图像工具。
- 在 OpenAI GPT 图像模型中，省略 `response_format`；图像数据以 base64 格式返回。
- 快速失败于不支持的 `gpt-image-2` 组合：透明背景、无效尺寸、`partial_images` 超出 `0..3` 范围，或在公共图像路由上 `stream=true` 且 `n>1`。

## 资源

- 脚本：[scripts/gpt_image.py](./scripts/gpt_image.py)
- 配置参考：[references/config.md](./references/config.md)
- API 表面参考：[references/api-surface.md](./references/api-surface.md)
