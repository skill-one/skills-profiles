# 在 Limrun 上开发 Expo 应用

使用此技能进行 Expo / React Native 特定的设置和 dev-client 迭代，在 iOS 模拟器和 Android 模拟器上。使用 **limrun-ios-simulator** 和 **limrun-android-emulator** 获取命令详情、设备交互、截图、录制和清理，使用构建技能 (**limrun-xcode**, **limrun-gradle**) 获取构建标志详情和非 Expo 工作流。

所有构建和设备操作必须在 Limrun 上运行。不要使用本地 Xcode、本地模拟器、本地 Android SDK 或本地模拟器；仅使用本地 `adb` 通过 CLI 的隧道与远程模拟器通信。

## Expo 准备就绪

在更改 Expo 依赖项或应用配置之前，检查应用的 Expo SDK 版本并使用匹配的 Expo 版本化文档。

验证这是一个 Expo 应用：

```bash
npx expo config --type introspect --json
```

推导出：

- 从 `ios.bundleIdentifier`（iOS）和 `android.package`（Android）中获取 `BUNDLE_ID`，从 `android.package` 中获取 `PACKAGE`。当 `android.package` 缺失时，introspect 报告占位符（如 `com.placeholder.appid`），而构建生成不同的真实 applicationId；在构建之前在 `app.json` 中设置 `android.package`，以便 `$PACKAGE` 与安装的应用匹配。
- 从 `slug` 中获取 `SLUG`。
- 从 `scheme` 中获取 `SCHEME`，如果缺失则回退到 `exp+${SLUG}`。
- 从 `git branch --show-current` 中获取 `BRANCH`，如果缺失则回退到 `main`。
- iOS 上 `ASSET_NAME="${BUNDLE_ID}/${BRANCH}-debug.zip"`，Android 上 `ASSET_NAME="${PACKAGE}/${BRANCH}-debug.apk"`。

## 确保 Dev Client

Expo 开发构建需要 `expo-dev-client`。如果 `package.json` 中缺少它，则自动安装它：

```bash
npx expo install expo-dev-client
```

安装 `expo-dev-client`、添加/删除/更新原生依赖项或更改原生应用配置意味着上传的 Debug 资产已过时。在开始 dev 循环之前构建一个全新的 Debug 应用。不要仅仅是警告用户可能需要重新构建；执行重新构建。

## Debug 构建资产

首先检查是否已存在可重用的 Debug dev-client 资产：

```bash
lim asset list --name-prefix "$BUNDLE_ID/"   # iOS
lim asset list --name-prefix "$PACKAGE/"     # Android
```

仅在以下情况下重用确切的 `$ASSET_NAME`：

- 它存在，
- 本次会议中没有更改原生依赖项或原生配置。

如果当前任务更改了原生依赖项或原生配置，即使 `$ASSET_NAME` 存在，也要跳过资产重用。

重用时，创建或重用设备并安装它：

```bash
lim ios create \
  --reuse-if-exists \
  --install-asset "$ASSET_NAME" \
  --label repo=<repo> \
  --label agent=<agent>

lim android create \
  --reuse-if-exists \
  --install-asset "$ASSET_NAME" \
  --no-open \
  --label repo=<repo> \
  --label agent=<agent>
```

Android 注意：保持 `create` 默认打开的隧道（不要传递 `--no-connect`，这与普通的驾驶会话不同）；Metro 反向隧道在下面运行。注意输出中的实例 ID，并将 `--id` 传递给后续的每个 `lim android` 调用：Metro 和 Expo 从应用目录运行，实例解析是按 git 工作树进行的，因此从其他地方运行的命令将无法找到该实例。

### Android 上的全新构建

远程构建 Debug APK 并将其作为资产上传（Expo 预构建、`--expo-app-dir` 和其他构建标志属于 **limrun-gradle**；默认的 `assembleDebug` 任务是正确的 dev-client 构建）：

```bash
lim gradle build . --upload "$ASSET_NAME"
lim android create --reuse-if-exists --install-asset "$ASSET_NAME" --no-open --label repo=<repo> --label agent=<agent>
```

在运行中的模拟器上进行后续原生重建时，使用 `--upload` 重新构建并通过构建打印的下载 URL 安装新的 APK（实例在服务器端获取它）：

```bash
lim gradle build . --upload "$ASSET_NAME"
lim android install-app "<Download URL from the build output>" --id <android-instance-id>
```

### iOS 上的全新构建

在全新构建时，创建或重用独立的 Xcode 沙盒并在创建模拟器之前构建，这样模拟器不会在长时间构建期间闲置（并触发不活动超时）：

```bash
lim xcode create --reuse-if-exists --label repo=<repo> --label agent=<agent>

lim xcode build . \
  --configuration Debug \
  --upload "$ASSET_NAME"
```

在仓库中运行一次 `lim xcode version set <major|major.minor>`，当项目需要特定 Xcode 时（`27` 用于 Xcode 27 GA，`27.1` 用于预览版）；参见 `limrun-xcode` 了解规则。

在项目布局需要时使用 `--expo-app-dir`、`--scheme` 或 `--workspace`。

