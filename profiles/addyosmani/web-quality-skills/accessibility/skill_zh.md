# 可访问性 (a11y)

基于 WCAG 2.2 和 Lighthouse 可访问性审计的综合可访问性指南。目标：让包括残障人士在内的所有人都能使用内容。

## 以证据为导向的审计工作流

当有渲染后的页面时：

1. 当该功能可用时，运行实时的 Lighthouse 可访问性审计；使用 Chrome DevTools MCP 时，调用 `lighthouse_audit`。对于通用公开页面，使用移动导航模式；当重新加载会丢失已认证或用户创建的状态时，使用快照模式。
2. 使用审计中失败的节点来定位相关的组件或模板，而不是在整个仓库中搜索通用的模式。
3. 检查渲染后的无障碍树快照，以查看名称、角色、状态、地标和标题结构；使用 Chrome DevTools MCP 时，调用 `take_snapshot`。使用键盘执行受影响的流程。
4. 修复源代码，然后重新运行相同的审计和手动交互测试。

如果实时工具不可用，使用 Lighthouse CLI 或 axe 进行自动化覆盖检查，并完成相同的手动检查。自动化工具只能检测一部分无障碍障碍：100 分并不意味着符合 WCAG 标准，低分也不能替代问题层面的证据。

## WCAG 原则：POUR

| 原则 | 描述 |
|--------|-------------|
| **P**erceivable | 内容可通过不同感官被感知 |
| **O**perable | 界面可被所有用户操作 |
| **U**nderstandable | 内容与界面易于理解 |
| **R**obust | 内容兼容辅助技术 |

## 符合级别

| 级别 | 要求 | 目标 |
|-------|-------------|--------|
| **A** | 最低无障碍 | 必须满足 |
| **AA** | 标准合规 | 应满足（许多司法管辖区有法律要求） |
| **AAA** | 增强无障碍 | 锦上添花 |

---

## 可感知

### 文本替代（1.1）

**图片需要替代文本：**
```html
<!-- ❌ 缺少替代文本 -->
<img src="chart.png">

<!-- ✅ 描述性替代文本 -->
<img src="chart.png" alt="条形图显示 Q3 销售额增长 40%">

<!-- ✅ 装饰性图片（空替代文本） -->
<img src="decorative-border.png" alt="" role="presentation">

<!-- ✅ 复杂图片，带更详细描述 -->
<figure>
  <img src="infographic.png" alt="2024 市场趋势信息图" 
       aria-describedby="infographic-desc">
  <figcaption id="infographic-desc">
    <!-- 详细描述 -->
  </figcaption>
</figure>
```

**图标按钮需要可访问的名称：**
```html
<!-- ❌ 无可访问名称 -->
<button><svg><!-- 菜单图标 --></svg></button>

<!-- ✅ 使用 aria-label -->
<button aria-label="打开菜单">
  <svg aria-hidden="true"><!-- 菜单图标 --></svg>
</button>

<!-- ✅ 使用视觉隐藏文本 -->
<button>
  <svg aria-hidden="true"><!-- 菜单图标 --></svg>
  <span class="visually-hidden">打开菜单</span>
</button>
```

**视觉隐藏类：**
```css
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

### 颜色对比（1.4.3, 1.4.6）

| 文本尺寸 | AA 最低要求 | AAA 增强要求 |
|-----------|------------|--------------|
| 正文文本（< 18px / < 14px 加粗） | 4.5:1 | 7:1 |
| 大号文本（≥ 18px / ≥ 14px 加粗） | 3:1 | 4.5:1 |
| UI 组件与图形 | 3:1 | 3:1 |

```css
/* ❌ 对比度不足（2.5:1） */
.low-contrast {
  color: #999;
  background: #fff;
}

/* ✅ 对比度足够（7:1） */
.high-contrast {
  color: #333;
  background: #fff;
}

/* ✅ 焦点状态也需要对比度（与背景对比 ≥3:1，WCAG 1.4.11） */
:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}
```

**不要仅依赖颜色：**
```html
<!-- ❌ 仅通过颜色表示错误 -->
<input class="error-border">
<style>.error-border { border-color: red; }</style>

<!-- ✅ 颜色 + 图标 + 文本 -->
<div class="field-error">
  <input aria-invalid="true" aria-describedby="email-error">
  <span id="email-error" class="error-message">
    <svg aria-hidden="true"><!-- 错误图标 --></svg>
    请输入有效的邮箱地址
  </span>
</div>
```

### 媒体替代（1.2）

```html
<!-- 带字幕的视频 -->
<video controls>
  <source src="video.mp4" type="video/mp4">
  <track kind="captions" src="captions.vtt" srclang="en" label="English" default>
  <track kind="descriptions" src="descriptions.vtt" srclang="en" label="Descriptions">
</video>

<!-- 带转录的音频 -->
<audio controls>
  <source src="podcast.mp3" type="audio/mp3">
