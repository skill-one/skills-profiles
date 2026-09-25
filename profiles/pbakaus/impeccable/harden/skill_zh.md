强化接口对边界情况、错误、国际化问题以及破坏理想化设计的现实使用场景的应对能力。

## 评估加固需求

识别弱点和边界情况：

1. **测试极端输入**：
   - 非常长的文本（名称、描述、标题）
   - 非常短的文本（空值、单字符）
   - 特殊字符（emoji、RTL 文本、重音符号）
   - 大数字（百万、十亿）
   - 大量项目（1000+ 列表项、50+ 选项）
   - 无数据（空状态）

2. **测试错误场景**：
   - 网络故障（离线、网络慢、超时）
   - API 错误（400、401、403、404、500）
   - 验证错误
   - 权限错误
   - 限流
   - 并发操作

3. **测试国际化**：
   - 较长的翻译（德语通常比英语长 30%）
   - RTL 语言（阿拉伯语、希伯来语）
   - 字符集（中文、日文、韩文、emoji）
   - 日期/时间格式
   - 数字格式（1,000 对比 1.000）
   - 货币符号

**CRITICAL**：只有完美数据才适用的设计尚未达到生产就绪状态。需以现实为基准进行加固。

## 加固维度

系统性提升健壮性：

### 文本溢出与换行

**长文本处理**：
```css
/* Single line with ellipsis */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Multi-line with clamp */
.line-clamp {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Allow wrapping */
.wrap {
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
```

**Flex/Grid 溢出**：
```css
/* Prevent flex items from overflowing */
.flex-item {
  min-width: 0; /* Allow shrinking below content size */
  overflow: hidden;
}

/* Prevent grid items from overflowing */
.grid-item {
  min-width: 0;
  min-height: 0;
}
```

**响应式文本尺寸**：
- 使用 `clamp()` 实现流式排版
- 设置最小可读尺寸（移动端 14px）
- 测试文本缩放（缩放至 200%）
- 确保容器随文本自动扩展

### 国际化（i18n）

**文本扩展**：
- 为翻译预留 30-40% 的空间预算
- 使用随内容自适应或适配的 flexbox/grid
- 使用最长语言（通常是德语）进行测试
- 避免在文本容器上设置固定宽度

```jsx
// ❌ Bad: Assumes short English text
<button className="w-24">Submit</button

// ✅ Good: Adapts to content
<button className="px-4 py-2">Submit</button
```

**RTL（从右向左）支持**：
```css
/* Use logical properties */
margin-inline-start: 1rem; /* Not margin-left */
padding-inline: 1rem; /* Not padding-left/right */
border-inline-end: 1px solid; /* Not border-right */

/* Or use dir attribute */
[dir="rtl"] .arrow { transform: scaleX(-1); }
```

**字符集支持**：
- 全程使用 UTF-8 编码
- 使用中文、日文、韩文（CJK）字符进行测试
- 使用 emoji 进行测试（它们可能占 2-4 字节）
- 处理不同的文字系统（拉丁、西里尔、阿拉伯等）

**日期/时间格式化**：
```javascript
// ✅ Use Intl API for proper formatting
new Intl.DateTimeFormat('en-US').format(date); // 1/15/2024
new Intl.DateTimeFormat('de-DE').format(date); // 15.1.2024

new Intl.NumberFormat('en-US', { 
  style: 'currency', 
  currency: 'USD' 
}).format(1234.56); // $1,234.56
```

**复数化（变格）**：
```javascript
// ❌ Bad: Assumes English pluralization
`${count} item${count !== 1 ? 's' : ''}`

// ✅ Good: Use proper i18n library
t('items', { count }) // Handles complex plural rules
```

### 错误处理

**网络错误**：
- 显示清晰的错误信息
- 提供重试按钮
- 说明发生了什么
- 如适用，提供离线模式
- 处理超时场景

```jsx
// Error states with recovery
{error && (
  <ErrorMessage >
    <p >Failed to load data. {error.message}</p >
    <button onClick={retry}>Try again</button >
  </ErrorMessage >
)}
```

**表单验证错误**：
- 在字段附近显示内联错误
- 消息清晰、具体
- 给出修改建议
- 不要在不必要时阻止提交
- 在出错时保留用户输入

**API 错误**：
- 根据每种状态码进行适当处理
  - 400：显示验证错误
  - 401：重定向至登录页
  - 403：显示权限错误
  - 404：显示未找到状态
  - 429：显示限流消息
  - 500：显示通用错误，并提供支持

**优雅降级**：
- 核心功能无需 JavaScript 即可运行
- 图片带有 alt 文本
- 渐进式增强
- 为不支持的特性提供回退方案

### 边界情况与边界条件

**空状态**：
- 列表无项目
- 无搜索结果
- 无通知
- 无数据可显示
- 提供清晰的下一步操作

**加载状态**：
- 初始加载
- 分页加载
- 刷新
- 显示加载内容（“正在加载你的项目...”）
- 为长时间操作提供耗时预估

**大数据集**：
- 分页或虚拟滚动
- 搜索/筛选功能
- 性能优化
- 不要一次性加载全部 10,000 项

**并发操作**：
- 防止重复提交（加载时禁用按钮）
- 处理竞态条件
- 带回滚的乐观更新
- 冲突解决

