# 上下文窗口管理

管理大型语言模型（LLM）上下文窗口的策略，包括摘要、裁剪、路由和避免上下文陈旧

## 功能

- 上下文工程
- 上下文摘要
- 上下文裁剪
- 上下文路由
- token计数
- 上下文优先级

## 前置条件

- 知识：LLM基础、分词基础、提示工程
- 推荐技能：提示工程

## 范围

- 不涵盖：RAG实现细节、模型微调、嵌入模型
- 边界：专注于上下文优化，涵盖策略而非特定实现

## 生态系统

### 主要工具

- tiktoken - OpenAI的分词器，用于计数token
- LangChain - 具备上下文管理工具的框架
- Claude API - 支持200K+上下文和缓存

## 模式

### 分层上下文策略

根据上下文大小采用不同策略

**何时使用**：构建任何多轮对话系统

```typescript
interface ContextTier {
    maxTokens: number;
    strategy: 'full' | 'summarize' | 'rag';
    model: string;
}

const TIERS: ContextTier[] = [
    { maxTokens: 8000, strategy: 'full', model: 'claude-3-haiku' },
    { maxTokens: 32000, strategy: 'full', model: 'claude-3-5-sonnet' },
    { maxTokens: 100000, strategy: 'summarize', model: 'claude-3-5-sonnet' },
    { maxTokens: Infinity, strategy: 'rag', model: 'claude-3-5-sonnet' }
];

async function selectStrategy(messages: Message[]): ContextTier {
    const tokens = await countTokens(messages);

    for (const tier of TIERS) {
        if (tokens <= tier.maxTokens) {
            return tier;
        }
    }
    return TIERS[TIERS.length - 1];
}

async function prepareContext(messages: Message[]): PreparedContext {
    const tier = await selectStrategy(messages);

    switch (tier.strategy) {
        case 'full':
            return { messages, model: tier.model };

        case 'summarize':
            const summary = await summarizeOldMessages(messages);
            return { messages: [summary, ...recentMessages(messages)], model: tier.model };

        case 'rag':
            const relevant = await retrieveRelevant(messages);
            return { messages: [...relevant, ...recentMessages(messages)], model: tier.model };
    }
}
```

### 顺序位置优化

将重要内容放置在开头和结尾

**何时使用**：构建具有显著上下文的提示

```typescript
// LLMs更重视开头和结尾
// 构建提示以利用这一特性

function buildOptimalPrompt(components: {
    systemPrompt: string;
    criticalContext: string;
    conversationHistory: Message[];
    currentQuery: string;
}): string {
    // 开头：系统指令（始终最先）
    const parts = [components.systemPrompt];

    // 关键上下文：系统指令后立即放置（高优先级）
    if (components.criticalContext) {
        parts.push(`## 关键上下文\n${components.criticalContext}`);
    }

    // 中间：对话历史（较低权重）
    // 如果过长则摘要，保留最近消息
    const history = components.conversationHistory;
    if (history.length > 10) {
        const oldSummary = summarize(history.slice(0, -5));
        const recent = history.slice(-5);
        parts.push(`## 早期对话（摘要）\n${oldSummary}`);
        parts.push(`## 最近消息\n${formatMessages(recent)}`);
    } else {
        parts.push(`## 对话\n${formatMessages(history)}`);
    }

    // 结尾：当前查询（高时效性）
    // 在此处重申关键要求
    parts.push(`## 当前请求\n${components.currentQuery}`);

    // 最终：提醒关键约束
    parts.push(`记住：${extractKeyConstraints(components.systemPrompt)}`);

    return parts.join('\n\n');
}
```

### 智能摘要

按重要性而非时效性摘要

**何时使用**：上下文超过最佳大小

```typescript
interface MessageWithMetadata extends Message {
    importance: number;  // 0-1分数
    hasCriticalInfo: boolean;  // 用户偏好、决策
    referenced: boolean;  // 后面是否引用了这条消息？
}

