# 创建和开发 Paperclip 插件

在需要创建、搭建或迭代本地 Paperclip 实例上的 Paperclip 插件的任务中使用此技能。

## 1. 默认：在 Paperclip 核心外部构建插件

插件是其自身的包。除非任务**明确**要求提供一个存放在仓库内的示例，否则不要将插件源代码添加到此仓库的 `packages/plugins/` 目录下。

- 将插件搭建到 Paperclip 检出（checkout）目录外部的目录（例如 `~/dev/paperclip-plugins/<name>`）。
- 通过本地绝对路径将其安装到正在运行的 Paperclip 实例中。
- 在外部包中编辑代码；让 Paperclip 拾取重新构建的输出。

仅在用户要求将插件作为捆绑示例展示时才编辑 Paperclip 核心（`server/src/routes/plugins.ts`、仓库内示例列表、文档）。

## 2. 基本规则

需要详细信息时参考文档：

1. `doc/plugins/PLUGIN_AUTHORING_GUIDE.md`
2. `packages/plugins/sdk/README.md`
3. `doc/plugins/PLUGIN_SPEC.md` — 仅用于未来展望的上下文

当前的运行时假设：

- 插件工作进程是受信任的代码
- 插件 UI 是受信任的同源主机代码
- 工作进程 API 是按能力分组的
- 插件 UI 没有通过清单（manifest）能力进行沙盒化
- 尚未提供主机提供的共享插件 UI 组件工具包
- `ctx.assets` 在当前运行时不受支持

## 3. 以 CLI 优先的搭建工作流程

使用 `paperclipai plugin init`。除非环境中没有 CLI 命令，否则不要手动调用搭建包的 node 入口点。

```bash
paperclipai plugin init @acme/my-plugin --output ~/dev/paperclip-plugins
```

有用的标志（全部可选）：

- `--output <dir>` — 父目录；命令会创建 `<dir>/<unscoped-name>/`。默认为当前目录。
- `--template <default|connector|workspace|environment>` — 启动模板。
- `--category <connector|workspace|automation|ui|environment>` — 清单（manifest）类别。
- `--display-name <name>`, `--description <text>`, `--author <name>` — 清单（manifest）元数据。
- `--sdk-path <path>` — 将本地 SDK 从 Paperclip 检出（checkout）快照到 `.paperclip-sdk/`（在开发未发布的 SDK 时很有用）。

成功后，命令会打印确切的下一步命令（`cd`、`pnpm install`、`pnpm dev`、`paperclipai plugin install <abs-path>`）。按顺序运行它们。

如果 `paperclipai` 在您的环境中不在 PATH 中，则回退到：

```bash
pnpm --filter @paperclipai/create-paperclip-plugin build
node packages/plugins/create-paperclip-plugin/dist/index.js @acme/my-plugin \
  --output /absolute/path \
  --sdk-path /absolute/path/to/paperclip/packages/plugins/sdk
```

## 4. 本地安装 + 重新构建循环

在搭建的插件文件夹中：

```bash
pnpm install
pnpm dev            # esbuild --watch: 重新构建 dist/manifest.js, dist/worker.js, dist/ui/
paperclipai plugin install /absolute/path/to/my-plugin
```

注意：

- `paperclipai plugin install` 自动检测本地路径（绝对路径、`./`、`../`、`~` 或现有的相对文件夹），并将 `isLocalPath: true` 转发给服务器。如果启发式算法（heuristic）不明确，请传递 `--local` 以强制本地模式。
- 路径在发送到服务器之前会被解析为绝对路径。
- 服务器会监视本地路径插件的构建输出（`dist/`），并在重新构建时重启插件工作进程 — 你不需要在每次编辑后重新安装。
- 通过 SDK 开发服务器（`pnpm dev:ui`，端口 `4177`）的 UI 热重载是可选的，并且取决于模板；如果模板配置了 `devUiUrl` 并且您验证了端到端工作，才提及它。
- `--version` 仅适用于 npm 包安装。将其与本地路径结合使用是错误的。

安装后，使用以下命令检查：

```bash
paperclipai plugin list
paperclipai plugin inspect <plugin-key>
```

## 5. 搭建后，检查包的合理性

打开并确认：

- `src/manifest.ts` — 声明的能力和插槽
- `src/worker.ts` — 工作进程入口
- `src/ui/index.tsx` — UI 入口（如果适用）
- `tests/plugin.spec.ts` — 占位符测试
- `package.json` — `paperclipPlugin` 块指向 `dist/manifest.js`、`dist/worker.js`、`dist/ui/`

确保插件：

- 仅声明受支持的能力
- 不使用 `ctx.assets`
- 不导入主机 UI 组件占位符
- 保持 UI 自包含
- 仅在 `page` 插槽上使用 `routePath`

## 6. 验证（成功声明前运行）

从插件文件夹运行：

```bash
pnpm typecheck
pnpm test
pnpm build
```

如果插件已经在 `pnpm dev` 下运行，你可以保持监视器开启，并在单独的 shell 中运行 `pnpm typecheck` 和 `pnpm test`。

如果你除了插件还修改了 Paperclip SDK/主机/插件运行时代码，也运行相关的 Paperclip 工作空间检查。

## 7. 成功检查清单（需报告）

完成本地插件任务后，报告：

- **搭建路径** — 创建的插件文件夹的绝对路径。
- **运行的命令** — 确切的 `paperclipai plugin init`、`pnpm install`、`pnpm dev`、`paperclipai plugin install <path>` 调用（以及任何验证命令）。
- **安装状态** — `paperclipai plugin list` / `plugin inspect` 的输出（插件 key、版本、状态）。注意如果 `status` 不是 `ready`，请包含 `lastError`。
- **测试 / 构建结果** — `pnpm typecheck`、`pnpm test`、`pnpm build` 通过/失败，如果有失败输出请包含。
- **重新加载限制** — 指出任何未热重载的内容（例如，清单变更需要重新安装、UI 开发服务器未配置等）。

如果任何项缺失，请标记为缺失 — 不要静默跳过。

## 8. 不应编辑 Paperclip 核心的情况

除非用户明确要求提供捆绑示例，否则不要在 `packages/plugins/` 下添加插件或更新捆绑示例的连接。本地路径安装是受支持的开发模型；npm 包是生产部署路径。

如果用户确实要求提供捆绑示例，还请更新：

- `server/src/routes/plugins.ts` 示例列表
- 任何枚举仓库内示例插件的文档

## 9. 文档预期

在编写或更新插件文档时：

- 区分当前实现与未来规范的构想
- 明确说明受信任代码模型
- 不要承诺主机 UI 组件或资产 API
- 优先提供本地路径开发 + npm 包部署的指导，而不是仓库本地工作流程
