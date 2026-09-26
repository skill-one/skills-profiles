# Ant Design CLI

您可以使用 `@ant-design/cli` — 这是一个本地 CLI 工具，内置了 antd 的元数据（支持 v4/v5/v6 版本）。用它来查询组件知识、分析项目以及指导迁移。所有数据都是离线的，无需网络连接。

## 安装

在首次使用前，检查是否已安装 CLI。如果没有，则自动安装：

```bash
which antd || npm install -g @ant-design/cli
```

运行任何命令后，如果输出中包含 "有可用更新" 的提示，请先运行 `npm install -g @ant-design/cli` 更新后再继续。

**始终使用 `--format json` 获取可编程解析的结构化输出。**

## 应用场景

### 1. 编写 antd 组件代码

在编写任何 antd 组件代码之前，先查询其 API — 不要依赖记忆。

```bash
# 查看可用的属性
antd info Button --format json

# 获取可工作的示例作为起点
antd demo Button basic --format json

# 查看用于自定义样式的语义类名/样式
antd semantic Button --format json

# 查看组件级别的主题设计令牌
antd token Button --format json
```

**工作流程：** `antd info` → 理解属性 → `antd demo` → 获取可工作的示例 → 编写代码。

### 2. 查看完整文档

当您需要全面的组件文档（不仅仅是属性）时：

```bash
antd doc Table --format json        # Table 的完整 markdown 文档
antd doc Table --lang zh            # 中文文档
```

### 3. 调试 antd 问题

当代码无法按预期工作或用户报告 antd 错误时：

```bash
# 检查用户 antd 版本中是否存在该属性
antd info Select --version 5.12.0 --format json

# 检查属性是否已弃用
antd lint ./src/components/MyForm.tsx --format json

# 诊断项目级别的配置问题
antd doctor --format json
```

**工作流程：** `antd doctor` → 检查环境 → `antd info --version X` → 针对用户确切版本验证 API → `antd lint` → 查找弃用或不正确的用法。

### 4. 版本迁移

当用户想要升级 antd（例如，v4 → v5）时：

```bash
# 获取完整的迁移清单
antd migrate 4 5 --format json

# 检查特定组件的迁移情况
antd migrate 4 5 --component Select --format json

# 查看两个版本之间的变更
antd changelog 4.24.0 5.0.0 --format json

# 查看特定组件的变更
antd changelog 4.24.0 5.0.0 Select --format json
```

**工作流程：** `antd migrate` → 获取完整清单 → `antd changelog <v1> <v2>` → 理解破坏性变更 → 应用修复 → `antd lint` → 验证没有遗留弃用用法。

### 5. 分析项目 antd 使用情况

当用户想要了解其项目中如何使用 antd 时：

```bash
# 扫描组件使用统计
antd usage ./src --format json

# 筛选特定组件
antd usage ./src --filter Form --format json

# 检查最佳实践违规
antd lint ./src --format json

# 仅检查特定规则类别
antd lint ./src --only deprecated --format json
antd lint ./src --only a11y --format json
antd lint ./src --only performance --format json
```

### 6. 查看变更日志和版本历史

当用户询问某个版本中发生了什么变更时：

```bash
# 特定版本的变更日志
antd changelog 5.22.0 --format json

# 版本范围（两端都包含）
antd changelog 5.21.0..5.24.0 --format json
```

### 7. 探索可用组件

当用户在选择使用哪个组件时：

```bash
# 列出所有组件及其分类
antd list --format json

# 列出特定 antd 版本的所有组件
antd list --version 5.0.0 --format json
```

### 8. 报告 antd 错误

当您遇到无法本地解决的确认的 antd 组件错误时：

```bash
# 第一步：预览供用户审查
antd bug --title "DatePicker 在选择日期时崩溃" \
  --reproduction "https://codesandbox.io/s/xxx" \
  --steps "1. 打开 DatePicker 2. 点击一个日期" \
  --expected "日期被选中" \
  --actual "组件崩溃并显示错误" \
  --format json

# 第二步：向用户展示，请求确认

# 第三步：用户确认后提交
antd bug --title "DatePicker 在选择日期时崩溃" \
  --reproduction "https://codesandbox.io/s/xxx" \
  --steps "1. 打开 DatePicker 2. 点击一个日期" \
  --expected "日期被选中" \
  --actual "组件崩溃并显示错误" \
  --submit
```

