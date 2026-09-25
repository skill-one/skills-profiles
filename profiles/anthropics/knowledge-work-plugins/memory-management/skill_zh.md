# 内存管理

内存让 Claude 成为你的工作场所协作伙伴——一个能说你的内部语言的人。

## 目标

将简写转化为理解：

```
用户："ask todd to do the PSR for oracle"
              ↓ Claude 解码
"Ask Todd Martinez (财务主管) 准备 Oracle 系统交易的管道状态报告
(合同金额 230 万美元，第二季度结束)"
```

没有内存，这个请求就没有意义。有了内存，Claude 知道：
- **todd** → Todd Martinez，财务主管，偏好使用 Slack
- **PSR** → 管道状态报告（每周销售文档）
- **oracle** → Oracle 系统交易，不是公司本身

## 架构

```
CLAUDE.md          ← 热缓存 (~30 人，常用术语)
memory/
  glossary.md      ← 完整解码器（所有内容）
  people/          ← 完整资料
  projects/        ← 项目详情
  context/         ← 公司、团队、工具
```

**CLAUDE.md (热缓存)：**
- 你最常互动的前 30 人
- ~30 个最常用的缩写/术语
- 活动项目（5-15 个）
- 你的偏好
- **目标：覆盖 90% 的日常解码需求**

**memory/glossary.md (完整词汇表)：**
- 完整解码器——所有人，所有术语
- 当某项内容不在 CLAUDE.md 中时搜索
- 可以无限增长

**memory/people/, projects/, context/:**
- 执行时需要时提供丰富细节
- 完整资料、历史记录、上下文

## 查找流程

```
用户："ask todd about the PSR for phoenix"

1. 检查 CLAUDE.md (热缓存)
   → Todd? ✓ Todd Martinez，财务
   → PSR? ✓ 管道状态报告
   → Phoenix? ✓ 数据库迁移项目

2. 如果未找到 → 搜索 memory/glossary.md
   → 完整词汇表包含所有人/所有内容

3. 如果仍然未找到 → 询问用户
   → "X 代表什么？我会记住它。"
```

这种分层方法使 CLAUDE.md 保持精简 (~100 行)，同时在内存中支持无限扩展。

## 文件位置

- **工作内存：** 当前工作目录中的 `CLAUDE.md`
- **深层内存：** `memory/` 子目录

## 工作内存格式 (CLAUDE.md)

使用表格以保持紧凑性。总行数目标为 ~50-80 行。

```markdown
# 内存

## 我
[姓名]，[角色] 在 [团队]。关于我做什么的一句话。

## 人员
| 谁 | 角色 |
|-----|------|
| **todd** | Todd Martinez，财务主管 |
| **Sarah** | Sarah Chen，工程（平台） |
| **Greg** | Greg Wilson，销售 |
→ 完整列表：memory/glossary.md，资料：memory/people/

## 术语
| 术语 | 含义 |
|------|---------|
| PSR | 管道状态报告 |
| P0 | 放弃一切优先级 |
| standup | 每日 9 点同步 |
→ 完整词汇表：memory/glossary.md

## 项目
| 名称 | 内容 |
|------|------|
| **Phoenix** | 数据库迁移，第二季度启动 |
| **Horizon** | 移动应用改版 |
→ 详情：memory/projects/

## 偏好
- 25 分钟会议带缓冲
- 异步优先，Slack 超过邮件
- 周五下午不开会
```

## 深层内存格式 (memory/)

**memory/glossary.md** - 解码器：
```markdown
# 词汇表

工作场所简写、缩写和内部语言。

## 缩写
| 术语 | 含义 | 上下文 |
|------|---------|---------|
| PSR | 管道状态报告 | 每周销售文档 |
| OKR | 目标与关键成果 | 每季度规划 |
| P0/P1/P2 | 优先级级别 | P0 = 放弃一切 |

## 内部术语
| 术语 | 含义 |
|------|------|
| standup | 每日 9 点在 #engineering 进行同步 |
| the migration | 项目 Phoenix 数据库工作 |
| ship it | 部署到生产环境 |
| escalate | 循环领导层 |

## 昵称 → 全名
| 昵称 | 人物 |
|----------|------|
| Todd | Todd Martinez (财务) |
| T | 也是 Todd Martinez |

## 项目代号
| 代号 | 项目 |
|------|------|
| Phoenix | 数据库迁移 |
| Horizon | 新移动应用 |
```

**memory/people/{name}.md:**
```markdown
# Todd Martinez

**也称为：** Todd, T
**角色：** 财务主管
**团队：** 财务
**汇报给：** CFO (Michael Chen)

## 沟通
- 偏好 Slack DM
- 反应迅速，非常直接
- 最佳时间：早上

## 上下文
- 负责所有 PSR 和财务报告
- 50 万美元以上交易批准的关键联系人
- 与销售密切合作进行预测

## 备注
- 芝加哥小熊队球迷，喜欢谈论棒球
```

