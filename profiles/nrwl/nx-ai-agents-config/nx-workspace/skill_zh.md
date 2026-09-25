# Nx 工作区探索

本技能提供对 Nx 工作区的只读探索。使用它可以了解工作区结构、项目配置、可用目标及依赖项。

请记住，如果 nx 未全局安装，则可能需要在使用命令时加上 `npx`/`pnpx`/`yarn` 前缀。请检查锁文件以确定所使用的包管理器。

## 列出项目

使用 `nx show projects` 列出工作区中的项目。

项目过滤语法（`-p`/`--projects`）可在许多 Nx 命令中使用，包括 `nx run-many`、`nx release`、`nx show projects` 等。过滤器支持显式名称、全局模式、标签引用（例如 `tag:name`）、目录以及否定（例如 `!project-name`）。

```bash
# List all projects
nx show projects

# Filter by pattern (glob)
nx show projects --projects "apps/*"
nx show projects --projects "shared-*"

# Filter by tag
nx show projects --projects "tag:publishable"
nx show projects -p 'tag:publishable,!tag:internal'

# Filter by target (projects that have a specific target)
nx show projects --withTarget build

# Combine filters
nx show projects --type lib --withTarget test
nx show projects --affected --exclude="*-e2e"
nx show projects -p "tag:scope:client,packages/*"

# Negate patterns
nx show projects -p '!tag:private'
nx show projects -p '!*-e2e'

# Output as JSON
nx show projects --json
```

## 项目配置

使用 `nx show project <name>` --json` 获取项目的完整解析配置。

**重要**：请勿直接读取 `project.json` -它仅包含部分配置。`nx show project --json` 命令会返回完整的解析配置，包括从插件中推断出的目标。

您可以查阅位于 `node_modules/nx/schemas/project-schema.json` 的完整项目架构，以了解 Nx 项目配置选项。

```bash
# Get full project configuration
nx show project my-app --json

# Extract specific parts from the JSON
nx show project my-app --json | jq '.targets'
nx show project my-app --json | jq '.targets.build'
nx show project my-app --json | jq '.targets | keys'

# Check project metadata
nx show project my-app --json | jq '{name, root, sourceRoot, projectType, tags}'
```

## 目标信息

目标定义了可以在项目上运行的任务。

```bash
# List all targets for a project
nx show project my-app --json | jq '.targets | keys'

# Get full target configuration
nx show project my-app --json | jq '.targets.build'

# Check target executor/command
nx show project my-app --json | jq '.targets.build.executor'
nx show project my-app --json | jq '.targets.build.command'

# View target options
nx show project my-app --json | jq '.targets.build.options'

# Check target inputs/outputs (for caching)
nx show project my-app --json | jq '.targets.build.inputs'
nx show project my-app --json | jq '.targets.build.outputs'

# Find projects with a specific target
nx show projects --withTarget serve
nx show projects --withTarget e2e
```

## 工作区配置

直接读取 `nx.json` 以获取工作区级别配置。
您可以查阅位于 `node_modules/nx/schemas/nx-schema.json` 的完整项目架构，以了解 Nx 项目配置选项。

```bash
# Read the full nx.json
cat nx.json

# Or use jq for specific sections
cat nx.json | jq '.targetDefaults'
cat nx.json | jq '.namedInputs'
cat nx.json | jq '.plugins'
cat nx.json | jq '.generators'
```

`nx.json` 的关键部分：

- `targetDefaults` - 针对特定名称的所有目标应用的默认配置
- `namedInputs` - 用于缓存的可复用输入定义
- `plugins` - Nx 插件及其配置
- `...以及更多，请查阅架构或 nx.json 了解详情`

## 受影响的项目

如果用户询问的是受影响的项目，请阅读[受影响的项目的参考文档](references/AFFECTED.md)以获取详细的命令和示例。

## 常见的探索模式

### “此工作区中有哪些内容？”

```bash
nx show projects
nx show projects --type app
nx show projects --type lib
```

### “如何为项目 X 构建/测试/检查？”

```bash
nx show project X --json | jq '.targets | keys'
nx show project X --json | jq '.targets.build'
```

### “什么项目依赖 Y 库？”

```bash
# Use the project graph to find dependents
nx graph --print | jq '.graph.dependencies | to_entries[] | select(.value[].target == "Y") | .key'
```

## 程序化回答

在处理 Nx CLI 结果时，请使用命令行工具以编程方式计算结果，而非手动统计或解析输出。始终使用 `--json` 标志以获取结构化输出，该输出可使用 `jq`、`grep` 或其他已本地安装的工具进行处理。

### 列出项目

```bash
nx show projects --json
```

示例输出：

```json
["my-app", "my-app-e2e", "shared-ui", "shared-utils", "api"]
```

常用操作：

```bash
# Count projects
nx show projects --json | jq 'length'

# Filter by pattern
nx show projects --json | jq '.[] | select(startswith("shared-"))'

# Get affected projects as array
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
  "intermediateDependencies": []
}
```

常用操作：

```bash
# Get target names
nx show project my-app --json | jq '.targets | keys'

# Get specific target config
nx show project my-app --json | jq '.targets.build'

# Get tags
nx show project my-app --json | jq '.tags'

# Get project root
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

常用操作：

```bash
# Get all project names from graph
nx graph --print | jq '.graph.nodes | keys'

# Find dependencies of a project
nx graph --print | jq '.graph.dependencies["my-app"]'

# Find projects that depend on a library
nx graph --print | jq '.graph.dependencies | to_entries[] | select(.value[].target == "shared-ui") | .key'
```

## 故障排除

### “无法找到任务 X:target 的配置”

```bash
# Check what targets exist on the project
nx show project X --json | jq '.targets | keys'

# Check if any projects have that target
nx show projects --withTarget target
```

### “工作区不同步”

```bash
nx sync
nx reset  # if sync doesn't fix stale cache
```
