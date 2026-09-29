---
name: limrun-android-emulator
description: 在 Limrun 云 Android 模拟器上运行应用程序：安装 APK，通过崩溃报告启动和终止应用程序，点击、输入、读取 UI 元素树，截图、录制视频、注入麦克风音频、调整网络带宽、读取应用程序日志、运行 Shell 命令、传输文件，通过 HTTP 检查和 HAR 捕获将应用程序的网络目的地通过您的机器进行隧道传输，并使用 CLI 的 adb 隧道进行完整的 logcat 和交互式工具。在构建后（来自 limrun-gradle 或任何构建器）使用，当用户希望在模拟器上查看、测试或与他们的应用程序交互，或说“给我一个截图”、“点击”、“在模拟器上运行它”、“检查 logcat”、“录制视频”、“检查网络流量”或“从模拟器连接到我的本地服务器”。要首先构建 APK 或 AAB，请使用 limrun-gradle。
---

# Limrun Android Emulator

与在任何环境（Linux、Windows、macOS、虚拟机、容器）中运行的 Limrun 云 Android 模拟器中的应用程序进行交互。这项技能与构建无关：它假设 APK 已经构建完成，通常由 **limrun-gradle** 构建。将构建问题保留在该技能中；这个技能是关于驱动正在运行的模拟器。

永远不要使用本地模拟器、本地 Android SDK 或 Android Studio。

## 认证和 CLI

如果需要，请安装：`npm install --global lim`。认证是 `lim login` 或 `LIM_API_KEY`（即使 `.env` 和 shell 没有显示，它也可能已经设置在用户的环境中；在要求它之前进行检查）。CLI 是真相来源：这个技能中的命令是经过验证的，但如果一个标志出错或你需要这里没有显示的标志，请检查 `lim android <子命令> --help` 而不是猜测。

## 安装应用程序

你可以使用 Limrun 的远程 Gradle 服务构建，并自动在新的模拟器上安装 APK，或者安装预构建的本地 APK 或 URL。首先需要知道一个默认值：`lim android create` 打开 ADB 隧道（`--connect`）和带有实时流（`--open`）的浏览器标签页，除非另有指示。作为代理，始终传递 `--no-open`，并且除非你需要立即使用 adb，否则传递 `--no-connect`。

### 构建和安装

将 **limrun-gradle** 构建的 APK 作为命名资源上传，然后创建一个预装它的模拟器：

```bash
lim gradle build . --upload myapp.apk
lim android create --install-asset myapp.apk --no-open --no-connect
```

创建块，直到实例准备好驱动；不需要等待启动。创建输出包括一个签名流 URL；将其作为 Markdown 链接与用户共享，例如 `[Live emulator](<signed-stream-url>)`。如果你有一个用户可以查看的浏览器，打开该 URL 并告诉他们。创建还打印一个控制台 URL：它打开相同的实时视图，但需要控制台登录，因此请优先共享签名流 URL。

有用的创建标志：`--reuse-if-exists`（如果标签相同，则重用正在运行的实例）、`--rm`（CLI 退出时删除）、`--jurisdiction us|eu|as`（实例运行的位置；不要使用 `--region`，它已弃用）、`--inactivity-timeout` / `--hard-timeout`、`--display-name` 和 `--label k=v`（稍后使用 `lim android list --label-selector k=v` 找到标记的实例）。

### 从本地安装应用程序

创建一个新的模拟器，然后安装本地文件或 URL：

```bash
lim android create --no-open --no-connect
lim android install-app ./app-debug.apk
lim android install-app https://example.com/app.apk
```

本地路径首先上传到 Limrun 资源存储；实例本身获取 URL，这对于大型 APK 比从你的机器上传快得多。`install-app` 一旦发送应用程序就返回；安装在几秒钟内以背景方式完成。新安装的应用程序位于应用程序抽屉中，而不是主屏幕上，所以不要寻找它们的图标；只需使用 `lim android launch-app <package> --detach`（如果没有 `--detach`，它会阻塞监视应用程序直到它退出）或确认 `lim android adb-shell -- sh -c "pm list packages | grep <name>"`。

每次你需要安装新的 APK 版本时，请同步而不是重新安装：

```bash
lim android sync ./app-debug.apk
```

它只发送与实例上已有的 APK 的差异，然后重新安装。`--watch` 在文件更改时保持重新同步，`--launch-mode ForegroundIfRunning|RelaunchIfRunning` 控制每次安装后正在运行的应用程序发生什么。

## 针对正确的实例

