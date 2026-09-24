# 迁移到 Shoehorn

## 为什么使用 shoehorn?

`shoehorn` 允许你在测试中传入部分数据，同时保持 TypeScript 的兼容性。它用类型安全的替代方案替换了 `as` 断言。

**仅限测试代码。** 切勿在生产代码中使用 shoehorn。

测试中 `as` 存在的问题：

- 习惯不在此使用
- 必须手动指定目标类型
- 为故意错误的数据使用双重 `as`（`as unknown as Type`）

## 安装

```bash
npm i @total-typescript/shoehorn
```

## 迁移模式

### 需要少量属性的大型对象

之前：

```ts
type Request = {
  body: { id: string };
  headers: Record<string, string>;
  cookies: Record<string, string>;
  // ...20 more properties
};

it("gets user by id", () => {
  // Only care about body.id but must fake entire Request
  getUser({
    body: { id: "123" },
    headers: {},
    cookies: {},
    // ...fake all 20 properties
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
getUser({ body: { id: 123 } } as unknown as Request); // wrong type on purpose
```

之后：

```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```

## 各函数的使用场景

 | Function        | Use case                                           |
 | --------------- | -------------------------------------------------- |
 | `fromPartial()` | 传入仍能通过类型检查的部分数据                   |
 | `fromAny()`     | 传入故意错误的数据（保留自动补全）               |
 | `fromExact()`   | 强制传入完整对象（后续可替换为 fromPartial）      |

## 工作流程

1. **收集需求** - 询问用户：
   - 哪些测试文件包含导致问题的 `as` 断言？
   - 它们是否涉及只需要部分属性生效的大型对象？
   - 它们是否需要为了错误测试而传入故意错误的数据？

2. **安装并迁移**：
   - [ ] 安装：`npm i @total-typescript/shoehorn`
   - [ ] 查找包含 `as` 断言的测试文件：`grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] 将 `as Type` 替换为 `fromPartial()`
   - [ ] 将 `as unknown as Type` 替换为 `fromAny()`
   - [ ] 添加 `@total-typescript/shoehorn` 的导入
   - [ ] 运行类型检查以验证
