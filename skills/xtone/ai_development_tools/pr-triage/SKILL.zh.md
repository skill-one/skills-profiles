---
name: pr-triage
description: 对PR的变更内容进行分诊，进行变更类别分类、表层检查、必要参考判定。将结果输出到`.pr-triage.json`文件中，并在后续的代码审查阶段中使用。请用于CI环境中的成本优化。
---

# PR三级分类

PR变更内容分析，并结构化输出后续代码评审阶段所需信息的技能。
基于轻量模型（Haiku）执行，旨在优化CI环境下的成本。

## 步骤

1. 使用 `gh pr view <PR编号> --json title,body,headRefName,baseRefName,changedFiles` 获取PR信息
2. 使用 `gh pr diff <PR编号> --name-only` 获取变更文件列表
3. 差分获取（**当 `changedFiles` 超过15个时，跳过步骤3，仅通过文件名和PR说明进行分析**）：
   - 仅当 `changedFiles` 不足15个时，使用 `gh pr diff <PR编号>` 获取代码差异
   - 若表层检查所需的文件（.ts, .js, .tsx, .jsx）较多，则分别使用 `gh pr diff <PR编号> -- <文件>` 获取
4. 检查是否存在 `.pr-review-state.json`（上次评审状态）
5. 执行以下分析：
   - 变更文件的分类（added/modified/deleted）
   - 检测使用的语言和框架
   - 判定变更类别（批准变更、DB变更、RLS变更、API变更、测试变更、配置变更、技能变更）
   - 判定必要的参考文件
   - 检测Minor/Suggestion级别的表层问题（增量模式下仅检查变更文件）
   - 差分摘要（200字以内）
   - 评审时需关注的要点
6. 将分析结果输出到 `.pr-triage.json` 文件

## 增量模式（存在 `.pr-review-state.json` 时）

利用上次评审状态优化检查范围：

1. 获取 `.pr-review-state.json` 的 `last_reviewed_commit`
2. 使用 `git diff <last_reviewed_commit>..HEAD --name-only` 确定上次评审后变更的文件
3. **未变更的文件**的 `surface_issues` 直接继承上次状态（添加 `"carried_over": true"`），无需重新检查
4. 仅对**已变更的文件**执行表层检查
5. 将上次 `surface_issues` 和 `review_comments` 中已修正的部分加入 `resolved_issues`
6. 在输出 `.pr-triage.json` 中添加 `"incremental": true`、`"base_commit"`、`"changed_since_last_review"`、`"unchanged_since_last_review"`、`"resolved_issues"` 字段

`resolved_issues` 的格式：
```json
{
  "comment_id": 12345678,
  "file": "<文件路径>",
  "line": 42,
  "issue": "<原问题说明>",
  "resolution": "fixed"
}
```

> 若不存在 `.pr-review-state.json`，则执行完整三级分类。
> 若 `.pr-review-state.json` 格式不正确（如JSON解析错误），则输出警告并执行完整三级分类。不得基于损坏的状态文件执行增量模式。

## 必要参考文件判定标准

仅当符合以下条件时，将对应参考文件加入 `required_references`：
- TypeScript/JavaScript 文件变更 → `typescript-best-practices.md`
- 存在认证/授权相关代码变更（auth, permission, role, session, token等关键词）→ `authorization-review-general.md`
- 存在PostgreSQL RLS相关变更（RLS, row level security, policy等关键词）→ `authorization-review-postgres-rls.md`
- `SKILL.md` 文件变更 → `skill-review.md`
- 需要在CI环境提交GitHub PR → `github-pr-review-actions.md`（始终包含）

## 表层检查项（Minor/Suggestion）

检查差异并检测以下问题（仅限适用项）：
- TypeScript中的`any`类型使用
- TypeScript/JavaScript中的`var`关键字使用
- 空的接口定义
- 魔术数字使用
- 命名规则违规（camelCase/PascalCase/UPPER_CASE）
- 未添加测试（存在新文件但缺少测试文件）

## 输出格式

将以下JSON结构输出到 `.pr-triage.json`：

```json
{
  "pr_number": 123,
  "incremental": false,
  "base_commit": "<上次评审时的提交SHA（增量模式仅）>",
  "summary": "<变更概要（1-2句）>",
  "files": {
    "added": ["<追加文件路径>"],
    "modified": ["<变更文件路径>"],
    "deleted": ["<删除文件路径>"]
  },
  "changed_since_last_review": ["<上次变更的文件（增量模式仅）>"],
  "unchanged_since_last_review": ["<上次未变更的文件（增量模式仅）>"],
  "languages": ["<检测到的语言>"],
  "frameworks": ["<检测到的框架>"],
  "change_categories": {
    "has_auth_changes": false,
    "has_db_changes": false,
    "has_rls_changes": false,
    "has_api_changes": false,
    "has_test_changes": false,
    "has_config_changes": true,
    "has_skill_changes": true
  },
  "required_references": ["<必要参考文件名>"],
  "surface_issues": [
    {
      "severity": "Minor|Suggestion",
      "file": "<文件路径>",
      "line": 15,
      "issue": "<问题说明>",
      "suggestion": "<改进建议>",
      "carried_over": true
    }
  ],
  "resolved_issues": [
    {
      "comment_id": 12345678,
      "file": "<文件路径>",
      "line": 42,
      "issue": "<原问题说明>",
      "resolution": "fixed"
    }
  ],
  "diff_summary": "<差异摘要（200字以内）>",
  "estimated_complexity": "low|medium|high",
  "focus_areas": ["<评审时关注点>"]
}
```

重要：
- 文本输出应最小化，集中输出 `.pr-triage.json`。
