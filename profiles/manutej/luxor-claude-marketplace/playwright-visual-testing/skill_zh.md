# Playwright 可视化测试与浏览器自动化

使用 Playwright MCP 服务器集成的全面技能，用于浏览器自动化和可视化测试。该技能支持快速 UI 测试、可视化回归检测、自动化浏览器交互以及现代 Web 应用的跨浏览器验证。

## 何时使用此技能

在以下情况下使用此技能：

- 跨多个浏览器（Chromium、Firefox、WebKit）测试 Web 应用
- 实现可视化回归测试以检测 UI 变更
- 自动化用户交互以进行 QA 和测试
- 在不同视口验证响应式设计
- 为文档或错误报告拍摄屏幕截图
- 测试表单提交和用户工作流
- 验证 Web 界面的可访问性
- 调试浏览器特定问题
- 创建自动化端到端测试套件
- 在部署前验证 Web 应用
- 测试 PWAs 和单页应用
- 捕获用于设计评审的可视化状态

## 核心概念

### Playwright 浏览器自动化理念

Playwright 为现代 Web 应用提供可靠的端到端测试：

- **自动等待**：在交互前自动等待元素变为可操作状态
- **Web 优先断言**：重试断言直到通过或超时
- **跨浏览器**：使用单个 API 在 Chromium、Firefox 和 WebKit 上进行测试
- **可访问性快照**：使用语义结构导航页面，而非视觉渲染
- **可视化测试**：比较屏幕截图以检测可视化回归
- **网络控制**：拦截和模拟网络请求
- **多上下文**：在隔离的浏览器上下文中测试多个场景

### Playwright 关键实体

1. **浏览器**：浏览器实例（Chromium、Firefox、WebKit）
2. **页面**：浏览器中的单个页面/标签
3. **定位器**：使用可访问性树进行元素选择
4. **快照**：页面状态的可访问性树表示
5. **屏幕截图**：页面或元素的视觉捕获
6. **网络请求**：页面发出的 HTTP 请求
7. **控制台消息**：浏览器控制台输出
8. **对话框**：浏览器提示、警告、确认

### 可视化测试工作流程

1. **导航**到目标页面
2. **等待**页面稳定（动画、加载）
3. **捕获**可访问性快照以供参考
4. **拍摄屏幕截图**页面或特定元素
5. **比较**与基线（可选）
6. **验证**视觉外观和功能
7. **记录**结果和问题

## Playwright MCP 服务器工具参考

### 浏览器生命周期管理

#### browser_navigate
在当前页面导航到 URL。

**参数：**
```
url: 要导航到的 URL（必填）
```

**示例：**
```javascript
url: "https://example.com"
```

**最佳实践：**
- 使用包含协议的完整 URL（https://）
- 在执行操作前等待导航完成
- 处理重定向和页面转换

#### browser_navigate_back
导航到历史记录中的上一页。

**参数：** 无

**示例：**
```javascript
// 点击链接后导航回上一页
```

**用例：**
- 测试导航流程
- 验证后退按钮行为
- 多步骤表单导航

#### browser_close
关闭当前浏览器页面。

**参数：** 无

**何时使用：**
- 测试后清理
- 释放系统资源
- 重置浏览器状态

#### browser_resize
调整浏览器视口大小。

**参数：**
```
width: 像素宽度（必填）
height: 像素高度（必填）
```

**常见视口：**
```javascript
// 手机
width: 375, height: 667  // iPhone SE
width: 414, height: 896  // iPhone XR

// 平板
width: 768, height: 1024  // iPad

// 桌面
width: 1280, height: 720  // HD
width: 1920, height: 1080 // 全高清
```

**示例：**
```javascript
width: 375
height: 667
```

### 页面检查与快照

#### browser_snapshot
捕获当前页面的可访问性快照。

**参数：** 无

**返回：**
- 具有语义结构的可访问性树
- 交互元素引用（ref）
- 文本内容和角色
- 交互元素和状态

**使用快照的原因：**
- 比屏幕截图更适合自动化
- 对页面结构的语义理解
- 精确交互的元素引用
- 比视觉解析更快
- 无需视觉渲染即可工作

**示例快照结构：**
```
heading "Welcome" [ref=123]
  text "to our site"
button "Sign In" [ref=456]
textbox "Email" [ref=789]
  value: ""
```

#### browser_take_screenshot
拍摄当前页面或元素的屏幕截图。

**参数：**
```
filename: 输出文件名（可选，默认为 page-{timestamp}.png）
type: 图像格式 - "png" 或 "jpeg"（默认：png）
fullPage: 捕获可滚动的完整页面（默认：false）
element: 人类可读的元素描述（可选）
ref: 从快照中获取的元素引用（可选，需要 element）
```

**屏幕截图类型：**

1. **视口屏幕截图**（默认）：
```javascript
filename: "homepage-viewport.png"
```

2. **完整页面屏幕截图**：
```javascript
filename: "homepage-full.png"
fullPage: true
```

3. **元素屏幕截图**：
```javascript
filename: "header.png"
element: "main header navigation"
ref: "123"
```

