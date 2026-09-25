# 屏幕阅读器测试

测试网站应用使用屏幕阅读器的实用指南，用于全面进行无障碍性验证。

## 使用此技能的场景

- 验证屏幕阅读器兼容性
- 测试ARIA实现
- 调试辅助技术问题
- 验证表单无障碍性
- 测试动态内容通知
- 确保导航无障碍性

## 核心概念

### 1. 主要屏幕阅读器

| 屏幕阅读器 | 平台   | 浏览器   | 使用率 |
| ---------- | ------ | ------- | ----- |
| **VoiceOver** | macOS/iOS | Safari  | ~15%  |
| **NVDA**    | Windows | Firefox/Chrome | ~31%  |
| **JAWS**    | Windows | Chrome/IE | ~40%  |
| **TalkBack** | Android | Chrome  | ~10%  |
| **Narrator** | Windows | Edge    | ~4%   |

### 2. 测试优先级

```
最低覆盖率：
1. NVDA + Firefox (Windows)
2. VoiceOver + Safari (macOS)
3. VoiceOver + Safari (iOS)

全面覆盖率：
+ JAWS + Chrome (Windows)
+ TalkBack + Chrome (Android)
+ Narrator + Edge (Windows)
```

### 3. 屏幕阅读器模式

| 模式         | 目的               | 使用场景         |
| ------------ | ------------------ | ---------------- |
| **浏览/虚拟** | 读取内容           | 默认阅读         |
| **焦点/表单** | 与控件交互         | 填写表单         |
| **应用**     | 自定义小部件       | ARIA应用         |

## VoiceOver (macOS)

### 设置

```
启用：系统偏好设置 → 辅助功能 → VoiceOver
切换：Cmd + F5
快速切换：三击Touch ID
```

### 基本命令

```
导航：
VO = Ctrl + Option (VoiceOver修饰键)

VO + 右箭头   下一个元素
VO + 左箭头    上一个元素
VO + Shift + 下  进入组
VO + Shift + 上    退出组

阅读：
VO + A             从光标处朗读全部
Ctrl               停止说话
VO + B             朗读当前段落

交互：
VO + 空格         激活元素
VO + Shift + M     打开菜单
Tab                下一个可聚焦元素
Shift + Tab        上一个可聚焦元素

转子 (VO + U)：
通过：标题、链接、表单、地标
左/右箭头   切换转子类别
上/下箭头    在类别内导航
Enter              跳转到项目

特定于网页：
VO + Cmd + H       下一个标题
VO + Cmd + J       下一个表单控件
VO + Cmd + L       下一个链接
VO + Cmd + T       下一个表格
```

### 测试清单

```markdown
## VoiceOver测试清单

### 页面加载

- [ ] 页面标题被宣布
- [ ] 主要地标被找到
- [ ] 跳过链接有效

### 导航

- [ ] 所有标题可通过转子发现
- [ ] 标题级别逻辑 (H1 → H2 → H3)
- [ ] 地标正确标记
- [ ] 跳过链接有效

### 链接和按钮

- [ ] 链接目的清晰
- [ ] 按钮操作被描述
- [ ] 新窗口/标签页被宣布

### 表单

- [ ] 所有标签与输入关联
- [ ] 必填字段被宣布
- [ ] 错误消息被读取
- [ ] 指令可用
- [ ] 焦点移动到错误

### 动态内容

- [ ] 提示立即宣布
- [ ] 加载状态被传达
- [ ] 内容更新被宣布
- [ ] 模态正确捕获焦点

### 表格

- [ ] 表头与单元格关联
- [ ] 表格导航有效
- [ ] 复杂表格有标题
```

### 常见问题及修复

```html
<!-- 问题：按钮未宣布目的 -->
<button><svg>...</svg></button>

<!-- 修复 -->
<button aria-label="关闭对话框"><svg aria-hidden="true">...</svg></button>

<!-- 问题：动态内容未宣布 -->
<div id="results">新结果已加载</div>

<!-- 修复 -->
<div id="results" role="status" aria-live="polite">新结果已加载</div>

<!-- 问题：表单错误未被读取 -->
<input type="email" />
<span class="error">无效的邮箱</span>

<!-- 修复 -->
<input type="email" aria-invalid="true" aria-describedby="email-error" />
<span id="email-error" role="alert">无效的邮箱</span>
```

