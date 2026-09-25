# @json-render/codegen

跨框架的实用工具，用于从 json-render UI 树生成代码。使用这些工具来构建 Next.js、Remix 或其他框架的自定义代码导出器。

## 安装

```bash
npm install @json-render/codegen
```

## 树遍历

```typescript
import {
  traverseSpec,
  collectUsedComponents,
  collectStatePaths,
  collectActions,
} from "@json-render/codegen";

// 深度优先遍历 spec
traverseSpec(spec, (element, key, depth, parent) => {
  console.log(`${" ".repeat(depth * 2)}${key}: ${element.type}`);
});

// 获取所有使用的组件类型
const components = collectUsedComponents(spec);
// Set { "Card", "Metric", "Button" }

// 获取所有引用的状态路径
const statePaths = collectStatePaths(spec);
// Set { "analytics/revenue", "user/name" }

// 获取所有动作名称
const actions = collectActions(spec);
// Set { "submit_form", "refresh_data" }
```

## 序列化

```typescript
import {
  serializePropValue,
  serializeProps,
  escapeString,
  type SerializeOptions,
} from "@json-render/codegen";

// 序列化单个值
serializePropValue("hello");
// { value: '"hello"', needsBraces: false }

serializePropValue({ $state: "/user/name" });
// { value: '{ $state: "/user/name" }', needsBraces: true }

// 序列化 JSX 的属性
serializeProps({ title: "Dashboard", columns: 3, disabled: true });
// 'title="Dashboard" columns={3} disabled'

// 为代码转义字符串
escapeString('hello "world"');
// 'hello \"world\"'
```

### SerializeOptions

```typescript
interface SerializeOptions {
  quotes?: "single" | "double";
  indent?: number;
}
```

## 类型

```typescript
import type { GeneratedFile, CodeGenerator } from "@json-render/codegen";

const myGenerator: CodeGenerator = {
  generate(spec) {
    return [
      { path: "package.json", content: "..." },
      { path: "app/page.tsx", content: "..." },
    ];
  },
};
```

## 构建自定义生成器

```typescript
import {
  collectUsedComponents,
  collectStatePaths,
  traverseSpec,
  serializeProps,
  type GeneratedFile,
} from "@json-render/codegen";
import type { Spec } from "@json-render/core";

export function generateNextJSProject(spec: Spec): GeneratedFile[] {
  const files: GeneratedFile[] = [];
  const components = collectUsedComponents(spec);
  // 生成 package.json、组件文件、主页面...
  return files;
}
```
