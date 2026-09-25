## 概述

TanStack Form 是一个无头表单库，与 TypeScript 深度集成。它提供字段级和表单级的验证（同步/异步）、数组字段、关联/依赖字段、细粒度响应性以及模式验证适配器支持（Zod、Valibot、Yup）。

**包名：** `@tanstack/react-form`
**适配器：** `@tanstack/zod-form-adapter`，`@tanstack/valibot-form-adapter`
**状态：** 稳定（v1）

## 安装

```bash
npm install @tanstack/react-form
# 可选的模式适配器：
npm install @tanstack/zod-form-adapter zod
npm install @tanstack/valibot-form-adapter valibot
```

## 核心：useForm

```tsx
import { useForm } from '@tanstack/react-form'

function MyForm() {
  const form = useForm({
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      age: 0,
    },
    onSubmit: async ({ value }) => {
      // value 完全类型化
      await submitToServer(value)
    },
    onSubmitInvalid: ({ value, formApi }) => {
      console.log('验证失败：', formApi.state.errors)
    },
  })

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        e.stopPropagation()
        form.handleSubmit()
      }}
    >
      {/* 字段 */}
      <form.Subscribe
        selector={(state) => ({ canSubmit: state.canSubmit, isSubmitting: state.isSubmitting })}
        children={({ canSubmit, isSubmitting }) => (
          <button type="submit" disabled={!canSubmit}>
            {isSubmitting ? '提交中...' : '提交'}
          </button>
        )}
      />
    </form>
  )
}
```

## 字段 (form.Field)

```tsx
<form.Field
  name="firstName"
  validators={{
    onChange: ({ value }) =>
      value.length < 3 ? '至少需要 3 个字符' : undefined,
  }}
  children={(field) => (
    <div>
      <label htmlFor={field.name}>名字</label>
      <input
        id={field.name}
        name={field.name}
        value={field.state.value}
        onBlur={field.handleBlur}
        onChange={(e) => field.handleChange(e.target.value)}
      />
      {field.state.meta.isTouched && field.state.meta.errors.length > 0 && (
        <em>{field.state.meta.errors.join(', ')}</em>
      )}
    </div>
  )}
/>

<!-- 嵌套字段使用点表示法 -->
<form.Field name="address.city">
  {(field) => (
    <input
      value={field.state.value}
      onChange={(e) => field.handleChange(e.target.value)}
      onBlur={field.handleBlur}
    />
  )}
</form.Field>
```

## 验证

### 验证时机

| 原因 | 何时 |
|------|------|
| `onChange` | 每次值变化后 |
| `onBlur` | 字段失去焦点时 |
| `onSubmit` | 提交期间 |
| `onMount` | 字段挂载时 |

### 同步验证

```tsx
<form.Field
  name="age"
  validators={{
    onChange: ({ value }) => {
      if (value < 18) return '必须年满 18 岁'
      return undefined // undefined = 有效
    },
    onBlur: ({ value }) => {
      if (!value) return '必填'
      return undefined
    },
  }}
/>
```

### 异步验证

```tsx
<form.Field
  name="username"
  asyncDebounceMs={500}
  validators={{
    onChangeAsync: async ({ value }) => {
      const res = await fetch(`/api/check-username?q=${value}`)
      const { available } = await res.json()
      if (!available) return '用户名已被占用'
      return undefined
    },
  }}
>
  {(field) => (
    <>
      <input value={field.state.value} onChange={(e) => field.handleChange(e.target.value)} />
      {field.state.meta.isValidating && <span>检查中...</span>}
    </>
  )}
</form.Field>
```

### 模式验证 (Zod)

```tsx
import { zodValidator } from '@tanstack/zod-form-adapter'
import { z } from 'zod'

const form = useForm({
  defaultValues: { email: '', age: 0 },
  validatorAdapter: zodValidator(),
  onSubmit: async ({ value }) => { /* ... */ },
})

<form.Field
  name="email"
  validators={{
    onChange: z.string().email('无效的邮箱'),
    onBlur: z.string().min(1, '必填'),
  }}
/>

<form.Field
  name="age"
  validators={{
    onChange: z.number().min(18, '必须年满 18+'),
  }}
/>
```

### 表单级验证

```tsx
const form = useForm({
  defaultValues: { password: '', confirmPassword: '' },
  validators: {
    onChange: ({ value }) => {
      if (value.password !== value.confirmPassword) {
        return '密码不匹配'
      }
      return undefined
    },
  },
})
```

### 关联/依赖字段

```tsx
<form.Field
  name="confirmPassword"
  validators={{
    onChangeListenTo: ['password'], // 密码变化时重新验证
    onChange: ({ value, fieldApi }) => {
      const password = fieldApi.form.getFieldValue('password')
      if (value !== password) return '密码不匹配'
      return undefined
    },
  }}
/>
```

## 数组字段

```tsx
<form.Field name="people" mode="array">
  {(field) => (
    <div>
      {field.state.value.map((_, index) => (
        <div key={index}>
          <form.Field name={`people[${index}].name`}>
            {(subField) => (
              <input
                value={subField.state.value}
                onChange={(e) => subField.handleChange(e.target.value)}
              />
            )}
          </form.Field>
          <button type="button" onClick={() => field.removeValue(index)}>
            删除
          </button>
        </div>
      ))}
      <button type="button" onClick={() => field.pushValue({ name: '', age: 0 })}>
        添加人员
      </button>
    </div>
  )}
</form.Field>
```