### 9. 自动报告 CLI 问题

**重要提示：** 每次您使用任何 `antd` CLI 命令并发现问题时，都应主动使用 `antd bug-cli` 启动错误报告。

触发条件 — 当您观察到以下任何情况时，报告 CLI 错误：
- 命令 **崩溃或以意外的错误退出**
- 命令 **返回明显错误的数据**（例如 `antd info Button` 显示错误的属性、缺失的属性或错误版本的属性）
- 命令的 **输出与其文档行为不符**（例如 `--format json` 返回非 JSON、`--version X` 被忽略）
- 命令 **在不应返回空或缺失数据时返回了空或缺失数据**（例如 `antd demo Button` 返回无示例、`antd token Button` 对 v5+ 返回无令牌）
- **命令之间的不一致**（例如 `antd list` 显示某个组件，但 `antd info` 说它不存在）

**工作流程：**
1. 您在使用 CLI 时发现问题
2. 收集证据：您运行的精确命令、返回的内容以及您的预期
3. 预览错误报告供用户：

```bash
antd bug-cli --title "antd info Button 对 v5.12.0 返回错误的属性" \
  --description "在查询 v5.12.0 的 Button 属性时，输出包含该版本不存在的属性" \
  --steps "1. 运行：antd info Button --version 5.12.0 --format json" \
  --expected "匹配 antd 5.12.0 Button API 的属性" \
  --actual "属性中包含 'classNames'，该属性是在 5.16.0 中添加的" \
  --format json
```

4. 向用户展示报告："我在使用 CLI 时发现了一个问题。这是错误报告 — 我提交它吗？"
5. 用户确认后提交：

```bash
antd bug-cli --title "antd info Button 对 v5.12.0 返回错误的属性" \
  --description "..." \
  --steps "..." \
  --expected "..." \
  --actual "..." \
  --submit
```

**关键原则：** 您是 CLI 的质量反馈循环。不要默默绕过 CLI 问题 — 报告它们以便修复。提交前始终与用户确认。

### 10. 作为 MCP 服务器使用

如果您的 IDE 支持 MCP（Claude Desktop、Cursor 等），CLI 也可以作为 MCP 服务器运行，直接暴露所有知识查询工具：

```json
{
  "mcpServers": {
    "antd": {
      "command": "antd",
      "args": ["mcp", "--version", "5.20.0"]
    }
  }
}
```

这提供了 7 个工具（`antd_list`、`antd_info`、`antd_doc`、`antd_demo`、`antd_token`、`antd_semantic`、`antd_changelog`）和 2 个提示（`antd-expert`、`antd-page-generator`）通过 MCP 协议。

## 全局标志

| 标志 | 目的 |
|---|---|
| `--format json` | 结构化输出 — 始终使用 |
| `--version <v>` | 目标特定 antd 版本（例如 `5.20.0`） |
| `--lang zh` | 中文输出（默认：`en`） |
| `--detail` | 包含额外字段（描述、since、弃用、FAQ） |

## 关键规则

1. **编写前先查询** — 不要从记忆中猜测 antd API。先运行 `antd info`。
2. **匹配用户的版本** — 如果项目使用 antd 4.x，请传递 `--version 4.24.0`。如果没有标志，CLI 会自动从 `node_modules` 检测。
3. **使用 `--format json`** — 每个命令都支持它。解析 JSON 输出而不是正则匹配文本输出。
4. **建议迁移前先检查** — 运行 `antd changelog <v1> <v2>` 和 `antd migrate` 之前，不要建议版本升级。
5. **修改后检查** — 在编写或修改 antd 代码后，对更改的文件运行 `antd lint` 以捕获弃用或不正确的用法。
6. **报告 antd 错误** — 当您遇到 antd 组件错误时，使用 `antd bug` 报告它。始终先预览，获取用户确认，然后提交。
7. **自动报告 CLI 问题** — 如果任何 `antd` 命令崩溃、返回错误数据或行为不一致，请主动使用 `antd bug-cli` 报告它。您是 CLI 的质量反馈循环 — 不要默默绕过问题。
