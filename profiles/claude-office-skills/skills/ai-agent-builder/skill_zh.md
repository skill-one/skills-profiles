# AI Agent Builder

使用工具、记忆和多步骤推理能力设计和构建AI代理。涵盖基于n8n的5,000多个AI工作流模板的ChatGPT、Claude和Gemini集成模式。

## 概述

本技能涵盖：
- AI代理架构设计
- 工具/函数调用模式
- 记忆和上下文管理
- 多步骤推理工作流
- 平台集成（Slack、Telegram、Web）

---

## AI代理架构

### 核心组件

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI AGENT ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │   输入     │────▶│   Agent     │────▶│   输出    │       │
│  │  (查询)    │     │   (LLM)     │     │  (响应)    │       │
│  └─────────────┘     └──────┬──────┘     └─────────────┘       │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐              │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │   工具     │     │   记忆    │     │  知识  │       │
│  │ (函数)    │     │  (上下文)  │     │   (RAG)  │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 代理类型

```yaml
agent_types:
  reactive_agent:
    description: "单轮响应，无记忆"
    use_case: 简单问答，分类
    complexity: 低
    
  conversational_agent:
    description: "多轮对话带会话记忆"
    use_case: 聊天机器人，支持
    complexity: 中等
    
  tool_using_agent:
    description: "可以调用外部工具/API"
    use_case: 数据查询，操作
    complexity: 中等
    
  reasoning_agent:
    description: "多步骤规划和执行"
    use_case: 复杂任务，研究
    complexity: 高
    
  multi_agent:
    description: "多个专业代理协作"
    use_case: 复杂工作流
    complexity: 非常高
```

---

## 工具调用模式

### 工具定义

```yaml
tool_definition:
  name: "get_weather"
  description: "获取某个位置的当前天气"
  parameters:
    type: object
    properties:
      location:
        type: string
        description: "城市名称或坐标"
      units:
        type: string
        enum: ["celsius", "fahrenheit"]
        default: "celsius"
    required: ["location"]
    
  implementation:
    type: api_call
    endpoint: "https://api.weather.com/v1/current"
    method: GET
    params:
      q: "{location}"
      units: "{units}"
```

### 常见工具类别

```yaml
tool_categories:
  data_retrieval:
    - web_search: 搜索互联网
    - database_query: 查询SQL/NoSQL
    - api_lookup: 调用外部API
    - file_read: 读取文档
    
  actions:
    - send_email: 发送邮件
    - create_calendar: 安排事件
    - update_crm: 修改CRM记录
    - post_slack: 发送Slack消息
    
  computation:
    - calculator: 数学运算
    - code_interpreter: 运行Python
    - data_analysis: 分析数据集
    
  generation:
    - image_generation: 创建图像
    - document_creation: 生成文档
    - chart_creation: 创建可视化
```

### n8n工具集成

```yaml
n8n_agent_workflow:
  nodes:
    - trigger:
        type: webhook
        path: "/ai-agent"
        
    - ai_agent:
        type: "@n8n/n8n-nodes-langchain.agent"
        model: openai_gpt4
        system_prompt: |
          你是一个有帮助的助手，可以：
          1. 搜索互联网获取信息
          2. 查询我们的客户数据库
          3. 代表用户发送邮件
          
        tools:
          - web_search
          - database_query
          - send_email
          
    - respond:
        type: respond_to_webhook
        data: "{{ $json.output }}"
```

---

## 记忆模式

### 记忆类型

```yaml
memory_types:
  buffer_memory:
    description: "存储最近N条消息"
    implementation: |
      messages = []
      def add_message(role, content):
          messages.append({"role": role, "content": content})
          if len(messages) > MAX_MESSAGES:
              messages.pop(0)
    use_case: 简单聊天机器人
    
  summary_memory:
    description: "定期总结对话"
    implementation: |
      当messages > threshold:
          summary = llm.summarize(messages[:-5])
          messages = [summary_message] + messages[-5:]
    use_case: 长对话
    
  vector_memory:
    description: "存储在向量数据库中进行语义检索"
    implementation: |
      # 存储
      embedding = embed(message)
      vector_db.insert(embedding, message)
      
      # 检索
      relevant = vector_db.search(query_embedding, k=5)
    use_case: 知识检索
    
  entity_memory:
    description: "跟踪对话中提到的实体"
    implementation: |
      entities = {}
      def update_entities(message):
          extracted = llm.extract_entities(message)
          entities.update(extracted)
    use_case: 个性化助手
```

### 上下文窗口管理

```yaml
context_management:
  strategies:
    sliding_window:
      keep: last_n_messages
      n: 10
      
    relevance_based:
      method: embed_and_rank
      keep: top_k_relevant
      k: 5
      
    hierarchical:
      levels:
        - immediate: last_3_messages
        - recent: last_10的总结
        - long_term: 所有关键事实
        
  token预算:
    total: 8000
    system_prompt: 1000
    tools: 1000
    memory: 4000
    current_query: 1000
    response: 1000
```

---

## 多步骤推理

### ReAct模式

```
Thought: 我需要找到关于X的信息
Action: web_search("X")
Observation: [搜索结果]
Thought: 基于结果，我应该检查Y
Action: database_query("SELECT * FROM Y")
Observation: [数据库结果]
Thought: 现在我有足够的信息来回答
Action: respond("基于X和Y的最终答案")
```

