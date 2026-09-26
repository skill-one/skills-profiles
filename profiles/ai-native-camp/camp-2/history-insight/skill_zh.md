# 历史洞察

分析 Claude Code 会话历史并提取洞察。

---

## 数据位置

```
~/.claude/projects/<encoded-cwd>/*.jsonl
```

**路径编码：** `/Users/foo/project` → `-Users-foo-project`

> 详细文件格式：`${baseDir}/references/session-file-format.md`

---

## 执行算法

### 第1步：确定范围 [必填]

**范围确定：**

1. **已明确指定** (可省略 AskUserQuestion):
   - "仅当前项目" / "此项目" → `current_project`
   - "所有会话" / "全部" → `all_sessions`

2. **未明确指定** - 调用 AskUserQuestion:
   ```
   question: "请选择会话搜索范围"
   options:
     - "仅当前项目" → ~/.claude/projects/<encoded-cwd>/*.jsonl
     - "所有 Claude Code 会话" → ~/.claude/projects/**/*.jsonl
   ```

---

### 第2步：查找会话文件

```bash
# 仅当前项目
find ~/.claude/projects/<encoded-cwd> -name "*.jsonl" -type f

# 所有会话 (所有项目)
find ~/.claude/projects -name "*.jsonl" -type f
```

**日期过滤**：检查文件的 mtime(修改时间) 后过滤。不同操作系统 `stat` 选项不同：
- macOS: `stat -f "%Sm" -t "%Y-%m-%d" <file>`
- Linux: `stat -c "%y" <file>`

---

### 第3步：处理会话

#### 决策树

```
找到会话文件？
├─ 否 → 错误："未找到会话"
└─ 是 → 文件数量多少？
    ├─ 1-3 个文件 → 直接读取 + 解析
    └─ 4+ 个文件 → 批量提取流程
```

#### 1-3 个文件

直接读取 JSONL 解析。文件过大(≥5000 tokens)时使用 `extract-session.sh`:
```bash
${baseDir}/scripts/extract-session.sh <session.jsonl>
```

#### 4+ 个文件：批量提取流程

1. 创建缓存目录 (`/tmp/cc-cache/<analysis-name>/`)
2. 保存会话列表 (`sessions.txt`)
3. 使用 jq 批量提取消息 (`user_messages.txt`)
4. 整理及过滤 (`clean_messages.txt`)
5. 使用 Task(opus) 进行综合分析

#### 文件过大时的并行批量分析

当 `clean_messages.txt` 过大导致读取失败时：

1. **文件分割**:
   ```bash
   split -l 2000 clean_messages.txt /tmp/cc-cache/<name>/batch_
   ```

2. **并行 Task(opus) 调用**:
   ```
   Task(subagent_type="general-purpose", model="opus", run_in_background=true)
   prompt: "读取 batch_XX 文件并总结主题/模式"
   ```

3. **结果合并**：使用 Task(opus) 进行综合

---

### 第4步：报告结果

```markdown
## 会话捕获完成

- **会话数量：** N 个文件处理
- **消息数量：** X 总数，Y 过滤后

### 提取的洞察
[分析结果]
```

---

## 错误处理

| 场景 | 响应 |
|------|------|
| 未找到会话文件 | "此项目未找到会话文件。" |
| 文件过大 | 自动使用 extract-session.sh 预处理 |
| jq 未安装 | "错误：需要 jq。使用 brew install jq 安装" |
| Task 失败 | "警告：无法处理 [文件]。跳过。" |
| 0 个相关会话 | "没有会话符合您的标准。" |

---

## 安全注意事项

- 禁止在输出中暴露完整路径 (`~` 前缀)

---

## 相关资源

- **`${baseDir}/scripts/extract-session.sh`** - JSONL 压缩 (移除 thinking, tool_use)
- **`${baseDir}/references/session-file-format.md`** - JSONL 结构及解析
