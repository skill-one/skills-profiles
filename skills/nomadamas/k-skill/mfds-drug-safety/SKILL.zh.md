---
name: mfds-drug-safety
description: 该技能属于访谈型药物安全核查工具：在通过 k-skill-proxy 查询食药处公共 OpenAPI 之前，必须先回询患者的症状及用药状况。
---

# mfds-drug-safety

<!-- k-skill:cli-stub — 由 scripts/generate-skill-stubs.js 生成；请修改 skill.json / instruction.md 而不是此文件 -->

## 获取完整说明（必须的第一步）

运行以下命令，并按照其输出作为此技能的主要说明：

```bash
npx -y @nomadamas/k-skill@0 instruct mfds-drug-safety
```

CLI 会检测当前运行时环境（Dolshoi vault/CloakBrowser 或通用），并仅打印适用的说明，始终保持最新。CLI 捆绑的辅助文件列表可通过以下命令获取：

```bash
npx -y @nomadamas/k-skill@0 files mfds-drug-safety
```

使用以下命令保持 CLI 和所有 coding-agent 技能（包括 Vercel Agent Skills）保持最新：

```bash
npx -y @nomadamas/k-skill@0 update
```

如果 `npx` 不可用，请安装 Node.js 18+ 或遵循 https://github.com/NomaDamas/k-skill#readme，或阅读源代码说明 https://github.com/NomaDamas/k-skill/blob/main/mfds-drug-safety/instruction.md。

## 即使没有 CLI 也必须遵守的硬性规则

- 未经用户事先明确批准，不得执行支付、消息/邮件发送、最终提交、取消或公开发布。
- 不得在聊天、文件或 shell 参数中请求、打印或存储明文凭证。
- 不得绕过法律、物理在场、CAPTCHA、身份验证或电子签名边界。