**最佳实践：**
- 使用描述性文件名并包含上下文
- PNG 用于 UI 元素（无损）
- JPEG 用于照片/图像（更小的文件大小）
- 完整页面用于文档
- 元素屏幕截图用于专注测试

### 浏览器交互

#### browser_click
在元素上执行点击。

**参数：**
```
element: 人类可读的元素描述（必填）
ref: 从快照中获取的元素引用（必填）
button: "left", "right" 或 "middle"（默认：left）
doubleClick: true 为双击（默认：false）
modifiers: 修饰键数组 ["Alt", "Control", "ControlOrMeta", "Meta", "Shift"]
```

**示例：**

1. **基本点击**：
```javascript
element: "Submit button"
ref: "456"
```

2. **右键点击**：
```javascript
element: "Context menu trigger"
ref: "789"
button: "right"
```

3. **带修饰键的点击**：
```javascript
element: "Link to open in new tab"
ref: "123"
modifiers: ["ControlOrMeta"]
```

4. **双击**：
```javascript
element: "Word to select"
ref: "321"
doubleClick: true
```

#### browser_type
将文本输入到可编辑元素。

**参数：**
```
element: 人类可读的元素描述（必填）
ref: 从快照中获取的元素引用（必填）
text: 要输入的文本（必填）
slowly: 逐个字符输入（默认：false）
submit: 输入后按 Enter（默认：false）
```

**示例：**

1. **表单输入**：
```javascript
element: "Email textbox"
ref: "123"
text: "user@example.com"
```

2. **带提交的搜索**：
```javascript
element: "Search field"
ref: "456"
text: "playwright testing"
submit: true
```

3. **逐字符输入**（触发键处理器）：
```javascript
element: "Auto-complete input"
ref: "789"
text: "New York"
slowly: true
```

#### browser_press_key
按键盘键。

**参数：**
```
key: 键名或字符（必填）
```

**常见键：**
```
ArrowLeft, ArrowRight, ArrowUp, ArrowDown
Enter, Escape, Tab, Backspace, Delete
Home, End, PageUp, PageDown
F1-F12
Control, Alt, Shift, Meta
```

**示例：**
```javascript
// 导航
key: "ArrowDown"

// 提交表单
key: "Enter"

// 关闭对话框
key: "Escape"

// 通过字段切换
key: "Tab"
```

#### browser_fill_form
一次性填充多个表单字段。

**参数：**
```
fields: 字段对象数组（必填）
  - name: 人类可读的字段名
  - type: "textbox", "checkbox", "radio", "combobox", "slider"
  - ref: 从快照中获取的元素引用
  - value: 要设置的值（字符串，"true"/"false" 用于复选框）
```

**示例：**
```javascript
fields: [
  {
    name: "Username",
    type: "textbox",
    ref: "123",
    value: "john_doe"
  },
  {
    name: "Password",
    type: "textbox",
    ref: "456",
    value: "secretpass123"
  },
  {
    name: "Remember me",
    type: "checkbox",
    ref: "789",
    value: "true"
  }
]
```

#### browser_select_option
从下拉菜单选择选项。

**参数：**
```
element: 人类可读的元素描述（必填）
ref: 从快照中获取的元素引用（必填）
values: 要选择的值数组（必填）
```

**示例：**
```javascript
element: "Country dropdown"
ref: "123"
values: ["United States"]
```

**多选：**
```javascript
element: "Programming languages"
ref: "456"
values: ["JavaScript", "Python", "Go"]
```

#### browser_hover
悬停在元素上。

**参数：**
```
element: 人类可读的元素描述（必填）
ref: 从快照中获取的元素引用（必填）
```

**用例：**
- 触发工具提示
- 显示下拉菜单
- 测试悬停状态
- 显示隐藏元素

**示例：**
```javascript
element: "Help icon"
ref: "123"
```

#### browser_drag
在元素之间拖放。

**参数：**
```
startElement: 源元素描述（必填）
startRef: 源元素引用（必填）
endElement: 目标元素描述（必填）
endRef: 目标元素引用（必填）
```

**示例：**
```javascript
startElement: "Task card"
startRef: "123"
endElement: "Done column"
endRef: "456"
```

**用例：**
- 拖放界面
- 列表排序
- 文件上传
- 看板

### 高级交互

#### browser_evaluate
在页面上下文中执行 JavaScript。

**参数：**
```
function: JavaScript 函数作为字符串（必填）
element: 元素描述（可选）
ref: 元素引用（可选，需要 element）
```

**示例：**

1. **页面级脚本**：
```javascript
function: "() => { return document.title; }"
```

2. **元素级脚本**：
```javascript
element: "Custom widget"
ref: "123"
function: "(element) => { return element.getAttribute('data-value'); }"
```

**常见用例：**
```javascript
// 获取页面标题
function: "() => document.title"

// 滚动到底部
function: "() => window.scrollTo(0, document.body.scrollHeight)"

// 获取元素尺寸
function: "(element) => { const rect = element.getBoundingClientRect(); return { width: rect.width, height: rect.height }; }"

// 设置本地存储
function: "() => localStorage.setItem('theme', 'dark')"

// 获取计算样式
function: "(element) => getComputedStyle(element).backgroundColor"
```

