# InkOS 多智能体小说创作系统

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能合集

InkOS 是一个多智能体命令行界面系统，能够自主创作、审核和修订小说。智能体负责完整的工作流程：作者 → 验证者 → 审核者 → 修订者，并在可配置的检查点进行人工审核。

## 安装

```bash
npm install -g @actalk/inkos
# 或直接运行
npx @actalk/inkos --version
```

**要求：** Node.js ≥ 20.0.0

## 快速入门

```bash
# 创建新的小说项目
inkos book create --title "吞天魔帝" --genre xuanhuan

# 写下一章
inkos write next 吞天魔帝

# 审核特定章节
inkos audit 吞天魔帝 --chapter 3

# 运行完整守护进程（持续生产）
inkos daemon start
```

## 项目结构

执行 `inkos book create` 后，项目目录包含：

```
story/
  outline.md              # 故事大纲（架构智能体输入）
  book_rules.md           # 每本书的定制规则和审核维度
  chapter_summaries.md    # 自动生成的每章摘要
  subplot_board.md        # 子情节进度跟踪（A/B/C线）
  emotional_arcs.md       # 每个角色的情感弧线跟踪
  character_matrix.md     # 角色互动矩阵 + 信息边界
  parent_canon.md         # 衍生作品仅限：导入的典籍约束
  style_profile.json      # 风格指纹（如果使用风格导入）
  style_guide.md          # LLM生成的定性风格指南
  chapters/
    ch001.md
    ch002.md
    ...
```

## 核心命令

### 书籍管理

```bash
inkos book create --title "标题" --genre xuanhuan  # 类别：玄幻 | 仙侠 | 都市 | 恐怖 | 一般
inkos book list
inkos book status 吞天魔帝
```

### 写作流程

```bash
inkos write next 吞天魔帝           # 写下一章（自动加载所有上下文）
inkos write chapter 吞天魔帝 5      # 写特定章节
inkos audit 吞天魔帝 --chapter 3    # 审核章节（33个维度）
inkos revise 吞天魔帝 --chapter 3   # 根据审核结果修订
inkos revise 吞天魔帝 --chapter 3 --mode spot-fix   # 仅点式修正（默认）
inkos revise 吞天魔帝 --chapter 3 --mode rewrite    # 全文重写（谨慎使用）
inkos revise 吞天魔帝 --chapter 3 --mode polish     # 精炼（无结构调整）
```

### 类别系统

```bash
inkos genre list                        # 列出所有内置类别
inkos genre show xuanhuan               # 查看类别的完整规则
inkos genre copy xuanhuan               # 复制类别规则到项目进行定制
inkos genre create wuxia --name 武侠     # 从零创建新类别
```

### 风格匹配

```bash
inkos style analyze reference.txt               # 分析风格指纹
inkos style import reference.txt 吞天魔帝        # 导入风格到书籍
inkos style import reference.txt 吞天魔帝 --name "某作者"
```

### 衍生作品（前传/续集/IF分支）

```bash
inkos book create --title "烈焰前传" --genre xuanhuan
inkos import canon 烈焰前传 --from 吞天魔帝       # 导入父作品典籍约束
inkos write next 烈焰前传                         # 作者自动读取典籍约束
```

### AIGC检测

```bash
inkos detect 吞天魔帝 --chapter 3     # 检测章节中的AIGC标记
inkos detect 吞天魔帝 --all           # 检测所有章节
inkos detect --stats                  # 查看检测历史统计数据
```

### 守护进程（持续生产）

```bash
inkos daemon start                    # 启动调度器（默认：15分钟/周期）
inkos daemon stop
inkos daemon status
```

## 配置

