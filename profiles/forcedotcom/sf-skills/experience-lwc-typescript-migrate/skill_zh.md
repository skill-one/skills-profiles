<!-- adk-managed-skill -->
# 将 LWC 转换为 TypeScript

将 Lightning Web Component (LWC) 包从 JavaScript 转换为 TypeScript。交付成果是一个完全带类型的 `.ts` 实现文件 **以及** 一个仅暴露 `@api` 成员（其他 LWC 消费的外部接口）的 `.d.ts` 文件。

## 使用此技能的场景

- 用户希望将单个组件或一个文件夹中的组件从 `.js` 转换到 `.ts`。
- 用户需要一个现有的 LWC 的 `.d.ts` 文件，以便其他组件（或外部 TypeScript 主机）可以安全地导入它。
- 用户正在向一个已经重命名的 `.ts` LWC 添加类型注解，而该 LWC 尚未正确地进行类型化。
- 用户希望将 JSDoc 风格的类型提示升级为真正的 TypeScript 类型。

## 前置条件

- 组件在 JavaScript 中可以正常构建和运行。
- `git` 是可用的（重命名必须通过 `git mv` 保留历史记录）。
- TypeScript 编译器已集成到构建流程中（无论是 SFDX TypeScript 管道还是独立的 `tsc` 步骤）。

---

## 工作流程

### 第 1 步 — 读取组件

打开包中的每个文件：

```text
componentName/
├── componentName.js
├── componentName.html
├── componentName.css
└── (可能) __tests__/, __utam__/, 现有的 .d.ts
```

理解：

- 哪个扩展了 `LightningElement`？类名是什么？
- 哪些字段和方法带有 `@api` 装饰器？
- 哪些属性/方法有现有的 JSDoc（用作类型提示的起点，但需根据实际使用情况进行验证——JSDoc 可能不真实）。
- 你能从代码的内部调用方式推断出哪些参数/返回类型？

### 第 2 步 — 使用 `git mv` 将 `.js` 重命名为 `.ts`

```bash
git mv componentName/componentName.js componentName/componentName.ts
```

对包中的任何辅助 `.js` 文件重复此操作（除非它们已经是 `.ts`）。**绝对不要** 使用普通的 `mv`——那样会丢失 TypeScript 审查人员依赖的历史记录链接。

### 第 3 步 — 在 `.ts` 中添加类型注解

按以下优先级顺序应用类型，以便在公共契约确定后停止：

1. **首先处理 `@api` 属性和方法。** 如果缺少 JSDoc，则生成 JSDoc，然后将 JSDoc 类型转换为 TS 语法（`string`、`number`、`boolean`、`Promise<T>`）。在信任它之前，验证每个 JSDoc 声明与代码的一致性。
2. **复杂结构变为 `interface` 或 `type` 别名**——而不是到处重复的行内结构。
3. **可选成员使用 `?`** 仅当值确实允许为 `undefined` 时。不要防御性地撒播 `?`。
4. **私有/内部状态**——仍然进行类型化，但不要导出类型。对于必须永远不会被消费者触碰的成员，使用 `private`。
5. **事件处理程序**——优先使用精确的 DOM 事件类型：
   - `MouseEvent` 用于 `onclick`（以及其他点击类处理程序）。`click` 作为 `MouseEvent` 分发——包括键盘触发的点击——因此将其类型化为 `PointerEvent` 会让处理程序依赖于仅指针字段（`pointerType`、`pressure` 等），而在这些情况下这些字段是未定义的。
   - `PointerEvent` 用于 `onpointerdown` / `onpointerup` / `onpointermove` 以及其他 `pointer*` 处理程序，其中指针特定字段确实有意义。
   - `CustomEvent<{ detail: ... }>` 用于 LWC 自定义事件。
   - `Event` 是最后的手段；在使用它时记录原因。
6. **异步方法始终返回 `Promise<T>`**——永远不会返回裸 `T`。
7. **避免使用 `any`。** 如果你确实无法对某些内容进行类型化，请使用 `unknown` 并通过类型守卫进行缩小。

#### 参考模式

加载 [[assets/type-patterns.ts|assets/type-patterns.ts]] 作为内联示例，涵盖属性类型、方法类型和事件处理程序类型。

