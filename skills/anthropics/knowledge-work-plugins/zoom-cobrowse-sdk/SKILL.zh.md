---
name: zoom-cobrowse-sdk
description: Zoom Cobrowse SDK的参考技能。在实现浏览器协同浏览、标注工具、隐私遮罩、远程协助或基于PIN的会话共享时，在路由到协作支持工作流后使用。
---

# Zoom Cobrowse SDK - Web 开发

使用 Zoom Cobrowse SDK 进行网页协同浏览的背景参考。在支持工作流程明确后，需要实现细节时使用。

**官方文档**: https://developers.zoom.us/docs/cobrowse-sdk/  
**API 参考**: https://marketplacefront.zoom.us/sdk/cobrowse/  
**快速入门仓库**: https://github.com/zoom/CobrowseSDK-Quickstart  
**认证端点示例**: https://github.com/zoom/cobrowsesdk-auth-endpoint-sample

## 快速链接

**新接触 Cobrowse SDK？请遵循此路径：**

1. **[入门指南](get-started.md)** - 从凭证到首次会话的完整设置
2. **[会话生命周期](concepts/session-lifecycle.md)** - 理解客户和代理的流程
3. **[JWT 认证](concepts/jwt-authentication.md)** - 令牌生成和安全
4. **[客户集成](examples/customer-integration.md)** - 将 SDK 集成到您的网站
5. **[代理集成](examples/agent-integration.md)** - 设置代理门户（iframe 或 npm）

**核心概念：**
- **[双重角色模式](concepts/two-roles-pattern.md)** - 客户与代理的架构
- **[会话生命周期](concepts/session-lifecycle.md)** - PIN 生成、连接、重连
- **[JWT 认证](concepts/jwt-authentication.md)** - SDK Key 与 API Key、role_type、声明
- **[分发方法](concepts/distribution-methods.md)** - CDN 与 npm（BYOP）

**功能：**
- **[标注工具](examples/annotations.md)** - 绘制、高亮、指针工具
- **[隐私遮罩](examples/privacy-masking.md)** - 隐藏代理的敏感字段
- **[远程协助](examples/remote-assist.md)** - 代理可以滚动客户的页面
- **[多标签持久化](examples/multi-tab-persistence.md)** - 会话跨标签继续
- **[BYOP 模式](examples/byop-custom-pin.md)** - 使用 npm 集成自带 PIN

**故障排除：**
- **[常见问题](troubleshooting/common-issues.md)** - 快速诊断和解决方案
- **[错误代码](troubleshooting/error-codes.md)** - 完整错误参考
- **[CORS 和 CSP](troubleshooting/cors-csp.md)** - 跨域和安全策略配置
- **[浏览器兼容性](troubleshooting/browser-compatibility.md)** - 支持的浏览器和限制
- **[5 分钟运行手册](RUNBOOK.md)** - 深入调试前的快速预检

**参考：**
- **[API 参考](references/api-reference.md)** - 完整 SDK 方法和事件
- **[设置参考](references/settings-reference.md)** - 所有初始化设置
- **集成索引** - 查看本文件下方的部分

## SDK 概述

Zoom Cobrowse SDK 是一个 JavaScript 库，提供：

- **实时协同浏览**：代理实时查看客户的浏览器活动
- **基于 PIN 的会话**：客户到代理的连接使用安全的 6 位 PIN
- **标注工具**：绘制、高亮、消失笔、矩形、颜色选择器
- **隐私遮罩**：基于 CSS 选择器遮罩敏感表单字段
- **远程协助**：代理可以滚动客户的页面（需同意）
- **多标签持久化**：客户打开新标签时会话继续
- **自动重连**：页面刷新时恢复会话（2 分钟窗口期）
- **会话事件**：实时事件用于会话状态变化
- **HTTPS 必须使用**：安全连接（仅在回环/本地开发主机上工作 HTTP）
- **无需插件**：纯 JavaScript，无需浏览器扩展

## 双重角色架构

Cobrowse 有 **两种不同的角色**，每种都有不同的集成模式：

| 角色 | role_type | 集成 | JWT 必须使用 | 目的 |
|------|-----------|------|--------------|------|
| **客户** | 1 | 网站集成（CDN 或 npm） | 是 | 分享浏览器会话的用户 |
| **代理** | 2 | iframe（CDN）或 npm（仅限 BYOP） | 是 | 查看/协助客户的客服人员 |

