# Mantine 表单技能

## 核心工作流

### 1. 设置表单

```tsx
const form = useForm({
  mode: 'controlled',       // 或 'uncontrolled' 用于大型表单
  initialValues: {
    email: '',
    age: 0,
  },
  validate: {
    email: isEmail('无效的邮箱'),
    age: isInRange({ min: 18 }, '必须至少18岁'),
  },
});
```

### 2. 使用 `getInputProps` 连接输入

```tsx
<TextInput {...form.getInputProps('email')} label="邮箱" />
<NumberInput {...form.getInputProps('age')} label="年龄" />
```

对于复选框，传递 `{ type: 'checkbox' }`：
```tsx
<Checkbox {...form.getInputProps('agreed', { type: 'checkbox' })} label="我同意" />
```

### 3. 处理提交

```tsx
<form onSubmit={form.onSubmit((values) => console.log(values))}>
  ...
  <Button type="submit">提交</Button>
</form>
```

`onSubmit` 仅在验证通过时调用处理程序。要处理失败：
```tsx
form.onSubmit(
  (values) => save(values),
  (errors) => console.log('验证失败', errors)
)
```

## 验证

### 规则对象（最常用）
```tsx
validate: {
  name: isNotEmpty('必填'),
  email: isEmail('无效的邮箱'),
  password: hasLength({ min: 8 }, '至少8个字符'),
  confirmPassword: matchesField('password', '密码不匹配'),
}
```

### 函数（用于跨字段逻辑）
```tsx
validate: (values) => ({
  endDate: values.endDate < values.startDate ? '结束日期必须在开始日期之后' : null,
})
```

### 验证时机
```tsx
validateInputOnChange: true,        // 每次变更时验证所有字段
validateInputOnChange: ['email'],    // 仅验证特定字段
validateInputOnBlur: true,          // 失焦时验证
```

## 模式

| 模式 | 状态存储 | 重新渲染 | 输入属性 |
|---|---|---|---|
| `'controlled'` (默认) | React 状态 | 每次变更时 | `value` + `onChange` |
| `'uncontrolled'` | Refs | 无 | `defaultValue` + `onChange` |

在非受控模式下，当需要强制重新渲染输入时，使用 `form.key('fieldPath')` 作为 React 的 `key` 属性。

## 参考

- **[`references/api.md`](references/api.md)** — 完整API：`useForm` 选项、完整返回值、`useField`、`createFormContext`、`createFormActions`、所有内置验证器、键类型
- **[`references/patterns.md`](references/patterns.md)** — 代码示例：嵌套对象、数组字段、异步验证、跨组件表单上下文、`transformValues`、`useField` 独立使用
