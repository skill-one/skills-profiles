# Ant Design

## S - 范围
- 目标：`antd@^6` + React 18-19，根据需要使用 `ant-design-pro@^5` / `@ant-design/pro-components` 和 `@ant-design/x@^2`。
- 工具：`@ant-design/cli` 用于离线组件元数据、示例、变更日志、迁移、代码检查、医生检查和使用分析。
- 重点：仅提供决策指导，不提供面向最终用户的教程。
- 源码策略：仅使用官方文档；不包含未公开的 API 或内部 `.ant-*` 依赖。

### 默认假设
- 语言：TypeScript。
- 样式：先使用 token，然后使用 `classNames`/`styles`；避免全局覆盖。
- 提供者：除非需要严格隔离，否则使用一个根 `ConfigProvider`。

### 强制规则
- 在编写或修改 antd 组件代码之前，使用 `antd info <Component> --format json` 查询组件 API。不要依赖内存，当 CLI 可以离线回答时。
- 使用 `antd` CLI 命令时始终使用 `--format json`。
- 如果项目版本很重要，使用 `--version <x.y.z>` 匹配，或让 CLI 从本地 `node_modules` 自动检测。
- 修改 antd 代码后，运行 `antd lint <changed-path> --format json`。
- 如果 `antd` CLI 命令崩溃、返回错误数据或违反其文档行为，准备 `antd bug-cli` 预览供用户确认，而不是静默地绕过它。
- 对于组件问题，首先将组件名称映射到官方路由 slug `{components}`（小写连字符命名，例如 `TreeSelect -> tree-select`，`Button -> button`），然后按以下顺序请求文档（中文优先，英文备用）：
  1. `https://ant.design/components/{components}-cn`
  2. `https://ant.design/components/{components}`
  - 示例：`tree-select-cn -> tree-select`，`button-cn -> button`。
- 仅使用文档中记录的 antd/Pro/X API。
- 不要编造 props/事件/组件名称。
- 不要依赖内部 DOM 或 `.ant-*` 选择器。
- 主题优先级：全局 token -> 组件 token -> 别名 token。

## P - 流程
### 1) 分类
- 确定层级：核心 antd、Pro 或 X。
- 确认版本、渲染模式（CSR/SSR/streaming）、数据规模，以及是否应将 `@ant-design/cli` 作为主要查找路径。

### 2) 查询权威来源
- 优先使用本地 `@ant-design/cli` 进行结构化查找：
  - `antd info` 用于 props/API
  - `antd demo` 用于工作基线
  - `antd doc` 用于完整文档
  - `antd token` / `antd semantic` 用于主题和样式钩子
  - `antd doctor`、`antd lint`、`antd usage`、`antd migrate`、`antd changelog` 用于调试或升级
- 当需要叙述性文档或交叉验证时，请求官方组件文档（中文优先，英文备用）。

### 3) 决策
- 提供者基线：CSR -> `ConfigProvider`；SSR -> `ConfigProvider` + `StyleProvider`。
- 主题基线：全局 token -> 组件 token -> `classNames`/`styles`。
- 输出建议 + 风险 + 验证点（SSR/a11y/perf），使用 CLI 结果时引用。

## O - 输出
- 提供简短的决策理由（1-3 句话）。
- 包括最小的提供者/主题策略。
- 包括具体的 SSR/a11y/perf 检查。
- 对于 Pro：包括路由/菜单/权限和 CRUD 模式方向。
- 对于 X：包括消息/工具模式和流式状态方向。

## 参考文献

| 文件 | 使用场景 |
| --- | --- |
| `references/antd-cli.md` | 您需要离线 CLI 工作流程进行 API 查找、示例、代码检查、医生检查、迁移、变更日志审查、使用分析或错误报告。 |

## 回归检查清单
- [ ] 一个根 `ConfigProvider`；SSR 样式顺序/水合验证。
- [ ] 先使用 token；没有广泛的全局 `.ant-*` 覆盖。
- [ ] 表格具有稳定的 `rowKey`；排序/过滤/分页入口统一。
- [ ] 选择远程模式在使用远程搜索时禁用本地过滤。
- [ ] 上传受控/非受控模式明确，具有失败/重试路径。
- [ ] Pro 路由/菜单/权限与后端强制保持一致。
- [ ] X 流式支持停止/重试和确定性工具渲染。
- [ ] 如果使用 `antd` CLI，命令使用 `--format json` 执行，任何 CLI 缺陷通过 `antd bug-cli` 预览升级。
