---
name: mobile-platform-native-capabilities-integrate
description: 构建一个使用原生移动设备功能的 Salesforce LWC，包括条形码扫描器、生物识别、位置、NFC、日历、联系人、文档扫描器、地理围栏、AR 空间捕获、应用审核和支付。当用户需要 LWC 扫描条形码、捕获文档照片、读取位置或地理围栏、提示生物识别、读取/写入设备日历或联系人、轻触 NFC、进行支付、提示应用审核或扫描 AR 空间时，使用此技能。同时，在 "lightning/mobileCapabilities"、"mobile capability"、"Nimbus"、"device capability" 触发时使用。不要用于移动离线 / Komaci 初始审核（使用 `mobile-platform-offline-validate`）或用于选择通用 Lightning 基础组件（使用 `design-systems-slds-apply`）。
---

# 使用移动原生功能

`lightning/mobileCapabilities` 模块公开了一组工厂函数，这些函数返回用于访问原生设备功能（如条码扫描、生物识别、位置信息等）的服务对象。每个服务都继承自一个通用的 [BaseCapability](references/base-capability.md) 类，该类提供 `isAvailable()` 方法，因此 LWC 可以在不支持该功能的环境（桌面端、移动网页端）中优雅降级。

此技能引导代理按以下流程操作：(1) 选择正确的能力，(2) 加载权威的类型定义，以及 (3) 将服务接入 LWC，并正确实现可用性门控、错误处理和考虑弃用状态的 API 选择。

## 何时使用此技能

- 用户请求使用下文能力索引中列出的设备能力的 LWC。
- 用户按名称提及 `lightning/mobileCapabilities`、“mobile capability” 或 “Nimbus”。
- 用户希望了解哪些移动原生 API 可用，或哪一个适合其功能需求。

请勿在以下情况使用此技能：

- 对 LWC 进行移动离线审查（lwc:if、内联 GraphQL、Komaci-priming 违规）——请使用 `mobile-platform-offline-validate`。
- 选择或设置样式化的通用 Lightning Base Components / SLDS 设计蓝图——请使用 `design-systems-slds-apply`。

## 前提条件

- 了解该 LWC 将在受支持的移动容器内运行（Salesforce Mobile App、Field Service Mobile App）。这些功能在桌面端和移动网页端不可用；所有调用都必须以 `isAvailable()` 进行门控。
- 熟悉 `lightning/mobileCapabilities` 模块声明（参见 [mobile-capabilities](references/mobile-capabilities.md)）。

## 能力索引

| 能力 | 参考链接 | 一句话用途 |
| --- | --- | --- |
| App Review | [App Review](references/app-review.md) | 提示用户进行原生应用内评价。 |
| AR Space Capture | [AR Space Capture](references/ar-space-capture.md) | 使用 AR 捕获物理空间的 3D 扫描。 |
| Barcode Scanner | [Barcode Scanner](references/barcode-scanner.md) | 通过相机读取 QR / UPC / EAN / Code-128 / 等条码。 |
| Biometrics | [Biometrics](references/biometrics.md) | 通过 Face ID / 指纹进行身份验证。 |
| Calendar | [Calendar](references/calendar.md) | 读取或创建设备日历中的事件。 |
| Contacts | [Contacts](references/contacts.md) | 读取或创建设备通讯录中的条目。 |
| Document Scanner | [Document Scanner](references/document-scanner.md) | 使用带边缘检测的相机扫描纸质文档。 |
| Geofencing | [Geofencing](references/geofencing.md) | 当设备跨越地理边界时触发动作。 |
| Location | [Location](references/location.md) | 读取 GPS 坐标并监听更新。 |
| NFC | [NFC](references/nfc.md) | 读取或写入 NFC 标签。 |
| Payments | [Payments](references/payments.md) | 接收 Apple Pay / Google Pay 支付。 |

## 工作流程

### 步骤 1 — 识别能力

将用户的请求映射到能力索引中的一行。如果请求涉及多个能力（例如“扫描条码并将其存储到联系人中”），请为**每个**能力单独制定计划——每个能力只有一个工厂函数。

### 步骤 2 — 加载共享参考和能力特定参考

在每个会话中**只需读取一次**以下两个共享参考文档——它们适用于所有能力，并且未在单个能力文件中重复：

