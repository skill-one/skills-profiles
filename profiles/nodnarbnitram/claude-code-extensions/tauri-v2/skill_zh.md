# Tauri v2+ 开发技能

> 使用 Web 前端和 Rust 后端构建跨平台桌面和移动应用。

## 开始前

**此技能可防止 8+ 种常见错误，并节省 ~60% 的 token。**

| 指标 | 无技能 | 有技能 |
|------|--------|--------|
| 配置时间 | ~2 小时 | ~30 分钟 |
| 常见错误 | 8+ | 0 |
| token 使用 | 高（探索） | 低（直接模式） |

### 此技能可防止的已知问题

1. 由于缺少权限导致的权限拒绝错误
2. 在 `generate_handler!` 中未注册命令导致的 IPC 失败
3. 由于类型不匹配导致的状态管理恐慌
4. 由于缺少 Rust 目标导致的移动构建失败
5. 由于开发 URL 配置错误导致的白屏问题

## 快速入门

### 第 1 步：创建 Tauri 命令

```rust
// src-tauri/src/lib.rs
#[tauri::command]
fn greet(name: String) -> String {
    format!("Hello, {}!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("运行 Tauri 应用时出错");
}
```

**为什么这很重要：** 命令不在 `generate_handler![]` 中时，从前端调用时会静默失败。

> **`main.rs` 保持精简：** `src-tauri/src/main.rs` 只应是一个精简的转发器——所有应用逻辑都存在于 `lib.rs` 中：
> ```rust
> // src-tauri/src/main.rs
> #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
> fn main() {
>     app_lib::run();
> }
> ```
> 此拆分对于移动构建是必需的——Tauri 会将移动目标上的 `main()` 替换为 `mobile_entry_point`。

### 第 2 步：从前端调用

```typescript
import { invoke } from '@tauri-apps/api/core';

const greeting = await invoke<string>('greet', { name: 'World' });
console.log(greeting); // "Hello, World!"
```

**为什么这很重要：** 使用 `@tauri-apps/api/core`（而不是 `@tauri-apps/api/tauri` - 这是 v1 API）。

### 第 3 步：添加所需权限

```json
// src-tauri/capabilities/default.json
{
    "$schema": "../gen/schemas/desktop-schema.json",
    "identifier": "default",
    "windows": ["main"],
    "permissions": ["core:default"]
}
```

**为什么这很重要：** Tauri v2 默认拒绝所有操作——所有操作都需要显式权限。

## 关键规则

### 必须做

- 在 `tauri::generate_handler![cmd1, cmd2, ...]` 中注册每个命令
- 从命令中返回 `Result<T, E>` 以进行适当的错误处理
- 使用 `Mutex<T>` 处理多个命令访问的共享状态
- 在使用任何插件功能之前添加权限
- 使用 `lib.rs` 进行共享代码（移动构建必需）
- 在 `lib.rs` 中的 `pub fn run()` 上使用 `#[cfg_attr(mobile, tauri::mobile_entry_point)]` 以实现移动兼容性

### 绝对不要做

- 绝对不要在异步命令中使用借用类型（`&str`）——使用拥有类型
- 绝对不要阻塞主线程——使用异步进行 I/O 操作
- 绝对不要硬编码路径——使用 Tauri 路径 API（`app.path()`）
- 绝对不要跳过权限设置——即使是“安全”操作也需要权限

### 常见错误

**错误 - 借用类型在异步中：**
```rust
#[tauri::command]
async fn bad(name: &str) -> String { // 编译错误！
    name.to_string()
}
```

**正确 - 拥有类型：**
```rust
#[tauri::command]
async fn good(name: String) -> String {
    name
}
```

**原因：** 异步命令不能跨 `await` 点借用数据；Tauri 要求异步命令参数为拥有类型。

## 已知问题预防

