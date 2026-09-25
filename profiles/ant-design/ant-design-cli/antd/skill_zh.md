# Ant Design CLI

您可以使用 `@ant-design/cli` — 这是一个本地 CLI 工具，捆绑了 antd 的元数据（支持 v4/v5/v6 版本），还包含从 v3 → v4、v4 → v5、v5 → v6 的迁移指南。使用它来查询组件知识、分析项目以及指导迁移。所有数据都是离线的，无需网络连接。

## 安装

首次使用前，请检查是否已安装 CLI。如果没有，则自动安装：

```bash
which antd || npm install -g @ant-design/cli
```

运行任何命令后，如果输出中包含“有可用更新”的提示，请在继续之前运行 `antd upgrade` 进行更新。

**始终使用 `--format json` 以获得结构化的输出，以便程序化解析。**

## 应用场景

### 1. 编写 antd 组件代码

在编写任何 antd 组件代码之前，先查询其 API — 不要依赖记忆。

```bash
# 检查可用属性
antd info Button --format json

# 获取可工作的示例作为起点
antd demo Button basic --format json

# 检查语义类名/样式以进行自定义样式
antd semantic Button --format json

# 检查组件级别的主题设计令牌
antd token Button --format json

# 获取整体设计语言（design.md）：颜色、排版、间距、圆角 + 原则
antd design.md --format json
```

**工作流程：** `antd info` → 理解属性 → `antd demo` → 获取可工作的示例 → 编写代码。

### 2. 查看完整文档

当您需要全面的组件文档（而不仅仅是属性）时：

```bash
antd doc Table --format json        # Table 的完整 markdown 文档
antd doc Table --lang zh            # 中文文档
```

### 3. 调试 antd 问题

当代码无法按预期工作或用户报告 antd 错误时：

```bash
# 收集完整的环境快照（系统、依赖、浏览器、构建工具）
antd env --format json

# 检查用户 antd 版本中是否存在该属性
antd info Select --version 5.12.0 --format json

# 检查该属性是否已弃用
antd lint ./src/components/MyForm.tsx --format json

# 诊断项目级别的配置问题
antd doctor --format json
```

**工作流程：** `antd env` → 捕获完整环境 → `antd doctor` → 检查配置 → `antd info --version X` → 针对用户的精确版本验证 API → `antd lint` → 查找弃用或不正确的用法。

### 4. 版本迁移

当用户想要升级 antd（例如，v3 → v4 或 v4 → v5）时：

```bash
# 获取完整的迁移清单
antd migrate 3 4 --format json    # v3 → v4
antd migrate 4 5 --format json    # v4 → v5

# 检查特定组件的迁移
antd migrate 4 5 --component Select --format json

# 生成对 agent 友好的自动迁移提示（不会修改文件）
antd migrate 4 5 --apply ./src --format json

# 查看两个版本之间的变更
antd changelog 4.24.0 5.0.0 --format json

# 查看特定组件的变更
antd changelog 4.24.0 5.0.0 Select --format json
```

**工作流程：** `antd migrate` → 获取完整的清单 → `antd changelog <v1> <v2>` → 理解破坏性变更 → 应用修复 → `antd lint` → 验证没有遗留弃用用法。

### 5. 分析项目中的 antd 使用情况

当用户想要了解他们的项目中如何使用 antd 时：

```bash
# 扫描组件使用统计
antd usage ./src --format json

# 筛选到特定组件
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

# 列出特定 antd 版本的组件
antd list --version 5.0.0 --format json
```

### 8. 收集环境信息

当您需要了解项目的 antd 设置，或为错误报告准备信息时：

```bash
# 完整的环境快照（文本 — 复制到 GitHub Issues）
antd env

# 结构化的 JSON 以供程序化使用
antd env --format json

# 扫描特定项目目录
antd env ./my-project --format json
```

收集内容：操作系统、Node、包管理器（npm/pnpm/yarn/bun/utoo）、npm 仓库、浏览器、核心依赖（antd/react/dayjs）、所有 `@ant-design/*` 和 `rc-*` 包，以及构建工具（umi/vite/webpack/typescript 等）。

### 9. 报告 antd 错误

当用户要求您报告 antd 错误时：

