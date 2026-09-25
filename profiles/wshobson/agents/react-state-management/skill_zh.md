# React 状态管理

现代 React 状态管理模式的全面指南，从本地组件状态到全局存储和服务器状态同步。

## 何时使用此技能

- 在 React 应用中设置全局状态管理
- 在 Redux Toolkit、Zustand 或 Jotai 之间进行选择
- 使用 React Query 或 SWR 管理服务器状态
- 实现乐观更新
- 调试状态相关问题
- 从遗留 Redux 迁移到现代模式

## 核心概念

### 1. 状态类别

| 类型             | 描述                  | 解决方案                     |
| ---------------- | ---------------------------- | ----------------------------- |
| **本地状态**  | 组件特定，UI 状态 | useState, useReducer          |
| **全局状态** | 跨组件共享     | Redux Toolkit, Zustand, Jotai |
| **服务器状态** | 远程数据，缓存         | React Query, SWR, RTK Query   |
| **URL 状态**    | 路由参数，查询     | React Router, nuqs            |
| **表单状态**   | 输入值，验证     | React Hook Form, Formik       |

### 2. 选择标准

```
小型应用，简单状态 → Zustand 或 Jotai
大型应用，复杂状态 → Redux Toolkit
重度服务器交互 → React Query + 轻量级客户端状态
原子/粒度更新 → Jotai
```

## 快速入门

### Zustand (最简单)

```typescript
// store/useStore.ts
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface AppState {
  user: User | null
  theme: 'light' | 'dark'
  setUser: (user: User | null) => void
  toggleTheme: () => void
}

export const useStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        theme: 'light',
        setUser: (user) => set({ user }),
        toggleTheme: () => set((state) => ({
          theme: state.theme === 'light' ? 'dark' : 'light'
        })),
      }),
      { name: 'app-storage' }
    )
  )
)

// 组件中使用
function Header() {
  const { user, theme, toggleTheme } = useStore()
  return (
    <header className={theme}>
      {user?.name}
      <button onClick={toggleTheme}>切换主题</button>
    </header>
  )
}
```

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

### 应做

- **状态局部化** - 将状态尽可能保持在使用的附近
- **使用选择器** - 通过选择性订阅防止不必要的重新渲染
- **数据归一化** - 展平嵌套结构以便于更新
- **全面类型化** - 完整的 TypeScript 覆盖防止运行时错误
- **分离关注点** - 服务器状态（React Query）与客户端状态（Zustand）

### 不应做

- **不要过度全局化** - 并非所有内容都需要全局状态
- **不要重复服务器状态** - 让 React Query 管理
- **不要直接修改** - 始终使用不可变更新
- **不要存储派生数据** - 而是计算它
- **不要混合范式** - 每个类别选择一个主要解决方案

## 迁移指南

### 从遗留 Redux 到 RTK

```typescript
// 之前（遗留 Redux）
const ADD_TODO = "ADD_TODO";
const addTodo = (text) => ({ type: ADD_TODO, payload: text });
function todosReducer(state = [], action) {
  switch (action.type) {
    case ADD_TODO:
      return [...state, { text: action.payload, completed: false }];
    default:
      return state;
  }
}

// 之后（Redux Toolkit）
const todosSlice = createSlice({
  name: "todos",
  initialState: [],
  reducers: {
    addTodo: (state, action: PayloadAction<string>) => {
      // Immer 允许“修改”
      state.push({ text: action.payload, completed: false });
    },
  },
});
```