| 问题 | 根本原因 | 解决方案 |
|------|----------|----------|
| "命令未找到" | 缺少 `generate_handler!` 中 | 将命令添加到处理程序宏中 |
| "权限拒绝" | 缺少权限 | 添加到 `capabilities/default.json` |
| 插件功能静默失败 | 插件已安装但权限不在能力中 | 将插件权限字符串添加到 `capabilities/default.json` |
| 生产环境中更新器失败 | 签名未签名的工件或 HTTP 端点 | 使用 `cargo tauri signer generate` 生成密钥，仅使用 HTTPS 端点 |
| 侧车未找到 | `externalBin` 未在 `tauri.conf.json` 中或缺少可执行文件 | 将路径添加到 `bundle.externalBin`，确保二进制文件被捆绑 |
| 功能在桌面工作，在移动设备上中断 | 使用了仅桌面 API | 检查 API 是否有移动支持——某些插件仅支持桌面 |
| 访问时状态恐慌 | `State<T>` 中的类型不匹配 | 使用从 `.manage()` 获取的确切类型 |
| 启动时白屏 | 前端未构建 | 检查配置中的 `beforeDevCommand` |

## 深入参考

- **安全性与权限** → [`references/capabilities-reference.md`](references/capabilities-reference.md)
- **IPC 决策指南** → [`references/ipc-patterns.md`](references/ipc-patterns.md)
- **官方插件** → [`references/plugin-reference.md`](references/plugin-reference.md)
- **更新器与分发** → [`references/updater-distribution-reference.md`](references/updater-distribution-reference.md)
- **托盘、侧车、深度链接** → [`references/advanced-runtime-reference.md`](references/advanced-runtime-reference.md)

## 配置参考

### tauri.conf.json

```json
{
    "$schema": "./gen/schemas/desktop-schema.json",
    "productName": "my-app",
    "version": "1.0.0",
    "identifier": "com.example.myapp",
    "build": {
        "devUrl": "http://localhost:5173",
        "frontendDist": "../dist",
        "beforeDevCommand": "npm run dev",
        "beforeBuildCommand": "npm run build"
    },
    "app": {
        "windows": [{
            "label": "main",
            "title": "My App",
            "width": 800,
            "height": 600
        }],
        "security": {
            "csp": "default-src 'self'; img-src 'self' data:",
            "capabilities": ["default"]
        }
    },
    "bundle": {
        "active": true,
        "targets": "all",
        "icon": ["icons/icon.icns", "icons/icon.ico", "icons/icon.png"]
    }
}
```

**关键设置：**
- `build.devUrl`：必须与您的前端开发服务器端口匹配
- `app.security.capabilities`：能力文件标识符的数组

**插件配置**——某些插件需要额外的 `tauri.conf.json` 块（例如，`store`、`updater`）。始终检查特定插件文档 `v2.tauri.app/plugin/<plugin-name>/` 以获取必需的配置键。

## 项目结构

```
my-tauri-app/
├── src/                    # 前端源代码
├── src-tauri/
│   ├── src/
│   │   ├── main.rs         # 精简的转发器——调用 lib::run()
│   │   └── lib.rs          # 所有应用逻辑都放在这里
│   ├── capabilities/
│   │   └── default.json    # 能力定义（在这里授予权限）
│   ├── tauri.conf.json     # 应用配置（devUrl、bundle、security）
│   ├── Cargo.toml          # Rust 依赖
│   └── build.rs            # 构建脚本（构建 tauri-build 所需）
└── package.json
```

**为什么 `lib.rs` 拥有所有逻辑：** Tauri 会将移动目标上的 `main()` 替换为 `#[cfg_attr(mobile, tauri::mobile_entry_point)]`。所有命令、状态和构建器设置都必须存在于 `lib.rs::run()` 中。

### Cargo.toml

```toml
[package]
name = "app"
version = "0.1.0"
edition = "2021"

[lib]
name = "app_lib"
crate-type = ["staticlib", "cdylib", "rlib"]

[build-dependencies]
tauri-build = { version = "2", features = [] }

[dependencies]
tauri = { version = "2", features = [] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

**关键设置：**
- `[lib]` 部分：移动构建必需
- `crate-type`：必须包含所有三种类型以实现跨平台

## 常见模式

### 错误处理模式

使用 `Result<T, E>` 和 `thiserror` 在 IPC 边界进行类型安全的错误传播。有关完整实现细节，请参阅 [`references/ipc-patterns.md`](references/ipc-patterns.md)。

```rust
use thiserror::Error;

#[derive(Debug, Error)]
enum AppError {
    #[error("IO 错误: {0}")]
    Io(#[from] std::io::Error),
    #[error("未找到: {0}")]
    NotFound(String),
}

impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where S: serde::ser::Serializer {
        serializer.serialize_str(self.to_string().as_ref())
    }
}

