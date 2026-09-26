使用此技能用于 `tzst` 命令行界面。当用户明确希望执行实际归档操作且所需的路径或归档名称已知时，默认执行操作。

此技能仅适用于 CLI。如果用户询问关于 Python 代码（例如 `from tzst import ...`），应将其视为一般 Python 库或 API 文档任务，而不是使用此技能作为主要指南。

## 使用时机

当用户：

- 提及 `.tzst` 或 `.tar.zst` 归档
- 希望创建、提取、展平、列出或测试 `tzst` 归档
- 需要帮助安装 `tzst` 或选择 CLI 标志
- 希望为脚本或自动化获取机器可读的 `tzst` 输出
- 需要安全的冲突处理或提取过滤器指导

时使用此技能。除非请求中实际包含 `tzst`，否则不要使用此技能回答通用的 `tar`、`zip` 或 Python API 问题。

## 预检查

1. 使用 `tzst --version` 或 `tzst --help` 检查 `tzst` 是否可用。
2. 如果缺失，优先选择以下安装路径之一：
   - `uv tool install tzst`
   - `pip install tzst`
   - 当用户不想安装 Python 时，从 <https://github.com/xixu-me/tzst/releases/latest> 获取独立发布二进制文件
3. 在执行实际操作前重新运行 `tzst --version` 或 `tzst --help`。

## 工作流程

1. 判断请求是执行意图还是指导意图。
   类似于 "归档这些文件"、"提取这个备份"、"列出里面有什么"、"测试这个归档" 或 "安装 tzst" 的请求属于执行意图。
2. 选择匹配请求的命令：
   - `a`、`add`、`create` 用于归档创建
   - `x`、`extract` 用于保留目录结构的正常提取
   - `e`、`extract-flat` 仅当用户明确要求展平输出时使用
   - `l`、`list` 用于归档检查
   - `t`、`test` 用于完整性检查
3. 如果用户只想提取少量成员且成员名称不确定，应先列出。
4. 当需要命令矩阵、精确标志名称或复制粘贴示例时，加载 [`references/cli-reference.md`](./references/cli-reference.md)。

## 安全默认值

- 除非明确要求展平，否则优先使用 `x` 而不是 `e`。
- 将 `--filter data` 作为默认提取模式。
- 仅当用户需要标准 tar 风格兼容性时使用 `--filter tar`。
- 仅当用户明确说明归档源完全可信时使用 `--filter fully_trusted`。
- 保持原子归档创建启用。仅在用户明确要求时使用 `--no-atomic`。
- 对于大归档或内存受限环境，优先使用 `--streaming`。
- 对于自动化或管道，优先使用 `tzst --json --no-banner ...`。
- 对于自动化提取，要求明确的非交互式冲突解决选择，如 `replace_all`、`skip_all` 或 `auto_rename_all`。
- 不要将 `--json` 与交互式冲突提示结合使用。

## 脚本注意事项

- 在示例中将全局标志放在子命令之前，例如 `tzst --json --no-banner l archive.tzst`。
- 在脚本中使用退出码：`0` 表示成功，`1` 表示操作错误，`2` 表示参数解析错误，`130` 表示中断。
- 当归档命名重要时，告知用户 `tzst` 可能将创建目标标准化为 `.tzst` 或 `.tar.zst`。

## 常见错误

- 用户期望保留原始目录结构时使用 `e`
- 为来自未知或不可信源的归档推荐 `fully_trusted`
- 非交互式提取时忘记明确冲突策略
- 将 Python API 问题视为 CLI 问题
- 根据 tar 习惯猜测标志，而不是检查捆绑的参考或已安装的 CLI 帮助
