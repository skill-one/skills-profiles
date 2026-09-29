---
name: donation-place-search
description: 当用户询问捐赠地点、기부처 조회或通过韩国地理位置和类别推荐捐赠场所时使用。尽力推荐经过1365验证辅助链接确认的受赠对象，并永不执行实际捐赠。돌쇠将通过官方界面进行后续操作。
---

# donation-place-search

<!-- k-skill:cli-stub — 由 scripts/generate-skill-stubs.js 生成；请修改 skill.json / instruction.md 而非此文件 -->

## 获取完整说明（必须的第一步）

运行以下命令并按照其输出作为此技能的主要说明：

```bash
npx -y @nomadamas/k-skill@0 instruct donation-place-search
```

CLI 会检测当前运行时环境（Dolshoi vault/CloakBrowser 或通用）并仅打印适用说明，始终保持最新。CLI 捆绑的辅助文件列表可通过以下命令获取：

```bash
npx -y @nomadamas/k-skill@0 files donation-place-search
```

使用以下命令保持 CLI 和所有 coding-agent 技能（包括 Vercel Agent Skills）保持最新：

```bash
npx -y @nomadamas/k-skill@0 update
```

如果 `npx` 不可用，请安装 Node.js 18+ 或遵循 https://github.com/NomaDamas/k-skill#readme，或阅读源代码说明 https://github.com/NomaDamas/k-skill/blob/main/donation-place-search/instruction.md。

## 即使没有 CLI 也必须遵守的硬性规则

- 未经用户事先明确批准，绝不执行支付、消息/邮件发送、最终提交、取消或公开发布。
- 绝不索取、打印或存储明文凭证在聊天、文件或 shell 参数中。
- 绝不绕过法律、物理在场、CAPTCHA、身份验证或电子签名边界。