#### browser_file_upload
将文件上传到文件输入。

**参数：**
```
paths: 绝对文件路径数组（必填）
  - 省略或传递空数组以取消文件选择器
```

**示例：**
```javascript
paths: [
  "/Users/user/Documents/resume.pdf",
  "/Users/user/Photos/headshot.jpg"
]
```

**单个文件：**
```javascript
paths: ["/Users/user/Downloads/report.csv"]
```

**取消上传：**
```javascript
paths: []
```

### 浏览器状态与调试

#### browser_console_messages
获取浏览器的控制台消息。

**参数：**
```
onlyErrors: 仅返回错误消息（默认：false）
```

**返回：**
- 所有 console.log、console.error、console.warn 消息
- 时间戳和消息类型
- JavaScript 错误和堆栈跟踪

**示例：**

1. **所有消息**：
```javascript
onlyErrors: false
```

2. **仅错误**：
```javascript
onlyErrors: true
```

**用例：**
- 调试 JavaScript 错误
- 监控 API 失败
- 追踪控制台警告
- 验证日志行为

#### browser_network_requests
获取自页面加载以来的所有网络请求。

**参数：** 无

**返回：**
- URL、方法、状态码
- 请求/响应头
- 时间信息
- 请求/响应正文

**用例：**
- 验证 API 调用
- 检查资源加载
- 调试失败请求
- 监控性能
- 验证分析跟踪

#### browser_handle_dialog
响应浏览器对话框。

**参数：**
```
accept: 接受或关闭对话框（必填）
promptText: 提示对话框的文本（可选）
```

**对话框类型：**
- alert：信息消息
- confirm：是/否选择
- prompt：文本输入请求
- beforeunload：页面导航警告

**示例：**

1. **接受警告**：
```javascript
accept: true
```

2. **关闭确认**：
```javascript
accept: false
```

3. **回答提示**：
```javascript
accept: true
promptText: "John Doe"
```

#### browser_wait_for
在继续之前等待条件。

**参数：**
```
text: 等待出现的文本（可选）
textGone: 等待消失的文本（可选）
time: 等待指定秒数（可选）
```

**示例：**

1. **等待文本**：
```javascript
text: "Loading complete"
```

2. **等待移除**：
```javascript
textGone: "Loading..."
```

3. **固定等待**：
```javascript
time: 2
```

**最佳实践：**
- 优先等待特定条件而非固定时间
- 用于动态内容加载
- 等待动画完成
- 确保页面稳定后再拍摄屏幕截图

### 标签管理

#### browser_tabs
管理浏览器标签。

**参数：**
```
action: "list", "new", "close", "select"（必填）
index: 关闭/选择的标签索引（可选）
```

**操作：**

1. **列出标签**：
```javascript
action: "list"
```

2. **新建标签**：
```javascript
action: "new"
```

3. **关闭标签**：
```javascript
action: "close"
index: 1  // 可选，省略则关闭当前标签
```

4. **切换标签**：
```javascript
action: "select"
index: 0
```

**用例：**
- 多标签工作流
- 测试标签特定功能
- 在新标签中打开链接
- 管理多个会话

### 浏览器安装

#### browser_install
安装配置中指定的浏览器。

**参数：** 无

**何时使用：**
- 首次设置
- "浏览器未安装"错误
- 更新浏览器版本
- CI/CD 环境设置

## 可视化测试工作流模式

### 模式 1：基本可视化回归测试

**场景：** 验证主页没有视觉变化

```workflow
1. 导航到页面
   - 使用 browser_navigate 并指定目标 URL
   - 等待页面完全加载

2. 捕获基线
   - 拍摄完整页面屏幕截图
   - 使用 browser_snapshot 获取上下文
   - 记录可见元素

3. 进行变更（如果测试变更）
   - 更新代码、部署
   - 清理缓存

4. 捕获新状态
   - 导航到相同 URL
   - 拍摄相同屏幕截图
   - 手动或使用工具比较

5. 验证差异
   - 预期变更存在
   - 无意外回归
   - 记录发现
```

### 模式 2：响应式设计测试

**场景：** 跨设备测试布局

```workflow
1. 定义视口
   - 手机：375x667（iPhone SE）
   - 平板：768x1024（iPad）
   - 桌面：1920x1080（全高清）

2. 对每个视口：
   a. 调整浏览器
      - browser_resize 并指定尺寸

   b. 导航到页面
      - browser_navigate 到 URL

   c. 等待布局
      - browser_wait_for 条件

   d. 捕获快照
      - browser_snapshot 获取结构

   e. 拍摄屏幕截图
      - browser_take_screenshot 带描述性名称
      - 在文件名中包含视口

3. 比较布局
   - 验证响应式断点
   - 检查元素重排
   - 验证移动导航
   - 确保内容可访问

4. 记录问题
   - 截图任何问题
   - 记录发生问题的视口
   - 记录预期与实际行为
```

### 模式 3：表单测试工作流

**场景：** 测试多步骤表单提交

