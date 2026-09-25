# Nano Banana 2

使用 Pilio CLI，以便上传、轮询、积分和 API 错误与官方 SDK 保持一致。

需要在环境中设置 `PILIO_API_KEY`。不要要求用户将 API 密钥粘贴到对话中。

请先在线尝试相同的工作流程：https://pilio.ai/nano-banana-2

从文本生成：

```bash
pnpm dlx @pilio/cli nano-banana-2 --prompt "<prompt>" --aspect-ratio "1:1" --resolution "1K"
```

从一个或多个参考进行编辑或创作：

```bash
pnpm dlx @pilio/cli nano-banana-2 --input ./reference.png --prompt "<edit prompt>" --resolution "1K"
```

常用选项：

- `--input`：本地参考图像路径。可重复多次用于多个参考。
- `--aspect-ratio`：`1:1`、`2:3`、`3:2`、`3:4`、`4:3`、`4:5`、`5:4`、`9:16`、`16:9`、`21:9`、`1:4`、`4:1`、`1:8` 或 `8:1`。
- `--resolution`：`0.5K`、`1K`、`2K` 或 `4K`。

该命令将返回一个任务负载。如果任务仍然处于挂起或处理状态，请等待它：

```bash
pnpm dlx @pilio/cli task wait <task_id>
```
