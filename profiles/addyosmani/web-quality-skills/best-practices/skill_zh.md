# 最佳实践

基于 Lighthouse 最佳实践审核的现代网页开发标准。涵盖安全性、浏览器兼容性和代码质量模式。

## 基于证据的审核工作流

当渲染后的页面可用时：

1.  当该功能可用时，运行实时 Lighthouse 最佳实践审核；使用 Chrome DevTools MCP 时，使用 `lighthouse_audit`。使用导航模式进行正常页面加载，或使用快照模式保留当前状态。
2.  检查列出的控制台和网络错误，仅在它们支持发现时才获取详细信息。
3.  用依赖项、标头、配置和源检查补充运行时证据；Lighthouse 不是一个完整的安全评估。
4.  修复相关代码，重新运行相同的审核，并将安全发现与样式偏好分开。

如果实时工具不可用，请使用 Lighthouse CLI 加上集中的依赖项和标头检查。永远不要将 Lighthouse 分数高报为应用程序安全的证据。

## 安全性

当安全性在范围内或实时审核发现相关问题时，请阅读[安全参考](references/SECURITY.md)。它涵盖了 HTTPS/HSTS、CSP 和 Trusted Types、子资源完整性、标头、依赖项、清理和 Cookie。

至少：

*   **使用 HTTPS 且无混合内容。** 仅在确认所有相关子域名都支持 HTTPS 后才添加 HSTS。
*   **将严格的 CSP 视为纵深防御。** 优先考虑非ces或哈希，并在强制执行前使用报告模式进行测试。
*   **清理不受信任的 HTML 并保护 DOM XSS 池。** 当不需要标记时，优先使用文本 API。
*   **固定和审查第三方代码。** 在交付模型支持的情况下使用 SRI，并保持依赖项更新。
*   **在运行时验证响应标头。** 源配置本身并不能证明部署的页面发送了什么。

## 浏览器兼容性

### 文档类型声明

```html
<!-- ❌ 缺失或无效的文档类型 -->
<HTML>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">

<!-- ✅ HTML5 文档类型 -->
<!DOCTYPE html>
<html lang="en">
```

### 字符编码

```html
<!-- ❌ 缺失或晚于字符集 -->
<html>
<head>
  <title>页面</title>
  <meta charset="UTF-8">
</head>

<!-- ✅ 标头中第一个元素是字符集 -->
<html>
<head>
  <meta charset="UTF-8">
  <title>页面</title>
</head>
```

### 视口元标签

```html
<!-- ❌ 缺失视口 -->
<head>
  <title>页面</title>
</head>

<!-- ✅ 响应式视口 -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>页面</title>
</head>
```

### 功能检测

```javascript
// ❌ 浏览器检测（易碎）
if (navigator.userAgent.includes('Chrome')) {
  // Chrome 特定代码
}

// ✅ 功能检测
if ('IntersectionObserver' in window) {
  // 使用 IntersectionObserver
} else {
  // 回退
}

// ✅ 在 CSS 中使用 @supports
@supports (display: grid) {
  .container {
    display: grid;
  }
}

@supports not (display: grid) {
  .container {
    display: flex;
  }
}
```

### 通用程序（当需要时）

优先考虑**在构建时捆绑通用程序**（Babel/SWC + `core-js`，或 `@vitejs/plugin-legacy`），这些通用程序针对您支持的浏览器列表进行定向。这完全消除了运行时检查，并避免了向现代浏览器发送通用程序字节。

如果您必须在运行时加载通用程序，请追加一个脚本元素——永远不要使用 `document.write`（它阻止解析器，并且在异步/延迟上下文中已损坏）：

```html
<script>
  if (!('fetch' in window)) {
    const s = document.createElement('script');
    s.src = '/通用程序/fetch.js';
    s.defer = true;
    document.head.appendChild(s);
  }
</script>
```

