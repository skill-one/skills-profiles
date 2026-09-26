# React Hook Form + Zod 验证

**状态**: 生产就绪 ✅
**最后验证**: 2026-01-20
**最新版本**: react-hook-form@7.71.1, zod@4.3.5, @hookform/resolvers@5.2.2

---

## 快速入门

```bash
npm install react-hook-form@7.70.0 zod@4.3.5 @hookform/resolvers@5.2.2
```

**基本表单模式**:
```typescript
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

type FormData = z.infer<typeof schema>

const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
  resolver: zodResolver(schema),
  defaultValues: { email: '', password: '' }, // REQUIRED to prevent uncontrolled warnings
})

<form onSubmit={handleSubmit(onSubmit)}>
  <input {...register('email')} />
  {errors.email && <span role="alert">{errors.email.message}</span>}
</form>
```

**服务器验证** (CRITICAL - never skip):
```typescript
// SAME schema on server
const data = schema.parse(await req.json())
```

---

## 关键模式

**useForm 选项** (验证模式):
- `mode: 'onSubmit'` (默认) - 最佳性能
- `mode: 'onBlur'` - 良好平衡
- `mode: 'onChange'` - 实时反馈，更多重渲染
- `shouldUnregister: true` - 卸载时移除字段数据 (用于多步骤表单)

**Zod Refinements** (跨字段验证):
```typescript
z.object({ password: z.string(), confirm: z.string() })
  .refine((data) => data.password === data.confirm, {
    message: "密码不匹配",
    path: ['confirm'], // CRITICAL: 错误显示在此字段
  })
```

**Zod Transforms**:
```typescript
z.string().transform((val) => val.toLowerCase()) // 数据处理
z.string().transform(parseInt).refine((v) => v > 0) // 链接 refine
```

**Zod v4.3.0+ 功能**:
```typescript
// Exact optional (可以省略字段，但不能为 undefined)
z.string().exactOptional()

// Exclusive union (必须匹配其中之一)
z.xor([z.string(), z.number()])

// 从 JSON Schema 导入
z.fromJSONSchema({ type: "object", properties: { name: { type: "string" } } })
```

**zodResolver** 连接 Zod 和 React Hook Form，保留类型安全

---

## 注册

**register** (用于标准 HTML 输入):
```typescript
<input {...register('email')} /> // 非受控，最佳性能
```

**Controller** (用于第三方组件):
```typescript
<Controller
  name="category"
  control={control}
  render={({ field }) => <CustomSelect {...field} />} // MUST spread {...field}
/>
```

**何时使用 Controller**: React Select, 日期选择器，没有 ref 的自定义组件。否则使用 `register`。

---

## 错误处理

**显示错误**:
```typescript
{errors.email && <span role="alert">{errors.email.message}</span>}
{errors.address?.street?.message} // 嵌套错误 (使用可选链)
```

**服务器错误**:
```typescript
const onSubmit = async (data) => {
  const res = await fetch('/api/submit', { method: 'POST', body: JSON.stringify(data) })
  if (!res.ok) {
    const { errors: serverErrors } = await res.json()
    Object.entries(serverErrors).forEach(([field, msg]) => setError(field, { message: msg }))
  }
}
```

---

## 高级模式

**useFieldArray** (动态列表):
```typescript
const { fields, append, remove } = useFieldArray({ control, name: 'contacts' })

{fields.map((field, index) => (
  <div key={field.id}> {/* CRITICAL: Use field.id, NOT index */}
    <input {...register(`contacts.${index}.name` as const)} />
    {errors.contacts?.[index]?.name && <span>{errors.contacts[index].name.message}</span>}
    <button onClick={() => remove(index)}>移除</button>
  </div>
))}
<button onClick={() => append({ name: '', email: '' })}>添加</button>
```

**异步验证** (防抖):
```typescript
const debouncedValidation = useDebouncedCallback(() => trigger('username'), 500)
```

**多步骤表单**:
```typescript
const step1 = z.object({ name: z.string(), email: z.string().email() })
const step2 = z.object({ address: z.string() })
const fullSchema = step1.merge(step2)

const nextStep = async () => {
  const isValid = await trigger(['name', 'email']) // 验证特定字段
  if (isValid) setStep(2)
}
```

**条件验证**:
```typescript
z.discriminatedUnion('accountType', [
  z.object({ accountType: z.literal('personal'), name: z.string() }),
  z.object({ accountType: z.literal('business'), companyName: z.string() }),
])
```

**带 shouldUnregister 的条件字段**:
```typescript
const form = useForm({
  resolver: zodResolver(schema),
  shouldUnregister: false, // 字段卸载时保留值 (默认)
})

// 或使用条件模式验证:
z.object({
  showAddress: z.boolean(),
  address: z.string(),
}).refine((data) => {
  if (data.showAddress) {
    return data.address.length > 0;
  }
  return true;
}, {
  message: "地址是必填项",
  path: ["address"],
})
```

---

## shadcn/ui 集成

**注意**: shadcn/ui 已弃用 Form 组件。新实现请使用 Field 组件 (检查最新文档)。