```workflow
1. 导航到表单
   - browser_navigate 到表单 URL
   - browser_snapshot 获取字段引用

2. 填写表单字段
   - 使用 browser_fill_form 批量输入
   - 或逐个使用 browser_type 输入每个字段
   - 包含验证触发器

3. 测试验证
   - 使用无效数据提交
   - browser_snapshot 查看错误
   - 拍摄错误状态屏幕截图
   - 验证错误消息出现

4. 完成有效提交
   - 填写所有必填字段
   - browser_click 提交按钮
   - 等待成功消息
   - browser_wait_for 确认文本

5. 验证结果
   - 检查成功页面
   - 验证数据提交
   - 拍摄确认屏幕截图
   - 检查网络请求
```

### 模式 4：元素特定可视化测试

**场景：** 测试单个组件变更

```workflow
1. 导航到组件页面
   - 使用 browser_navigate 访问页面
   - 使用 browser_snapshot 获取结构

2. 定位组件
   - 从快照中查找元素引用（ref）
   - 验证组件是否可见

3. 测试各种状态
   a. 默认状态
      - 截取元素截图
      - 记录初始外观

   b. 悬停状态
      - 对元素执行 browser_hover
      - 截取元素截图
      - 与默认状态进行对比

   c. 激活/聚焦状态
      - 对元素执行 browser_click
      - 截取元素截图
      - 验证视觉反馈

   d. 错误状态（如适用）
      - 触发表单验证错误
      - 截取元素截图
      - 验证错误样式

4. 记录状态变化
   - 对比截图
   - 记录预期行为
   - 报告任何问题
```

### 模式 5：跨浏览器测试

**场景：** 验证跨浏览器一致性

```workflow
1. 定义浏览器矩阵
   - Chromium（Chrome/Edge）
   - Firefox
   - WebKit（Safari）

2. 对每个浏览器执行：
   a. 配置浏览器
      - 在 MCP 服务器配置中设置

   b. 运行测试套件
      - 导航到各页面
      - 捕获快照
      - 截取截图
      - 测试交互

   c. 记录结果
      - 保存各浏览器专属截图
      - 记录渲染差异
      - 记录各浏览器特有的缺陷

3. 对比结果
   - 并排截图对比
   - 功能差异
   - 性能差异
   - CSS 渲染问题

4. 处理差异
   - 修复关键的跨浏览器缺陷
   - 记录可接受的差异
   - 必要时添加浏览器专属样式
```

### 模式 6：端到端用户旅程测试

**场景：** 完整用户工作流验证

```workflow
1. 开始旅程
   - 使用 browser_navigate 导航到落地页
   - 使用 browser_snapshot 获取初始状态
   - 截取起始点截图

2. 身份认证
   - 导航到登录页
   - 使用 browser_fill_form 填写凭据
   - 提交表单
   - 等待页面跳转
   - 截取登录成功状态截图

3. 主要工作流步骤
   对每个步骤：
   - 执行操作前获取快照
   - 执行用户操作
   - 等待完成
   - 操作后截取截图
   - 验证预期状态

4. 完成交易
   - 提交最终操作
   - 等待确认
   - 截取成功状态截图
   - 验证完成提示

5. 清理
   - 如有需要则退出登录
   - 截取最终状态截图
   - 记录旅程测试结果
```

### 模式 7：可访问性快照测试

**场景：** 验证语义结构和可访问性

```workflow
1. 导航到页面
   - 使用 browser_navigate 访问 URL

2. 捕获可访问性快照
   - 使用 browser_snapshot 获取语义树
   - 审查元素角色
   - 检查标题层级
   - 验证标签和描述

3. 验证结构
   - 正确的标题层级（h1 → h2 → h3）
   - 表单输入框有标签
   - 按钮有可访问名称
   - 交互元素有角色
   - ARIA 属性存在

4. 测试键盘导航
   - 使用 browser_press_key 按下 "Tab"
   - 每次 Tab 后获取快照
   - 验证焦点指示器
   - 确保逻辑上的 Tab 顺序
   - 测试跳过链接

5. 测试屏幕阅读器体验
   - 审查快照文本内容
   - 验证替代文本是否存在
   - 检查 ARIA 实时区域
   - 验证语义地标
   - 确保结构有意义

6. 记录发现
   - 截取可访问性树截图
   - 记录缺失的标签
   - 报告层级问题
   - 提出改进建议
```

## 浏览器自动化最佳实践

### 截图最佳实践

1. **一致的命名规范**
```
{页面}-{视口}-{状态}-{时间戳}.png

示例：
homepage-desktop-default-1634567890.png
login-mobile-error-1634567891.png
checkout-tablet-success-1634567892.png
```

2. **文件名组织**
```
screenshots/
  ├── baselines/
  │   ├── homepage-desktop.png
  │   ├── homepage-mobile.png
  │   └── homepage-tablet.png
  ├── current/
  │   └── homepage-desktop-20251017.png
  └── diffs/
      └── homepage-desktop-diff-20251017.png
```

3. **整页截图 vs 视口截图**
- 文档记录使用整页截图
- 回归测试使用视口截图
- 组件使用元素截图
- 整页截图时需考虑页面长度

4. **图片格式选择**
- PNG：UI 元素、文本、锐利边缘（无损）
- JPEG：照片、背景、大图（体积更小）
- 测试时默认使用 PNG

