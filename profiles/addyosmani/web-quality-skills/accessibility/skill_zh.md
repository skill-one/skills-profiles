# 可访问性 (a11y)

基于 WCAG 2.2 和 Lighthouse 可访问性审核的综合可访问性指南。目标：使内容可供所有人使用，包括残障人士。

## 基于证据的审核工作流程

当渲染后的页面可用时：

1.  当该功能可用时，运行实时 Lighthouse 可访问性审核；使用 Chrome DevTools MCP 时，使用 `lighthouse_audit`。对于通用公共页面，使用移动导航模式；在重新加载会丢失认证或用户创建状态时，使用快照模式。
2.  使用失败的审核节点来定位相关的组件或模板，而不是在整个存储库中搜索通用模式。
3.  检查渲染的可访问性树快照，以检查名称、角色、状态、地标和标题结构；使用 Chrome DevTools MCP 时，使用 `take_snapshot`。使用键盘执行受影响的流程。
4.  修复源代码，然后重新运行相同的审核和手动交互。

如果实时工具不可用，请使用 Lighthouse CLI 或 axe 进行自动化覆盖，并完成相同的手动检查。自动化工具仅检测可访问性障碍的一小部分：100 分并不代表 WCAG 合规性，低分也不能替代问题级别的证据。

## WCAG 原则：POUR

| 原则 | 描述 |
|-------|-------------|
| **P**erceivable | 内容可以通过不同的感官感知 |
| **O**perable | 界面可以被所有用户操作 |
| **U**nderstandable | 内容和界面是易于理解的 |
| **R**obust | 内容可以在辅助技术中工作 |

## 合规级别

| 级别 | 要求 | 目标 |
|-------|-------------|--------|
| **A** | 最小可访问性 | 必须通过 |
| **AA** | 标准合规性 | 应该通过（在许多司法管辖区是法律要求） |
| **AAA** | 增强可访问性 | 不错 |

---

## 可感知

### 文本替代 (1.1)

**图像需要 alt 文本：**
```html
<!-- ❌ 缺少 alt -->
<img src="chart.png">

<!-- ✅ 描述性 alt -->
<img src="chart.png" alt="显示第三季度销售额增长40%的条形图">

<!-- ✅ 装饰性图像（空 alt） -->
<img src="decorative-border.png" alt="" role="presentation">

<!-- ✅ 复杂图像的较长描述 -->
<figure>
  <img src="infographic.png" alt="2024市场趋势信息图" 
       aria-describedby="infographic-desc">
  <figcaption id="infographic-desc">
    <!-- 详细描述 -->
  </figcaption>
</figure>
```

**图标按钮需要可访问的名称：**
```html
<!-- ❌ 无可访问的名称 -->
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

### 颜色对比度 (1.4.3, 1.4.6)

| 文本大小 | AA 最小 | AAA 增强 |
|-----------|------------|--------------|
| 普通文本 (< 18px / < 14px 粗体) | 4.5:1 | 7:1 |
| 大文本 (≥ 18px / ≥ 14px 粗体) | 3:1 | 4.5:1 |
| UI 组件和图形 | 3:1 | 3:1 |

```css
/* ❌ 低对比度 (2.5:1) */
.low-contrast {
  color: #999;
  background: #fff;
}

/* ✅ 充足对比度 (7:1) */
.high-contrast {
  color: #333;
  background: #fff;
}

/* ✅ 聚焦状态也需要对比度（相对于背景，WCAG 1.4.11） */
:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}
```

**不要仅依赖颜色：**
```html
<!-- ❌ 仅用颜色表示错误 -->
<input class="error-border">
<style>.error-border { border-color: red; }</style>

<!-- ✅ 颜色 + 图标 + 文本 -->
<div class="field-error">
  <input aria-invalid="true" aria-describedby="email-error">
  <span id="email-error" class="error-message">
    <svg aria-hidden="true"><!-- 错误图标 --></svg>
    请输入有效的电子邮件地址
  </span>
</div>
```

### 媒体替代 (1.2)

```html
<!-- 带字幕的视频 -->
<video controls>
  <source src="video.mp4" type="video/mp4">
  <track kind="captions" src="captions.vtt" srclang="en" label="English" default>
  <track kind="descriptions" src="descriptions.vtt" srclang="en" label="Descriptions">
</video>

<!-- 带文本稿的音频 -->
<audio controls>
  <source src="podcast.mp3" type="audio/mp3">
</audio>
<details>
  <summary>文本稿</summary>
  <p>完整文本稿...</p>
