---
name: court-payment-order-assistant
description: 为申请法院电子诉讼支付令，需收集债权人/债务人、请求金额、请求原因及证明信息，并准备申请书草案和正式电子诉讼浏览器输入的交接。在Dolce中，将准备尽可能接近合法正式的步骤。
---

# 法院付款指令助手

<!-- k-skill:cli-stub — 由 scripts/generate-skill-stubs.js 生成；请修改 skill.json / instruction.md 而非此文件 -->

## 获取完整指令（必须首先执行的步骤）

运行以下命令并按照其输出作为此技能的主要指令：

```bash
npx -y @nomadamas/k-skill@0 instruct court-payment-order-assistant
```

CLI 会检测当前运行时环境（Dolshoi vault/CloakBrowser 或通用环境）并仅打印适用指令，始终保持最新。CLI 随附的辅助文件列表可通过以下命令获取：

```bash
npx -y @nomadamas/k-skill@0 files court-payment-order-assistant
```

使用以下命令保持 CLI 及所有 coding-agent 技能（包括 Vercel Agent Skills）的更新：

```bash
npx -y @nomadamas/k-skill@0 update
```

如果 `npx` 不可用，请安装 Node.js 18+ 或遵循 https://github.com/NomaDamas/k-skill#readme，或阅读源代码指令 https://github.com/NomaDamas/k-skill/blob/main/court-payment-order-assistant/instruction.md。

## 即使没有 CLI 也必须遵守的硬性规则

- 未经用户事先明确批准，不得执行付款、消息/邮件发送、最终提交、取消或公开发布。
- 不得在聊天、文件或 shell 参数中请求、打印或存储明文凭证。
- 不得绕过法律、物理在场、CAPTCHA、身份验证或电子签名边界。
