---
name: limrun-ios-simulator
description: 在 Limrun 云 iOS 模拟器上运行的应用程序进行操作：启动、点击、输入、读取可访问性元素树、截图、录制视频、将应用程序连接到本地服务、作为相机播放视频文件，以及运行定时动作链。在构建后（来自任何构建器）使用，当用户希望在模拟器上查看、测试或与应用程序交互，或说出“给我看一张截图”、“点击”、“运行 UI 测试”、“录制视频”、“连接 localhost”、“从模拟器连接我的本地服务器”、“模拟相机”或“在模拟器上启动”时。首先构建应用程序，使用 limrun-xcode-bazel（Bazel 工作区）或 limrun-xcode（xcodebuild 项目）。
---

# Limrun iOS 模拟器

在任何环境（Linux、Windows、macOS、虚拟机、容器）中与在 Limrun 云 iOS 模拟器上运行的应用进行交互。这项技能与构建无关：它假设应用已经被构建技能（`limrun-xcode-bazel` 用于 Bazel，`limrun-xcode` 用于 xcodebuild）构建并安装。将构建相关的问题保留在这些技能中；这个技能是关于驱动正在运行的模拟器。

永远不要使用本地 Xcode、本地模拟器或本地 macOS 工具。

## 认证和 CLI

如果需要，请安装：`npm install --global lim`。认证是 `lim login` 或 `LIM_API_KEY`（即使 `.env` 和 shell 没有显示，它也可能已经在用户的环境中设置；在使用之前检查）。CLI 是真相来源：这个技能中的命令是经过验证的，但如果一个标志出现错误或你需要这里没有显示的标志，请使用 `lim ios <子命令> --help` 而不是猜测。

## 安装应用包

你可以使用 Limrun 远程 Bazel 或 Xcode 服务来构建应用包并自动将其安装到模拟器中，或者你可以将预构建的本地 `.ipa` 文件或 `.app` 文件夹同步到模拟器中。主要要求是它必须为模拟器构建。

### 构建和安装

构建技能通常会为你附加模拟器（`lim xcode rbe --ios`，或者 `lim xcode build .` 然后附加）。检查已经有什么：

```bash
lim xcode get      # 当前构建目标是否附加了模拟器？
lim ios list       # 所有正在运行的 iOS 实例
```

如果没有附加，创建一个。它立即安装最后一个构建，所以你不需要重新构建：

```bash
lim ios create --attach
```

如果创建（或 `lim xcode rbe --ios`）输出包含一个已签名的流 URL，将一个 Markdown 链接与用户分享，例如 `[Live simulator](<signed-stream-url>)`。如果你有一个用户可以看到的浏览器，在那里打开 URL 并告诉他们。否则将 `--no-open` 传递给 `create`：它跳过本地打开 URL，但仍然打印出来以供分享。

`lim xcode get` 打印一个 Limrun 控制台 URL。它打开相同的实时视图，但需要控制台登录，所以对于分享，请优先使用已签名的流 URL。如果你只有控制台 URL，请分享它并提到需要登录。

### 从本地安装应用

创建一个新的模拟器：

```bash
lim ios create
```

与用户分享已签名的流 URL 作为 Markdown 链接，例如 `[Live simulator](<signed-stream-url>)`。如果你有一个用户可以看到的浏览器，在那里打开 URL 并告诉他们。

然后，你可以运行以下命令来从本地上传包：

```bash
lim ios sync <路径到 .ipa 文件或 .app 文件夹>
```

每次你需要安装新版本的包时，都可以运行相同的命令。它将使用差异进行修补并在模拟器中重新加载它。

## 折叠 iPhone Duo

在提供 Duo 的区域创建一个 Duo 实例：

```bash
lim ios create --model iphone-duo
lim ios fold --json --id <实例-ID>
lim ios fold 90 --orientation landscape-left --id <实例-ID>
lim ios fold 90 --id <实例-ID>
lim ios fold 180 --id <实例-ID>
lim ios screenshot ./inner.png --display inner --id <实例-ID>
lim ios tap 300 200 --display inner --id <实例-ID>
```

铰链接受从 **0°（关闭）** 到 **180°（平放）** 的分数角度。省略角度以读取折叠状态。`--orientation` 接受 `portrait`、`pud`（正面朝下）、`landscape-left` 或 `landscape-right`；它可以独立于铰链角度改变。
这会改变原生模拟器铰链，所以应用会收到 Apple 的铰链和布局更新。浏览器流从 2D 开始并提供一个懒加载的 3D 帧面。两种模式都提供铰链和旋转控制，触摸输入在封面和内屏上。框架的
睡眠/唤醒和音量按钮即使在位置锁定时也接受点击和长按。
对于自动化，将 `buttonDown` 和 `buttonUp` 动作与 `client.performActions` 中设置为 `side`、`volumeUp` 或 `volumeDown` 的 `button` 配对。

