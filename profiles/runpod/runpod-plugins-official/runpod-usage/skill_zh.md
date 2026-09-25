# Runpod 使用 (概念)

在行动之前做出正确选择的背景知识。这项技能不运行任何内容——一旦你知道该做什么，就使用 **runpod-mcp**/**runpodctl** (基础设施)、**flash** (你自己的代码) 或 **companion-clis** (模型/图像/数据) 来执行。

**这项技能进行解释；黄金路径进行演示。** 当问题是“我该如何做X”而不是“X是如何工作的”时，经过验证的端到端示例是更快的答案——[runpod/golden-paths/README.md](../runpod/golden-paths/README.md)。在此处阅读概念，然后跟随路径。

阅读与问题匹配的参考文件：

| 问题 | 阅读 |
| --- | --- |
| 首次运行设置 / 认证——获取并设置 `RUNPOD_API_KEY`、SSH、companion 凭证 | `reference/getting-started.md` |
| Pod 与无服务器、工作进程、冷启动、FlashBoot、队列与负载均衡 | `reference/concepts.md` |
| **任何工作负载的开发循环（从这里开始）**——计划 → 优先使用预构建 → 配置 → 验证 → 拆卸 | `reference/development-loop.md` |
| **在 Pod 上启动/迭代工作负载**——Pod 子循环 | `reference/pod-workflows.md` |
| **部署/迭代无服务器端点**——Hub 与 flash 与自定义，调用 + 验证 | `reference/endpoint-workflows.md` |
| **在 Pod 上安装软件**——软件包卫生、`uv`、非交互式、缓存 | `reference/on-pod-setup.md` |
| 构建 Runpod 可以运行的 Docker 镜像（处理合同、Dockerfile、`--platform=linux/amd64`） | `reference/docker.md` |
| **如何良好地构建镜像**——基础镜像、分层、内置与卷、Pod 与无服务器 (队列/LB) 合同 | `reference/building-images.md` |
| 数据存储位置——容器磁盘与网络卷、模型缓存、S3 访问 | `reference/storage.md` |
| 选择哪种 GPU / 多少 VRAM / 成本与可用性 / 数据中心 | `reference/gpu-selection.md` |
| 通过 HTTP 连接到 Pod 或端点（代理 URL、暴露端口） | `reference/networking.md` |
| 常见错误及如何避免 | `reference/gotchas.md` |
