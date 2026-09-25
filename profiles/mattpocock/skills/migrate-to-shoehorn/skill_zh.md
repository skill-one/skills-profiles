# 迁移到 Shoehorn

## 为什么使用 Shoehorn？

`shoehorn` 允许你在测试中传递部分数据，同时保持 TypeScript 的满意度。它用类型安全的替代方案替换了 `as` 断言。

**仅用于测试代码。** 永远不要在生产代码中使用 shoehorn。

`as` 在测试中的问题：

- 养成不使用它的习惯
- 必须手动指定目标类型
- 双重断言 (`as unknown as Type`) 用于故意传递错误数据

## 安装

```bash
npm i @total-typescript/shoehorn
```

## 迁移模式

### 具有少量所需属性的大型对象

之前：

```ts
type Request = {
  body: { id: string };
  headers: Record<string, string>;
  cookies: Record<string, string>;
  // ...还有 20 个其他属性
};

it("gets user by id", () => {
  // 只关心 body.id 但必须伪造整个 Request
  getUser({
    body: { id: "123" },
    headers: {},
    cookies: {},
    // ...伪造所有 20 个属性
  });
});
```

之后：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

it("gets user by id", () => {
  getUser(
    fromPartial({
      body: { id: "123" },
    }),
  );
});
```

### `as Type` → `fromPartial()`

之前：

```ts
getUser({ body: { id: "123" } } as Request);
```

之后：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

getUser(fromPartial({ body: { id: "123" } }));
```

### `as unknown as Type` → `fromAny()`

之前：

```ts
getUser({ body: { id: 123 } } as unknown as Request); // 故意传递错误类型
```

之后：

```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```

## 何时使用每个函数

| 函数        | 用例                                           |
| --------------- | -------------------------------------------------- |
| `fromPartial()` | 传递仍然能通过类型检查的部分数据           |
| `fromAny()`     | 传递故意传递的错误数据（保留自动补全） |
| `fromExact()`   | 强制传递完整对象（稍后与 fromPartial 交换） |

## 工作流程

1. **收集需求** - 询问用户：
   - 哪些测试文件中的 `as` 断言导致了问题？
   - 他们是否在处理只有部分属性重要的较大对象？
   - 他们是否需要为错误测试传递故意传递的错误数据？

2. **安装和迁移**：
   - [ ] 安装：`npm i @total-typescript/shoehorn`
   - [ ] 查找包含 `as` 断言的测试文件：`grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] 将 `as Type` 替换为 `fromPartial()`
   - [ ] 将 `as unknown as Type` 替换为 `fromAny()`
   - [ ] 添加来自 `@total-typescript/shoehorn` 的导入
   - [ ] 运行类型检查以验证
