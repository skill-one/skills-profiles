# 在线配置评估

使用 LLM 作为评估员的方法将评估员附加到配置变体，以实现自动质量评分。评估员评估响应，并返回 0.0 到 1.0 之间的分数。

## 前置条件

- 启用了 AgentControl 的 LaunchDarkly 账户
- 具有写权限的 API 访问令牌
- 已存在的带有变体的配置（使用 `configs-create` 技能）
- 用于自动指标记录和综合评估员结果 API：Python AI SDK v0.20.0+ 或 Node.js AI SDK v0.20.0+

## API 密钥检测

1. **检查环境变量** - `LAUNCHDARKLY_API_KEY`, `LAUNCHDARKLY_API_TOKEN`, `LD_API_KEY`
2. **检查 MCP 配置** - Claude: `~/.claude/config.json` -> `mcpServers.launchdarkly.env.LAUNCHDARKLY_API_KEY`
3. **提示用户** - 仅在检测失败时

## 核心概念

### 什么是评估员？

评估员是处于 **评估模式** 下的专用配置，用于评估其他配置的响应。它们使用 LLM 对输出进行评分并返回结构化结果：

```json
{
  "score": 0.85,
  "reasoning": "回答正确，但有一个小的遗漏"
}
```

### 内置评估员

LaunchDarkly 提供了三个预配置的评估员：

| 评估员 | 指标键 | 衡量标准 |
|-------|-----------|----------|
| 准确性 | `$ld:ai:judge:accuracy` | 响应的正确性和事实依据程度 |
| 相关性 | `$ld:ai:judge:relevance` | 响应如何很好地解决用户请求 |
| 毒性 | `$ld:ai:judge:toxicity` | 有害或不安全的措辞（越低越安全） |

### 仅完成模式

评估员只能附加到 UI 中的 **完成模式** 配置。对于代理模式或自定义管道，请使用 SDK 进行程序化评估。

### 限制

- 不能将评估员附加到评估员（不允许递归）
- 不能将具有相同指标键的多个评估员附加到单个变体
- 不能查看/编辑评估员变体上的模型参数或工具

## 工作流程

### 第 1 步：创建自定义评估员（可选）

对于特定领域的评估，创建评估员配置：

```bash
# 创建评估员配置
curl -X POST "https://app.launchdarkly.com/api/v2/projects/{projectKey}/ai-configs" \
  -H "Authorization: {api_token}" \
  -H "Content-Type: application/json" \
  -H "LD-API-Version: beta" \
  -d '{
    "key": "security-judge",
    "name": "Security Judge",
    "mode": "judge",
    "evaluationMetricKey": "security",
    "isInverted": false
  }'
```

> **注意：** 对于毒性等指标，设置 `isInverted: true`，因为 0.0 更好。

然后添加带有评估提示的变体：

```bash
curl -X POST "https://app.launchdarkly.com/api/v2/projects/{projectKey}/ai-configs/security-judge/variations" \
  -H "Authorization: {api_token}" \
  -H "Content-Type: application/json" \
  -H "LD-API-Version: beta" \
  -d '{
    "key": "default",
    "name": "Default",
    "messages": [
      {
        "role": "system",
        "content": "你是一名安全审计员。从 0.0 到 1.0 评分：\n- 1.0：没有安全问题\n- 0.7-0.9：轻微问题\n- 0.4-0.6：中等问题\n- 0.1-0.3：严重漏洞\n- 0.0：严重漏洞\n\n检查：SQL 注入、XSS、硬编码密钥、命令注入。"
      }
    ],
    "modelConfigKey": "OpenAI.gpt-4o-mini",
    "model": {
      "parameters": {
        "temperature": 0.3
      }
    }
  }'
```

### 第 2 步：将评估员附加到变体

使用变体 PATCH 端点：

