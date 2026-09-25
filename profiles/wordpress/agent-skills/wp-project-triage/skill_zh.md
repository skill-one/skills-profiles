# WP 项目筛选

## 使用场景

使用此技能快速了解您所在的 WordPress 仓库类型，并在进行修改前遵循相应的命令和约定。

## 所需输入

- 仓库根目录（当前工作目录）。

## 操作步骤

1. 运行检测器（将 JSON 输出到标准输出）：
   - `node skills/wp-project-triage/scripts/detect_wp_project.mjs`
2. 如果需要精确的输出契约，请阅读：
   - `skills/wp-project-triage/references/triage.schema.json`
3. 使用报告选择工作流约束条件：
   - 项目类型
   - PHP/Node 工具链是否存在
   - 测试是否存在
   - 版本提示和来源
4. 如果报告缺少您需要的信号，请更新检测器而不是猜测。

## 验证

- JSON 应该可以解析并包含：`project.kind`、`signals` 和 `tooling`。
- 在修改影响结构/工具链的文件后（如添加 `theme.json`、`block.json`、构建配置）重新运行。

## 失败模式/调试

- 如果报告为 `unknown`，请检查仓库根目录是否正确。
- 如果扫描速度慢，请在脚本中添加/扩展忽略目录。