### 规划代理

```yaml
planning_workflow:
  step_1_plan:
    prompt: |
      任务: {user_request}
      
      创建一个完成此任务的逐步计划。
      每个步骤应该是具体和可操作的。
      
    output: numbered_steps
    
  step_2_execute:
    for_each: step
    actions:
      - execute_step
      - validate_result
      - adjust_if_needed
      
  step_3_synthesize:
    prompt: |
      完成的步骤: {executed_steps}
      结果: {results}
      
      为用户综合一个最终响应。
```

---

## 平台集成

### Slack机器人代理

```yaml
slack_agent:
  trigger: slack_message
  
  workflow:
    1. receive_message:
        extract: [user, channel, text, thread_ts]
        
    2. get_context:
        if: thread_ts
        action: fetch_thread_history
        
    3. process_with_agent:
        model: gpt-4
        system: "你是一个有帮助的Slack助手"
        tools: [web_search, jira_lookup, calendar_check]
        
    4. respond:
        action: post_to_slack
        channel: "{channel}"
        thread_ts: "{thread_ts}"
        text: "{agent_response}"
```

### Telegram机器人代理

```yaml
telegram_agent:
  trigger: telegram_message
  
  handlers:
    text_message:
      - extract_text
      - process_with_ai
      - send_response
      
    voice_message:
      - transcribe_with_whisper
      - process_with_ai
      - send_text_or_voice_response
      
    image:
      - analyze_with_vision
      - process_with_ai
      - send_response
      
    document:
      - extract_content
      - process_with_ai
      - send_response
```

### Web聊天界面

```yaml
web_chat_agent:
  frontend:
    type: react_component
    features:
      - message_input
      - message_history
      - typing_indicator
      - file_upload
      
  backend:
    endpoint: "/api/chat"
    method: POST
    streaming: true
    
  session_management:
    method: jwt_token
    storage: redis
    ttl: 24_hours
```

---

## 代理模板

### 客户支持代理

```yaml
support_agent:
  name: "客户支持AI"
  model: gpt-4
  
  system_prompt: |
    你是{company}的客户支持代理。
    
    指南：
    - 要有帮助、专业和有同理心
    - 使用知识库回答问题
    - 如果不能帮助，升级到人工
    - 永远不要编造信息
    
    可用操作：
    - 搜索知识库
    - 查询客户账户
    - 创建支持工单
    - 升级到人工代理
    
  tools:
    - knowledge_search:
        description: "搜索帮助文章"
    - customer_lookup:
        description: "获取客户账户信息"
    - create_ticket:
        description: "创建支持工单"
    - escalate:
        description: "转接人工代理"
        
  升级触发器：
    - 情感：非常负面
    - 关键词：["和人工说话", "经理", "投诉"]
    - 失败解决：尝试3次后
```

### 研究代理

```yaml
research_agent:
  name: "研究助手"
  model: claude-opus
  
  system_prompt: |
    你是一个研究助手，帮助用户在任何主题上找到
    和综合信息。
    
    流程：
    1. 理解研究问题
    2. 规划搜索策略
    3. 执行跨多个来源的搜索
    4. 综合发现
    5. 带引用呈现
    
  tools:
    - web_search
    - academic_search
    - news_search
    - wikipedia_lookup
    
  output_format:
    - executive_summary
    - key_findings
    - detailed_analysis
    - sources_cited
```

---

## 输出示例

**请求**: "设计一个用于预约安排的AI代理"

**输出**:

```markdown
# 预约安排代理设计

## 架构

```yaml
agent:
  name: "Scheduling Assistant"
  model: gpt-4
  
  capabilities:
    - 检查日历可用性
    - 安排预约
    - 发送确认
    - 处理重新安排
    - 回答FAQ
```

## 需要的工具

1. **calendar_check**
   - 输入: date_range, duration
   - 输出: available_slots[]

2. **book_appointment**
   - 输入: datetime, customer_info, service_type
   - 输出: confirmation_id

3. **send_notification**
   - 输入: type, recipient, details
   - 输出: success/failure

4. **customer_lookup**
   - 输入: email或phone
   - 输出: customer_record

## 对话流程

```
User: "我想预约一个预约"
Agent: [Thought: 需要知道服务类型和首选时间]
Agent: "我很乐意帮忙！你在找什么服务，你首选的日期和时间是什么？"

User: "理发，下周二下午"
Agent: [Action: calendar_check(date="下周二", time="下午")]
Agent: "我下周二下午有2pm、3pm和4:30pm的空档。哪个最适合你？"

User: "3pm请"
Agent: [Action: book_appointment(datetime="下周二3pm", service="理发")]
Agent: [Action: send_notification(type="confirmation", ...)]
Agent: "你已安排下周二下午3pm的理发。我已发送确认邮件到你的邮箱。到时候见！"
```

## n8n实现

```yaml
workflow:
  - webhook_trigger: /schedule-chat
  - ai_agent:
      tools: [calendar, booking, notification]
  - respond_to_user
```
```

---

*AI Agent Builder技能 - 部分Claude Office技能*
