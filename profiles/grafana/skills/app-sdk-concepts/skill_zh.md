# Grafana 应用程序 SDK 概念

grafana-app-sdk 是一个用于在 Grafana 应用程序平台构建模式化应用程序的命令行界面（CLI）+ Go 库。应用程序通过 CUE 模式（"种类"）定义资源，生成 Go + TypeScript 代码，并通过准入控制和协调器实现业务逻辑。

## 前置条件

```bash
go install github.com/grafana/grafana-app-sdk/cmd/grafana-app-sdk@latest
grafana-app-sdk version   # 验证
```

## 常见工作流程

### 搭建独立的操作员应用程序

```bash
# 1. 初始化项目（使用 Go 模块路径）
grafana-app-sdk project init github.com/example/my-app

# 2. 添加操作员模板——首先询问用户。
#    他们可能更喜欢手动编写 app.App。
grafana-app-sdk project component add operator

# 3. 验证生成的布局
ls pkg/app pkg/watchers cmd/operator
# 预期：app.go, watchers/<kind>.go, main.go
```

常见错误：忘记 `go install` 更新二进制文件——初始化前使用 `grafana-app-sdk version` 进行验证。

### 搭建 grafana/apps 风格的应用程序（在 `grafana/grafana` 内）

仅在 Grafana 仓库（或分支）内可用——初始化命令检测仓库根目录下的 `apps/` 和 `pkg/registry/apps/`。

```bash
mkdir -p apps/my-app && cd apps/my-app
grafana-app-sdk project init github.com/grafana/grafana/apps/my-app

# 仅保留：kinds/ pkg/ go.mod go.sum — 删除其他所有内容。
cp apps/example/Makefile       apps/my-app/Makefile
cp apps/example/kinds/config.cue apps/my-app/kinds/config.cue   # 覆盖
go work use ./apps/my-app
```

然后将应用程序注册到 Grafana 内（`pkg/registry/apps/apps.go` + `register.go`）。完整步骤在 [references/deployment-modes.md](references/deployment-modes.md#grafanaapps)。

### 端到端开发循环

```
1. project init               → 模块、Makefile、kinds/
2. project kind add MyKind    → CUE 种类模板
3. 编辑 kinds/*.cue           → 模式、验证、版本
4. grafana-app-sdk generate   → Go 类型、客户端、TS 类型、AppManifest、CRDs
5. 实现逻辑            → 填充协调器 / 准入控制模板
6. (可选) project component add frontend
```

每次修改 CUE 后始终重新运行 `generate`——生成的代码是协调器看到的 API。

## 部署模式（单行表格）

| 模式 | 选择时机 | 运行位置 |
|------|--------------|---------------|
| Standalone operator | 在 Grafana 仓库外，需要自己的二进制文件 | Kubernetes 操作员及其自己的 webhook 服务器 |
| grafana/apps | 在 `github.com/grafana/grafana`（或分支）内 | Grafana API 服务器内部 |
| Frontend-only | 仅 UI 应用程序，无需 Go 逻辑 | 无后端 — 仅 TS 类型 |

每种模式的初始化、运行时和连接细节在 [references/deployment-modes.md](references/deployment-modes.md)。

## 参考

- [`references/deployment-modes.md`](references/deployment-modes.md) — 每种模式的初始化、运行时语义、grafana/apps 注册步骤
- [`references/project-structure.md`](references/project-structure.md) — 独立项目布局、手动编辑与生成内容
- [`references/cli-reference.md`](references/cli-reference.md) — 每个 `grafana-app-sdk` 子命令及标志
- [`references/specific-config.md`](references/specific-config.md) — `app.Config.SpecificConfig` 模式用于功能标志驱动的应用程序配置
- [`references/local-development.md`](references/local-development.md) — Tilt + k3d 本地开发循环
- [`references/local-config.md`](references/local-config.md) — `local/config.yaml` 参考

## 资源

- [grafana-app-sdk 仓库](https://github.com/grafana/grafana-app-sdk)
- [App 平台文档](https://grafana.com/docs/grafana/latest/developers/plugins/app-platform/)