### 快照与截图策略

**使用快照的场景：**
- 自动化交互
- 测试功能
- 验证结构
- 检查可访问性
- 需要元素引用
- 测试动态内容

**使用截图的场景：**
- 视觉回归测试
- 文档记录
- 缺陷报告
- 设计评审
- 干系人演示
- 视觉对比

**两者都使用的场景：**
- 全面测试
- 调试视觉问题
- 创建测试报告
- 记录复杂流程

### 等待策略

1. **等待特定元素**
```javascript
// 推荐
browser_wait_for 使用 text: "Data loaded"

// 避免
browser_wait_for 使用 time: 5
```

2. **等待动画**
```javascript
// 等待加载指示器消失
browser_wait_for 使用 textGone: "Loading..."
```

3. **等待网络空闲**
```javascript
// 等待后检查网络请求
使用 browser_network_requests 验证完成
```

4. **动态内容**
```javascript
// 截图前等待特定文本出现
browser_wait_for 使用 text: "Results: 42 items"
```

### 交互可靠性

1. **始终先使用快照**
```workflow
1. browser_snapshot
2. 在快照中查找元素引用（ref）
3. 使用 ref 进行交互
4. 切勿猜测元素引用
```

2. **验证元素状态**
```javascript
// 获取快照验证元素是否存在
// 检查元素是否可见且可操作
// 然后执行交互
```

3. **处理动态元素**
```javascript
// 等待元素出现
browser_wait_for 使用 text: "Submit"
// 然后获取新的快照
browser_snapshot
// 获取更新的 ref 并进行交互
```

4. **错误恢复**
```javascript
// 如果交互失败：
1. 截取当前状态截图
2. 捕获控制台消息（browser_console_messages）
3. 检查网络请求（browser_network_requests）
4. 获取新快照查看当前状态
```

### 表单测试策略

1. **批量输入 vs 逐字段输入**
```javascript
// 简单表单使用批量输入（更快）
browser_fill_form 填写所有字段

// 复杂表单使用逐字段输入（更好的控制）
对每个字段使用 browser_type
每次输入后使用 browser_wait_for
验证验证规则是否触发
```

2. **验证测试**
```javascript
// 测试每条验证规则
1. 输入无效数据
2. 尝试提交
3. 获取快照查看错误
4. 截取错误信息截图
5. 修正数据
6. 验证错误已清除
```

3. **多步骤表单**
```javascript
// 记录每个步骤
1. 填写第 1 步
2. 提交前截取截图
3. 点击下一步
4. 等待第 2 步
5. 获取新状态快照
6. 对每个步骤重复操作
```

### 网络监控

1. **跟踪 API 调用**
```javascript
// 用户操作后
使用 browser_network_requests
// 验证预期的端点是否被调用
// 检查状态码
// 验证请求/响应数据
```

2. **性能测试**
```javascript
// 捕获网络时序
使用 browser_network_requests
// 分析：
- 请求数量
- 总传输大小
- 响应时间
- 失败的请求
```

3. **调试失败的请求**
```javascript
使用 browser_network_requests
// 查找失败的请求
// 检查错误信息
// 截取当前状态截图
// 查看控制台错误消息
```

## 开发加速策略

### 策略 1：创建测试模板

创建可复用的测试模式：

```template
视觉回归测试模板：
1. 导航：使用 browser_navigate 访问 {URL}
2. 等待：使用 browser_wait_for 等待 {条件}
3. 基线：使用 browser_take_screenshot "baseline-{name}.png"，fullPage: true
4. [进行修改]
5. 捕获：使用 browser_take_screenshot "current-{name}.png"，fullPage: true
6. 对比：[手动或自动化对比]
7. 记录：截取差异部分截图

响应式测试模板：
对每个视口 in [mobile, tablet, desktop]：
  1. 调整大小：使用 browser_resize 调整为 {视口尺寸}
  2. 导航：使用 browser_navigate 访问 {URL}
  3. 等待：使用 browser_wait_for 等待稳定
  4. 快照：使用 browser_snapshot
  5. 截图：使用 browser_take_screenshot "{page}-{viewport}.png"
  6. 验证：检查布局完整性

表单测试模板：
1. 导航：使用 browser_navigate 访问 {表单 URL}
2. 快照：使用 browser_snapshot 获取引用
3. 填写：使用 browser_fill_form 填入测试数据
4. 截图："form-filled.png"
5. 提交：使用 browser_click 点击提交按钮
6. 等待：使用 browser_wait_for 等待结果
7. 验证：获取结果快照并截图
8. 检查：使用 browser_network_requests 检查提交
```

### 策略 2：自动化截图组织

系统化地组织截图：

```organization
项目结构：
tests/
  visual/
    baselines/        # 参考截图
    results/          # 当前测试截图
    diffs/            # 差异图片
    reports/          # 带对比的 HTML 报告

命名规范：
{测试名称}_{视口}_{状态}_{日期}.png

示例：
login_desktop_default_20251017.png
cart_mobile_empty_20251017.png
checkout_tablet_error_20251017.png

元数据文件：
screenshot-metadata.json:
{
  "screenshot": "login_desktop_default_20251017.png",
  "timestamp": "2025-10-17T10:30:00Z",
  "url": "https://example.com/login",
  "viewport": {"width": 1920, "height": 1080},
  "browser": "chromium",
  "test": "login_flow",
  "passed": true
}
```