大多数 `lim android` 命令默认为最后创建的实例，并从当前工作目录的 **git 仓库 / 工作树** 中解析“当前”一个。在不同的目录（或在任何 git 仓库之外）命令可能会报告没有找到最近的实例，即使有一个正在运行。可靠的配方：

```bash
lim android list                          # 显示所有实例及其 ID
lim android element-tree --id <that-id>   # 将 --id 传递给 EVERY lim android 命令
```

一旦你有了 ID（格式 `android_<region>_<ulid>`），将 `--id <android-instance-id>` 传递给所有 `lim android` 调用，以供会话其余时间使用。或者，对项目进行 `git init`，以便工作空间自行解析。在控制多个实例时，始终传递 `--id`。

## 启动应用程序

通过包名启动和停止已安装的应用程序：

```bash
lim android launch-app com.example.app --detach                  # 启动并返回
lim android launch-app com.example.app                           # 启动并监视直到它退出
lim android launch-app com.example.app --mode RelaunchIfRunning  # 重新启动以获得干净的状态
lim android terminate-app com.example.app                        # 停止它，例如重置应用程序状态
```

如果没有 `--detach`，`launch-app` 会阻塞监视应用程序：当它崩溃、ANRs 或停止时，命令会打印退出原因、带有堆栈跟踪的崩溃详细信息以及最近的应用程序日志尾，然后返回。该报告是查看应用程序死因的方式，而无需 adb；在应用程序运行时使用 `lim android app-log`（下面）。没有 `list-apps`；发现包名使用 `lim android adb-shell -- pm list packages`，或者从构建中获取应用程序 ID。

## 应用程序日志

一个应用程序的日志不需要隧道：

```bash
lim android app-log com.example.app --tail 100   # 最近几行（应用程序必须正在运行）
lim android app-log com.example.app --follow     # 流式传输实时几行，直到 Ctrl+C；不要流式传输到上下文
```

## Shell 和文件

一次性 Shell 命令和文件传输也不需要隧道：

```bash
lim android adb-shell -- pm list packages -3                     # 像adb shell；参数在 -- 后面
lim android adb-shell -- sh -c "dumpsys battery | grep level"    # 管道需要一个显式的 shell
lim android push-file ./fixture.json /sdcard/Download/fixture.json
lim android pull-file /sdcard/Download/out.json ./out.json
```

它们以 adb shell 用户相同的权限运行，并且 `adb-shell` 以命令的退出代码退出。

## 通过隧道进行完整的 logcat 和交互式 adb

完整的设备 logcat 和任何交互式内容（Android Studio、scrcpy、流式传输）都通过 CLI 的隧道的纯 `adb` 进行。在一个后台 Shell 中启动隧道并保持其活动状态：

```bash
lim android connect        # 打印 "Tunnel started on 127.0.0.1:<port>."
```

`connect` 为你运行 `adb connect`（如果 adb 不在 PATH 上，请使用 `--adb-path`）。打印的 `127.0.0.1:<port>` 是设备序列；将它与 `-s` 一起传递到每个 adb 调用（`adb devices` 也列出了它）：

```bash
SERIAL=127.0.0.1:<port>
adb -s $SERIAL logcat -d | tail -100    # 转储最近的完整设备日志，不要流式传输到上下文
```

隧道与启动它的进程一起生存和死亡：当该 Shell 退出时，`adb devices` 显示序列为 `offline`，而实例仍在运行。只需再次运行 `lim android connect` 即可获取新的隧道（端口每次都会改变）。过时的离线序列是无害的；`adb disconnect` 会清除它们。

## 测试更改

当模拟器交互是任务的一部分时，在每次安装或同步后使用交互命令测试新功能或更改。专注于更改的内容，并快速测试核心流程。在采取行动之前，先阅读元素树以查看屏幕上有什么：

```bash
lim android element-tree
```

输出是单行上的原始 UIAutomator XML 层次结构，因此一个简单的 grep 会回显整个文档。首先将其拆分为每行一个节点，然后使用 `text`、`resource-id`、`content-desc` 或 `bounds` 你需要的而不是将整个树导入上下文进行 grep：

```bash
lim android element-tree | sed 's/></>\n</g' | grep -i "save"
```

## 与应用程序交互

优先通过资源 ID 点击，然后通过可见文本或内容描述，最后作为最后的手段通过坐标：

```bash
lim android tap-element --resource-id com.example.app:id/startButton
lim android tap-element --text "Save"
lim android tap-element --content-desc "Open menu"
lim android tap 360 800
```

