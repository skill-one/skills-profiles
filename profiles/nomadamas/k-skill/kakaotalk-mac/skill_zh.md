# kakaotalk-mac

<!-- k-skill:cli-stub — 由 scripts/generate-skill-stubs.js 生成；请修改 skill.json / instruction.md 而非此文件 -->

## 获取完整说明（必须首先执行的步骤）

运行以下命令并按照其输出作为此技能的主要说明：

```bash
npx -y @nomadamas/k-skill@0 instruct kakaotalk-mac
```

CLI 会检测当前运行时环境（Dolshoi vault/CloakBrowser 或通用）并仅打印适用说明，始终保持最新。CLI 随附的辅助文件列表如下：

```bash
npx -y @nomadamas/k-skill@0 files kakaotalk-mac
```

使用以下命令保持 CLI 和所有 coding-agent 技能（包括 Vercel Agent Skills）的当前状态：

```bash
npx -y @nomadamas/k-skill@0 update
```

如果 `npx` 不可用，请安装 Node.js 18+ 或遵循 https://github.com/NomaDamas/k-skill#readme，或阅读源代码说明 https://github.com/NomaDamas/k-skill/blob/main/kakaotalk-mac/instruction.md。

## 法律免责声明（必须）

此技能并非其识别的任何第三方商标所有者或服务运营商的官方功能、官方支持、关联、赞助、批准或合作开发。仅使用第三方名称来描述技能的功能、查找目标或兼容性。

任何公开可访问信息的自动化收集必须限制在个人、非组织性查找范围内。不要使用此技能进行系统性或批量爬取、数据库构建、访问控制或绕过阻止，或进行干扰第三方业务或服务的活动。

在使用前，请阅读完整的韩国法律免责声明，包括引用的韩国最高法院先例和法定限制：

```bash
npx -y @nomadamas/k-skill@0 read kakaotalk-mac references/DISCLAIMER.md
```

## 即使没有 CLI 也必须遵守的硬性规则

- 未经用户事先立即明确批准，切勿执行支付、消息/邮件发送、最终提交、取消或公开发布。
- 切勿在聊天、文件或 shell 参数中请求、打印或存储明文凭证。
- 切勿绕过法律、物理在场、验证码、身份验证或电子签名边界。
