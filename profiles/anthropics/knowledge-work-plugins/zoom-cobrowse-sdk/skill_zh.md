# Zoom Cobrowse SDK - Web 开发

使用 Zoom Cobrowse SDK 进行网页协同浏览的背景参考。在支持流程清晰后，您需要实现细节时使用此文档。

**官方文档**: https://developers.zoom.us/docs/cobrowse-sdk/  
**API 参考**: https://marketplacefront.zoom.us/sdk/cobrowse/  
**快速入门仓库**: https://github.com/zoom/CobrowseSDK-Quickstart  
**认证端点示例**: https://github.com/zoom/cobrowsesdk-auth-endpoint-sample

## 快速链接

**如果您是 Cobrowse SDK 的新手？请遵循此路径：**

1. **[入门指南](get-started.md)** - 从凭证到第一个会话的完整设置
2. **[会话生命周期](concepts/session-lifecycle.md)** - 理解客户和代理的流程
3. **[JWT 认证](concepts/jwt-authentication.md)** - 令牌生成和安全
4. **[客户集成](examples/customer-integration.md)** - 将 SDK 集成到您的网站
5. **[代理集成](examples/agent-integration.md)** - 设置代理门户（iframe 或 npm）

**核心概念：**
- **[两角色模式](concepts/two-roles-pattern.md)** - 客户与代理架构
- **[会话生命周期](concepts/session-lifecycle.md)** - PIN 生成、连接、重连
- **[JWT 认证](concepts/jwt-authentication.md)** - SDK Key 与 API Key、role_type、claims
- **[分发方法](concepts/distribution-methods.md)** - CDN 与 npm（BYOP）

**功能：**
- **[标注工具](examples/annotations.md)** - 绘制、高亮、指针工具
- **[隐私遮罩](examples/privacy-masking.md)** - 遮盖代理的敏感字段
- **[远程协助](examples/remote-assist.md)** - 代理可以滚动客户的页面
- **[多标签持久化](examples/multi-tab-persistence.md)** - 会话跨标签继续
- **[BYOP 模式](examples/byop-custom-pin.md)** - 使用 npm 集成带自己的 PIN

**故障排除：**
- **[常见问题](troubleshooting/common-issues.md)** - 快速诊断和解决方案
- **[错误代码](troubleshooting/error-codes.md)** - 完整错误参考
- **[CORS 和 CSP](troubleshooting/cors-csp.md)** - 跨域和安全策略配置
- **[浏览器兼容性](troubleshooting/browser-compatibility.md)** - 支持的浏览器和限制
- **[5 分钟运行手册](RUNBOOK.md)** - 深度调试前的快速预检

**参考：**
- **[API 参考](references/api-reference.md)** - 完整 SDK 方法和事件
- **[设置参考](references/settings-reference.md)** - 所有初始化设置
- **集成索引** - 查看本文件中的下一节

## SDK 概述

Zoom Cobrowse SDK 是一个 JavaScript 库，提供：

- **实时协同浏览**：代理实时查看客户的浏览器活动
- **基于 PIN 的会话**：客户到代理连接的 6 位安全 PIN
- **标注工具**：绘制、高亮、消失笔、矩形、颜色选择器
- **隐私遮罩**：基于 CSS 选择器的敏感表单字段遮罩
- **远程协助**：代理可以滚动客户的页面（需同意）
- **多标签持久化**：客户打开新标签时会话继续
- **自动重连**：页面刷新时恢复会话（2 分钟窗口）
- **会话事件**：实时事件用于会话状态变化
- **HTTPS 必须使用**：安全连接（仅在回环/本地开发主机上工作 HTTP）
- **无需插件**：纯 JavaScript，无需浏览器扩展

## 两角色架构

Cobrowse 有 **两个不同的角色**，每个角色都有不同的集成模式：

