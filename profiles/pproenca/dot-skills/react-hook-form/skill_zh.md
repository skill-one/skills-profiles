# 社区 React Hook Form 最佳实践

React Hook Form 应用程序的全面性能优化指南。包含 7 个类别中的 35 条规则，每条规则都指出了一个默认情况下会出错的决策。已针对 react-hook-form **7.82.0** 进行验证。

## 何时应用

在以下情况下参考这些指南：
- 使用 React Hook Form 编写新表单
- 配置 useForm 选项（mode、defaultValues、validation）
- 使用 watch / useWatch / subscribe 订阅表单值
- 集成受控 UI 组件（MUI、shadcn、Ant Design）
- 使用 useFieldArray 管理动态字段数组
- 处理异步提交、服务器错误和提交生命周期状态
- 审查表单性能问题

## 何时不使用此技能

- **React 19 Server Actions / `useActionState`** — 请使用 `react-19` 技能
- **深层嵌套、完全类型安全的表单** — 对于具有复杂嵌套模式的表单，TanStack Form 可能是更好的选择；此技能假设您已经选择了 RHF
- **单输入或简单表单** — 未受控的 `<form>` + `FormData` 通常比引入任何库更简单

## 按优先级排序的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 表单配置 | CRITICAL | `formcfg-` |
| 2 | 字段订阅 | CRITICAL | `sub-` |
| 3 | 受控组件 | HIGH | `ctrl-` |
| 4 | 验证模式 | HIGH | `valid-` |
| 5 | 状态管理 | MEDIUM-HIGH | `formstate-` |
| 6 | 字段数组 | MEDIUM-HIGH | `array-` |
| 7 | 集成模式 | MEDIUM | `integ-` |

## 快速参考

### 1. 表单配置 (CRITICAL)

- `formcfg-default-values` - 表单初始化时始终提供 defaultValues
- `formcfg-useeffect-dependency` - 依赖表单状态切片，而不是表单状态本身
- `formcfg-validation-mode` - 除非默认的 onSubmit 外，否则合理化任何其他模式
- `formcfg-revalidate-mode` - 除非验证成本高昂，否则保持默认的 reValidateMode
- `formcfg-should-unregister` - 除非隐藏字段必须离开负载，否则保持 shouldUnregister 关闭
- `formcfg-transformed-values-generic` - 当解析器转换值时，传递第三个 useForm 泛型
- `formcfg-async-default-values` - 使用异步 defaultValues 处理服务器数据
- `formcfg-disabled-prop` - 使用 HTML disabled 属性进行视觉禁用，而不是 register 的 disabled 选项
- `formcfg-values-prop` - 使用 values 属性使表单与服务器数据保持同步

### 2. 字段订阅 (CRITICAL)

- `sub-avoid-watch-in-render` - 避免在渲染中调用 watch() 进行一次性读取
- `sub-memo-cannot-beat-context` - React.memo 无法阻止 FormProvider 下的上下文驱动重新渲染
- `sub-subscribe-outside-react` - 使用 subscribe() 订阅 React 生命周期外的表单变化
- `sub-render-prop-components` - 使用 Render-Prop 组件隔离没有子组件的重新渲染
- `sub-useformcontext-sparingly` - 对于深层嵌套，谨慎使用 useFormContext
- `sub-usewatch-over-watch` - 使用 useWatch 而不是 watch 进行隔离的重新渲染
- `sub-watch-specific-fields` - 订阅特定字段而不是整个表单

### 3. 受控组件 (HIGH)

- `ctrl-usecontroller-isolation` - 在专用的子组件中隔离受控输入
- `ctrl-controller-field-props` - 正确连接控制器字段属性以用于 UI 库

### 4. 验证模式 (HIGH)

- `valid-resolver-caching` - 一次构建验证模式，在渲染路径之外
- `valid-valueasnumber-empty-nan` - 处理空输入产生的 NaN 值
- `valid-server-errors` - 通过 setError('root.serverError', ...) 提交服务器错误
- `valid-delay-error` - 使用 delayError 防抖快速错误显示

### 5. 状态管理 (MEDIUM-HIGH)

- `formstate-avoid-isvalid-with-onsubmit` - 对于按钮状态，避免在 onSubmit 模式下使用 isValid
- `formstate-destructure-formstate` - 在渲染期间读取您依赖的每个 formState 属性
- `formstate-reset-default-values` - 成功保存后使用 resetDefaultValues 重新基于默认值
- `formstate-handlesubmit-oninvalid` - 使用 handleSubmit 的第二个参数处理拒绝的提交
- `formstate-useformstate-isolation` - 使用 useFormState 进行隔离的状态订阅
- `formstate-async-submit-lifecycle` - 将异步提交处理程序包装在 try/catch 中，并在 isSubmitSuccessful 时重置

### 6. 字段数组 (MEDIUM-HIGH)

- `array-separate-crud-operations` - 分离顺序字段数组操作
- `array-use-field-id-as-key` - 在 useFieldArray 映射中使用 field.id 作为键
- `array-unique-fieldarray-per-name` - 每个字段名使用单个 useFieldArray 实例
- `array-disabled-silently-noops` - useFieldArray 的 disabled 选项使每个变更成为静默的无操作

### 7. 集成模式 (MEDIUM)

- `integ-value-transform` - 在控制器级别转换值以进行类型强制
- `integ-shadcn-form-import` - 验证 shadcn 表单组件导入源
- `integ-shadcn-select-wiring` - 使用 onValueChange 而不是展开连接 shadcn Select

## 如何使用

阅读单独的参考文件以获取详细说明和代码示例：

- [部分定义](references/_sections.md) - 类别结构和影响级别
- [规则模板](assets/templates/_template.md) - 添加新规则的模板
- 参考文件：`references/{prefix}-{slug}.md`

## 相关技能

- 对于使用 Zod 解析器的模式验证，请参阅 `zod` 技能
- 对于 React 19 服务器操作，请参阅 `react-19` 技能
- 对于 UI/UX 表单设计，请参阅 `frontend-design` 技能

## 完整编译文档

获取包含所有规则展开的完整指南：`AGENTS.md`