</details>
```

---

## 可操作

### 键盘可访问 (2.1)

**所有功能必须通过键盘访问。** 优先使用原生交互元素——`<button>`、`<a href>` 和表单控件可以免费处理 Enter/Space 激活、焦点和辅助技术语义。只有在无法使用原生元素时才添加手动键盘处理。

```html
<!-- ❌ 非交互元素仅点击：不可聚焦，无键盘激活 -->
<div class="card" onclick="handleAction()">打开</div>

<!-- ✅ 最佳：使用原生按钮 -->
<button type="button" onclick="handleAction()">打开</button>
```

```javascript
// ✅ 当你必须使用非交互元素（例如 role="button" 的 div）时，
// 使其可聚焦并处理键盘激活。不要将此添加到原生 <button>——
// Enter/Space 已经触发点击，所以你会双触发。
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

**无键盘陷阱。** 用户必须能够 Tab 进入和退出每个组件。对于对话框，使用 [模态焦点陷阱模式](references/A11Y-PATTERNS.md#modal-focus-trap)——原生 `<dialog>` 元素会自动处理此功能。

### 聚焦可见 (2.4.7)

```css
/* ❌ 不要移除焦点轮廓 */
*:focus { outline: none; }

/* ✅ 使用 :focus-visible 仅用于键盘聚焦 */
:focus {
  outline: none;
}

:focus-visible {
  outline: 2px solid currentColor; /* 继承文本颜色 → 已经检查过对比度 */
  outline-offset: 2px;
}

/* ✅ 或者选择品牌颜色，并验证其与每个背景的对比度 ≥3:1 */
button:focus-visible {
  box-shadow: 0 0 0 3px rgba(0, 95, 204, 0.5);
}
```

### 聚焦不被遮挡 (2.4.11) — 2.2 新增

当元素获得键盘焦点时，它不能被其他作者创建的内容（如粘性页眉、页脚或重叠面板）完全隐藏。在 AAA 级别 (2.4.12)，聚焦元素的所有部分都不能被隐藏。

```css
/* ✅ 在滚动到聚焦元素时考虑粘性页眉 */
:target {
  scroll-margin-top: 80px;
}

/* ✅ 确保聚焦项清除固定/粘性条 */
:focus {
  scroll-margin-top: 80px;
  scroll-margin-bottom: 60px;
}
```

### 跳过链接 (2.4.1)

提供一个跳过链接，以便键盘用户可以跳过重复的导航。有关完整标记和样式的详细信息，请参阅 [跳过链接模式](references/A11Y-PATTERNS.md#skip-link)。

### 目标大小 (2.5.8) — 2.2 新增

交互目标必须至少为 **24 × 24 CSS 像素**（AA）。例外：内联文本链接、浏览器控制大小的元素，以及 24px 圆形以边界框为中心时不会与其他目标重叠的目标。

```css
/* ✅ 最小目标大小 */
button,
[role="button"],
input[type="checkbox"] + label,
input[type="radio"] + label {
  min-width: 24px;
  min-height: 24px;
}

/* ✅ 舒适的目标大小（推荐 44×44） */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

### 拖动动作 (2.5.7) — 2.2 新增

任何需要拖动的操作都必须有一个单指替代方案（例如，按钮、输入）。有关可排序列表示例，请参阅 [拖动动作模式](references/A11Y-PATTERNS.md#dragging-movements)。

### 时间 (2.2)

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

### 运动 (2.3)

```css
/* 尊重减少运动偏好 */
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

## 易理解

### 页面语言 (3.1.1)

```html
<!-- ❌ 未指定语言 -->
<html>

<!-- ✅ 指定语言 -->
<html lang="en">

<!-- ✅ 页面内语言变化 -->
<p>法语中的“你好”是 <span lang="fr">bonjour</span>。</p>
```

### 一致导航 (3.2.3)

```html
<!-- 导航应在页面之间保持一致 -->
<nav aria-label="主导航">
  <ul>
    <li><a href="/" aria-current="page">首页</a></li>
    <li><a href="/products">产品</a></li>
    <li><a href="/about">关于我们</a></li>
  </ul>
</nav>
```

### 一致帮助 (3.2.6) — 2.2 新增

如果一个帮助机制（联系信息、聊天小部件、常见问题解答链接、自助选项）在多个页面中重复出现，它必须在每次出现时以**相同的相对顺序**出现。依赖一致放置的用户不应在每页上都得寻找帮助。

### 表单标签 (3.3.2)

每个输入都需要一个程序关联的标签。有关显式、隐式和说明性示例，请参阅 [表单标签模式](references/A11Y-PATTERNS.md#form-labels)。

### 错误处理 (3.3.1, 3.3.3)

使用 `role="alert"` 或 `aria-live` 向屏幕阅读器宣布错误，在无效字段上设置 `aria-invalid="true"`，并在提交时聚焦第一个错误。有关完整标记和 JS，请参阅 [错误处理模式](references/A11Y-PATTERNS.md#error-handling)。

### 重复输入 (3.3.7) — 2.2 新增

不要强迫用户在同一会话中重新输入他们已经提供的信息。从早期步骤自动填充，或允许用户从之前输入的值中选择。例外：安全重新确认和已过期的内容。

```html
<!-- ✅ 从账单自动填充运货地址 -->
<fieldset>
  <legend>运货地址</legend>
  <label>
    <input type="checkbox" id="same-as-billing" checked>
    与账单地址相同
  </label>
  <!-- 当选中时自动填充的字段 -->
</fieldset>
```

### 可访问认证 (3.3.8) — 2.2 新增

登录流程不得依赖认知功能测试（例如，记住密码、解决谜题），除非至少满足以下条件之一：
- 提供复制粘贴或自动填充机制
- 存在替代方法（例如，密码凭证、SSO、电子邮件链接）
- 测试使用对象识别或个人内容（仅 AA；AAA 移除了此例外）

```html
<!-- ✅ 密码字段允许粘贴 -->
<input type="password" id="password" autocomplete="current-password">

<!-- ✅ 提供无密码替代方案 -->
<button type="button">使用密码凭证登录</button>
<button type="button">通过电子邮件获取登录链接</button>
```

---

## 稳健

### ARIA 使用 (4.1.2)

**优先使用原生元素：**
```html
<!-- ❌ div 上的 ARIA 角色 -->
<div role="button" tabindex="0">点击我</div>

<!-- ✅ 原生按钮 -->
<button>点击我</button>

<!-- ❌ ARIA 复选框 -->
<div role="checkbox" aria-checked="false">选项</div>

<!-- ✅ 原生复选框 -->
<label><input type="checkbox"> 选项</label>
```

**当需要 ARIA 时，使用正确的角色和状态。** 有关完整标签列表示例，请参阅 [ARIA 标签模式](references/A11Y-PATTERNS.md#aria-tabs)。

### 活动区域 (4.1.3)

使用 `aria-live` 区域来宣布动态内容变化，而无需移动焦点。有关标记和 `showNotification()` 辅助函数，请参阅 [活动区域和通知模式](references/A11Y-PATTERNS.md#live-regions-and-notifications)。

---

## 测试清单

### 自动化测试

优先使用返回直接失败渲染节点的实时 Lighthouse 审核到代理。使用 Chrome DevTools MCP 时，这是 `lighthouse_audit`。否则：

```bash
# Lighthouse 可访问性审核
npx lighthouse https://example.com --only-categories=accessibility

# axe-core
npm install @axe-core/cli -g
axe https://example.com
```

### 手动测试

- [ ] **键盘导航：** Tab 通过整个页面，使用 Enter/Space 激活
- [ ] **屏幕阅读器：** 使用 VoiceOver（Mac）、NVDA（Windows）或 TalkBack（Android）进行测试
- [ ] **缩放：** 内容在 200% 缩放下可用
- [ ] **高对比度：** 使用 Windows 高对比度模式进行测试
- [ ] **减少运动：** 使用 `prefers-reduced-motion: reduce` 进行测试
- [ ] **焦点顺序：** 逻辑且遵循视觉顺序
- [ ] **目标大小：** 交互元素满足 24×24px 最小要求

有关 VoiceOver 和 NVDA 快捷键的详细信息，请参阅 [屏幕阅读器命令参考](references/A11Y-PATTERNS.md#screen-reader-commands)。

---

## 按影响分类的常见问题

### 关键（立即修复）
1. 缺少表单标签
2. 缺少图像 alt 文本
3. 颜色对比度不足
4. 键盘陷阱
5. 无焦点指示

### 严重（发布前修复）
1. 缺少页面语言
2. 缺少标题结构
3. 非描述性链接文本
4. 自动播放媒体
5. 缺少跳过链接

### 适度（尽快修复）
1. 图标缺少 ARIA 标签
2. 导航不一致
3. 缺少错误识别
4. 无控制的时间
5. 缺少地标区域

## 参考

- [WCAG 2.2 快速参考](https://www.w3.org/WAI/WCAG22/quickref/)
- [WAI-ARIA 作者实践](https://www.w3.org/WAI/ARIA/apg/)
- [Deque axe 规则](https://dequeuniversity.com/rules/axe/)
- [Web 质量审核](../web-quality-audit/SKILL.md)
- [WCAG 标准参考](references/WCAG.md)
- [可访问性代码模式](references/A11Y-PATTERNS.md)
