# Limrun iOS 上的 Maestro

在远程 Limrun iOS 模拟器上运行上游 Maestro CLI。
`lim ios maestro` 透明地将 `maestro test` 连接到实例：它在需要时在模拟器上安装并启动 Maestro XCTest 运行器，然后将驱动程序流量路由到它。不需要 Maestro 的分支，不需要本地模拟器，也不需要本地 Xcode。

## 前置条件

- `lim` CLI 0.22.0 或更高版本：`npm install --global lim`。认证是 `lim login` 或 `LIM_API_KEY`（它可能设置在项目外部，所以不要因为它在 `.env` 或 shell 中缺失就询问它）。
- Maestro CLI 在 PATH 上：`curl -fsSL https://get.maestro.mobile.dev | bash`。Maestro 需要 Java 17+ (`java -version` 来检查)。Maestro 2.5.x 和 2.6+ 都可以工作；`lim` 会自动适应已安装的版本。

CLI 是事实来源：如果标志出错或你需要这里没有显示的标志，请检查 `lim ios <子命令> --help` 而不是猜测。

## 验证设置

在触摸用户的应用之前，使用针对内置设置应用的流程来证明整个管道；它不需要应用安装、隧道或构建：

```bash
ID=$(lim ios create --install-asset appstore/maestro-ios-runner-2.5.1.tar.gz \
  --no-open --quiet --json | jq -r .metadata.id)

cat > hello-flow.yaml <<'EOF'
appId: com.apple.Preferences
---
- launchApp
- assertVisible: General
- takeScreenshot: settings-check
EOF

lim ios maestro --id "$ID" test hello-flow.yaml
```

所有三个步骤报告 `COMPLETED` 表示 Maestro、运行器和远程连接都正常工作；在此之后失败的任何内容都是关于应用或流程，而不是设置。

## 运行流程

```bash
lim ios maestro test flow.yaml
lim ios maestro test flows/
lim ios maestro --id <ios-id> test flow.yaml
```

没有 `--id` 时，它会针对当前工作区中最最近创建的 iOS 实例（工作区遵循你从中运行的 git 仓库或 worktree）；在脚本、代理或从不同目录运行时，传递 `--id <ios-id>`（在 `test` 之前）。在实例上的第一次运行需要额外几秒钟来启动运行器（如果它没有被预安装，还需要安装）；后续运行会跳过这一步。额外的 Maestro 标志在 `--` 之后：

```bash
lim ios maestro -- test flow.yaml --include-tags smoke --test-output-dir artifacts
```

不要传递 `--platform`、`--device`、`--udid`、`--no-reinstall-driver` 或 `--driver-host-port`；`lim` 会自己设置这些并拒绝重复项。
真实的 Maestro 退出代码和报告被保留，所以 CI 连接工作与本地 Maestro 一样。

## 实例设置

任何正在运行的 iOS 实例都可以使用；运行器在第一次使用时安装。使用运行器预安装创建实例会跳过这一步：

```bash
lim ios create --install-asset appstore/maestro-ios-runner-2.5.1.tar.gz --no-open
```

`--no-open` 跳过在浏览器中打开流 URL（在无头和 CI 机器上很重要）。上面的运行器资产名称是唯一发布的，而且是版本无关的：同一个运行器服务于 Maestro 2.5.x 到 2.7.x，所以不要寻找与你 Maestro 版本匹配的资产。

像平常一样安装要测试的应用（`lim ios create --install app.ipa`、`lim ios install-app` 或构建技能），然后在流程中通过 `appId:` 引用其捆绑 ID。对于 Expo Go 测试，还预安装 `appstore/Expo-Go-54.0.6.tar.gz` 并用 `openLink` 打开项目 URL（环境变量必须以 `MAESTRO_` 前缀才能在流程中可见）：

```bash
MAESTRO_EXPO_URL='exp://<tunnel-host>' lim ios maestro test flow.yaml
```

## Expo dev-client 构建

Expo Go 是最快的路径，但 dev-client 构建 也行。`launchApp` 落在开发启动器上而不是你的应用上，所以打开 dev-client URL 而不是你的应用：`- stopApp` 后跟 `- openLink: <scheme>://expo-development-client/?url=<url-encoded-metro-url>`。使用 `limrun-expo-development` 来构建 dev 客户端、启动 Metro 并得出那个 URL。

## Limrun 上的流程注意事项

- `startRecording`/`stopRecording` YAML 命令不受支持（模拟器是远程的）。在运行周围录制：`lim ios record start --id <ios-id>` 立即返回（录制在实例上发生），流程后 `lim ios record stop --id <ios-id> -o video.mp4` 下载视频到本地路径。
- `takeScreenshot` 可以工作，并将 PNG 保存在本地工作目录（或 `--test-output-dir`）中，像标准的 Maestro 一样。
- `addMedia` 和引用本地模拟器文件路径的流程命令不受支持。
- `runScript`/`evalScript` 中的 HTTP 调用必须使用 `https://` URL。纯 `http://` 调用被拒绝（除了到驱动程序本身），因为 Maestro 的纯 HTTP 流量通过本地桥接器路由，该桥接器只转发到远程模拟器。
- 当流程重新运行针对已经打开的应用时（例如 Expo Go），在 `openLink`/`launchApp` 之前用 `- stopApp` 启动它；一个在前景中处于中间状态的应用可能会丢失深度链接，并且过时的屏幕会提前失败断言。
- 队列差异：在稳定的可访问性标识符和文本上锚定断言，而不是在时间上。使用 `extendedWaitUntil` 并设置一个慷慨的超时，用于第一次应用加载。
- 文本选择器匹配元素的访问性标签，在 iOS 上，标签经常折叠在兄弟内容（图标名称、相邻文本）或非断开空格中。在编写选择器之前，用 `lim ios element-tree` 读取确切的标签，而不是猜测屏幕显示的内容。

## 验证信号

- `Running maestro <version> against <ios-id>...` 然后是 `Running on Limrun iPhone - iOS ...`：驱动程序端到端连接。
- `Launching the Maestro runner...`：在此实例上的第一次使用。`Installing the Maestro runner...` 仅当实例在没有运行器资产的情况下创建时才会额外出现。后续运行会跳过两者。
- Maestro 本身在每次运行时都会打印几行 JDK `WARNING`（反射、本地访问），它们是上游噪音，不是 Limrun 错误。
- 流程失败会打印 Maestro 自己的调试输出目录，其中包含屏幕截图和 UI 层次结构；`lim ios element-tree --id <ios-id>` 在调试选择器时显示实时屏幕。

## 清理

完成时删除实例：`lim ios delete <ios-id>` (`--id` 对删除无效)。`lim ios maestro` 启动的连接在命令退出时会被拆除。
