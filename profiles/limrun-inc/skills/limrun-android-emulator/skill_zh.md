# Limrun Android 模拟器

在任何环境（Linux、Windows、macOS、虚拟机、容器）中与在 Limrun 云 Android 模拟器上运行的 App 交互。这项技能与构建无关：它假设 APK 已经构建完成，通常由 **limrun-gradle** 构建。将构建相关的考虑因素保留在该技能中；这个技能是关于驱动正在运行的模拟器。

永远不要使用本地模拟器、本地 Android SDK 或 Android Studio。

## 认证和 CLI

如果需要安装：`npm install --global lim`。认证是 `lim login` 或 `LIM_API_KEY`（它可能设置在项目外部，所以不要因为它缺失在 `.env` 或 shell 中就询问它）。CLI 是真相来源：本技能中的命令经过验证，但如果标志出错或你需要这里没有显示的标志，请检查 `lim android <子命令> --help` 而不是猜测。

## 安装 App

你可以使用 Limrun 的远程 Gradle 服务构建，并自动在新的模拟器上安装 APK，或者安装预构建的本地 APK 或 URL。首先要知道的默认选项：`lim android create` 打开 ADB 隧道（`--connect`）和一个带有实时流（`--open`）的浏览器标签页，除非另有指示。作为代理，始终传递 `--no-open`，并且除非你需要立即使用 adb，否则传递 `--no-connect`。

### 构建 和 安装

将 **limrun-gradle** 构建的 APK 作为命名资源上传，然后创建一个预装了它的模拟器：

```bash
lim gradle build . --upload myapp.apk
lim android create --install-asset myapp.apk --no-open --no-connect
```

创建块直到实例准备就绪以进行驱动；不需要启动等待。创建输出包括一个签名流 URL；将其作为 Markdown 链接与用户分享，例如 `[Live 模拟器](<signed-stream-url>)`。如果你有一个用户可以看到的浏览器，在那里打开 URL 并告诉他们。创建还打印一个控制台 URL：它打开相同的实时视图，但需要控制台登录，所以优先分享签名流 URL。

有用的创建标志：`--reuse-if-exists`（如果存在相同的标签则重用正在运行的实例）、`--rm`（CLI 退出时删除）、`--jurisdiction us|eu|as`（实例运行的位置；不要使用 `--region`，它已弃用）、`--inactivity-timeout` / `--hard-timeout`、`--display-name` 和 `--label k=v`（稍后使用 `lim android list --label-selector k=v` 找到标记的实例）。

### 从本地安装 App

创建一个新的模拟器，然后安装本地文件或 URL：

```bash
lim android create --no-open --no-connect
lim android install-app ./app-debug.apk
lim android install-app https://example.com/app.apk
```

本地路径首先上传到 Limrun 资源存储；URL 由实例本身获取，对于大型 APK 比从你的机器上传快得多。`install-app` 一旦发送 App 就返回；安装在几秒钟内在后台完成。新安装的 App 会出现在 App 抽屉中，而不是主屏幕上，所以不要寻找它们的图标；只需使用 `lim android launch-app <package> --detach`（如果没有 `--detach` 它会阻塞监视 App 直到它退出）或确认 `lim android adb-shell -- sh -c "pm list packages | grep <name>"`。

每次你需要安装新的 APK 版本时，同步而不是重新安装：

```bash
lim android sync ./app-debug.apk
```

它只发送与实例上已有的 APK 的差异，然后重新安装。`--watch` 在文件更改时保持重新同步，`--launch-mode ForegroundIfRunning|RelaunchIfRunning` 控制每次安装后正在运行的应用程序会发生什么。

## 针对正确的实例

大多数 `lim android` 命令默认为最后创建的实例，并从你的 cwd 的 **git 仓库 / 工作树** 中解析“当前”一个。在不同的目录（或在任何 git 仓库外）命令可能会报告没有找到最近的实例，即使有一个正在运行。可靠的配方：

```bash
lim android list                          # 显示所有实例及其 ID
lim android element-tree --id <that-id>   # 将 --id 传递给每个 lim android 命令
```

一旦你有了 ID（格式 `android_<region>_<ulid>`），将 `--id <android-instance-id>` 传递给所有 `lim android` 调用，直到会话结束。或者，对项目进行 `git init`，以便工作空间自行解析。在控制多个实例时，始终传递 `--id`。

## 启动 App