</audio>
<details>
  <summary>转录文本</summary>
  <p>完整转录文本...</p>
</details>
```

---

## 可操作

### 键盘可访问（2.1）

**所有功能都必须支持键盘操作。** 优先使用原生交互元素——` <button>`、` <a href>` 和表单控件天然支持 Enter/Space 激活、焦点和辅助技术语义。只有无法使用原生元素时，才添加手动键盘处理。

```html
<!-- ❌ 仅支持点击的非交互元素：不可聚焦，无键盘激活 -->
<div class="card" onclick="handleAction()">打开</div>

<!-- ✅ 最佳实践：使用原生按钮 -->
<button type="button" onclick="handleAction()">打开</button>
```

```javascript
// ✅ 必须使用非交互元素时（例如 role="button" 的 div），
// 请使其可聚焦并处理键盘激活。
// 不要将其添加到原生 <button> 中——Enter/Space 已触发点击，否则会重复触发。
element.setAttribute('role', 'button');
element.setAttribute('tabindex', '0');
element.addEventListener('click', handleAction);
element.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    handleAction();
  }
});
```

**无键盘陷阱。** 用户必须能够使用 Tab 键进入和离开每个组件。对于对话框，使用 [模态焦点陷阱模式](references/A11Y-PATTERNS.md#modal-focus-trap)——原生 `<dialog>` 元素会自动处理。

### 焦点可见（2.4.7）

```css
/* ❌ 切勿移除焦点轮廓 */
*:focus { outline: none; }

/* ✅ 使用 :focus-visible 实现仅键盘聚焦 */
:focus {
  outline: none;
}

:focus-visible {
  outline: 2px solid currentColor; /* 继承文本颜色 → 已检查对比度 */
  outline-offset: 2px;
}

/* ✅ 或选择品牌色，并验证与每个背景的对比度 ≥3:1 */
button:focus-visible {
  box-shadow: 0 0 0 3px rgba(0, 95, 204, 0.5);
}
```

### 焦点不被遮挡（2.4.11）——新增于 2.2

当元素获得键盘焦点时，不能被其他作者创建的内容（如粘性页眉、页脚或重叠面板）完全遮挡。在 AAA 级别（2.4.12），焦点元素不得有任何部分被遮挡。

```css
/* ✅ 滚动到聚焦元素时考虑粘性页眉 */
:target {
  scroll-margin-top: 80px;
}

/* ✅ 确保聚焦项避开固定/粘性栏 */
:focus {
  scroll-margin-top: 80px;
  scroll-margin-bottom: 60px;
}
```

### 跳转链接（2.4.1）

提供跳转链接，使键盘用户能够绕过重复的导航。参阅 [跳转链接模式](references/A11Y-PATTERNS.md#skip-link) 了解完整的标记和样式。

### 目标尺寸（2.5.8）——新增于 2.2

交互目标至少需要 **24 × 24 CSS 像素**（AA）。例外情况：行内文本链接、浏览器控制尺寸的元素，以及目标框居中放置的 24px 圆不与另一个目标重叠的情况。

```css
/* ✅ 最小目标尺寸 */
button,
[role="button"],
input[type="checkbox"] + label,
input[type="radio"] + label {
  min-width: 24px;
  min-height: 24px;
}

/* ✅ 舒适的目标尺寸（推荐 44×44） */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

### 拖拽移动（2.5.7）——新增于 2.2