## NVDA (Windows)

### 设置

```
下载：nvaccess.org
启动：Ctrl + Alt + N
停止：Insert + Q
```

### 基本命令

```
导航：
Insert = NVDA修饰键

下箭头         下一行
上箭头          上一行
Tab              下一个可聚焦
Shift + Tab        上一个可聚焦

阅读：
NVDA + 下箭头  朗读全部
Ctrl              停止说话
NVDA + 上箭头    当前行

标题：
H                  下一个标题
Shift + H          上一个标题
1-6                标题级别1-6

表单：
F                  下一个表单字段
B                  下一个按钮
E                  下一个编辑字段
X                  下一个复选框
C                  下一个组合框

链接：
K                  下一个链接
U                  下一个未访问的链接
V                  下一个已访问的链接

地标：
D                  下一个地标
Shift + D          上一个地标

表格：
T                  下一个表格
Ctrl + Alt + 箭头  在单元格间导航

元素列表 (NVDA + F7)：
显示所有链接、标题、表单字段、地标
```

### 浏览与焦点模式

```
NVDA自动切换模式：
- 浏览模式：箭头键导航内容
- 焦点模式：箭头键控制交互元素

手动切换：NVDA + 空格

注意：
- 导航时宣布"浏览模式"
- 进入表单字段时宣布"焦点模式"
- 应用角色强制表单模式
```

### 测试脚本

```markdown
## NVDA测试脚本

### 初始加载

1. 导航到页面
2. 等待页面加载完成
3. 按 Insert + 下箭头读取全部
4. 注意：页面标题、主要内容是否被识别？

### 地标导航

1. 重复按D
2. 检查：所有主要区域是否可达？
3. 检查：地标是否正确标记？

### 标题导航

1. 按 Insert + F7 → 标题
2. 检查：逻辑标题结构？
3. 按 H 导航标题
4. 检查：所有章节是否可发现？

### 表单测试

1. 按 F 找到第一个表单字段
2. 检查：标签是否被读取？
3. 填写无效数据
4. 提交表单
5. 检查：错误是否被宣布？
6. 检查：焦点是否移动到错误？

### 交互元素

1. Tab遍历所有交互元素
2. 检查：每个元素是否宣布角色和状态
3. 使用Enter/Space激活按钮
4. 检查：结果是否被宣布？

### 动态内容

1. 触发内容更新
2. 检查：变化是否被宣布？
3. 打开模态
4. 检查：焦点是否正确捕获？
5. 关闭模态
6. 检查：焦点是否返回？
```

## JAWS (Windows)

### 基本命令

```
启动：桌面快捷方式或 Ctrl + Alt + J
虚拟光标：浏览器中自动启用

导航：
箭头键         导航内容
Tab              下一个可聚焦
Insert + 下箭头  朗读全部
Ctrl              停止说话

快速键：
H                  下一个标题
T                  下一个表格
F                  下一个表单字段
B                  下一个按钮
G                  下一个图形
L                  下一个列表
;                  下一个地标

表单模式：
Enter              进入表单模式
Numpad +           退出表单模式
F5                 列出表单字段

列表：
Insert + F7        链接列表
Insert + F6        标题列表
Insert + F5        表单字段列表

表格：
Ctrl + Alt + 箭头  表格导航
```

## TalkBack (Android)

### 设置

```
启用：设置 → 辅助功能 → TalkBack
切换：同时按住两个音量按钮3秒
```

### 手势

```
探索：在屏幕上拖动手指
下一个：向右滑动
上一个：向左滑动
激活：双击
滚动：双指滑动

阅读控制 (向上滑动然后向右)：
- 标题
- 链接
- 控件
- 字符
- 单词
- 行
- 段落
```

## 常见测试场景

### 1. 模态对话框