通过包名启动和停止已安装的 App：

```bash
lim android launch-app com.example.app --detach                  # 启动并返回
lim android launch-app com.example.app                           # 启动并监视直到它退出
lim android launch-app com.example.app --mode RelaunchIfRunning  # 重新启动以获得干净的状态
lim android terminate-app com.example.app                        # 停止它，例如以重置应用状态
```

如果没有 `--detach`，`launch-app` 会阻塞监视 App：当它崩溃、ANRs 或被停止时，命令会打印退出原因、带有堆栈跟踪的崩溃详细信息和一个最近的 App 日志尾，然后返回。该报告是查看 App 死亡原因的方式，没有 adb；在 App 运行时使用 `lim android app-log`（见下文）。没有 `list-apps`；使用 `lim android adb-shell -- pm list packages` 发现包名，或从构建中获取应用程序 ID。

## App 日志

一个 App 的日志不需要隧道：

```bash
lim android app-log com.example.app --tail 100   # 最近几行（App 必须在运行）
lim android app-log com.example.app --follow     # 流式传输实时几行直到 Ctrl+C；不要流式传输到上下文
```

## Shell 和文件

一次性 Shell 命令和文件传输也不需要隧道：

```bash
lim android adb-shell -- pm list packages -3                     # 像adb shell；参数在 -- 后面
lim android adb-shell -- sh -c "dumpsys battery | grep level"    # 管道需要一个显式的 shell
lim android push-file ./fixture.json /sdcard/Download/fixture.json
lim android pull-file /sdcard/Download/out.json ./out.json
```

它们以 adb shell 用户相同的权限运行，并且 `adb-shell` 退出时带有命令的退出代码。

## 通过隧道进行完整的 logcat 和交互式 adb

完整的设备 logcat 和任何交互式内容（Android Studio、scrcpy、流式传输）通过 CLI 的隧道的纯 `adb`。在一个后台 Shell 中启动隧道并保持其活动状态：

```bash
lim android connect        # 打印 "Tunnel started on 127.0.0.1:<port>."
```

`connect` 为你运行 `adb connect`（如果 adb 不在 PATH 上，使用 `--adb-path`）。打印的 `127.0.0.1:<port>` 是设备序列；将它与 `-s` 一起传递到每个 adb 调用（`adb devices` 也列出了它）：

```bash
SERIAL=127.0.0.1:<port>
adb -s $SERIAL logcat -d | tail -100    # 转储最近的完整设备日志，不要流式传输到上下文
```

隧道与启动它的进程一起生存和死亡：当该 Shell 退出时，`adb devices` 显示序列为 `offline`，而实例仍在运行。只需再次运行 `lim android connect` 即可获取一个新的隧道（端口每次都会改变）。过时的离线序列是无害的；`adb disconnect` 会清除它们。

## 测试更改

当模拟器交互是任务的一部分时，在每次安装或同步后使用交互命令测试新功能或更改。专注于更改的内容，并快速测试核心流程。在采取行动之前，先通过阅读元素树查看屏幕上有什么：

```bash
lim android element-tree
```

输出是单行上的原始 UIAutomator XML 层次结构，所以一个普通的 `grep` 会回显整个文档。首先将其拆分为每行一个节点，然后 `grep` 你需要的 `text`、`resource-id`、`content-desc` 或 `bounds`，而不是将整个树转储到上下文中：

```bash
lim android element-tree | sed 's/></>\n</g' | grep -i "save"
```

## 与 App 交互

优先通过资源 ID 点击，然后通过可见文本或内容描述，最后作为最后的手段通过坐标：

```bash
lim android tap-element --resource-id com.example.app:id/startButton
lim android tap-element --text "Save"
lim android tap-element --content-desc "Open menu"
lim android tap 360 800
```

选择器值必须完全匹配，而不是通过子字符串匹配：`--text "Save"` 不会匹配一个 "Save draft" 按钮。从 `element-tree` 原封不动地复制值。一个不匹配任何元素的选择器会在几秒钟内失败，显示 `No element found for selector`。其他选择器：`--class-name`、`--package-name`、`--index`、`--clickable`、`--enabled`、`--focused` 和 `--bounds-contains-x/y`；将它们组合起来以缩小匹配范围。在浏览器中的网页上，资源 ID 是页面自己的 DOM ID（例如 `searchIcon`），并且通常是空的；在那里选择 `--text` 加上 `--class-name`，或者从节点的 `bounds` 落回坐标。为了在不点击的情况下检查匹配项，使用与相同选择器一起的 `find-element`：

