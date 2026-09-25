# TypeScript 高级类型

全面指南，用于掌握 TypeScript 高级类型系统（包括泛型、条件类型、映射类型、模板字面量类型和工具类型），以构建健壮、类型安全的程序。

## 何时使用本技能

- 构建类型安全的库或框架时使用
- 创建可复用的泛型组件时使用
- 实现复杂的类型推断逻辑时使用
- 设计类型安全的 API 客户端时使用
- 构建表单验证系统时使用
- 创建强类型配置对象时使用
- 实现类型安全的 state 管理时使用
- 将 JavaScript 代码库迁移至 TypeScript 时使用

## 核心概念

### 1. 泛型

**目的：** 在保持类型安全的同时，创建可复用、类型灵活的组件。

**基础泛型函数：**

```typescript
function identity<T>(value: T): T {
  return value;
}

const num = identity <number>(42); // Type: number
const str = identity <string>("hello"); // Type: string
const auto = identity <true>(); // Type inferred: boolean
```

**泛型约束：**

```typescript
interface HasLength {
  length: number;
}

function logLength<T extends HasLength>(item: T): T {
  console.log(item.length);
  return item;
}

logLength("hello"); // OK: string has length
logLength([1, 2, 3]); // OK: array has length
logLength({ length: 10 }); // OK: object has length
// logLength(42);             // Error: number has no length
```

**多个类型参数：**

```typescript
function merge<T, U>(obj1: T, obj2: U): T & U {
  return { ...obj1, ...obj2 };
}

const merged = merge({ name: "John" }, { age: 30 });
// Type: { name: string } & { age: number }
```

### 2. 条件类型

**目的：** 创建根据条件而变化的类型，以实现复杂的类型逻辑。

**基础条件类型：**

```typescript
type IsString<T>=T extends string ? true : false;

type A = IsString<string>; // true
type B = IsString <number>; // false
```

**提取返回类型：**

```typescript
type ReturnType<T>=T extends (...args: any[]) => infer R ? R : never;

function getUser() {
  return { id: 1, name: "John" };
}

type User = ReturnType <typeof getUser>;
// Type: { id: number; name: string; }
```

**分布条件类型：**

```typescript
type ToArray<T>=T extends any ? T[] : never;

type StrOrNumArray = ToArray <string | number>;
// Type: string[] | number[]
```

**嵌套条件：**

```typescript
type TypeName<T>=T extends string
  ? "string"
  : T extends number
    ? "number"
    : T extends boolean
      ? "boolean"
      : T extends undefined
        ? "undefined"
        : T extends Function
          ? "function"
          : "object";

type T1 = TypeName <string>; // "string"
type T2 = TypeName <() => void>; // "function"
```

### 3. 映射类型

**目的：** 通过遍历其属性来转换现有类型。

**基础映射类型：**

```typescript
type Readonly<T>={
  readonly [P in key of T]: T[P];
};

interface User {
  id: number;
  name: string;
}

type ReadonlyUser = Readonly<User>;
// Type: { readonly id: number; readonly name: string; }
```

**可选属性：**

```typescript
type Partial<T>={
  [P in key of T]?: T[P];
};

type PartialUser = Partial<User>;
// Type: { id?: number; name?: string; }
```

**键重映射：**

```typescript
type Getters<T>={
  [K in key of T as `get${Capitalize<string & K>'}`]: () => T[K];
};

interface Person {
  name: string;
  age: number;
}

type PersonGetters = Getters <Person>;
// Type: { getName: () => string; getAge: () => number; }
```

**属性过滤：**

```typescript
type PickByType<T, U>={
  [K in key of T as T[K] extends U ? K : never]: T[K];
};

interface Mixed {
  id: number;
  name: string;
  age: number;
  active: boolean;
}