| 角色 | role_type | 集成 | JWT 必须使用 | 目的 |
|------|-----------|-------------|--------------|---------|
| **客户** | 1 | 网站集成（CDN 或 npm） | 是 | 分享其浏览器会话的用户 |
| **代理** | 2 | iframe（CDN）或 npm（仅限 BYOP） | 是 | 查看协助客户的客服人员 |

**关键洞察**：客户和代理使用 **不同的集成方法**，但相同的 JWT 认证模式。

## 首次阅读（关键）

对于客户/代理演示，将客户 SDK 事件 `pincode_updated` 中的 PIN 视为唯一面向用户的 PIN。

- 在 UI 中显示一个清晰标记的值（例如，**支持 PIN**）。
- 使用相同的 PIN 进行代理加入。
- 不要将后端预启动记录中的临时/调试 PIN 暴露给用户。

如果忽略这些规则，代理工作站通常会失败，错误代码为 `30308`。

### 典型生产流程（最常见）

这是大多数团队首先实现的流程，也是用户通常期望在演示中看到的流程：

1. **客户首先开始会话**（`role_type=1`）
   - 后端创建/记录会话
   - 后端返回客户 JWT
   - 客户 SDK 启动并接收一个 PIN
2. **代理第二个加入**（`role_type=2`）
   - 代理输入客户 PIN
   - 后端验证 PIN 和会话状态
   - 后端返回代理 JWT
   - 代理打开 Zoom 托管的桌面 iframe（或 BYOP 的自定义 npm 代理 UI）

如果演示只有一个通用的“会话”用户，它对于真实的 Cobrowse 操作是不完整的。

## 前提条件

### 平台要求

- **支持的浏览器**:
  - Chrome 80+ ✓
  - Firefox 78+ ✓
  - Safari 14+ ✓
  - Edge 80+ ✓
  - Internet Explorer ✗（不支持）

- **网络要求**:
  - HTTPS 必须使用（仅在回环/本地开发主机上工作 HTTP）
  - 允许跨域请求到 `*.zoom.us`
  - CSP 头必须允许 Zoom 域（见 [CORS 和 CSP 指南](troubleshooting/cors-csp.md)）

- **第三方 Cookie**:
  - 必须启用第三方 Cookie 以便刷新重连
  - 隐私模式可能会限制某些功能

### Zoom 账户要求

1. **Zoom Workplace 账户** 带有 SDK Universal Credit
2. **Video SDK 应用** 在 Zoom Marketplace 中创建
3. **Cobrowse SDK 凭证** 从应用的 Cobrowse 选项卡获取

**注意**：Cobrowse SDK 是 Video SDK 的 **功能**（不是独立产品）。

### 凭证概述

您将收到 Zoom Marketplace → Video SDK 应用 → Cobrowse 选项卡中的 **4 个凭证**：

| 凭证 | 类型 | 用于 | 是否安全暴露 |
|------------|------|----------|----------------|
| **SDK Key** | 公开 | CDN URL, JWT `app_key` 声明 | ✓ 是（客户端） |
| **SDK Secret** | 私有 | 签名 JWTs | ✗ 否（仅限服务器端） |
| **API Key** | 私有 | REST API 调用（可选） | ✗ 否（仅限服务器端） |
| **API Secret** | 私有 | REST API 调用（可选） | ✗ 否（仅限服务器端） |

**关键**：SDK Key 是 **公开** 的（嵌入 CDN URL），但 SDK Secret 必须 **永不** 暴露在客户端。

## 快速入门

### 第 1 步：获取 SDK 凭证

