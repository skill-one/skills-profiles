# Valibot

这个技能帮助你有效地使用 [Valibot](https://valibot.dev)，它是一个模块化且类型安全的结构数据验证库。

## 何时使用此技能

- 当用户询问关于使用 Valibot 进行模式验证时
- 当创建或修改 Valibot 模式时
- 当解析或验证用户输入时
- 当用户提到 Valibot、模式或验证时
- 当从 Zod 迁移到 Valibot 时

## 关键警告：Valibot 与 Zod — 切勿混淆！

**Valibot 和 Zod 具有不同的 API。切勿将它们混淆！**

### 主要差异

| 功能             | Zod ❌                                | Valibot ✅                                                |
| ---------------- | ------------------------------------- | --------------------------------------------------------- |
| 导入              | `import { z } from 'zod'`             | `import * as v from 'valibot'`                            |
| 验证             | 链式方法：`.email().min(5)`    | 管道：`v.pipe(v.string(), v.email(), v.minLength(5))` |
| 解析             | `schema.parse(data)`                  | `v.parse(schema, data)`                                   |
| 安全解析        | `schema.safeParse(data)`              | `v.safeParse(schema, data)`                               |
| 可选            | `z.string().optional()`               | `v.optional(v.string())`                                  |
| 可空            | `z.string().nullable()`               | `v.nullable(v.string())`                                  |
| 默认             | `z.string().default('x')`             | `v.optional(v.string(), 'x')`                             |
| 转换           | `z.string().transform(fn)`            | `v.pipe(v.string(), v.transform(fn))`                     |
| 精炼/检查        | `z.string().refine(fn)`               | `v.pipe(v.string(), v.check(fn))`                         |
| 枚举                | `z.enum(['a', 'b'])`                  | `v.picklist(['a', 'b'])`                                  |
| 原生枚举         | `z.nativeEnum(MyEnum)`                | `v.enum(MyEnum)`                                          |
| 联合               | `z.union([a, b])`                     | `v.union([a, b])`                                         |
| 差异联合         | `z.discriminatedUnion('type', [...])` | `v.variant('type', [...])`                                |
| 交集            | `z.intersection(a, b)`                | `v.intersect([a, b])`                                     |
| 最小/最大长度      | `.min(5).max(10)`                     | `v.minLength(5), v.maxLength(10)`                         |
| 最小/最大值       | `.gte(5).lte(10)`                     | `v.minValue(5), v.maxValue(10)`                           |
| 推断类型          | `z.infer<typeof Schema>`              | `v.InferOutput<typeof Schema>`                            |
| 推断输入         | `z.input<typeof Schema>`              | `v.InferInput<typeof Schema>`                             |

### 常见错误避免

```typescript
// ❌ 错误 - 这是 Zod 语法，不是 Valibot！
const Schema = v.string().email().min(5);
const result = Schema.parse(data);

// ✅ 正确 - Valibot 使用函数和管道
const Schema = v.pipe(v.string(), v.email(), v.minLength(5));
const result = v.parse(Schema, data);
```

```typescript
// ❌ 错误 - Zod 风格的可选
const Schema = v.object({
  name: v.string().optional(),
});

// ✅ 正确 - Valibot 使用 optional() 包装
const Schema = v.object({
  name: v.optional(v.string()),
});
```

```typescript
// ❌ 错误 - Zod 风格的默认值
const Schema = v.string().default("hello");

// ✅ 正确 - Valibot 使用第二个参数
const Schema = v.optional(v.string(), "hello");
```

## 安装

```bash
npm install valibot     # npm
yarn add valibot        # yarn
pnpm add valibot        # pnpm
bun add valibot         # bun
```

使用通配符导入（推荐）：

```typescript
import * as v from "valibot";
```

或者使用单独导入：

```typescript
import { object, string, pipe, email, parse } from "valibot";
```

## 思维模型

Valibot 的 API 分为三个主要概念：

### 1. 模式

模式定义了预期的数据类型。它们是起点。

```typescript
import * as v from "valibot";

// 基本模式
const StringSchema = v.string();
const NumberSchema = v.number();
const BooleanSchema = v.boolean();
const DateSchema = v.date();

// 复杂模式
const ArraySchema = v.array(v.string());
const ObjectSchema = v.object({
  name: v.string(),
  age: v.number(),
});
```

### 2. 方法

方法帮助你使用或修改模式。模式始终是第一个参数。

```typescript
// 解析
const result = v.parse(StringSchema, "hello");
const safeResult = v.safeParse(StringSchema, "hello");

// 类型守卫
if (v.is(StringSchema, data)) {
  // data 被类型化为 string
}
```

### 3. 操作

操作在 `pipe()` 内验证或转换数据。它们必须在管道内使用。

```typescript
// 操作用于 pipe()
const EmailSchema = v.pipe(
  v.string(),
  v.trim(),
  v.email(),
  v.endsWith("@example.com"),
);
```

## 管道

管道通过验证和转换操作扩展模式。管道始终以模式开始，后跟操作。

```typescript
import * as v from "valibot";

const UsernameSchema = v.pipe(
  v.string(),
  v.trim(),
  v.minLength(3, "用户名至少需要 3 个字符"),
  v.maxLength(20, "用户名最多 20 个字符"),
  v.regex(
    /^[a-z0-9_]+$/i,
    "用户名只能包含字母、数字和下划线",
  ),
);

const AgeSchema = v.pipe(
  v.number(),
  v.integer("年龄必须是整数"),
  v.minValue(0, "年龄不能为负"),
  v.maxValue(150, "年龄不能超过 150"),
);
```

### 常见验证操作

**字符串验证：**

- `v.email()` — 有效电子邮件格式
- `v.url()` — 有效 URL 格式
- `v.uuid()` — 有效 UUID 格式
- `v.regex(pattern)` — 匹配正则表达式模式
- `v.minLength(n)` — 最小长度
- `v.maxLength(n)` — 最大长度
- `v.length(n)` — 精确长度
- `v.nonEmpty()` — 非空字符串
- `v.startsWith(str)` — 以字符串开头
- `v.endsWith(str)` — 以字符串结尾
- `v.includes(str)` — 包含字符串

**数字验证：**

- `v.minValue(n)` — 最小值（>=）
- `v.maxValue(n)` — 最大值（<=）
- `v.gtValue(n)` — 大于（>
- `v.ltValue(n)` — 小于（<
- `v.integer()` — 必须是整数
- `v.finite()` — 必须是有限数
- `v.safeInteger()` — 安全整数范围
- `v.multipleOf(n)` — 必须是 n 的倍数

**数组验证：**

- `v.minLength(n)` — 最小项数
- `v.maxLength(n)` — 最大项数
- `v.length(n)` — 精确项数
- `v.nonEmpty()` — 至少一项
- `v.includes(item)` — 包含项
- `v.excludes(item)` — 不包含项

### 使用 check() 进行自定义验证

```typescript
const PasswordSchema = v.pipe(
  v.string(),
  v.minLength(8),
  v.check(
    (input) => /[A-Z]/.test(input),
    "密码必须包含一个大写字母",
  ),
  v.check((input) => /[0-9]/.test(input), "密码必须包含一个数字"),
);
```

### 值转换

这些操作在不改变其类型的情况下修改值：

**字符串转换：**

- `v.trim()` — 移除首尾空格
- `v.trimStart()` — 移除首部空格
- `v.trimEnd()` — 移除尾部空格
- `v.toLowerCase()` — 转换为小写
- `v.toUpperCase()` — 转换为大写

**数字转换：**

- `v.toMinValue(n)` — 夹紧到最小值（如果小于 n，设置为 n）
- `v.toMaxValue(n)` — 夹紧到最大值（如果大于 n，设置为 n）

```typescript
const NormalizedEmailSchema = v.pipe(
  v.string(),
  v.trim(),
  v.toLowerCase(),
  v.email(),
);

// 夹紧数字到 0-100 范围
const PercentageSchema = v.pipe(v.number(), v.toMinValue(0), v.toMaxValue(100));
```

### 类型转换

用于在数据类型之间转换，使用这些内置转换操作：

- `v.toNumber()` — 转换为数字
- `v.toString()` — 转换为字符串
- `v.toBoolean()` — 转换为布尔值
- `v.toBigint()` — 转换为 bigint
- `v.toDate()` — 转换为 Date

```typescript
// 将字符串转换为数字
const PortSchema = v.pipe(v.string(), v.toNumber(), v.integer(), v.minValue(1));

// 将 ISO 字符串转换为 Date
const TimestampSchema = v.pipe(v.string(), v.isoDateTime(), v.toDate());

// 转换为布尔值
const FlagSchema = v.pipe(v.string(), v.toBoolean());
```

### 自定义转换

对于自定义转换，使用 `v.transform()`：

```typescript
const DateStringSchema = v.pipe(
  v.string(),
  v.isoDate(),
  v.transform((input) => new Date(input)),
);

// 自定义对象转换
const UserSchema = v.pipe(
  v.object({
    firstName: v.string(),
    lastName: v.string(),
  }),
  v.transform((input) => ({
    ...input,
    fullName: `${input.firstName} ${input.lastName}`,
  })),
);
```

## 对象模式

### 基本对象

```typescript
const UserSchema = v.object({
  id: v.number(),
  name: v.string(),
  email: v.pipe(v.string(), v.email()),
  age: v.optional(v.number()),
});

type User = v.InferOutput<typeof UserSchema>;
```

### 对象变体

```typescript
// 普通对象 - 移除未知键（默认）
const ObjectSchema = v.object({ key: v.string() });

// 松散对象 - 允许并保留未知键
const LooseObjectSchema = v.looseObject({ key: v.string() });

// 严格对象 - 未知键会报错
const StrictObjectSchema = v.strictObject({ key: v.string() });

// 带 rest 的对象 - 验证未知键是否符合模式
const ObjectWithRestSchema = v.objectWithRest(
  { key: v.string() },
  v.number(), // 未知键必须是数字
);
```

### 可选和可空字段

```typescript
const ProfileSchema = v.object({
  // 必填
  name: v.string(),

  // 可选（可以是 undefined 或缺失）
  nickname: v.optional(v.string()),

  // 可选带默认值
  role: v.optional(v.string(), "user"),

  // 可空（可以是 null）
  avatar: v.nullable(v.string()),

  // 可空（可以是 null 或 undefined）
  bio: v.nullish(v.string()),

  // 可空带默认值
  theme: v.nullish(v.string(), "light"),
});
```

### 对象方法

```typescript
const BaseSchema = v.object({
  id: v.number(),
  name: v.string(),
  email: v.string(),
  password: v.string(),
});

// 选择特定键
const PublicUserSchema = v.pick(BaseSchema, ["id", "name"]);

// 忽略特定键
const UserWithoutPasswordSchema = v.omit(BaseSchema, ["password"]);

// 使所有可选
const PartialUserSchema = v.partial(BaseSchema);

// 使所有必填
const RequiredUserSchema = v.required(PartialUserSchema);

// 合并对象
const ExtendedUserSchema = v.object({
  ...BaseSchema.entries,
  createdAt: v.date(),
});
```

### 跨字段验证

```typescript
const RegistrationSchema = v.pipe(
  v.object({
    password: v.pipe(v.string(), v.minLength(8)),
    confirmPassword: v.string(),
  }),
  v.forward(
    v.partialCheck(
      [["password"], ["confirmPassword"]],
      (input) => input.password === input.confirmPassword,
      "密码不匹配",
    ),
    ["confirmPassword"],
  ),
);
```

## 数组和元组

### 数组

```typescript
const TagsSchema = v.pipe(
  v.array(v.string()),
  v.minLength(1, "至少需要一个标签"),
  v.maxLength(10, "最多允许 10 个标签"),
);

// 数组中的对象
const UsersSchema = v.array(
  v.object({
    id: v.number(),
    name: v.string(),
  }),
);
```

### 元组

```typescript
// 固定长度的数组，具有特定类型
const CoordinatesSchema = v.tuple([v.number(), v.number()]);
// 类型: [number, number]

// 带 rest 的元组
const ArgsSchema = v.tupleWithRest(
  [v.string()], // 第一个参数是 string
  v.number(), // 剩余参数是数字
);
// 类型: [string, ...number[]]
```

## 联合和变体

### 联合

```typescript
const StringOrNumberSchema = v.union([v.string(), v.number()]);

const StatusSchema = v.union([
  v.literal("pending"),
  v.literal("active"),
  v.literal("inactive"),
]);
```

### Picklist（用于字符串/数字字面量）

```typescript
// 比联合字面量更简单
const StatusSchema = v.picklist(["pending", "active", "inactive"]);

const PrioritySchema = v.picklist([1, 2, 3]);
```

### Variant（区分联合）

使用 `variant` 以便在区分联合中具有更好的性能：

```typescript
const EventSchema = v.variant("type", [
  v.object({
    type: v.literal("click"),
    x: v.number(),
    y: v.number(),
  }),
  v.object({
    type: v.literal("keypress"),
    key: v.string(),
  }),
  v.object({
    type: v.literal("scroll"),
    direction: v.picklist(["up", "down"]),
  }),
]);
```

## 解析数据

### parse() — 出错时抛出

```typescript
import * as v from "valibot";

const EmailSchema = v.pipe(v.string(), v.email());

try {
  const email = v.parse(EmailSchema, "jane@example.com");
  console.log(email); // 'jane@example.com'
} catch (error) {
  console.error(error); // ValiError
}
```

### safeParse() — 返回结果对象

```typescript
const result = v.safeParse(EmailSchema, input);

if (result.success) {
  console.log(result.output); // 有效数据
} else {
  console.log(result.issues); // 问题数组
}
```

### is() — 类型守卫

```typescript
if (v.is(EmailSchema, input)) {
  // input 被类型化为 string
}
```

### 配置选项

```typescript
// 提前终止 - 遇到第一个错误就停止
v.parse(Schema, data, { abortEarly: true });

// 提前终止管道 - 管道在第一个错误时停止
v.parse(Schema, data, { abortPipeEarly: true });
```

## 类型推断

```typescript
import * as v from "valibot";

const UserSchema = v.object({
  name: v.string(),
  age: v.pipe(v.string(), v.transform(Number)),
  role: v.optional(v.string(), "user"),
});

// 输出类型（转换和默认值后）
type User = v.InferOutput<typeof UserSchema>;
// { name: string; age: number; role: string }

// 输入类型（转换前）
type UserInput = v.InferInput<typeof UserSchema>;
// { name: string; age: string; role?: string | undefined }

// 问题类型
type UserIssue = v.InferIssue<typeof UserSchema>;
```

## 错误处理

### 自定义错误消息

```typescript
const LoginSchema = v.object({
  email: v.pipe(
    v.string("电子邮件必须是字符串"),
    v.nonEmpty("请输入您的电子邮件"),
    v.email("无效的电子邮件格式"),
  ),
  password: v.pipe(
    v.string("密码必须是字符串"),
    v.nonEmpty("请输入您的密码"),
    v.minLength(8, "密码至少需要 8 个字符"),
  ),
});
```

### 展平错误

```typescript
const result = v.safeParse(LoginSchema, data);

if (!result.success) {
  const flat = v.flatten(result.issues);
  // { nested: { email: ['无效的电子邮件格式'], password: ['...'] } }
}
```

### 问题结构

每个问题都包含：

- `kind`: 'schema' | 'validation' | 'transformation'
- `type`: 函数名（例如，'string', 'email', 'min_length'）
- `input`: 有问题的输入
- `expected`: 期望值
- `received`: 接收到的值
- `message`: 人类可读消息
- `path`: 嵌套问题的路径项数组

## 备用值

```typescript
// 静态备用值
const NumberSchema = v.fallback(v.number(), 0);
v.parse(NumberSchema, "invalid"); // 返回 0

// 动态备用值
const DateSchema = v.fallback(v.date(), () => new Date());
```

## 递归模式

```typescript
import * as v from "valibot";

type TreeNode = {
  value: string;
  children: TreeNode[];
};

const TreeNodeSchema: v.GenericSchema<TreeNode> = v.object({
  value: v.string(),
  children: v.lazy(() => v.array(TreeNodeSchema)),
});
```

## 异步验证

对于异步操作（例如，数据库检查），使用异步变体：

```typescript
import * as v from "valibot";

const isUsernameAvailable = async (username: string) => {
  // 检查数据库
  return true;
};

const UsernameSchema = v.pipeAsync(
  v.string(),
  v.minLength(3),
  v.checkAsync(isUsernameAvailable, "用户名已被占用"),
);

// 必须使用 parseAsync
const username = await v.parseAsync(UsernameSchema, "john");
```

## JSON Schema 转换

```typescript
import { toJsonSchema } from "@valibot/to-json-schema";
import * as v from "valibot";

const EmailSchema = v.pipe(v.string(), v.email());
const jsonSchema = toJsonSchema(EmailSchema);
// { type: 'string', format: 'email' }
```

## 命名规范

### 规范 1：相同名称（推荐，简单）

```typescript
export const User = v.object({
  name: v.string(),
  email: v.pipe(v.string(), v.email()),
});

export type User = v.InferOutput<typeof User>;

// 使用
const users: User[] = [];
users.push(v.parse(User, data));
```

### 规范 2：带后缀（当输入/输出不同时推荐）

```typescript
export const UserSchema = v.object({
  name: v.string(),
  age: v.pipe(v.string(), v.transform(Number)),
});

export type UserInput = v.InferInput<typeof UserSchema>;
export type UserOutput = v.InferOutput<typeof UserSchema>;
```

## 常见模式

### 登录表单

```typescript
const LoginSchema = v.object({
  email: v.pipe(
    v.string(),
    v.nonEmpty("请输入您的电子邮件"),
    v.email("无效的电子邮件地址"),
  ),
  password: v.pipe(
    v.string(),
    v.nonEmpty("请输入您的密码"),
    v.minLength(8, "密码至少需要 8 个字符"),
  ),
});
```

### API 响应

```typescript
const ApiResponseSchema = v.variant("status", [
  v.object({
    status: v.literal("success"),
    data: v.unknown(),
  }),
  v.object({
    status: v.literal("error"),
    error: v.object({
      code: v.string(),
      message: v.string(),
    }),
  }),
]);
```

### 环境变量

```typescript
const EnvSchema = v.object({
  NODE_ENV: v.picklist(["development", "production", "test"]),
  PORT: v.pipe(v.string(), v.transform(Number), v.integer(), v.minValue(1)),
  DATABASE_URL: v.pipe(v.string(), v.url()),
  API_KEY: v.pipe(v.string(), v.minLength(32)),
});

const env = v.parse(EnvSchema, process.env);
```

### 日期处理

```typescript
// 字符串到日期
const DateFromStringSchema = v.pipe(
  v.string(),
  v.isoDate(),
  v.transform((input) => new Date(input)),
);

// 日期验证
const FutureDateSchema = v.pipe(
  v.date(),
  v.minValue(new Date(), "日期必须在未来"),
);
```

## 其他资源

- [Valibot 文档](https://valibot.dev)
- [Valibot GitHub](https://github.com/open-circle/valibot)
- [API 参考](https://valibot.dev/api/)
- [从 Zod 迁移](https://valibot.dev/guides/migrate-from-zod/)
