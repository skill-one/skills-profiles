---
name: court-auction-notice-search
description: 浏览大法院拍卖信息(courtauction.go.kr)的房地产拍卖公告，按拍卖日期、法院、日期/期间竞标，将每个公告展开为案件编号·用途·地址·评估金额·最低拍卖价，通过免费条件（地区·用途·价格·面积·异议次数）搜索房产项目，并可直接按法院+案件编号查询案件。仅读，设计上较慢（每调用约2秒），以避免IP封锁。돌쇠将尽可能准备最接近的合法正式步骤。
---

# 法院拍卖公告搜索

<!-- k-skill:cli-stub — 由 scripts/generate-skill-stubs.js 生成；请修改 skill.json / instruction.md 而非此文件 -->

## 获取完整说明（必须首先执行的步骤）

运行以下命令并按照其输出作为此技能的主要说明：

```bash
npx -y @nomadamas/k-skill@0 instruct court-auction-notice-search
```

CLI 会检测当前运行时环境（Dolshoi vault/CloakBrowser 或通用）并仅打印适用说明，始终保持最新。CLI 随附的辅助文件列表如下：

```bash
npx -y @nomadamas/k-skill@0 files court-auction-notice-search
```

使用以下命令保持 CLI 和所有 coding-agent 技能（包括 Vercel Agent Skills）保持最新：

```bash
npx -y @nomadamas/k-skill@0 update
```

如果 `npx` 不可用，请安装 Node.js 18+ 或遵循 https://github.com/NomaDamas/k-skill#readme，或阅读源代码说明 https://github.com/NomaDamas/k-skill/blob/main/court-auction-notice-search/instruction.md。

## 即使没有 CLI 也必须遵守的硬性规则

- 未经用户事先明确批准，不得执行支付、消息/邮件发送、最终提交、取消或公开发布。
- 不得索取、打印或存储明文凭证在聊天、文件或 shell 参数中。
- 不得绕过法律、物理在场、CAPTCHA、身份验证或电子签名边界。
