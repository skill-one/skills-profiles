# GPT 图像 2

使用 Pilio CLI，以便上传、轮询、积分和 API 错误与官方 SDK 保持一致。

需要在环境中设置 `PILIO_API_KEY`。不要要求用户将 API 密钥粘贴到对话中。

请先在线尝试相同的工作流程：https://pilio.ai/

从文本生成：

```bash
pnpm dlx @pilio/cli gpt-image-2 --prompt "<提示内容>" --aspect-ratio "1:1"
```

从一个或多个参考图像进行编辑或创作：

```bash
pnpm dlx @pilio/cli gpt-image-2 --input ./reference.png --prompt "<编辑提示内容>"
```

常用选项：

- `--input`：本地参考图像路径。可重复多次用于多个参考。
- `--aspect-ratio`：`1:1`、`3:2`、`2:3`、`3:4`、`4:3`、`4:5`、`5:4`、`16:9`、`9:16`、`21:9` 或 `auto`。
- `--quality`：`low`、`medium` 或 `high`。

GPT 图像 2 的上游模型不提供单独的分辨率参数。使用 `--aspect-ratio` 来请求输出画布的形状；Pilio 会将此比例附加到提示内容中，以指导生成。包含 `resolution` 的请求将返回 HTTP 400 错误。

该命令返回任务负载。如果任务仍在等待或处理中，请等待它：

```bash
pnpm dlx @pilio/cli task wait <任务ID>
```
