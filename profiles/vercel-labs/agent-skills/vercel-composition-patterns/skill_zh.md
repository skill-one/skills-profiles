# React 组合模式

构建灵活、可维护的 React 组件的组合模式。通过使用复合组件、状态提升与组合内部逻辑，避免布尔属性过多。这些模式使代码库在扩展时，能够使人（人类）与 AI 代理都更易于协作。

## 适用场景

当以下情况时，请参考这些指南：

- 重构具有大量布尔属性的组件
- 构建可复用的组件库
- 设计灵活的组件 API
- 审查组件架构
- 使用复合组件或上下文提供者

## 按优先级划分的规则类别

| 优先级 | 类别                | 影响 | 前缀          |
| -------- | ----------------------- | ------ | --------------- |
| 1        | 组件架构              | HIGH   | `architecture-` |
| 2        | 状态管理              | MEDIUM | `state-`        |
| 3        | 实现模式              | MEDIUM | `patterns-`     |
| 4        | React 19 API          | MEDIUM | `react19-`      |

## 快速参考

### 1. 组件架构（HIGH）

- `architecture-avoid-boolean-props` - 不要添加布尔属性来定制行为；使用组合
- `architecture-compound-components` - 使用共享上下文来构建复杂组件的结构

### 2. 状态管理（MEDIUM）

- `state-decouple-implementation` - Provider 是唯一知道状态如何管理的组件
- `state-context-interface` - 定义包含 state、actions、meta 的通用接口，用于依赖注入
- `state-lift-state` - 将状态移至 provider 组件中，以便兄弟组件访问

### 3. 实现模式（MEDIUM）

- `patterns-explicit-variants` - 创建显式的变体组件，而非使用布尔模式
- `patterns-children-over-render-props` - 使用子组件进行组合，而非使用 renderX 属性

### 4. React 19 API（MEDIUM）

> **⚠️ 仅适用于 React 19+。** 若使用 React 18 或更早版本，请跳过本节。

- `react19-no-forwardref` - 不要使用 `forwardRef`；使用 `use()` 而非 `useContext()`

## 使用方法

阅读单个规则文件以获取详细的解释和代码示例：

```
rules/architecture-avoid-boolean-props.md
rules/state-context-interface.md
```

每个规则文件包含：

- 说明其重要性的简要解释
- 带解释的错误代码示例
- 带解释的正确代码示例
- 额外上下文与参考

## 完整编译文档

“完整的、所有规则均已展开的指南文件：`AGENTS.md`”