1. 前往 [Zoom Marketplace](https://marketplace.zoom.us/)
2. 打开您的 **Video SDK 应用**（或创建一个）
3. 导航到 **Cobrowse** 选项卡
4. 复制您的凭证：
   - SDK Key
   - SDK Secret
   - API Key（可选）
   - API Secret（可选）

### 第 2 步：设置 Token 服务器

部署一个服务器端端点来生成 JWTs。使用官方示例：

```bash
git clone https://github.com/zoom/cobrowsesdk-auth-endpoint-sample.git
cd cobrowsesdk-auth-endpoint-sample
npm install

# 创建 .env 文件
cat > .env << EOF
ZOOM_SDK_KEY=your_sdk_key_here
ZOOM_SDK_SECRET=your_sdk_secret_here
PORT=4000
EOF

npm start
```

**Token 端点**:
```javascript
// POST https://YOUR_TOKEN_SERVICE_BASE_URL
{
  "role": 1,           // 1 = 客户, 2 = 代理
  "userId": "user123",
  "userName": "John Doe"
}

// 响应
{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 第 3 步：客户端集成（CDN）

```html
<!DOCTYPE html>
<html>
<head>
  <title>客户 - Cobrowse 演示</title>
  <script type="module">
    const ZOOM_SDK_KEY = 'YOUR_SDK_KEY';
    
    // 从 CDN 加载 SDK
    (function(r,a,b,f,c,d) {
      r[f] = r[f] || { init: function() { r.ZoomCobrowseSDKInitArgs = arguments }};
      var fragment = a.createDocumentFragment();
      function loadJs(url) {
        c = a.createElement(b);
        d = a.getElementsByTagName(b)[0];
        c["async"] = false;
        c.src = url;
        fragment.appendChild(c);
      }
      loadJs(`https://us01-zcb.zoom.us/static/resource/sdk/${ZOOM_SDK_KEY}/js/2.13.2`);
      d.parentNode.insertBefore(fragment, d);
    })(window, document, "script", "ZoomCobrowseSDK");
  </script>
</head>
<body>
  <h1>客户支持</h1>
  <button id="cobrowse-btn" disabled>Loading...</button>
  
  <!-- 敏感字段 - 将从代理中遮盖 -->
  <label>SSN: <input type="text" class="pii-mask" placeholder="XXX-XX-XXXX"></label>
  <label>信用卡: <input type="text" class="pii-mask" placeholder="XXXX-XXXX-XXXX-XXXX"></label>
  
  <script type="module">
    let sessionRef = null;
    
    const settings = {
      allowAgentAnnotation: true,
      allowCustomerAnnotation: true,
      piiMask: {
        maskCssSelectors: ".pii-mask",
        maskType: "custom_input"
      }
    };
    
    ZoomCobrowseSDK.init(settings, function({ success, session, error }) {
      if (success) {
        sessionRef = session;
        
        // 监听 PIN 代码
        session.on("pincode_updated", (payload) => {
          console.log("PIN 代码:", payload.pincode);
          // 重要提示：这是代理应使用的 PIN
          alert(`与代理分享此 PIN: ${payload.pincode}`);
        });
        
        // 监听会话事件
        session.on("session_started", () => console.log("会话开始"));
        session.on("agent_joined", () => console.log("代理加入"));
        session.on("agent_left", () => console.log("代理离开"));
        session.on("session_ended", () => console.log("会话结束"));
        
        document.getElementById("cobrowse-btn").disabled = false;
        document.getElementById("cobrowse-btn").innerText = "开始 Cobrowse 会话";
      } else {
        console.error("SDK 初始化失败:", error);
      }
    });
    
    document.getElementById("cobrowse-btn").addEventListener("click", async () => {
      // 从您的服务器获取 JWT
      const response = await fetch("https://YOUR_TOKEN_SERVICE_BASE_URL", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: 1,
          userId: "customer_" + Date.now(),
          userName: "Customer"
        })
      });
      const { token } = await response.json();
      
      // 开始 Cobrowse 会话
      sessionRef.start({ sdkToken: token });
    });
  </script>
</body>
</html>
```

### 第 4 步：代理端集成（Iframe）

```html
<!DOCTYPE html>
<html>
<head>
  <title>代理门户</title>