**权限状态**：
- 无查看权限
- 无编辑权限
- 只读模式
- 明确说明原因

**浏览器兼容性**：
- 为现代特性提供 polyfill
- 为不支持的 CSS 提供回退方案
- 特性检测（而非浏览器检测）
- 在目标浏览器中进行测试

### 新手引导与首次运行体验

生产就绪的功能面向首次用户，而非仅面向高级用户。设计能让新用户快速感受到价值的路径：

**空状态**：每个零数据屏幕都需要：
- 此处将显示的内容（描述或插画）
- 该内容对用户的重要性
- 创建第一个项目或从模板开始的清晰行动号召（CTA）
- 视觉吸引力（而非仅有“暂无项目”的空空格）

需处理的空状态类型：
- **首次使用**：突出价值，提供模板
- **用户已清空**：操作轻量，便于重新创建
- **无结果**：建议使用不同的查询，提供清除筛选器的选项
- **无权限**：说明原因，说明如何获取权限

**首次运行体验**：尽快让用户进入其“顿悟时刻”。
- 演示而非说明——以实际示例代替文字描述
- 渐进式披露——一次教授一项内容，而非一次性讲授所有内容
- 使引导可选——允许熟练用户跳过
- 提供智能默认值，使必要的设置最少化

**功能发现**：在用户需要时教授功能，而非前置讲授。
- 在功能使用点提供上下文提示（简短、可关闭、仅一次）
- 新功能或未使用功能上的徽章或标识
- 静默庆祝激活事件（使用提示，而非弹窗）

**绝不**：
- 在用户能够操作产品前强制展示冗长的引导
- 重复显示相同的提示（需记录并尊重关闭操作）
- 在引导 tour 期间阻断整个 UI
- 创建与真实产品脱节的独立教程模式
- 设计仅显示“无项目”且无下一步操作的空状态

### 输入验证与消毒

**客户端验证**：
- 必填字段
- 格式验证（邮箱、电话、URL）
- 长度限制
- 模式匹配
- 自定义验证规则

**服务端验证**（始终执行）：
- 绝不能仅信任客户端
- 验证并消毒所有输入
- 防范注入攻击
- 限流

**约束处理**：
```html
<!-- Set clear constraints -->
<a input 
  type="a text"
  maxlength="a 100"
  pattern="[A-Za-z0-9]+"
  required
  aria-describedby="a username-hint"
/>
<a small id="a username-hint" >
  Letters and numbers only, up to 100 characters
</a small >
```

### 无障碍健壮性

**键盘导航**：
- 所有功能均可通过键盘操作
- 合理的 Tab 顺序
- 模态框中的焦点管理
- 长内容的跳转链接

**屏幕阅读器支持**：
- 正确的 ARIA 标签
- 播报动态变化（实时区域）
- 描述性的 alt 文本
- 语义化 HTML

**运动敏感度**：
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**高对比度模式**：
- 在 Windows 高对比度模式下进行测试
- 不能仅依赖颜色
- 提供替代的视觉提示

### 性能健壮性

**网络较慢**：
- 渐进式图片加载
- 骨架屏
- 乐观 UI 更新
- 离线支持（服务工作者）

**内存泄漏**：
- 清理事件监听器
- 取消订阅
- 清除定时器/间隔器
- 组件卸载时取消待处理的请求

**节流与防抖**：
```javascript
// Debounce search input
const debouncedSearch = debounce(handleSearch, 300);

// Throttle scroll handler
const throttledScroll = throttle(handleScroll, 100);
```

## 测试策略

**手动测试**：
- 使用极端数据测试（非常长、非常短、为空）
- 在不同语言下进行测试
- 测试离线状态
- 测试慢网络（将连接限制至 3G）
- 使用屏幕阅读器测试
- 仅使用键盘导航测试
- 在旧版浏览器中测试

**自动化测试**：
- 边界情况的单元测试
- 错误场景的集成测试
- 关键路径的端到端（E2E）测试
- 视觉回归测试
- 无障碍测试（axe, WAVE）

**IMPORTANT**：加固的核心在于应对意想不到的情况。真实用户会做出你从未想象到的行为。

**NEVER**：
- 假定输入完美（需验证所有内容）
- 忽略国际化（需面向全球设计）
- 使用笼统的错误信息（“发生错误”）
- 忘记离线场景
- 仅信任客户端验证
- 为文本使用固定宽度
- 假定文本长度符合英语习惯
- 当单个组件出错时阻断整个界面

## 验证加固

使用边界情况进行充分测试：

- **长文本**：尝试 100+ 字符的名称
- **Emoji**：在所有文本字段中使用 emoji
- **RTL**：使用阿拉伯语或希伯来语进行测试
- **CJK**：使用中文/日文/韩文进行测试
- **网络问题**：禁用网络，限制连接速度
- **大数据集**：使用 1000+ 项进行测试
- **并发操作**：快速连续点击提交 10 次
- **错误**：强制 API 错误，测试所有错误状态
- **空值**：清除所有数据，测试空状态

请记住：你是为生产环境的现实进行加固，而非为演示的完美。预期用户输入异常数据、在操作中途失去网络连接，并以意想不到的方式使用你的产品。请将健壮性融入每一个组件。
