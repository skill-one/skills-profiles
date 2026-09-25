# Nx 工作区探索

此技能提供对 Nx 工作区的只读探索。使用它来了解工作区结构、项目配置、可用目标和依赖项。

请记住，如果 nx 没有全局安装，您可能需要用 `npx`/`pnpx`/`yarn` 前缀命令。检查锁文件以确定使用的包管理器。

## 列出项目

使用 `nx show projects` 列出工作区中的项目。

项目过滤语法（`-p`/`--projects`）适用于许多 Nx 命令，包括 `nx run-many`、`nx release`、`nx show projects` 等。过滤器支持显式名称、通配符模式、标签引用（例如 `tag:name`）、目录和否定（例如 `!project-name`）。

```bash
# 列出所有项目
nx show projects

# 按模式（通配符）过滤
nx show projects --projects "apps/*"
nx show projects --projects "shared-*"

# 按标签过滤
nx show projects --projects "tag:publishable"
nx show projects -p 'tag:publishable,!tag:internal'

# 按目标过滤（具有特定目标的项目）
nx show projects --withTarget build

# 组合过滤器
nx show projects --type lib --withTarget test
nx show projects --affected --exclude="*-e2e"
nx show projects -p "tag:scope:client,packages/*"

# 否定模式
nx show projects -p '!tag:private'
nx show projects -p '!*-e2e'

# 以 JSON 格式输出
nx show projects --json
```

## 项目配置

使用 `nx show project <name> --json` 获取项目的完整解析配置。

**重要**：不要直接读取 `project.json` - 它只包含部分配置。`nx show project --json` 命令返回完整的解析配置，包括插件推断的目标。

您可以在 `node_modules/nx/schemas/project-schema.json` 中阅读完整的项目模式，以了解 nx 项目配置选项。

```bash
# 获取完整项目配置
nx show project my-app --json

# 从 JSON 中提取特定部分
nx show project my-app --json | jq '.targets'
nx show project my-app --json | jq '.targets.build'
nx show project my-app --json | jq '.targets | keys'

# 检查项目元数据
nx show project my-app --json | jq '{name, root, sourceRoot, projectType, tags}'
```

## 目标信息

目标定义可以在项目上运行的任务。

```bash
# 列出项目的所有目标
nx show project my-app --json | jq '.targets | keys'

# 获取完整目标配置
nx show project my-app --json | jq '.targets.build'

# 检查目标执行器/命令
nx show project my-app --json | jq '.targets.build.executor'
nx show project my-app --json | jq '.targets.build.command'

# 查看目标选项
nx show project my-app --json | jq '.targets.build.options'

# 检查目标输入/输出（用于缓存）
nx show project my-app --json | jq '.targets.build.inputs'
nx show project my-app --json | jq '.targets.build.outputs'

# 查找具有特定目标的项目
nx show projects --withTarget serve
nx show projects --withTarget e2e
```

## 工作区配置

直接读取 `nx.json` 获取工作级配置。
您可以在 `node_modules/nx/schemas/nx-schema.json` 中阅读完整的项目模式，以了解 nx 项目配置选项。

```bash
# 读取完整的 nx.json
cat nx.json

# 或者使用 jq 获取特定部分
cat nx.json | jq '.targetDefaults'
cat nx.json | jq '.namedInputs'
cat nx.json | jq '.plugins'
cat nx.json | jq '.generators'
```

nx.json 的关键部分：

- `targetDefaults` - 应用于给定名称的所有目标的默认配置
- `namedInputs` - 可重用的输入定义，用于缓存
- `plugins` - Nx 插件及其配置
- ...等等，阅读模式或 nx.json 获取详细信息

## 受影响的项目

如果用户询问受影响的项目，请阅读 [受影响项目参考](references/AFFECTED.md) 获取详细命令和示例。

## 常见探索模式

### "这个工作区有什么？"

```bash
nx show projects
nx show projects --type app
nx show projects --type lib
```

### "如何构建/测试/检查项目 X？"

```bash
nx show project X --json | jq '.targets | keys'
nx show project X --json | jq '.targets.build'
```

### "库 Y 依赖什么？"

```bash
# 使用项目图查找依赖项
nx graph --print | jq '.graph.dependencies | to_entries[] | select(.value[].target == "Y") | .key'
```

## 程序化答案

处理 nx CLI 结果时，使用命令行工具进行程序化计算答案，而不是手动计数或解析输出。始终使用 `--json` 标志获取结构化输出，该输出可以使用 `jq`、`grep` 或您本地安装的其他工具进行处理。

### 列出项目

```bash
nx show projects --json
```

示例输出：

```json
["my-app", "my-app-e2e", "shared-ui", "shared-utils", "api"]
```

常见操作：

```bash
# 计数项目
nx show projects --json | jq 'length'

# 按模式过滤
nx show projects --json | jq '.[] | select(startswith("shared-"))'

# 获取受影响的项目作为数组
nx show projects --affected --json | jq '.'
```

### 项目详情

```bash
nx show project my-app --json
```

示例输出：

```json
{
  "root": "apps/my-app",
  "name": "my-app",
  "sourceRoot": "apps/my-app/src",
  "projectType": "application",
  "tags": ["type:app", "scope:client"],
  "targets": {
    "build": {
      "executor": "@nx/vite:build",
      "options": { "outputPath": "dist/apps/my-app" }
    },
    "serve": {
      "executor": "@nx/vite:dev-server",
      "options": { "buildTarget": "my-app:build" }
    },
    "test": {
      "executor": "@nx/vite:test",
      "options": {}
    }
  },
  "implicitDependencies": []
}
```

常见操作：

```bash
# 获取目标名称
nx show project my-app --json | jq '.targets | keys'

# 获取特定目标配置
nx show project my-app --json | jq '.targets.build'

# 获取标签
nx show project my-app --json | jq '.tags'

# 获取项目根目录
nx show project my-app --json | jq -r '.root'
```

### 项目图

```bash
nx graph --print
```

示例输出：

```json
{
  "graph": {
    "nodes": {
      "my-app": {
        "name": "my-app",
        "type": "app",
        "data": { "root": "apps/my-app", "tags": ["type:app"] }
      },
      "shared-ui": {
        "name": "shared-ui",
        "type": "lib",
        "data": { "root": "libs/shared-ui", "tags": ["type:ui"] }
      }
    },
    "dependencies": {
      "my-app": [
        { "source": "my-app", "target": "shared-ui", "type": "static" }
      ],
      "shared-ui": []
    }
  }
}
```

常见操作：

```bash
# 从图中获取所有项目名称
nx graph --print | jq '.graph.nodes | keys'

# 查找项目的依赖项
nx graph --print | jq '.graph.dependencies["my-app"]'

# 查找依赖库的项目
nx graph --print | jq '.graph.dependencies | to_entries[] | select(.value[].target == "shared-ui") | .key'
```

## 故障排除

### "找不到任务 X:target 的配置"

```bash
# 检查项目上存在哪些目标
nx show project X --json | jq '.targets | keys'

# 检查是否有任何项目具有该目标
nx show projects --withTarget target
```

### "工作区不同步"

```bash
nx sync
nx reset  # 如果 sync 没有解决陈旧的缓存
```
