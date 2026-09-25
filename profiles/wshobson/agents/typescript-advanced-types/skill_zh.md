# TypeScript 高级类型

全面指导，掌握TypeScript的高级类型系统，包括泛型、条件类型、映射类型、模板字面量类型以及用于构建健壮、类型安全的应用程序的工具类型。

## 何时使用此技能

- 构建类型安全的库或框架
- 创建可重用的泛型组件
- 实现复杂的类型推断逻辑
- 设计类型安全的API客户端
- 构建表单验证系统
- 创建强类型的配置对象
- 实现类型安全的状态管理
- 将JavaScript代码库迁移到TypeScript

## 核心概念

### 1. 泛型

**目的**：创建可重用、类型灵活的组件，同时保持类型安全。

**基本泛型函数**：

```typescript
function identity<T>(value: T): T {
  return value;
}

const num = identity<number>(42); // 类型：number
const str = identity<string>("hello"); // 类型：string
const auto = identity(true); // 类型推断：boolean
```

**泛型约束**：

```typescript
interface HasLength {
  length: number;
}

function logLength<T extends HasLength>(item: T): T {
  console.log(item.length);
  return item;
}

logLength("hello"); // OK：string具有length属性
logLength([1, 2, 3]); // OK：数组具有length属性
logLength({ length: 10 }); // OK：对象具有length属性
// logLength(42);             // 错误：number没有length属性
```

**多个类型参数**：

```typescript
function merge<T, U>(obj1: T, obj2: U): T & U {
  return { ...obj1, ...obj2 };
}

const merged = merge({ name: "John" }, { age: 30 });
// 类型：{ name: string } & { age: number }
```

### 2. 条件类型

**目的**：创建依赖于条件的类型，实现复杂的类型逻辑。

**基本条件类型**：

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>; // true
type B = IsString<number>; // false
```

**提取返回类型**：

```typescript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

function getUser() {
  return { id: 1, name: "John" };
}

type User = ReturnType<typeof getUser>;
// 类型：{ id: number; name: string; }
```

**分布式条件类型**：

```typescript
type ToArray<T> = T extends any ? T[] : never;

type StrOrNumArray = ToArray<string | number>;
// 类型：string[] | number[]
```

**嵌套条件**：

```typescript
type TypeName<T> = T extends string
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

type T1 = TypeName<string>; // "string"
type T2 = TypeName<() => void>; // "function"
```

### 3. 映射类型

**目的**：通过遍历其属性来转换现有类型。

**基本映射类型**：

```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

interface User {
  id: number;
  name: string;
}

type ReadonlyUser = Readonly<User>;
// 类型：{ readonly id: number; readonly name: string; }
```

**可选属性**：

```typescript
type Partial<T> = {
  [P in keyof T]?: T[P];
};

type PartialUser = Partial<User>;
// 类型：{ id?: number; name?: string; }
```

**键重映射**：

```typescript
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface Person {
  name: string;
  age: number;
}

type PersonGetters = Getters<Person>;
// 类型：{ getName: () => string; getAge: () => number; }
```

**过滤属性**：

```typescript
type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K];
};

interface Mixed {
  id: number;
  name: string;
  age: number;
  active: boolean;
}

type OnlyNumbers = PickByType<Mixed, number>;
// 类型：{ id: number; age: number; }
```

### 4. 模板字面量类型

**目的**：创建基于字符串的类型，支持模式匹配和转换。

**基本模板字面量**：

```typescript
type EventName = "click" | "focus" | "blur";
type EventHandler = `on${Capitalize<EventName>}`;
// 类型："onClick" | "onFocus" | "onBlur"
```

**字符串操作**：

```typescript
type UppercaseGreeting = Uppercase<"hello">; // "HELLO"
type LowercaseGreeting = Lowercase<"HELLO">; // "hello"
type CapitalizedName = Capitalize<"john">; // "John"
type UncapitalizedName = Uncapitalize<"John">; // "john"
```

**路径构建**：

```typescript
type Path<T> = T extends object
  ? {
      [K in keyof T]: K extends string ? `${K}` | `${K}.${Path<T[K]>}` : never;
    }[keyof T]
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

type ConfigPath = Path<Config>;
// 类型："server" | "database" | "server.host" | "server.port" | "database.url"
```

### 5. 工具类型

**内置工具类型**：

```typescript
// Partial<T> - 使所有属性可选
type PartialUser = Partial<User>;

// Required<T> - 使所有属性必需
type RequiredUser = Required<PartialUser>;

// Readonly<T> - 使所有属性只读
type ReadonlyUser = Readonly<User>;

// Pick<T, K> - 选择特定属性
type UserName = Pick<User, "name" | "email">;

// Omit<T, K> - 移除特定属性
type UserWithoutPassword = Omit<User, "password">;

// Exclude<T, U> - 从联合类型中排除类型
type T1 = Exclude<"a" | "b" | "c", "a">; // "b" | "c"

// Extract<T, U> - 从联合类型中提取类型
type T2 = Extract<"a" | "b" | "c", "a" | "b">; // "a" | "b"

// NonNullable<T> - 排除null和undefined
type T3 = NonNullable<string | null | undefined>; // string

// Record<K, T> - 创建具有键K和值T的对象类型
type PageInfo = Record<"home" | "about", { title: string }>;
```

## 详细示例和模式

详细部分（以`## 高级模式`开头）位于`references/details.md`中。当上面的导航摘要不足以满足需求时，请阅读该文件。

## 最佳实践

1. **使用`unknown`而不是`any`**：强制类型检查
2. **优先使用`interface`定义对象形状**：更好的错误消息
3. **使用`type`定义联合和复杂类型**：更灵活
4. **利用类型推断**：让TypeScript在可能的情况下进行推断
5. **创建辅助类型**：构建可重用的类型工具
6. **使用const断言**：保留字面量类型
7. **避免类型断言**：使用类型守卫代替
8. **记录复杂类型**：添加JSDoc注释
9. **使用严格模式**：启用所有严格编译选项
10. **测试你的类型**：使用类型测试来验证类型行为

## 类型测试

```typescript
// 类型断言测试
type AssertEqual<T, U> = [T] extends [U]
  ? [U] extends [T]
    ? true
    : false
  : false;

type Test1 = AssertEqual<string, string>; // true
type Test2 = AssertEqual<string, number>; // false
type Test3 = AssertEqual<string | number, string>; // false

// Expect error辅助类型
type ExpectError<T extends never> = T;

// 示例用法
type ShouldError = ExpectError<AssertEqual<string, number>>;
```

## 常见陷阱

1. **过度使用`any`**：违背了TypeScript的初衷
2. **忽略严格空值检查**：可能导致运行时错误
3. **类型过于复杂**：可能减慢编译速度
4. **不使用区分联合**：错失类型收窄的机会
5. **忘记只读修饰符**：允许意外的修改
6. **循环类型引用**：可能导致编译器错误
7. **不处理边缘情况**：如空数组或null值

## 性能考虑

- 避免使用深层嵌套的条件类型
- 尽可能使用简单类型
- 缓存复杂的类型计算
- 限制递归类型中的递归深度
- 使用构建工具在生产环境中跳过类型检查