</head>
<body>
  <h1>代理门户</h1>
  <iframe 
    id="agent-iframe"
    width="1024" 
    height="768"
    allow="autoplay *; camera *; microphone *; display-capture *; geolocation *;"
  ></iframe>
  
  <script>
    async function connectAgent() {
      // 从您的服务器获取 JWT
      const response = await fetch("https://YOUR_TOKEN_SERVICE_BASE_URL", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: 2,
          userId: "agent_" + Date.now(),
          userName: "Support Agent"
        })
      });
      const { token } = await response.json();
      
      // 加载 Zoom 代理门户
      const iframe = document.getElementById("agent-iframe");
      iframe.src = `https://us01-zcb.zoom.us/sdkapi/zcb/frame-templates/desk?access_token=${token}`;
    }
    
    connectAgent();
  </script>
</body>
</html>
```

### 第 5 步：测试集成

1. 打开 **两个独立的浏览器**（或隐身 + 正常）
2. **客户浏览器**：打开客户页面，点击“开始 Cobrowse 会话”
3. **客户浏览器**：记下显示的 6 位 PIN 代码
4. **代理浏览器**：输入客户的 PIN 代码
5. **两个浏览器**：会话连接，代理可以看到客户的页面
6. **测试功能**：标注工具、数据遮罩、远程协助

## 关键功能

### 1. 标注工具

客户和代理都可以在共享屏幕上绘制：

```javascript
const settings = {
  allowAgentAnnotation: true,      // 代理可以绘制
  allowCustomerAnnotation: true    // 客户可以绘制
};
```

**可用工具**:
- 笔（永久）
- 消失笔（4 秒后消失）
- 矩形
- 颜色选择器
- 橡皮擦
- 撤销/重做

### 2. 隐私遮罩

使用 CSS 选择器遮盖敏感字段：

```javascript
const settings = {
  piiMask: {
    maskType: "custom_input",           // 遮盖特定字段
    maskCssSelectors: ".pii-mask, #ssn", // CSS 选择器
    maskHTMLAttributes: "data-sensitive=true" // HTML 属性
  }
};
```

**支持的遮罩**:
- 文本节点 ✓
- 表单输入 ✓
- 选择元素 ✓
- 图片 ✗（不支持）
- 链接 ✗（不支持）

### 3. 远程协助

代理可以滚动客户的页面：

```javascript
const settings = {
  remoteAssist: {
    enable: true,
    enableCustomerConsent: true,        // 客户必须同意
    remoteAssistTypes: ['scroll_page'], // 仅支持滚动
    requireStopConfirmation: false      // 停止时无需确认
  }
};
```

### 4. 多标签会话持久化

客户打开新标签时会话继续：

```javascript
const settings = {
  multiTabSessionPersistence: {
    enable: true,
    stateCookieKey: '$$ZCB_SESSION$$'  // Cookie 键（base64 编码）
  }
};
```

## 会话生命周期

### 客户流程

1. **加载 SDK** → CDN 脚本加载 `ZoomCobrowseSDK`
2. **初始化** → `ZoomCobrowseSDK.init(settings, callback)`
3. **获取 JWT** → 从您的服务器请求令牌（role_type=1）
4. **开始会话** → `session.start({ sdkToken })`
5. **生成 PIN** → `pincode_updated` 事件触发
6. **分享 PIN** → 客户给 6 位 PIN 代码给代理
7. **代理加入** → `agent_joined` 事件触发
8. **会话激活** → 实时同步开始
9. **结束会话** → `session.end()` 或代理离开

### 代理流程

1. **获取 JWT** → 从您的服务器请求令牌（role_type=2）
2. **加载 Iframe** → 指向 Zoom 代理门户（iframe 或 npm）
3. **输入 PIN** → 代理输入客户的 6 位 PIN 代码
4. **连接** → `session_joined` 事件触发
5. **查看会话** → 代理可以看到客户的浏览器
6. **使用工具** → 标注工具、远程协助、缩放
7. **离开会话** → 点击“离开 Cobrowse”按钮

### 会话恢复（自动重连）

当客户刷新页面时：

```javascript
ZoomCobrowseSDK.init(settings, function({ success, session, error }) {
  if (success) {
    const sessionInfo = session.getSessionInfo();
    
    // 检查会话是否可恢复
    if (sessionInfo.sessionStatus === 'session_recoverable') {
      session.join();  // 自动重新加入以前的会话
    } else {
      // 开始新会话
      session.start({ sdkToken });
    }
  }
});
```

**恢复窗口**: 2 分钟。2 分钟后，会话结束。

## 关键陷阱和最佳实践

### ⚠️ 关键：SDK Secret 必须保留在服务器端

**问题**：开发人员经常不小心将 SDK Secret 嵌入前端代码。

**解决方案**:
- ✓ **SDK Key** → 安全暴露（嵌入 CDN URL）
- ✗ **SDK Secret** → 永远不要暴露（服务器端使用 JWT 签名）

```javascript
// ❌ 错误 - Secret 暴露在客户端
const jwt = signJWT(payload, 'YOUR_SDK_SECRET');  // 安全风险!

