# TypeScript Pro

## 核心工作流

1. **分析类型架构** - 审查 tsconfig、类型覆盖率、构建性能
2. **设计类型优先的 API** - 创建品牌类型、泛型、工具类型
3. **使用类型安全实现** - 编写类型守卫、区分联合类型、条件类型；运行 `tsc --noEmit` 在继续之前捕获类型错误
4. **优化构建** - 配置项目引用、增量编译、树摇；更改后重新运行 `tsc --noEmit` 确认零错误
5. **测试类型** - 使用 `type-coverage` 等工具确认类型覆盖率；验证所有公共 API 是否具有显式返回类型；迭代步骤 3–4 直到所有检查通过

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|-------|-----------|-----------|
| 高级类型 | `references/advanced-types.md` | 泛型、条件类型、映射类型、模板字面量 |
| 类型守卫 | `references/type-guards.md` | 类型收窄、区分联合类型、断言函数 |
| 工具类型 | `references/utility-types.md` | Partial、Pick、Omit、Record、自定义工具类型 |
| 配置 | `references/configuration.md` | tsconfig 选项、严格模式、项目引用 |
| 模式 | `references/patterns.md` | 构建者模式、工厂模式、类型安全的 API |

## 代码示例

### 品牌类型
```typescript
// 域建模的品牌类型
type Brand<T, B extends string> = T & { readonly __brand: B };
type UserId  = Brand<string, "UserId">;
type OrderId = Brand<number, "OrderId">;

const toUserId  = (id: string): UserId  => id as UserId;
const toOrderId = (id: number): OrderId => id as OrderId;

// 使用示例 — 在编译时防止意外 ID 混淆
function getOrder(userId: UserId, orderId: OrderId) { /* ... */ }
```

### 区分联合类型 & 类型守卫
```typescript
type LoadingState = { status: "loading" };
type SuccessState = { status: "success"; data: string[] };
type ErrorState   = { status: "error";   error: Error };
type RequestState = LoadingState | SuccessState | ErrorState;

// 类型谓词守卫
function isSuccess(state: RequestState): state is SuccessState {
  return state.status === "success";
}

// 区分联合的穷尽 switch
function renderState(state: RequestState): string {
  switch (state.status) {
    case "loading": return "Loading…";
    case "success": return state.data.join(", ");
    case "error":   return state.error.message;
    default: {
      const _exhaustive: never = state;
      throw new Error(`未处理的 state: ${_exhaustive}`);
    }
  }
}
```

### 自定义工具类型
```typescript
// 深度只读 — 不可变的嵌套对象
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

// 要求恰好一个键
type RequireExactlyOne<T, Keys extends keyof T = keyof T> =
  Pick<T, Exclude<keyof T, Keys>> &
  { [K in Keys]-?: Required<Pick<T, K>> & Partial<Record<Exclude<Keys, K>, never>> }[Keys];
```

### 推荐的 tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "isolatedModules": true,
    "declaration": true,
    "declarationMap": true,
    "incremental": true,
    "skipLibCheck": false
  }
}
```

## 限制

### 必须
- 启用所有编译器标志的严格模式
- 使用类型优先的 API 设计
- 为域建模实现品牌类型
- 使用 `satisfies` 运算符进行类型验证
- 为状态机创建区分联合类型
- 使用带类型谓词的 `Annotated` 模式
- 为库生成声明文件
- 优化类型推断

### 禁止
- 无正当理由使用显式 `any`
- 公共 API 跳过类型覆盖率
- 混合类型仅和值导入
- 禁用严格空值检查
- 无必要使用 `as` 断言
- 忽略编译器性能警告
- 跳过声明文件生成
- 使用枚举（优先使用带 `as const` 的常量对象）

## 输出模板

实现 TypeScript 功能时提供：
1. 类型定义（接口、类型、泛型）
2. 带类型守卫的实现
3. 如有需要，tsconfig 配置
4. 类型设计决策的简要说明

## 知识参考

TypeScript 5.0+、泛型、条件类型、映射类型、模板字面量类型、区分联合类型、类型守卫、品牌类型、tRPC、项目引用、增量编译、声明文件、常量断言、satisfies 运算符

[文档](https://jeffallan.github.io/claude-skills/skills/language/typescript-pro/)
