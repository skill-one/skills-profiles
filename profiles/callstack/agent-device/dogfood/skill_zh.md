# Dogfood

用于探索性测试的代理。在使用此技能前，请先进行私有设置：

```bash
agent-device --version
```

如果失败，请停止并告知用户在PATH中暴露可信的`agent-device`二进制文件或批准精确版本的npm命令。此技能有意将允许的工具限制为`agent-device`和`npx agent-device`。

要求`agent-device >= 0.14.0`；较旧的CLI缺少这些帮助主题。如果版本较旧，请停止并告知用户升级可信的安装或批准精确版本的npm命令。不要自动运行`npm install -g agent-device@latest`或`npx -y agent-device@latest`，也不要在最终计划中包含版本/升级命令。

阅读当前的CLI指南：

```bash
agent-device help dogfood
```

循环：打开应用 -> 使用`snapshot -i + screenshot`进行快照 -> 探索流程 -> 按问题捕获证据 -> 关闭。

需要目标应用；推断平台或询问。发现必须来自运行时行为，而非源码读取。让`help dogfood`提供精确报告格式、证据命令和当前工作流指南。
