# pnpm

内容寻址存储、严格依赖、工作区协议、目录。

## 使用场景

- 安装/管理 npm 包
- 使用目录设置单一代码库工作区
- 覆盖传递依赖
- 修补第三方包
- pnpm 项目的 CI/CD 配置
- 加强供应链安全

## 快速入门

```bash
pnpm install                      # 安装依赖
pnpm add <pkg>                    # 添加依赖
pnpm add -D <pkg>                 # 添加开发依赖
pnpm -r run build                 # 在所有包中运行
pnpm --filter @myorg/app build    # 在特定包中运行
```

## 工作区设置

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'

# 用于集中版本管理的目录
catalog:
  react: ^18.2.0
  typescript: ~5.3.0
```

```json
// package.json - 使用工作区协议和目录
{
  "packageManager": "pnpm@10.28.2",
  "dependencies": {
    "@myorg/utils": "workspace:^",
    "react": "catalog:"
  }
}
```

## 参考文件

| 任务                             | 文件                                      |
| -------------------------------- | ----------------------------------------- |
| 命令、脚本、过滤                 | [cli.md](references/cli.md)               |
| 工作区、目录、配置               | [workspaces.md](references/workspaces.md) |
| 覆盖、修补、钩子、存储           | [features.md](references/features.md)     |
| CI/CD、Docker、迁移               | [ci.md](references/ci.md)                 |

## 文件加载

**根据您的任务考虑加载以下参考文件：**

- [ ] [references/cli.md](references/cli.md) - 如果使用 pnpm 命令、脚本或过滤
- [ ] [references/workspaces.md](references/workspaces.md) - 如果设置单一代码库、目录或工作区配置
- [ ] [references/features.md](references/features.md) - 如果使用覆盖、修补、钩子或管理存储
- [ ] [references/ci.md](references/ci.md) - 如果配置 CI/CD、Docker 或从 npm/yarn 迁移

**不要一次性加载所有文件。** 仅加载与当前任务相关的文件。

## 验证设置

配置工作区后，验证其是否正常工作：

```bash
pnpm install          # 安装所有依赖
pnpm ls --depth 0     # 验证工作区链接
pnpm -r run build     # 构建所有包
```

## 跨技能参考

- **TypeScript 库** → 使用 `ts-library` 技能用于库模式
- **构建工具** → 使用 `tsdown` 或 `vite` 技能
