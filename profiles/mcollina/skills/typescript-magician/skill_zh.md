## 何时使用

使用此技能：
- 解决 TypeScript 错误和类型挑战
- 从代码库中消除 `any` 类型
- 处理复杂的泛型和类型推断问题
- 需要严格类型时

## 说明

调用时：
1. 运行 `tsc --noEmit` 在修改前捕获完整的错误输出
2. 确定类型问题的根本原因（不安全的推断、缺失约束、隐式 `any` 等）
3. 使用高级 TypeScript 功能构建精确、类型安全的解决方案
4. 使用正确的类型消除所有 `any` 类型——验证每个替换是否仍满足调用点
5. 使用第二次 `tsc --noEmit` 确认修复能干净编译

功能包括：
- 高级泛型和条件类型
- 模板字面量类型和映射类型
- 工具类型和类型操作
- 品牌类型和命名类型
- 复杂的推断模式
- 变异和分布规则
- 模块增强和声明合并

对于每个 TypeScript 挑战：
- 解释问题背后的类型理论
- 在适用情况下提供多种解决方案
- 显示前后类型表示
- 包含全面的类型测试
- 确保完整的 IntelliSense 支持

## 快速示例

### 使用泛型消除 `any`

**之前**
```ts
function getProperty(obj: any, key: string): any {
  return obj[key];
}
```

**之后**
```ts
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
// getProperty({ name: "Alice" }, "name") → 推断为 string ✓
```

### 窄化未知 API 响应

**之前**
```ts
async function fetchUser(): Promise<any> {
  const res = await fetch("/api/user");
  return res.json();
}
```

**之后**
```ts
interface User { id: number; name: string }

function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "name" in value
  );
}

async function fetchUser(): Promise<User> {
  const res = await fetch("/api/user");
  const data: unknown = await res.json();
  if (!isUser(data)) throw new Error("无效的用户形状");
  return data;
}
```

## 参考

阅读单个规则文件获取详细解释和代码示例：

### 核心模式
- [rules/as-const-typeof.md](rules/as-const-typeof.md) - 使用 `as const` 和 `typeof` 从运行时值派生类型
- [rules/array-index-access.md](rules/array-index-access.md) - 使用 `[number]` 索引访问数组元素类型
- [rules/utility-types.md](rules/utility-types.md) - 内置工具类型：Parameters、ReturnType、Awaited、Omit、Partial、Record

### 高级泛型
- [rules/generics-basics.md](rules/generics-basics.md) - 泛型类型的基础知识、约束和推断
- [rules/builder-pattern.md](rules/builder-pattern.md) - 使用链式方法的类型安全构建器模式
- [rules/deep-inference.md](rules/deep-inference.md) - 使用 F.Narrow 和 const 类型参数实现深度类型推断

### 类型级编程
- [rules/conditional-types.md](rules/conditional-types.md) - 用于类型级 if/else 逻辑的条件类型
- [rules/infer-keyword.md](rules/infer-keyword.md) - 在条件类型中使用 `infer` 提取类型
- [rules/template-literal-types.md](rules/template-literal-types.md) - 类型级字符串操作
- [rules/mapped-types.md](rules/mapped-types.md) - 通过转换现有类型属性创建新类型

### 类型安全模式
- [rules/opaque-types.md](rules/opaque-types.md) - 品牌类型和 opaque 类型用于类型安全的标识符
- [rules/type-narrowing.md](rules/type-narrowing.md) - 通过控制流分析窄化类型
- [rules/function-overloads.md](rules/function-overloads.md) - 使用函数重载处理复杂的函数签名

### 调试
- [rules/error-diagnosis.md](rules/error-diagnosis.md) - 诊断和理解 TypeScript 类型错误的策略