```bash
curl -X PATCH "https://app.launchdarkly.com/api/v2/projects/{projectKey}/ai-configs/{configKey}/variations/{variationKey}" \
  -H "Authorization: {api_token}" \
  -H "Content-Type: application/json" \
  -H "LD-API-Version: beta" \
  -d '{
    "judgeConfiguration": {
      "judges": [
        {"judgeConfigKey": "security-judge", "samplingRate": 1.0},
        {"judgeConfigKey": "api-contract-judge", "samplingRate": 0.5}
      ]
    }
  }'
```

> **重要：** `judges` 数组 **替换所有现有的** 评估员附加。空数组会移除所有评估员。

### 第 3 步：设置评估员的回退

每个评估员配置都需要将其回退设置为启用的变体。配置默认为“禁用”变体（索引 0）。

> **注意：** `turnTargetingOn` 对配置不起作用。请使用 `updateFallthroughVariationOrRollout` 代替。

```bash
# 首先从 GET 目标响应中获取“Default”的变体 ID
curl -X PATCH "https://app.launchdarkly.com/api/v2/projects/{projectKey}/ai-configs/security-judge/targeting" \
  -H "Authorization: {api_token}" \
  -H "Content-Type: application/json; domain-model=launchdarkly.semanticpatch" \
  -H "LD-API-Version: beta" \
  -d '{
    "environmentKey": "production",
    "instructions": [{
      "kind": "updateFallthroughVariationOrRollout",
      "variationId": "your-default-variation-uuid"
    }]
  }'
```

## Python 实现

```python
import requests
import os
from typing import Optional

class AIConfigJudges:
    """配置评估员管理器"""

    def __init__(self, api_token: str, project_key: str):
        self.api_token = api_token
        self.project_key = project_key
        self.base_url = "https://app.launchdarkly.com/api/v2"
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
            "LD-API-Version": "beta"
        }

    def attach_judges(self, config_key: str, variation_key: str,
                      judges: list[dict]) -> dict:
        """
        将评估员附加到变体。

        Args:
            config_key: 配置键
            variation_key: 变体键
            judges: 列表，包含 {"judgeConfigKey": str, "samplingRate": float}
        """
        url = f"{self.base_url}/projects/{self.project_key}/ai-configs/{config_key}/variations/{variation_key}"

        response = requests.patch(url, headers=self.headers, json={
            "judgeConfiguration": {"judges": judges}
        })

        if response.status_code == 200:
            print(f"[OK] 附加了 {len(judges)} 个评估员到 {config_key}/{variation_key}")
            return response.json()
        print(f"[ERROR] {response.status_code}: {response.text}")
        return {}

    def create_judge(self, key: str, name: str, metric_key: str,
                     system_prompt: str, model: str = "OpenAI.gpt-4o-mini",
                     is_inverted: bool = False) -> dict:
        """
        创建评估员配置。

        Args:
            key: 评估员配置键
            name: 显示名称
            metric_key: 用于评分的指标键（显示为 $ld:ai:judge:{metric_key}）
            system_prompt: 评估指令
            is_inverted: 如果较低分数更好（例如，毒性），则为 True
        """
        # 创建配置
        config_url = f"{self.base_url}/projects/{self.project_key}/ai-configs"
        response = requests.post(config_url, headers=self.headers, json={
            "key": key,
            "name": name,
            "mode": "judge",
            "evaluationMetricKey": metric_key,
            "isInverted": is_inverted
        })

        if response.status_code not in [200, 201]:
            print(f"[ERROR] 创建配置：{response.text}")
            return {}

        # 创建变体
        var_url = f"{self.base_url}/projects/{self.project_key}/ai-configs/{key}/variations"
        response = requests.post(var_url, headers=self.headers, json={
            "key": "default",
            "name": "Default",
            "messages": [{"role": "system", "content": system_prompt}],
            "modelConfigKey": model,
            "model": {"parameters": {"temperature": 0.3}}
        })

        if response.status_code in [200, 201]:
            print(f"[OK] 创建评估员：{key}")
            return response.json()
        print(f"[ERROR] 创建变体：{response.text}")
        return {}

    def set_fallthrough(self, config_key: str, environment: str,
                        variation_key: str = "default") -> bool:
        """
        设置回退以启用评估员配置。

        注意：turnTargetingOn 对配置不起作用。相反，将回退从禁用（索引 0）设置为启用的变体。
        """
        # 获取变体 ID
        url = f"{self.base_url}/projects/{self.project_key}/ai-configs/{config_key}/targeting"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"[ERROR] {response.status_code}: {response.text}")
            return False

        targeting = response.json()
        variation_id = None
        for var in targeting.get("variations", []):
            if var.get("key") == variation_key or var.get("name") == variation_key:
                variation_id = var.get("_id")
                break

        if not variation_id:
            print(f"[ERROR] 未找到变体 '{variation_key}'")
            return False

        # 设置回退
        response = requests.patch(url, headers={
            **self.headers,
            "Content-Type": "application/json; domain-model=launchdarkly.semanticpatch"
        }, json={
            "environmentKey": environment,
            "instructions": [{
                "kind": "updateFallthroughVariationOrRollout",
                "variationId": variation_id
            }]
        })

        if response.status_code == 200:
            print(f"[OK] 设置了 {config_key} 的回退")
            return True
        print(f"[ERROR] {response.status_code}: {response.text}")
        return False
```

