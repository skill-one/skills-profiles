# 使用移动原生功能

`lightning/mobileCapabilities` 模块暴露了一组工厂函数，这些函数返回用于原生设备功能（条形码扫描、生物识别、位置等）的服务对象。每个服务都扩展了一个通用的 [BaseCapability](references/base-capability.md)，并带有 `isAvailable()` 方法，因此 LWC 可以在功能不可用的情况下（桌面、移动网页）优雅地降级。

这项技能将代理引导通过以下步骤：(1) 选择正确的功能，(2) 加载权威的类型定义，以及 (3) 将服务连接到具有正确可用性门控、错误处理和弃用感知 API 选择的 LWC。

## 何时使用此技能

- 用户要求使用以下索引中列出的设备功能的 LWC。
- 用户提及 `lightning/mobileCapabilities`、"移动功能" 或 "Nimbus"。
- 用户想知道哪些移动原生 API 是可用的，或者哪个适合他们的功能。

**不要**使用此技能用于：

- LWC 的移动离线审查（lwc:if、内联 GraphQL、Komaci-priming 违规）— 使用 `reviewing-lwc-mobile-offline`。
- 选择通用的 Lightning Base 组件 — 使用 `using-lightning-base-components`。

## 前置条件

- 知道 LWC 将在受支持的移动容器内运行（Salesforce 移动应用、现场服务移动应用）。这些功能在桌面和移动网页上不可用；在每次调用后使用 `isAvailable()` 进行门控。
- 熟悉 `lightning/mobileCapabilities` 模块声明（参见 [mobile-capabilities](references/mobile-capabilities.md)）。

## 功能索引

| 功能 | 参考 | 一行使用说明 |
| --- | --- | --- |
| 应用审查 | [应用审查](references/app-review.md) | 提示用户进行原生应用内审查。 |
| AR 空间捕获 | [AR 空间捕获](references/ar-space-capture.md) | 使用 AR 捕获物理空间的 3D 扫描。 |
| 条形码扫描器 | [条形码扫描器](references/barcode-scanner.md) | 从相机读取 QR / UPC / EAN / Code-128 / 等。 |
| 生物识别 | [生物识别](references/biometrics.md) | 通过面容 ID / 指纹进行身份验证。 |
| 日历 | [日历](references/calendar.md) | 读取或创建设备日历上的事件。 |
| 联系人 | [联系人](references/contacts.md) | 读取或创建设备地址簿中的条目。 |
| 文档扫描器 | [文档扫描器](references/document-scanner.md) | 使用相机和边缘检测扫描纸质文档。 |
| 地理围栏 | [地理围栏](references/geofencing.md) | 当设备跨越地理边界时触发逻辑。 |
| 位置 | [位置](references/location.md) | 读取 GPS 坐标并监视更新。 |
| NFC | [NFC](references/nfc.md) | 读取或写入 NFC 标签。 |
| 支付 | [支付](references/payments.md) | 进行 Apple Pay / Google Pay 支付。 |

## 工作流程

### 第 1 步 — 确定功能

将用户的功能需求映射到功能索引的一行。如果需求跨越多个功能（例如 "扫描条形码并将其存储在联系人中"），请分别计划每个功能 — 每个功能都有一个工厂函数。

### 第 2 步 — 加载共享和特定功能的引用

每个会话中读取这两个共享引用一次 — 它们适用于每个功能，并且不在每个功能的文件中重复：

- [BaseCapability](references/base-capability.md) — 每个服务扩展的通用接口，带有 `isAvailable()`。
- [mobile-capabilities](references/mobile-capabilities.md) — `lightning/mobileCapabilities` 模块声明，显示每个重新导出的服务。

然后打开上表中每个功能的引用文件。每个特定功能的引用包含服务特定的 TypeScript API（工厂函数、服务接口、选项类型、结果类型、错误类型），并假定上述两个共享引用已经处于上下文中。