任何需要拖拽的操作都必须有单指针的替代方式（例如按钮、输入框）。参阅 [拖拽移动模式](references/A11Y-PATTERNS.md#dragging-movements) 了解可排序列表示例。

### 时间（2.2）

```javascript
// 允许用户延长时间限制
function showSessionWarning() {
  const modal = createModal({
    title: '会话即将过期',
    content: '您的会话将在 2 分钟后过期。',
    actions: [
      { label: '延长会话', action: extendSession },
      { label: '登出', action: logout }
    ],
    timeout: 120000
  });
}
```

### 动画（2.3）

```css
/* 尊重减少动画偏好设置 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 可理解

### 页面语言（3.1.1）

```html
<!-- ❌ 未指定语言 -->
<html>

<!-- ✅ 指定了语言 -->
<html lang="en">

<!-- ✅ 页面内语言可变化 -->
<p>法语中“你好”是 <span lang="fr">bonjour</span>。</p>
```

### 一致的导航（3.2.3）

```html
<!-- 导航应在所有页面中保持一致 -->
<nav aria-label="主要">
  <ul>
    <li><a href="/" aria-current="page">首页</a></li>
    <li><a href="/products">产品</a></li>
    <li><a href="/about">关于</a></li>
  </ul>
</nav>
```

### 一致的帮助（3.2.6）——新增于 2.2

如果帮助机制（联系信息、聊天组件、常见问题链接、自助选项）在多个页面中重复出现，每次都必须以**相同的相对顺序**出现。依赖一致位置的用户不应在每个页面中逐个查找帮助。

### 表单标签（3.3.2）

每个输入都需要程序关联的标签。参阅 [表单标签模式](references/A11Y-PATTERNS.md#form-labels) 了解显式、隐式和指导性示例。

### 错误处理（3.3.1, 3.3.3）

使用 `role="alert"` 或 `aria-live` 向屏幕阅读器播报错误，在无效字段上设置 `aria-invalid="true"`，并在提交时聚焦第一个错误。参阅 [错误处理模式](references/A11Y-PATTERNS.md#error-handling) 了解完整的标记和 JS。

### 冗余输入（3.3.7）——新增于 2.2

不要强制用户重新输入同一会话中已经提供的信息。可从之前的步骤自动填充，或让用户从之前输入的值中选择。例外情况：安全重新确认和已过期内容。

```html
<!-- ✅ 从账单地址自动填充配送地址 -->
<fieldset>
  <legend>配送地址</legend>
  <label>
    <input type="checkbox" id="same-as-billing" checked>
    与账单地址相同
  </label>
  <!-- 勾选时自动填充字段 -->
</fieldset>
```

### 可访问的身份验证（3.3.8）——新增于 2.2

登录流程不得依赖认知功能测试（例如，记住密码、解谜），除非至少满足以下一项：
- 提供复制粘贴或自动填充机制
- 存在替代方法（例如，通行密钥、单点登录、邮件链接）
- 测试使用物体识别或个人内容（仅 AA；AAA 移除此例外）

```html
<!-- ✅ 允许在密码字段中粘贴 -->
<input type="password" id="password" autocomplete="current-password">

<!-- ✅ 提供无密码替代方案 -->
<button type="button">使用通行密钥登录</button>
<button type="button">通过邮件获取登录链接</button>
```

---

## 稳健

### ARIA 使用（4.1.2）

**优先使用原生元素：**
```html
<!-- ❌ 在 div 上使用 ARIA 角色 -->
<div role="button" tabindex="0">点击我</div>

<!-- ✅ 原生按钮 -->
<button>点击我</button>

<!-- ❌ ARIA 复选框 -->
<div role="checkbox" aria-checked="false">选项</div>

<!-- ✅ 原生复选框 -->
<label><input type="checkbox"> 选项</label>
```

**当需要使用 ARIA 时，** 使用正确的角色和状态。参阅 [ARIA 标签页模式](references/A11Y-PATTERNS.md#aria-tabs) 了解完整的标签页列表示例。

### 实时区域（4.1.3）

使用 `aria-live` 区域在不移动焦点的情况下播报动态内容变化。参阅 [实时区域模式](references/A11Y-PATTERNS.md#live-regions-and-notifications) 了解标记和 `showNotification()` 辅助函数。

---

## 测试清单

### 自动化测试

优先使用返回失败渲染节点直接给代理的实时 Lighthouse 审计。使用 Chrome DevTools MCP 时，此操作为 `lighthouse_audit`。否则：

```bash
# Lighthouse 可访问性审计
npx lighthouse https://example.com --only-categories=accessibility

# axe-core
npm install @axe-core/cli -g
axe https://example.com
```

### 手动测试

- [ ] **键盘导航：** 通过整个页面 Tab 跳转，使用 Enter/Space 激活
- [ ] **屏幕阅读器：** 使用 VoiceOver（Mac）、NVDA（Windows）或 TalkBack（Android）进行测试
- [ ] **缩放：** 内容在 200% 缩放下可用
- [ ] **高对比度：** 使用 Windows 高对比度模式进行测试
- [ ] **减少动画：** 使用 `prefers-reduced-motion: reduce` 进行测试
- [ ] **焦点顺序：** 符合逻辑顺序且遵循视觉顺序
- [ ] **目标尺寸：** 交互元素满足 24×24px 最低要求

参阅 [屏幕阅读器命令参考](references/A11Y-PATTERNS.md#screen-reader-commands) 了解 VoiceOver 和 NVDA 快捷键。

---

## 按影响程度划分的常见问题

### 关键（立即修复）
1. 缺失表单标签
2. 缺失图片替代文本
3. 颜色对比不足
4. 键盘陷阱
5. 无焦点指示器

### 严重（发布前修复）
1. 缺失页面语言
2. 缺失标题结构
3. 非描述性链接文本
4. 自动播放媒体
5. 缺失跳转链接

### 中等（尽快修复）
1. 图标缺少 ARIA 标签
2. 导航不一致
3. 缺失错误识别
4. 无控制的计时
5. 缺失地标区域

## 参考

- [WCAG 2.2 快速参考](https://www.w3.org/WAI/WCAG22/quickref/)
- [WAI-ARIA 编写实践](https://www.w3.org/WAI/ARIA/apg/)
- [Deque axe 规则](https://dequeuniversity.com/rules/axe/)
- [Web 质量审计](../web-quality-audit/SKILL.md)
- [WCAG 标准参考](references/WCAG.md)
- [可访问性代码模式](references/A11Y-PATTERNS.md)
