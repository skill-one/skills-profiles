# 模态指令 API 指南

## 推荐：`@lobehub/ui/base-ui`

新代码应使用 **base-ui** 模态栈（无头原始组件，而非 antd `Modal`）：

- `createModal`、`confirmModal`、`ModalHost` 来自 `@lobehub/ui/base-ui`
- 在模态 **内容** 中使用 `useModalContext` 来自 `@lobehub/ui/base-ui`

主体插槽：传递 **`content`**（或 `children`；运行时使用 `content ?? children`）。

### 全局 `ModalHost`（必需）

Base-ui 的 `createModal` 通过与根包**分离**的主机渲染。应用必须在靠近根（例如与其他全局主机相邻）处挂载 **`ModalHost`** 来自 `@lobehub/ui/base-ui`。没有它，`createModal` 调用将不会显示。

如果项目仅挂载 `@lobehub/ui` 的 `ModalHost`，则添加第二个来自 `@lobehub/ui/base-ui` 的懒加载 `ModalHost`，直到所有指令式模态迁移完成。

### 为什么使用指令式？

| 模式        | 特点                          | 推荐 |
| ----------- | ----------------------------- | ---- |
| 声明式      | `open` 状态 + `<Modal />`     | ❌   |
| 指令式      | 调用 `createModal()`，无本地状态 | ✅   |

### 文件结构

```
features/
└── MyFeatureModal/
    ├── index.tsx            # 导出 createXxxModal
    └── MyFeatureContent.tsx # 模态主体
```

### 1. 内容 (`MyFeatureContent.tsx`)

```tsx
'use client';

import { useModalContext } from '@lobehub/ui/base-ui';
import { useTranslation } from 'react-i18next';

export const MyFeatureContent = () => {
  const { t } = useTranslation('namespace');
  const { close } = useModalContext();

  return <div>{/* ... */}</div>;
};
```

### 2. `createModal` (`index.tsx`)

```tsx
'use client';

import { createModal } from '@lobehub/ui/base-ui';
import { t } from 'i18next';

import { MyFeatureContent } from './MyFeatureContent';

export const createMyFeatureModal = () =>
  createModal({
    content: <MyFeatureContent />,
    footer: null,
    maskClosable: true,
    styles: {
      content: { overflow: 'hidden', padding: 0 },
    },
    title: t('myFeature.title', { ns: 'setting' }),
    width: 'min(80%, 800px)',
  });
```

### 3. 使用方法

```tsx
import { createMyFeatureModal } from '@/features/MyFeatureModal';

const handleOpen = useCallback(() => {
  createMyFeatureModal();
}, []);

return <Button onClick={handleOpen}>打开</Button>;
```

### i18n

- **内容**：组件中的 `useTranslation`。
- **`createModal` 选项**：在钩子不可用时，使用 `import { t } from 'i18next'`。

### `useModalContext`

```tsx
const { close, setCanDismissByClickOutside } = useModalContext();
```

### 关闭：哪个回调实际触发

`close()` — 来自内容中的 `useModalContext()`，或来自返回的
`ModalInstance` — 仅将栈条目切换为 `open: false`。它不通过 base-ui 的关闭路径，因此：

| 回调               | 用户关闭（Esc / 背景遮罩 / 头部 ✕） | 内容或实例的 `close()` |
| ------------------ | ----------------------------------- | --------------------- |
| `onOpenChange`     | 触发                                | **不触发**            |
| `onOpenChangeComplete` | 带有 `false` 触发                  | 带有 `false` 触发     |

将调用端清理（清除编辑标志、重置提供者的 `open` 状态）放在 **`onOpenChangeComplete`** 上。将其连接到 `onOpenChange` 看起来正确，直到底部按钮关闭模态，然后调用者永远不会知道它已关闭 — 通常会留下一个标志，导致模态无法重新打开。

`createModal` 仅在 `false` 完成时（指令式渲染器自己提供参数，从不将属性转发给 base-ui），但仍然需要保护 — 其他 base-ui 原始组件（如 `DropdownMenu`）确实报告双向，而保护措施使调用端不依赖于这种差异：

```tsx
onOpenChangeComplete: (open) => {
  if (!open) onClosed?.();
},
```

### 常见选项（base-ui）

`ImperativeModalProps` 基于 `BaseModalProps`：`title`、`width`、`maskClosable`、`open`、`onOpenChange`、`footer`、`styles` / `classNames`（键：`backdrop`、`popup`、`header`、`title`、`close`、`content`、…）。

| 属性       | 备注                                  |
| ---------- | ------------------------------------- |
| `content`  | 主干（与 `children` 的首选名称）      |
| `maskClosable` | 点击外部关闭                         |
| `styles.*` | 语义区域，非 antd `styles.body`        |

### 确认

```tsx
import { confirmModal } from '@lobehub/ui/base-ui';

confirmModal({
  title: '…',
  content: '…',
  okText: '…',
  cancelText: '…',
  onOk: async () => {},
});
```

---

## 传统：`@lobehub/ui`（根）

较旧的调用站点使用来自 **`@lobehub/ui`** 的 **`createModal`**，其类型为 **antd `Modal` 属性**（`children`、`allowFullscreen`、`getContainer`、`destroyOnHidden`、`styles.body` 等）。优先将新工作迁移到 **`@lobehub/ui/base-ui`**。

示例（传统）：`src/features/SkillStore/index.tsx`、`src/features/LibraryModal/CreateNew/index.tsx`。

---

## 示例

- Base-ui（推荐）：遵循上述部分；确保挂载 **base-ui `ModalHost`**。
- 传统：`src/features/SkillStore/index.tsx`、`src/features/LibraryModal/CreateNew/index.tsx`
