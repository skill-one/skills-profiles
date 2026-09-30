---
name: national-pension-workplace
description: 通过国民年金公团国民年金加入企业信息，利用公共数据门户API（经k-skill-proxy中转）进行查询。根据企业名称，确认参保人数、当月应缴金额以及月度获得/丧失趋势，以此分析该企业的员工规模和变化情况。
---

# 国家养老金工作场所

<!-- k-skill:cli-stub — 由 scripts/generate-skill-stubs.js 生成；请修改 skill.json / instruction.md 而不是此文件 -->

## 获取完整说明（必须的第一步）

运行以下命令并按照其输出作为此技能的主要说明：

```bash
npx -y @nomadamas/k-skill@0 instruct national-pension-workplace
```

CLI 会检测当前运行时环境（Dolshoi vault/CloakBrowser 对比通用）并仅打印适用说明，始终保持最新。CLI 捆绑的辅助文件列表可通过以下命令获取：

```bash
npx -y @nomadamas/k-skill@0 files national-pension-workplace
```

使用以下命令保持 CLI 和所有编码代理技能（包括 Vercel Agent Skills）的更新：

```bash
npx -y @nomadamas/k-skill@0 update
```

如果 `npx` 不可用，请安装 Node.js 18+ 或遵循 https://github.com/NomaDamas/k-skill#readme，或阅读源代码说明 https://github.com/NomaDamas/k-skill/blob/main/national-pension-workplace/instruction.md。

## 即使没有 CLI 也必须遵守的硬性规则

- 未经用户事先明确批准，不得执行支付、消息/邮件发送、最终提交、取消或公开发布。
- 不得在聊天、文件或 shell 参数中请求、打印或存储明文凭证。
- 不得绕过法律、物理在场、CAPTCHA、身份验证或电子签名边界。
