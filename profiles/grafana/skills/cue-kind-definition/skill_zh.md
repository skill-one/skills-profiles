# CUE 类型定义

## 常用工作流

### 添加新类型

```bash
# 1. 生成类型文件
grafana-app-sdk project kind add MyKind --overwrite
# 生成 kinds/mykind.cue + kinds/mykind_v1alpha1.cue + 更新 kinds/manifest.cue。

# 2. 编辑生成的 .cue 文件 — 填写 schema.spec / schema.status 字段

# 3. 生成类型和客户端
grafana-app-sdk generate

# 4. 验证生成的文件是否存在
ls pkg/generated/    # 应包含 MyKind 的新类型
```

如果 `generate` 因 CUE 错误失败：
- 查看错误信息 — CUE 会显示错误文件 + 行号 + 失败的约束条件
- 常见原因：缺少必填字段、类型不匹配（例如 `string` 字段分配了 `int`）、版本文件间存在未解析的引用
- 修复 `.cue` 源文件，重新运行 `grafana-app-sdk generate`。切勿编辑 `pkg/generated/` 下的文件 — 它们每次运行都会被覆盖。

### 向现有类型添加新版本

```bash
# 1. 复制现有版本文件
cp kinds/mykind_v1alpha1.cue kinds/mykind_v1.cue

# 2. 编辑 kinds/mykind_v1.cue — 重命名顶层对象（例如 myKindv1）并调整架构

# 3. 在 kinds/manifest.cue 中注册新版本
#    添加一个 versions["v1"]: { schema: myKindv1 } 条目

# 4. 重新生成
grafana-app-sdk generate

# 5. 验证两个版本都已生成 — 每个版本的 Go 类型位于 pkg/generated/<group>/<version>/
ls pkg/generated/             # 应列出两个版本目录（例如 v1alpha1/ v1/）
# 可选地检查 definitions/ 下的 CRD 架构以确认两个版本都出现在 `spec.versions[]`
```

**重大变更**（删除字段、更改类型、添加必填字段）必须放入新版本 — 切勿就地修改稳定版本（`v1`，`v2`）。

## 类型文件结构

CLI 在 `kinds/` 下生成扁平化布局：

```
kinds/
├── manifest.cue           # 应用程序清单 + 版本列表声明
├── mykind.cue             # 通用（跨版本）类型元数据
└── mykind_v1alpha1.cue    # v1alpha1 架构 + 代码生成配置
```

对于多版本类型，额外的版本文件与主文件并列（`mykind_v1.cue` 等）。对于非常大的类型集（10+ 类型），考虑按类型分目录布局 — 完整类型结构参考在 [references/kind-layout.md](references/kind-layout.md)。

## CUE 类型结构

每个类型包含三层：

### 1. 通用类型元数据

```cue
// kinds/mykind.cue
package kinds

myKind: {
    kind: "MyKind"               // 必填：PascalCase 类型名称
    // 其他跨版本字段（scope、pluralName、validation、mutation、conversion、…）
    // 完整字段参考在 references/kind-layout.md。
}
```

### 2. 每个版本的架构

```cue
// kinds/mykind_v1alpha1.cue
package kinds

myKindv1alpha1: myKind & {
    schema: {
        spec: {                       // 期望状态 — 用户设置
            title:       string
            description: string | *""
            count:       int & >=0
            enabled:     bool | *true
        }
        status: {                     // 观察状态 — 管理员设置
            lastObservedGeneration: int | *0
            state:                  string | *""
            message:                string | *""
        }
    }
    codegen: {
        ts: { enabled: true }
        go: { enabled: true }
    }
}
```

### 3. 应用程序清单

```cue
// kinds/manifest.cue
package kinds

App: {
    appName: "my-app"
    versions: {
        "v1alpha1": { schema: myKindv1alpha1 }
    }
}
```

## 代码生成配置

控制每个类型每个版本生成的内容：

```cue
codegen: {
    ts: { enabled: true | false }   // TypeScript 类型
    go: { enabled: true | false }   // Go 类型 + 客户端
}
```

对于仅前端应用，禁用 `go` 可避免未使用的 Go 代码。对于仅后端资源，禁用 `ts` 可减小包体积。两者默认为 `true`（若未指定）。

## 参考

- [`references/kind-layout.md`](references/kind-layout.md) — 完整通用元数据字段参考 + 应用程序清单字段 + 按类型分目录布局
- [`references/schema-types.md`](references/schema-types.md) — CUE 架构字段类型（基本类型、约束、正则、枚举、映射、列表）+ `#` 前缀命名类型定义
- [`references/custom-routes.md`](references/custom-routes.md) — 类型级 + 版本级自定义路由 + 在 `app.go` 中的处理器注册

## 外部资源

- [grafana-app-sdk GitHub](https://github.com/grafana/grafana-app-sdk)
- [CUE 语言参考](https://cuelang.org/docs/)
- [示例类型布局](https://github.com/grafana/grafana/tree/main/apps/example/kinds)
