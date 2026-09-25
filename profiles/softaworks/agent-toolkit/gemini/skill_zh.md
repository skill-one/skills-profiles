# Gemini 技能指南

## 何时使用 Gemini
- 当被要求激活时
- **代码审查**：跨多个文件的全面代码审查
- **计划审查**：分析架构计划、技术规范或项目路线图
- **大上下文处理**：需要 >200k 个 token 的上下文的任务（整个代码库、文档集）
- **多文件分析**：理解多个文件之间的关系和模式

## ⚠️ 重要提示：后台/非交互模式警告

**绝对不要在后台或非交互式 shell 中使用 `--approval-mode default`**（例如 Claude 代码工具调用）。它将无限期地挂起等待无法提供的审批提示。

**对于自动化的后台审查：**
- ✅ 使用 `--approval-mode yolo` 进行完全自动化执行
- ✅ 或者使用超时包装：`timeout 300 gemini ...`
- ❌ 绝对不要在没有交互式终端的情况下使用 `--approval-mode default`

**挂起 Gemini 的症状：**
- 进程运行 20+ 分钟，CPU 使用率为 0%
- 没有网络活动
- 进程状态显示为 'S'（睡眠）

**修复挂起的进程：**
```bash
# 检查是否挂起
ps aux | grep gemini | grep -v grep

# 如有必要则终止
pkill -9 -f "gemini.*gemini-3-pro-preview"
```

## 运行任务

1. 通过 `AskUserQuestion` 在**单个提示**中询问用户要使用哪个模型。可用的模型：
   - `gemini-3-pro-preview` ⭐（旗舰模型，最适合编码和复杂推理，比 2.5 Pro 在软件工程方面好 35%）
   - `gemini-3-flash`（亚秒级延迟，从 3 Pro 蒸馏而来，最适合速度关键任务）
   - `gemini-2.5-pro`（遗留选项，综合性能强大）
   - `gemini-2.5-flash`（遗留选项，具有思考能力且成本效益高）
   - `gemini-2.5-flash-lite`（遗留选项，处理速度最快）

2. 根据任务选择审批模式：
   - `default`：提示审批（⚠️ 仅适用于交互式终端会话）
   - `auto_edit`：仅自动批准编辑工具（用于带有建议的代码审查）
   - `yolo`：自动批准所有工具（✅ 必须用于后台/自动化任务）

3. 使用适当的选项组装命令：
   - `-m, --model <MODEL>` - 模型选择
   - `--approval-mode <default|auto_edit|yolo>` - 控制工具审批
   - `-y, --yolo` - `--approval-mode yolo` 的替代方案
   - `-i, --prompt-interactive "prompt"` - 执行提示并继续交互式操作
   - `--include-directories <DIR>` - 工作区中要包含的附加目录
   - `-s, --sandbox` - 以隔离模式运行

4. **对于后台/自动化任务，始终使用 `--approval-mode yolo`** 或添加超时包装。在非交互式 shell 中绝对不要使用 `default`。

5. 运行命令并捕获输出。对于后台/自动化模式：
   ```bash
   # 推荐：使用 yolo 进行后台任务
   gemini -m gemini-3-pro-preview --approval-mode yolo "审查此代码库的安全问题"

   # 或者使用超时（5 分钟限制）
   timeout 300 gemini -m gemini-3-pro-preview --approval-mode yolo "审查此代码库"
   ```

6. 对于带有初始提示的交互式会话：
   ```bash
   gemini -m gemini-3-pro-preview -i "审查认证系统" --approval-mode auto_edit
   ```

7. **在 Gemini 完成后**，通知用户："Gemini 分析已完成。您可以开始新的 Gemini 会话进行后续分析或继续探索结果。"

### 快速参考

| 使用场景 | 审批模式 | 关键标志 |
| --- | --- | --- |
| 后台代码审查 | `yolo` ✅ | `-m gemini-3-pro-preview --approval-mode yolo` |
| 后台分析 | `yolo` ✅ | `-m gemini-3-pro-preview --approval-mode yolo` |
| 带超时的后台 | `yolo` ✅ | `timeout 300 gemini -m gemini-3-pro-preview --approval-mode yolo` |
| 交互式代码审查 | `default` | `-m gemini-3-pro-preview --approval-mode default`（仅限交互式终端） |
| 带自动编辑的代码审查 | `auto_edit` | `-m gemini-3-pro-preview --approval-mode auto_edit` |
| 自动化重构 | `yolo` | `-m gemini-3-pro-preview --approval-mode yolo` |
| 速度关键的后台 | `yolo` ✅ | `-m gemini-3-flash --approval-mode yolo` |
| 成本优化的后台 | `yolo` ✅ | `-m gemini-2.5-flash --approval-mode yolo` |
| 多目录分析 | `yolo`（如果后台） | `--include-directories <DIR1> --include-directories <DIR2>` |
| 带提示的交互式 | `auto_edit` 或 `default` | `-i "prompt" --approval-mode <mode>` |

### 模型选择指南

