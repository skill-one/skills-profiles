# 面向令牌的对象符号（TOON）

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

TOON 是 JSON 数据模型的紧凑、人类可读的编码，它最小化了用于 LLM 输入的令牌。它结合了 YAML 风格的缩进来表示嵌套对象，以及 CSV 风格的表格布局来表示统一数组，在保持或提高 LLM 理解准确性的同时，实现了约 40% 的令牌减少。

## 安装

```bash
# npm
npm install @toon-format/toon

# pnpm
pnpm add @toon-format/toon

# yarn
yarn add @toon-format/toon
```

## 命令行界面（CLI）

```bash
# 全局安装
npm install -g @toon-format/toon

# 将 JSON 文件转换为 TOON
toon encode input.json
toon encode input.json -o output.toon

# 将 TOON 转换回 JSON
toon decode input.toon
toon decode input.toon -o output.json

# 管道支持
cat data.json | toon encode
cat data.toon | toon decode

# 美化 JSON 输出
toon decode input.toon --pretty

# 显示令牌计数比较
toon encode input.json --stats
```

## 核心API

### encode / stringify

```typescript
import { encode, decode } from '@toon-format/toon';

// 基本编码（JSON → TOON 字符串）
const data = {
  context: {
    task: '我们最喜欢的徒步旅行',
    location: '博尔德',
    season: 'spring_2025',
  },
  friends: ['ana', 'luis', 'sam'],
  hikes: [
    { id: 1, name: '蓝湖步道', distanceKm: 7.5, elevationGain: 320, companion: 'ana', wasSunny: true },
    { id: 2, name: '山脊展望', distanceKm: 9.2, elevationGain: 540, companion: 'luis', wasSunny: false },
    { id: 3, name: '野花环线', distanceKm: 5.1, elevationGain: 180, companion: 'sam', wasSunny: true },
  ],
};

const toon = encode(data);
console.log(toon);
// context:
//   task: 我们最喜欢的徒步旅行
//   location: 博尔德
//   season: spring_2025
// friends[3]: ana,luis,sam
// hikes[3]{id,name,distanceKm,elevationGain,companion,wasSunny}:
//   1,Blue Lake Trail,7.5,320,ana,true
//   2,Ridge Overlook,9.2,540,luis,false
//   3,Wildflower Loop,5.1,180,sam,true
```

### decode / parse

```typescript
import { decode } from '@toon-format/toon';

const toonString = `
context:
  task: 我们最喜欢的徒步旅行
  location: 博尔德
friends[2]: ana,luis
hikes[2]{id,name,distanceKm}:
  1,Blue Lake Trail,7.5
  2,Ridge Overlook,9.2
`;

const parsed = decode(toonString);
// 返回原始的 JavaScript 对象
console.log(parsed.hikes[0].name); // 'Blue Lake Trail'
```

### 编码选项

```typescript
import { encode } from '@toon-format/toon';

const toon = encode(data, {
  // 强制所有数组使用表格格式（默认：自动检测统一数组）
  tabular: 'always',

  // 从不使用表格格式
  // tabular: 'never',

  // 嵌套对象的缩进大小（默认：2）
  indent: 2,

  // 引用包含特殊字符的字符串（默认：自动）
  quoting: 'auto',
});
```

## 格式概述

### 基本标量

TOON 与 YAML 一样编码标量，当没有歧义时不加引号：

```
name: Alice
age: 30
active: true
score: 98.6
nothing: null
```

### 嵌套对象（YAML 风格缩进）

```
user:
  name: Alice
  address:
    city: Boulder
    zip: 80301
```

### 平面数组（标量项）

方括号声明数组长度，值用逗号分隔：

```
tags[3]: typescript,llm,serialization
scores[4]: 10,20,30,40
```

### 统一对象数组（表格格式）

花括号声明字段标题；每个后续缩进的行是一个行：

```
employees[3]{id,name,department,salary}:
  1,Alice,Engineering,95000
  2,Bob,Marketing,72000
  3,Carol,Engineering,102000
```

### 引用规则

包含逗号、冒号或换行符的值被引用：

```
notes[2]: "hello, world","line1\nline2"
messages[1]{from,text}:
  alice,"See you at 3:00, okay?"
```

### 混合嵌套