然后创建连接到该 Xcode 目标的模拟器；连接会立即安装并启动构建：

```bash
lim ios create --attach \
  --reuse-if-exists \
  --label repo=<repo> \
  --label agent=<agent>
```

在您没有浏览器向用户展示时，向任何 `create` 添加 `--no-open`；它会跳过打开流 URL 并将 URL 留在输出中以供分享。

如果 iOS 模拟器已从重用的资产运行，并且需要后续原生重建，则连接到相同的模拟器，而不是创建第二个：

```bash
lim xcode attach-simulator <ios-instance-id> --id <xcode-instance-id>
```

连接后，每个成功的 `lim xcode build` 都会在连接的模拟器上安装并启动应用。

## 通过 Limrun 在 iOS 上启动 Metro

此流程适用于 iOS。Android 使用 `adb reverse`；跳过 `lim ios` 命令，直接运行 **在 Android 上启动 Metro**。

在安装 Debug 应用后启动一个目标隧道。Metro 可以保持其正常本地端口；Expo 广告 localhost：

```bash
METRO_PORT=8081
lim ios tunnel \
  --selector "localhost:${METRO_PORT}" \
  --detach \
  --id <ios-instance-id>
TUNNEL_URL="http://localhost:${METRO_PORT}"
echo "TUNNEL_URL=$TUNNEL_URL"

EXPO_PACKAGER_PROXY_URL="$TUNNEL_URL" \
  npx expo start --dev-client --port "$METRO_PORT"
```

`EXPO_PACKAGER_PROXY_URL` 保留 localhost 和声明的端口在清单、捆绑 URL 和深度链接中。内联设置它，以便它优先于项目 dotenv 值。在用户迭代期间保持 Metro 和分离的隧道运行。以受管理的后台进程方式运行 Metro，或在启动应用之前将打印的 `TUNNEL_URL` 复制到第二个终端。

如果端口 8081 已被占用，选择另一个显式端口，并使用相同的值作为隧道选择器、`TUNNEL_URL` 和 Expo 的 `--port`。选择器集是不可变的：端口更改时，停止并使用完整的选择器列表重新创建隧道。

仅在真正隔离的网络环境中安装依赖项后添加 `--offline`。离线模式禁用网络检查和依赖项验证，因此不要使用它来弥补普通的 Expo 认证。

### 启动 iOS dev client

通过 dev-client URL 打开 Debug 应用：

```bash
ENCODED_URL="$(node -e 'console.log(encodeURIComponent(process.argv[1]))' "$TUNNEL_URL")"
DEV_CLIENT_URL="${SCHEME}://expo-development-client/?url=${ENCODED_URL}"
lim ios open-url --id <ios-instance-id> "$DEV_CLIENT_URL"
```

如果打开失败且主要方案来自 `scheme`，则使用 `exp+${SLUG}` 重试一次。在全新实例上，iOS dev-menu onboarding 表单可能会消耗第一个深度链接；通过它并再次打开 URL。

对于 Expo Go，将 `--dev-client` 替换为 `--go`，然后打开：

```bash
lim ios open-url \
  --id <ios-instance-id> \
  "exp://${TUNNEL_URL#http://}"
```

隧道生命周期：

```bash
lim ios tunnel status --id <ios-instance-id> --json
lim ios tunnel stop --id <ios-instance-id>
```

一个实例只接受一个活动的目标隧道。在启动另一个路由集之前停止当前隧道。迭代结束时，使用 `Ctrl+C` 停止 Metro，并使用上述命令停止分离的隧道。

如果模拟器在 Metro 停止时尝试路由，隧道将保持活动状态，状态记录相关的 `connection_refused`。使用相同的代理 URL 重新启动 Metro 并重新打开 dev-client URL；不要重新创建模拟器或隧道。

## 在 Android 上启动 Metro

Android 使用 CLI 的 ADB 隧道上的 `adb reverse`。Metro 保持其默认端口 8081，不需要覆盖 packager 主机名，模拟器在 `http://127.0.0.1:8081` 处可达：

```bash
lim android connect --id <android-instance-id>   # 后台 shell；打印 "Tunnel started on 127.0.0.1:<port>."
adb -s 127.0.0.1:<port> reverse tcp:8081 tcp:8081

npx expo start --dev-client --port 8081

DEV_CLIENT_URL="${SCHEME}://expo-development-client/?url=http%3A%2F%2F127.0.0.1%3A8081"
lim android open-url "$DEV_CLIENT_URL" --id <android-instance-id>
```

ADB 隧道随启动它的 shell 死亡，并且每次重新连接时端口都会更改；在重新连接后，使用新的序列重新运行 `adb reverse`。参见 **limrun-android-emulator** 了解隧道详情。

在首次启动时，通过 dev-menu onboarding 表单（`lim android tap-element --text Continue`）并关闭 dev 菜单。捆绑包在原生表单后面加载。

## 备用方案：Expo 隧道

如果 Limrun 端点不可用，启动 Expo 的公共隧道：

```bash
npm install --save-dev '@expo/ngrok@^4.1.0'
npx expo start --dev-client --tunnel
```

使用 Expo 打印的完整 dev-client URI：