**常见导入错误**: IDEs/AI 可能自动从 "react-hook-form" 导入 `Form` 而不是从 shadcn。始终导入:
```typescript
// ✅ 正确:
import { useForm } from "react-hook-form";
import { Form, FormField, FormItem } from "@/components/ui/form"; // shadcn

// ❌ 错误 (自动导入错误):
import { useForm, Form } from "react-hook-form";
```

**遗留 Form 组件**:
```typescript
<FormField control={form.control} name="username" render={({ field }) => (
  <FormItem>
    <FormControl><Input {...field} /></FormControl>
    <FormMessage />
  </FormItem>
)} />
```

---

## 性能

- 使用 `register` (非受控) 而不是 `Controller` (受控) 用于标准输入
- 使用 `watch('email')` 而不是 `watch()` (隔离特定字段的重新渲染)
- `shouldUnregister: true` 用于多步骤表单 (卸载时清除数据)

### 大型表单 (300+ 字段)

**警告**: 使用解析器 (Zod/Yup) 且读取 `formState` 属性的 300+ 字段表单在注册时可能冻结 10-15 秒。([Issue #13129](https://github.com/react-hook-form/react-hook-form/issues/13129))

**性能特征**:
- 清理 (无解析器，无 formState 读取): 几乎立即
- 仅使用解析器: 几乎立即
- 仅读取 formState: 几乎立即
- 使用解析器 + formState 读取: 300 字段约 9.5 秒

**解决方法**:

1. **避免解构 formState** - 仅在需要时内联读取属性:
```typescript
// ❌ 300+ 字段时慢:
const { isDirty, isValid } = form.formState;

// ✅ 快:
const handleSubmit = () => {
  if (!form.formState.isValid) return; // 仅在需要时内联读取
};
```

2. **使用 mode: "onSubmit"** - 不要在每次更改时验证:
```typescript
const form = useForm({
  resolver: zodResolver(largeSchema),
  mode: "onSubmit", // 仅在提交时验证，不在 onChange 时验证
});
```

3. **拆分为子表单** - 使用多个具有单独模式的小表单:
```typescript
// 代替一个 300 字段的表单，使用 5-6 个每个 50-60 字段的表单
const form1 = useForm({ resolver: zodResolver(schema1) }); // 字段 1-50
const form2 = useForm({ resolver: zodResolver(schema2) }); // 字段 51-100
```

4. **延迟渲染字段** - 使用标签/手风琴仅挂载可见字段:
```typescript
// 仅挂载活动标签的字段，减少初始注册时间
{activeTab === 'personal' && <PersonalInfoFields />}
{activeTab === 'address' && <AddressFields />}
```

---

## 关键规则

✅ **始终设置 defaultValues** (防止非受控→受控警告)

✅ **客户端和服务器双重验证** (客户端可能被绕过 - 安全性!)

✅ **在 useFieldArray 中使用 field.id 作为 key** (不是 index)

✅ **在 Controller 渲染中展开 `{...field}`**

✅ **使用 `z.infer<typeof schema>`** 进行类型推断

❌ **永远不要跳过服务器验证** (安全漏洞)

❌ **永远不要直接修改值** (使用 `setValue()`)

❌ **永远不要混合受控和非受控模式**

❌ **永远不要在 useFieldArray 中使用 index 作为 key**

---

## 已知问题 (已解决 20 个)

1. **Zod v4 类型推断** - [#13109](https://github.com/react-hook-form/react-hook-form/issues/13109): 明确使用 `z.infer<typeof schema>`。已在 v7.66.x+ 中解决。**注意**: @hookform/resolvers 与 Zod v4 的 TypeScript 兼容性问题 ([#813](https://github.com/react-hook-form/resolvers/issues/813))。解决方法: 使用 `import { z } from 'zod/v3'` 或等待解析器更新。

2. **非受控→受控警告** - 为所有字段设置 `defaultValues`

3. **嵌套对象错误** - 使用可选链: `errors.address?.street?.message`

4. **数组字段重新渲染** - 在 useFieldArray 中使用 `key={field.id}` (不是 index)

5. **异步验证竞争条件** - 防抖验证，取消挂起的请求

6. **服务器错误映射** - 使用 `setError()` 将服务器错误映射到字段

7. **默认值未应用** - 在 useForm 选项中设置 `defaultValues` (不是 useState)

8. **Controller 字段未更新** - 在渲染函数中始终展开 `{...field}`

9. **useFieldArray key 警告** - 使用 `field.id` 作为 key (不是 index)

10. **模式 Refinement 错误路径** - 在 refinement 中指定 `path`: `refine(..., { path: ['fieldName'] })`

11. **Transform vs Preprocess** - 使用 `transform` 进行输出，`preprocess` 进行输入

12. **多个解析器冲突** - 使用单个解析器 (zodResolver)，如有需要组合模式

13. **Zod v4 可选字段错误** - [#13102](https://github.com/react-hook-form/react-hook-form/issues/13102): 将可选字段 (`.optional()`) 设置为空字符串 `""` 错误地触发验证错误。解决方法: 使用 `.nullish()`, `.or(z.literal(""))` 或 `z.preprocess((val) => val === "" ? undefined : val, z.email().optional())`

14. **useFieldArray 原始数组不受支持** - [#12570](https://github.com/react-hook-form/react-hook-form/issues/12570): 设计限制。`useFieldArray` 仅适用于对象数组，不适用于字符串等原始类型。解决方法: 将原始类型包装在对象中: `[{ value: "string" }]` 而不是 `["string"]`

15. **useFieldArray SSR ID 不匹配** - [#12782](https://github.com/react-hook-form/react-hook-form/issues/12782): SSR (Remix, Next.js) 与 hydration 不匹配警告。服务器生成的字段 ID 与客户端不匹配。解决方法: 使用客户端渲染字段数组或等待 V8 (使用确定性 `key`)

16. **Next.js 16 reset() 验证错误** - [#13110](https://github.com/react-hook-form/react-hook-form/issues/13110): 在 Server Actions 提交后调用 `form.reset()` 导致下次提交时出现验证错误。已在 v7.65.0+ 中修复。修复前: 使用 `setValue()` 而不是 `reset()`

17. **验证竞争条件** - [#13156](https://github.com/react-hook-form/react-hook-form/issues/13156): 在解析器验证期间，中间渲染时 `isValidating=false` 但 `errors` 尚未填充。不要仅从错误推导有效性。使用: `!errors.field && !isValidating`

18. **Beta 版本中抛出 ZodError** - [#12816](https://github.com/react-hook-form/react-hook-form/issues/12816): Zod v4 beta 版本直接抛出 `ZodError` 而不是在 `formState.errors` 中捕获。已在稳定 Zod v4.1.x+ 中修复。避免使用 beta 版本

19. **大型表单性能** - [#13129](https://github.com/react-hook-form/react-hook-form/issues/13129): 300+ 字段使用解析器 + formState 读取冻结 10-15 秒。见性能部分 4 种解决方法

20. **shadcn 导入混淆** - IDEs/AI 可能自动从 "react-hook-form" 导入 `Form` 而不是 shadcn。始终从 `@/components/ui/form` 导入 `Form` 组件

---

## V8 即将到来的变化 (Beta)

React Hook Form v8 (截至 2026-01-11 已在 beta 版本中，v8.0.0-beta.1 发布) 引入破坏性变更。[RFC 讨论 #7433](https://github.com/orgs/react-hook-form/discussions/7433)

**破坏性变更**:

1. **useFieldArray: `id` → `key`**:
```typescript
// V7:
const { fields } = useFieldArray({ control, name: "items" });
fields.map(field => <div key={field.id}>...</div>)

// V8:
const { fields } = useFieldArray({ control, name: "items" });
fields.map(field => <div key={field.key}>...</div>)
// keyName 属性已移除
```

2. **Watch 组件: `names` → `name`**:
```typescript
// V7:
<Watch names={["email", "password"]} />

// V8:
<Watch name={["email", "password"]} />
```

3. **watch() 回调 API 已移除**:
```typescript
// V7:
watch((data, { name, type }) => {
  console.log(data, name, type);
});

// V8: 使用 useWatch 或手动订阅
const data = useWatch({ control });
useEffect(() => {
  console.log(data);
}, [data]);
```

4. **setValue() 不再更新 useFieldArray**:
```typescript
// V7:
setValue("items", newArray); // 更新字段数组

// V8: 必须使用 replace() API
const { replace } = useFieldArray({ control, name: "items" });
replace(newArray);
```

**V8 优势**:
- 修复 SSR hydration 不匹配 (使用确定性 `key` 而不是随机 `id`)
- 性能提升
- 更好的 TypeScript 推断

**迁移时间线**: V8 正在 beta 版本中。稳定版本发布日期待定。监控 [发布](https://github.com/react-hook-form/react-hook-form/releases) 以获取稳定版本。

---

## 嵌套资源

**模板**: basic-form.tsx, advanced-form.tsx, shadcn-form.tsx, server-validation.ts, async-validation.tsx, dynamic-fields.tsx, multi-step-form.tsx, package.json

**参考**: zod-schemas-guide.md, rhf-api-reference.md, error-handling.md, performance-optimization.md, shadcn-integration.md, top-errors.md

**文档**: https://react-hook-form.com/ | https://zod.dev/ | https://ui.shadcn.com/docs/components/form

---

**许可证**: MIT | **最后验证**: 2026-01-20 | **技能版本**: 2.1.0 | **变更**: 添加了 8 个新已知问题 (Zod v4 可选字段错误, useFieldArray 原始数组限制, SSR hydration 不匹配, 大型表单性能指导, Next.js 16 reset() 错误, 验证竞争条件, Beta 版本中抛出 ZodError, shadcn 导入混淆), 添加了 Zod v4.3.0 功能 (.exactOptional(), .xor(), z.fromJSONSchema), 添加了带 shouldUnregister 的条件字段模式, 添加了 V8 beta 破坏性变更部分, 扩展了 Zod v4 解析器兼容性说明, 更新为 react-hook-form@7.71.1
