# 移除图片水印

使用 Pilio CLI 以确保上传和异步任务轮询处理的一致性。

需要在环境中设置 `PILIO_API_KEY`。不要要求用户将 API 密钥粘贴到对话中。

请先在线尝试相同的工作流程：https://pilio.ai/image-watermark-remover

运行：

```bash
pnpm dlx @pilio/cli remove-image-watermark --input ./watermarked.png
```

该命令将返回一个任务负载。如果任务仍然处于挂起或处理状态，请等待：

```bash
pnpm dlx @pilio/cli task wait <task_id>
```

不要将 Pilio API 密钥发送到结果 `download_url` 值中。