**永远不要从您不控制的第三方 CDN 加载通用程序。** `polyfill.io` 服务在 2024 年中期[遭到破坏](https://sansec.io/research/polyfill-supply-chain-attack)并在供应链攻击中用于向 ~100k 个网站提供恶意软件。自托管，或使用经过审核的镜像（例如[Cloudflare 的 `cdnjs` 通用程序构建](https://blog.cloudflare.com/polyfill-io-now-available-on-cdnjs-reduce-your-supply-chain-risk/)）——并使用[子资源完整性](#subresource-integrity-sri-for-third-party-scripts)固定版本。

---

## 已弃用的 API

### 避免

```javascript
// ❌ document.write（阻止解析）
document.write('<script src="..."></script>');

// ✅ 动态脚本加载
const script = document.createElement('script');
script.src = '...';
document.head.appendChild(script);

// ❌ 同步 XHR（阻止主线程）
const xhr = new XMLHttpRequest();
xhr.open('GET', url, false); // false = 同步

// ✅ 异步 fetch
const response = await fetch(url);

// ❌ 应用程序缓存（已弃用）
<html manifest="cache.manifest">

// ✅ Service Workers
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

### 事件监听器 passive

```javascript
// ❌ 非passive 触摸/滚轮（可能阻止滚动）
element.addEventListener('touchstart', handler);
element.addEventListener('wheel', handler);

// ✅ Passive 监听器（允许平滑滚动）
element.addEventListener('touchstart', handler, { passive: true });
element.addEventListener('wheel', handler, { passive: true });

// ✅ 如果您需要 preventDefault，请明确
element.addEventListener('touchstart', handler, { passive: false });
```

---

## 控制台和错误

### 无控制台错误

```javascript
// ❌ 生产环境中的错误
console.log('调试信息'); // 生产环境中移除
throw new Error('未处理的'); // 捕获所有错误

// ✅ 正确的错误处理
try {
  riskyOperation();
} catch (error) {
  // 记录到错误跟踪服务
  errorTracker.captureException(error);
  // 显示用户友好消息
  showErrorMessage('出错了。请重试。');
}
```

### 错误边界（React）

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, info) {
    errorTracker.captureException(error, { extra: info });
  }
  
  render() {
    if (this.state.hasError) {
      return <FallbackUI />;
    }
    return this.props.children;
  }
}

// 使用
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

### 全局错误处理程序

```javascript
// 捕获未处理的错误
window.addEventListener('error', (event) => {
  errorTracker.captureException(event.error);
});

// 捕获未处理的 promise 拒绝
window.addEventListener('unhandledrejection', (event) => {
  errorTracker.captureException(event.reason);
});
```

---

## 源映射

### 生产配置

```javascript
// ❌ 生产环境中暴露源映射
// webpack.config.js
module.exports = {
  devtool: 'source-map', // 暴露源代码
};

// ✅ 隐藏源映射（上传到错误跟踪器）
module.exports = {
  devtool: 'hidden-source-map',
};

// ✅ 或生产环境中无源映射
module.exports = {
  devtool: process.env.NODE_ENV === 'production' ? false : 'source-map',
};
```

**从生产映射中移除 `sourcesContent`** 当上传到您的错误跟踪器时。默认情况下，捆绑程序将完整的原始源嵌入到 `.map` 文件中——任何获得映射的人（包括通过配置错误的上传步骤）都会获得您的未压缩代码。配置您的捆绑程序省略 `sourcesContent`，或使用一个 Sentry/Bugsnag CLI 标志在上传时这样做。

对于 Vite，优先选择 `sourcemap: 'hidden'` 而不是 `'true'`，这样 `//# sourceMappingURL=` 注释就不会发出到包中。

---

## 性能最佳实践

### 避免阻塞模式

```javascript
// ❌ 阻塞脚本
<script src="heavy-library.js"></script>

// ✅ Deferred 脚本
<script defer src="heavy-library.js"></script>

// ❌ 阻塞 CSS 导入
@import url('other-styles.css');

// ✅ Link 标签（并行加载）
<link rel="stylesheet" href="styles.css">
<link rel="stylesheet" href="other-styles.css">
```

### 高效的事件处理程序

```javascript
// ❌ 每个元素上的处理程序
items.forEach(item => {
  item.addEventListener('click', handleClick);
});

// ✅ 事件委托
container.addEventListener('click', (e) => {
  if (e.target.matches('.item')) {
    handleClick(e);
  }
});
```

### 内存管理

```javascript
// ❌ 内存泄漏（从未移除）
const handler = () => { /* ... */ };
window.addEventListener('resize', handler);

// ✅ 完成时清理
const handler = () => { /* ... */ };
window.addEventListener('resize', handler);

// 后来，当组件卸载时：
window.removeEventListener('resize', handler);

// ✅ 使用 AbortController
const controller = new AbortController();
window.addEventListener('resize', handler, { signal: controller.signal });

// 清理：
controller.abort();
```

---

## 代码质量

### 有效的 HTML

```html
<!-- ❌ 无效的 HTML -->
<div id="header">
<div id="header"> <!-- 重复 ID -->

<ul>
  <div>项目</div> <!-- 无效的子元素 -->
</ul>

<a href="/"><button>点击</button></a> <!-- 无效的嵌套 -->

<!-- ✅ 有效的 HTML -->
<header id="site-header">
</header>

<ul>
  <li>项目</li>
</ul>

<a href="/" class="button">点击</a>
```

### 语义化 HTML

```html
<!-- ❌ 非语义化 -->
<div class="header">
  <div class="nav">
    <div class="nav-item">主页</div>
  </div>
</div>
<div class="main">
  <div class="article">
    <div class="title">标题</div>
  </div>
</div>

<!-- ✅ 语义化 HTML5 -->
<header>
  <nav>
    <a href="/">主页</a>
  </nav>
</header>
<main>
  <article>
    <h1>标题</h1>
  </article>
</main>
```

### 图像长宽比

```html
<!-- ❌ 扭曲的图像 -->
<img src="photo.jpg" width="300" height="100">
<!-- 如果实际比例是 4:3，这将挤压图像 -->

<!-- ✅ 保留长宽比 -->
<img src="photo.jpg" width="300" height="225">
<!-- 实际 4:3 尺寸 -->

<!-- ✅ CSS object-fit 以灵活性 -->
<img src="photo.jpg" style="width: 300px; height: 200px; object-fit: cover;">
```

---

## 权限和隐私

### 正确请求权限

```javascript
// ❌ 页面加载时请求（不良用户体验，通常被拒绝）
navigator.geolocation.getCurrentPosition(success, error);

// ✅ 在上下文中请求，在用户操作后
findNearbyButton.addEventListener('click', async () => {
  // 解释为什么需要它
  if (await showPermissionExplanation()) {
    navigator.geolocation.getCurrentPosition(success, error);
  }
});
```

### 权限策略

```html
<!-- 限制强大功能 -->
<meta http-equiv="Permissions-Policy" 
      content="geolocation=(), camera=(), microphone=()">

<!-- 或为特定原点允许 -->
<meta http-equiv="Permissions-Policy" 
      content="geolocation=(self 'https://maps.example.com')">
```

---

## 审核清单

### 安全性（关键）
- [ ] 启用 HTTPS，无混合内容
- [ ] 无易受攻击的依赖项（`npm audit`）
- [ ] 配置 CSP 标头（带有 `frame-ancestors`，`base-uri`，`form-action`）
- [ ] 强制执行 `require-trusted-types-for 'script'`（或在推出期间报告）
- [ ] 使用 SRI 哈希固定第三方 `<script>`/`<link rel="stylesheet">`
- [ ] 存在安全标头（HSTS，X-Content-Type-Options，Referrer-Policy）
- [ ] 无暴露的源映射（并且上传的映射中省略了 `sourcesContent`）

### 兼容性
- [ ] 有效的 HTML5 文档类型
- [ ] 字符集在标头中首先声明
- [ ] 存在视口元标签
- [ ] 未使用已弃用的 API
- [ ] 滚动/触摸的 Passive 事件监听器

### 代码质量
- [ ] 无控制台错误
- [ ] 有效的 HTML（无重复 ID）
- [ ] 使用语义化 HTML 元素
- [ ] 正确的错误处理
- [ ] 组件中的内存清理

### 用户体验
- [ ] 无侵入式插页广告
- [ ] 在上下文中请求权限
- [ ] 清晰的错误消息
- [ ] 适当的图像长宽比

## 工具

| 工具 | 目的 |
|------|---------|
| `npm audit` | 依赖项漏洞 |
| [SecurityHeaders.com](https://securityheaders.com) | 标头分析 |
| [W3C Validator](https://validator.w3.org) | HTML 验证 |
| Live Lighthouse 审核代理（Chrome DevTools MCP: `lighthouse_audit`） | 渲染后的最佳实践检查 |
| Lighthouse CLI | 最佳实践审核回退 |
| [Observatory](https://observatory.mozilla.org) | 安全扫描 |

## 参考

- [MDN Web 安全](https://developer.mozilla.org/en-US/docs/Web/Security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Web 质量审核](../web-quality-audit/SKILL.md)
