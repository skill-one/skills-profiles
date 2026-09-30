---
name: pr-review
description: 请检查MiniMax Skills存储库的拉取请求。在审查PR时、验证新技能提交或检查现有技能的合规性时使用。首先运行验证脚本进行硬性检查，然后应用内容审查的质量指南。触发器：PR审查、拉取请求、验证技能、检查技能。
---

# PR 审查技能

根据仓库标准审查拉取请求（Pull Request）。该流程分为两个阶段：自动化验证，然后是手动内容审查。

## 阶段 1：自动化验证（硬性规则）

运行验证脚本以检查结构性要求：

```bash
python .claude/skills/pr-review/scripts/validate_skills.py
```

该脚本会检查：
- 每个技能目录中是否存在 `SKILL.md`
- YAML frontmatter 是否可解析
- 必需字段是否存在：`name`、`description`
- `name` 是否与目录名称匹配
- 是否未检测到硬编码的机密信息

所有 ERROR 级别的检查必须通过。WARNING 级别的项目（缺少 `license`、`metadata`）应被标记，但不构成阻断项。

完整的硬性规则规范请参阅 [references/structure-rules.md](references/structure-rules.md)。

## 阶段 2：内容审查（软性指南）

在自动化检查通过后，根据质量指南审查 PR：

1. **技能范围** — 是否与现有技能重叠？边界是否清晰？
2. **描述质量** — `description` 是否包含明确的触发条件？
3. **文件大小** — 参考文档的大小是否适中，以避免占用过多的上下文窗口？
4. **API 密钥处理** — 如果使用外部 API，凭据是否从环境变量中读取？
5. **脚本质量** — 脚本是否包含 shebang、requirements.txt 以及错误处理？
6. **语言** — SKILL.md 和代码是否使用英文编写？
7. **README 同步** — 对于新技能，是否已更新 `README.md` 和 `README_zh.md`？

软性指南的详细信息请参阅 [references/quality-guidelines.md](references/quality-guidelines.md)。

## 审查清单摘要

### 必须通过（阻断项）
- [ ] `validate_skills.py` 退出码为 0
- [ ] PR 标题遵循约定式提交（Conventional Commit）格式
- [ ] 一个 PR 对应一个目的

### 应当通过（在审查中标记）
- [ ] 与现有技能没有功能重叠
- [ ] 描述中包含触发条件
- [ ] 文件大小适中
- [ ] API 密钥通过环境变量获取
- [ ] 已为新技能更新 README 表格（Source 列设置为 `Community`）
