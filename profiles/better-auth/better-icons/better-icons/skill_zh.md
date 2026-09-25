# 更好的图标

通过 Iconify 从 200 多个库中搜索和检索图标。

## 安装

在使用任何 `better-icons` 命令之前，请确保该工具在环境中可用。

**选项 1 — 全局安装（推荐，与以下所有示例匹配）：**

```bash
# 使用 npm
npm install -g better-icons

# 使用 Bun（更快）
bun add -g better-icons
```

**选项 2 — 不安装直接运行（为每个命令前缀 `npx` 或 `bunx`）：**

```bash
# 使用 npx (npm)
npx better-icons search arrow --limit 10
npx better-icons get lucide:home > icon.svg

# 使用 bunx (Bun — 更快)
bunx better-icons search arrow --limit 10
bunx better-icons get lucide:home > icon.svg
```

> **对于 AI 代理：** 优先选择全局安装，以便 `better-icons` 在 `$PATH` 中，以下命令按原样工作。在环境设置时运行安装步骤一次，然后无需 `npx`/`bunx` 即可使用命令。

## 命令行界面 (CLI)

```bash
# 搜索图标
better-icons search <query> [--prefix <prefix>] [--limit <n>] [--json]

# 搜索并下载所有找到的图标作为 SVG 文件
better-icons search <query> -d [dir] [--color <color>] [--size <px>]

# 获取图标 SVG（输出到标准输出）
better-icons get <icon-id> [--color <color>] [--size <px>] [--json]

# 为 AI 代理设置 MCP 服务器
better-icons setup [-a cursor,claude-code] [-s global|project]
```

## 示例

```bash
better-icons search arrow --limit 10
better-icons search home --json | jq '.icons[0]'
better-icons get lucide:home > icon.svg
better-icons get mdi:home --color '#333' --json

# 批量下载所有搜索结果
better-icons search arrow -d              # 保存到 ./icons/
better-icons search check -d ./my-icons   # 保存到 ./my-icons/
better-icons search star -d -c '#000' -s 24 --limit 64
```

## 图标 ID 格式

`prefix:name` - 例如，`lucide:home`，`mdi:arrow-right`，`heroicons:check`

## 热门集合

`lucide`，`mdi`，`heroicons`，`tabler`，`ph`，`ri`，`solar`，`iconamoon`

---

## MCP 工具（用于 AI 代理）

| 工具            | 描述             |
|-----------------|------------------|
| `search_icons`  | 跨所有库搜索     |
| `get_icon`      | 获取单个图标 SVG |
| `get_icons`     | 批量检索多个图标 |
| `list_collections` | 浏览可用图标集   |
| `recommend_icons` | 为用例提供智能推荐 |
| `find_similar_icons` | 在集合中查找变体 |
| `sync_icon`     | 将图标添加到项目文件 |
| `scan_project_icons` | 列出项目中的图标 |

## TypeScript 接口

```typescript
interface SearchIcons {
  query: string
  limit?: number        // 1-999，默认 32
  prefix?: string       // 例如，'mdi'，'lucide'
  category?: string     // 例如，'General'，'Emoji'
}

interface GetIcon {
  icon_id: string       // 'prefix:name' 格式
  color?: string        // 例如，'#ff0000'，'currentColor'
  size?: number         // 像素
}

interface GetIcons {
  icon_ids: string[]    // 最大 20 个
  color?: string
  size?: number
}

interface RecommendIcons {
  use_case: string      // 例如，'navigation menu'
  style?: 'solid' | 'outline' | 'any'
  limit?: number        // 默认 10
}

interface SyncIcon {
  icons_file: string    // 绝对路径
  framework: 'react' | 'vue' | 'svelte' | 'solid' | 'svg'
  icon_id: string
  component_name?: string
}
```

## API

所有图标来自 `https://api.iconify.design`
