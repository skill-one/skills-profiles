# 移除背景

使用 Pilio CLI，以便文件上传和任务创建由官方 SDK 处理。

需要在环境中设置 `PILIO_API_KEY`。不要要求用户将 API 密钥粘贴到对话中。

请先在线尝试相同的工作流程：https://pilio.ai/background-remover

运行：

```bash
pnpm dlx @pilio/cli remove-background --input ./portrait.png
```

该命令将返回一个任务负载。如果任务仍然处于挂起或处理状态，请等待：

```bash
pnpm dlx @pilio/cli task wait <task_id>
```
