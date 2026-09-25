# diff-intake

请按以下步骤逐步操作。
你处于分析工具化工作流的步骤1。生成一份紧凑的YAML变更简报，下游技能（discover-event-surfaces、instrument-events）将使用它。保持输出机器可读且精确——YAML块周围不要有散文。

## 步骤1：收集变更文件并分类

从源代码中获取变更文件列表，然后对每个文件进行分类。

### 获取变更
- **PR链接**
`gh pr view <number-or-url>`
`gh pr view <pr-number> --json files --jq '.files[] | "\(.path)\t+\(.additions) -\(.deletions)\t"'`
- **分支比较**
`git log <main|master>..<branch>`
`git diff --stat <main|master>..<branch>`
- **模糊提及**（PR编号、分支名称）：推断正确的形式并获取，无需询问，除非认证失败。

### 分类文件
根据文件路径将每个文件分配到类别：
- **核心逻辑**：应用程序源代码（例如 src/auth/login.py、database/models.ts）
- **生成**：路径中包含`generated`的任何文件
- **测试**：测试文件
- **配置 / 依赖项**：package.json、docker-compose.yml等
- **文档**：READMEs、docs/
- **噪音**：lock-files、.svg、自动生成的迁移文件

对于每个文件，记录：路径、类别、变更类型（添加 / 修改 / 删除）和分析可能性（1–5）。

## 步骤2：构建文件摘要映射
读取每个**核心逻辑**文件并创建文件摘要映射。
仅处理并包含**核心逻辑**文件。

### 获取详细差异
- **PR**
`gh pr view <number-or-url> --json baseRefOid,headRefOid`
使用响应获取详细差异
`git diff <baseRefOid>...<headRefOid> -- <file1> <file2> <file_n>`
- **分支比较**
`git diff main..feature/foo  -- <file1> <file2> <file_n>`

### 对于每个文件，记录
- `summary` — 变更的2行摘要
- `stack` — 前端、后端或共享

### 还需推导用户界面变更和受影响的表面

在读取差异和变更文件时，还生成下游事件发现所需的高级信号：

- `user_facing_changes` — 一个扁平列表，包含对用户、产品经理或分析师重要的具体行为变更。每个项目应描述用户现在可以做什么、看到什么或体验到的不同。忽略纯粹内部的重构。
- `surfaces.components` — 直接涉及这些用户界面变更的UI组件、路由、页面、处理程序或其他交互表面。优先考虑可能的工具化点，而不是低级辅助工具。

对于每个表面，记录：
- `name` — 组件、路由、页面、钩子或表面名称
- `file` — 仓库相对路径
- `change` — `added`、`modified`或`deleted`

如果变更仅限于后端或没有明确的交互表面，则省略`surfaces.components`，而不是编造一个。

## 步骤3：分类整体变更

推断变更类型和分析范围：

| 类型                                     | 分析影响                             |
| ---------------------------------------- | ------------------------------------------------- |
| feat                                     | 高 — 可能需要跟踪新表面              |
| fix                                      | 低–中 — 可能会影响现有事件条件         |
| refactor                                 | 低 — 跟踪路径可能移动，回归风险       |
| perf                                     | 低 — 通常没有跟踪影响                  |
| revert                                   | 中 — 需要检查丢失了什么跟踪           |
| style / docs / test / build / ci / chore | 无 — 跳过分析分析                    |

`analytics_scope` = 最高影响：
- `none` — 仅无影响类型
- `low` — 仅perf/refactor
- `medium` — fix
- `high` — 任何功能或能力添加

如果`analytics_scope`是`none`，则发出简报并注明下游技能不需要。

## 步骤4：发出YAML简报
仅输出YAML块——之前或之后没有散文。严格遵循格式。
在`file_summary_map`中逐个列出每个文件（不要使用通配符）。

```yaml
change_brief:
  classification:
    primary: feat           # 主导的常规提交类型
    types: [feat, fix]      # 检测到的所有类型
    analytics_scope: high   # none | low | medium | high
    stack: frontend         # frontend | backend | fullstack
  summary: "用一句话描述整体变更"
  user_facing_changes:
    - "用户现在可以拖放上传头像并预览，然后保存。"
  surfaces:
    components:
      - name: "AvatarUpload"
        file: "src/components/AvatarUpload.tsx"
        change: modified
  file_summary_map:         # 每个条目包括一个layer字段
    - file: "src/components/AvatarUpload.tsx"
      summary: "用于头像上传的新组件，支持拖放和预览"
      layer: frontend       # frontend | backend | shared
    - file: "src/api/upload.ts"
      summary: "上传端点处理程序，验证文件类型并持久化到S3"
      layer: backend
```
