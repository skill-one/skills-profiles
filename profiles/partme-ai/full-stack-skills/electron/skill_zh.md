## 何时使用此技能

当用户希望：
- 使用 Electron 构建跨平台桌面应用
- 理解 Electron 架构（主进程、渲染进程、预加载）
- 在进程间实现 IPC（进程间通信）
- 创建和管理 BrowserWindow 实例
- 实现菜单、托盘图标和原生功能
- 打包和分发 Electron 应用
- 使用 Electron Forge 进行项目脚手架和构建
- 调试和测试 Electron 应用
- 实施安全最佳实践
- 使用 Electron API（app、BrowserWindow、ipcMain、ipcRenderer 等）

## 如何使用此技能

此技能的编排结构与 Electron 官方文档结构相匹配（https://www.electronjs.org/zh/docs/latest/，https://www.electronjs.org/zh/docs/latest/api/app）。在使用 Electron 时：

1. **从用户请求中识别主题**：
   - Getting started/快速开始 → `examples/getting-started/installation.md` 或 `examples/getting-started/quick-start.md`
   - Main process/主进程 → `examples/processes/main-process.md`
   - Renderer process/渲染进程 → `examples/processes/renderer-process.md`
   - IPC communication/IPC 通信 → `examples/processes/ipc-communication.md`
   - BrowserWindow/窗口 → `examples/api/browser-window.md`
   - Menu/菜单 → `examples/api/menu.md`
   - Packaging/打包 → `examples/advanced/packaging.md`
   - Security/安全 → `examples/advanced/security.md`

2. **从 `examples/` 目录加载相应的示例文件**：

   **Getting Started (快速开始) - `examples/getting-started/`**：
   - `examples/getting-started/installation.md` - 安装 Electron 和基本设置
   - `examples/getting-started/quick-start.md` - 快速入门教程

   **Processes (进程) - `examples/processes/`**：
   - `examples/processes/main-process.md` - 主进程概念和使用
   - `examples/processes/renderer-process.md` - 渲染进程概念
   - `examples/processes/preload-scripts.md` - 预加载脚本使用
   - `examples/processes/ipc-communication.md` - IPC 通信模式

   **API Examples (API 示例) - `examples/api/`**：
   - `examples/api/browser-window.md` - BrowserWindow 使用
   - `examples/api/menu.md` - 菜单和上下文菜单
   - `examples/api/tray.md` - 系统托盘
   - `examples/api/dialog.md` - 文件对话框
   - `examples/api/ipc-main.md` - ipcMain 使用
   - `examples/api/ipc-renderer.md` - ipcRenderer 使用

   **Advanced (高级) - `examples/advanced/`**：
   - `examples/advanced/packaging.md` - 应用打包
   - `examples/advanced/security.md` - 安全最佳实践
   - `examples/advanced/auto-updater.md` - 自动更新器
   - `examples/advanced/native-modules.md` - 原生模块

   **Tools (工具) - `examples/tools/`**：
   - `examples/tools/electron-forge.md` - Electron Forge 使用
   - `examples/tools/electron-fiddle.md` - Electron Fiddle 使用

3. **遵循该示例文件中的特定说明**，包括语法、结构和最佳实践

   **重要提示**：
   - 所有示例均遵循最新 Electron API
   - 示例使用 CommonJS（require）和 ES 模块（import）
   - 每个示例文件包含关键概念、代码示例和要点
   - 始终检查示例文件以获取最佳实践和常见模式
   - Electron 支持 Windows、macOS 和 Linux

4. **在需要时参考 `api/` 目录中的 API 文档**：
   - `api/app.md` - app 模块 API
   - `api/browser-window.md` - BrowserWindow API
   - `api/ipc-main.md` - ipcMain API
   - `api/ipc-renderer.md` - ipcRenderer API
   - `api/menu.md` - Menu API
   - `api/tray.md` - Tray API

5. **使用 `templates/` 目录中的模板**：
   - `templates/main-process.md` - 主进程模板
   - `templates/preload-script.md` - 预加载脚本模板
   - `templates/renderer-process.md` - 渲染进程模板
   - `templates/package-json.md` - package.json 模板

### 文档映射（与官方文档一一对应）

- `examples/` → https://www.electronjs.org/zh/docs/latest/
- `api/` → https://www.electronjs.org/zh/docs/latest/api/app

## 快速入门示例

```javascript
// main.js
const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')

function createWindow() {
  const win = new BrowserWindow({
    width: 800, height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,  // 安全：始终禁用
      contextIsolation: true    // 安全：始终启用
    }
  })
  win.loadFile('index.html')
}

app.whenReady().then(createWindow)

// IPC 处理器示例
ipcMain.handle('get-data', async () => {
  return { message: '来自主进程的问候' }
})
```

```javascript
// preload.js
const { contextBridge, ipcRenderer } = require('electron')
contextBridge.exposeInMainWorld('api', {
  getData: () => ipcRenderer.invoke('get-data')
})
```

## API 参考 (`api/`)

- `api/app.md` - app 模块 API
- `api/browser-window.md` - BrowserWindow API
- `api/ipc-main.md` / `api/ipc-renderer.md` - IPC API
- `api/menu.md` / `api/tray.md` / `api/dialog.md` - UI API

## 最佳实践

1. **安全**：渲染进程中切勿启用 nodeIntegration，使用预加载脚本
2. **进程分离**：保持主进程和渲染进程分离
3. **IPC 通信**：使用 IPC 在进程间进行安全通信
4. **资源管理**：正确清理资源（窗口、监听器）
5. **错误处理**：实现适当的错误处理和崩溃报告
6. **性能**：优化性能，使用 webContents 进行调试
7. **打包**：使用 Electron Forge 或 electron-builder 进行打包
8. **自动更新**：为生产应用实现自动更新器
9. **原生模块**：处理原生模块兼容性
10. **跨平台**：在所有目标平台上进行测试

## 资源

- **官方网站**：https://www.electronjs.org/zh/
- **文档**：https://www.electronjs.org/zh/docs/latest/
- **API 参考**：https://www.electronjs.org/zh/docs/latest/api/app
- **Electron Forge**：https://www.electronforge.io
- **Electron Fiddle**：https://www.electronjs.org/zh/fiddle
- **GitHub 仓库**：https://github.com/electron/electron

## 关键词

Electron、桌面应用、主进程、渲染进程、预加载、IPC、BrowserWindow、Menu、Tray、Dialog、打包、electron-builder、electron-forge、electron-fiddle、跨平台、桌面应用、主进程、渲染进程、IPC 通信、窗口、菜单、托盘、打包