### 策略 3：并行多浏览器测试

高效地跨浏览器测试：

```strategy
浏览器矩阵：
- Chromium（最新版）
- Firefox（最新版）
- WebKit（最新版）

并行执行：
1. 定义测试套件
2. 配置各浏览器
3. 并行运行测试
4. 收集结果
5. 跨浏览器对比
6. 生成跨浏览器报告

结果组织：
screenshots/
  chromium/
    homepage.png
    login.png
  firefox/
    homepage.png
    login.png
  webkit/
    homepage.png
    login.png
  comparison/
    homepage-browsers.html
    login-browsers.html
```

### 策略 4：视觉回归自动化

自动化视觉对比工作流：

```automation
1. 捕获基线（一次性）：
   - 导航到各页面
   - 截取参考截图
   - 存储在 baselines/ 目录中

2. 运行视觉测试：
   - 导航到各页面
   - 截取当前截图
   - 存储在 results/ 目录中

3. 对比图片：
   - 逐像素对比
   - 高亮差异
   - 生成差异图片
   - 计算相似度分数

4. 生成报告：
   - 列出所有对比
   - 显示并排视图
   - 高亮失败项
   - 包含指标数据

5. 审查和更新：
   - 审查失败项
   - 接受有意为之的变更
   - 更新基线
   - 修复回归问题
```

### 策略 5：组件库测试

测试设计系统组件：

```strategy
组件测试套件：
对每个组件：
  1. 导航到组件页面
  2. 获取快照查看结构
  3. 测试每个变体：
     - 默认
     - 悬停
     - 激活
     - 禁用
     - 错误
  4. 截取每个状态的截图
  5. 验证可访问性
  6. 检查响应式行为

文档生成：
1. 捕获所有组件状态
2. 按组件组织
3. 生成视觉目录
4. 包含代码示例
5. 记录使用指南

示例：
components/
  Button/
    button-default.png
    button-hover.png
    button-active.png
    button-disabled.png
    button-error.png
  Input/
    input-default.png
    input-focus.png
    input-error.png
    input-disabled.png
```

## 故障排除

### 常见问题

**截图显示为空白**
- 等待页面加载完成：browser_wait_for
- 检查元素是否可见：browser_snapshot
- 确保页面已渲染完成：添加延迟
- 验证 URL 是否正确

**找不到要交互的元素**
- 获取新快照：browser_snapshot
- 检查元素引用是否仍有效
- 等待元素出现：browser_wait_for
- 验证元素是否存在于快照中

**浏览器无法启动**
- 运行 browser_install
- 检查 MCP 服务器配置
- 验证浏览器二进制文件路径
- 检查系统权限

**截图与预期不一致**
- 检查视口大小：browser_resize
- 等待动画完成：browser_wait_for
- 确保字体加载完成
- 禁用动态内容（时间戳、广告）

**表单提交失败**
- 验证所有必填字段已填写
- 检查验证错误：browser_snapshot
- 等待提交按钮变为可用
- 检查控制台中的 JavaScript 错误：browser_console_messages

**未捕获网络请求**
- 在操作后调用 browser_network_requests
- 确保页面请求已完成
- 检查请求是否失败
- 验证请求时序

**对话框未处理**
- 在触发前设置 browser_handle_dialog
- 适当选择接受或取消
- 为 prompt 对话框提供 promptText
- 提前测试对话框

### 调试工作流

1. **捕获当前状态**
```workflow
1. browser_snapshot - 查看页面结构
2. browser_take_screenshot - 查看视觉状态
3. browser_console_messages onlyErrors: true - 检查错误
4. browser_network_requests - 查看网络活动
```

2. **隔离问题**
```workflow
1. 将测试简化为最小复现步骤
2. 在单个浏览器中测试
3. 禁用动态内容
4. 移除可变元素
5. 逐步测试
```

3. **记录问题**
```workflow
1. 截取问题发生前的截图
2. 截取失败点的截图
3. 捕获控制台消息
4. 保存网络请求
5. 记录预期与实际结果的对比
6. 包含复现步骤
```

## 实用示例

### 示例 1：首页视觉回归

**测试首页未发生视觉变化：**

```test
1. 导航
   browser_navigate
   url: "https://example.com"

2. 等待页面加载
   browser_wait_for
   textGone: "Loading..."

3. 捕获基线
   browser_take_screenshot
   filename: "homepage-baseline.png"
   fullPage: true

4. [代码修改后，重复以上步骤]

5. 捕获当前状态
   browser_take_screenshot
   filename: "homepage-current.png"
   fullPage: true

6. 手动或使用工具对比图片
7. 记录差异
```

### 示例 2：登录表单测试

**测试登录表单功能：**

