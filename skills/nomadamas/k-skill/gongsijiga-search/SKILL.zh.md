---
name: gongsijiga-search
description: '韩国国土交通部每年公布的“个别公示地价”（元/平方米）查询。

  这是以地籍单元为单位土地的政府公示单价，是财产税、继承税、转让税等税收计算的法定标准。**不是市场价/实际成交价。**

  在用户询问 공시지가（公示地价）、개별공시지가（个别公示地价）、토지 공시단가（土地公示单价）、税务计算用土地单价，或“这块地的公示地价是多少”时使用。

  **不适用于** 시세（市场价）、실거래가（实际成交价）、매매가（买卖价）、호가（报价）、공동주택가격（共同住宅价格）（这些需要不同的数据来源）。'
---

# gongsijiga-search

<!-- k-skill:cli-stub — 由 scripts/generate-skill-stubs.js 生成；请修改 skill.json / instruction.md 而非此文件 -->

## 获取完整说明（必须的第一步）

运行以下命令并按照其输出作为此技能的主要说明：

```bash
npx -y @nomadamas/k-skill@0 instruct gongsijiga-search
```

CLI 会检测当前运行时环境（Dolshoi vault/CloakBrowser 或通用）并仅打印适用说明，始终保持最新。CLI 随附的辅助文件列表可通过以下命令获取：

```bash
npx -y @nomadamas/k-skill@0 files gongsijiga-search
```

使用以下命令保持 CLI 和所有 coding-agent 技能（包括 Vercel Agent Skills）的更新：

```bash
npx -y @nomadamas/k-skill@0 update
```

如果 `npx` 不可用，请安装 Node.js 18+ 或遵循 https://github.com/NomaDamas/k-skill#readme，或阅读源代码说明 https://github.com/NomaDamas/k-skill/blob/main/gongsijiga-search/instruction.md。

## 即使没有 CLI 也必须遵守的硬性规则

- 未经用户事先明确批准，绝不执行支付、消息/邮件发送、最终提交、取消或公开发布。
- 绝不索取、打印或存储明文凭证，包括聊天、文件或 shell 参数中。
- 绝不绕过法律、物理在场、CAPTCHA、身份验证或电子签名边界。