**关键洞察**：客户和代理使用 **不同的集成方法**，但使用相同的 JWT 认证模式。

## 首次阅读（关键）

对于客户/代理演示，将客户 SDK 事件 `pincode_updated` 中的 PIN 视为唯一的面向用户的 PIN。

- 在 UI 中清晰地显示一个值（例如，**支持 PIN**）。
- 使用相同的 PIN 进行代理加入。
- 不要向用户暴露后端预启动记录中的临时/调试 PIN。

如果忽略这些规则，代理工作站通常会失败，显示 `Pincode is not found` / 代码 `30308`。

### 典型生产流程（最常见）

这是大多数团队首先实现的流程，也是用户通常在演示中期望的流程：

1. **客户首先启动会话** (`role_type=1`)
   - 后端创建/记录会话
   - 后端返回客户 JWT
   - 客户 SDK 启动并接收一个 PIN
2. **代理其次加入** (`role_type=2`)
   - 代理输入客户的 PIN
   - 后端验证 PIN 和会话状态
   - 后端返回代理 JWT
   - 代理打开 Zoom 托管的桌面 iframe（或 BYOP 中的自定义 npm 代理 UI）

如果演示只有一个通用的“会话”用户，则对于真实的 Cobrowse 操作是不完整的。

## 前置条件

### 平台要求

- **支持的浏览器**:
  - Chrome 80+ ✓
  - Firefox 78+ ✓
  - Safari 14+ ✓
  - Edge 80+ ✓
  - Internet Explorer ✗（不支持）

- **网络要求**:
  - HTTPS 必须使用（仅在回环/本地开发主机上 HTTP 有效）
  - 允许跨域请求到 `*.zoom.us`
  - CSP 头必须允许 Zoom 域名（参见 [CORS 和 CSP 指南](troubleshooting/cors-csp.md)）

- **第三方 Cookie**:
  - 必须启用第三方 Cookie 以便刷新重连
  - 隐私模式可能会限制某些功能

### Zoom 账户要求

1. **Zoom Workplace 账户**，带有 SDK 通用积分
2. **Video SDK 应用** 在 Zoom Marketplace 中创建
3. **Cobrowse SDK 凭证** 从应用的 Cobrowse 选项卡获取

**注意**：Cobrowse SDK 是 **Video SDK 的功能**（不是独立产品）。

### 凭证概述

您将从 Zoom Marketplace → Video SDK 应用 → Cobrowse 选项卡收到 **4 个凭证**：

| 凭证 | 类型 | 用于 | 是否安全暴露 |
|------|------|------|--------------|
| **SDK Key** | 公开 | CDN URL、JWT `app_key` 声明 | ✓ 是（客户端） |
| **SDK Secret** | 私有 | 签名 JWT | ✗ 否（仅服务器端） |
| **API Key** | 私有 | REST API 调用（可选） | ✗ 否（仅服务器端） |
| **API Secret** | 私有 | REST API 调用（可选） | ✗ 否（仅服务器端） |

**关键**：SDK Key 是 **公开的**（嵌入 CDN URL），但 SDK Secret 必须 **永不** 在客户端暴露。

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

### 第 2 步：设置令牌服务器

部署一个服务器端端点来生成 JWT。使用官方示例：

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

