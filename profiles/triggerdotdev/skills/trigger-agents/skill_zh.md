# 使用 Trigger.dev 构建 AI 代理模式

利用 Trigger.dev 的持久化执行构建生产就绪的 AI 代理。

## 模式选择

```
需要...                                  → 使用
─────────────────────────────────────────────────────
并行处理项目                           → 并行化
路由到不同的模型/处理器                 → 路由
带验证门的步骤链式执行                 → 提示链式执行
协调多个专业任务                     → 协调器-工作器
自我改进直至质量阈值                 → 评估器-优化器
暂停等待人工批准                     → 人机回路（waitpoints.md）
向前端实时流式传输进度             → 实时流式传输（streaming.md）
让 LLM 将您的任务作为工具调用        → ai.tool（ai-tool.md）
```

---

## 核心模式

### 1. 提示链式执行（带门的顺序执行）

在步骤之间链式调用 LLM 并进行验证。如果中间输出有误，则提前失败。

```typescript
import { task } from "@trigger.dev/sdk";
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

export const translateCopy = task({
  id: "translate-copy",
  run: async ({ text, targetLanguage, maxWords }) => {
    // 步骤 1：生成
    const draft = await generateText({
      model: openai("gpt-4o"),
      prompt: `撰写关于：${text} 的营销文案`,
    });

    // 门：验证后继续
    const wordCount = draft.text.split(/\s+/).length;
    if (wordCount > maxWords) {
      throw new Error(`草稿过长：${wordCount} > ${maxWords}`);
    }

    // 步骤 2：翻译（仅当门通过时）
    const translated = await generateText({
      model: openai("gpt-4o"),
      prompt: `翻译到 ${targetLanguage}：${draft.text}`,
    });

    return { draft: draft.text, translated: translated.text };
  },
});
```

---

### 2. 路由（分类→分发）

使用一个廉价模型进行分类，然后路由到适当的处理器。

```typescript
import { task } from "@trigger.dev/sdk";
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const routingSchema = z.object({
  model: z.enum(["gpt-4o", "o1-mini"]),
  reason: z.string(),
});

export const routeQuestion = task({
  id: "route-question",
  run: async ({ question }) => {
    // 廉价分类调用
    const routing = await generateText({
      model: openai("gpt-4o-mini"),
      messages: [
        {
          role: "system",
          content: `分类问题复杂度。返回 JSON：{"model": "gpt-4o" | "o1-mini", "reason": "..."}
          - gpt-4o：简单事实性问题
          - o1-mini：复杂推理、数学、代码`,
        },
        { role: "user", content: question },
      ],
    });

    const { model } = routingSchema.parse(JSON.parse(routing.text));

    // 路由到选定的模型
    const answer = await generateText({
      model: openai(model),
      prompt: question,
    });

    return { answer: answer.text, routedTo: model };
  },
});
```

---

### 3. 并行化

使用 `batch.triggerByTaskAndWait` 同时运行独立的 LLM 调用。

```typescript
import { batch, task } from "@trigger.dev/sdk";

export const analyzeContent = task({
  id: "analyze-content",
  run: async ({ text }) => {
    // 三个全部并行运行
    const { runs: [sentiment, summary, moderation] } = await batch.triggerByTaskAndWait([
      { task: analyzeSentiment, payload: { text } },
      { task: summarizeText, payload: { text } },
      { task: moderateContent, payload: { text } },
    ]);

    // 首先检查内容审核
    if (moderation.ok && moderation.output.flagged) {
      return { error: "内容被标记", reason: moderation.output.reason };
    }

    return {
      sentiment: sentiment.ok ? sentiment.output : null,
      summary: summary.ok ? summary.output : null,
    };
  },
});
```

**参见：** `references/orchestration.md` 了解高级模式

---

### 4. 协调器-工作器（扇出/扇入）

协调器提取工作项，扇出到工作器，聚合结果。

```typescript
import { batch, task } from "@trigger.dev/sdk";

export const factChecker = task({
  id: "fact-checker",
  run: async ({ article }) => {
    // 步骤 1：提取声明（顺序执行 - 需要先输出）
    const { runs: [extractResult] } = await batch.triggerByTaskAndWait([
      { task: extractClaims, payload: { article } },
    ]);

    if (!extractResult.ok) throw new Error("提取声明失败");
    const claims = extractResult.output;

    // 步骤 2：扇出 - 并行验证所有声明
    const { runs } = await batch.triggerByTaskAndWait(
      claims.map(claim => ({ task: verifyClaim, payload: claim }))
    );

    // 步骤 3：扇入 - 聚合结果
    const verified = runs
      .filter((r): r is typeof r & { ok: true } => r.ok)
      .map(r => r.output);

    return { claims, verifications: verified };
  },
});
```

---

### 5. 评估器-优化器（自我改进循环）

生成→评估→带反馈重试直至批准。

```typescript
import { task } from "@trigger.dev/sdk";

export const refineTranslation = task({
  id: "refine-translation",
  run: async ({ text, targetLanguage, feedback, attempt = 0 }) => {
    // 退出条件
    if (attempt >= 5) {
      return { text, status: "MAX_ATTEMPTS", attempts: attempt };
    }

    // 生成（重试时带反馈）
    const prompt = feedback
      ? `根据反馈改进此翻译：\n${feedback}\n\n原文：${text}`
      : `翻译到 ${targetLanguage}：${text}`;

    const translation = await generateText({
      model: openai("gpt-4o"),
      prompt,
    });

    // 评估
    const evaluation = await generateText({
      model: openai("gpt-4o"),
      prompt: `评估翻译质量。回复 APPROVED 或提供具体反馈：\n${translation.text}`,
    });

    if (evaluation.text.includes("APPROVED")) {
      return { text: translation.text, status: "APPROVED", attempts: attempt + 1 };
    }

    // 带反馈的递归自我调用
    return refineTranslation.triggerAndWait({
      text,
      targetLanguage,
      feedback: evaluation.text,
      attempt: attempt + 1,
    }).unwrap();
  },
});
```

---

## Trigger 特有功能

| 功能       | 它能实现什么     | 参考       |
|---------|-----------------|-----------|
| **Waitpoints** | 人工批准门、外部回调 | `references/waitpoints.md` |
| **Streams**   | 向前端实时传输进度 | `references/streaming.md` |
| **ai.tool**   | 让 LLM 调用您的任务作为工具 | `references/ai-tool.md` |
| **batch.triggerByTaskAndWait** | 带类型的并行执行 | `references/orchestration.md` |

---

## 错误处理

```typescript
const { runs } = await batch.triggerByTaskAndWait([...]);

// 检查单个结果
for (const run of runs) {
  if (run.ok) {
    console.log(run.output);  // 带类型的输出
  } else {
    console.error(run.error);  // 错误详情
    console.log(run.taskIdentifier);  // 哪个任务失败
  }
}

// 或按任务类型过滤
const verifications = runs
  .filter((r): r is typeof r & { ok: true } =>
    r.ok && r.taskIdentifier === "verify-claim"
  )
  .map(r => r.output);
```

---

## 快速参考

```typescript
// 触发并等待结果
const result = await myTask.triggerAndWait(payload);
if (result.ok) console.log(result.output);

// 批量触发相同任务
const results = await myTask.batchTriggerAndWait([
  { payload: item1 },
  { payload: item2 },
]);

// 批量触发不同任务（带类型）
const { runs } = await batch.triggerByTaskAndWait([
  { task: taskA, payload: { foo: 1 } },
  { task: taskB, payload: { bar: "x" } },
]);

// 带 unwrap 的自我递归
return myTask.triggerAndWait(newPayload).unwrap();
```