- [BaseCapability](references/base-capability.md) — 通用接口，包含每个服务都继承的 `isAvailable()` 方法。
- [mobile-capabilities](references/mobile-capabilities.md) — `lightning/mobileCapabilities` 模块声明，显示所有重新导出的服务。

然后，请从上表中打开该能力的参考文件。每个单个能力的参考文件包含服务特定的 TypeScript API（工厂函数、服务接口、选项类型、结果类型、错误类型），并假定上述两个共享参考文件已在上下文中。

不要凭记忆推断 API——请阅读它们。服务正在演进，某些方法明确标记为 `@deprecated`，建议使用新的替代方案。

### 步骤 3 — 将服务接入 LWC

对于每个能力：

1. 从 `lightning/mobileCapabilities` 导入工厂函数：
   ```js
   import { getBarcodeScanner } from 'lightning/mobileCapabilities';
   ```
2. 获取实例：`const scanner = getBarcodeScanner();`
3. 将调用置于 `isAvailable()` 门控之后：
   ```js
   if (!scanner.isAvailable()) {
     // 优雅的回退或用户消息
     return;
   }
   ```
4. 调用**未弃用**的入口点。多个服务将标记为 `@deprecated` 的旧方法与新推荐方法并列——始终优先使用参考文件中的推荐方法。
5. 用 `try/catch` 包装 Promise，并处理服务公开的具类型故障代码（例如 `BarcodeScannerFailureCode`、`LocationServiceFailureCode`）。用户取消、权限被拒和服务不可用是不同的用户体验状态。

### 步骤 4 — 向用户展示故障模式

每个服务都定义自己的故障代码枚举。将代码转换为可操作的用户消息：`USER_DENIED_PERMISSION` 应要求用户授予权限；`USER_DISABLED_PERMISSION` 必须引导用户前往操作系统设置；`SERVICE_NOT_ENABLED` 应作为对开发者可见的错误，不展示给用户。

### 步骤 5 — 保持在受支持的操作环境内

移动原生功能**仅**在 LWC 于受支持的 Salesforce 移动应用内运行时可用。如果同一组件在桌面端或移动网页端渲染，工厂函数仍将返回一个对象，但 `isAvailable()` 将返回 `false`。切勿假设功能可用——对所有调用进行门控。

## 示例

### 示例 — “扫描条码并写入字段”

1. 映射到：Barcode Scanner。
2. 阅读 [Barcode Scanner](references/barcode-scanner.md)。
3. 使用 `scan(options)`（不要使用已弃用的 `beginCapture` / `resumeCapture` / `endCapture` 三重组合）。
4. 在选项中，将 `barcodeTypes` 设置为所需的条码制式（默认为所有受支持的类型），并将 `enableMultiScan: false` 用于单次读取。
5. 在 resolve 时，将 `result[0].value` 写入绑定字段。在 reject 时，对照 `BarcodeScannerFailureCode` 检查 `error.code`。

### 示例 — “为订单总额收取 Apple Pay 支付”

1. 映射到：Payments。
2. 阅读 [Payments](references/payments.md)。
3. 根据 `isAvailable()` 进行门控。
4. 按照参考文件构建支付请求对象。
5. 在 resolve 时，向调用流程展示交易 ID。在 reject 时，分别处理用户取消和支付失败路径。

## 验证清单

- [ ] 每个能力调用前都有 `isAvailable()`。
- [ ] 使用了未弃用的入口点（条码不使用 `beginCapture` / `resumeCapture` / `endCapture` 等）。
- [ ] 每个 reject 路径都映射到了具类型故障代码枚举。
- [ ] 导入来自 `lightning/mobileCapabilities`，而不是来自私有路径。
- [ ] 没有假设该能力可在桌面端或移动网页端运行。

## 故障排除

- **在真实设备上 `isAvailable()` 返回 `false`** — 设备正在运行不受支持的应用环境（不是 Salesforce Mobile 或 Field Service Mobile），或者服务被组织级设置门控。解决方法是组织配置，而非代码。
- **TypeScript 找不到导入** — 确认 LWC 可以访问 `lightning/mobileCapabilities`。该模块在 Salesforce 移动容器内全局声明；在此之外，必须单独安装类型定义。
- **已弃用的条码方法仍然有效** — 是的，但新代码必须使用 `scan()` 和 `dismiss()`。在返回代理接收的任何示例代码之前对其进行重构。
- **一个组件中的多个能力** — 为每个能力获取单独的实例（它们是独立的服务对象）；不要尝试在它们之间共享状态。
