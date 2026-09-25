# 将应用迁移至 Flows 基础设施

协调将遗留的 Dune 应用完全迁移至新的 Flows 应用托管 (`appsApi`)。按顺序处理每个区域，跳过任何已处于正确状态的区域。

## 第 1 步 — 审核当前状态

读取 `app.json`、`package.json`、`vite.config.ts`，以及（如果存在）`manifest.json`。

在做出任何更改之前，报告一份简洁的摘要：

```
迁移审核：
✗ app.json：缺少 infra 字段 → 将添加 "infra": "appsApi"
✗ 认证：使用 DuneAuthProvider → 将运行 setup-flows-auth
✗ manifest.json：缺失 → 将创建
✓ 部署脚本：已使用 @cognite/cli
```

然后继续执行第 2 步至第 5 步。

---

## 第 2 步 — 更新 `app.json`

如果 `infra` 已经是 `"appsApi"`，则跳过此步骤。否则：

**首先修复遗留部署密钥格式。** 许多 POC 应用使用 `"deployment"`（单数，普通对象）。CLI 需要 `"deployments"`（复数，数组）。如果文件具有旧格式，请重命名密钥并在继续之前将值包装在数组中：

```json
// 之前（遗留）
{
  "deployment": { "org": "...", "project": "...", ... }
}

// 之后（正确）
{
  "deployments": [{ "org": "...", "project": "...", ... }]
}
```

然后添加 `"infra": "appsApi"`：

```json
{
  "name": "My App",
  "externalId": "my-app",
  "versionTag": "0.0.1",
  "infra": "appsApi",
  "deployments": [...]
}
```

---

## 第 3 步 — 设置 Flows 认证

现在运行 `setup-flows-auth` 命令。它处理所有与认证相关的操作：包安装、Vite 插件更新、入口文件更改，以及连接到 `connectToHostApp`。

---

## 第 4 步 — 创建或更新 `manifest.json`

Flows 托管使用 `manifest.json` 来强制执行应用的 Content Security Policy。它必须存在于代码库根目录。

**如果缺失，则创建：**

```json
{
  "manifestVersion": 1,
  "permissions": {
    "network": []
  }
}
```

**通过扫描查找对外部域的出站调用来填充网络权限**：

```bash
grep -rn "fetch\|axios\|new XMLHttpRequest" src/ --include="*.ts" --include="*.tsx"
```

对于每个找到的外部 URL 组，使用 `sources`/`directives` 结构向 `network` 数组添加条目：

```json
{
  "manifestVersion": 1,
  "permissions": {
    "network": [
      {
        "sources": ["https://api.example.com", "https://maps.googleapis.com"],
        "directives": ["connect-src"]
      }
    ]
  }
}
```

规则：
- 在 `sources` 中使用完整原点（协议 + 主机名），而不仅仅是主机名。
- `"connect-src"` 涵盖 `fetch`/`XMLHttpRequest`。使用 `"img-src"` 用于图像 URL，使用 `"font-src"` 用于字体。
- CDF 集群 URL 会自动允许；无需列出它。
- 如果没有外部调用，请保留 `"network": []`。
- 标记任何需要用户手动验证的动态 URL。

---

## 第 5 步 — 更新部署脚本

在 `package.json` 中替换任何 `dune deploy` 或 `npx @cognite/dune` 命令：

```json
{
  "scripts": {
    "deploy": "npx @cognite/cli@latest apps deploy --interactive",
    "deploy-preview": "npx @cognite/cli@latest apps deploy --interactive"
  }
}
```

保持所有其他脚本（`start`、`build`、`test` 等）不变。

---

## 第 6 步 — 最终检查

```bash
grep -rn "DuneAuthProvider\|useDune\|@cognite/dune" src/ vite.config.ts 2>/dev/null
```

列出任何剩余的匹配项供用户解决。然后报告：

```
迁移完成：
✓ app.json：infra 设置为 "appsApi"，deployments 键是一个数组
✓ 认证：已应用 setup-flows-auth
✓ manifest.json：已设置网络权限
✓ 部署脚本：已更新为 @cognite/cli
```

然后明确告诉用户下一步该做什么：

```
下一步：
1. 运行 `npm run dev` 以启动开发服务器
2. 打开 Fusion 并验证应用加载且 CDF 数据正确显示
3. 满意后，使用：npx @cognite/cli@latest apps deploy --interactive
```
