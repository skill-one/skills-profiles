# 迁移到 Shoehorn

## 为什么使用 Shoehorn？

`shoehorn` 允许你在测试中传入部分数据，同时保持 TypeScript 的类型安全。它用类型安全的替代方案替换 `as` 断言。

**仅用于测试代码。** 永远不要在生产代码中使用 shoehorn。

测试中 `as` 的问题：

- 经过训练，不去使用它
- 必须手动指定目标类型
- 对故意错误的数据需要双重断言（`as unknown as Type`）

## 安装

```bash
npm i @total-typescript/shoehorn
```

## 迁移模式

### 包含少量所需属性的大型对象

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
getUser({ body: { id: 123 } } as unknown as Request); // 故意使用错误类型
```

之后：

```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```

## 何时使用每个函数

| 函数        | 用例                                           |
| --------------- | -------------------------------------------------- |
| `fromPartial()` | 传入仍能进行类型检查的部分数据                |
| `fromAny()`     | 传入故意错误的数据（保留自动补全）             |
| `fromExact()`   | 强制使用完整对象（之后可换成 fromPartial）          |

## 工作流程

1. **收集需求** — 询问用户：
   - 哪些测试文件中的 `as` 断言造成问题？
   - 是否在处理大型对象，但只关心部分属性？
   - 是否需要传入故意错误的数据来测试错误路径？

2. **安装和迁移**：
   - [ ] 安装：`npm i @total-typescript/shoehorn`
   - [ ] 查找测试文件中的 `as` 断言：`grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] 用 `fromPartial()` 替换 `as Type`
   - [ ] 用 `fromAny()` 替换 `as unknown as Type`
   - [ ] 添加来自 `@total-typescript/shoehorn` 的导入
   - [ ] 运行类型检查验证
