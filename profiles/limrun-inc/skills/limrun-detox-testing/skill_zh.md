# Limrun 解毒

用于 Limrun iOS 的 Detox 运行时工作。除非用户明确要求原生构建，否则请将构建问题与其他问题分开。

## 组件

- 测试器：本地 Node/Jest/Detox 进程。
- 中介：`detox run-server`，通常位于代理机器上。
- 应用客户端：由 limulator 通过 `lim ios launch-app --runtime detox` 注入。

## CLI 流程

在运行本会话中未使用过的命令之前，请先检查当前帮助信息：

```bash
lim ios tunnel --help
lim ios launch-app --help
```

从不同的终端运行长时间运行的中介、测试器和隧道。
在使用此快速路径之前，请确保项目的 `.detoxrc` 读取了会话环境。Detox 不会自动消耗这些变量：

```js
session: {
  server: process.env.DETOX_SERVER || 'ws://localhost:8099',
  sessionId: process.env.DETOX_SESSION_ID || 'limrun-detox',
}
```

完整的配置如下面的 **Detox 测试设置** 所示。

终端 1：

```bash
npx detox run-server -p 8099 -l verbose
```

终端 2：

```bash
lim ios tunnel \
  --selector localhost:8099 \
  --detach \
  --id <ios-id>
DETOX_SERVER_URL="ws://localhost:8099"
```

终端 3 在应用连接之前启动测试器：

```bash
DETOX_SERVER="ws://localhost:8099" \
DETOX_SESSION_ID=<session-id> \
  npx detox test --no-start
```

然后从终端 2 重新启动应用。从项目中使用 `node_modules/detox` 运行时，`--detox-version` 是可选的。

```bash
lim ios launch-app <bundle-id> \
  --id <ios-id> \
  --runtime detox \
  --detox-server-url "$DETOX_SERVER_URL" \
  --detox-session-id <session-id> \
  --detox-version <detox-version>
```

建议在应用连接之前启动测试器，或使用维护的编排，在 [limrun-inc/typescript-sdk `examples/detox-ios`](https://github.com/limrun-inc/typescript-sdk/tree/main/examples/detox-ios) 中，以避免中介“无法转发”的无害噪声。
如果您在 `npx detox test --no-start` 之前手动启动应用，则中介消息是预期的，直到测试器连接。

如果隧道启动报告活动会话，请使用 `lim ios tunnel status --id <ios-id> --json` 检查它。使用 `lim ios tunnel stop --id <ios-id>` 停止过时的会话，然后重新启动声明的中介选择器。
空闲的隧道不会计入实例活动，因此它不会阻止模拟器在测试运行之间的不活动超时。

## Detox 测试设置

`npx detox test --no-start` 仍然需要正常的 Detox 项目配置：

- 从您的项目中传递 Detox 配置文件和配置名称（有关参考布局，请参阅 [`limrun-inc/typescript-sdk examples/detox-ios/.detoxrc.cjs`](https://github.com/limrun-inc/typescript-sdk/blob/main/examples/detox-ios/.detoxrc.cjs)）。
- 使用 Limrun 第三方驱动程序：`type: '@limrun/detox/driver'`。
- 保持 `DETOX_SERVER` 和 `DETOX_SESSION_ID` 与中介和启动命令一致。
- 当截图或驱动程序调用需要实例 API 时，提供 Limrun 驱动程序环境，例如 `LIMRUN_IOS_ID`、`LIMRUN_IOS_API_URL` 和 `LIMRUN_IOS_TOKEN`。

使用 [limrun-inc/typescript-sdk `examples/detox-ios`](https://github.com/limrun-inc/typescript-sdk/tree/main/examples/detox-ios) 作为维护的精确配置/环境连接的快速路径。仅在详细日志不足以使用时，才在 `detox run-server` 上使用 `-l trace`。

对于原生 SwiftUI 应用，最小的 Detox 配置通常如下：

```js
const server = process.env.DETOX_SERVER || 'ws://localhost:8099';
const sessionId = process.env.DETOX_SESSION_ID || 'limrun-detox';

module.exports = {
  testRunner: { args: { $0: 'jest' }, jest: { setupTimeout: 120000 } },
  session: {
    server,
    sessionId,
    debugSynchronization: 0,
  },
  apps: { ios: { type: 'ios.app', binaryPath: 'unused-by-limrun' } },
  devices: {
    limrun: {
      type: '@limrun/detox/driver',
      device: { id: process.env.LIMRUN_IOS_ID },
    },
  },
  configurations: {
    'ios.limrun': {
      device: 'limrun',
      app: 'ios',
      behavior: { init: { reinstallApp: false }, cleanup: { shutdownDevice: false } },
    },
  },
};
```

然后使用 `lim ios launch-app <bundle-id> --runtime detox ...` 启动，并运行 `npx detox test --no-start`。

## 验证信号

- 应用连接：`detox run-server` 记录 `role:"app"` 和 `appConnected:true`。
- 测试器连接：相同的会话达到 `testerConnected:true, appConnected:true`。
- 运行时加载：应用在 `--runtime detox` 启动后连接到中介。
- UI 可见：`lim ios element-tree --id <ios-id>` 显示预期的应用屏幕。

## 注意事项

- 不要传递任意的环境变量、应用参数或可注入路径。使用 `--runtime detox`。
- `--detox-version` 应与测试器使用的本地 `detox` 包版本匹配。如果省略，`lim ios launch-app` 会从当前工作目录解析它；在 Detox 项目外运行时，请显式传递它。
- 不支持的捆绑 Detox 版本应失败并显示清晰的受支持版本列表。
- `Cannot forward the message to the Detox client` 可能仅仅意味着应用在测试器之前连接。
- 对于 SwiftUI，建议使用稳定的可访问性标识符，例如 `.accessibilityIdentifier("greetingText")` 与 `by.id('greetingText')`；`by.text(...)` 可能会错过在 `lim ios element-tree` 中出现的标签。
- 通过首先检查 `lim ios element-tree --id <ios-id>`，然后检查中介日志以获取应用/测试器连接状态来调试失败。
- 通过停止 `detox run-server`、运行 `lim ios tunnel stop --id <ios-id>` 并使用 `lim ios delete <ios-id>` 删除实例来清理手动运行（`--id` 对删除无效）。
- 这不会使 Detox 拥有 iOS 生命周期；请单独准备或重用 Limrun 实例。