**令牌端点**：
```javascript
// POST https://YOUR_TOKEN_SERVICE_BASE_URL
{
  "role": 1,           // 1 = 客户，2 = 代理
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
    (function(r, a, b, f, c, d) {
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
  
  <!-- 敏感字段 - 将被代理遮罩 -->
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
          alert(`与代理分享此 PIN：${payload.pincode}`);
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
          userName: "客户"
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
          userName: "支持代理"
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

1. 打开 **两个独立的浏览器**（或隐身模式+正常模式）
2. **客户浏览器**：打开客户页面，点击“开始 Cobrowse 会话”
3. **客户浏览器**：记下显示的 6 位 PIN 代码
4. **代理浏览器**：输入客户的 6 位 PIN 代码
5. **两个浏览器**：会话连接，代理可以看到客户的浏览器
6. **测试功能**：标注、数据遮罩、远程协助

## 关键功能

### 1. 标注工具

客户和代理都可以在共享屏幕上绘制：

```javascript
const settings = {
  allowAgentAnnotation: true,      // 代理可以绘制
  allowCustomerAnnotation: true    // 客户可以绘制
};
```

**可用工具**：
- 钢笔（永久）
- 消失笔（4 秒后消失）
- 矩形
- 颜色选择器
- 橡皮擦
- 撤销/重做

### 2. 隐私遮罩

使用 CSS 选择器隐藏敏感字段：

```javascript
const settings = {
  piiMask: {
    maskType: "custom_input",           // 遮罩特定字段
    maskCssSelectors: ".pii-mask, #ssn", // CSS 选择器
    maskHTMLAttributes: "data-sensitive=true" // HTML 属性
  }
};
```

**支持的遮罩**：
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
3. **获取 JWT** → 从您的服务器请求 token（role_type=1）
4. **启动会话** → `session.start({ sdkToken })`
5. **生成 PIN** → `pincode_updated` 事件触发
6. **分享 PIN** → 客户给代理 6 位 PIN
7. **代理加入** → `agent_joined` 事件触发
8. **会话激活** → 实时同步开始
9. **结束会话** → `session.end()` 或代理离开

### 代理流程

1. **获取 JWT** → 从您的服务器请求 token（role_type=2）
2. **加载 Iframe** → 指向带有 token 的 Zoom 代理门户
3. **输入 PIN** → 代理输入客户的 6 位 PIN
4. **连接** → `session_joined` 事件触发
5. **查看会话** → 代理看到客户的浏览器
6. **使用工具** → 标注、远程协助、缩放
7. **离开会话** → 点击“离开 Cobrowse”按钮

### 会话恢复（自动重连）

当客户刷新页面时：

```javascript
ZoomCobrowseSDK.init(settings, function({ success, session, error }) {
  if (success) {
    const sessionInfo = session.getSessionInfo();
    
    // 检查是否可以恢复会话
    if (sessionInfo.sessionStatus === 'session_recoverable') {
      session.join();  // 自动重连到之前的会话
    } else {
      // 启动新会话
      session.start({ sdkToken });
    }
  }
});
```

**恢复窗口**：2 分钟。超过 2 分钟后，会话结束。

## 关键陷阱和最佳实践

### ⚠️ 关键：SDK Secret 必须保持服务器端

**问题**：开发人员经常在客户端代码中意外嵌入 SDK Secret。

**解决方案**：
- ✓ **SDK Key** → 安全暴露（嵌入 CDN URL）
- ✗ **SDK Secret** → 永不暴露（用于服务器端 JWT 签名）

```javascript
// ❌ 错误 - Secret 在客户端暴露
const jwt = signJWT(payload, 'YOUR_SDK_SECRET');  // 安全风险！

// ✅ 正确 - Secret 保持服务器端
const response = await fetch('/api/token', {
  method: 'POST',
  body: JSON.stringify({ role: 1, userId, userName })
});
const { token } = await response.json();
```

### SDK Key 与 API Key（不同用途！）

| 凭证 | 用于 | JWT 声明 |
|------|------|----------|
| **SDK Key** | CDN URL、JWT `app_key` | `app_key: "SDK_KEY"` |
| **API Key** | REST API 调用（可选） | 不在 JWT 中使用 |

**常见错误**：在 JWT `app_key` 声明中使用 API Key 而不是 SDK Key。

### 会话限制

| 限制 | 值 | 发生什么事 |
|-------|-------|--------------|
| 每次会话的客户数 | 1 | 错误 1012: `SESSION_CUSTOMER_COUNT_LIMIT` |
| 每次会话的代理数 | 5 | 错误 1013: `SESSION_AGENT_COUNT_LIMIT` |
| 每个浏览器中的活动会话数 | 1 | 错误 1004: `SESSION_COUNT_LIMIT` |
| PIN码长度 | 最大10个字符 | 错误 1008: `SESSION_PIN_INVALID_FORMAT` |

### 会话超时行为

| 事件 | 超时时间 | 发生什么事 |
|-------|---------|--------------|
| 代理等待客户 | 3分钟 | 会话自动结束 |
| 页面刷新重新连接 | 2分钟 | 如果未重新连接，会话结束 |
| 重新连接尝试次数 | 最多2次 | 2次失败的尝试后，会话结束 |

### HTTPS要求

**问题**： SDK在HTTP网站上无法加载。

**解决方案**：
- 生产环境：使用HTTPS ✓
- 开发环境：使用本地HTTP测试的回环主机 ✓
- 开发环境：如果需要，使用本地HTTPS端点和一个受信任/自签名证书 ✓

### 第三方Cookie需要

**问题**： 刷新重新连接不起作用。

**解决方案**： 在浏览器设置中启用第三方Cookie。

**受影响的场景**：
- 浏览器隐私模式
- 启用了“阻止跨站跟踪”的Safari
- 启用了“阻止第三方Cookie”的Chrome

### 分发方式混淆

| 方法 | 用例 | 代理集成 | 需要BYOP |
|--------|----------|-------------------|---------------|
| **CDN** | 大多数用例 | Zoom托管的iframe | 否 (自动PIN) |
| **npm** | 自定义代理UI，完全控制 | 自定义npm集成 | 是 (需要) |

**关键洞察**： 如果您想要**npm**集成，您**必须**使用BYOP（自带PIN）模式。

### 跨域iframe处理

**问题**： 在跨域iframe中Cobrowse无法工作。

**解决方案**： 将SDK片段注入跨域iframe中：

```html
<script>
const ZOOM_SDK_KEY = "YOUR_SDK_KEY_HERE";

