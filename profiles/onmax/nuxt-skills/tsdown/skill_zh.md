# tsdown

Rolldown + Oxc 驱动的 TypeScript 打包工具。即插即用的 tsup 替代品。

## 使用场景

- 构建 TypeScript 库
- 生成 .d.ts 声明文件
- 发布 npm 包
- 支持 ESM/CJS 双输出
- Vue/React 组件库

## 快速入门

```bash
npm i -D tsdown typescript
```

```ts
// tsdown.config.ts
import { defineConfig } from 'tsdown'

export default defineConfig({
  entry: 'src/index.ts',
  format: 'esm',
  dts: true,
  exports: true,
})
```

```bash
tsdown           # 构建
tsdown --watch   # 监听模式
```

## 参考文件

| 任务                                          | 文件                                  |
| --------------------------------------------- | ------------------------------------- |
| 配置文件、CLI、入口点                          | [config.md](references/config.md)     |
| 格式、目标、dts、输出、验证                    | [output.md](references/output.md)     |
| 补丁、解包、监听、框架集成、WebAssembly          | [features.md](references/features.md) |
| 插件、钩子、校验、程序化、迁移                  | [advanced.md](references/advanced.md) |

## 文件加载

**根据您的任务考虑加载以下参考文件：**

- [ ] [references/config.md](references/config.md) - 如果设置 tsdown.config.ts、CLI 或入口点
- [ ] [references/output.md](references/output.md) - 如果配置输出格式、目标、.d.ts、输出或验证
- [ ] [references/features.md](references/features.md) - 如果使用补丁、解包、监听模式、框架集成或 WebAssembly
- [ ] [references/advanced.md](references/advanced.md) - 如果编写插件、使用校验/验证、程序化 API 或从 tsup 迁移

**不要一次性加载所有文件。** 仅加载与当前任务相关的文件。

## 跨技能参考

- **库模式** → 使用 `ts-library` 技能
- **Vue 组件库** → 使用 `vue` 技能
- **包管理** → 使用 `pnpm` 技能
