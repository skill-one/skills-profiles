# Rust 每日报告

> **版本:** 2.1.0 | **最后更新:** 2025-01-27

获取 Rust 社区更新，并按时间范围进行筛选。

## 数据来源

| 类别 | 来源 |
|------|------|
| 生态系统 | Reddit r/rust, This Week in Rust |
| 官方 | blog.rust-lang.org, Inside Rust |
| 基金会 | rustfoundation.org (新闻、博客、活动) |

## 参数

- `time_range`: day | week | month (默认: week)
- `category`: all | ecosystem | official | foundation

## 执行模式检测

**关键：首先检查代理文件是否存在，以确定执行模式。**

尝试读取：`../../agents/rust-daily-reporter.md`

---

## 代理模式（插件安装）

**当 `../../agents/rust-daily-reporter.md` 存在时：**

### 工作流程

```
1. 读取: ../../agents/rust-daily-reporter.md
2. 任务(subagent_type: "general-purpose", run_in_background: false, prompt: <代理内容>)
3. 等待结果
4. 格式化并展示给用户
```

---

## 内联模式（仅技能安装）

**当代理文件不存在时，直接执行每个来源：**

### 1. Reddit r/rust

```bash
# 使用 agent-browser CLI
agent-browser open "https://www.reddit.com/r/rust/hot/"
agent-browser get text ".Post" --limit 10
agent-browser close
```

**或使用 WebFetch 降级：**
```
WebFetch("https://www.reddit.com/r/rust/hot/", "提取前 10 篇帖子及其分数和标题")
```

**解析输出为：**
| 分数 | 标题 | 链接 |
|------|------|------|

### 2. This Week in Rust

```bash
# 首先检查 actionbook
mcp__actionbook__search_actions("this week in rust")
mcp__actionbook__get_action_by_id(<action_id>)

# 然后获取
agent-browser open "https://this-week-in-rust.org/"
agent-browser get text "<从 actionbook 获取的选择器>"
agent-browser close
```

**解析输出为：**
- Issue #{number} ({date}): 精华

### 3. Rust 博客（官方）

```bash
agent-browser open "https://blog.rust-lang.org/"
agent-browser get text "article" --limit 5
agent-browser close
```

**或使用 WebFetch 降级：**
```
WebFetch("https://blog.rust-lang.org/", "提取最新 5 篇博客文章及其日期和标题")
```

**解析输出为：**
| 日期 | 标题 | 摘要 |
|------|------|------|

### 4. Inside Rust

```bash
agent-browser open "https://blog.rust-lang.org/inside-rust/"
agent-browser get text "article" --limit 3
agent-browser close
```

**或使用 WebFetch 降级：**
```
WebFetch("https://blog.rust-lang.org/inside-rust/", "提取最新 3 篇文章及其日期和标题")
```

### 5. Rust 基金会

```bash
# 新闻
agent-browser open "https://rustfoundation.org/media/category/news/"
agent-browser get text "article" --limit 3
agent-browser close

# 博客
agent-browser open "https://rustfoundation.org/media/category/blog/"
agent-browser get text "article" --limit 3
agent-browser close

# 活动
agent-browser open "https://rustfoundation.org/events/"
agent-browser get text "article" --limit 3
agent-browser close
```

### 时间筛选

获取所有来源后，按时间范围筛选：

| 范围 | 筛选 |
|------|------|
| day | 过去 24 小时 |
| week | 过去 7 天 |
| month | 过去 30 天 |

### 结果合并

获取所有来源后，合并为以下输出格式。

---

## 工具链优先级

两种模式都使用相同的工具链顺序：

1. **actionbook MCP** - 首先检查缓存的预获取内容
   ```
   mcp__actionbook__search_actions("rust news {date}")
   mcp__actionbook__search_actions("this week in rust")
   mcp__actionbook__search_actions("rust blog")
   ```

2. **agent-browser CLI** - 用于动态网页内容
   ```bash
   agent-browser open "<url>"
   agent-browser get text "<选择器>"
   agent-browser close
   ```

3. **WebFetch** - 如果 agent-browser 不可用时的降级方案

| 来源 | 主要工具 | 降级方案 |
|------|----------|----------|
| Reddit | agent-browser | WebFetch |
| TWIR | actionbook → agent-browser | WebFetch |
| Rust 博客 | actionbook → WebFetch | - |
| 基金会 | actionbook → WebFetch | - |

**禁止使用：**
- 直接使用 Chrome MCP
- 使用 WebSearch 获取新闻页面

---

## 输出格式

```markdown
# Rust {Weekly|Daily|Monthly} Report

**时间范围:** {start} - {end}

## 生态系统

### Reddit r/rust
| 分数 | 标题 | 链接 |
|------|------|------|
| {score} | {title} | [link]({url}) |

### This Week in Rust
- Issue #{number} ({date}): 精华

## 官方
| 日期 | 标题 | 摘要 |
|------|------|------|
| {date} | {title} | {summary} |

## 基金会
| 日期 | 标题 | 摘要 |
|------|------|------|
| {date} | {title} | {summary} |
```

---

## 验证

- 每个来源应至少有 1 个结果，否则标记为 "无更新"
- 获取失败时，使用替代工具重试
- 如果所有工具对某个来源都失败，则报告原因

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 代理文件未找到 | 仅技能安装 | 使用内联模式 |
| agent-browser 不可用 | CLI 未安装 | 使用 WebFetch |
| 网站超时 | 网络问题 | 重试一次，然后跳过该来源 |
| 空结果 | 选择器不匹配 | 报告并使用降级方案 |