(function(r,a,b,f,c,d){r[f]=r[f]||{init:function(){r.ZoomCobrowseSDKInitArgs=arguments}};
var fragment=a.createDocumentFragment();function loadJs(url) {c=a.createElement(b);d=a.getElementsByTagName(b)[0];c.async=false;c.src=url;fragment.appendChild(c);};
loadJs('https://us01-zcb.zoom.us/static/resource/sdk/${ZOOM_SDK_KEY}/js');d.parentNode.insertBefore(fragment,d);})(window,document,'script','ZoomCobrowseSDK');
</script>
```

**同源iframe**： 无需额外设置。

## 已知限制

### 同步限制

**不同步**：
- HTML5 Canvas元素
- WebGL内容
- 音频和视频元素
- Shadow DOM
- 使用Canvas渲染的PDF
- Web组件

**部分同步**：
- 下拉框（仅选中结果）
- 日期选择器（仅选中结果）
- 颜色选择器（仅选中结果）

### 渲染限制

- 高分辨率图像可能会被压缩
- 不同的屏幕尺寸可能导致CSS媒体查询差异
- 跨域图像可能无法渲染（CORS限制）
- 跨域字体可能无法渲染（CORS限制）

### 掩码限制

**支持**：
- 文本节点 ✓
- 表单输入 ✓
- 选择元素 ✓

**不支持**：
- `<img>`元素 ✗
- 链接 ✗

## 完整文档库

此技能包含按类别组织的综合指南：

### 核心概念
- **[双角色模式](concepts/two-roles-pattern.md)** - 客户与代理架构
- **[会话生命周期](concepts/session-lifecycle.md)** - 从开始到结束的完整流程
- **[JWT认证](concepts/jwt-authentication.md)** - 令牌结构和签名
- **[分发方法](concepts/distribution-methods.md)** - CDN与npm（BYOP）

### 示例
- **[客户集成](examples/customer-integration.md)** - 完整的客户端设置
- **[代理集成](examples/agent-integration.md)** - iframe和npm代理设置
- **[注释](examples/annotations.md)** - 绘图工具配置
- **[隐私掩码](examples/privacy-masking.md)** - 字段掩码模式
- **[远程协助](examples/remote-assist.md)** - 代理页面控制
- **[多标签持久化](examples/multi-tab-persistence.md)** - 跨标签会话
- **[BYOP自定义PIN](examples/byop-custom-pin.md)** - 自定义PIN码

### 参考
- **[API参考](references/api-reference.md)** - 完整SDK方法和事件
- **[设置参考](references/settings-reference.md)** - 所有初始化设置
- **[错误代码](references/error-codes.md)** - 完整错误参考
- **[会话事件](references/session-events.md)** - 所有事件类型

### 故障排除
- **[常见问题](troubleshooting/common-issues.md)** - 快速诊断
- **[错误代码](troubleshooting/error-codes.md)** - 错误代码参考
- **[CORS和CSP](troubleshooting/cors-csp.md)** - 跨域配置
- **[浏览器兼容性](troubleshooting/browser-compatibility.md)** - 浏览器支持

## 资源

- **官方文档**： https://developers.zoom.us/docs/cobrowse-sdk/
- **API参考**： https://marketplacefront.zoom.us/sdk/cobrowse/
- **快速入门仓库**： https://github.com/zoom/CobrowseSDK-Quickstart
- **认证端点示例**： https://github.com/zoom/cobrowsesdk-auth-endpoint-sample
- **开发者论坛**： https://devforum.zoom.us/
- **开发者博客**： https://developers.zoom.us/blog/?category=zoom-cobrowse-sdk

---

**需要帮助？** 从下面的集成索引部分开始，以获得完整导航。

---

## 集成索引

本节是从`SKILL.md`迁移过来的。

**所有Cobrowse SDK文档的完整导航指南。**

## 入门指南（从这里开始！）

如果您是Zoom Cobrowse SDK的新手，请按照此学习路径进行：

1. **[SKILL.md](SKILL.md)** - 主要概述和快速入门
2. **[5分钟运行手册](RUNBOOK.md)** - 常见失败的预飞行检查
3. **[入门指南](get-started.md)** - 从凭证到第一个会话的逐步设置
4. **[会话生命周期](concepts/session-lifecycle.md)** - 了解完整的客户和代理流程
5. **[客户集成](examples/customer-integration.md)** - 将SDK集成到您的网站
6. **[代理集成](examples/agent-integration.md)** - 设置代理门户

## 核心概念

您需要了解的基础概念：

- **[双角色模式](concepts/two-roles-pattern.md)** - 客户（role_type=1）与代理（role_type=2）架构
- **[会话生命周期](concepts/session-lifecycle.md)** - 完整流程：初始化→开始→PIN→连接→结束
- **[JWT认证](concepts/jwt-authentication.md)** - 令牌结构、签名、SDK Key与API Key
- **[分发方法](concepts/distribution-methods.md)** - CDN与npm（BYOP模式）

## 示例和模式

常见场景的完整工作示例：

### 会话管理
- **[客户集成](examples/customer-integration.md)** - 完整的客户端实现（CDN和npm）
- **[代理集成](examples/agent-integration.md)** - iframe和npm代理设置模式
- **[会话事件](examples/session-events.md)** - 处理所有会话生命周期事件
- **[自动重新连接](examples/auto-reconnection.md)** - 页面刷新和会话恢复

### 功能
- **[注释工具](examples/annotations.md)** - 启用绘图、高亮显示、消失笔
- **[隐私掩码](examples/privacy-masking.md)** - 使用CSS选择器掩码敏感字段
- **[远程协助](examples/remote-assist.md)** - 代理可以滚动客户的页面
- **[多标签持久化](examples/multi-tab-persistence.md)** - 会话在浏览器标签之间继续
- **[BYOP自定义PIN](examples/byop-custom-pin.md)** - 带npm集成的自带PIN

## 参考

完整的API和配置参考：

### SDK参考
- **[API参考](references/api-reference.md)** - 所有SDK方法和接口
  - ZoomCobrowseSDK.init()
  - session.start()
  - session.join()
  - session.end()
  - session.on()
  - session.getSessionInfo()

- **[设置参考](references/settings-reference.md)** - 所有初始化设置
  - allowAgentAnnotation
  - allowCustomerAnnotation
  - piiMask
  - remoteAssist
  - multiTabSessionPersistence

- **[会话事件参考](references/session-events.md)** - 所有事件类型
  - pincode_updated
  - session_started
  - session_ended
  - agent_joined
  - agent_left
  - session_error
  - session_reconnecting
  - remote_assist_started
  - remote_assist_stopped

### 错误参考
- **[错误代码](references/error-codes.md)** - 完整错误代码参考
  - 1001-1017：会话错误
  - 2001：令牌错误
  - 9999：服务错误

### 官方文档
- **[入门](references/get-started.md)** - 官方入门文档（爬取）
- **[功能](references/features.md)** - 官方功能文档（爬取）
- **[授权](references/authorization.md)** - 官方JWT授权文档（爬取）
- **[API文档](references/api.md)** - 爬取的API参考文档

## 故障排除

快速诊断和常见问题解决：

- **[常见问题](troubleshooting/common-issues.md)** - 频繁问题的快速修复
  - SDK未加载
  - 令牌生成失败
  - 代理无法连接
  - 字段未掩码
  - 刷新后会话不重新连接

- **[错误代码](troubleshooting/error-codes.md)** - 错误代码查找和解决方案
  - 会话启动/加入失败 (1001, 1011, 1016)
  - 会话限制错误 (1002, 1004, 1012, 1013, 1015)
  - PIN码错误 (1006, 1008, 1009, 1010)
  - 令牌错误 (2001)

- **[CORS和CSP](troubleshooting/cors-csp.md)** - 跨域和内容安全策略设置
  - Access-Control-Allow-Origin标头
  - Content-Security-Policy标头
  - 跨域iframe处理
  - 同源iframe处理

- **[浏览器兼容性](troubleshooting/browser-compatibility.md)** - 浏览器要求和限制
  - 支持的浏览器 (Chrome 80+，Firefox 78+，Safari 14+，Edge 80+)
  - 不支持Internet Explorer
  - 隐私模式限制
  - 第三方Cookie要求

## 按用例划分

根据您试图做什么查找文档：

### 我想...

**首次设置cobrowse**：
- [入门指南](get-started.md)
- [JWT认证](concepts/jwt-authentication.md)
- [客户集成](examples/customer-integration.md)
- [代理集成](examples/agent-integration.md)

**添加注释工具**：
- [注释工具示例](examples/annotations.md)
- [设置参考 - allowAgentAnnotation](references/settings-reference.md#allowa gentannotation)
- [设置参考 - allowCustomerAnnotation](references/settings-reference.md#allowcustomerannotation)

**向代理隐藏敏感数据**：
- [隐私掩码示例](examples/privacy-masking.md)
- [设置参考 - piiMask](references/settings-reference.md#piimask)

**让代理控制客户的页面**：
- [远程协助示例](examples/remote-assist.md)
- [设置参考 - remoteAssist](references/settings-reference.md#remoteassist)

**使用自定义PIN码**：
- [BYOP自定义PIN示例](examples/byop-custom-pin.md)
- [JWT认证 - enable_byop](concepts/jwt-authentication.md#enable-byop)

**处理页面刷新**：
- [自动重新连接示例](examples/auto-reconnection.md)
- [会话生命周期 - 恢复](concepts/session-lifecycle.md#session-recovery)

**集成npm（非CDN）**：
- [BYOP自定义PIN示例](examples/byop-custom-pin.md)
- [分发方法](concepts/distribution-methods.md#npm-integration)

**调试会话连接问题**：
- [常见问题](troubleshooting/common-issues.md)
- [错误代码](troubleshooting/error-codes.md)
- [会话事件 - session_error](examples/session-events.md#session-error)

**配置CORS和CSP标头**：
- [CORS和CSP指南](troubleshooting/cors-csp.md)
- [浏览器兼容性](troubleshooting/browser-compatibility.md)

## 按错误代码划分

快速查找错误代码解决方案：

### 会话错误
- **1001** (SESSION_START_FAILED) → [错误代码](troubleshooting/error-codes.md#1001-session-start-failed)
- **1002** (SESSION_CONNECTING_IN_PROGRESS) → [错误代码](troubleshooting/error-codes.md#1002-session-connecting-in-progress)
- **1004** (SESSION_COUNT_LIMIT) → [错误代码](troubleshooting/error-codes.md#1004-session-count-limit)
- **1011** (SESSION_JOIN_FAILED) → [错误代码](troubleshooting/error-codes.md#1011-session-join-failed)
- **1012** (SESSION_CUSTOMER_COUNT_LIMIT) → [错误代码](troubleshooting/error-codes.md#1012-session-customer-count-limit)
- **1013** (SESSION_AGENT_COUNT_LIMIT) → [错误代码](troubleshooting/error-codes.md#1013-session-agent-count-limit)
- **1015** (SESSION_DUPLICATE_USER) → [错误代码](troubleshooting/error-codes.md#1015-session-duplicate-user)
- **1016** (NETWORK_ERROR) → [错误代码](troubleshooting/error-codes.md#1016-network-error)
- **1017** (SESSION_CANCELING_IN_PROGRESS) → [错误代码](troubleshooting/error-codes.md#1017-session-canceling-in-progress)

### PIN错误
- **1006** (SESSION_JOIN_PIN_NOT_FOUND) → [错误代码](troubleshooting/error-codes.md#1006-session-join-pin-not-found)
- **1008** (SESSION_PIN_INVALID_FORMAT) → [错误代码](troubleshooting/error-codes.md#1008-session-pin-invalid-format)
- **1009** (SESSION_START_PIN_REQUIRED) → [错误代码](troubleshooting/error-codes.md#1009-session-start-pin-required)
- **1010** (SESSION_START_PIN_CONFLICT) → [错误代码](troubleshooting/error-codes.md#1010-session-start-pin-conflict)

### 认证错误
- **2001** (TOKEN_INVALID) → [错误代码](troubleshooting/error-codes.md#2001-token-invalid)

### 服务错误
- **9999** (UNDEFINED) → [错误代码](troubleshooting/error-codes.md#9999-undefined)

## 官方资源

外部文档和示例：

- **官方文档**： https://developers.zoom.us/docs/cobrowse-sdk/
- **API参考**： https://marketplacefront.zoom.us/sdk/cobrowse/
- **快速入门仓库**： https://github.com/zoom/CobrowseSDK-Quickstart
- **认证端点示例**： https://github.com/zoom/cobrowsesdk-auth-endpoint-sample
- **开发者论坛**： https://devforum.zoom.us/
- **开发者博客**： https://developers.zoom.us/blog/?category=zoom-cobrowse-sdk

## 文档结构

```
cobrowse-sdk/
├── SKILL.md                    # 主技能入口
├── SKILL.md                    # 此文件 - 完整导航
├── get-started.md              # 步骤式设置指南
│
├── concepts/                   # 核心概念
│   ├── two-roles-pattern.md
│   ├── session-lifecycle.md
│   ├── jwt-authentication.md
│   └── distribution-methods.md
│
├── examples/                   # 工作示例
│   ├── customer-integration.md
│   ├── agent-integration.md
│   ├── annotations.md
│   ├── privacy-masking.md
│   ├── remote-assist.md
│   ├── multi-tab-persistence.md
│   ├── byop-custom-pin.md
│   ├── session-events.md
│   └── auto-reconnection.md
│
├── references/                 # API和配置参考
│   ├── api-reference.md        # SDK方法
│   ├── settings-reference.md   # 初始化设置
│   ├── session-events.md       # 事件类型
│   ├── error-codes.md          # 错误参考
│   ├── get-started.md          # 官方文档（爬取）
│   ├── features.md             # 官方文档（爬取）
│   ├── authorization.md        # 官方文档（爬取）
│   └── api.md                  # API文档（爬取）
│
└── troubleshooting/            # 问题解决
    ├── common-issues.md
    ├── error-codes.md
    ├── cors-csp.md
    └── browser-compatibility.md
