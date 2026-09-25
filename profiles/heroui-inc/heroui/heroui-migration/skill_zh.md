# HeroUI v2到v3迁移指南

本技能帮助代理将HeroUI v2应用程序迁移到v3。HeroUI v3引入了破坏性变更：复合组件、无Provider、Tailwind v4以及移除的hooks。

---

## 安装

```bash
curl -fsSL https://heroui.com/install | bash -s heroui-migration
```

---

## 关键提示：应用变更前始终获取迁移文档

**不要假设v2模式在v3中有效。** 应用变更前始终获取迁移指南。

### v2 → v3关键变更

| 功能       | v2（迁移来源）          | v3（迁移目标）                        |
| ------------- | -------------------------- | -------------------------------------- |
| Provider      | `<HeroUIProvider>`必需 | **无需Provider**                 |
| 组件API | 平铺属性: `<Card title="x">` | 复合: `<Card><Card.Header>`      |
| 事件处理器 | `onClick`                 | `onPress`                              |
| 样式       | `classNames`属性         | `className`属性                       |
| Hooks         | `useSwitch`, `useDisclosure`, 等. | 复合组件, `useOverlayState` |
| 包       | `@heroui/system`, `@heroui/theme` | `@heroui/react`, `@heroui/styles` |

---

## 访问迁移文档

**为获取迁移细节、示例和分步指南，始终获取文档：**

### 使用脚本

```bash
# 列出所有可用的组件迁移指南
node scripts/list_migration_guides.mjs

# 获取主要迁移工作流（完整或增量）
node scripts/get_migration_guide.mjs full
node scripts/get_migration_guide.mjs incremental

# 获取特定组件的迁移指南
node scripts/get_component_migration_guides.mjs button
node scripts/get_component_migration_guides.mjs button card modal

# 获取样式迁移指南
node scripts/get_styling_migration_guide.mjs

# 获取hooks迁移指南
node scripts/get_hooks_migration_guide.mjs
```

### 直接URL

迁移文档（预览）：使用以下示例中的具体指南URL，切勿获取仍包含占位符的URL。

示例：

- 完整迁移: `.../agent-guide-full.mdx`
- 增量: `.../agent-guide-incremental.mdx`
- 按钮: `.../button.mdx`
- 样式: `.../styling.mdx`
- Hooks: `.../hooks.mdx`

当文档合并到生产环境时，使用`HEROUI_MIGRATION_DOCS_BASE`覆盖基本URL。

### MCP替代方案

使用Cursor或其他MCP客户端时，配置迁移MCP服务器以基于工具访问：

```json
{
  "mcpServers": {
    "heroui-migration": {
      "url": "https://migration-mcp.heroui.com"
    }
  }
}
```

---

## 迁移策略

### 完整迁移

- 最佳适用场景：可以投入专注时间的项目；团队对暂时性破坏代码感到舒适
- 首先迁移所有组件代码（迁移期间项目会中断）
- 切换依赖到v3
- 完成样式迁移

### 增量迁移

- 最佳适用场景：必须保持功能的项目；逐步迁移的大型代码库
- 设置共存（pnpm别名或组件包）
- 逐个迁移组件
- 迁移期间v2和v3共存

**开始前始终获取代理指南：** `node scripts/get_migration_guide.mjs full` 或 `incremental`

---

## 核心原则

1. **先获取文档**：在应用变更前使用脚本获取迁移指南
2. **复合组件**：v3使用`Card.Header`, `Card.Title`, `Button`带子元素——而非平铺属性
3. **无Provider**：迁移时移除`HeroUIProvider`
4. **onPress而非onClick**：所有交互组件使用`onPress`
5. **工作流**：分析 → 迁移组件 → 切换依赖 → 样式迁移

---

## 迁移工作流概要

1. 创建迁移分支
2. 分析项目（HeroUI导入、组件使用）
3. 获取主要指南: `node scripts/get_migration_guide.mjs full`
4. 批量迁移组件（每批获取组件指南）
5. 切换依赖到v3
6. 获取样式指南: `node scripts/get_styling_migration_guide.mjs`
7. 应用样式更新

---

## 预览模式

本技能针对`docs/migration`分支的staging部署。一旦文档合并到main并在heroui.com上线，设置`HEROUI_MIGRATION_DOCS_BASE=https://heroui.com/docs/react/migration`或更新脚本中的默认值。
