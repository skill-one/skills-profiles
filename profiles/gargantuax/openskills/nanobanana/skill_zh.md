# Nano Banana

一个用于 Gemini 兼容的 Nano Banana 图像生成和编辑的 Python 单一入口，支持模型别名、严格选项验证、批量运行和自定义端点支持。

## 工作流程

1. 打开 `[references/config.md](./references/config.md)` 选择环境变量和覆盖顺序。
2. 打开 `[references/models-and-api.md](./references/models-and-api.md)` 选择合适的 Nano Banana 层级并检查模型特定约束。
3. 除非你需要最快的低成本默认选项 (`nanobanana`) 或最高保真推理模型 (`nanobanana-pro`)，否则优先使用 `gemini-3.1-flash-image-preview` (`nanobanana-2`)。
4. 对于单个请求运行 `scripts/nanobanana.py generate`，对于重复变体运行 `scripts/nanobanana.py batch`。
5. 当主要风险是有效载荷形状、端点或模型特定选项支持时，首先添加 `--dry-run`。
6. 当你需要自定义的 Gemini 兼容网关时，传递 `--base-url` 或 `GEMINI_BASE_URL`。
7. 在 `generate` 时添加 `--save-response <路径>` 以获取用于调试的原始 JSON 正文。

## 命令

单个文本到图像请求：

```powershell
python .\skills\nanobanana\scripts\nanobanana.py generate `
  --prompt "为一个开发者工具创作复古未来主义的产品英雄插画" `
  --output .\out\hero.png `
  --model nanobanana-2 `
  --ratio 16:9 `
  --size 2K
```

使用两个本地参考编辑现有图像：

```powershell
python .\skills\nanobanana\scripts\nanobanana.py generate `
  --prompt "将这些参考转换为清晰的发布海报，并包含可读的标题文本" `
  --input-image .\refs\subject.png `
  --input-image .\refs\background.png `
  --output .\out\poster.png `
  --model nanobanana-pro `
  --ratio 4:5 `
  --size 2K
```

使用自定义的 Gemini 兼容网关：

```powershell
python .\skills\nanobanana\scripts\nanobanana.py generate `
  --prompt "一个大胆的吉祥物贴纸包" `
  --output .\out\stickers.png `
  --base-url http://your-gateway.example.com/v1beta `
  --auth-mode bearer
```

批量生成五个变体：

```powershell
python .\skills\nanobanana\scripts\nanobanana.py batch `
  --prompt "PDF 工作流产品的小型应用图标" `
  --count 5 `
  --dir .\out\icons `
  --prefix icon `
  --model nanobanana `
  --ratio 1:1
```

在不发送的情况下检查最终请求：

```powershell
python .\skills\nanobanana\scripts\nanobanana.py generate `
  --prompt "AI 代理工作的编辑插画" `
  --model nanobanana-2 `
  --output .\out\agents.png `
  --dry-run
```

## 规则

- `--model` 接受别名 `nanobanana`、`nanobanana-2` 和 `nanobanana-pro`，或精确的 Gemini 模型 ID。
- `nanobanana` 解析为 `gemini-2.5-flash-image`，`nanobanana-2` 解析为 `gemini-3.1-flash-image-preview`，`nanobanana-pro` 解析为 `gemini-3-pro-image-preview`。
- `image_size` 仅在 Gemini 3 图像模型上有效；`nanobanana` 拒绝 `--size`。
- `512` 分辨率仅适用于 `nanobanana-2`。
- 环境变量覆盖 `.env`；CLI 标志覆盖两者。
- 永不打印密钥。
- `generate` 接受重复的 `--input-image` 路径用于图像编辑或多参考生成。
- `--base-url` 应指向 Gemini API 根目录，例如 `https://generativelanguage.googleapis.com/v1beta`，而不是直接指向 `/models/...`。
- `--auth-mode auto` 对官方 Google 端点使用 `x-goog-api-key`，对自定义端点发送 `Authorization: Bearer` 和 `x-goog-api-key` 以最大化网关兼容性。

## 资源

- 脚本：[scripts/nanobanana.py](./scripts/nanobanana.py)
- 配置参考：[references/config.md](./references/config.md)
- 模型和 API 参考：[references/models-and-api.md](./references/models-and-api.md)
