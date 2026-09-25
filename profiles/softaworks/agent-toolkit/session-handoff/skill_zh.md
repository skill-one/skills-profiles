# 交接

创建全面的交接文档，使新的 AI 代理能够无缝地继续工作，消除任何模糊性。解决长期存在的代理上下文耗尽问题。

## 模式选择

确定适用哪种模式：

**创建交接文档？** 用户希望保存当前状态、暂停工作或上下文已满。
- 跟随：下方的 CREATE 工作流

**从交接中恢复？** 用户希望继续之前的工作、加载上下文或提及现有的交接文档。
- 跟随：下方的 RESUME 工作流

**主动建议？** 在完成大量工作（5+ 文件编辑、复杂调试、重大决策）后，建议：
> "我们取得了显著进展。考虑创建一个交接文档以保存此上下文供未来会话使用。准备好时请说 'create handoff'。"

## CREATE 工作流

### 第 1 步：生成框架

运行智能框架脚本以创建预填充的交接文档：

```bash
python scripts/create_handoff.py [task-slug]
```

示例：`python scripts/create_handoff.py implementing-user-auth`

**对于延续性交接文档**（链接到之前的工作）：
```bash
python scripts/create_handoff.py "auth-part-2" --continues-from 2024-01-15-auth.md
```

该脚本将：
- 如有需要，创建 `.claude/handoffs/` 目录
- 生成带时间戳的文件名
- 预填充：时间戳、项目路径、git 分支、最近提交、修改文件
- 如有需要，添加交接链链接
- 输出用于编辑的文件路径

### 第 2 步：完成交接文档

打开生成的文件并填写所有 `[TODO: ...]` 部分。优先处理这些部分：

1. **当前状态摘要** - 当前正在发生什么
2. **重要上下文** - 下一个代理必须知道的临界信息
3. **立即下一步行动** - 清晰、可执行的第一步
4. **已做出的决策** - 带有理由的选择（而不仅仅是结果）

参考 [references/handoff-template.md](references/handoff-template.md) 中的模板结构以获取指导。

### 第 3 步：验证交接文档

运行验证脚本以检查完整性和安全性：

```bash
python scripts/validate_handoff.py <handoff-file>
```

验证器检查：
- [ ] 仍有 `[TODO: ...]` 占位符
- [ ] 必要部分存在且已填充
- [ ] 未检测到潜在的秘密（API 密钥、密码、令牌）
- [ ] 引用的文件存在
- [ ] 质量分数（0-100）

**不要最终确定包含秘密或分数低于 70 的交接文档。**

### 第 4 步：确认交接

向用户报告：
- 交接文件位置
- 验证分数和任何警告
- 捕获上下文的摘要
- 下一个会话的第一个行动项

## RESUME 工作流

### 第 1 步：查找可用的交接文档

列出当前项目中的交接文档：

```bash
python scripts/list_handoffs.py
```

这将显示所有交接文档的日期、标题和完成状态。

### 第 2 步：检查陈旧性

在加载之前，检查交接文档的时效性：

```bash
python scripts/check_staleness.py <handoff-file>
```

陈旧性级别：
- **FRESH**：安全继续 - 自交接以来变化最小
- **SLIGHTLY_STALE**：审查变更后继续
- **STALE**：在继续前仔细验证上下文
- **VERY_STALE**：考虑创建新的交接文档

该脚本检查：
- 创建交接文档以来的时间
- 自交接以来的 git 提交
- 自交接以来更改的文件
- 分支分歧
- 缺失引用文件

### 第 3 步：加载交接文档

在采取任何行动之前，完整阅读相关的交接文档。

如果交接文档是链的一部分（具有 "Continues from" 链接），也请阅读链接的前一个交接文档以获取完整上下文。

### 第 4 步：验证上下文

遵循 [references/resume-checklist.md](references/resume-checklist.md) 中的清单：

1. 验证项目目录和 git 分支是否匹配
2. 检查是否已解决阻塞项
3. 验证假设是否仍然成立
4. 审查修改文件以查找冲突
5. 检查环境状态

### 第 5 步：开始工作

从交接文档中的 "立即下一步行动" 第 1 项开始。

参考以下部分：
- "关键文件" 以获取重要位置
- "发现的关键模式" 以遵循约定
- "潜在的陷阱" 以避免已知问题

### 第 6 步：更新或链式交接文档

在工作时：
- 在 "待办工作" 中标记完成的项
- 将新发现添加到相关部分
- 对于长时间会话：使用 `--continues-from` 创建新的交接文档以链式连接

## 交接链式

对于长期项目，将交接文档链式连接以保持上下文谱系：

```
handoff-1.md (初始工作)
    ↓
handoff-2.md --continues-from handoff-1.md
    ↓
handoff-3.md --continues-from handoff-2.md
```

链中的每个交接文档：
- 链接到其前驱
- 可以标记旧交接文档为过时
- 为新代理提供上下文面包屑

从链中恢复时，首先阅读最新的交接文档，然后按需参考前驱。

## 存储位置

交接文档存储在：`.claude/handoffs/`

命名约定：`YYYY-MM-DD-HHMMSS-[slug].md`

示例：`2024-01-15-143022-implementing-auth.md`

## 资源

### scripts/

| 脚本 | 目的 |
|------|------|
| `create_handoff.py [slug] [--continues-from <file>]` | 使用智能框架生成新的交接文档 |
| `list_handoffs.py [path]` | 列出项目中的可用交接文档 |
| `validate_handoff.py <file>` | 检查完整性、质量和安全性 |
| `check_staleness.py <file>` | 评估交接文档上下文是否仍然当前 |

### references/

- [handoff-template.md](references/handoff-template.md) - 带有指导的完整模板结构
- [resume-checklist.md](references/resume-checklist.md) - 用于恢复代理的验证清单