| 模型 | 最适合 | 上下文窗口 | 关键特性 |
| --- | --- | --- | --- |
| `gemini-3-pro-preview` ⭐ | **旗舰模型**：复杂推理、编码、代理任务 | 1M 输入 / 64k 输出 | 编码氛围，76.2% SWE-bench，$2-4/M 输入 |
| `gemini-3-flash` | 亚秒级延迟，速度关键应用 | 1M 输入 / 64k 输出 | 从 3 Pro 蒸馏，TPU 优化 |
| `gemini-2.5-pro` | 遗留：综合性能强大 | 1M 输入 / 65k 输出 | 思考模式，成熟稳定性 |
| `gemini-2.5-flash` | 遗留：成本效益高，高容量任务 | 1M 输入 / 65k 输出 | 最佳价格 ($0.15/M)，思考模式 |
| `gemini-2.5-flash-lite` | 遗留：处理速度最快，高吞吐量 | 1M 输入 / 65k 输出 | 最大速度，最小延迟 |

**Gemini 3 优势**：软件工程准确率提高 35%，在 SWE-bench（76.2%）、GPQA Diamond（91.9%）和 WebDev Arena（1487 Elo）上处于最先进水平。知识截止日期：2025 年 1 月。

**即将推出**：`gemini-3-deep-think`，用于超复杂推理，具有增强的思考能力。

## 常见使用场景

### 代码审查（后台/自动化）
```bash
# 后台执行（Claude 代码、CI/CD 等）
gemini -m gemini-3-pro-preview --approval-mode yolo \
  "执行全面的代码审查，重点关注：
   1. 安全漏洞
   2. 性能问题
   3. 代码质量和可维护性
   4. 最佳实践违规"

# 带超时安全（5 分钟）
timeout 300 gemini -m gemini-3-pro-preview --approval-mode yolo \
  "执行全面的代码审查..."
```

### 计划审查（后台/自动化）
```bash
# 后台执行
gemini -m gemini-3-pro-preview --approval-mode yolo \
  "审查此架构计划，重点关注：
   1. 可扩展性问题
   2. 缺少组件
   3. 集成挑战
   4. 替代方法"
```

### 大上下文分析（后台/自动化）
```bash
# 后台执行
gemini -m gemini-3-pro-preview --approval-mode yolo \
  "分析整个代码库，以理解：
   1. 整体架构
   2. 关键模式和规范
   3. 潜在的技术债务
   4. 重构机会"
```

### 交互式代码审查（仅限终端）
```bash
# 仅在交互式终端中使用 default 模式
gemini -m gemini-3-pro-preview --approval-mode default \
  "审查认证流程中的安全问题"
```

## 后续操作

- Gemini CLI 会话通常是单次或交互式的。与 Codex 不同，没有内置的恢复功能。
- 对于后续分析，使用之前的发现启动新的 Gemini 会话。
- 当提出后续操作时，重述所选模型和审批模式。
- 在每个 Gemini 命令后使用 `AskUserQuestion` 确认下一步或收集澄清。

## 错误处理

- 当 `gemini --version` 或 Gemini 命令以非零状态退出时，停止并报告失败。
- 在重试失败命令之前请求指示。
- 在使用高影响标志（`--approval-mode yolo`、`-y`、`--sandbox`）之前，使用 `AskUserQuestion` 询问用户权限，除非已经获得许可。
- 当输出包含警告或部分结果时，总结它们并使用 `AskUserQuestion` 询问如何调整。

## 挂起 Gemini 进程的故障排除

### 检测
```bash
# 检查挂起进程
ps aux | grep -E "gemini.*gemini-3" | grep -v grep

# 查找以下症状：
# - 进程运行 20+ 分钟
# - CPU 使用率为 0%
# - 进程状态 'S'（睡眠）
# - 没有网络连接
```

### 诊断
```bash
# 获取详细进程信息
ps -o pid,etime,pcpu,stat,command -p <PID>

# 检查网络活动
lsof -p <PID> 2>/dev/null | grep -E "(TCP|ESTABLISHED)" | wc -l
# 如果结果为 0，进程挂起
```

### 解决方案
```bash
# 终止挂起的 Gemini 进程
pkill -9 -f "gemini.*gemini-3-pro-preview"

# 或者终止特定 PID
kill -9 <PID>

# 验证清理
ps aux | grep gemini | grep -v grep
```

### 预防
- **始终使用 `--approval-mode yolo` 对于后台/自动化任务**
- 添加安全超时包装：`timeout 300 gemini ...`
- 绝对不要在非交互式 shell 中使用 `--approval-mode default`
- 使用 `ps` 监控首次运行，确保进程完成

## 大上下文处理的技巧

1. **具体**：提供清晰、结构化的提示，说明要分析的内容
2. **使用 include-directories**：明确指定所有相关目录
3. **选择合适的模型**：
   - 使用 `gemini-3-pro-preview` 进行复杂推理、编码任务和最高分析质量（推荐默认）
   - 使用 `gemini-3-flash` 进行需要亚秒级响应时间的速度关键任务
   - 使用 `gemini-2.5-flash` 进行成本优化的高容量处理
4. **利用 Gemini 3 的优势**：在软件工程任务上比 35% 更好，在代理工作流程和编码氛围方面表现优异
5. **分解复杂任务**：即使具有大上下文，结构化分析更有效
6. **保存结果**：要求 Gemini 输出结构化报告，以便参考

## CLI 版本

需要 Gemini CLI v0.16.0 或更高版本支持 Gemini 3 模型。检查版本：`gemini --version`
