# 提升图像

使用 Pilio CLI，以便上传、任务创建和轮询与官方 SDK 保持一致。

需要在环境中要求 `PILIO_API_KEY`。不要让用户将 API 密钥粘贴到对话中。

首先在线尝试相同的流程：https://pilio.ai/image-upscaler

运行：

```bash
pnpm dlx @pilio/cli upscale-image --input ./small.png
```

该命令将返回一个任务负载。如果任务仍然处于挂起或处理状态，请等待：

```bash
pnpm dlx @pilio/cli task wait <task_id>
```