选择器值必须完全匹配，而不是通过子字符串：`--text "Save"` 不会匹配一个 "Save draft" 按钮。从 `element-tree` 复制值。没有任何匹配的选择器会在几秒钟内以 `No element found for selector` 失败。其他选择器：`--class-name`、`--package-name`、`--index`、`--clickable`、`--enabled`、`--focused` 和 `--bounds-contains-x/y`；将它们组合起来以缩小匹配。在浏览器中的网页上，资源 ID 是页面自己的 DOM ID（如 `searchIcon`），并且通常是空的；选择 `--text` 加上 `--class-name`，或者从节点的 `bounds` 落回坐标。要检查匹配而不点击，请使用与相同选择器的 `find-element`：

```bash
lim android find-element --text "Save"   # 匹配的表格，带有 bounds
```

对于文本输入，直接目标字段；不需要先前的聚焦点击。`type` 使用与 `tap-element` 相同的选择器（`--class-name android.widget.EditText --focused` 对没有资源 ID 的字段有效）：

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

每次交互后，重新运行 `element-tree` 以确认 UI 转换。点击和 `element-tree` 之间不需要睡眠；点击会阻塞直到完成。`open-url` 后的页面加载是异步的：重新运行 `element-tree`，直到你期望的节点出现。一个存在但没有子节点的 `android.webkit.WebView` 表示页面仍在加载，而不是树损坏。

```bash
lim android element-tree
```

### 当元素树为空时

一些 React Native 和 Expo 应用程序根本不暴露任何可访问性节点，这使 `element-tree`、`tap-element` 和 `find-element` 失明（系统对话框仍然暴露节点）。回退到通过像素驱动：拍摄屏幕截图，读取目标坐标，并使用 `tap x y` / `type --x --y`。屏幕截图像素与点击坐标 1:1 映射，因此图像中位于 (360, 1322) 中心的按钮是使用 `lim android tap 360 1322` 点击的。每次操作后重新拍摄屏幕截图以确认结果。

## 屏幕截图和视频

屏幕截图需要一个**位置路径**（不是 `-o`）：

```bash
lim android screenshot screenshot.png
lim android screenshot screenshot.png --id <android-instance-id>
```

使用元素树进行功能断言（元素存在、文本、状态更改），并且只对视觉属性使用屏幕截图。对于任何涉及运动的内容（动画、游戏、流式 UI），请优先使用视频：

```bash
lim android record start                     # 非阻塞
lim android record stop -o /tmp/recording.mp4
```

`record stop` 接受 `--quality 5-10`。录制的帧是屏幕截图分辨率的一半，因此从屏幕截图而不是视频帧中读取点击坐标。对于 UI 更改，请在拉取请求中包含一个演示视频，以便用户可以看到它。

## 使用音频文件模拟麦克风

对于语音驱动流程（助手、语音到文本、音频通话），播放本地音频文件作为模拟器的麦克风。应用程序通过其正常捕获管道听到音频：

```bash
lim android play-on-microphone ./fixtures/command.wav          # 默认循环
lim android play-on-microphone ./fixtures/command.mp3 --once
```

WAV 和 MP3 都可以工作。文件通过 adb 推送，因此此命令需要一个本地 `adb` 二进制文件（如果不在 PATH 上，请使用 `--adb-path`）并打开自己的短时隧道。相机注入仅在 iOS 上可用；对于相机驱动的测试流程，请使用 **limrun-ios-simulator**。

## 形状网络带宽

通过限制实例的 Wi-Fi 带宽来测试慢速网络行为：

```bash
lim android set-wifi-bandwidth --down-kbps 1000 --up-kbps 500
lim android set-wifi-bandwidth --down-kbps 0 --up-kbps 0       # 0 清除限制
```

## 将应用程序流量通过您的机器隧道

当应用程序必须到达只有您的机器可以到达的服务（本地开发服务器、仅限 VPN 的暂存 API）时，或者您需要查看其 HTTP 流量时，启动目标隧道。只有您选择的目标才会通过运行 `lim` 的机器重定向；其他所有内容都直接从实例离开。

```bash
lim android tunnel --selector localhost:8080 --detach --id <android-instance-id>
```

- 一个精确的选择器（`localhost:port` 或 `IP:port`，端口 >= 1024）在模拟器上成为监听器，也作为 `10.0.2.2:<port>` 可达；应用程序连接到它将到达您的机器并被在那里拨打。
- 域选择器（`api.example.com`、`"*.corp.example"`）在模拟器上被拦截，并从您的机器拨打，因此您的 DNS 和 VPN 适用。自行通过 HTTPS 解析 DNS 的应用程序会绕过域拦截。
- 在启动应用程序**之前**启动隧道：较早打开的连接保持其原始路由。每个实例一个隧道；第二次启动失败。

