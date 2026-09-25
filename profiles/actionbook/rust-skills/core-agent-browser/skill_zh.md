# 使用 agent-browser 进行浏览器自动化

## 优先级提示

获取 Rust/crate 信息时，请按以下优先级顺序操作：
1. **rust-learner 技能** - 协调 actionbook + browser-fetcher
2. **actionbook MCP** - 针对已知网站的预计算选择器
3. **agent-browser CLI** - 直接浏览器自动化（最后手段）

仅当以下情况时才直接使用 agent-browser：
- actionbook 没有针对目标网站预计算的选择器
- 您需要交互式浏览器测试/自动化
- 您需要截图或表单填写

## 快速入门

```bash
agent-browser open <url>        # 导航到页面
agent-browser snapshot -i       # 获取带引用的交互元素
agent-browser click @e1         # 通过引用点击元素
agent-browser fill @e2 "text"   # 通过引用填充输入
agent-browser close             # 关闭浏览器
```

## 核心工作流程

1. 导航：`agent-browser open <url>`
2. 截图：`agent-browser snapshot -i`（返回带引用的元素，如 `@e1`、`@e2`）
3. 使用截图中的引用进行交互
4. 在导航后或 DOM 发生重大变化后重新截图

## 命令

### 导航
```bash
agent-browser open <url>      # 导航到 URL
agent-browser back            # 后退
agent-browser forward         # 前进
agent-browser reload          # 重新加载页面
agent-browser close           # 关闭浏览器
```

### 截图（页面分析）
```bash
agent-browser snapshot        # 完整的可访问性树
agent-browser snapshot -i     # 仅交互元素（推荐）
agent-browser snapshot -c     # 紧凑输出
agent-browser snapshot -d 3   # 限制深度为 3
```

### 交互（使用截图中的 @引用）
```bash
agent-browser click @e1           # 点击
agent-browser dblclick @e1        # 双击
agent-browser fill @e2 "text"     # 清空并输入
agent-browser type @e2 "text"     # 输入但不清空
agent-browser press Enter         # 按键
agent-browser press Control+a     # 组合键
agent-browser hover @e1           # 悬停
agent-browser check @e1           # 勾选复选框
agent-browser uncheck @e1         # 取消勾选复选框
agent-browser select @e1 "value"  # 选择下拉菜单
agent-browser scroll down 500     # 滚动页面
agent-browser scrollintoview @e1  # 将元素滚动到视图中
```

### 获取信息
```bash
agent-browser get text @e1        # 获取元素文本
agent-browser get value @e1       # 获取输入值
agent-browser get title           # 获取页面标题
agent-browser get url             # 获取当前 URL
```

### 截图
```bash
agent-browser screenshot          # 输出到标准输出
agent-browser screenshot path.png # 保存到文件
agent-browser screenshot --full   # 全页截图
```

### 等待
```bash
agent-browser wait @e1                     # 等待元素
agent-browser wait 2000                    # 等待毫秒
agent-browser wait --text "Success"        # 等待文本
agent-browser wait --load networkidle      # 等待网络空闲
```

### 语义定位器（引用的替代方案）
```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
```

## 示例：表单提交

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# 输出显示：文本框 "Email" [ref=e1]、文本框 "Password" [ref=e2]、按钮 "Submit" [ref=e3]

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i  # 检查结果
```