```

## 搜索提示

**通过关键词查找：**
- "annotation" → [Annotation Tools](examples/annotations.md)
- "mask" 或 "privacy" → [Privacy Masking](examples/privacy-masking.md)
- "PIN" 或 "custom PIN" → [BYOP Custom PIN](examples/byop-custom-pin.md)
- "JWT" 或 "token" → [JWT Authentication](concepts/jwt-authentication.md)
- "error" → [Error Codes](troubleshooting/error-codes.md)
- "CORS" 或 "CSP" → [CORS and CSP](troubleshooting/cors-csp.md)
- "iframe" → [Agent Integration](examples/agent-integration.md)
- "npm" → [Distribution Methods](concepts/distribution-methods.md), [BYOP](examples/byop-custom-pin.md)
- "refresh" 或 "reconnect" → [Auto-Reconnection](examples/auto-reconnection.md)
- "agent" → [Agent Integration](examples/agent-integration.md), [Two Roles Pattern](concepts/two-roles-pattern.md)
- "customer" → [Customer Integration](examples/customer-integration.md), [Two Roles Pattern](concepts/two-roles-pattern.md)

---

**没有找到你需要的内容？** 请查看 [官方文档](https://developers.zoom.us/docs/cobrowse-sdk/) 或在 [开发者论坛](https://devforum.zoom.us/) 上提问。

## 环境变量

- 查看 [references/environment-variables.md](references/environment-variables.md) 了解标准化的 `.env` 键及其值来源。