使用已经连接的 TypeScript 设备客户端：

```ts
const fold = await client.getFoldState(); // 普通模拟器上为 null
await client.setHingeAngle(110);
await client.setDuoOrientation('landscape-left');
const inner = await client.screenshotDisplay('inner');
await client.tapDisplay('inner', inner.width / 2, inner.height / 2);
```

`setDuoOrientation` 接受 `portrait`、`landscape-left`、`landscape-right` 和 `pud`（正面朝下）。显示截图是直立的，并报告点尺寸；`tapDisplay` 使用这些坐标。使用 `outer` 表示封面或 `inner` 表示展开的显示。iOS 关闭的显示返回黑色图像。

使用这些显示特定方法进行 Duo 自动化。现有的截图、录制和可访问性命令不会自动跟随内屏。3D 查看器支持单指触摸和拖动。旋转视图会改变相机；**旋转设备** 会改变原生方向。**笔记本电脑视图**
设置铰链和方向；它不会启用 Apple 的独立 Table 模式。

## 针对正确的实例

大多数 `lim ios` 命令默认为最后创建的实例，并从你的 cwd 的 **git 仓库 / 工作树** 中解析“当前”一个。所以即使模拟器已附加并且 `lim xcode get` 显示它，`lim ios` 命令仍然可以报告 `No instance ID provided and no recent ios instance found`，因为你的 cwd 不是创建实例的 git 工作树（或者根本不是 git 仓库）。这最常发生在使用 `lim xcode rbe --ios` 的新项目中。

当这种情况发生时，可靠的配方是：

```bash
lim xcode get                          # 显示附加模拟器的 ID
lim ios element-tree --id <that-id>    # 将 --id 传递给 EVERY lim ios 命令
```

`lim xcode get` 是附加模拟器 ID 的可靠来源（`lim ios list` 也起作用）。一旦你有了它，将 `--id <ios-instance-id>` 传递给会话中所有的 `lim ios` 调用（截图、点击、输入、element-tree、录制）。或者，对项目进行 `git init`，以便工作区自行解析。在控制多个实例时，始终传递 `--id`。

## 访问本地机器上的服务

目标隧道让 iPhone 模拟器应用保持调用其正常目标，而 CLI 从运行 `lim` 的机器上拨打它们。选择精确的 `localhost:port` 或字面 `IP:port` 目标，或只有你的机器或 VPN 才能访问的域名：

```bash
lim ios tunnel \
  --id <ios-instance-id> \
  --selector localhost:3000 \
  --selector localhost:8081 \
  --selector "*.staging.example" \
  --detach
```

使用应用的正常 URL，例如 `http://localhost:3000`。声明 `localhost:3000` 也会捕获回环形式，例如 `127.0.0.1:3000` 和 `[::1]:3000`，以及 `[::ffff:127.0.0.1]:3000`。域选择器（精确的 `api.corp.example` 或标签绑定通配符 `"*.staging.example"`）在模拟器上被拦截，无论名称是否在公共 DNS 上解析，你的 DNS 和 VPN 都会生效。自己解析 DNS 的应用通过 HTTPS 会绕过域拦截。
隧道仅携带 TCP：最多十个精确选择器和 64 个域选择器，端口 1-65535 除 53；CIDR 和 UDP 不支持。在启动应用或打开页面之前启动隧道：较早打开的连接保持其原始路线，所以如果它首先连接，请重新启动应用。

一个实例只接受一个活动的目标隧道，并且其选择器集是不可变的。要添加或删除目标，停止隧道并使用完整的选择器列表重新启动它：

```bash
lim ios tunnel status --id <ios-instance-id> --json
lim ios tunnel stop --id <ios-instance-id>
```

如果模拟器在本地服务停止时尝试路由，隧道保持活动并报告 `connection_refused`；重启服务而不重新创建模拟器或隧道。

### 检查 HTTP 流量，捕获 HAR，持久化网络日志

检查默认开启：通过隧道的每个 HTTP 和 HTTPS 请求都会被解码，作为每个请求的一个摘要行打印（在分离的隧道日志文件中），并在控制台的网络面板中实时显示。

