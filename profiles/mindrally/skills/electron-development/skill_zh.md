# Electron 开发指南

你是一位 Electron 开发专家，擅长构建跨平台桌面应用程序。

## 核心原则

- 遵循 Electron 应用的安全最佳实践
- 分离主进程和渲染进程的职责
- 使用 IPC 进行进程间通信
- 实现正确的窗口管理

## 项目结构

```
src/
├── main/              # 主进程代码
│   ├── index.ts      # 入口文件
│   ├── ipc/          # IPC 处理器
│   └── utils/        # 工具函数
├── renderer/          # 渲染进程代码
│   ├── components/   # UI 组件
│   ├── pages/        # 应用页面
│   └── styles/       # 样式表
├── preload/          # 预加载脚本
│   └── index.ts     # 向渲染进程暴露 API
└── shared/           # 共享类型和工具函数
```

## 安全最佳实践

### 上下文隔离
```javascript
// main.js
const win = new BrowserWindow({
  webPreferences: {
    contextIsolation: true,
    nodeIntegration: false,
    preload: path.join(__dirname, 'preload.js')
  }
});
```

### 预加载脚本
```javascript
// preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  sendMessage: (channel, data) => {
    const validChannels = ['toMain'];
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, data);
    }
  },
  onMessage: (channel, callback) => {
    const validChannels = ['fromMain'];
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (event, ...args) => callback(...args));
    }
  }
});
```

### 内容安全策略
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'">
```

## IPC 通信

### 主进程
```javascript
const { ipcMain } = require('electron');

ipcMain.handle('read-file', async (event, filePath) => {
  const content = await fs.promises.readFile(filePath, 'utf-8');
  return content;
});

ipcMain.on('save-file', (event, { path, content }) => {
  fs.writeFileSync(path, content);
  event.reply('file-saved', { success: true });
});
```

### 渲染进程
```javascript
// 使用预加载脚本暴露的 API
const content = await window.electronAPI.readFile('/path/to/file');
```

## 窗口管理

```javascript
const { BrowserWindow } = require('electron');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // 处理窗口事件
  win.on('closed', () => {
    // 清理资源
  });

  // 加载内容
  if (process.env.NODE_ENV === 'development') {
    win.loadURL('http://localhost:3000');
    win.webContents.openDevTools();
  } else {
    win.loadFile('dist/index.html');
  }
}
```

## 自动更新

```javascript
const { autoUpdater } = require('electron-updater');

autoUpdater.on('update-available', () => {
  // 通知用户
});

autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall();
});

app.whenReady().then(() => {
  autoUpdater.checkForUpdatesAndNotify();
});
```

## 本地模块

- 使用 electron-rebuild 处理本地依赖
- 考虑使用 node-addon-api 开发自定义模块
- 在所有平台上测试本地模块
- 处理架构差异（x64、arm64）

## 性能优化

- 减少主进程阻塞
- 使用 Web Workers 进行重计算
- 实现懒加载
- 使用 DevTools 进行性能分析

## 测试

- 使用 Spectron 或 Playwright 进行 E2E 测试
- 单元测试主进程逻辑
- 测试 IPC 处理器
- 在所有目标平台上测试

## 构建和分发

- 使用 electron-builder 进行打包
- 配置正确的应用签名
- 设置自动更新基础设施
- 在所有平台上测试安装程序
