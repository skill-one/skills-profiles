# Netlify 表单

在 `<form>` 标签上使用 `data-netlify="true"`（或简化的 `netlify` 属性——等效）来标记表单以进行检测。表单通过在部署时**解析最终构建的 HTML**来检测——没有运行时 API 调用或后端代码。客户端/JS 渲染/SSR 表单不在构建的 HTML 中，并且不会自行检测；它们需要一个静态骨架文件（见下文）。

前提条件：必须在 Netlify 界面中启用表单检测一次（表单 > **启用表单检测**）。将在下一次部署时生效。

## 静态 HTML 表单

```html
<form name="contact" method="POST" data-netlify="true">
  <p><label>您的姓名: <input type="text" name="name" /></label></p>
  <p><label>您的邮箱: <input type="email" name="email" /></label></p>
  <p><label>消息: <textarea name="message"></textarea></label></p>
  <p><button type="submit">发送</button></p>
</form>
```

- `name` 设置 UI 中的表单名称，并且**每个站点必须唯一**。
- 在部署时，Netlify 会移除 `data-netlify`/`netlify` 属性并注入 `<input type="hidden" name="form-name" value="contact" />`。
- 添加一个 `<input name="email">`，以便通知邮件的 `Reply-to` 设置为提交者。

## JS 渲染 / SSR / 框架表单（Next.js, Nuxt, SvelteKit, Astro, Gatsby）

两个必需部分：

**1. 静态骨架文件 `public/__forms.html`**——每个表单的隐藏副本，带有 `data-netlify="true"`、隐藏的 `form-name` 输入以及组件提交的每个字段，名称必须**完全匹配**（Netlify 会验证字段名称与注册的表单）。没有这个文件，提交会静默失败。

```html
<!-- public/__forms.html -->
<form name="pizzaOrder" data-netlify="true" hidden>
  <input type="hidden" name="form-name" value="pizzaOrder" />
  <input name="order" type="text" />
</form>
```

**2. 渲染的表单**带有匹配的隐藏 `form-name` 输入：

```jsx
<form name="pizzaOrder" method="post" data-netlify="true" onSubmit={handleSubmit}>
  <input type="hidden" name="form-name" value="pizzaOrder" />
  <input name="order" type="text" onChange={handleChange} />
  <input type="submit" />
</form>
```

**⚠️ SSR POST 目标**：在 SSR 应用中，`fetch("/")` 被 SSR 捕获函数拦截，并且永远不会到达表单处理。POST 到静态骨架文件本身——`/__forms.html`——而不是 `/` 或任意路径。

**⚠️ Astro 按需路由**：带有 `export const prerender = false` 或 `output: "server"` 路由在构建时永远不会被扫描，因此它们的表单永远不会被注册。将表单放在预渲染页面上，或依赖静态骨架文件。

**Next.js 运行时 v5 (Next.js 13.5+)**：将表单定义提取到静态骨架文件中，并通过 AJAX 提交而不是全页导航。见 https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview#v5-breaking-changes

## AJAX 提交

```js
const handleSubmit = event => {
  event.preventDefault();
  const formData = new FormData(event.target);
  fetch("/__forms.html", {   // 静态站点可以 POST 到 "/"；SSR 必须目标骨架文件
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams(formData).toString()
  })
    .then(() => alert("感谢您的提交"))  // 或导航到 "/thank-you"
    .catch(error => alert(error));
};
document.querySelector("form").addEventListener("submit", handleSubmit);
```

- **正文必须 URL 编码。不支持 JSON。**
- 如果渲染的表单没有隐藏的 `form-name` 输入，您必须在 POST 正文包含 `form-name` 字段。
- 蜜罐字段名称和 `g-recaptcha-response`（如果使用）必须在正文——使用 `FormData()` 会自动包含。

## 文件上传

添加 `type="file"`；可选地 `<form>` 上添加 `enctype="multipart/form-data"`。对于 AJAX 文件上传，**不要设置 `Content-Type` 头**——让浏览器设置（带有多部分边界）。

```js
document.forms.fileForm.addEventListener("submit", event => {
  event.preventDefault();
  fetch("/", { body: new FormData(event.target), method: "POST" })  // 无需头信息
    .then(() => { /* 成功 */ });
});
```

限制：每个字段一个文件（使用多个字段上传多个文件）· 最大请求大小 8 MB · 上传超时 30 s · 表单删除后，上传的文件在其直接 URL 下保留 24 小时。PII 上传需要额外安全（非常良好安全集成）。

## 自定义成功页面

添加相对于站点根的 `action` 路径，以 `/` 开头。**使用无扩展名的路径**——Netlify 在 `/thank-you` 下提供 `thank-you.html`；`.html` 路径返回 404。

```html
<form name="contact" action="/thank-you" method="POST" data-netlify="true"></form>
```

自定义成功*提示*只能通过 AJAX 实现（用您自己的逻辑替换重定向）。

## 防止垃圾邮件

所有提交都由 Akismet 过滤。通过 → **验证提交**；标记 → **垃圾邮件提交**。蜜罐/reCAPTCHA 失败会被拒绝，并且不会出现在任何列表中。

**蜜罐**：将 `netlify-honeypot="bot-field"` 添加到 `<form>`，并包含一个该名称的 CSS 隐藏字段。任何值输入 → 提交被静默拒绝。

```html
<form name="contact" method="POST" netlify-honeypot="bot-field" data-netlify="true">
  <p class="hidden"><label>不要填写这个： <input name="bot-field" /></label></p>
  <!-- 真实字段 -->
</form>
```

