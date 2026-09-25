# Netlify 部署技能

使用 Netlify CLI 将 Web 项目部署到 Netlify，智能检测项目配置和部署上下文。

## 概述

该技能通过以下方式自动化 Netlify 部署：
- 验证 Netlify CLI 身份验证
- 检测项目配置和框架
- 链接到现有站点或创建新站点
- 部署到生产环境或预览环境

## 前置条件

- **Netlify CLI**：通过 npx 安装（无需全局安装）
- **身份验证**：具有活跃登录会话的 Netlify 账户
- **项目**：当前目录中的有效 Web 项目
- 当沙盒阻止部署网络调用时，使用 `sandbox_permissions=require_escalated` 重新运行
- 部署可能需要几分钟时间。使用适当的超时值。

## 身份验证模式

该技能使用 **预认证的 Netlify CLI** 方法：

1. 使用 `npx netlify status` 检查身份验证状态
2. 如果未认证，引导用户通过 `npx netlify login`
3. 如果无法建立身份验证，则优雅地失败

身份验证使用以下方式之一：
- **基于浏览器的 OAuth**（主要）：`netlify login` 在浏览器中打开身份验证窗口
- **API 密钥**（替代）：设置 `NETLIFY_AUTH_TOKEN` 环境变量

## 工作流程

### 1. 验证 Netlify CLI 身份验证

检查用户是否登录到 Netlify：

```bash
npx netlify status
```

**预期输出模式**：
- ✅ 已认证：显示登录用户邮箱和站点链接状态
- ❌ 未认证：显示“未登录到任何站点”或身份验证错误

**如果未认证**，引导用户：

```bash
npx netlify login
```

这将在浏览器窗口中打开 OAuth 身份验证。等待用户完成登录，然后再次使用 `netlify status` 进行验证。

**替代：API 密钥身份验证**

如果浏览器身份验证不可用，用户可以设置：

```bash
export NETLIFY_AUTH_TOKEN=your_token_here
```

可以在以下位置生成密钥：https://app.netlify.com/user/applications#personal-access-tokens

### 2. 检测站点链接状态

从 `netlify status` 输出中确定：
- **已链接**：站点已连接到 Netlify（显示站点名称/URL）
- **未链接**：需要链接或创建站点

### 3. 链接到现有站点或创建新站点

**如果已链接** → 跳转到步骤 4

**如果未链接**，尝试通过 Git 远程链接：

```bash
# 检查项目是否基于 Git
git remote show origin

# 如果基于 Git，提取远程 URL
# 格式：https://github.com/username/repo 或 git@github.com:username/repo.git

# 尝试通过 Git 远程链接
npx netlify link --git-remote-url <REMOTE_URL>
```

**如果链接失败**（站点不存在于 Netlify）：

```bash
# 交互式创建新站点
npx netlify init
```

这将引导用户完成：
1. 选择团队/账户
2. 设置站点名称
3. 配置构建设置
4. 如有必要创建 netlify.toml

### 4. 验证依赖项

在部署之前，确保项目依赖项已安装：

```bash
# 对于 npm 项目
npm install

# 对于其他包管理器，检测并使用适当的命令
# yarn install, pnpm install 等
```

### 5. 部署到 Netlify

根据上下文选择部署类型：

**预览/草稿部署**（现有站点的默认值）：

```bash
npx netlify deploy
```

这将创建一个部署预览，并提供一个唯一的 URL 用于测试。

**生产部署**（新站点或显式生产部署）：

```bash
npx netlify deploy --prod
```

这将部署到实时生产 URL。

**部署过程**：
1. CLI 检测构建设置（从 netlify.toml 或提示用户）
2. 本地构建项目
3. 将构建的资产上传到 Netlify
4. 返回部署 URL

### 6. 报告结果

部署后，向用户报告：
- **部署 URL**：此部署的唯一 URL
- **站点 URL**：生产 URL（如果生产部署）
- **部署日志**：指向 Netlify 控制台的日志链接
- **下一步**：建议使用 `netlify open` 查看站点或控制台

## 处理 netlify.toml

如果存在 `netlify.toml` 文件，CLI 将自动使用它。如果没有，CLI 将提示用户输入：
- **构建命令**：例如，`npm run build`，`next build`
- **发布目录**：例如，`dist`，`build`，`.next`

常见框架默认值：
- **Next.js**：构建命令 `npm run build`，发布 `.next`
- **React (Vite)**：构建命令 `npm run build`，发布 `dist`
- **静态 HTML**：无需构建命令，发布当前目录

该技能应尽可能从 `package.json` 中检测框架并建议适当的设置。

## 示例完整工作流程

```bash
# 1. 检查身份验证
npx netlify status

# 如果未认证：
npx netlify login

# 2. 链接站点（如果需要）
# 首先尝试基于 Git 链接
git remote show origin
npx netlify link --git-remote-url https://github.com/user/repo

# 如果没有站点，创建新站点：
npx netlify init

# 3. 安装依赖项
npm install

# 4. 部署（预览用于测试）
npx netlify deploy

# 5. 部署到生产（准备好时）
npx netlify deploy --prod
```

## 错误处理

常见问题和解决方案：

**"未登录"**
→ 运行 `npx netlify login`

**"未链接到站点"**
→ 运行 `npx netlify link` 或 `npx netlify init`

**"构建失败"**
→ 检查 netlify.toml 或 CLI 提示中的构建命令和发布目录
→ 验证依赖项是否已安装
→ 查看构建日志以获取特定错误

**"发布目录未找到"**
→ 验证构建命令是否成功运行
→ 检查发布目录路径是否正确

## 故障排除

### 升级网络访问权限

如果由于网络问题（超时、DNS 错误、连接重置）部署失败，使用 `sandbox_permissions=require_escalated` 重新运行部署以获取升级权限。当沙盒网络阻止出站请求时，部署需要升级的网络访问权限。

向用户提供的示例指导：

```
部署需要升级的网络访问权限才能部署到 Netlify。我可以使用升级权限重新运行命令——要继续吗？
```

## 环境变量

用于密钥和配置：

1. 不要将密钥提交到 Git
2. 在 Netlify 控制台设置：站点设置 → 环境变量
3. 在构建中通过 `process.env.VARIABLE_NAME` 访问

## 小贴士

- 首先使用 `netlify deploy`（无 `--prod`）进行测试，然后再进行生产
- 运行 `netlify open` 在 Netlify 控制台中查看站点
- 运行 `netlify logs` 查看（如果使用 Netlify Functions）的函数日志
- 使用 `netlify dev` 进行本地开发（如果使用 Netlify Functions）

## 参考

- Netlify CLI 文档：https://docs.netlify.com/cli/get-started/
- netlify.toml 参考：https://docs.netlify.com/configure-builds/file-based-configuration/

## 嵌套参考（按需加载）

- [CLI 命令](references/cli-commands.md)
- [部署模式](references/deployment-patterns.md)
- [netlify.toml 指南](references/netlify-toml.md)
