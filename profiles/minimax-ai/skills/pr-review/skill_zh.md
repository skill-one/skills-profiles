# PR 审核技能

对照仓库标准审核拉取请求。两阶段流程：自动验证，然后人工内容审核。

## 第一阶段：自动验证（硬性规则）

运行验证脚本检查结构要求：

```bash
python .claude/skills/pr-review/scripts/validate_skills.py
```

脚本检查：

- 每个技能目录中存在 `SKILL.md`
- YAML 前置内容可解析
- 必填字段：`name`、`description`
- `name` 与目录名匹配
- 未检测到硬编码的密钥

所有 ERROR 级别的检查必须通过。WARNING 级别的项目（缺少 `license`、`metadata`）应被标记但不是阻碍项。

参考 [references/structure-rules.md](references/structure-rules.md) 了解完整的硬性规则规范。

## 第二阶段：内容审核（软性指南）

自动检查通过后，根据质量指南审核 PR：

1. **技能范围** — 是否与现有技能重叠？边界是否清晰？
2. **描述质量** — `description` 是否包含清晰的触发条件？
3. **文件大小** — 参考文档是否合理大小以供上下文窗口使用？
4. **API 密钥处理** — 如果使用外部 API，凭证是否从环境变量读取？
5. **脚本质量** — 脚本是否包含 shebang、requirements.txt 和错误处理？
6. **语言** — `SKILL.md` 和代码是否使用英文编写？
7. **README 同步** — `README.md` 和 `README_zh.md` 是否更新以反映新技能？

参考 [references/quality-guidelines.md](references/quality-guidelines.md) 了解软性指南详情。

## 审核清单摘要

### 必须通过（阻碍项）
- [ ] `validate_skills.py` 退出码为 0
- [ ] PR 标题遵循常规提交格式
- [ ] 一个 PR 一个目的

### 应通过（审核中标记）
- [ ] 无功能重叠于现有技能
- [ ] 描述包含触发条件
- [ ] 文件大小合理
- [ ] API 密钥通过环境变量
- [ ] README 表格更新以反映新技能（源列设置为 `Community`）
