# Promptfoo 评估

## 概述

此技能提供配置和运行 LLM 评估的指导，使用 [Promptfoo](https://www.promptfoo.dev/)，一个用于测试和比较 LLM 输出的开源 CLI 工具。

## 快速入门

```bash
# 初始化一个新的评估项目
npx promptfoo@latest init

# 运行评估
npx promptfoo@latest eval

# 在浏览器中查看结果
npx promptfoo@latest view
```

## 配置结构

一个典型的 Promptfoo 项目结构：

```
project/
├── promptfooconfig.yaml    # 主配置文件
├── prompts/
│   ├── system.md           # 系统提示
│   └── chat.json           # 聊天格式提示
├── tests/
│   └── cases.yaml          # 测试用例
└── scripts/
    └── metrics.py          # 自定义 Python 断言
```

## 核心配置 (promptfooconfig.yaml)

```yaml
# yaml-language-server: $schema=https://promptfoo.dev/config-schema.json
description: "我的 LLM 评估"

# 要测试的提示
prompts:
  - file://prompts/system.md
  - file://prompts/chat.json

# 要比较的模型
providers:
  - id: anthropic:messages:claude-sonnet-4-6
    label: Claude-Sonnet-4.6
  - id: openai:gpt-4.1
    label: GPT-4.1

# 测试用例
tests: file://tests/cases.yaml

# 并发控制 (MUST be under commandLineOptions, NOT top-level)
commandLineOptions:
  maxConcurrency: 2

# 所有测试的默认断言
defaultTest:
  assert:
    - type: python
      value: file://scripts/metrics.py:custom_assert
    - type: llm-rubric
      value: |
        基于以下标准评估响应质量：0-1 分制。
      threshold: 0.7

# 输出路径
outputPath: results/eval-results.json
```

## 提示格式

### 文本提示 (system.md)

```markdown
你是一个有帮助的助手。

任务：{{task}}
上下文：{{context}}
```

### 聊天格式 (chat.json)

```json
[
  {"role": "system", "content": "{{system_prompt}}"},
  {"role": "user", "content": "{{user_input}}"}
]
```

### 少样本模式

直接在提示中嵌入示例，或使用聊天格式并包含助手消息：

```json
[
  {"role": "system", "content": "{{system_prompt}}"},
  {"role": "user", "content": "示例输入：{{example_input}}"},
  {"role": "assistant", "content": "{{example_output}}"},
  {"role": "user", "content": "现在处理：{{actual_input}}"}
]
```

## 测试用例 (tests/cases.yaml)

```yaml
- description: "测试用例 1"
  vars:
    system_prompt: file://prompts/system.md
    user_input: "Hello world"
    # 从文件加载内容
    context: file://data/context.txt
  assert:
    - type: contains
      value: "expected text"
    - type: python
      value: file://scripts/metrics.py:custom_check
      threshold: 0.8
```

## Python 自定义断言

创建一个 Python 文件用于自定义断言（例如，`scripts/metrics.py`）：

```python
def get_assert(output: str, context: dict) -> dict:
    """默认断言函数。"""
    vars_dict = context.get('vars', {})

    # 访问测试变量
    expected = vars_dict.get('expected', '')

    # 返回结果
    return {
        "pass": expected in output,
        "score": 0.8,
        "reason": "包含预期内容",
        "named_scores": {"relevance": 0.9}
    }

def custom_check(output: str, context: dict) -> dict:
    """自定义命名断言。"""
    word_count = len(output.split())
    passed = 100 <= word_count <= 500

    return {
        "pass": passed,
        "score": min(1.0, word_count / 300),
        "reason": f"单词数：{word_count}"
    }
```

**要点：**
- 默认函数名是 `get_assert`
- 使用 `file://path.py:function_name` 指定函数
- 返回 `bool`、`float`（分数）或包含 `pass`/`score`/`reason` 的 `dict`
- 通过 `context['vars']` 访问变量

## LLM-as-Judge (llm-rubric)

```yaml
assert:
  - type: llm-rubric
    value: |
      基于以下标准评估响应：
      1. 信息准确性
      2. 解释清晰度
      3. 完整性

      0.0-1.0 分制，0.7+ 为通过。
    threshold: 0.7
    provider: openai:gpt-4.1  # 可选：覆盖评分模型
```

**当使用中继/代理 API 时**，每个 `llm-rubric` 断言都需要其自己的 `provider` 配置，包含 `apiBaseUrl`。否则评分器会回退到默认的 Anthropic/OpenAI 端点，并出现 401 错误：

```yaml
assert:
  - type: llm-rubric
    value: |
      在 0-1 分制上评估质量。
    threshold: 0.7
    provider:
      id: anthropic:messages:claude-sonnet-4-6
      config:
        apiBaseUrl: https://your-relay.example.com/api  # Promptfoo 会自动追加 /v1/messages
```

**最佳实践：**
- 提供清晰的评分标准
- 使用 `threshold` 设置最低通过分数
- 默认评分器使用可用的 API 密钥（OpenAI → Anthropic → Google）
- **使用中继/代理时**：每个 `llm-rubric` 必须有自己的 `provider` 和 `apiBaseUrl` — 主 `provider` 的 `apiBaseUrl` 不会被继承

## 常用断言类型

| 类型 | 用法 | 示例 |
|------|-------|-------|
| `contains` | 检查子字符串 | `value: "hello"` |
| `icontains` | 不区分大小写 | `value: "HELLO"` |
| `equals` | 精确匹配 | `value: "42"` |
| `regex` | 模式匹配 | `value: "\\d{4}"` |
| `python` | 自定义逻辑 | `value: file://script.py` |
| `llm-rubric` | LLM 评分 | `value: "Is professional"` |
| `latency` | 响应时间 | `threshold: 1000` |

## 文件引用

所有 `file://` 路径都相对于 `promptfooconfig.yaml` 的位置解析（不是包含引用的 YAML 文件）。这是一个常见陷阱，当 `tests:` 引用一个单独的 YAML 文件时 — 该测试文件中的 `file://` 路径仍然从配置根目录解析。

```yaml
# 从文件加载内容作为变量
vars:
  content: file://data/input.txt

# 从文件加载提示
prompts:
  - file://prompts/main.md

# 从文件加载测试用例
tests: file://tests/cases.yaml

# 从文件加载 Python 断言
assert:
  - type: python
    value: file://scripts/check.py:validate
```

## 运行评估

```bash
# 基本运行
npx promptfoo@latest eval

# 使用特定配置
npx promptfoo@latest eval --config path/to/config.yaml

# 输出到文件
npx promptfoo@latest eval --output results.json

# 过滤测试
npx promptfoo@latest eval --filter-metadata category=math

# 查看结果
npx promptfoo@latest view
```

## 中继/代理 API 配置

当使用中继或代理 API 而不是直接 Anthropic/OpenAI 端点时：

```yaml
providers:
  - id: anthropic:messages:claude-sonnet-4-6
    label: Claude-Sonnet-4.6
    config:
      max_tokens: 4096
      apiBaseUrl: https://your-relay.example.com/api  # Promptfoo 会自动追加 /v1/messages

# 关键：maxConcurrency 必须在 commandLineOptions 下 (NOT top-level)
commandLineOptions:
  maxConcurrency: 1  # 尊重中继速率限制
```

**关键规则：**
- `apiBaseUrl` 放在 `providers[].config` 中 — Promptfoo 会自动追加 `/v1/messages`
- `maxConcurrency` 必须在 `commandLineOptions:` 下 — 放在顶层会被静默忽略
- 使用中继时，设置 `maxConcurrency: 1` 以避免并发请求限制（生成和评分共享同一池）
- 将中继令牌作为 `ANTHROPIC_API_KEY` 环境变量传递

## 故障排除

**Python 未找到：**
```bash
export PROMPTFOO_PYTHON=python3
```

**大输出被截断：**
超过 30000 个字符的输出会被截断。在断言中使用 `head_limit`。

**文件未找到错误：**
所有 `file://` 路径都相对于 `promptfooconfig.yaml` 的位置解析。

**maxConcurrency 被忽略（显示 "up to N at a time"）：**
`maxConcurrency` 必须在 `commandLineOptions:` 下，而不是 YAML 顶层。这是一个常见错误。

**LLM-as-judge 使用中继 API 返回 401：**
每个 `llm-rubric` 断言必须有自己的 `provider` 和 `apiBaseUrl`。主 `provider` 配置不会被继承给评分器断言。

**模型输出中的 HTML 标签导致指标膨胀：**
模型可能会在结构化内容中输出 `<br>`、`<b>` 等。在 Python 断言中移除 HTML 后再测量：
```python
import re
clean_text = re.sub(r'<[^>]+>', '', raw_text)
```

## 回声提供者 (预览模式)

使用 **回声提供者** 来预览渲染后的提示，而无需进行 API 调用：

```yaml
# promptfooconfig-preview.yaml
providers:
  - echo  # 返回提示作为输出，不进行 API 调用

tests:
  - vars:
      input: "test content"
```

**用例：**
- 在昂贵 API 调用前预览提示渲染
- 验证 Few-shot 示例是否正确加载
- 调试变量替换问题
- 验证提示结构

```bash
# 运行预览模式
npx promptfoo@latest eval --config promptfooconfig-preview.yaml
```

**成本：** 免费 — 不消耗 API 令牌。

## 高级 Few-Shot 实现

### 多轮对话模式

用于复杂少样本学习的完整示例：

```json
[
  {"role": "system", "content": "{{system_prompt}}"},

  // 少样本示例 1
  {"role": "user", "content": "任务：{{example_input_1}}"},
  {"role": "assistant", "content": "{{example_output_1}}"},

  // 少样本示例 2 (可选)
  {"role": "user", "content": "任务：{{example_input_2}}"},
  {"role": "assistant", "content": "{{example_output_2}}"},

  // 实际测试
  {"role": "user", "content": "任务：{{actual_input}}"}
]
```

**测试用例配置：**

```yaml
tests:
  - vars:
      system_prompt: file://prompts/system.md
      # 少样本示例
      example_input_1: file://data/examples/input1.txt
      example_output_1: file://data/examples/output1.txt
      example_input_2: file://data/examples/input2.txt
      example_output_2: file://data/examples/output2.txt
      # 实际测试
      actual_input: file://data/test1.txt
```

**最佳实践：**
- 使用 1-3 个少样本示例（更多可能会降低效果）
- 确保示例与任务格式完全匹配
- 从文件加载示例以实现更好的可维护性
- 首先使用回声提供者验证结构

## 长文本处理

用于中文/长文本内容评估（10k+ 字符）：

**配置：**

```yaml
providers:
  - id: anthropic:messages:claude-sonnet-4-6
    config:
      max_tokens: 8192  # 增加以处理长输出

defaultTest:
  assert:
    - type: python
      value: file://scripts/metrics.py:check_length
```

**Python 断言用于文本指标：**

```python
import re

def strip_tags(text: str) -> str:
    """移除 HTML 标签以获取纯文本。"""
    return re.sub(r'<[^>]+>', '', text)

def check_length(output: str, context: dict) -> dict:
    """检查输出长度约束。"""
    raw_input = context['vars'].get('raw_input', '')

    input_len = len(strip_tags(raw_input))
    output_len = len(strip_tags(output))

    reduction_ratio = 1 - (output_len / input_len) if input_len > 0 else 0

    return {
        "pass": 0.7 <= reduction_ratio <= 0.9,
        "score": reduction_ratio,
        "reason": f"缩减：{reduction_ratio:.1%} (目标：70-90%)",
        "named_scores": {
            "input_length": input_len,
            "output_length": output_len,
            "reduction_ratio": reduction_ratio
        }
    }
```

## 真实案例

**项目：** 从长文本中生成中文短视频内容

**结构：**
```
tiaogaoren/
├── promptfooconfig.yaml          # 生产配置
├── promptfooconfig-preview.yaml  # 预览配置 (回声提供者)
├── prompts/
│   ├── tiaogaoren-prompt.json   # 聊天格式，包含少样本
│   └── v4/system-v4.md          # 系统提示
├── tests/cases.yaml              # 3 个测试样本
├── scripts/metrics.py            # 自定义指标 (缩减率等)
├── data/                         # 5 个样本 (2 个少样本，3 个评估)
└── results/
```

**参见：** `./tiaogaoren/` (示例项目根目录) 以获取完整实现。

## 资源

有关详细的 API 参考和高级模式，请参阅 [references/promptfoo_api.md](references/promptfoo_api.md)。