### 数组方法

```typescript
field.pushValue(item)              // 添加到末尾
field.insertValue(index, item)     // 在索引处插入
field.replaceValue(index, item)    // 在索引处替换
field.removeValue(index)           // 在索引处删除
field.swapValues(indexA, indexB)    // 交换位置
field.moveValue(from, to)          // 移动位置
```

## 侦听器（副作用）

```tsx
<form.Field
  name="country"
  listeners={{
    onChange: ({ value }) => {
      // 副作用：重置依赖字段
      form.setFieldValue('state', '')
      form.setFieldValue('postalCode', '')
    },
  }}
/>
```

## 响应性 (form.Subscribe & useStore)

```tsx
// 渲染属性订阅（细粒度）
<form.Subscribe
  selector={(state) => ({ canSubmit: state.canSubmit, isDirty: state.isDirty })}
  children={({ canSubmit, isDirty }) => (
    <div>
      {isDirty && <span>未保存的更改</span>}
      <button disabled={!canSubmit}>保存</button>
    </div>
  )}
/>

// 基于钩子的订阅
function FormStatus() {
  const isValid = form.useStore((s) => s.isValid)
  return isValid ? null : <p>修复错误</p>
}
```

## 表单状态

```typescript
interface FormState {
  values: TFormData
  errors: ValidationError[]
  errorMap: Record<string, ValidationError>
  isFormValid: boolean
  isFieldsValid: boolean
  isValid: boolean               // isFormValid && isFieldsValid
  isTouched: boolean
  isPristine: boolean
  isDirty: boolean
  isSubmitting: boolean
  isSubmitted: boolean
  isSubmitSuccessful: boolean
  submissionAttempts: number
  canSubmit: boolean             // isValid && !isSubmitting
}
```

## 字段状态

```typescript
interface FieldState<TData> {
  value: TData
  meta: {
    isTouched: boolean
    isDirty: boolean
    isPristine: boolean
    isValidating: boolean
    errors: ValidationError[]
    errorMap: Record<ValidationCause, ValidationError>
  }
}
```

## FormApi 方法

```typescript
form.handleSubmit()
form.reset()
form.getFieldValue(field)
form.setFieldValue(field, value)
form.getFieldMeta(field)
form.setFieldMeta(field, updater)
form.validateAllFields(cause)
form.validateField(field, cause)
form.deleteField(field)
```

## 共享表单选项 (formOptions)

```tsx
import { formOptions } from '@tanstack/react-form'

const sharedOpts = formOptions({
  defaultValues: { firstName: '', lastName: '' },
})

// 跨组件复用
const form = useForm({
  ...sharedOpts,
  onSubmit: async ({ value }) => { /* ... */ },
})
```

## 服务器端验证

```tsx
// TanStack Start / Next.js 服务器动作
import { ServerValidateError } from '@tanstack/react-form/nextjs'

export async function validateForm(data: FormData) {
  const email = data.get('email') as string
  if (await checkEmailExists(email)) {
    throw new ServerValidateError({
      form: '提交失败',
      fields: { email: '邮箱已注册' },
    })
  }
}
```

## TypeScript 集成

```tsx
// 带有 DeepKeys 的类型安全字段路径
interface UserForm {
  name: string
  address: { street: string; city: string }
  tags: string[]
  contacts: Array<{ name: string; phone: string }>
}

// TypeScript 自动补全所有有效路径：
// 'name', 'address', 'address.street', 'address.city', 'tags', 'contacts'
<form.Field name="address.city" />     // OK
<form.Field name="nonexistent" />       // 类型错误！
```

## 最佳实践

1. **始终调用 `e.preventDefault()` 和 `e.stopPropagation()`** 在表单提交
2. **始终附加 `onBlur={field.handleBlur}`** 用于模糊验证和 isTouched 跟踪
3. **使用 `mode="array"`** 对于数组字段以获取数组方法
4. **返回 `undefined`**（不是 null/false）对于有效的验证器
5. **使用 `asyncDebounceMs`** 对于异步验证器以防止 API 繁忙
6. **在显示错误前检查 `isTouched`** 以获得更好的用户体验
7. **使用 `form.Subscribe` 与选择器** 以最小化重新渲染
8. **使用 `formOptions`** 对于跨组件的共享配置
9. **使用模式验证器**（Zod/Valibot）对于复杂的验证规则
10. **使用 `onChangeListenTo`** 对于跨字段验证依赖

## 常见陷阱

- 忘记在表单提交时调用 `e.preventDefault()`（导致页面重新加载）
- 未将 `onBlur` 附加到输入（破坏模糊验证和 isTouched）
- 返回 `null` 或 `false` 而不是 `undefined` 对于有效的字段
- 不正确使用 `mode="array"`（仅需要在数组字段本身上使用，不需要在子字段上使用）
- 订阅整个表单状态而不是使用选择器（不必要的重新渲染）
- 未使用 `asyncDebounceMs` 与异步验证器（每次按键都会触发）