### 全局配置 (`~/.inkos/config.json`)

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4o",
    "apiKey": "sk-...",
    "temperature": 0.8
  },
  "daemon": {
    "intervalMinutes": 15,
    "dailyChapterLimit": 10,
    "parallelBooks": 2
  },
  "webhook": {
    "url": "https://your-server.com/hooks/inkos",
    "secret": "your-hmac-secret",
    "events": ["chapter-complete", "audit-failed", "pipeline-error"]
  },
  "aigcDetection": {
    "provider": "gptzero",
    "apiKey": "...",
    "endpoint": "https://api.gptzero.me/v2/predict/text"
  }
}
```

### 每本书的规则 (`story/book_rules.md`)

````markdown
# 书籍规则：吞天魔帝

## 禁忌 (禁止)
- 主角不得主动求饶
- 不得出现「命运」「天意」等宿命论表述

## 高疲劳词
- 震撼, 惊骇, 恐惧, 颤抖

## additionalAuditDimensions
- 数值系统一致性: 战力数值不得前后矛盾
- 角色成长节奏: 主角突破间隔不少于3章

## 写手特别指令
- 战斗场面优先感官描写，禁止数值报告
````

## 智能体架构

InkOS 依次运行五个专用智能体：

```
架构智能体  →  outline.md, book_rules.md
     ↓
写作者智能体     →  ch00N.md (读取：大纲, 摘要, 弧线, 矩阵, style_guide, canon)
     ↓
验证者智能体  →  11确定性规则，无LLM成本
     ↓  (发现错误 → 立即触发点式修正)
审核者智能体    →  33 LLM维度，temperature=0以确保一致性
     ↓
修订者智能体    →  点式修正 | 重写 | 精炼 | 抗检测
```

### 写后验证规则（确定性，无LLM）

| 规则 | 条件 |
|------|-----------|
| 禁止模式 | `不是……而是……`结构 |
| 破折号禁用 | `——`字符 |
| 过渡词密度 | 仿佛/忽然/竟然≤1 per 3000字符 |
| 高疲劳词 | 每本书列表，每章≤1 |
| 元叙事 | 电影剧本式叙述 |
| 报告术语 | 分析框架术语在散文中 |
| 作者道德说教 | 显然/不言而喻等 |
| 集体反应 | 「全场震惊」陈词滥调 |
| 连续了 | ≥4连续句子有了 |
| 段落长度 | ≥2段落超过300字符 |
| 书籍特定禁令 | `book_rules.md`禁止列表 |

### 审核维度（共33个，LLM评估）

关键维度包括：
- 维度1–23：核心叙事质量（情节、角色、节奏、伏笔）
- 维度24–26：子情节停滞、弧线平缓、节奏单调（所有5个类别）
- 维度27：敏感内容
- 维度28–31：衍生作品特定（典籍冲突、未来信息泄露、世界规则一致性、伏笔隔离）
- 维度32：读者预期管理
- 维度33：大纲偏离检测

## 代码集成示例

### 编程使用（TypeScript）

```typescript
import { BookManager } from '@actalk/inkos'
import { WriterAgent } from '@actalk/inkos/agents'
import { ValidatorAgent } from '@actalk/inkos/agents'

// 创建并配置书籍
const manager = new BookManager()
const book = await manager.createBook({
  title: '吞天魔帝',
  genre: 'xuanhuan',
  outlinePath: './my-outline.md'
})

// 运行写作流程下一章
const writer = new WriterAgent({ temperature: 0.8 })
const chapter = await writer.writeNext(book)

// 运行确定性验证（无LLM成本）
const validator = new ValidatorAgent()
const validationResult = await validator.validate(chapter, book)

if (validationResult.hasErrors) {
  // 自动触发点式修正
  const reviser = new ReviserAgent({ mode: 'spot-fix' })
  const fixed = await reviser.revise(chapter, validationResult.errors, book)
  console.log('修正违规:', validationResult.errors.length)
}
```

### Webhook处理器（Express）

```typescript
import express from 'express'
import crypto from 'crypto'

const app = express()
app.use(express.raw({ type: 'application/json' }))

app.post('/hooks/inkos', (req, res) => {
  const sig = req.headers['x-inkos-signature'] as string
  const expected = crypto
    .createHmac('sha256', process.env.INKOS_WEBHOOK_SECRET!)
    .update(req.body)
    .digest('hex')

  if (sig !== `sha256=${expected}`) {
    return res.status(401).send('Invalid signature')
  }

  const event = JSON.parse(req.body.toString())

  switch (event.type) {
    case 'chapter-complete':
      console.log(`章节${event.chapter}的"${event.book}"完成`)
      // 触发人工审核关卡
      notifyReviewer(event)
      break
    case 'audit-failed':
      console.log(`审核失败：${event.criticalCount}个严重问题`)
      break
    case 'pipeline-error':
      console.error(`"${event.book}"流程错误：`, event.error)
      break
  }

  res.status(200).json({ received: true })
})
```

### 自定义类别定义

```typescript
// genres/wuxia.ts
import type { GenreConfig } from '@actalk/inkos/types'

