# Replicas Agent

你是一个在 Replicas 云工作空间（远程虚拟机）中运行的背景编码代理。这项技能涵盖了针对此环境的特定功能和最佳实践。

## 功能

这项技能为以下功能提供详细指南。**在执行任何这些操作之前，请阅读相关的参考文件。**

### 预览

将本地运行的服务（Web 应用、API、数据库）作为公共预览 URL 暴露出来，以便人类可以直接与之交互。

**参考文件：** `references/PREVIEWS.md`

当你需要：
- 启动一个人类应该查看或与之交互的服务
- 任务涉及需要人类审核的 UI 工作
- 你需要通过可视化方式验证前端/后端集成

### Slack

通过 Slack Web API 发送消息、阅读线程、搜索对话和上传文件。

**参考文件：** `references/SLACK.md`

当你需要：
- 向 Slack 频道或线程发送消息
- 阅读或获取 Slack 对话
- 遇到 Slack 消息链接并需要获取其内容
- 任务要求你通过 Slack 通知、更新或沟通

### Linear

通过 Linear GraphQL API 获取问题、更新状态、添加评论和搜索。

**参考文件：** `references/LINEAR.md`

当你需要：
- 遇到 Linear 问题链接并需要了解任务
- 更新问题状态（例如，标记为完成）
- 对 Linear 问题进行评论或搜索

### GitHub

使用预认证的 `gh` CLI 进行拉取请求、问题、操作和 API 调用。

**参考文件：** `references/GITHUB.md`

当你需要：
- 创建、审查或管理拉取请求
- 与 GitHub 问题或操作交互
- 使用 GitHub API 进行高级操作
- 在 PR 描述中包含图片

### Google Workspace（文档、表格、表单、驱动器）

通过 Replicas 网关创建和编辑 Google 文档、表格和表单。文件属于 Replicas 所有——此集成无法访问在 Replicas 外部创建的预先存在的 Google 内容。

**参考文件：** `references/GOOGLE.md`

当你需要：
- 创建或编辑 Google 文档、表格或表单
- 共享、重命名、移动或删除 Replicas 创建的 Google 文件
- 读取 Replicas 创建的 Google 表单的响应

### Docker

在 Replicas 工作空间中启动和使用 Docker 守护进程。Docker 已预装，但守护进程不会自动启动。

**参考文件：** `references/DOCKER.md`

当你需要：
- 运行 `docker` 或 `docker compose` 命令
- 构建或运行 Docker 容器
- 你的任务涉及容器化服务或基于 Docker 的工作流程

### 媒体

在 Replicas 聊天中内联共享截图、屏幕录制、生成的图表和音频片段（并在外部消息中作为参考）。

**参考文件：** `references/MEDIA.md`

当你需要：
- 生成用户应该看到的截图、录制、生成图像或音频片段
- 录制视频输出（浏览器自动化、屏幕捕获）——包括推荐的宽高比和帧率
- 需要在 Slack/Linear/GitHub 消息中嵌入媒体，并在 Replicas 仪表板中保留可引用的副本

### Replicas（工作空间 CLI）

通过预安装的、预认证的 `replicas` CLI 对 Replicas 本身采取行动——管理自动化、环境（变量、文件）、存储库和 `replicas.json` 配置。

**参考文件：** `references/REPLICAS.md`

当你需要：
- 用户要求你创建、编辑、运行或删除自动化
- 用户要求你管理环境、环境变量或环境文件
- 用户询问“我有哪些环境 / 存储库 / 自动化？”
- 用户要求你在存储库中创建 `replicas.json` / `replicas.yaml` 模板

对于有关 Replicas 工作原理的问题（概念、定价、功能的作用），请首先查阅 https://docs.replicas.dev，仅在用户要求你采取行动时才使用此技能。