```test
1. 导航到登录页
   browser_navigate
   url: "https://example.com/login"

2. 获取表单结构
   browser_snapshot

3. 填写表单
   browser_fill_form
   fields: [
     {
       name: "Email",
       type: "textbox",
       ref: "123",
       value: "test@example.com"
     },
     {
       name: "Password",
       type: "textbox",
       ref: "456",
       value: "password123"
     }
   ]

4. 截取已填写的表单截图
   browser_take_screenshot
   filename: "login-filled.png"

5. 提交
   browser_click
   element: "Sign In button"
   ref: "789"

6. 等待跳转
   browser_wait_for
   text: "Welcome back"

7. 截取成功截图
   browser_take_screenshot
   filename: "login-success.png"

8. 验证网络请求
   browser_network_requests
```

### 示例 3：响应式设计检查

**测试响应式布局：**

```test
移动端：
1. 调整为移动端视口
   browser_resize
   width: 375
   height: 667

2. 导航
   browser_navigate
   url: "https://example.com"

3. 等待
   browser_wait_for
   time: 2

4. 截图
   browser_take_screenshot
   filename: "homepage-mobile.png"
   fullPage: true

平板端：
5. 调整为平板视口
   browser_resize
   width: 768
   height: 1024

6. 导航
   browser_navigate
   url: "https://example.com"

7. 截图
   browser_take_screenshot
   filename: "homepage-tablet.png"
   fullPage: true

桌面端：
8. 调整为桌面视口
   browser_resize
   width: 1920
   height: 1080

9. 导航
   browser_navigate
   url: "https://example.com"

10. 截图
    browser_take_screenshot
    filename: "homepage-desktop.png"
    fullPage: true
```

### 示例 4：组件状态测试

**测试按钮状态：**

```test
1. 导航至组件库
   browser_navigate
   url: "https://example.com/components/button"

2. 获取页面结构
   browser_snapshot

3. 默认状态
   browser_take_screenshot
   filename: "button-default.png"
   element: "主要按钮"
   ref: "123"

4. 悬停状态
   browser_hover
   element: "主要按钮"
   ref: "123"

   browser_take_screenshot
   filename: "button-hover.png"
   element: "主要按钮"
   ref: "123"

5. 激活状态
   browser_click
   element: "主要按钮"
   ref: "123"

   browser_take_screenshot
   filename: "button-active.png"
   element: "主要按钮"
   ref: "123"

6. 验证快照
   browser_snapshot
```

### 示例 5：端到端结账流程

**测试完整结账过程：**

```test
1. 导航至商品
   browser_navigate
   url: "https://example.com/products/item-123"

2. 添加到购物车
   browser_snapshot

   browser_click
   element: "添加到购物车按钮"
   ref: "456"

   browser_wait_for
   text: "已添加到购物车"

3. 进入购物车
   browser_click
   element: "购物车图标"
   ref: "789"

   browser_take_screenshot
   filename: "含商品的购物车.png"

4. 结账
   browser_click
   element: "结账按钮"
   ref: "101"

5. 填写配送信息
   browser_snapshot

   browser_fill_form
   fields: [
     {name: "姓名", type: "textbox", ref: "111", value: "John Doe"},
     {name: "地址", type: "textbox", ref: "222", value: "123 Main St"},
     {name: "城市", type: "textbox", ref: "333", value: "New York"},
     {name: "邮编", type: "textbox", ref: "444", value: "10001"}
   ]

6. 结账截图
   browser_take_screenshot
   filename: "已填写结账.png"
   fullPage: true

7. 完成订单
   browser_click
   element: "提交订单按钮"
   ref: "555"

   browser_wait_for
   text: "订单确认"

8. 确认截图
   browser_take_screenshot
   filename: "订单确认.png"
   fullPage: true

9. 验证网络请求
   browser_network_requests
```

### 示例 6：可访问性测试

**测试键盘导航和结构：**

```test
1. 导航至页面
   browser_navigate
   url: "https://example.com/form"

2. 捕获语义结构
   browser_snapshot

3. 验证标题层级
   - 检查 h1 → h2 → h3 顺序
   - 确保单个 h1
   - 验证逻辑结构

4. 测试键盘导航
   browser_press_key
   key: "Tab"

   browser_snapshot

   browser_take_screenshot
   filename: "焦点字段-1.png"

5. 继续按 Tab
   browser_press_key
   key: "Tab"

   browser_snapshot

   browser_take_screenshot
   filename: "焦点字段-2.png"

6. 验证所有交互元素可访问
   - 按钮
   - 链接
   - 表单字段
   - 自定义组件

7. 检查 ARIA 标签
   - 表单标签存在
   - 按钮标签描述性
   - 错误消息被播报
   - 状态更新实时

8. 截图可访问性树
   browser_take_screenshot
   filename: "可访问性结构.png"
```

### 示例 7：网络调试

**调试失败的 API 调用：**

```test
1. 导航至页面
   browser_navigate
   url: "https://example.com/dashboard"

2. 等待页面
   browser_wait_for
   time: 3

3. 检查控制台错误
   browser_console_messages
   onlyErrors: true

4. 检查网络请求
   browser_network_requests

5. 查找失败请求
   - 状态：4xx 或 5xx
   - 超时错误
   - CORS 问题

6. 截图错误状态
   browser_take_screenshot
   filename: "api错误状态.png"

7. 重试操作
   browser_click
   element: "刷新按钮"
   ref: "123"

8. 监控新请求
   browser_network_requests

9. 记录发现
   - 失败端点
   - 错误消息
   - 请求/响应数据
   - 截图
```