```bash
lim android find-element --text "Save"   # 匹配项表格，带有 bounds
```

对于文本输入，直接针对字段；不需要先聚焦点击。`type` 使用与 `tap-element` 相同的选择器（`--class-name android.widget.EditText --focused` 对没有资源 ID 的字段有效）：

```bash
lim android type "hello world" --resource-id com.example.app:id/searchBox
lim android type "hello" --x 360 --y 400   # 通过坐标
lim android press-key enter
lim android press-key backspace            # --modifier shift/control/alt/command 以组合
```

对于滚动和导航：

```bash
lim android scroll down --amount 600
lim android scroll up --amount 300
lim android press-key back
lim android press-key home
lim android open-url "https://example.com"   # 在默认浏览器中打开；也触发深度链接
```

每次交互后，重新运行 `element-tree` 以确认 UI 转换。点击和 `element-tree` 之间不需要睡眠；点击会阻塞直到完成。`open-url` 后的页面加载是异步的：重新运行 `element-tree` 直到你期望的节点出现。一个存在但没有子节点的 `android.webkit.WebView` 表示页面仍在加载，而不是树损坏。

```bash
lim android element-tree
```

### 当元素树为空时

一些 React Native 和 Expo App 完全不暴露可访问性节点，这使 `element-tree`、`tap-element` 和 `find-element` 失明（系统对话框仍然暴露节点）。回退到通过像素驱动：截取屏幕截图，读取目标坐标，并使用 `tap x y` / `type --x --y`。屏幕截图像素与点击坐标一对一映射，所以图像中位于 (360, 1322) 中心的按钮通过 `lim android tap 360 1322` 点击。每次操作后重新截图以确认结果。

## 截图和视频

截图需要一个**位置路径**（不是 `-o`）：

```bash
lim android screenshot screenshot.png
lim android screenshot screenshot.png --id <android-instance-id>
```

使用元素树进行功能断言（元素存在、文本、状态更改），并且只将截图用于视觉属性。对于任何涉及运动的操作（动画、游戏、流式 UI），优先选择视频：

```bash
lim android record start                     # 非阻塞
lim android record stop -o /tmp/recording.mp4
```

`record stop` 接受 `--quality 5-10`。录制的帧是截图分辨率的一半，所以从截图而不是视频帧中读取点击坐标。对于 UI 更改，在拉取请求中包含一个演示视频，以便用户可以看到它。

## 使用音频文件模拟麦克风

对于语音驱动流程（助手、语音到文本、音频通话），播放本地音频文件作为模拟器的麦克风。App 通过其正常捕获管道听到音频：

```bash
lim android play-on-microphone ./fixtures/command.wav          # 默认循环
lim android play-on-microphone ./fixtures/command.mp3 --once
```

WAV 和 MP3 都可以工作。文件通过 adb 推送，所以这个命令需要一个本地 `adb` 二进制文件（如果不在 PATH 上，使用 `--adb-path`）并打开它自己的短生命周期隧道。相机注入仅限 iOS；对于相机驱动的测试流程使用 **limrun-ios-simulator**。

## 形状网络带宽

通过限制实例的 Wi-Fi 带宽来测试慢网络行为：

```bash
lim android set-wifi-bandwidth --down-kbps 1000 --up-kbps 500
lim android set-wifi-bandwidth --down-kbps 0 --up-kbps 0       # 0 清除限制
```

## 将 App 的流量通过你的机器隧道

当 App 必须到达只有你的机器可以到达的服务（本地开发服务器、仅 VPN 的预发布 API）时，或者你需要看到它的 HTTP 流量时，启动目标隧道。只有你选择的目的地才会通过运行 `lim` 的机器重定向；其他所有内容都直接离开实例。

```bash
lim android tunnel --selector localhost:8080 --detach --id <android-instance-id>
```

- 一个精确的选择器（`localhost:port` 或 `IP:port`，port >= 1024）在模拟器上成为一个监听器，也作为 `10.0.2.2:<port>` 可达；App 的连接到它的连接会到达你的机器并被在那里拨打。
- 域选择器（`api.example.com`，`"*.corp.example"`）在模拟器上被拦截，并从你的机器拨打，所以你的 DNS 和 VPN 适用。自己解析 DNS 的 App 通过 HTTPS 会绕过域拦截。
- 在启动 App **之前**启动隧道：早先打开的连接会保持其原始路由。每个实例一个隧道；第二次启动失败。

