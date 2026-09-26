# Zustand 模式

使用 Zustand 5.x 进行现代状态管理 - 轻量级、TypeScript 优先、无样板代码。

## 概述

- 无 Redux 复杂性的全局状态
- 组件间共享状态，无需通过 props 钻探
- 使用 localStorage/sessionStorage 持久化状态
- 使用选择器实现计算/派生状态
- 需要中间件的状态（日志记录、调试工具、持久化）

## 上游覆盖（无需重述）

Zustand 的官方文档是机制说明的来源。这项技能仅包含它们之上的 OrchestKit 差异，在 `references/ork-delta.md`、`rules/` 文件和检查清单中。

| 主题 | 一方来源 |
|------|----------|
| 基本存储、`create<State>()()`、动作、异步动作 | https://github.com/pmndrs/zustand/blob/main/docs/reference/apis/create.md |
| 切片模式（拆分和组合存储） | https://github.com/pmndrs/zustand/blob/main/docs/learn/guides/slices-pattern.md |
| 类型化切片和中间件突变元组 | https://github.com/pmndrs/zustand/blob/main/docs/learn/guides/advanced-typescript.md |
| Immer 中间件（草稿突变） | https://github.com/pmndrs/zustand/blob/main/docs/reference/middlewares/immer.md |
| persist: `partialize`、`version`、`migrate`、`onRehydrateStorage`、存储适配器 | https://github.com/pmndrs/zustand/blob/main/docs/reference/middlewares/persist.md |
| devtools: 动作名称、`enabled`、`serialize`、`trace` | https://github.com/pmndrs/zustand/blob/main/docs/reference/middlewares/devtools.md |
| `subscribeWithSelector` 和非 React 订阅 | https://github.com/pmndrs/zustand/blob/main/docs/reference/middlewares/subscribe-with-selector.md |
| 选择器和 `useShallow` 重绘控制 | https://github.com/pmndrs/zustand/blob/main/docs/learn/guides/prevent-rerenders-with-use-shallow.md |
| v4 到 v5 迁移 (`createWithEqualityFn`、React 18 基础) | https://github.com/pmndrs/zustand/blob/main/docs/reference/migrations/migrating-to-v5.md |
| SSR 和 hydration | https://github.com/pmndrs/zustand/blob/main/docs/learn/guides/ssr-and-hydration.md |
| 存储测试和重置 | https://github.com/pmndrs/zustand/blob/main/docs/learn/guides/testing.md |
| 服务器状态所有权（使用 TanStack Query，而不是 Zustand） | https://tanstack.com/query/latest/docs/framework/react/guides/does-this-replace-client-state |

## 快速参考

```typescript
// ✅ 使用双调用模式创建类型化存储
const useStore = create<State>()((set, get) => ({ ... }));

// ✅ 使用选择器访问所有状态
const count = useStore((s) => s.count);

// ✅ 使用 useShallow 处理多个值（Zustand 5.x）
const { a, b } = useStore(useShallow((s) => ({ a: s.a, b: s.b })));

// ✅ 中间件顺序：immer → subscribeWithSelector → devtools → persist
create(persist(devtools(immer((set) => ({ ... })))))

// ❌ 不要解构整个存储
const store = useStore(); // 任何更改都会导致重绘

// ❌ 不要存储服务器状态（使用 TanStack Query 代替）
const useStore = create((set) => ({ users: [], fetchUsers: async () => ... }));
```

## 关键决策

| 决策 | 选项 A | 选项 B | 推荐方案 |
|------|--------|--------|----------|
| 状态结构 | 单个存储 | 多个存储 | **单个存储中的切片** - 更容易跨切片访问 |
| 嵌套更新 | 展开运算符 | Immer 中间件 | **Immer** 用于深层嵌套状态（3+ 级别） |
| 持久化 | 手动 localStorage | persist 中间件 | **persist 中间件** 配合 partialize |
| 多个值 | 多个选择器 | useShallow | **useShallow** 用于 2-5 个相关值 |
| 服务器状态 | Zustand | TanStack Query | **TanStack Query** - Zustand 用于客户端状态 |
| 调试工具 | 始终开启 | 条件开启 | **条件开启** - `enabled: process.env.NODE_ENV === 'development'` |

## 反模式与集成

禁止模式（存储解构、派生状态、服务器状态、直接突变）和 React Query 集成指南。

加载 Read("references/anti-patterns-and-integration.md") 获取反模式示例和 TanStack Query 分离模式。

## 相关技能

- `react-server-components-framework` - 使用 Zustand 的 RSC hydration 考虑事项
- 服务器状态：https://tanstack.com/query/latest/docs/framework/react/guides/does-this-replace-client-state
- 表单状态：https://react-hook-form.com/docs/useform

## 能力详情

### store-creation
**关键词**：zustand、create、store、typescript、state
**解决**：使用正确的 TypeScript 推断设置类型安全的 Zustand 存储

### slices-pattern
**关键词**：slices、modular、split、combine、StateCreator
**解决**：将大型存储组织为可维护的、特定领域的切片

### middleware-stack
**关键词**：immer、persist、devtools、middleware、compose
**解决**：按正确顺序组合中间件，以实现不可变性、持久化和调试

### selector-optimization
**关键词**：selector、useShallow、re-render、performance、memoization
**解决**：使用正确的选择器模式防止不必要的重绘

### persistence-migration
**关键词**：persist、localStorage、sessionStorage、migrate、version
**解决**：在版本之间使用架构迁移持久化状态

## 参考文献

按需加载 `Read("references/<file>")`：

| 文件 | 内容 |
|------|------|
| `ork-delta.md` | OrchestKit 特定规则：修正的 `zustand/shallow` 标签、v5 基础、密钥处理、分级切片类型化 |
| `anti-patterns-and-integration.md` | 禁止模式和 React Query 集成 |

其他资源：
- 加载：`Read("scripts/store-template.ts")` - 生产就绪的存储模板
- 加载：`Read("checklists/zustand-checklist.md")` - 实现检查清单