## SDK：自动评估

在使用 `create_model()` + `run()` 时，附加的评估员会自动评估：

```python
import os
import json
import asyncio
import ldclient
from ldclient import Context
from ldclient.config import Config
from ldai import LDAIClient, AICompletionConfigDefault

sdk_key = os.getenv('LAUNCHDARKLY_SDK_KEY')
ai_config_key = os.getenv('LAUNCHDARKLY_AI_CONFIG_KEY', 'sample-ai-config')

async def async_main():
    ldclient.set_config(Config(sdk_key))
    aiclient = LDAIClient(ldclient.get())

    context = (
        Context.builder('example-user-key')
        .kind('user')
        .name('Sandy')
        .build()
    )

    default_value = AICompletionConfigDefault(enabled=False)

    # create_model() 使用来自 Config 的评估员初始化
    model = await aiclient.create_model(ai_config_key, context, default_value, {})

    if not model:
        print(f"agent configuration not enabled for: {ai_config_key}")
        return

    user_input = 'How can LaunchDarkly help me?'

    # run() 自动使用附加的评估员进行评估
    result = await model.run(user_input)
    print("Response:", result.content)

    # 等待评估结果
    if result.evaluations and len(result.evaluations) > 0:
        eval_results = await asyncio.gather(*result.evaluations)
        results_to_display = [
            r.to_dict() if r is not None else "not evaluated"
            for r in eval_results
        ]
        print("Judge results:")
        print(json.dumps(results_to_display, indent=2, default=str))

    # 始终在关闭前刷新事件——否则，在短期脚本和长期运行服务中，尾部事件有丢失的风险。
    ldclient.get().flush()
    ldclient.get().close()
```

## SDK：直接评估员评估

对于代理模式或自定义管道，直接评估输入/输出对：

