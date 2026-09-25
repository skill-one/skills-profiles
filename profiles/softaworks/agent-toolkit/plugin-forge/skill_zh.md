# CC 插件锻造工具

## 目的

构建和管理具有正确结构的 Claude 代码插件，包括清单文件和市集集成。包含工作流、自动化脚本和参考文档。

## 使用场景

- 为市集创建新插件
- 添加/修改插件组件（命令、技能、代理、钩子）
- 更新插件版本
- 处理插件或市集清单文件
- 设置本地插件测试
- 发布插件

## 快速入门

### 创建新插件

使用 `create_plugin.py` 生成插件结构：

```bash
python scripts/create_plugin.py 插件名称 \
  --marketplace-root /path/to/marketplace \
  --author-name "您的姓名" \
  --author-email "your.email@example.com" \
  --description "插件描述" \
  --keywords "keyword1,keyword2" \
  --category "productivity"
```

这会自动：

- 创建插件目录结构
- 生成 `plugin.json` 清单文件
- 创建 README 模板
- 更新 `marketplace.json`

### 版本更新

使用 `bump_version.py` 更新两个清单文件中的版本：

```bash
python scripts/bump_version.py 插件名称 major|minor|patch \
  --marketplace-root /path/to/marketplace
```

语义化版本控制：

- **major**：破坏性变更（1.0.0 → 2.0.0）
- **minor**：新功能、重构（1.0.0 → 1.1.0）
- **patch**：修复错误、文档（1.0.0 → 1.0.1）

## 开发工作流

### 1. 创建结构

手动方法（如果未使用脚本）：

```bash
mkdir -p plugins/plugin-name/.claude-plugin
mkdir -p plugins/plugin-name/commands
mkdir -p plugins/plugin-name/skills
```

### 2. 插件清单

文件：`plugins/plugin-name/.claude-plugin/plugin.json`

```json
{
  "name": "插件名称",
  "version": "0.1.0",
  "description": "插件描述",
  "author": {
    "name": "您的姓名",
    "email": "your.email@example.com"
  },
  "keywords": ["keyword1", "keyword2"]
}
```

### 3. 市集注册

更新 `.claude-plugin/marketplace.json`：

```json
{
  "name": "插件名称",
  "source": "./plugins/plugin-name",
  "description": "插件描述",
  "version": "0.1.0",
  "keywords": ["keyword1", "keyword2"],
  "category": "productivity"
}
```

### 4. 添加组件

在相应目录中创建：

| 组件 | 位置 | 格式 |
|------|------|------|
| 命令 | `commands/` | 带前导块的 Markdown |
| 技能 | `skills/<名称>/` | 带有 `SKILL.md` 的目录 |
| 代理 | `agents/` | Markdown 定义 |
| 钩子 | `hooks/hooks.json` | 事件处理器 |
| MCP 服务器 | `.mcp.json` | 外部集成 |

### 5. 本地测试

```bash
# 添加市集
/plugin marketplace add /path/to/marketplace-root

# 安装插件
/plugin install 插件名称@marketplace名称

# 修改后：重新安装
/plugin uninstall 插件名称@marketplace名称
/plugin install 插件名称@marketplace名称
```

## 插件模式

### 框架插件

用于特定框架指导（React、Vue 等）：

```
plugins/framework-name/
├── .claude-plugin/plugin.json
├── skills/
│   └── framework-name/
│       ├── SKILL.md
│       └── references/
├── commands/
│   └── prime/
│       ├── components.md
│       └── framework.md
└── README.md
```

### 工具插件

用于工具和命令：

```
plugins/utility-name/
├── .claude-plugin/plugin.json
├── commands/
│   ├── action1.md
│   └── action2.md
└── README.md
```

### 领域插件

用于特定领域知识：

```
plugins/domain-name/
├── .claude-plugin/plugin.json
├── skills/
│   └── domain-name/
│       ├── SKILL.md
│       ├── references/
│       └── scripts/
└── README.md
```

## 命令命名

基于子目录的命名空间，使用 `:` 分隔符：

- `commands/namespace/command.md` → `/namespace:command`
- `commands/simple.md` → `/simple`

示例：

- `commands/prime/vue.md` → `/prime:vue`
- `commands/docs/generate.md` → `/docs:generate`

## 版本管理

**重要提示**：在两个位置更新版本：

1. `plugins/<名称>/.claude-plugin/plugin.json`
2. `.claude-plugin/marketplace.json`

使用 `bump_version.py` 自动化。

## Git 提交

使用常规提交：

```bash
git commit -m "feat: 添加新插件"
git commit -m "fix: 修正插件清单"
git commit -m "docs: 更新插件 README"
git commit -m "feat!: 破坏性变更"
```

## 参考文档

包含详细文档：

| 参考 | 内容 |
|------|------|
| `references/plugin-structure.md` | 目录结构、清单文件模式、组件 |
| `references/marketplace-schema.md` | 市集格式、插件条目、分发 |
| `references/workflows.md` | 步骤式工作流、模式、发布 |

### 脚本

| 脚本 | 目的 |
|------|------|
| `scripts/create_plugin.py` | 框架新插件 |
| `scripts/bump_version.py` | 更新版本 |