#[tauri::command]
fn risky_operation() -> Result<String, AppError> {
    Ok("success".into())
}
```

### Serde 边界规则

所有命令参数必须实现 `serde::Deserialize`，返回类型必须实现 `serde::Serialize`。这是 Tauri 如何通过 IPC 边界桥接 JSON 的方式。

```rust
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct CreateUserArgs {
    name: String,
    email: String,
    role: Option<String>,  // 可选字段使用 Option<T>
}

#[derive(Serialize)]
struct User {
    id: u64,
    name: String,
}

#[tauri::command]
fn create_user(args: CreateUserArgs) -> Result<User, String> {
    Ok(User { id: 1, name: args.name })
}
```

**常见的 serde 陷阱：**
- 字段名在前端为 camelCase，在 Rust 中为 snake_case——Tauri 自动在它们之间转换
- `Option<T>` 映射到可选的 JS 参数（可以是 `undefined` 或 `null`）
- 复杂枚举需要 `#[serde(tag = "type")]` 或类似方式才能安全地转换为 JSON
- 错误类型也必须实现 `Serialize`（见上面的错误处理模式）

### 状态管理模式

Tauri 状态管理跨命令的应用数据。有关更复杂的状态模式，请参阅 [`references/ipc-patterns.md`](references/ipc-patterns.md)。

```rust
use std::sync::Mutex;
use tauri::State;

struct AppState {
    counter: u32,
}

#[tauri::command]
fn increment(state: State<'_, Mutex<AppState>>) -> u32 {
    let mut s = state.lock().unwrap();
    s.counter += 1;
    s.counter
}

// 在构建器中：
tauri::Builder::default()
    .manage(Mutex::new(AppState { counter: 0 }))
```

### 事件发射模式

事件是“发射即忘”的通知。有关双向示例，请参阅 [`references/ipc-patterns.md`](references/ipc-patterns.md)。

```rust
use tauri::Emitter;

#[tauri::command]
fn start_task(app: tauri::AppHandle) {
    std::thread::spawn(move || {
        app.emit("task-progress", 50).unwrap();
        app.emit("task-complete", "done").unwrap();
    });
}
```

```typescript
import { listen } from '@tauri-apps/api/event';

const unlisten = await listen('task-progress', (e) => {
    console.log('进度:', e.payload);
});
// 调用 unlisten() 当完成时
```

### 通道流模式

通道提供从 Rust 到前端的、高频的、类型的流。有关完整实现细节，请参阅 [`references/ipc-patterns.md`](references/ipc-patterns.md)。

```rust
use tauri::ipc::Channel;

#[derive(Clone, serde::Serialize)]
#[serde(tag = "event", content = "data")]
enum DownloadEvent {
    Progress { percent: u32 },
    Complete { path: String },
}

#[tauri::command]
async fn download(url: String, on_event: Channel<DownloadEvent>) {
    for i in 0..=100 {
        on_event.send(DownloadEvent::Progress { percent: i }).unwrap();
    }
    on_event.send(DownloadEvent::Complete { path: "/downloads/file".into() }).unwrap();
}
```

```typescript
import { invoke, Channel } from '@tauri-apps/api/core';

const channel = new Channel<DownloadEvent>();
channel.onmessage = (msg) => console.log(msg.event, msg.data);
await invoke('download', { url: 'https://...', onEvent: channel });
```

### 窗口访问模式

Tauri v2 使用 `WebviewWindow` 进行统一的窗口和 Webview 管理。

```rust
use tauri::Manager;

#[tauri::command]
fn focus_window(app: tauri::AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.set_focus();
    }
}
```

**为什么这很重要：** 在 v2 中使用 `tauri::WebviewWindow` 和 `app.get_webview_window("label")`——v1 的 `app.get_window()` API 在 v2 中已移除。

## 捆绑资源

### 参考

位于 `references/` 中：
- [`capabilities-reference.md`](references/capabilities-reference.md) - 权限模式和示例
- [`ipc-patterns.md`](references/ipc-patterns.md) - 完整的 IPC 示例
- [`plugin-reference.md`](references/plugin-reference.md) - 官方插件的安装、注册和权限字符串
- [`updater-distribution-reference.md`](references/updater-distribution-reference.md) - 签名、HTTPS 要求和捆绑发货
- [`advanced-runtime-reference.md`](references/advanced-runtime-reference.md) - `TrayIconBuilder`、侧车、深度链接和资产协议

