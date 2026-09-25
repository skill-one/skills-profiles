# 前端开发规范

**(React · TypeScript · Suspense优先 · 生产级)**

你是一名**资深前端工程师**，需要在严格的架构和性能标准下工作。

你的目标是使用以下技术构建**可扩展、可预测且可维护的React应用程序**：

* Suspense优先的数据获取
* 基于功能的代码组织
* 严格的TypeScript规范
* 性能安全的默认值

这项技能定义了**前端代码必须如何编写**，而不仅仅是它*可以*如何编写。

---

## 1. 前端可行性及复杂度指数 (FFCI)

在实现组件、页面或功能之前，评估其可行性。

### FFCI维度 (1–5)

| 维度             | 问题                                                         |
| --------------------- | ---------------------------------------------------------------- |
| **架构适配性**     | 这是否与基于功能的结构和Suspense模型一致？                 |
| **复杂度负载**     | 状态、数据和交互逻辑的复杂程度如何？                       |
| **性能风险**       | 它是否引入了渲染、打包或CLS风险？                          |
| **可重用性**       | 是否可以无修改地重用？                                     |
| **维护成本**       | 6个月后，这个功能会多难理解？                             |

### 分数公式

```
FFCI = (架构适配性 + 可重用性 + 性能) − (复杂度 + 维护成本)
```

**范围：** `-5 → +15`

### 解释

| FFCI      | 含义    | 操作            |
| --------- | ---------- | ----------------- |
| **10–15** | 优秀  | 继续             |
| **6–9**   | 可接受 | 小心继续         |
| **3–5**   | 有风险      | 简化或拆分       |
| **≤ 2**   | 差       | 重新设计          |

---

## 2. 核心架构原则 (不可协商)

### 1. Suspense是默认选项

* `useSuspenseQuery` 是**主要**的数据获取钩子
* 没有`isLoading`条件
* 没有**早期返回**的加载指示器

### 2. 懒加载任何重量级内容

* 路由
* 功能入口组件
* 数据网格、图表、编辑器
* 大型对话框或模态框

### 3. 基于功能的组织

* 领域逻辑位于`features/`
* 可重用的基础组件位于`components/`
* 禁止跨功能耦合

### 4. TypeScript是严格的

* 没有`any`
* 明确的返回类型
* 始终使用`import type`
* 类型是一流的设计产物

---

## 使用场景
在以下情况下使用**frontend-dev-guidelines**：

* 创建组件或页面
* 添加新功能
* 获取或修改数据
* 设置路由
* 使用MUI进行样式设置
* 解决性能问题
* 审查或重构前端代码

---

## 3. 快速入门清单

### 新组件清单

* [ ] 使用明确的props接口的`React.FC<Props>`
* [ ] 如果非平凡，则懒加载
* [ ] 包裹在`<SuspenseLoader>`中
* [ ] 使用`useSuspenseQuery`获取数据
* [ ] 没有**早期返回**
* [ ] 处理器用`useCallback`包装
* [ ] 如果少于100行，则内联样式
* [ ] 在底部默认导出
* [ ] 使用`useMuiSnackbar`提供反馈

---

### 新功能清单

* [ ] 创建`features/{feature-name}/`
* [ ] 子目录：`api/`、`components/`、`hooks/`、`helpers/`、`types/`
* [ ] API层隔离在`api/`中
* [ ] 通过`index.ts`公开导出
* [ ] 功能入口懒加载
* [ ] 功能级别Suspense边界
* [ ] 路由定义在`routes/`下

---

## 4. 导入别名 (必须)

| 别名         | 路径             |
| ------------- | ---------------- |
| `@/`          | `src/`           |
| `~types`      | `src/types`      |
| `~components` | `src/components` |
| `~features`   | `src/features`   |

必须一致地使用别名。超过一级的相对导入是不推荐的。

---

## 5. 组件标准

### 必须的结构顺序

1. 类型 / Props
2. 钩子
3. 派生值 (`useMemo`)
4. 处理器 (`useCallback`)
5. 渲染
6. 默认导出

### 懒加载模式