### 第 4 步 — 生成 `.d.ts`

在 `.ts` 旁边创建 `componentName.d.ts`。它必须：

- 仅包含 **`@api` 成员**——没有私有状态，没有内部方法，没有生命周期钩子（除非它们本身是 `@api`）。
- 逐字保留 `@api` JSDoc（包括 `@type`、`@required`、`@default`、`@param`、`@returns` 标签），直接放在每个声明上方。
- 声明 LWC 模块命名空间 `c/componentName`（如果不同，则为组织的命名空间）。

模板：加载 [[assets/dts-template.ts|assets/dts-template.ts]] 作为 `.d.ts` 的初始形状。

如果组件**没有** `@api` 成员，仍然生成模块声明，并附上评论说明没有公共接口——不要跳过该文件。

### 第 5 步 — 编译和测试

- 运行 TypeScript 编译器（`tsc --noEmit` 或构建的等效命令）。在完成之前解决所有错误；不要使用 `@ts-ignore` 补丁。
- 运行组件现有的 Jest 测试。行为应保持一致。
- 无条件运行捆绑的消费者查找器——空输出是有效结果，不是跳过的理由。该脚本从 `sfdx-project.json` 的 `packageDirectories`（或回退到 `<project-root>`）解析搜索路径，拒绝任何逃逸项目根的条目，并在内部执行 LWC 导入搜索，因此调用是完全确定的：

```bash
"<skill_dir>/scripts/find-consumers.sh" "<project-root>" "<componentName>"
```

对于每个匹配项，确认消费者的预期类型与新的 `.d.ts` 公共接口仍然一致。

### 第 6 步 — 预期的最终包形状

```text
componentName/
├── componentName.ts          # 主要的 TypeScript 实现
├── componentName.html        # 模板（未更改）
├── componentName.css         # 样式（未更改）
└── componentName.d.ts        # 类型定义（新）
```

---

## 验证清单

**转换前：**

- [ ] 组件是有效的 JS，并且所有测试都通过。
- [ ] 你已经识别了所有 `@api` 成员及其预期类型。

**转换后：**

- [ ] 使用了 `git mv` 以保留历史记录。
- [ ] `.ts` 中的每个变量和参数都有一个具体的类型（没有隐式的 `any`）。
- [ ] 复杂的对象结构位于 `interface` / `type` 别名中，而不是行内重复。
- [ ] 仅在确实可选的字段上使用 `?`。
- [ ] 存在 `.d.ts`，声明 `c/componentName`，扩展 `LightningElement`，仅包含 **`@api` 成员**。
- [ ] 每个 `@api` JSDoc 都逐字保留在 `.d.ts` 中。
- [ ] `tsc` 通过且没有错误；没有使用 `@ts-ignore` 或 `any` 作为解决方法。
- [ ] Jest 测试仍然通过。

---

## 常见陷阱

- **使用 `any` 来抑制错误。** 解决实际类型问题。如果值确实未知，请使用 `unknown` + 类型守卫。
- **在 `.d.ts` 中包含私有成员。** `.d.ts` 是公共契约。内部生命周期和辅助方法不得泄漏。
- **在重命名过程中丢失 JSDoc。** 在重命名前后扫描——`@api` 成员的 JSDoc 评论必须出现在 `.ts` 和 `.d.ts` 中。
- **跳过 `git mv`。** 使审查变得痛苦，并混淆责任。
- **忘记异步返回类型。** 带有 `async` 关键字的 `foo()` 始终返回 `Promise`。声明它。
- **将 `onclick` 类型化为 `PointerEvent`。** `click` 是 `MouseEvent`（包括键盘触发的点击），因此 `PointerEvent` 字段（如 `pointerType`）对于这些事件是未定义的。将 `onclick` 类型化为 `MouseEvent`；将 `PointerEvent` 保留用于 `onpointer*` 处理程序。仅在代码分支在 `TouchEvent` 上明确区分时使用 `MouseEvent | TouchEvent`。

## 支持资源

- [LWC TypeScript 文档](https://developer.salesforce.com/docs/platform/lwc/guide/ts.html)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)
- [LWC 开发者指南](https://developer.salesforce.com/docs/component-library/documentation/en/lwc)
