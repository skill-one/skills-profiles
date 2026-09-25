# 沙盒 npm 安装

## 使用此技能的场景

在以下情况使用此技能：
- 在新的沙盒会话中首次需要安装 npm 包
- `package.json` 或 `package-lock.json` 发生变化需要重新安装
- 遇到原生二进制崩溃错误，如 `SIGILL`、`SIGSEGV`、`mmap` 或 `unaligned sysNoHugePageOS`
- `node_modules` 目录缺失或损坏

## 前置条件

- 具有通过 **virtiofs** 挂载工作区的 Docker 沙盒环境
- 容器中提供 Node.js 和 npm
- 目标工作区存在 `package.json` 文件

## 背景

Docker 沙盒工作区通常通过 **virtiofs** 挂载（主机与 Linux 虚拟机之间的文件同步）。当在 aarch64 平台上从 virtiofs 执行原生 Go 和 Rust 二进制文件（如 esbuild、lightningcss、rollup 等）时，会因为 mmap 对齐失败而崩溃。解决方法是安装在容器的本地 ext4 文件系统上，并创建符号链接回工作区。

## 分步安装

从工作区根目录运行捆绑的安装脚本：

```bash
bash scripts/install.sh
```

### 常用选项

| 选项 | 描述 |
|---|---|
| `--workspace <路径>` | 包含 `package.json` 的目录路径（如果省略，将自动检测） |
| `--playwright` | 同时安装 Playwright Chromium 浏览器用于 E2E 测试 |

### 脚本执行的操作

1. 将 `package.json`、`package-lock.json` 和 `.npmrc`（如果存在）复制到本地 ext4 目录
2. 在本地文件系统上运行 `npm ci`（如果没有锁定文件则运行 `npm install`）
3. 将 `node_modules` 符号链接回工作区
4. 如果存在，验证已知原生二进制文件（esbuild、rollup、lightningcss、vite）
5. 可选地安装 Playwright 浏览器和系统依赖项（在可用时使用 `sudo`）

如果验证失败，请再次运行脚本——初始设置期间崩溃可能是间歇性的。

## 安装后验证

脚本完成后，验证您的工具链是否正常工作。例如：

```bash
npm test             # 运行项目测试
npm run build        # 构建项目
npm run dev          # 启动开发服务器
```

## 重要提示

- 本地安装目录（例如 `/home/agent/project-deps`）是 **容器本地** 的，**不会** 同步回主机
- `node_modules` 符号链接在主机上显示为断开的链接——这无危害，因为 `node_modules` 通常会被 git 忽略
- 在主机上运行 `npm ci` 或 `npm install` 会自然地用实际目录替换符号链接
- 任何 `package.json` 或 `package-lock.json` 的更改后，重新运行安装脚本
- **不要** 在挂载的工作区中直接运行 `npm ci` 或 `npm install`——原生二进制文件会崩溃

## 故障排除

| 问题 | 解决方案 |
|---|---|
| 运行开发服务器时出现 `SIGILL` 或 `SIGSEGV` | 再次运行安装脚本；确保您没有在沙盒中直接运行 `npm install` |
| 安装后未找到 `node_modules` | 检查符号链接是否存在：`ls -la node_modules` |
| 安装过程中出现权限错误 | 确保本地依赖目录对当前用户可写 |
| 验证失败且不稳定 | 再次运行脚本——原生二进制文件在首次加载时可能非确定性崩溃 |

## Vite 兼容性

如果您的项目使用 Vite，您可能需要在 `server.fs.allow` 中允许符号链接路径。将符号链接目标父目录（例如 `/home/agent/project-deps/`）添加到您的 Vite 配置中，以便 Vite 可以通过符号链接提供文件。