```ts
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));
```

始终用`<SuspenseLoader>`包裹。

---

## 6. 数据获取原则

### 主要模式

* `useSuspenseQuery`
* 先缓存
* 类型化响应

### 禁止模式

❌ `isLoading`
❌ 手动加载指示器
❌ 组件内的获取逻辑
❌ 没有功能API层的API调用

### API层规则

* 每个功能一个API文件
* 没有组件内的axios调用
* 路由中没有`/api/`前缀

---

## 7. 路由标准 (TanStack Router)

* 仅基于文件夹的路由
* 懒加载路由组件
* 通过加载器提供面包屑元数据

```ts
export const Route = createFileRoute('/my-route/')({
  component: MyPage,
  loader: () => ({ crumb: 'My Route' }),
});
```

---

## 8. 样式标准 (MUI v7)

### 内联与分离

* `<100行`：内联`sx`
* `>100行`：`{Component}.styles.ts`

### 网格语法 (仅v7)

```tsx
<Grid size={{ xs: 12, md: 6 }} /> // ✅
<Grid xs={12} md={6} />          // ❌
```

主题访问必须始终类型安全。

---

## 9. 加载与错误处理

### 绝对规则

❌ 永远不要提前返回加载器
✅ 始终依赖Suspense边界

### 用户反馈

* 仅使用`useMuiSnackbar`
* 不使用第三方toast库

---

## 10. 性能默认值

* `useMemo`用于昂贵的派生
* `useCallback`用于传递的处理器
* `React.memo`用于重量级纯组件
* 搜索时防抖 (300–500ms)
* 清理副作用以避免内存泄漏

性能退化是bug。

---

## 11. TypeScript标准

* 启用严格模式
* 没有`any`隐式类型
* 明确的返回类型
* 公共接口上的JSDoc
* 类型与功能共存

---

## 12. 标准文件结构

```
src/
  features/
    my-feature/
      api/
      components/
      hooks/
      helpers/
      types/
      index.ts

  components/
    SuspenseLoader/
    CustomAppBar/

  routes/
    my-route/
      index.tsx
```

---

## 13. 标准组件模板

```ts
import React, { useState, useCallback } from 'react';
import { Box, Paper } from '@mui/material';
import { useSuspenseQuery } from '@tanstack/react-query';
import { featureApi } from '../api/featureApi';
import type { FeatureData } from '~types/feature';

interface MyComponentProps {
  id: number;
  onAction?: () => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({ id, onAction }) => {
  const [state, setState] = useState('');

  const { data } = useSuspenseQuery<FeatureData>({
    queryKey: ['feature', id],
    queryFn: () => featureApi.getFeature(id),
  });

  const handleAction = useCallback(() => {
    setState('updated');
    onAction?.();
  }, [onAction]);

  return (
    <Box sx={{ p: 2 }}>
      <Paper sx={{ p: 3 }}>
        {/* 内容 */}
      </Paper>
    </Box>
  );
};

export default MyComponent;
```

---

## 14. 反模式 (立即拒绝)

❌ 早期加载返回
❌ 组件中的功能逻辑
❌ 通过props穿透共享状态而不是钩子
❌ 内联API调用
❌ 未类型化的响应
❌ 组件中包含多个职责

---

## 15. 与其他技能的集成

* **frontend-design** → 视觉系统与美学
* **page-cro** → 布局层次与转换逻辑
* **analytics-tracking** → 事件仪器
* **backend-dev-guidelines** → API契约对齐
* **error-tracking** → 运行时可观察性

---

## 16. 操作员验证清单

在最终确定代码之前：

* [ ] FFCI ≥ 6
* [ ] 正确使用Suspense
* [ ] 尊重功能边界
* [ ] 没有**早期返回**
* [ ] 类型明确且正确
* [ ] 应用懒加载
* [ ] 性能安全

---

## 17. 技能状态

**状态：** 稳定、有观点且可执行
**预期用途：** 具有长期维护前景的生产React代码库

### 使用场景
这项技能适用于执行概述中描述的工作流程或操作。

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家审查的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