```
company:
  name: Acme Corp
  founded: 1987
  offices[2]: NYC,SF
  teams[2]{name,headcount}:
    Engineering,45
    Marketing,20
```

## 使用 TOON 与 LLM

### 直接提示注入

```typescript
import { encode } from '@toon-format/toon';
import OpenAI from 'openai';

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function queryWithToon(data: unknown, question: string) {
  const toon = encode(data);

  const response = await client.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      {
        role: 'system',
        content: [
          '你是数据分析师。用户将提供 TOON 格式的数据。',
          'TOON 是 JSON 的紧凑编码：缩进 = 嵌套，',
          'key[N]: v1,v2 = N 个标量值的数组，',
          'key[N]{field1,field2}: 行 = N 个具有 field1、field2 字段的对象数组。',
        ].join(' '),
      },
      {
        role: 'user',
        content: `数据:\n\`\`\`\n${toon}\n\`\`\`\n\n问题: ${question}`,
      },
    ],
  });

  return response.choices[0].message.content;
}

// 使用示例
const employees = [
  { id: 1, name: 'Alice', dept: 'Eng', salary: 95000 },
  { id: 2, name: 'Bob', dept: 'Marketing', salary: 72000 },
];

const answer = await queryWithToon(
  { employees },
  '谁薪水最高？'
);
```

### Anthropic / Claude

```typescript
import { encode } from '@toon-format/toon';
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

async function analyzeWithClaude(data: unknown, prompt: string) {
  const toon = encode(data);

  const message = await client.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 1024,
    system:
      '数据以 TOON 格式提供：缩进 = 嵌套对象，key[N]: 值 = 标量数组，key[N]{字段}: 行 = 对象数组。',
    messages: [
      {
        role: 'user',
        content: `\`\`\`toon\n${toon}\n\`\`\`\n\n${prompt}`,
      },
    ],
  });

  return message.content[0].type === 'text' ? message.content[0].text : null;
}
```

### 令牌计数比较工具

```typescript
import { encode } from '@toon-format/toon';
import { encode as gptEncode } from 'gpt-tokenizer';

function compareTokens(data: unknown) {
  const jsonStr = JSON.stringify(data);
  const toonStr = encode(data);

  const jsonTokens = gptEncode(jsonStr).length;
  const toonTokens = gptEncode(toonStr).length;
  const savings = (((jsonTokens - toonTokens) / jsonTokens) * 100).toFixed(1);

  console.log(`JSON:  ${jsonTokens} 令牌`);
  console.log(`TOON:  ${toonTokens} 令牌`);
  console.log(`节省: ${savings}%`);

  return { jsonTokens, toonTokens, savings: parseFloat(savings) };
}
```

## 常见模式

### 使用 TOON 进行批量 API 调用

```typescript
import { encode } from '@toon-format/toon';

// 分别编码每条记录以进行独立的 LLM 调用
function encodeRecords<T>(records: T[]): string[] {
  return records.map((r) => encode(r));
}

// 将所有记录编码为一个 TOON 文档（批量处理最有效）
function encodeAll<T>(records: T[], key = 'records'): string {
  return encode({ [key]: records });
}
```

### RAG / 检索上下文注入

```typescript
import { encode } from '@toon-format/toon';

interface SearchResult {
  id: string;
  title: string;
  snippet: string;
  score: number;
  url: string;
}

function buildRagContext(results: SearchResult[]): string {
  // TOON 在这里非常理想 — 统一对象会折叠成一个紧凑的表格
  return encode({ results });
}

// 输出:
// results[5]{id,title,snippet,score,url}:
//   doc1,Introduction to TOON,...,0.95,https://...
//   doc2,TOON vs JSON,...,0.87,https://...
```

### 大型数据集的流式编码

```typescript
import { encode } from '@toon-format/toon';
import { createReadStream, createWriteStream } from 'fs';

// 对于大型 JSON 文件：读取 → 解析 → 编码 → 写入
async function convertFile(inputPath: string, outputPath: string) {
  const raw = await fs.promises.readFile(inputPath, 'utf-8');
  const data = JSON.parse(raw);
  const toon = encode(data);
  await fs.promises.writeFile(outputPath, toon, 'utf-8');

  const jsonBytes = Buffer.byteLength(raw);
  const toonBytes = Buffer.byteLength(toon);
  console.log(`减小了 ${(((jsonBytes - toonBytes) / jsonBytes) * 100).toFixed(1)}% 的大小`);
}
```

### 基于模式的编码（TypeScript）

```typescript
import { encode, decode } from '@toon-format/toon';