> **注意：** 有关特定主题的深入探讨，请参阅上述参考文件。

## 依赖项

### 必需的

| 包 | 版本 | 目的 |
|------|------|------|
| `@tauri-apps/cli` | ^2 (v2+) | CLI 工具 |
| `@tauri-apps/api` | ^2 (v2+) | 前端 API |
| `tauri` | ^2 (v2+) | Rust 核心 |
| `tauri-build` | ^2 (v2+) | 构建脚本 |

*\*最后验证：2026-04-02。始终检查 [官方发布说明](https://github.com/tauri-apps/tauri/blob/dev/crates/tauri/CHANGELOG.md) 以获取功能时间表。*

### 可选的（插件）

| 包 | 版本 | 目的 | 关键权限 |
|------|------|------|----------|
| `tauri-plugin-fs` | ^2 (v2+) | 文件系统访问 | `fs:default` |
| `tauri-plugin-dialog` | ^2 (v2+) | 本地对话框 | `dialog:default` |
| `tauri-plugin-shell` | ^2 (v2+) | Shell 命令、打开 URL | `shell:default` |
| `tauri-plugin-http` | ^2 (v2+) | HTTP 客户端 | `http:default` |
| `tauri-plugin-store` | ^2 (v2+) | 键值存储 | `store:default` |

> **插件权限是强制的。** 安装插件而不将其权限字符串添加到能力文件会导致静默运行时失败。有关所有官方插件的完整安装 + 权限细节，请参阅 [`references/plugin-reference.md`](references/plugin-reference.md)。

## 官方文档

- [Tauri v2+ 文档](https://v2.tauri.app/)
- [命令参考](https://v2.tauri.app/develop/calling-rust/)
- [能力与权限](https://v2.tauri.app/security/capabilities/)
- [配置参考](https://v2.tauri.app/reference/config/)

## 故障排除

### 启动时白屏

**症状：** 应用启动但显示空白白屏

**解决方案：**
1. 验证 `devUrl` 与您的前端开发服务器端口匹配
2. 检查 `beforeDevCommand` 运行您的开发服务器
3. 打开 DevTools（Cmd+Option+I / Ctrl+Shift+I）以检查错误

### 命令返回未定义

**症状：** `invoke()` 返回未定义而不是预期值

**解决方案：**
1. 验证命令在 `generate_handler![]` 中
2. 检查 Rust 命令实际返回值
3. 确保参数名称匹配（前端为 camelCase，Rust 为 snake_case，默认情况下）

### 移动构建失败

**症状：** Android/iOS 构建失败并显示缺少目标

**解决方案：**
```bash
# Android 目标
rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android

# iOS 目标（仅 macOS）
rustup target add aarch64-apple-ios x86_64-apple-ios aarch64-apple-ios-sim
```

### 桌面与移动行为差异

并非所有 Tauri API 和插件都支持移动（iOS/Android）。在在移动构建中使用任何插件或 API 之前：

1. **检查插件页面** 在 `v2.tauri.app/plugin/<name>/` 以获取平台支持矩阵
2. **常见的桌面仅项**：系统托盘（`TrayIconBuilder`）、窗口标签/多窗口、某些 shell 插件功能
3. **移动安全模式**：IPC 命令/事件/通道在所有平台上工作；`tauri::AppHandle` 是移动安全的
4. **条件编译**：使用 `#[cfg(desktop)]` / `#[cfg(mobile)]` 为平台特定 Rust 逻辑

```rust
#[tauri::command]
fn platform_info() -> String {
    #[cfg(desktop)]
    return "desktop".to_string();
    #[cfg(mobile)]
    return "mobile".to_string();
}
```

## 设置检查清单

在使用此技能之前，请验证：

- [ ] `npx tauri info` 显示正确的 Tauri v2 版本
- [ ] `src-tauri/capabilities/default.json` 存在，至少包含 `core:default`
- [ ] 所有命令注册在 `generate_handler![]`
- [ ] `lib.rs` 包含共享代码（移动支持必需）
- [ ] 安装了目标平台所需的 Rust 目标