作为代理，始终传递 `--detach`：它在隧道就绪后返回，并在后台进程中保持其活动状态。使用以下方式管理它：

```bash
lim android tunnel status --id <android-instance-id>   # 状态，每个选择器的绑定，最后的拨号失败
lim android tunnel stop --id <android-instance-id>
```

### 检查 HTTP 流量，捕获 HAR，持久化网络日志

检查默认启用：通过隧道的每个 HTTP 和 HTTPS 请求都被解码，作为每个请求的一个摘要行打印（在隧道日志文件中分离时），并在控制台的网络面板中实时显示。

```bash
lim android tunnel --selector "*.api.example" --har ./traffic.har --detach   # 写入 1.2 版本的 HAR，带有正文
lim android tunnel --selector "*.api.example" --persist --detach             # 网络日志在实例终止时持续存在
```

`--persist` 在隧道停止或实例终止时上传正文包含的网络日志作为会话资源，它出现在控制台实例会话页面上，带有 HAR 下载（默认生存期 3 天，`--ttl <seconds>` 最高 30 天）。HTTPS 使用模拟器信任的 CA 解码，因此**具有证书固定失败通过检查域选择器**：将固定主机排除在选择器之外，或传递 `--no-inspect` 以不透明地转发字节（没有摘要、HAR 或持久性）。

## 供人类预览的 URL

将 APK 上传到 Limrun 资源存储，并返回一个预览 URL，供用户在浏览器中手动打开和测试应用程序：

```bash
export ASSET_NAME=myapp.apk   # 可以是任何名称
lim asset push ./app-debug.apk -n ${ASSET_NAME}

echo "https://console.limrun.com/preview?asset=${ASSET_NAME}&platform=android"
```

在 Limrun 控制台中打开链接会配置一个预装 APK 的模拟器。

## 清理

当工作完成后，您可以删除模拟器。`delete` 接受一个**位置** ID（`--id` 不是其他命令的有效标志）：

```bash
lim android delete <android-instance-id>
```

## 注意事项

- **只打包一种 ABI，不要混合。** 模拟器是 x86_64 宿主机，它上报
  `x86_64,arm64-v8a` 并通过翻译层运行 arm64 原生库。仅包含
  `arm64-v8a` 库的 APK 可以正常安装和运行；x86_64 库则以原生方式运行，
  速度最快。如果 APK 混合了多种 ABI，例如某个厂商 SDK 库仅支持 arm64，
  其余库为 x86_64，该 APK 会被安装为 x86_64，但当首次加载仅支持 arm64
  的代码时就会因 `UnsatisfiedLinkError` 而崩溃。仅包含
  `armeabi-v7a` 的 APK 会被拒绝安装并返回
  `INSTALL_FAILED_NO_MATCHING_ABIS`，且在翻译模式下不支持执行应用自带
  的 ARM 命令行二进制文件。
- **选择器必须精确匹配。** `tap-element --text` 和 `find-element --text`
  需要来自 `element-tree` 的完整、精确字符串；子字符串不会匹配到任何内容。
- **`install-app` 在安装完成前即返回。** 应用会在几秒后才真正落地；在启动前
  应使用 `find-element` 或 `pm list packages` 进行验证。建议优先使用
  `install-app <URL>` 或 `create --install-asset`，而非直接使用
  `adb install`：通过 `adb install` 传输大型 APK 时以流式进行且没有任何
  进度输出，看起来像是挂起了好几分钟，若在传输中途强制终止会导致安装损坏。
- **ADB 隧道与 shell 会话绑定。** 当启动它的 shell 退出时隧道也会断开，
  但实例仍在运行；请使用 `lim android connect` 重新连接并重新读取端口，
  该端口每次都会变化。
- **create 管道失败仍可能泄漏实例。** 如果 `create` 调用在客户端出错
  （管道破裂、JSON 解析失败），请检查 `lim android list`；实例可能仍然存在，
  此时应当将其删除。
- **空的元素树通常意味着这是一个 React Native 应用**，而非实例损坏。
  参见上文“元素树为空时”一节。
- **`element-tree` 可能很大。** 请通过 `grep` 管道提取所需内容，而不是将
  整棵树都倒入上下文。
- **在非 git 目录中，实例解析可能无法正确匹配。** 参见上文“定位正确的
  实例”一节；如有疑虑，请显式传入 `--id`。
- **构建错误是构建技能负责处理的部分。** 如果 APK 无法构建，说明问题
  出在上游；请回到 **limrun-gradle** 进行处理。
