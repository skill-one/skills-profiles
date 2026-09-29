---
name: korean-humanizer
description: AI生成的带有明显痕迹的韩语文本，将其改写成自然流畅的人类风格文本。针对翻译腔、AI套话、过度名词化·被动语态、三的法则、过度赋予意义、结尾套话、聊天机器人残留痕迹、以及类似断行标点·曲线引号等韩语特有的AI痕迹，按严重程度（S1/S2/S3）进行分类并修正，同时保留原意进行重写。若提供目标字数（例如："1000字"，length=1000），将根据该字数调整文本长度。适用于"消除AI痕迹"、"写得像人类写的"、"自然润色"、"修正翻译腔"、"修正别扭之处"、"调整为N字"等请求。
---

# korean-humanizer

<!-- k-skill:cli-stub — 由 scripts/generate-skill-stubs.js 生成；请修改 skill.json / instruction.md 而非此文件 -->

## 获取完整说明（必须的第一步）

运行以下命令并按照其输出作为此技能的主要说明：

```bash
npx -y @nomadamas/k-skill@0 instruct korean-humanizer
```

CLI 会检测当前运行时环境（Dolshoi vault/CloakBrowser 或通用）并仅打印适用说明，始终保持最新。CLI 随附的辅助文件列表可通过以下命令获取：

```bash
npx -y @nomadamas/k-skill@0 files korean-humanizer
```

使用以下命令保持 CLI 和所有 coding-agent 技能（包括 Vercel Agent Skills）保持最新：

```bash
npx -y @nomadamas/k-skill@0 update
```

如果 `npx` 不可用，请安装 Node.js 18+ 或遵循 https://github.com/NomaDamas/k-skill#readme，或阅读源代码说明 https://github.com/NomaDamas/k-skill/blob/main/korean-humanizer/instruction.md。

## 即使没有 CLI 也必须遵守的硬性规则

- 未经用户事先明确批准，绝不执行支付、消息/邮件发送、最终提交、取消或公开发布。
- 绝不索取、打印或存储明文凭证在聊天、文件或 shell 参数中。
- 绝不绕过法律、物理在场、CAPTCHA、身份验证或电子签名边界。