```bash
lim ios tunnel --selector "*.api.example" --har ./traffic.har --detach   # 写入 HAR 1.2 并包含正文
lim ios tunnel --selector "*.api.example" --persist --detach             # 网络日志在实例终止后仍然存在
```

`--persist` 在隧道停止或实例终止时上传正文包含的网络日志作为会话工件；它出现在控制台实例的会话页面上，并带有 HAR 下载（默认生存期 3 天，`--ttl <seconds>` 最长 30 天）。HTTPS 使用模拟器信任的 CA 进行解码，所以 **具有证书锁定失败的应用通过检查选择器**：
将锁定的主机从选择器中排除，或将 `--no-inspect` 传递以保持端到端的 TLS（没有摘要、HAR 或持久化）。

## 启动应用

构建技能在每次成功构建后都会重新安装并重新启动应用，所以你通常不需要自己启动它。当应用关闭时（新附加到旧构建，或终止后），通过包 ID 启动它：

```bash
lim ios launch-app <bundle-id>                            # 如果已经运行，将其带到前台
lim ios launch-app <bundle-id> --mode RelaunchIfRunning   # 重新启动以获得干净状态
lim ios terminate-app <bundle-id>                         # 停止它，例如重置应用状态
```

如果你不知道包 ID，请运行 `lim ios list-apps`。

`lim ios launch-app` 将实时流应用的日志供你调试。如果你想要启动并忘记，你可以使用 `--detach` 标志。

## 测试更改

当模拟器交互是任务的一部分时，在每次构建后使用交互命令测试新功能或更改。专注于发生了什么变化，以及核心流程的快速冒烟测试。在采取行动之前，先读取元素树以查看屏幕上有什么：

```bash
lim ios element-tree
```

## 与应用交互

优先通过可访问性 ID 点击，然后通过标签，最后作为最后的手段通过坐标：

```bash
lim ios tap-element --ax-unique-id startButton
lim ios tap-element --ax-label "Save"
lim ios tap 201 450
```

`tap-element` 使用真实的合成触摸点击。可访问性树可以看到的元素会自动滚动到视图中。一个与树中没有任何匹配的选择器在约一秒后失败；iOS 懒加载列表行，所以折叠下的行通常根本不在树中。对于这些，传递 `--scroll-search`：CLI 会分页屏幕（向下几页，然后向上）重试点击，直到行出现，这可能需要 ~10 秒。传递 `--activate ax` 以使用可访问性按针权击而不是触摸（不滚动，适用于没有可用框架的元素）。

**工具栏 / 导航栏项通常无法通过 ID 点击。** SwiftUI 将工具栏子项折叠成一个单一的导航栏组，并且这些项即使在设置 `.accessibilityIdentifier(...)`（常规内容 `Button` 会暴露它）时也报告 `AXUniqueId: null`。所以 `tap-element --ax-unique-id` 找不到导航栏按钮。无论如何点击它，请从元素树读取其 `AXFrame` 并通过坐标点击框架的中心：

```bash
lim ios element-tree --id <id> | grep -i -A6 -B2 moon   # 查找项的 AXFrame
lim ios tap <x> <y> --id <id>                           # 点击框架的中心
```

对于文本输入，首先聚焦字段（点击它），然后输入：

```bash
lim ios type "hello world"     # 真实的按键事件；如果没有聚焦字段会出错
lim ios type "hi" --no-require-focus  # 跳过聚焦检查：用于通过坐标点击聚焦的字段，当可访问性聚焦扫描不可靠时
lim ios press-key backspace
lim ios press-key @            # 直接工作 Shift 符号
```

`type` 按下真实按键，所以文本代理会触发，并且字段自己的键盘行为适用（例如，默认文本字段自动大写第一个字母）。要设置纯文本值而没有任何键盘行为，请使用 `set-text`：

```bash
lim ios set-text "P@ssw0rd!" --focused                 # 聚焦的字段
lim ios set-text "hello" --ax-unique-id emailField     # 通过选择器
```

对于滚动和拖动：

```bash
lim ios scroll down --amount 300                       # 从屏幕中心
lim ios scroll down --amount 300 --coordinate 200,400  # 从特定点
lim ios swipe --from 200,600 --to 200,200              # 显式拖动；--duration 800 用于更慢、更精确的
```

每次交互后，重新运行 `element-tree` 以确认 UI 转换。点击和 `element-tree` 之间不需要睡眠；点击会阻塞直到完成。

```bash
lim ios element-tree
```

通过 `perform` 链接多个具有精确时间的操作：

```bash
lim ios perform --action type=tap,x=100,y=200 --action "type=typeText,text=Hello World"
lim ios perform --action type=wait,durationMs=1000 --action type=pressKey,key=enter
lim ios perform --file ./actions.yaml
```

