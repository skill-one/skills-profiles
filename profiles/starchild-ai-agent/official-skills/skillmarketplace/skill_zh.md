# 技能市场

## 搜索与安装技能

**始终使用 `search_skills` 工具。** 请勿手动使用 `curl`、浏览 GitHub 或下载 SKILL.md 文件。

`search_skills` 会自动完成所有操作：

1. **本地** — 首先检查已安装的技能
2. **Starchild 社区** — 搜索社区技能索引
3. **skills.sh** — 搜索全局技能生态系统（OpenClaw、Vercel、Anthropic 等）
4. **自动安装** — 通过 `npx skills add` 安装最佳匹配项（默认：`auto_install=true`）

### 使用方法

```
search_skills(query="deploy")           # 搜索并自动安装最佳匹配项
search_skills(query="trading")          # 搜索并自动安装
search_skills(query="k8s", auto_install=false)  # 仅搜索，不安装
search_skills()                         # 列出所有已安装的技能
```

`search_skills` 安装技能后，该技能立即可用。仅在手动编辑技能文件时才需要调用 `skill_refresh()`。

### 不应执行的操作

- 请勿 `curl` GitHub 仓库来浏览/下载技能
- 请勿 `mkdir -p skills/<name>` 并手动编写 SKILL.md
- 请勿使用 `web_fetch` 下载技能文件
- 请勿使用旧的网关搜索/安装端点（它们已不再存在）

---

## 发布（仅限 Starchild）

发布仍使用网关。仅 Starchild 开发的技能可以发布。

### SKILL.md 要求

```yaml
---
name: my-skill
version: 1.0.0
description: 该技能的功能描述
author: 你的名字
tags: [tag1, tag2]
---
```

| 字段 | 是否必需 | 规则 |
|-------|----------|-------|
| `name` | 是 | 小写字母、数字 + 连字符，2-64 个字符 |
| `version` | 是 | Semver 格式（例如 `1.0.0`）— 发布后不可更改 |
| `description` | 推荐使用 | 搜索用的简短摘要 |
| `author` | 推荐使用 | 作者名称 |
| `tags` | 推荐使用 | 用于可发现性的标签数组 |

### 发布工作流程

**步骤 1：验证技能目录**

```bash
SKILL_DIR="./skills/my-skill"
head -20 "$SKILL_DIR/SKILL.md"
```

**步骤 2：获取 OIDC 令牌**

```bash
TOKEN=$(curl -s --unix-socket /.fly/api \
  -X POST -H "Content-Type: application/json" \
  "http://localhost/v1/tokens/oidc" \
  -d '{"aud": "skills-market-gateway"}')
```

**步骤 3：构建并发送发布请求**

```bash
SKILL_DIR="./skills/my-skill"
GATEWAY="https://skills-market-gateway.fly.dev"

PAYLOAD=$(python3 -c "
import os, json
files = {}
for root, dirs, fnames in os.walk('$SKILL_DIR'):
    for f in fnames:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, '$SKILL_DIR')
        with open(full) as fh:
            files[rel] = fh.read()
print(json.dumps({'files': files}))
")

curl -s -X POST "$GATEWAY/skills/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | python3 -m json.tool
```

### 响应（201）

```json
{
  "namespace": "@554",
  "name": "my-skill",
  "version": "1.0.0",
  "tag": "@554/my-skill@1.0.0",
  "download_url": "https://github.com/.../bundle.zip",
  "release_url": "https://github.com/.../releases/tag/..."
}
```

### 版本规则

- 每个版本是 **不可变的** — 发布后无法被覆盖。
- 要更新，请增加版本号并重新发布。

---

## 决策树

```
用户想要查找/安装技能
  → 使用 `search_skills(query)` 工具 — 它会搜索所有来源并自动安装
  → 绝不使用 `curl` GitHub 或手动下载文件

用户想要列出已安装的技能
  → 使用不带查询参数的 `search_skills()`

用户想要发布技能
  → 验证 SKILL.md 的 frontmatter
  → 获取 OIDC 令牌（受众：skills-market-gateway）
  → POST 到 /skills/publish

用户想要创建新技能
  → 首先阅读 skill-creator 技能
```
