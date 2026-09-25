# Rsbuild 最佳实践

在编写或审查 Rsbuild 项目时，请遵循这些规则。

## 配置

- 使用 `rsbuild.config.ts` 和 `defineConfig`
- 仅在没有 Rsbuild 一流选项时使用 `tools.rspack` 或 `tools.bundlerChain`
- 为多页面应用程序定义明确的 `source.entry` 值
- 在 TypeScript 项目中，优先使用 `tsconfig.json` 路径别名

## CLI

- 使用 `rsbuild` 进行本地开发
- 使用 `rsbuild build` 进行生产构建
- 仅使用 `rsbuild preview` 进行本地生产预览
- 使用 `rsbuild inspect` 检查最终的 Rsbuild/Rspack 配置

## 类型检查

- 使用 `@rsbuild/plugin-type-check` 进行集成开发/构建类型检查
- 或作为显式脚本步骤运行 `tsc --noEmit`/`vue-tsc --noEmit`

## 打包大小优化

- 对于非关键代码路径，优先使用动态 `import()`
- 尽可能使用轻量级库
- 保持 `browserslist` 与实际兼容性要求一致

## 资产管理

- 从项目源目录导入源管理资产，而不是从 `public` 导入
- 通过绝对 URL 路径引用 `public` 文件

## 安全

- 当生产源映射启用时，不要将 `.map` 文件发布到公共服务器/CDN

## 调试

- 在诊断配置解析或插件行为时，使用 `DEBUG=rsbuild` 运行
- 通过 `dist/.rsbuild` 中生成的文件确认最终配置，而不是假设的配置

## 性能分析

- 当怀疑 JavaScript 端存在开销时，使用 Node CPU 性能分析 (`--cpu-prof`)
- 使用 `RSPACK_PROFILE=OVERVIEW` 并分析跟踪输出，以查找编译阶段的瓶颈

## 文档

- 对于最新（v2）文档，请阅读 http://rsbuild.rs/llms.txt
- 对于 Rsbuild v1 文档，请阅读 http://v1.rsbuild.rs/llms.txt
