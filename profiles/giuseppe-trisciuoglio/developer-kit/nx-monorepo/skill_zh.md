# Nx 单体仓库

## 概述

为 TypeScript/JavaScript 项目中的 Nx 单体仓库管理提供指导。涵盖工作区创建、项目生成、任务执行、缓存策略、模块联邦以及 CI/CD 集成。

## 何时使用

在以下情况下使用此技能：
- 创建新的 Nx 工作区或在新项目中初始化 Nx
- 使用 Nx 生成器生成应用程序、库或组件
- 运行受影响命令或跨多个项目执行任务
- 为 Nx 项目设置 CI/CD 管道（GitHub Actions、CircleCI 等）
- 使用 React 或 Next.js 配置模块联邦
- 在 Nx 中实现 NestJS 后端应用程序
- 管理 TypeScript 包库（可构建和可发布的库）
- 设置远程缓存或 Nx Cloud
- 优化单体仓库构建时间和缓存策略
- 调试依赖关系图问题或循环依赖

**触发短语：** "create Nx workspace"、"Nx monorepo"、"generate Nx app"、"Nx affected"、"Nx CI/CD"、"Module Federation Nx"、"Nx Cloud"

## 说明

### 工作区创建

1. **使用交互式设置创建新工作区：**
   ```bash
   npx create-nx-workspace@latest
   ```
   按提示选择预设（Integrated、Standalone、Package-based）和框架堆栈。

2. **在新项目中初始化 Nx：**
   ```bash
   nx@latest init
   ```

3. **使用特定预设创建（非交互式）：**
   ```bash
   npx create-nx-workspace@latest my-workspace --preset=react
   ```
   **验证：** `nx show projects` 列出新的工作区项目

### 项目生成

1. **生成 React 应用程序：**
   ```bash
   nx g @nx/react:app my-app
   ```

2. **生成库：**
   ```bash
   # React 库
   nx g @nx/react:lib my-lib

   # TypeScript 库
   nx g @nx/js:lib my-util
   ```
   **验证：** `nx show projects` 列出新的库

3. **在库中生成组件：**
   ```bash
   nx g @nx/react:component my-comp --project=my-lib
   ```

4. **生成 NestJS 后端：**
   ```bash
   nx g @nx/nest:app my-api
   ```
   **验证：** `nx show projects` 列出 `my-api`，且 `nx run my-api:build` 成功

### 任务执行

1. **仅针对受影响项目运行任务：**
   ```bash
   nx affected -t lint test build
   ```

2. **跨所有项目运行任务：**
   ```bash
   # 构建所有项目
   nx run-many -t build

   # 测试特定项目
   nx run-many -t test -p=my-app,my-lib

   # 按模式测试
   nx run-many -t test --projects=*-app
   ```

3. **在单个项目上运行特定目标：**
   ```bash
   nx run my-app:build
   ```

4. **可视化依赖关系图：**
   ```bash
   nx graph
   ```

### 项目配置

每个项目都有一个 `project.json`，定义目标、执行器和配置：

```json
{
  "name": "my-app",
  "projectType": "application",
  "sourceRoot": "apps/my-app/src",
  "targets": {
    "build": {
      "executor": "@nx/react:webpack",
      "outputs": ["{workspaceRoot}/dist/apps/my-app"],
      "configurations": {
        "production": {
          "optimization": true
        }
      }
    },
    "test": {
      "executor": "@nx/vite:test"
    }
  },
  "tags": ["type:app", "scope:frontend"]
}
```

### 依赖管理

1. **设置项目依赖：**
   ```json
   {
     "targets": {
       "build": {
         "dependsOn": [
           { "projects": ["shared-ui"], "target": "build" }
         ]
       }
     }
   }
   ```

2. **使用标签进行组织：**
   ```json
   { "tags": ["type:ui", "scope:frontend", "platform:web"] }
   ```

### 模块联邦（Nx 17+）

1. **生成远程（微前端）：**
   ```bash
   nx g @nx/react:remote checkout --host=dashboard
   ```

2. **生成主机：**
   ```bash
   nx g @nx/react:host dashboard
   ```

### CI/CD 设置

在 CI 中使用受影响命令，仅构建/测试已更改的项目：

```yaml
# .github/workflows/ci.yml
- run: npx nx affected -t lint --parallel
- run: npx nx affected -t test --parallel
- run: npx nx affected -t build --parallel
```

## 示例

### 示例 1：创建新的 React 工作区

**输入：** "Create a new Nx workspace with React and TypeScript"

**步骤：**
```bash
npx create-nx-workspace@latest my-workspace
# 选择：Integrated Monorepo → React → Integrated monorepo (Nx Cloud)
```
**验证：** `cd my-workspace && nx show projects` 列出创建的应用