```bash
# 第 0 步：收集环境信息以供参考（可选 — antd 错误报告已嵌入基本环境）
# 使用输出交叉检查版本或附加额外细节到错误报告
antd env --format json

# 第 1 步：预览供用户审查
antd bug --title "DatePicker 在选择日期时崩溃" \
  --reproduction "https://codesandbox.io/s/xxx" \
  --steps "1. 打开 DatePicker 2. 点击一个日期" \
  --expected "日期被选中" \
  --actual "组件崩溃并显示错误" \
  --format json

# 第 2 步：展示给用户，请求确认

# 第 3 步：用户确认后提交
antd bug --title "DatePicker 在选择日期时崩溃" \
  --reproduction "https://codesandbox.io/s/xxx" \
  --steps "1. 打开 DatePicker 2. 点击一个日期" \
  --expected "日期被选中" \
  --actual "组件崩溃并显示错误" \
  --submit
```

### 10. 报告 CLI 问题

当用户要求您报告 CLI 错误，或明确要求帮助提交报告时：

```bash
# 预览错误报告给用户
antd bug-cli --title "antd info Button 对 v5.12.0 返回错误的属性" \
  --description "在查询 v5.12.0 版本的 Button 属性时，输出包含该版本不存在的属性" \
  --steps "1. 运行：antd info Button --version 5.12.0 --format json" \
  --expected "匹配 antd 5.12.0 Button API 的属性" \
  --actual "属性包含 'classNames'，该属性是在 5.16.0 中添加的" \
  --format json
```

向用户展示报告并确认后再提交：

```bash
antd bug-cli --title "antd info Button 对 v5.12.0 返回错误的属性" \
  --description "..." \
  --steps "..." \
  --expected "..." \
  --actual "..." \
  --submit
```

**选择退出：** 如果环境变量 `ANTD_NO_AUTO_REPORT=1` 被设置，则完全跳过所有错误报告建议 — 除非用户直接询问，否则不要建议 `antd bug` 或 `antd bug-cli`。

### 11. 升级 CLI

当用户想要将 `@ant-design/cli` 更新到最新版本，或出现“有可用更新”的提示时：

```bash
# 升级到最新版本（自动检测包管理器）
antd upgrade
```

该命令检测安装 CLI 的包管理器（npm、yarn、pnpm、bun、cnpm、utoo）并运行相应的升级命令。如果检测失败，则建议手动命令。

### 12. 作为 MCP 服务器使用

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

这提供了 8 个工具（`antd_list`、`antd_info`、`antd_doc`、`antd_demo`、`antd_token`、`antd_design_md`、`antd_semantic`、`antd_changelog`）和 2 个提示（`antd-expert`、`antd-page-generator`）通过 MCP 协议。

## 全局标志

| 标志 | 目的 |
|---|---|
| `--format <format>` | 输出格式：`json`、`text` 或 `markdown`（代理应优先选择 `json`） |
| `--version <v>` | 目标特定 antd 版本（例如 `5.20.0`） |
| `--lang zh` | 中文输出（默认 `en`） |
| `--detail` | 包含额外字段（描述、since、弃用、FAQ） |
| `-V, --cli-version` | 打印 CLI 版本并退出 |

## 关键规则

1. **始终先查询再编写** — 不要从记忆中猜测 antd API。先运行 `antd info`。
2. **匹配用户的版本** — 知识查询（`list/info/doc/demo/token/semantic/changelog`）支持 antd v4+。如果项目使用 antd 4.x/5.x/6.x，传递 `--version 4.24.0` / `5.24.0` / `6.x`。对于 antd v3 项目，先使用 `antd migrate 3 4`。
3. **使用 `--format json`** — 每个命令都支持它。解析 JSON 输出而不是正则匹配文本输出。
4. **在建议迁移前检查** — 运行 `antd changelog <v1> <v2>` 和 `antd migrate` 之前，建议版本升级。
5. **变更后检查** — 在编写或修改 antd 代码后，对更改的文件运行 `antd lint` 以捕获弃用或不正确的用法。
6. **报告 antd 错误** — 当用户要求报告 antd 错误时，使用 `antd bug`。始终先预览，获取用户确认，然后提交。
7. **报告 CLI 问题** — 当用户询问 CLI 问题，使用 `antd bug-cli` 帮助他们提交报告。始终先预览，获取用户确认，然后提交。
