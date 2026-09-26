# AntV技能维护者

此技能确保每当此存储库中添加或更新技能时，所有文档和配置文件都能保持同步。

## 重要提示

`antv-skills-maintainer` 技能是 **仅供内部使用** — 它仅用于此存储库的迭代工作流程。**不要**将其添加到 `README.md` "可用技能" 或 `.claude-plugin/marketplace.json` 中。只有面向用户的技能才应出现在这些文件中。

## 何时应用

在**每次代码变更后**自动应用此技能 — 特别是当：

- 在 `skills/` 下添加新的技能目录
- 修改现有技能的 `SKILL.md`（名称、描述、功能）
- 删除或弃用技能

## 需要保持同步的内容

### 1. README.md — "可用技能" 部分

`README.md` 中的 `## 可用技能` 部分必须列出 `skills/` 下所有技能，并包含：

- 合适的 emoji 图标
- 技能 **名称**（粗体，与目录名称匹配）
- 与技能 `SKILL.md` frontmatter `description` 字段匹配的一行描述
- 简短的段落详细说明技能的功能

**格式：**

```markdown
- 🔧 **skill-name**: 来自 SKILL.md frontmatter 的一行描述。

`Skill Display Name` 详细说明段落...
```

**步骤：**

1. 扫描 `skills/` 目录以列出所有可用技能。
2. 读取每个技能的 `SKILL.md` frontmatter（`name`、`description`）。
3. 与 `README.md` 中的当前 `## 可用技能` 部分进行比较。
4. 为新技能添加条目，更新已更改技能的条目，删除已删除技能的条目。
5. 保留该部分的现有格式样式。

### 2. `.claude-plugin/marketplace.json` — 插件数组

`.claude-plugin/marketplace.json` 中的 `plugins` 数组必须包含 `skills/` 下每个技能的条目。

**条目格式：**

```json
{
  "name": "skill-name",
  "description": "来自 SKILL.md frontmatter 的描述。",
  "source": "./",
  "strict": false,
  "skills": [
    "./skills/skill-name"
  ]
}
```

**步骤：**

1. 扫描 `skills/` 目录以列出所有可用技能。
2. 读取每个技能的 `SKILL.md` frontmatter（`name`、`description`）。
3. 与 `.claude-plugin/marketplace.json` 中的当前 `plugins` 数组进行比较。
4. 为新技能添加条目，更新已更改技能的 `description`，删除已删除技能的条目。
5. 保持 JSON 格式正确且有效。

## 执行检查清单

在发生任何与技能相关的代码变更后，请执行以下检查清单：

- [ ] `skills/` 中的所有技能目录都列在 `README.md` 的 `## 可用技能` 下
- [ ] `README.md` 中的所有技能描述都与相应的 `SKILL.md` frontmatter 匹配
- [ ] `skills/` 中的所有技能目录都在 `.claude-plugin/marketplace.json` 中有相应的条目
- [ ] `marketplace.json` 中的所有 `description` 字段都与相应的 `SKILL.md` frontmatter 匹配
- [ ] `README.md` 或 `marketplace.json` 中不存在已删除技能的过时条目
- [ ] 修改后 `marketplace.json` 仍然是有效的 JSON
