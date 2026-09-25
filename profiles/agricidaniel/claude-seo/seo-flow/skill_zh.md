# FLOW 框架：发现 · 利用 · 优化 · 获胜

FLOW 是一个以证据为导向的 SEO 运营模式，专为 AI 搜索时代构建。Claude SEO 集成了 FLOW 提示库（涵盖 5 个阶段共 41 个提示），使每项分析都能由结构化、有证据支持的 AI 提示驱动，而非临时查询。

> 框架和提示 © Daniel Agrici, CC BY 4.0: github.com/AgriciDaniel/flow

**运行时上下文：** 每次激活 `/seo flow` 时加载 `references/flow-framework.md`。按需加载提示文件，仅针对用户请求的阶段。

---

## 命令

| 命令 | 功能 |
|------|------|
| `/seo flow` | 显示 FLOW 概览 + 阶段菜单 |
| `/seo flow find [url\|topic]` | 发现阶段：关键词研究、差距分析、SERP 意图映射（5 个提示） |
| `/seo flow leverage [url]` | 利用阶段：反向链接策略、站外权威（1 个提示） |
| `/seo flow optimize [url]` | 优化阶段：根据上下文选择 2-3 个最相关的 21 个提示 |
| `/seo flow win [url]` | 获胜阶段：最终转化目标、转化率、双重表面评分卡（3 个提示） |
| `/seo flow local [url]` | 本地阶段：GBP 优化、元数据、标题标签、本地审核（11 个提示） |
| `/seo flow prompts` | 所有 41 个提示的完整索引（阶段、名称、触发条件） |
| `/seo flow sync` | 从 github.com/AgriciDaniel/flow 拉取最新提示文件 |

---

## 协调逻辑

### 在 `/seo flow`（无子命令）
1. 读取 `references/flow-framework.md`
2. 显示 FLOW 阶段概览，每个阶段附有一行描述
3. 询问：哪个阶段符合用户当前情况？

### 在 `/seo flow find [url|topic]`
1. 读取 `references/prompts/find/` 中的所有文件
2. 将每个提示应用于 URL 或主题
3. 交叉引用："要进行更深入的 SERP 聚类分析，请查看 `/seo cluster <种子关键词>`"

### 在 `/seo flow leverage [url]`
1. 读取 `references/prompts/leverage/` 中的文件
2. 应用于 URL 的当前反向链接上下文
3. 交叉引用："要查看原始反向链接数据，请查看 `/seo backlinks <url>`"

### 在 `/seo flow optimize [url]`
1. 读取 `references/prompts/optimize/` 中的所有文件名
2. 读取先前的分析上下文（URL、行业垂直领域、对话中任何先前的技能输出）
3. 选择 2-3 个最相关的提示；仅加载这些文件
4. 应用选定的提示；其他提示可通过 `/seo flow prompts` 访问
5. 交叉引用："要进行完整的内容质量分析，请查看 `/seo content <url>` 和 `/seo geo <url>`"

### 在 `/seo flow win [url]`
1. 读取 `references/prompts/win/` 中的所有文件
2. 将每个提示应用于 URL 的转化和最终转化目标上下文
3. 交叉引用："要进行 SXO 人设评分，请查看 `/seo sxo <url>`"

### 在 `/seo flow local [url]`
1. 读取 `references/prompts/local/` 中的所有文件
2. 应用于 URL 的本地 SEO 上下文
3. 交叉引用："要进行完整的本地 SEO 分析，请查看 `/seo local <url>` 和 `/seo maps [命令]"`

### 在 `/seo flow prompts`
1. 读取 `references/prompts/README.md`
2. 显示完整索引：所有 41 个提示（阶段、名称、触发条件）

### 在 `/seo flow sync`
1. 运行：`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run sync_flow.py`
2. 显示 JSON 摘要（添加的文件、更新的文件、未更改的文件）
3. 同步完成后显示署名声明

---

## 上下文匹配（优化阶段）

优化阶段有 21 个提示。全部 21 个提示都是噪音。按优先级选择：

1. **行业垂直领域**（SaaS → 站内 + 技术；本地 → 引用 + GBP；发布商 → E-E-A-T + 刷新度）
2. **先前的技能输出**（SEO 技术标记的爬取问题 → 技术优化提示；SEO 内容标记的 E-E-A-T 差距 → 内容优化提示）
3. **URL 信号**（产品页面 → 转化；博客 → 刷新度 + 权威性）

始终显示 2-3 个提示。说明你选择了哪些提示以及原因。

---

## 参考文件

按需加载，启动时不要全部加载：
- `references/flow-framework.md`：FLOW 运营模式（每次激活 `/seo flow` 时加载）
- `references/bibliography.md`：证据来源；引用研究或统计数据时加载
- `references/prompts/README.md`：提示索引；用于 `/seo flow prompts`
- `references/prompts/find/`：5 个提示；用于 `/seo flow find`
- `references/prompts/leverage/`：1 个提示；用于 `/seo flow leverage`
- `references/prompts/optimize/`：21 个提示；按需加载用于 `/seo flow optimize`
- `references/prompts/win/`：3 个提示；用于 `/seo flow win`
- `references/prompts/local/`：11 个提示；用于 `/seo flow local`

---

## 署名

每次激活 `/seo flow`（任何子命令）在分析前输出：

```
Framework and prompts © Daniel Agrici, CC BY 4.0: github.com/AgriciDaniel/flow
```

不要遗漏或修改署名。

---

## 错误处理

| 场景 | 操作 |
|------|------|
| `references/flow-framework.md` 缺失 | "FLOW 参考文件未同步。运行：`/seo flow sync`" |
| 提示文件缺失 | "运行 `/seo flow sync` 从 FLOW 仓库拉取最新提示。" |
| `sync_flow.py` 网络错误 | 显示脚本的 stderr。检查速率限制：`gh api rate_limit`。 |
| `sync_flow.py` 认证错误 | 运行 `gh auth login` 然后重试。 |