// ✅ 正确 - Secret 保留在服务器端
const response = await fetch('/api/token', {
  method: 'POST',
  body: JSON.stringify({ role: 1, userId, userName })
});
const { token } = await response.json();
```

### SDK Key 与 API Key（不同用途！）

| 凭证 | 用于 | JWT Claim |
|------------|----------|-----------|
| **SDK Key** | CDN URL, JWT `app_key` 声明 | `app_key: "SDK_KEY"` |
| **API Key** | REST API 调用（可选） | 不用于 JWT `app_key`

**常见错误**：在 JWT `app_key` 声明中使用 API Key 考虑使用 SDK Key。

### 会话限制

| 限制 | 值 | 发生什么 |
|-------|-------|--------------|
| 每个会话的客户数量 | 1 | 错误 1012: `SESSION_CUSTOMER_COUNT_LIMIT` |
| 每个会话的代理数量 | 5 | 错误 1013: `SESSION_AGENT_COUNT_LIMIT` |
| 每个浏览器的活动会话数量 | 1 | 错误 1004: `SESSION_COUNT_LIMIT` |
| PIN 代码长度 | 10 个字符最大 | 错误 1008: `SESSION_PIN_INVALID_FORMAT` |

### 会话超时行为

| 事件 | 超时 | 发生什么 |
|-------|---------|--------------|
| 代理等待客户 | 3 分钟 | 会话自动结束 |
| 页面刷新重连 | 2 分钟 | 如果未重新连接，会话结束 |
| 重连尝试次数 | 2 次最大 | 2 次失败后，会话结束 |

### HTTPS 要求

**问题**：SDK 在 HTTP 网站上无法加载。

**解决方案**:
- 生产：使用 HTTPS ✓
- 开发：使用回环主机进行本地 HTTP 测试 ✓
- 开发：如果需要，使用本地 HTTPS 端点并使用受信任的/自签名证书 ✓

### 第三方 Cookie 必须启用

**问题**：刷新重连不起作用。

**解决方案**：在浏览器设置中启用第三方 Cookie。

**受影响的场景**:
- 浏览器隐私模式
- Safari 的“阻止跨站点跟踪”启用
- Chrome 的“阻止第三方 Cookie”启用

### 分发方法混淆

| 方法 | 用例 | 代理集成 | BYOP 必须使用 |
|--------|----------|-------------------|---------------|
| **CDN** | 大多数用例 | Zoom 托管的 iframe | 不需要（自动 PIN） |
| **npm** | 自定义代理 UI、完全控制 | 自定义 npm 集成 | 是（必须） |

**关键洞察**：如果您想要 **npm** 集成，您 **必须** 使用 BYOP（自带 PIN）模式。

### 跨域 Iframe 处理

**问题**：Cobrowse 在跨域 Iframe 中不起作用。

**解决方案**：将 SDK 片段注入跨域 Iframe：

```html
<script>
const ZOOM_SDK_KEY = "YOUR_SDK_KEY_HERE";