interface Employee {
  id: number;
  name: string;
  department: string;
  salary: number;
  active: boolean;
}

interface EmployeeReport {
  generatedAt: string;
  employees: Employee[];
}

// encode 是泛型友好的 — 传递任何可序列化的对象
const report: EmployeeReport = {
  generatedAt: new Date().toISOString(),
  employees: [
    { id: 1, name: 'Alice', department: 'Engineering', salary: 95000, active: true },
    { id: 2, name: 'Bob', department: 'Marketing', salary: 72000, active: true },
  ],
};

const toon = encode(report);

// 解码回类型断言
const recovered = decode(toon) as EmployeeReport;
console.log(recovered.employees[0].name); // 'Alice'
```

### Express 中间件用于 TOON 内容类型

```typescript
import express from 'express';
import { encode, decode } from '@toon-format/toon';

const app = express();

// 解析传入的 TOON 正文
app.use((req, res, next) => {
  if (req.headers['content-type']?.startsWith('text/toon')) {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      try {
        (req as any).toonBody = decode(body);
        next();
      } catch (e) {
        res.status(400).json({ error: '无效的 TOON 正文' });
      }
    });
  } else {
    next();
  }
});

// 当客户端请求时返回 TOON
app.get('/api/employees', (req, res) => {
  const employees = [
    { id: 1, name: 'Alice', dept: 'Eng' },
    { id: 2, name: 'Bob', dept: 'Marketing' },
  ];

  if (req.headers.accept?.includes('text/toon')) {
    res.setHeader('Content-Type', 'text/toon; charset=utf-8');
    res.send(encode({ employees }));
  } else {
    res.json({ employees });
  }
});
```

## 何时使用 TOON 而不是 JSON

| 场景 | 建议 |
|---|---|
| 统一的对象数组 | ✅ TOON（最大的节省） |
| 深度嵌套 / 非统一 | ⚠️ 比较两者；JSON-紧凑可能更优 |
| 纯平面表格数据 | 考虑 CSV（更小）或 TOON（结构化） |
| 低延迟（本地模型） | 比较TTFT + 每秒令牌数 |
| 程序化 API 调用 | 保持 JSON；仅将 TOON 用于 LLM 输入 |
| 半统一（~40–60% 表格） | 比较测试；节省减少 |

## 故障排除

### 包含逗号的值解析错误

在 TOON 字符串中用双引号括起来，或确保 `encode()` 自动处理：

```typescript
// encode() 自动引用包含逗号的值
const data = { tags: ['hello, world', 'foo,bar'] };
encode(data);
// tags[2]: "hello, world","foo,bar"
```

### 往返类型丢失（数字 vs 字符串）

TOON 使用未加引号的值表示数字和布尔值。确保在编码前使用正确的 JS 类型 — 不要传递 `"95000"`（字符串）而应传递 `95000`（数字）：

```typescript
// ✅ 正确
{ salary: 95000, active: true }

// ❌ 将解码为字符串 "95000" 和字符串 "true"
{ salary: '95000', active: 'true' }
```

### LLM 误读表格行

在系统提示中添加简短的 TOON 格式说明：

```
TOON 格式规则:
- 缩进 = 嵌套对象
- key[N]: v1,v2,v3 = N 个标量值的数组
- key[N]{field1,field2}: 后跟 N 个缩进行 = 对象数组
```

### 命令行在全局安装后找不到

```bash
# 验证全局二进制路径是否在 PATH 中
npm bin -g   # 或: npm root -g

# 或者使用 npx
npx @toon-format/toon encode input.json
```

### 手写 TOON 解码失败

手写 TOON 常见错误：
- 缺少长度声明：`items{id,name}:` → 必须是 `items[2]{id,name}:`
- 缩进不一致（混合制表符/空格）
- 包含冒号作为第一个字符的未加引值

## 资源

- [官方规范（SPEC v3.0）](https://github.com/toon-format/spec/blob/main/SPEC.md)
- [npm 包：@toon-format/toon](https://www.npmjs.com/package/@toon-format/toon)
- [在线游乐场](https://toonformat.dev)
- [GitHub 仓库](https://github.com/toon-format/toon)
