# TypeScript 最佳实践

遵循 CLAUDE.md 中的类型优先、函数式和错误处理模式。这项技能仅涵盖语言特定的惯用法。

## 与 React 最佳实践搭配使用

在处理 React 组件（`.tsx`、`.jsx` 文件或 `@react` 导入）时，始终与这项技能一起加载 `react-best-practices`。这项技能涵盖 TypeScript 基础知识；React 特定模式（效果、钩子、引用、组件设计）在专门的 React 技能中。

## 使非法状态不可表示

使用类型系统在编译时防止无效状态。

**用于互斥状态的区分联合类型：**
```ts
// 好：仅允许有效的组合
type RequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

// 不好：允许无效的组合，如 { loading: true, error: Error }
type RequestState<T> = {
  loading: boolean;
  data?: T;
  error?: Error;
};
```

**用于领域原语的品牌类型：**
```ts
type UserId = string & { readonly __brand: 'UserId' };
type OrderId = string & { readonly __brand: 'OrderId' };

// 编译器阻止将 OrderId 传递到期望 UserId 的地方
function getUser(id: UserId): Promise<User> { /* ... */ }
```

**用于字面量联合类型的常量断言：**
```ts
const ROLES = ['admin', 'user', 'guest'] as const;
type Role = typeof ROLES[number]; // 'admin' | 'user' | 'guest'

// 数组和类型会自动保持同步
function isValidRole(role: string): role is Role {
  return ROLES.includes(role as Role);
}
```

**带有 never 检查的穷尽 switch：**
```ts
type Status = "active" | "inactive";

function processStatus(status: Status): string {
  switch (status) {
    case "active":
      return "processing";
    case "inactive":
      return "skipped";
    default: {
      const _exhaustive: never = status;
      throw new Error(`unhandled status: ${_exhaustive}`);
    }
  }
}
```

## 使用 Zod 进行运行时验证

- 将模式定义为一个单一的事实来源；使用 `z.infer<>` 推断 TypeScript 类型。避免重复类型和模式。
- 使用 `safeParse` 处理预期会失败的用户输入；在信任边界处使用 `parse`，无效数据是错误。
- 使用 `.extend()`、`.pick()`、`.omit()`、`.merge()` 组合模式，以实现 DRY 定义。
- 使用 `.transform()` 在解析时进行数据规范化（修剪字符串、解析日期）。

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1),
  createdAt: z.string().transform((s) => new Date(s)),
});

type User = z.infer<typeof UserSchema>;

// 信任边界处的严格解析——如果 API 合约被违反则抛出错误
export async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error(`fetch user ${id} failed: ${response.status}`);
  }
  return UserSchema.parse(await response.json());
}

// 调用者处理用户输入的成功和错误
const result = UserSchema.safeParse(formData);
if (!result.success) {
  setErrors(result.error.flatten().fieldErrors);
  return;
}
```

## 可选：type-fest

对于超出 TypeScript 内建类型的先进类型工具，可以考虑 [type-fest](https://github.com/sindresorhus/type-fest)：

- `Opaque<T, Token>` - 比手动 `& { __brand }` 模式更干净的标记类型
- `PartialDeep<T>` - 递归部分嵌套对象
- `ReadonlyDeep<T>` - 递归只读，用于不可变数据
- `SetRequired<T, K>` / `SetOptional<T, K>` - 针对性字段修改
- `Simplify<T>` - 在 IDE 工具提示中展平复杂的交叉类型

```ts
import type { Opaque, PartialDeep } from 'type-fest';

type UserId = Opaque<string, 'UserId'>;
type UserPatch = PartialDeep<User>;
```