**memory/projects/{name}.md:**
```markdown
# 项目 Phoenix

**代号：** Phoenix
**也称为：** "the migration"
**状态：** 活动中，第二季度启动

## 内容
从遗留 Oracle 迁移到 PostgreSQL 的数据库迁移。

## 关键人物
- Sarah - 技术主管
- Todd - 预算负责人
- Greg - 利益相关者（销售影响）

## 上下文
120 万美元预算，6 个月时间表。对 Horizon 项目的关键路径。
```

**memory/context/company.md:**
```markdown
# 公司上下文

## 工具和系统
| 工具 | 用于 | 内部名称 |
|------|------|----------|
| Slack | 沟通 | - |
| Asana | 工程任务 | - |
| Salesforce | CRM | "SF" 或 "the CRM" |
| Notion | 文档/维基 | - |

## 团队
| 团队 | 他们做什么 | 关键人物 |
|------|------------|----------|
| Platform | 基础设施 | Sarah (主管) |
| Finance | 金钱事务 | Todd (主管) |
| Sales | 收入 | Greg |

## 流程
| 流程 | 含义 |
|------|------|
| Weekly sync | 周一 10 点全体会议 |
| Ship review | 周四部署批准 |
```

## 如何交互

### 解码用户输入（分层查找）

**始终**在执行请求前解码简写：

```
1. CLAUDE.md (热缓存)     → 首先检查，覆盖 90% 的情况
2. memory/glossary.md        → 热缓存中未找到时，使用完整词汇表
3. memory/people/, projects/ → 需要时提供丰富细节
4. 询问用户                  → 未知术语？学习它。
```

示例：
```
用户："ask todd to do the PSR for oracle"

CLAUDE.md 查找：
  "todd" → Todd Martinez，财务 ✓
  "PSR" → 管道状态报告 ✓
  "oracle" → 热缓存中未找到

memory/glossary.md 查找：
  "oracle" → Oracle 系统交易 (230 万美元) ✓

现在 Claude 可以带完整上下文执行。
```

### 添加内存

当用户说“记住这个”或“X 代表 Y”：

1. **词汇表项**（缩写、术语、简写）：
   - 添加到 memory/glossary.md
   - 如果经常使用，添加到 CLAUDE.md 快速词汇表

2. **人员：**
   - 创建/更新 memory/people/{name}.md
   - 如果重要，添加到 CLAUDE.md 关键人员
   - **捕获昵称**——对解码至关重要

3. **项目：**
   - 创建/更新 memory/projects/{name}.md
   - 如果当前活跃，添加到 CLAUDE.md 活动项目
   - **捕获代号**——"Phoenix"、"the migration" 等

4. **偏好：** 添加到 CLAUDE.md 偏好部分

### 回忆内存

当用户问“X 是谁”或“X 代表什么”：

1. 首先检查 CLAUDE.md
2. 检查 memory/ 以获取完整细节
3. 如果未找到： "我还不知道 X 代表什么。你能告诉我吗？"

### 逐步披露

1. 加载 CLAUDE.md 以快速解析任何请求
2. 当需要完整上下文执行时，深入 memory/
3. 示例：起草一封关于 PSR 的邮件给 Todd
   - CLAUDE.md 告诉你 Todd = Todd Martinez，PSR = 管道状态报告
   - memory/people/todd-martinez.md 告诉你他偏好使用 Slack，非常直接

## 初始化

使用 `/productivity:start` 通过扫描你的聊天、日历、邮件和文档来初始化。提取人员、项目，并开始构建词汇表。

## 规范

- **粗体** CLAUDE.md 中的术语以提高可读性
- 保持 CLAUDE.md 在 ~100 行以内（“热 30”规则）
- 文件名：小写，连字符 (`todd-martinez.md`, `project-phoenix.md`)
- 始终捕获昵称和别名
- 词汇表表格以便于查找
- 当某项内容经常使用时，将其提升到 CLAUDE.md
- 当某项内容过时，将其降级到 memory/ 仅存储

## 哪里存放什么

| 类型 | CLAUDE.md (热缓存) | memory/ (完整存储) |
|------|----------------------|------------------------|
| 人员 | 前 ~30 位频繁联系人 | glossary.md + people/{name}.md |
| 缩写/术语 | ~30 个最常见 | glossary.md (完整列表) |
| 项目 | 仅活动项目 | glossary.md + projects/{name}.md |
| 昵称 | 如果前 30 位则添加到关键人员 | glossary.md (所有昵称) |
| 公司上下文 | 快速参考仅 | context/company.md |
| 偏好 | 所有偏好 | - |
| 历史记录/过时 | ✗ 删除 | ✓ 在 memory/ 中保留 |

## 提升 / 降级

**提升到 CLAUDE.md 当：**
- 你经常使用某个术语/人物
- 它是当前工作的一部分

**降级到 memory/ 仅当：**
- 项目已完成
- 人物不再是频繁联系人
- 术语很少使用

这使 CLAUDE.md 保持新鲜和相关。