type OnlyNumbers = PickByType<Mixed, number>;
// Type: { id: number; age: number; }
```

### 4. 模板字面量类型

**目的：** 创建基于字符串的类型，支持模式匹配与转换。

**基础模板字面量：**

```typescript
type EventName = "click" | "focus" | "blur";
type EventHandler = `on${Capitalize <EventName>'}`;
// Type: "onClick" | "onFocus" | "onBlur"
```

**字符串操作：**

```typescript
type UppercaseGreeting = Uppercase <"hello">; // "HELLO"
type LowercaseGreeting = Lowercase <"HELLO">; // "hello"
type CapitalizedName = Capitalize <"john">; // "John"
type UncapitalizedName = Uncapitalize <"John">; // "john"
```

**路径构建：**

```typescript
type Path<T>=T extends object
  ? {
      [K in key of T]: K extends string ? `${K}` | `${K}.${Path<T[K]>}` : never;
    }[key of T]
  : never;

interface Config {
  server: {
    host: string;
    port: number;
  };
  database: {
    url: string;
  };
}

type ConfigPath = Path <Config>;
// Type: "server" | "database" | "server.host" | "server.port" | "database.url"
```

### 5. 工具类型

**内置工具类型：**

```typescript
// Partial<T>- Make all properties optional
type PartialUser = Partial<User>;

// Required<T>- Make all properties required
type RequiredUser = Required <PartialUser>;

// Readonly<T>- Make all properties readonly
type ReadonlyUser = Readonly<User>;

// Pick<T, K>- Select specific properties
type UserName = Pick <User, "name" | "email">;

// Omit<T, K>- Remove specific properties
type UserWithoutPassword = Omit <User, "password">;

// Exclude<T, U>- Exclude types from union
type T1 = Exclude <"a" | "b" | "c", "a">; // "b" | "c"

// Extract<T, U>- Extract types from union
type T2 = Extract <"a" | "b" | "c", "a" | "b">; // "a" | "b"

// NonNullable<T>- Exclude null and undefined
type T3 = NonNullable <string | null | undefined>; // string

// Record<K, T>- Create object type with keys K and values T
type PageInfo = Record <"home" | "about", { title: string }>;
```

## 详细示例与模式

以 `## Advanced Patterns` 开头的详细章节位于 `references/details.md` 文件中。若上述导航摘要不够详细，请阅读该文件。

## 最佳实践

1. **使用 `unknown` 而非 `any`**：强制执行类型检查
2. **对象结构优先使用 `interface`**：获得更好的错误提示信息
3. **对联合类型和复杂类型使用 `type`**：更具灵活性
4. **利用类型推断**：尽可能让 TypeScript 进行推断
5. **创建辅助类型**：构建可复用的类型工具
6. **使用 const 断言**：保留字面量类型
7. **避免使用类型断言**：改用类型守卫
8. **文档化复杂类型**：添加 JSDoc 注释
9. **启用严格模式**：开启所有严格编译选项
10. **测试你的类型**：使用类型测试来验证类型的实际行为

## 类型测试

```typescript
// Type assertion tests
type AssertEqual<T, U>=[T] extends [U]
  ? [U] extends [T]
    ? true
    : false
  : false;

type Test1 = AssertEqual<string, string>; // true
type Test2 = AssertEqual<string, number>; // false
type Test3 = AssertEqual<string | number, string>; // false;

// Expect error helper
type ExpectError<T extends never>=T;

// Example usage
type ShouldError = ExpectError <AssertEqual<string, number>>;
```

## 常见陷阱

1. **过度使用 `any`**：违背了 TypeScript 的初衷
2. **忽略严格空值检查**：可能导致运行时错误
3. **类型过于复杂**：可能会拖慢编译速度
4. **未使用判别联合类型**：错失了类型收窄的机会
5. **忽略 readonly 修饰符**：允许未经意料的修改
6. **循环类型引用**：可能导致编译器报错
7. **未处理边界情况**：如空数组或 null 值

## 性能考量

- 避免深层嵌套的条件类型
- 尽可能使用简单的类型
- 缓存复杂的类型计算
- 限制递归类型中的递归深度
- 使用构建工具在 production 环境中跳过类型检查
