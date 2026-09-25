# Zod 验证工具

## 概述

适用于生产环境的 Zod v4 模式，用于可重用、类型安全的验证，且最小化样板代码。专注于现代 API、可预测的错误处理和表单集成。

## 使用场景

- 在 TypeScript 服务中定义请求/响应验证模式
- 解析来自 API、表单、环境变量或外部系统的不可信输入
- 标准化强制转换、转换和跨字段验证
- 跨团队构建可重用的模式工具
- 使用 `zodResolver` 将 React Hook Form 与 Zod 集成

## 使用说明

1. 从严格的对象模式开始，并显式定义字段约束
2. 优先使用现代 Zod v4 API 和 `error` 选项来处理错误消息
3. 在边界处使用强制转换 (`z.coerce.*`)，当输入类型不确定时
4. 将业务不变量保持在 `refine`/`superRefine` 附近，靠近模式定义
5. 导出模式及其推断类型 (`z.input`/`z.output`) 以保持一致性
6. 重用工具模式（电子邮件、ID、日期、分页）以减少重复

## 验证工作流

当将验证集成到 API 处理程序或服务中时：

1. **定义** 边界处的模式（处理程序、队列、配置加载器）
2. 使用 `safeParse` 进行解析，以优雅地处理错误
3. 检查 `result.success` 以根据成功/失败进行分支
4. 在成功路径中使用 `result.data`，具有完整的类型推断
5. 返回格式化的错误或继续使用验证后的数据

参考示例 7（`safeParse` 工作流）以获取完整模式。

## 示例

### 1) 现代 Zod 4 基本类型和对象错误

```ts
import { z } from "zod";

export const UserIdSchema = z.uuid({ error: "无效的用户 ID" });
export const EmailSchema = z.email({ error: "无效的电子邮件" });
export const WebsiteSchema = z.url({ error: "无效的 URL" });

export const UserProfileSchema = z.object(
  {
    id: UserIdSchema,
    email: EmailSchema,
    website: WebsiteSchema.optional(),
  },
  { error: "无效的用户资料负载" }
);
```

### 2) 强制转换、预处理和转换

```ts
import { z } from "zod";

export const PaginationQuerySchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
  includeArchived: z.coerce.boolean().default(false),
});

export const DateFromUnknownSchema = z.preprocess(
  (value) => (typeof value === "string" || value instanceof Date ? value : undefined),
  z.coerce.date({ error: "无效的日期" })
);

export const NormalizedEmailSchema = z
  .string()
  .trim()
  .toLowerCase()
  .email({ error: "无效的电子邮件" })
  .transform((value) => value as Lowercase<string>);
```

### 3) 复杂的模式结构

```ts
import { z } from "zod";

const TagSchema = z.string().trim().min(1).max(40);

export const ProductSchema = z.object({
  sku: z.string().min(3).max(24),
  tags: z.array(TagSchema).max(15),
  attributes: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])),
  dimensions: z.tuple([z.number().positive(), z.number().positive(), z.number().positive()]),
});

export const PaymentMethodSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("card"), last4: z.string().regex(/^\d{4}$/) }),
  z.object({ type: z.literal("paypal"), email: z.email() }),
  z.object({ type: z.literal("wire"), iban: z.string().min(10) }),
]);
```

### 4) `refine` 和 `superRefine`

```ts
import { z } from "zod";

export const PasswordSchema = z
  .string()
  .min(12)
  .refine((v) => /[A-Z]/.test(v), { error: "必须包含一个大写字母" })
  .refine((v) => /\d/.test(v), { error: "必须包含一个数字" });

export const RegisterSchema = z
  .object({
    email: z.email(),
    password: PasswordSchema,
    confirmPassword: z.string(),
  })
  .superRefine((data, ctx) => {
    if (data.password !== data.confirmPassword) {
      ctx.addIssue({
        code: "custom",
        path: ["confirmPassword"],
        message: "密码不匹配",
      });
    }
  });
```

### 5) 可选、可空、空值和默认值

```ts
import { z } from "zod";

export const UserPreferencesSchema = z.object({
  nickname: z.string().min(2).optional(),      // 允许未定义
  bio: z.string().max(280).nullable(),         // 允许 null
  avatarUrl: z.url().nullish(),                // 允许 null 或未定义
  locale: z.string().default("en"),           // 缺失时的回退值
});
```

### 6) React Hook Form 集成（`zodResolver`）

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const ProfileFormSchema = z.object({
  name: z.string().min(2, { error: "名字太短" }),
  email: z.email({ error: "无效的电子邮件" }),
  age: z.coerce.number().int().min(18),
});

type ProfileFormInput = z.input<typeof ProfileFormSchema>;
type ProfileFormOutput = z.output<typeof ProfileFormSchema>;

const form = useForm<ProfileFormInput, unknown, ProfileFormOutput>({
  resolver: zodResolver(ProfileFormSchema),
  criteriaMode: "all",
});
```

### 7) 使用 `safeParse` 的错误处理工作流

```ts
import { z } from "zod";
import type { ZodError } from "zod";

const ResultSchema = z.object({ id: z.string(), name: z.string() });

function parseAndHandle(input: unknown) {
  const result = ResultSchema.safeParse(input);

  if (!result.success) {
    const error = result.error as ZodError;
    console.error("验证失败:", error.errors);
    return { success: false as const, error: error.format() };
  }

  return { success: true as const, data: result.data };
}
```

> **提示**：对于高级区分联合模式和复杂的 React Hook Form 工作流，请参阅 `references/advanced-patterns.md`。

## 最佳实践

- 将模式保持在边界附近（HTTP 处理程序、队列、配置加载器）
- 优先使用 `safeParse` 进行可恢复流程；使用 `parse` 进行快速失败执行
- 共享小的模式工具（ID、电子邮件、缩写）以强制一致性
- 当转换/强制转换改变运行时形状时，使用 `z.input` 和 `z.output`
- 避免过度使用 `preprocess`；在可能的情况下，优先使用显式的 `z.coerce.*`
- 将外部负载视为不可信，并在使用前始终验证

## 限制和警告

- 确保示例与您安装的 `zod` 主版本匹配（显示 v4 API）
- `error` 是 Zod v4 模式中自定义错误的首选选项
- 区分联合要求跨变体具有稳定的区分器键
- 强制转换可能会隐藏上游的坏数据；防御性地添加边界和细化