**Netlify reCAPTCHA 2**：将 `data-netlify-recaptcha="true"` 添加到 `<form>`，并在渲染的位置添加一个空的 `<div data-netlify-recaptcha="true"></div>`。每个页面只能有一个 Netlify 提供的挑战——多个使用自定义 reCAPTCHA。对于 JS 渲染的表单，也将在静态骨架文件中添加 `div`。

**自定义 reCAPTCHA 2**：您自己的 reCAPTCHA 代码片段 + `<form>` 上的 `data-netlify-recaptcha="true"`，加上环境变量：
- `SITE_RECAPTCHA_KEY` — 站点密钥（范围：构建 + 运行时）
- `SITE_RECAPTCHA_SECRET` — 密钥（范围：运行时）

## 邮件通知和主题行

默认发送者：`formresponses@netlify.com`。通过隐藏的 `subject` 输入设置主题**或**在 Netlify 界面中设置（表单 > 提交通知）——**不能同时使用；HTML 值始终覆盖界面设置。**

```html
<input type="hidden" name="subject" value="来自 %{formName} (%{submissionId}) 的新线索" />
```

变量：`%{formName}`、`%{siteName}`、`%{submissionId}`。在 **2023 年 5 月 5 日**之前创建的表单带有 `[Netlify]` 主题前缀——通过在 `subject` 输入中添加 `data-remove-prefix` 属性来移除它。

在界面中设置通知（邮件/ webhook/Slack）：表单 > 提交通知 > **添加通知**。

## 通过 API 读取提交

仅使用文档化接口。**不要**使用 `api.netlify.com` 端点或从本地 CLI 配置文件中读取令牌。参考：https://open-api.netlify.com/#tag/submission/operation/listFormSubmissions

- **使用 `Link` 头分页结果**——只读取第一个响应的代码会静默丢弃其余响应。
- `listFormSubmissions` 返回旧/已移除字段的数据，这些字段不再在 UI 中显示。
- 查询垃圾邮件使用 `?state=spam`。

## 提交摘要（字段顺序很重要）

UI 摘要基于字段**类型**而不是名称：
- **标题**：第一个非隐藏的文本 `<input>`，不是电子邮件样式（`type="email"`，或名称匹配 `email`/`mail`/`from`/`twitter`/`sender`）；回退到名为 `title` 或 `subject` 的字段。
- **正文**：第一个 `<textarea>`。

HTML 中的字段顺序会影响摘要中显示的内容。

## 调试缺失提交

- **首要怀疑对象：Akismet 假阳性。** 缺失的合法提交通常是垃圾邮件标记——检查 **垃圾邮件** 列表（或 API `?state=spam`）并标记为验证。**不要**首先构建自定义恢复函数或禁用垃圾邮件过滤。
- 测试提交被标记为垃圾邮件：使用真实邮箱（不是 `test@test.com`），写完整句子，不要从单个 IP 持续攻击。
- 完全没有提交：确认表单检测已启用（表单 > 表单检测）并重新部署。
- SSR/JS 表单静默失败：验证静态骨架文件存在且字段名称完全匹配，并确保 AJAX 目标是骨架文件，而不是 `/`。
- 缺失旧字段数据：UI 仅显示最后一个部署的表单版本中的字段。将旧字段标记为 `hidden` 而不是删除它们以保持可见；旧数据可通过 `listFormSubmissions` 保持可用。

## 限制

- 删除表单是永久性的：未来的提交返回 `404`，过去的提交将不可用。先导出 CSV。
- 提交的代码会被清理（`<script>` → 转义实体）。
- 对于 PII，定期导出和删除数据。
- 数据存储在 Netlify 的数据库中，只能通过 UI/API/CSV 访问。

<!-- 表单使用现在在表单 > 使用；表单检测在表单 > 表单检测——UI 路径根据 manifest 提交 a28cd46 更新。 -->

<!-- system: agent-context/forms/system.md — 人类拥有，由 ctx-gen 合并；编辑 system.md，不要编辑此部分 -->
# Netlify 房间规则（表单）

这些是组织约定和经验学习的护栏，不是文档事实——它们被合并到渲染的技能中并由 ctx-gen 处理，并且永远不会生成。
从之前手写的 netlify-forms 技能中提取；由技能维护者拥有。

1. 在 SSR 应用中（Next.js, Nuxt, SvelteKit 等），`fetch("/")` 被SSR 捕获函数拦截，永远不会到达 Netlify 的表单处理。
   将 AJAX 提交到静态骨架文件本身（例如 `/__forms.html`），而不是任意路径。
2. 仅使用文档化接口：不要用发明的端点形状 curl `https://api.netlify.com/...`，也不要从本地 CLI 配置文件中读取令牌（`~/Library/Preferences/netlify/config.json`）。
3. 通过 API 读取提交时，使用 `Link` 头分页结果；只读取第一个响应的代码会静默丢弃其余响应。
4. 对于 JS 渲染和 SSR 表单，始终创建静态骨架文件 `public/__forms.html`：每个表单的隐藏副本，带有 `data-netlify="true"`、隐藏的 `form-name` 输入以及组件提交的每个字段——名称完全匹配（Netlify 会验证字段名称与注册的表单）。没有这个文件，提交会静默失败。
5. Astro 按需渲染的路由（`export const prerender = false`，或 `output: "server"` 路由）在构建时永远不会被扫描，因此它们的表单永远不会被注册。将表单放在预渲染页面上或依赖静态骨架文件。
6. 一个“缺失”的合法提交通常是 Akismet 假阳性：检查垃圾邮件列表（或使用 `?state=spam` 的 API）并标记为验证。不要首先构建自定义恢复函数或禁用垃圾邮件过滤。
7. 对于自定义成功页面，使用无扩展名的 `action` 路径（`/thank-you`，而不是 `/thank-you.html`）——Netlify 在 `/thank-you` 下提供 `thank-you.html`，而 `.html` 路径返回 404。