```bash
DEV_CLIENT_URL="<complete URI printed by Expo>"
lim ios open-url --id <ios-instance-id> "$DEV_CLIENT_URL"
lim android open-url "$DEV_CLIENT_URL" --id <android-instance-id>
```

## 遗留的 iOS 固定端口反向隧道

`lim ios reverse` 仍然可用于已经使用保留的 57090–57099 范围的工作流。Expo dev-client 可以推导或广告多个 packager URL，因此不匹配的映射（如 `57090:8081`）可能会使某些 URL 指向本地 Metro 端口而不是模拟器面向的反向端点。

在 `lim ios reverse` 打印的模拟器面向主机名中，在 `REACT_NATIVE_PACKAGER_HOSTNAME` 和编码的 dev-client URL 中使用该主机名。在 Metro 运行时，在单独或后台终端中保持反向命令运行：

```bash
lim ios reverse 57090:57090 --id <ios-instance-id>

REACT_NATIVE_PACKAGER_HOSTNAME=<reverse-host> \
  npx expo start --dev-client --host lan --port 57090

ENCODED_URL="$(node -e 'console.log(encodeURIComponent(process.argv[1]))' "http://<reverse-host>:57090")"
DEV_CLIENT_URL="${SCHEME}://expo-development-client/?url=${ENCODED_URL}"
lim ios open-url --id <ios-instance-id> "$DEV_CLIENT_URL"
```

## 验证

对于快速静态验证，请优先使用：

```bash
npx tsc --noEmit
```

仅在仓库已经配置了 ESLint 时运行 `npm run lint` 或 `npx expo lint`。Expo lint 可以创建 ESLint 配置并更改尚未配置代码检查的项目中的依赖项。

在 iOS 上，首先使用元素树：

```bash
lim ios element-tree
```

成功意味着应用 UI 可见或 Expo dev 菜单显示它已连接到隧道。在全新实例上，第一个 dev-client 启动可能会落在覆盖启动器的 dev-menu onboarding 表单上：通过它（`lim ios tap-element --ax-label Continue`），然后再次打开 dev-client URL，因为第一个深度链接被表单消耗。如果树不确认连接，请检查应用日志：

```bash
lim ios app-log "$BUNDLE_ID" --tail 100
```

在 Android 上，通过截图而不是元素树进行验证：Expo 应用通常不在此处暴露无障碍节点，因此渲染的屏幕和空树共存（参见 **limrun-android-emulator**）：

```bash
lim android screenshot check.png --id <android-instance-id>
```

要查看应用崩溃的原因（崩溃、ANR），请监视重新启动它；该命令在应用运行时阻塞（在后台 shell 中运行），并在应用死亡时打印退出原因、堆栈跟踪和最近的最近应用日志尾：

```bash
lim android launch-app "$PACKAGE" --mode RelaunchIfRunning --id <android-instance-id>
```

## 迭代

连接后，JS/TS 编辑应通过 Metro 无需另一个原生构建。如果任务更改了原生依赖项、原生配置或构建设置，请在重新启动 dev 循环之前构建 Debug。

告诉用户：

- 设备流作为短 Markdown 链接，例如 `[Open simulator stream](<signedStreamUrl>)` 或 `[Open emulator stream](<signedStreamUrl>)`
- 上传的 Debug 资产名称
- JS/TS 变化现在可以通过 Metro 迭代
- 原生变化需要新的 Debug 构建

## 最终预览

对于最终可分享的预览或 PR 演示，使用发布构建，以便用户不需要 Metro 运行：

```bash
ASSET_NAME="<bundle-id>/<pr-or-session>.zip"
lim xcode build . --configuration Release --upload "$ASSET_NAME"

ASSET_NAME="<package>/<pr-or-session>.apk"
lim gradle build . --task assembleRelease --upload "$ASSET_NAME"
```

预览 URL（对于 APK 资产使用 `platform=android`）：

```text
https://console.limrun.com/preview?asset=${ASSET_NAME}&platform=ios
```

## 注意事项

- `npx expo start --dev-client` 需要 `expo-dev-client`；没有它，Expo 无法确定开发构建的方案。
- `No script URL provided` 通常意味着应用不是 dev-client 构建，或者没有通过 dev-client URL 启动。
- 在全新原生重建/安装后，可能出现的陈旧的 Metro/运行时错误（如 `Cannot find native module`）可能来自旧的应用进程。在假设重建失败之前，重新打开 dev-client URL 并使用 `element-tree` 进行验证。
- 如果在添加原生依赖项后的 Debug 构建仍然表现得像旧的原生图，那是意外的 Limrun 行为。重试构建；创建全新的构建/设备目标是仅用于故障排除的回退。
- Expo 隧道启动可能不稳定。在更改工作流之前重试。
- 原生依赖项或原生配置更改后，不要重用上传的 Debug 资产。
- 在 Android 上，将 `--id <android-instance-id>` 传递给此循环中的每个 `lim android` 调用：实例解析是按 git 工作树进行的，并且此循环的命令从混合目录运行。
- Android 的空元素树而截图显示应用是正常的，对于 Expo 应用来说是正常的；通过截图进行验证。