export const wuxia: GenreConfig = {
  id: 'wuxia',
  name: '武侠',
  chapterTypes: ['江湖相遇', '武功切磋', '恩怨纠葛', '门派争斗', '武林大会'],
  forbiddenPatterns: [
    '内力值', '战力', '等级提升',   // 无数值力量系统
    '系统', '面板', '属性点'
  ],
  fatiguedWords: ['震惊', '无敌', '碾压', '秒杀'],
  languageRules: [
    {
      bad: '内力增加了100点',
      good: '一股暖流沿经脉漫开，指尖的颤抖渐渐平息'
    }
  ],
  auditDimensions: [
    '武功描写感官化',
    '江湖规则内部一致性',
    '恩怨情仇弧线完整性'
  ]
}
```

### 风格导入流程

```typescript
import { StyleAnalyzer } from '@actalk/inkos/style'

const analyzer = new StyleAnalyzer()

// 分析参考文本
const profile = await analyzer.analyze('./reference-novel.txt')
console.log(profile)
// {
//   avgSentenceLength: 18.3,
//   ttr: 0.42,           // 类型-词数比
//   rhetoricalDensity: 0.15,
//   paragraphLengthDist: { p25: 45, p50: 89, p75: 156 },
//   punctuationStyle: '稀疏'
// }

// 导入到书籍（生成 style_profile.json + style_guide.md）
await analyzer.importToBook('./reference-novel.txt', '吞天魔帝', {
  authorName: '某作者'
})
```

## 审核修订循环

v0.4版本加固的审核-修订循环防止修订引入更多AI标记：

```
审核者智能体 (temp=0)
     ↓ 发现严重问题
修订者智能体 点式修正
     ↓
AI标记计数比较
     ↓ 标记增加？
  是 → 放弃修订，保留原始
  否  → 接受修订
     ↓
重新审核 (temp=0)
```

**审核一致性的关键设置：**
- 审核者始终运行在 `temperature: 0` — 消除同一章节0–6个严重差异
- 默认修订模式是 `spot-fix`（仅修改问题句子）
- `rewrite` 模式可用，但会引入6倍更多AI标记
- `polish` 模式边界锁定：无段落增删，无名称变更，无新情节

## 衍生作品典籍约束

检测到 `parent_canon.md` 时，4个额外审核维度自动激活：

```markdown
# parent_canon.md (由 `inkos import canon` 自动生成)

## 正传世界规则
- 力量体系: 炼体→炼气→炼丹→炼神→炼虚
- 地理: 九州大陆，东海以东无人居住
- 阵营: 正道五宗 vs 魔道三门

## 关键事件时间线
- 第1章: 主角获得吞天诀
- 第45章: 正道五宗盟约成立 [分歧点]

## 角色快照 (分歧点时状态)
- 林天: 炼气期第三层，未知父母身世
- 剑宗宗主: 在世，尚未叛变

## 伏笔状态 (正传专属，番外禁止回收)
- 古剑残片: 未解
- 神秘老人身份: 未解
```

## 故障排除

**验证器每章触发**
检查 `book_rules.md` 疲劳词列表 — 列出的词每章强制≤1。

**审核结果在不同运行中差异巨大**
确认配置中审核者温度锁定为0。如果使用代理LLM API，确保其尊重 `temperature: 0`。

**修订引入比原始更多AI标记**
这是预期行为 — InkOS v0.4自动检测并放弃修订。如果反复发生，显式切换到 `spot-fix` 模式。

**衍生作品审核错误标记事件**
验证 `parent_canon.md` 分歧点时间戳准确。分歧点前的事件是典籍锁定；分歧点后的事件对衍生作品开放。

**守护进程在重复失败后停止某本书**
检查 `daemon status` 挂起的书籍。修复根本问题（通常是大纲模糊或 `book_rules.md` 矛盾）后，运行 `inkos daemon resume 书名`。

**风格指南未被写作者应用**
再次运行 `inkos style import` — 如果 `style_guide.md` 缺失或为空，写作者会静默跳过风格注入。确保参考文本≥5000字符以获得可靠指纹。