```html
<!-- 无障碍模态结构 -->
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-desc"
>
  <h2 id="dialog-title">确认删除</h2>
  <p id="dialog-desc">此操作无法撤销。</p>
  <button>取消</button>
  <button>删除</button>
</div>
```

```javascript
// 焦点管理
function openModal(modal) {
  // 保存最后聚焦的元素
  lastFocus = document.activeElement;

  // 聚焦到模态
  modal.querySelector("h2").focus();

  // 捕获焦点
  modal.addEventListener("keydown", trapFocus);
}

function closeModal(modal) {
  // 返回焦点
  lastFocus.focus();
}

function trapFocus(e) {
  if (e.key === "Tab") {
    const focusable = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      last.focus();
      e.preventDefault();
    } else if (!e.shiftKey && document.activeElement === last) {
      first.focus();
      e.preventDefault();
    }
  }

  if (e.key === "Escape") {
    closeModal(modal);
  }
}
```

### 2. Live Regions

```html
<!-- 状态消息 (礼貌) -->
<div role="status" aria-live="polite" aria-atomic="true">
  <!-- 内容更新将在当前语音后宣布 -->
</div>

<!-- 警报 (断言) -->
<div role="alert" aria-live="assertive">
  <!-- 内容更新将中断当前语音 -->
</div>

<!-- 进度更新 -->
<div
  role="progressbar"
  aria-valuenow="75"
  aria-valuemin="0"
  aria-valuemax="100"
  aria-label="上传进度"
></div>

<!-- 日志 (仅添加) -->
<div role="log" aria-live="polite" aria-relevant="additions">
  <!-- 新消息将被宣布，移除不会 -->
</div>
```

### 3. Tab界面

```html
<div role="tablist" aria-label="产品信息">
  <button role="tab" id="tab-1" aria-selected="true" aria-controls="panel-1">
    描述
  </button>
  <button
    role="tab"
    id="tab-2"
    aria-selected="false"
    aria-controls="panel-2"
    tabindex="-1"
  >
    评论
  </button>
</div>

<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
  产品描述内容...
</div>

<div role="tabpanel" id="panel-2" aria-labelledby="tab-2" hidden>
  评论内容...
</div>
```

```javascript
// Tab键盘导航
tablist.addEventListener("keydown", (e) => {
  const tabs = [...tablist.querySelectorAll('[role="tab"]')];
  const index = tabs.indexOf(document.activeElement);

  let newIndex;
  switch (e.key) {
    case "ArrowRight":
      newIndex = (index + 1) % tabs.length;
      break;
    case "ArrowLeft":
      newIndex = (index - 1 + tabs.length) % tabs.length;
      break;
    case "Home":
      newIndex = 0;
      break;
    case "End":
      newIndex = tabs.length - 1;
      break;
    default:
      return;
  }

  tabs[newIndex].focus();
  activateTab(tabs[newIndex]);
  e.preventDefault();
});
```

## 调试技巧

```javascript
// 记录屏幕阅读器看到的内容
function logAccessibleName(element) {
  const computed = window.getComputedStyle(element);
  console.log({
    role: element.getAttribute("role") || element.tagName,
    name:
      element.getAttribute("aria-label") ||
      element.getAttribute("aria-labelledby") ||
      element.textContent,
    state: {
      expanded: element.getAttribute("aria-expanded"),
      selected: element.getAttribute("aria-selected"),
      checked: element.getAttribute("aria-checked"),
      disabled: element.disabled,
    },
    visible: computed.display !== "none" && computed.visibility !== "hidden",
  });
}
```

## 最佳实践

### 应做

- **使用实际屏幕阅读器测试** - 而不是仅使用模拟器
- **优先使用语义HTML** - ARIA是补充
- **在浏览和焦点模式中测试** - 不同的体验
- **验证焦点管理** - 特别是对于SPAs
- **先仅使用键盘测试** - 为屏幕阅读器测试打下基础

### 不应做

- **不要假设一个屏幕阅读器就足够** - 测试多个
- **不要忽略移动设备** - 用户群正在增长
- **不要仅测试成功路径** - 测试错误状态
- **不要跳过动态内容** - 最常见的问题
- **不要依赖视觉测试** - 体验不同
