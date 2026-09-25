# React 组合模式

构建灵活、可维护的 React 组件的组合模式。通过使用复合组件、提升状态和组合内部结构来避免布尔类型属性（boolean prop）的泛滥。这些模式使代码库在扩展时对人类和 AI 代理都更容易使用。

## 何时应用

在以下情况下参考这些指南：

- 重构具有许多布尔类型属性的组件
- 构建可重用的组件库
- 设计灵活的组件 API
- 审查组件架构
- 使用复合组件或上下文提供者

## 按优先级分类的规则类别

| 优先级 | 类别                | 影响 | 前缀          |
| ------ | ----------------------- | ------ | --------------- |
| 1        | 组件架构  | 高   | `architecture-` |
| 2        | 状态管理        | 中   | `state-`        |
| 3        | 实现模式     | 中   | `patterns-`     |
| 4        | React 19 API     | 中   | `react19-`      |

## 快速参考

### 1. 组件架构 (高)

- `architecture-avoid-boolean-props` - 不要添加布尔类型属性来自定义行为；使用组合
- `architecture-compound-components` - 使用共享上下文结构复杂组件

### 2. 状态管理 (中)

- `state-decouple-implementation` - 提供者（Provider）是唯一知道状态如何管理的位置
- `state-context-interface` - 定义具有状态、操作、元数据的通用接口用于依赖注入
- `state-lift-state` - 将状态移动到提供者组件中以便兄弟组件访问

### 3. 实现模式 (中)

- `patterns-explicit-variants` - 创建显式的变体组件而不是布尔类型模式
- `patterns-children-over-render-props` - 使用子组件（children）进行组合而不是 renderX 属性

### 4. React 19 API (中)

> **⚠️ 仅适用于 React 19+。** 如果使用 React 18 或更早版本，请跳过此部分。

- `react19-no-forwardref` - 不要使用 `forwardRef`；使用 `use()` 而不是 `useContext()`

## 如何使用

阅读单个规则文件以获取详细解释和代码示例：

```
rules/architecture-avoid-boolean-props.md
rules/state-context-interface.md
```

每个规则文件包含：

- 解释为什么它很重要
- 带有解释的错误代码示例
- 带有解释的正确代码示例
- 额外的上下文和参考

## 完整编译文档

要获取包含所有规则展开的完整指南：`AGENTS.md`
