---
name: remove-pdf-watermark
description: 使用Pilio开发者API从PDF中去除水印。当用户需要PDF水印去除、可编辑PDF清理、AI PDF页面重建或通过Pilio进行自动化的PDF水印处理时使用。
---

# 移除PDF水印

使用Pilio CLI，使得PDF上传、异步任务创建和轮询使用官方SDK路径。

需要在环境中提供`PILIO_API_KEY`。不要要求用户将API密钥粘贴到对话中。

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

该命令将返回一个任务负载。如果任务仍然处于挂起或处理状态，请等待它：

```bash
pnpm dlx @pilio/cli task wait <task_id>
```