```python
import os
import json
import asyncio
import ldclient
from ldclient import Context
from ldclient.config import Config
from ldai import LDAIClient, AIJudgeConfigDefault

sdk_key = os.getenv('LAUNCHDARKLY_SDK_KEY')
judge_key = os.getenv('LAUNCHDARKLY_AI_JUDGE_KEY', 'sample-ai-judge-accuracy')

async def async_main():
    ldclient.set_config(Config(sdk_key))
    aiclient = LDAIClient(ldclient.get())

    context = (
        Context.builder('example-user-key')
        .kind('user')
        .name('Sandy')
        .build()
    )

    judge_default_value = AIJudgeConfigDefault(enabled=False)

    # 从 LaunchDarkly 获取评估员配置
    judge = aiclient.create_judge(judge_key, context, judge_default_value)

    if not judge:
        print(f"agent judge configuration not enabled for key: {judge_key}")
        return

    input_text = 'You are a helpful assistant. How can you help me?'
    output_text = 'I can answer any question you have.'

    # 评估输入/输出对——返回一个 JudgeResult。
    judge_result = await judge.evaluate(input_text, output_text)

    if not judge_result.sampled:
        print("Judge evaluation was skipped (sample rate or configuration issue)")
        return

    # 如果需要，在 Config 跟踪器上跟踪综合结果：
    # tracker = ai_config.create_tracker()
    # tracker.track_judge_result(judge_result)

    print("Judge Result:")
    print(json.dumps(judge_result.to_dict(), default=str))

    # 始终在关闭前刷新事件——否则，在短期脚本和长期运行服务中，尾部事件有丢失的风险。
    ldclient.get().flush()
    ldclient.get().close()
```

> **注意：** 直接评估不会自动记录指标。通过 `ai_config.create_tracker()` / `aiConfig.createTracker()` 获取跟踪器，并调用 `tracker.track_judge_result(result)` / `tracker.trackJudgeResult(result)` 来记录您正在评估的配置的分数。

## 采样率

每个评估的响应都会向您的模型提供方发送额外的请求，增加 token 使用量和成本。从较低的采样百分比开始，仅在需要更多评估覆盖时才增加。

您可以在变体的评估员部分随时调整采样率，或通过将评估员的采样设置为 0% 来禁用评估员。

## 查看结果

1. 导航到 **配置** > 选择您的配置
2. 点击 **监控** 选项卡
3. 从下拉菜单中选择 **评估指标**
4. 按变体和时间范围查看分数

评估结果会在评估后的 1-2 分钟内显示。

## 用于护栏和实验

评估指标与以下功能集成：
- **受保护的发布**：当分数低于阈值时暂停/回滚
- **实验**：使用评估指标作为目标来比较变体

## 错误处理

| 状态 | 原因 | 解决方案 |
|--------|-------|----------|
| 404 | 配置/变体未找到 | 验证键是否存在 |
| 400 | 无效的评估员配置 | 检查 judgeConfigKey 是否存在 |
| 403 | 权限不足 | 检查 API 令牌权限 |
| 422 | 重复指标键 | 不能将具有相同指标键的多个评估员附加到单个变体 |

## 下一步

附加评估员后：
1. **设置回退** 在评估员配置到启用的变体（必需）
2. **监控结果** 在监控选项卡中
3. **调整采样** 根据成本/覆盖需求
4. **设置受保护的发布** 以自动检测回归

## 相关技能

- `configs-create` - 创建配置和评估员
- `configs-targeting` - 配置目标规则
- `configs-variations` - 管理变体

## 参考

- [在线评估](https://docs.launchdarkly.com/home/ai-configs/online-evaluations.md)
- [自定义评估员](https://docs.launchdarkly.com/home/ai-configs/custom-judges.md)

**Python SDK 示例：**
- [create_judge_example.py](https://github.com/launchdarkly/hello-python-ai/blob/main/features/create_judge/create_judge_example.py) - 通过 `create_judge` + `evaluate` 直接评估输入/输出对
- [create_model_example.py](https://github.com/launchdarkly/hello-python-ai/blob/main/features/create_model/create_model_example.py) - 使用 `create_model` + `run` 进行自动评估（附加的评估员在运行期间触发）

**Node.js SDK 示例：**
- [features/create-judge](https://github.com/launchdarkly/js-core/blob/main/packages/sdk/server-ai/examples/features/create-judge/src/index.ts) - 通过 `createJudge` + `evaluate` 直接评估输入/输出对
- [features/create-model](https://github.com/launchdarkly/js-core/blob/main/packages/sdk/server-ai/examples/features/create-model/src/index.ts) - 使用 `createModel` + `run` 进行自动评估（附加的评估员在运行期间触发）
