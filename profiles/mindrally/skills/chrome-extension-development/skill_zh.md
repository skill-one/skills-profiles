# Chrome 扩展开发

这项技能为 Chrome 扩展开发提供专家级指导，涵盖 JavaScript/TypeScript、浏览器扩展 API 以及现代 Web 开发实践。

## 工作流：从零开始构建 Chrome 扩展

1. **初始化项目** — 使用 `manifest.json`、后台服务工作者、内容脚本和弹出文件创建目录结构。
2. **配置清单** — 在 Manifest V3 格式中定义权限、内容脚本匹配、服务工作者注册和操作设置。
3. **实现后台服务工作者** — 使用 `chrome.*` API 设置扩展生命周期事件监听器、消息传递和闹钟。
4. **构建内容脚本** — 编写与网页 DOM 交互的脚本，通过 `chrome.runtime.sendMessage` 与后台工作者通信，并遵守内容安全策略。
5. **创建弹出界面** — 设计弹出 HTML/CSS 并通过后台和内容脚本实现交互。
6. **添加存储和状态管理** — 使用 `chrome.storage.local` 或 `chrome.storage.sync` 持久化用户设置和扩展状态。
7. **测试和调试** — 通过 `chrome://extensions` 加载未打包的扩展，使用 Chrome 开发者工具检查服务工作者和内容脚本，并运行单元测试。
8. **打包和发布** — 准备商店资源（图标、截图、描述），创建隐私政策，并提交到 Chrome Web Store。

## 示例：最小化 Manifest V3 配置

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "一个使用 Manifest V3 的示例 Chrome 扩展",
  "permissions": ["storage", "activeTab"],
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "background": {
    "service_worker": "background/service-worker.js",
    "type": "module"
  },
  "content_scripts": [
    {
      "matches": ["https://*.example.com/*"],
      "js": ["content/content-script.js"],
      "css": ["content/styles.css"]
    }
  ]
}
```

## 示例：带消息传递的后台服务工作者

```typescript
// background/service-worker.ts

// 监听扩展安装或更新
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    chrome.storage.local.set({ initialized: true, count: 0 });
    console.log('Extension installed');
  }
});

// 处理来自内容脚本或弹出的消息
chrome.runtime.onMessage.addListener(
  (message: { type: string; payload?: unknown }, sender, sendResponse) => {
    if (message.type === 'GET_COUNT') {
      chrome.storage.local.get('count', (result) => {
        sendResponse({ count: result.count ?? 0 });
      });
      return true; // 保持消息通道打开以进行异步响应
    }

    if (message.type === 'INCREMENT') {
      chrome.storage.local.get('count', (result) => {
        const newCount = (result.count ?? 0) + 1;
        chrome.storage.local.set({ count: newCount }, () => {
          sendResponse({ count: newCount });
        });
      });
      return true;
    }
  }
);

// 使用 chrome.alarms 安排周期性任务
chrome.alarms.create('sync-data', { periodInMinutes: 30 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'sync-data') {
    console.log('Running scheduled sync');
  }
});
```

## 代码风格和结构

- 编写清晰、模块化的 TypeScript 代码，并包含正确的类型定义
- 遵循函数式编程模式；避免使用类
- 使用描述性变量名（例如，isLoading、hasPermission）
- 逻辑地组织文件：弹出、后台、内容脚本、工具
- 实现适当的错误处理和日志记录
- 使用 JSDoc 注释记录代码

## 架构和最佳实践

- 严格遵循 Manifest V3 规范
- 在后台、内容脚本和弹出之间划分职责
- 遵循最小权限原则配置权限
- 使用现代构建工具（webpack/vite）进行开发
- 实现适当的版本控制和变更管理

## Chrome API 使用

- 正确使用 `chrome.*` API（存储、标签、运行时等）
- 使用 Promise 处理异步操作
- 使用服务工作者作为后台脚本（MV3 要求）
- 使用 `chrome.alarms` 实现计划任务
- 使用 `chrome.action` API 实现浏览器操作
- 优雅地处理离线功能

## 安全和隐私

- 实现内容安全策略（CSP）
- 安全处理用户数据
- 防止 XSS 和注入攻击
- 在组件之间使用安全消息传递
- 安全处理跨域请求
- 实现安全数据加密
- 遵循 `web_accessible_resources` 最佳实践

## 性能和优化

- 最小化资源使用并避免内存泄漏
- 优化后台脚本性能
- 实现适当的缓存机制
- 高效处理异步操作
- 监控和优化 CPU/内存使用

## UI 和用户体验

- 遵循 Material Design 指南
- 实现响应式弹出窗口
- 提供清晰的用户反馈
- 支持键盘导航
- 确保适当的加载状态
- 添加适当的动画

## 国际化

- 使用 `chrome.i18n` API 进行翻译
- 遵循 `_locales` 结构
- 支持从右到左的语言
- 处理区域格式

## 可访问性

- 实现 ARIA 标签
- 确保足够的颜色对比度
- 支持屏幕阅读器
- 添加键盘快捷键

## 测试和调试

- 高效使用 Chrome 开发者工具
- 编写单元和集成测试
- 测试跨浏览器兼容性
- 监控性能指标
- 处理错误场景

## 发布和维护

- 准备商店列表和截图
- 编写清晰的隐私政策
- 实现更新机制
- 处理用户反馈
- 维护文档

## 遵循官方文档

- 参考 Chrome 扩展文档
- 跟进 Manifest V3 变更
- 遵循 Chrome Web Store 指南
- 监控 Chrome 平台更新

## 输出预期

- 提供清晰、可工作的代码示例
- 包含必要的错误处理
- 遵循安全最佳实践
- 确保跨浏览器兼容性
- 编写可维护和可扩展的代码