作为代理，始终传递 `--detach`：它在隧道就绪后返回，并在后台进程中保持其活动状态。使用以下方式管理它：

```bash
lim android tunnel status --id <android-instance-id>   # 状态，每个选择器的绑定，最后的拨号失败
lim android tunnel stop --id <android-instance-id>
```

### 检查 HTTP 流量，捕获 HAR，持久化网络日志

检查默认开启：通过隧道的每个 HTTP 和 HTTPS 请求都会被解码，作为每个请求的摘要行打印（当脱离时在隧道日志文件中），并在控制台的网络面板中实时显示。

```bash
lim android tunnel --selector "*.api.example" --har ./traffic.har --detach   # 写入包含体的 HAR 1.2
lim android tunnel --selector "*.api.example" --persist --detach             # 网络日志在实例终止后仍然存在
```

`--persist` 在隧道停止或实例终止时上传包含体的网络日志作为会话资源，它会在控制台的实例会话页面中出现，并提供 HAR 下载（默认生存期 3 天，`--ttl <seconds>` 最长 30 天）。HTTPS 使用模拟器信任的 CA 解码，所以**具有证书固定功能的 App 会通过检查的域选择器失败**：将固定的主机从选择器中排除，或将 `--no-inspect` 传递以不透明地转发字节（不提供摘要、HAR 或持久化）。

## 供人类预览的 URL

将 APK 上传到 Limrun 资源存储，并返回一个预览 URL，供用户在浏览器中手动打开并测试 App：

```bash
export ASSET_NAME=myapp.apk   # 可以是任何名称
lim asset push ./app-debug.apk -n ${ASSET_NAME}

echo "https://console.limrun.com/preview?asset=${ASSET_NAME}&platform=android"
```

在 Limrun 控制台中打开链接会为 APK 预装一个模拟器。

## 清理

当工作完成后，你可以删除模拟器。`delete` 接受一个**位置** ID（这里 `--id` 不是一个有效的标志，与其他命令不同）：

```bash
lim android delete <android-instance-id>
```

## 注意事项

- **发送一个 ABI，而不是混合。** 模拟器是 x86_64 主机，报告 `x86_64,arm64-v8a` 并通过翻译运行 arm64 本地库。只有 `arm64-v8a` 库的 APK 可以安装和运行；x86_64 库原生运行最快。一个混合 ABI 的 APK（一些仅 arm64 的供应商 SDK 库和其余 x86_64）会作为 x86_64 安装，然后在 arm64 仅代码第一次加载时崩溃，显示 `UnsatisfiedLinkError`。仅 `armeabi-v7a` 的 APK 会因 `INSTALL_FAILED_NO_MATCHING_ABIS` 被拒绝，并且执行自己的捆绑 ARM 命令行二进制的 App 不支持翻译。
- **选择器完全匹配。** `tap-element --text` 和 `find-element --text` 需要来自 `element-tree` 的完整、精确字符串；子字符串匹配不到任何内容。
- **`install-app` 在安装完成前返回。** App 几秒钟后到达；在启动之前使用 `find-element` 或 `pm list packages` 进行验证。优先选择 `install-app <URL>` 或 `create --install-asset` 覆盖原始 `adb install`：对于大型 APK 通过 `adb install` 流式传输没有进度输出，看起来挂起了几分钟，并且中途杀死它会损坏安装。
- **ADB 隧道是会话绑定的。** 它会随着启动它的 Shell 死亡，而实例仍在运行；使用 `lim android connect` 重新连接并重新读取端口，它每次都会改变。
- **失败的创建管道仍然可能泄漏一个实例。** 如果 `create` 调用在客户端出错（broken pipe，JSON 解析），检查 `lim android list`；实例可能仍然存在，应该被删除。
- **空的元素树通常意味着一个 React Native App**，而不是一个损坏的实例。见上面的“当元素树为空时”。
- **`element-tree` 可能很大。** 通过 `grep` 提取你需要的内容，而不是将整个树转储到上下文中。
- **实例解析可能在非 git 目录中遗漏。** 见上面的“针对正确的实例”；如有疑问，传递 `--id`。
- **构建错误是构建技能的工作。** 如果 APK 没有构建，失败是上游的；回到 **limrun-gradle**。
