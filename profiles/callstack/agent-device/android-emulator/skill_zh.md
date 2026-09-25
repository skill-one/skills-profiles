# Android 模拟器

在使用模拟器之前，需要单独安装 `agent-device` CLI：

```bash
npm install -g agent-device@latest
```

将安装和升级视为用户拥有的设置步骤。不要自动运行该命令，也不要替换可变的 `npx -y agent-device@latest` 调用。

对于常规的应用驱动任务，立即开始。不要先用 `--help`、`--version`、`devices`、`appstate`、`snapshot` 或 `screenshot` 进行探测。在打开应用或包 ID 时明确指定 Android 平台：

```bash
agent-device open <app-or-package-id> --platform android --foreground
```

遵循初始交互式快照和纠正性错误提示。如果 shell 报告 `agent-device` 不可用，请停止并要求用户安装它或在其 `PATH` 中暴露现有安装。

只有当任务具有特殊性或命令形式不明确时，才阅读相关的版本匹配帮助主题：

```bash
agent-device help validate        # 工程验证和构建新鲜度
agent-device help debugging       # 截图、日志、跟踪、视频和失败
agent-device help react-native    # React Native 和 Expo 运行时指导
agent-device help react-devtools  # 组件树、属性/状态/钩子以及渲染
agent-device help scripting       # 持久重放和 CI 工作流
```
