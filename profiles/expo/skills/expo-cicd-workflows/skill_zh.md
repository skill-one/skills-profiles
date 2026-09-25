# EAS 工作流技能

帮助开发者编写和编辑 EAS CI/CD 工作流 YAML 文件。

## 参考文档

在生成或验证工作流文件之前，请获取这些资源。首先解析此技能的目录，然后使用其 `scripts/` 目录中的获取脚本。它使用 Node.js 实现，并使用 ETags 缓存响应以提高效率：

```bash
# 获取资源
node <skill-dir>/scripts/fetch.js <url>
```

1. **JSON Schema** — https://api.expo.dev/v2/workflows/schema
   - 必须获取此模式
   - 验证的真实来源
   - 所有作业类型及其必需/可选参数
   - 触发类型和配置
   - 运行器类型、虚拟机镜像以及所有枚举

2. **语法文档** — https://raw.githubusercontent.com/expo/expo/refs/heads/main/docs/pages/eas/workflows/syntax.mdx
   - 工作流 YAML 语法的概述
   - 示例和英文解释
   - 表达式语法和上下文

3. **预打包作业** — https://raw.githubusercontent.com/expo/expo/refs/heads/main/docs/pages/eas/workflows/pre-packaged-jobs.mdx
   - 支持的预打包作业类型的文档
   - 作业特定参数和输出

不要依赖记忆值；这些资源会随着新功能的添加而演变。

## 工作流文件位置

工作流位于 `.eas/workflows/*.yml`（或 `.yaml`）。

## 顶层结构

工作流文件具有以下顶层键：

- `name` — 工作流的显示名称
- `on` — 启动工作流的触发器（至少需要一个）
- `jobs` — 作业定义（必需）
- `defaults` — 所有作业的共享默认值
- `concurrency` — 控制并行工作流运行

请参考模式以获取每个部分的完整规范。

## 表达式

使用 `${{ }}` 语法表示动态值。模式定义了可用的上下文：

- `github.*` — GitHub 仓库和事件信息
- `inputs.*` — 来自 `workflow_dispatch` 输入的值
- `needs.*` — 从依赖作业的输出和状态
- `jobs.*` — 作业输出（替代语法）
- `steps.*` — 自定义作业中的步骤输出
- `workflow.*` — 工作流元数据

## 生成工作流

在生成或编辑工作流时：

1. 获取模式以获取当前作业类型、参数和允许的值
2. 验证每个作业类型所需的字段是否存在
3. 验证 `needs` 和 `after` 中的作业引用是否存在于工作流中
4. 检查表达式是否引用了有效的上下文和输出
5. 确保 `if` 条件遵守模式的长度限制

## 验证

生成或编辑工作流文件后，请根据模式对其进行验证：

```sh
# 如果缺少依赖项，请安装
[ -d "<skill-dir>/scripts/node_modules" ] || npm install --prefix <skill-dir>/scripts

node <skill-dir>/scripts/validate.js <workflow.yml> [workflow2.yml ...]
```

验证器会获取最新的模式并检查 YAML 结构。在考虑工作流完成之前，修复任何报告的错误。

## 回答问题

当用户询问有关可用选项（作业类型、触发器、运行器类型等）时，请获取模式并从其中推导出答案，而不是依赖可能过时的信息。