运行 `lim ios perform --help` 获取完整操作语法。

## 截图和视频

截图使用 **位置路径**（不是 `-o`）：

```bash
lim ios screenshot screenshot.png
lim ios screenshot screenshot.png --id <ios-instance-id>
```

使用元素树进行功能断言（元素存在、标签、状态变化），并且只使用截图来检查视觉属性。对于任何涉及运动（动画、游戏、流式 UI）的内容，请优先使用视频：

```bash
lim ios record start                       # 非阻塞
lim ios record stop -o /tmp/recording.mp4
```

对于 UI 更改，请在拉取请求中包含一个演示视频，以便用户可以看到它。

## 应用容器文件

在拉取文件之前列出应用的数据容器，以便你使用应用创建的确切路径。对于列表、拉取、推送和删除，保持相同的 `--bundle-id` 和 `--container-type` 标志：

```bash
lim ios ls Documents --bundle-id com.example.app --container-type data
lim ios pull-file Documents/recording.mov ./recording.mov \
  --bundle-id com.example.app --container-type data
lim ios push-file ./fixture.json Documents/fixture.json \
  --bundle-id com.example.app --container-type data
lim ios delete-file Documents/fixture.json \
  --bundle-id com.example.app --container-type data
```

`lim ios ls` 默认为暂存文件夹根目录。使用 `--bundle-id` 时，它默认为应用包（`--container-type app`）；使用 `data` 表示应用的可写 `Documents`、`Library` 和 `tmp` 目录。`ls` 输出中的路径相对于选定的根，可以直接复制到其他文件命令中。

## 使用视频模拟相机

对于相机驱动流程（二维码扫描、文档捕获、视频通话），播放本地视频文件作为模拟器的相机。应用通过其正常捕获管道看到帧：

```bash
lim ios camera play ./fixtures/qr-scan.mp4            # 默认循环
lim ios camera play ./fixtures/intro.mp4 --no-loop    # 播放一次，最后一帧冻结
lim ios camera clear                                  # 恢复默认相机
```

任何可解码的 AVFoundation 文件都可以工作（H.264/HEVC 在 `.mp4`/`.mov` 中）。当应用必须精确观察剪辑的结束时使用 `--no-loop`（馈送在最后一帧冻结而不是停滞）。

## 供人类预览的 URL

将 `.ipa` 文件直接上传或 `.app` 文件夹的 targz 存档到 Limrun 资产存储，并返回一个预览 URL，供用户在浏览器中打开并手动测试应用。

上传它的方法如下：
```bash
export ASSET_NAME=myapp.tar.gz # 可以是任何名称
lim asset push ${ASSET_NAME}

echo "https://console.limrun.com/preview?asset=${ASSET_NAME}&platform=ios"
```

命令完成后，你可以将以下 URL 给用户点击，以查看预装此包的模拟器。

```
https://console.limrun.com/preview?asset=${ASSET_NAME}&platform=ios
```

## 清理

当工作完成后，你可以删除 iOS 模拟器。

```bash
lim ios delete
```

## 注意事项

- **在非 git 目录中，实例解析可能会失败。** 参考上文的“定位正确的实例”；如有疑问，请使用 `--id` 参数。
- **`element-tree` 可能会很大。** 通过 `grep` / `jq` 管道提取所需内容，而不是将整个树结构输出到上下文中。
- **`type` / `perform typeText` 可能无法驱动 SwiftUI（或 React Native）的状态。** 自动化文本注入通过可访问性设置字段的值，这与真实按键操作**不**总是能触发 SwiftUI 的 `@Binding` / `onChange`。现象：文本出现在字段中（并在 `element-tree` 中显示），但与之绑定的响应式 UI 没有更新（发送按钮保持禁用状态，字符计数器不变化），提交处理程序看到的是空状态。在直播流上的真实键盘可以正常工作。在自动化时，通过可点击控件（如按钮、建议芯片）驱动提交，而不是依赖绑定到响应式状态中的文本，或者让应用程序暴露一个测试功能。
- **工具栏 / 导航栏的项无法通过 id 点击。** 参考上文的“与应用程序交互”：从 `element-tree` 中读取 `AXFrame` 并通过坐标点击。
- **Bundle ID 的发现。** 如果不知道 Bundle ID，在成功安装后运行 `lim ios list-apps`。
- **构建错误是构建技能的工作。** 如果应用程序无法安装，失败是上游问题；返回到 `limrun-xcode-bazel` / `limrun-xcode`。