### 示例 8：对话框处理

**测试确认对话框：**

```test
1. 导航至页面
   browser_navigate
   url: "https://example.com/settings"

2. 触发删除操作
   browser_snapshot

   browser_click
   element: "删除账户按钮"
   ref: "123"

3. 处理确认
   browser_handle_dialog
   accept: false  # 第一次取消

4. 验证仍在页面
   browser_snapshot

5. 再次尝试
   browser_click
   element: "删除账户按钮"
   ref: "123"

6. 这次确认
   browser_handle_dialog
   accept: true

7. 等待结果
   browser_wait_for
   text: "账户已删除"

8. 截图确认
   browser_take_screenshot
   filename: "账户已删除.png"
```

### 示例 9：标签管理

**测试多标签工作流：**

```test
1. 列出当前标签
   browser_tabs
   action: "list"

2. 在新标签打开链接
   browser_click
   element: "隐私政策链接"
   ref: "123"
   modifiers: ["ControlOrMeta"]

3. 切换到新标签
   browser_tabs
   action: "select"
   index: 1

4. 截图新标签
   browser_take_screenshot
   filename: "隐私政策.png"

5. 切换回
   browser_tabs
   action: "select"
   index: 0

6. 关闭额外标签
   browser_tabs
   action: "close"
   index: 1

7. 验证单个标签
   browser_tabs
   action: "list"
```

### 示例 10：动画测试

**测试加载动画：**

```test
1. 导航至页面
   browser_navigate
   url: "https://example.com/data-heavy"

2. 截图加载状态
   browser_take_screenshot
   filename: "加载转圈.png"

3. 等待加载完成
   browser_wait_for
   textGone: "加载中..."

4. 等待动画
   browser_wait_for
   time: 1

5. 截图最终状态
   browser_take_screenshot
   filename: "内容加载.png"
   fullPage: true

6. 验证稳定性
   browser_wait_for
   time: 2

   browser_take_screenshot
   filename: "稳定状态.png"
   fullPage: true

7. 对比截图
   - loading-spinner.png
   - content-loaded.png
   - stable-state.png
```

## 快速参考

### 基本命令

```
导航：
  browser_navigate url: "{URL}"

截图：
  browser_snapshot

截图：
  browser_take_screenshot filename: "{name}.png"

全页截图：
  browser_take_screenshot filename: "{name}.png", fullPage: true

元素截图：
  browser_take_screenshot filename: "{name}.png", element: "{描述}", ref: "{ref}"

点击：
  browser_click element: "{描述}", ref: "{ref}"

输入：
  browser_type element: "{描述}", ref: "{ref}", text: "{文本}"

填写表单：
  browser_fill_form fields: [{name, type, ref, value}, ...]

等待：
  browser_wait_for text: "{文本}"
  browser_wait_for textGone: "{文本}"
  browser_wait_for time: {秒数}

调整大小：
  browser_resize width: {宽度}, height: {高度}

控制台：
  browser_console_messages onlyErrors: true

网络：
  browser_network_requests
```

### 常见视口尺寸

```
手机：
  375 x 667   (iPhone SE)
  390 x 844   (iPhone 12/13/14)
  414 x 896   (iPhone 11 Pro Max)
  360 x 640   (安卓小屏)
  412 x 915   (安卓大屏)

平板：
  768 x 1024  (iPad 竖屏)
  1024 x 768  (iPad 横屏)
  810 x 1080  (安卓平板)

桌面：
  1280 x 720  (高清)
  1366 x 768  (笔记本电脑)
  1920 x 1080 (全高清)
  2560 x 1440 (2K)
  3840 x 2160 (4K)
```

### 测试组织模板

```
tests/
  ├── visual/
  │   ├── baselines/
  │   ├── results/
  │   └── diffs/
  ├── e2e/
  │   ├── auth/
  │   ├── checkout/
  │   └── navigation/
  ├── responsive/
  │   ├── mobile/
  │   ├── tablet/
  │   └── desktop/
  └── components/
      ├── buttons/
      ├── forms/
      └── navigation/

reports/
  ├── visual-regression.html
  ├── cross-browser.html
  └── accessibility.html
```

## 资源

- [Playwright 文档](https://playwright.dev)
- [Playwright API 参考](https://playwright.dev/docs/api/class-playwright)
- [Playwright MCP 服务器](https://github.com/microsoft/playwright-mcp)
- [视觉测试指南](https://playwright.dev/docs/test-snapshots)
- [最佳实践](https://playwright.dev/docs/best-practices)
- [可访问性测试](https://playwright.dev/docs/accessibility-testing)

---

**技能版本**: 1.0.0
**最后更新**: 2025年10月
**技能分类**: 浏览器自动化、视觉测试、质量保证
**兼容**: Playwright MCP 服务器、Chromium、Firefox、WebKit
