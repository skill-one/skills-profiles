# 链接工作区包

在单体仓库中添加包之间的依赖关系。所有包管理器都支持工作区，但语法不同。

## 检测包管理器

检查根级别的 `package.json` 中是否存在 `packageManager` 字段。

或者检查仓库根目录中的锁文件：

- `pnpm-lock.yaml` → pnpm
- `yarn.lock` → yarn
- `bun.lock` / `bun.lockb` → bun
- `package-lock.json` → npm

## 工作流

1. 识别消费者包（导入的包）
2. 识别提供者包（被导入的包）
3. 使用包管理器的工作区语法添加依赖
4. 验证消费者 `node_modules/` 中创建的符号链接

---

## pnpm

使用 `workspace:` 协议 - 只有在明确声明时才会创建符号链接。

```bash
# 从消费者目录
pnpm add @org/ui --workspace

# 或者使用 --filter 从任何地方
pnpm add @org/ui --filter @org/app --workspace
```

`package.json` 中的结果：

```json
{ "dependencies": { "@org/ui": "workspace:*" } }
```

---

## yarn (v2+/berry)

也使用 `workspace:` 协议。

```bash
yarn workspace @org/app add @org/ui
```

`package.json` 中的结果：

```json
{ "dependencies": { "@org/ui": "workspace:^" } }
```

---

## npm

没有 `workspace:` 协议。npm 自动符号链接工作区包。

```bash
npm install @org/ui --workspace @org/app
```

`package.json` 中的结果：

```json
{ "dependencies": { "@org/ui": "*" } }
```

npm 在安装过程中自动解析本地工作区。

---

## bun

支持 `workspace:` 协议（与 pnpm 兼容）。

```bash
cd packages/app && bun add @org/ui
```

`package.json` 中的结果：

```json
{ "dependencies": { "@org/ui": "workspace:*" } }
```

---

## 示例

**示例 1：pnpm - 将 ui 库链接到 app**

```bash
pnpm add @org/ui --filter @org/app --workspace
```

**示例 2：npm - 链接多个包**

```bash
npm install @org/data-access @org/ui --workspace @org/dashboard
```

**示例 3：调试 "Cannot find module"**

1. 检查依赖是否在消费者的 `package.json` 中声明
2. 如果没有，使用上述适当命令添加它
3. 运行安装 (`pnpm install`, `npm install` 等)

## 注意事项

- 符号链接出现在 `<消费者>/node_modules/@org/<包>`
- **提升行为因管理器而异：**
  - npm/bun：将共享依赖提升到根 `node_modules`
  - pnpm：不提升（严格隔离，防止幽灵依赖）
  - yarn berry：默认使用 Plug'n'Play（没有 `node_modules`）
- 根 `package.json` 应该有 `"private": true` 以防止意外发布
