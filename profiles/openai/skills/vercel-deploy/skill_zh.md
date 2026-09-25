# Vercel 部署

立即将任何项目部署到 Vercel。**始终以预览模式部署**（而不是生产模式），除非用户明确要求生产模式。

## 前置条件

- 检查 Vercel CLI 是否已安装，**无需**提升权限（例如，`command -v vercel`）。
- 只有在沙盒环境阻止部署网络调用时（`sandbox_permissions=require_escalated`），才需要提升实际部署命令的权限。
- 部署可能需要几分钟时间。使用适当的超时值。

## 快速入门

1. 检查 Vercel CLI 是否已安装（此检查无需提升权限）：

```bash
command -v vercel
```

2. 如果 `vercel` 已安装，运行此命令（设置 10 分钟超时）：
```bash
vercel deploy [路径] -y
```

**重要提示**：为部署命令使用 10 分钟（600000ms）的超时，因为构建可能需要较长时间。

3. 如果 `vercel` 未安装，或 CLI 出现 "未找到现有凭证" 的错误，请使用以下后备方法。

## 后备方法（无需认证）

如果 CLI 因认证错误失败，请使用部署脚本：

```bash
skill_dir="<技能路径>"

# 部署当前目录
bash "$skill_dir/scripts/deploy.sh"

# 部署特定项目
bash "$skill_dir/scripts/deploy.sh" /路径/到/项目

# 部署现有 tarball
bash "$skill_dir/scripts/deploy.sh" /路径/到/项目.tgz
```

脚本会处理框架检测、打包和部署。它会等待构建完成，并返回包含 `previewUrl` 和 `claimUrl` 的 JSON。

**告知用户**："您的部署已完成，请访问 [previewUrl]。在 [claimUrl] 处进行认领，以管理您的部署。"

## 生产模式部署

只有当用户明确要求时：
```bash
vercel deploy [路径] --prod -y
```

## 输出

向用户显示部署 URL。对于后备部署，还需显示认领 URL。

**不要** 使用 `curl` 或 `fetch` 获取部署 URL 以验证其是否正常工作。只需返回链接。

## 故障排除

### 提升网络访问权限

如果因网络问题（超时、DNS 错误、连接重置）导致部署失败，请使用提升权限的方式重新运行实际部署命令（使用 `sandbox_permissions=require_escalated`）。**不要**提升 `command -v vercel` 安装检查的权限。当沙盒网络环境阻止出站请求时，部署需要提升网络访问权限。

向用户提供的示例指导：

```
部署需要提升网络访问权限才能部署到 Vercel。我可以使用提升权限的方式重新运行命令——要我继续吗？
```
