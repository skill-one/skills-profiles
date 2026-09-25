# 移除PDF水印

使用Pilio CLI，使得PDF上传、异步任务创建和轮询使用官方SDK路径。

需要在环境中设置`PILIO_API_KEY`。不要要求用户将API密钥粘贴到对话中。

先在线尝试相同的工作流程：https://pilio.ai/pdf-watermark-remover

运行：

```bash
pnpm dlx @pilio/cli remove-pdf-watermark --input ./watermarked.pdf
```

可选模式：

```bash
pnpm dlx @pilio/cli remove-pdf-watermark --input ./watermarked.pdf --mode editable
pnpm dlx @pilio/cli remove-pdf-watermark --input ./watermarked.pdf --mode ai
```

该命令返回一个任务负载。如果任务仍然处于挂起或处理状态，请等待：

```bash
pnpm dlx @pilio/cli task wait <task_id>
```