**预期结果：** 工作区创建，包含：
- `apps/` 目录，包含 React 应用
- `libs/` 目录，用于共享库
- `nx.json`，包含缓存配置
- CI/CD 工作流文件已准备就绪

### 示例 2：仅针对已更改项目运行测试

**输入：** "Run tests only for projects affected by recent changes"

**命令：**
```bash
nx affected -t test --base=main~1 --head=main
```

**预期结果：** 仅执行受提交更改影响的项目测试，利用先前运行的缓存结果。

### 示例 3：生成并构建共享库

**输入：** "Create a shared UI library and use it in the app"

**步骤：**
```bash
# 生成库
nx g @nx/react:lib shared-ui

# 在库中生成组件
nx g @nx/react:component button --project=shared-ui

# 在应用中导入（tsconfig paths 自动配置）
import { Button } from '@my-workspace/shared-ui'
```
**验证：** `nx run shared-ui:build` 成功完成，且 `nx graph` 显示对应用的项目依赖关系

**预期结果：** 可构建的库位于 `libs/shared-ui`，并配置了正确的 TypeScript 路径映射。

### 示例 4：设置模块联邦

**输入：** "Configure Module Federation for micro-frontends"

**步骤：**
```bash
# 创建主机应用
nx g @nx/react:host dashboard

# 向主机添加远程
nx g @nx/react:remote product-catalog --host=dashboard

# 启动开发服务器
nx run dashboard:serve
nx run product-catalog:serve
```
**验证：** 两个服务器均无错误启动，且 `nx graph` 显示 dashboard → product-catalog 远程连接

**预期结果：** 两个独立应用程序运行，其中 product-catalog 在运行时动态加载到 dashboard 中。

### 示例 5：调试构建依赖

**输入：** "Why is my app rebuilding when unrelated lib changes?"

**诊断：**
```bash
# 显示项目图
nx graph --focused=my-app

# 检查隐式依赖
nx show project my-app --json | grep implicitDependencies
```

**解决方案：** 添加显式依赖配置，或在 `nx.json` 中使用 `namedInputs` 排除某些文件以防止触发构建。

**验证修复是否有效：** 对无关库进行更改，运行 `nx affected -t build` — `my-app` 不应出现在受影响项目列表中。

## 最佳实践

- **始终在 CI 中使用 `nx affected`** 仅测试/构建已更改的项目
- **按业务能力而非技术层级组织库**（例如：`shared-ui`、`core-api`）
- **一致使用标签**（`type:app|lib`、`scope:frontend|backend|shared`）
- **通过在 `nx.json` 中配置 `workspaceLayout` 边界** 防止循环依赖
- **使用 Nx Cloud 启用远程缓存** 提高团队效率
- **保持 `project.json` 简洁** — 尽可能使用 `nx.json` 的默认值
- **使用生成器代替手动文件创建** 以保持一致性
- **配置 `namedInputs`** 将测试文件排除在生产缓存键之外
- **使用模块联邦** 独立部署微前端
- **将项目特定生成器** 放在 `tools/` 用于项目特定脚手架

## 限制和警告

- **需要 Node.js 18.10+** 才能使用 Nx 17+
- **Windows 用户**：使用 WSL 或 Git Bash 以获得最佳体验
- **首次设置** 可能因包安装而耗时较长
- **大型单体仓库**（50+ 项目）应使用分布式任务执行
- **模块联邦** 需要 webpack 5+ 和特定的 Nx 配置
- **某些生成器** 需要先安装额外的插件
- **缓存位置**：默认 `~/.nx/cache` 可能会变得很大；如有需要，在 `nx.json` 中配置 `cacheDirectory`
- **循环依赖** 将导致构建失败；使用 `nx graph` 可视化
- **预设迁移**：在 Integrated/Standalone/Package-based 之间转换需要手动操作

## 参考文件

有关特定主题的详细指导，请参阅：

| 主题 | 参考文件 |
|-------|----------------|
| 工作区设置、基本命令 | [references/basics.md](references/basics.md) |
| 生成器（应用、库、组件） | [references/generators.md](references/generators.md) |
| React、Next.js、Expo 模式 | [references/react.md](references/react.md) |
| NestJS 后端模式 | [references/nestjs.md](references/nestjs.md) |
| TypeScript 包 | [references/typescript.md](references/typescript.md) |
| CI/CD（GitHub、CircleCI 等） | [references/ci-cd.md](references/ci-cd.md) |
| 缓存、affected、高级 | [references/advanced.md](references/advanced.md) |