不要从内存中推断 API — 读取它。服务会演进，并且某些方法明确标记为 `@deprecated`，以支持新的替代方法。

### 第 3 步 — 将服务连接到 LWC

对于每个功能：

1. 从 `lightning/mobileCapabilities` 导入工厂：
   ```js
   import { getBarcodeScanner } from 'lightning/mobileCapabilities';
   ```
2. 获取实例：`const scanner = getBarcodeScanner();`
3. 在 `isAvailable()` 后面门控调用：
   ```js
   if (!scanner.isAvailable()) {
     // 优雅的回退或用户消息
     return;
   }
   ```
4. 调用**非弃用的**入口点。几个服务保留旧方法标记为 `@deprecated`，同时推荐使用新方法 — 始终在参考中优先使用推荐的方法。
5. 将 Promise 包裹在 `try/catch` 中，并处理服务暴露的定型失败代码（例如 `BarcodeScannerFailureCode`、`LocationServiceFailureCode`）。用户取消与权限拒绝与服务不可用是不同的用户体验状态。

### 第 4 步 — 将失败模式呈现给用户

每个服务定义了自己的失败码枚举。将代码转换为用户可操作的消息：`USER_DENIED_PERMISSION` 应提示用户授予权限；`USER_DISABLED_PERMISSION` 必须引导他们到操作系统设置；`SERVICE_NOT_ENABLED` 应该是开发者可见的错误，不应向用户显示。

### 第 5 步 — 确保在受支持表面上运行

移动功能仅在 LWC 在受支持的 Salesforce 移动应用内运行时可用。如果相同的组件在桌面或移动网页上渲染，工厂仍然会返回一个对象，但 `isAvailable()` 将返回 `false`。永远不要假设可用性 — 每次调用都要进行门控。

## 示例

### 示例 — "扫描条形码并将其写入字段"

1. 映射到：条形码扫描器。
2. 读取 [条形码扫描器](references/barcode-scanner.md)。
3. 使用 `scan(options)`（不要使用弃用的 `beginCapture` / `resumeCapture` / `endCapture` 三重）。
4. 在选项中，将 `barcodeTypes` 设置为所需的符号（默认是所有支持类型）并将 `enableMultiScan: false` 用于单次读取。
5. 在解决时，将 `result[0].value` 写入绑定字段。在拒绝时，检查 `error.code` 对应 `BarcodeScannerFailureCode`。

### 示例 — "为订单总额进行 Apple Pay 支付"

1. 映射到：支付。
2. 读取 [支付](references/payments.md)。
3. 在 `isAvailable()` 上门控。
4. 根据参考构建支付请求对象。
5. 在解决时，将交易 ID 呈现给调用流程。在拒绝时，分别处理用户取消和支付失败路径。

## 验证清单

- [ ] 每个功能调用都由 `isAvailable()` 预先执行。
- [ ] 使用非弃用的入口点（条形码等没有 `beginCapture` / `resumeCapture` / `endCapture`）。
- [ ] 每个拒绝路径都映射到定型失败码枚举。
- [ ] 导入来自 `lightning/mobileCapabilities`，而不是私有路径。
- [ ] 没有假设功能在桌面或移动网页上运行。

## 故障排除

- **`isAvailable()` 在真实设备上返回 `false`** — 设备正在运行不受支持的应用表面（不是 Salesforce 移动应用或现场服务移动应用），或者服务被组织级设置门控。修复是组织配置，而不是代码。
- **TypeScript 找不到导入** — 确认 LWC 可以访问 `lightning/mobileCapabilities`。该模块在 Salesforce 移动容器内全局声明；在该容器外，必须单独安装类型。
- **弃用的条形码方法仍然工作** — 是的，但新代码必须使用 `scan()` 和 `dismiss()`。重构代理在返回之前收到的任何示例代码。
- **一个组件中有多个功能** — 为每个功能获取单独的实例（它们是独立的服务对象）；不要尝试在它们之间共享状态。
