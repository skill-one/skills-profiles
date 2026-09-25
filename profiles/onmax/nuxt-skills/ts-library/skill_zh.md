# TypeScript 库开发

从研究 unocss、shiki、unplugin、vite、vitest、vueuse、zod、trpc、drizzle-orm 等项目提取的高质量 TypeScript 库开发模式。

## 何时使用

- 开始新的 TypeScript 库（单库或单一代码库）
- 设置 `package.json` 导出以支持 CJS/ESM 双重导出
- 配置库开发的 tsconfig
- 选择构建工具（tsdown、unbuild）
- 设计类型安全的 API（构建器、工厂、插件模式）
- 编写高级 TypeScript 类型
- 设置 vitest 进行库测试
- 配置发布工作流和 CI

**对于 Nuxt 模块开发：** 使用 `nuxt-modules` 技能

## 快速参考

| 正在处理...         | 加载文件                                                          |
| --------------------- | ------------------------------------------------------------------ |
| 新项目设置     | [references/project-setup.md](references/project-setup.md)         |
| 包导出       | [references/package-exports.md](references/package-exports.md)     |
| tsconfig 选项      | [references/typescript-config.md](references/typescript-config.md) |
| 构建配置   | [references/build-tooling.md](references/build-tooling.md)         |
| ESLint 配置         | [references/eslint-config.md](references/eslint-config.md)         |
| API 设计模式   | [references/api-design.md](references/api-design.md)               |
| 类型推断技巧 | [references/type-patterns.md](references/type-patterns.md)         |
| 测试设置         | [references/testing.md](references/testing.md)                     |
| 发布工作流      | [references/release.md](references/release.md)                     |
| CI/CD 设置           | [references/ci-workflows.md](references/ci-workflows.md)           |

## 加载文件

**根据您的任务考虑加载以下参考文件：**

- [ ] [references/project-setup.md](references/project-setup.md) - 如果开始新的 TypeScript 库项目
- [ ] [references/package-exports.md](references/package-exports.md) - 如果配置 `package.json` 导出或 CJS/ESM 双重导出
- [ ] [references/typescript-config.md](references/typescript-config.md) - 如果设置或修改 tsconfig.json
- [ ] [references/build-tooling.md](references/build-tooling.md) - 如果配置 tsdown、unbuild 或构建脚本
- [ ] [references/eslint-config.md](references/eslint-config.md) - 如果为库开发设置 ESLint
- [ ] [references/api-design.md](references/api-design.md) - 如果设计公共 API、构建器模式或插件系统
- [ ] [references/type-patterns.md](references/type-patterns.md) - 如果处理高级 TypeScript 类型或类型推断
- [ ] [references/testing.md](references/testing.md) - 如果设置 vitest 或为库代码编写测试
- [ ] [references/release.md](references/release.md) - 如果配置发布工作流或版本控制
- [ ] [references/ci-workflows.md](references/ci-workflows.md) - 如果设置 GitHub Actions 或 CI/CD 管道

**不要一次性加载所有文件。** 仅加载与当前任务相关的文件。

## 新库工作流

1. 创建项目结构 → 加载 [references/project-setup.md](references/project-setup.md)
2. 配置 `package.json` 导出 → 加载 [references/package-exports.md](references/package-exports.md)
3. 使用 tsdown 设置构建 → 加载 [references/build-tooling.md](references/build-tooling.md)
4. 验证构建: `pnpm build && pnpm pack --dry-run` — 检查输出是否包含 `.mjs`、`.cjs`、`.d.ts`
5. 添加测试 → 加载 [references/testing.md](references/testing.md)
6. 配置发布 → 加载 [references/release.md](references/release.md)

## 快速入门

```json
// package.json (最小配置)
{
  "name": "my-lib",
  "type": "module",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    }
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "files": ["dist"]
}
```

```ts
// tsdown.config.ts
import { defineConfig } from 'tsdown'

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  dts: true,
})
```

## 核心原则

- ESM 优先: `"type": "module"` 并使用 `.mjs` 输出
- 双重格式: 始终支持 CJS 和 ESM 消费者
- `moduleResolution: "Bundler"` 用于现代 TypeScript
- tsdown 用于大多数构建，unbuild 用于复杂情况
- 智能默认值: 检测环境，不要强制配置
- 可树形拆分: 懒加载获取器，正确设置 `sideEffects: false`

_令牌效率: 主技能 ~300 令牌，每个参考 ~800-1200 令牌_