async function smartSummarize(
    messages: MessageWithMetadata[],
    targetTokens: number
): Message[] {
    // 按重要性排序，相同分数保持顺序
    const sorted = [...messages].sort((a, b) =>
        (b.importance + (b.hasCriticalInfo ? 0.5 : 0) + (b.referenced ? 0.3 : 0)) -
        (a.importance + (a.hasCriticalInfo ? 0.5 : 0) + (a.referenced ? 0.3 : 0))
    );

    const keep: Message[] = [];
    const summarizePool: Message[] = [];
    let currentTokens = 0;

    for (const msg of sorted) {
        const msgTokens = await countTokens([msg]);
        if (currentTokens + msgTokens < targetTokens * 0.7) {
            keep.push(msg);
            currentTokens += msgTokens;
        } else {
            summarizePool.push(msg);
        }
    }

    // 摘要低重要性消息
    if (summarizePool.length > 0) {
        const summary = await llm.complete(`
            摘要这些消息，保留：
            - 任何用户偏好或决策
            - 可能被后续引用的关键事实
            - 对话的整体流程

            消息：
            ${formatMessages(summarizePool)}
        `);

        keep.unshift({ role: 'system', content: `[早期上下文：${summary}]` });
    }

    // 恢复原始顺序
    return keep.sort((a, b) => a.timestamp - b.timestamp);
}
```

### token预算分配

在上下文组件间分配token预算

**何时使用**：需要可预测的上下文管理

```typescript
interface TokenBudget {
    system: number;      // 系统提示
    criticalContext: number;  // 用户偏好、关键信息
    history: number;     // 对话历史
    query: number;       // 当前查询
    response: number;    // 预留用于响应
}

function allocateBudget(totalTokens: number): TokenBudget {
    return {
        system: Math.floor(totalTokens * 0.10),      // 10%
        criticalContext: Math.floor(totalTokens * 0.15),  // 15%
        history: Math.floor(totalTokens * 0.40),     // 40%
        query: Math.floor(totalTokens * 0.10),       // 10%
        response: Math.floor(totalTokens * 0.25),    // 25%
    };
}

async function buildWithBudget(
    components: ContextComponents,
    modelMaxTokens: number
): PreparedContext {
    const budget = allocateBudget(modelMaxTokens);

    // 裁剪/摘要每个组件以适应预算
    const prepared = {
        system: truncateToTokens(components.system, budget.system),
        criticalContext: truncateToTokens(
            components.criticalContext, budget.criticalContext
        ),
        history: await summarizeToTokens(components.history, budget.history),
        query: truncateToTokens(components.query, budget.query),
    };

    // 重新分配未使用的预算
    const used = await countTokens(Object.values(prepared).join('\n'));
    const remaining = modelMaxTokens - used - budget.response;

    if (remaining > 0) {
        // 额外分配给历史（对对话最有价值）
        prepared.history = await summarizeToTokens(
            components.history,
            budget.history + remaining
        );
    }

    return prepared;
}
```

## 验证检查

### 无token计数

严重性：警告

消息：在发送上下文时不进行token计数。可能超出模型限制。

修复操作：发送前计数token，实现预算分配

### 简单消息裁剪

严重性：警告

消息：未摘要即裁剪消息。关键上下文可能丢失。

修复操作：摘要旧消息而不是简单删除

### 硬编码token限制

严重性：信息

消息：硬编码token限制。考虑按模型进行可配置。

修复操作：使用配置中的模型特定限制

### 无上下文管理策略

严重性：警告

消息：无上下文管理策略的LLM调用。

修复操作：实现上下文管理：预算、摘要或RAG

## 协作

### 授权触发器

- retrieval|rag|search -> rag-implementation (需要检索系统)
- memory|persistence|remember -> conversation-memory (需要内存存储)
- cache|caching -> prompt-caching (需要缓存优化)

### 完整上下文系统

技能：上下文窗口管理、rag-implementation、conversation-memory、prompt-caching

工作流程：

```
1. 设计上下文策略
2. 实现RAG用于大型语料库
3. 设置内存持久化
4. 添加缓存以提升性能
```

## 相关技能

与：`rag-implementation`、`conversation-memory`、`prompt-caching`、`llm-npc-dialogue` 配合使用

## 何时使用
- 用户提及或暗示：上下文窗口
- 用户提及或暗示：token限制
- 用户提及或暗示：上下文管理
- 用户提及或暗示：上下文工程
- 用户提及或暗示：长上下文
- 用户提及或暗示：上下文溢出

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必需的输入、权限、安全边界或成功标准，请停止并请求澄清。