(function(r,a,b,f,c,d){r[f]=r[f]||{init:function(){r.ZoomCobrowseSDKInitArgs=arguments}};
var fragment = a.createDocumentFragment();
function loadJs(url) {c=a.createElement(b);d=a.getElementsByTagName(b)[0];c["async"] = false;c.src = url;fragment.appendChild(c);
};
loadJs(`https://us01-zcb.zoom.us/static/resource/sdk/${ZOOM_SDK_KEY}/js`);d.parentNode.insertBefore(fragment,d);
</script>
```

**同源 Iframe**: 无需额外设置。

## 已知限制

### 同步限制

**不同步**:
- HTML5 Canvas 元素
- WebGL 内容
- 音频和视频元素
- Shadow DOM
- 使用 Canvas 渲染的 PDF
- Web Components

**部分同步**:
- 下拉框（仅同步选中结果）
- 日期选择器（仅同步选中结果）
- 颜色选择器（仅同步选中结果）

### 渲染限制

- 高分辨率图像可能会被压缩
- 不同的屏幕尺寸可能会导致 CSS 媒体查询差异
- 跨域图像可能无法渲染（CORS 限制）
- 跨域字体可能无法渲染（CORS 限制）

### 遮罩限制

**支持**:
- 文本节点 ✓
- 表单输入 ✓
- 选择元素 ✓

**不支持**:
- `<img>` 元素 ✗
- 链接 ✗

## 完整文档库

此技能包含按类别组织的综合指南：

### 核心概念
- **[两角色模式](concepts/two-roles-pattern.md)** - 客户与代理架构
- **[会话生命周期](concepts/session-lifecycle.md)** - 从开始到结束的完整流程
- **[JWT 认证](concepts/jwt-authentication.md)** - 令牌结构、签名、SDK Key 与 API Key、role_type、claims
- **[分发方法](concepts/distribution-methods.md)** - CDN 与 npm（BYOP）

### 示例
- **[客户集成](examples/customer-integration.md)** - 完整客户端设置
- **[代理集成](examples/agent-integration.md)** - iframe 和 npm 代理设置模式
- **[标注](examples/session-events.md)** - 处理所有会话生命周期事件
- **[自动重连](examples/auto-reconnection.md)** - 页面刷新时恢复会话

**功能**:
- **[标注](examples/annotations.md)** - 启用绘制、高亮、消失笔、矩形、颜色选择器
- **[隐私遮罩](examples/privacy-masking.md)** - 遮盖敏感字段
- **[远程协助](examples/remote-assist.md)** - 代理可以滚动客户的页面
- **[多标签持久化](examples/multi-tab-persistence.md)** - 会话跨标签继续
- **[BYOP 自定义 PIN](examples/byop-custom-pin.md)** - 使用 npm 集成带自己的 PIN

**参考**:
- **[API 参考](references/api-reference.md)** - 完整 SDK 方法和事件
- **[设置参考](references/settings-reference.md)** - 所有初始化设置
- **集成索引** - 查看本文件中的下一节

## 资源

- **官方文档**: https://developers.zoom.us/docs/cobrowse-sdk/
- **API 参考**: https://marketplacefront.zoom.us/sdk/cobrowse/
- **快速入门仓库**: https://github.com/zoom/CobrowseSDK-Quickstart
- **认证端点示例**: https://github.com/zoom/cobrowsesdk-auth-endpoint-sample
- **开发者论坛**: https://devforum.zoom.us/
- **开发者博客**: https://developers.zoom.us/blog/?category=zoom-cobrowse-sdk

---

**找不到您需要的内容？** 检查 [官方文档](https://developers.zoom.us/docs/cobrowse-sdk/) 或在 [开发者论坛](https://devforum.zoom.us/) 上提问。

## 环境变量

- 查看 [references/environment-variables.md](references/environment-variables.md) 以获取标准化的 `.env` 键和每个值的位置。
