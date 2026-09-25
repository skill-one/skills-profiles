# 配置目标定位

配置配置的目标定位规则，以控制哪些变体服务于不同的上下文。完成模式和代理模式都使用相同的方式。

## 前置条件

- 启用了 AgentControl 的 LaunchDarkly 账户
- 具有写权限的 API 访问令牌
- 项目密钥和环境密钥
- 具有变体的现有配置（使用 `configs-create` 技能）

## API 密钥检测

1. **检查环境变量** - `LAUNCHDARKLY_API_KEY`、`LAUNCHDARKLY_API_TOKEN`、`LD_API_KEY`
2. **检查 MCP 配置** - Claude: `~/.claude/config.json` -> `mcpServers.launchdarkly.env.LAUNCHDARKLY_API_KEY`
3. **提示用户** - 仅在检测失败时

## 核心概念

### 评估顺序

目标定位规则按以下顺序评估（与功能标志相同）：

1. **单个目标** - 特定的上下文键（最高优先级）
2. **分段规则** - 预定义的分段
3. **自定义规则** - 基于属性的条件（按顺序评估）
4. **默认规则** - 所有其他情况的回退
5. **关闭变体** - 当目标定位被禁用时

### 语义补丁 API

配置目标定位使用语义补丁指令：

```
PATCH /api/v2/projects/{projectKey}/ai-configs/{configKey}/targeting
Content-Type: application/json; domain-model=launchdarkly.semanticpatch
```

### 关键概念

- **variationId**: UUID，不是键。始终先获取目标定位以获取 ID。
- **Weights**: 千分之一（50000 = 50%，100000 = 100%）
- **子句逻辑**: 多个子句 = AND，多个值 = OR
- **Null 属性**: 具有 null/缺失属性的规则会被跳过

## 工作流程

### 第 1 步：获取目标定位（包含变体 ID）

```bash
curl -X GET "https://app.launchdarkly.com/api/v2/projects/{projectKey}/ai-configs/{configKey}/targeting" \
  -H "Authorization: {api_token}" \
  -H "LD-API-Version: beta"
```

响应包含 `variations` 数组，其中包含每个变体的 `_id`（UUID）。

### 第 2 步：编辑默认规则

编辑默认规则以服务您创建的变体。

> **重要提示**：`turnTargetingOn` 指令对配置无效。请使用 `updateFallthroughVariationOrRollout` 代替。

```bash
# 首先，从第 1 步响应中获取变体 ID
# 然后，将回退设置为启用的变体（例如，“默认”变体）
curl -X PATCH "https://app.launchdarkly.com/api/v2/projects/{projectKey}/ai-configs/{configKey}/targeting" \
  -H "Authorization: {api_token}" \
  -H "Content-Type: application/json; domain-model=launchdarkly.semanticpatch" \
  -H "LD-API-Version: beta" \
  -d '{
    "environmentKey": "production",
    "instructions": [{
      "kind": "updateFallthroughVariationOrRollout",
      "variationId": "your-enabled-variation-uuid"
    }]
  }'
```

### 第 3 步：添加目标定位规则

**基于属性的规则：**

```bash
curl -X PATCH "https://app.launchdarkly.com/api/v2/projects/{projectKey}/ai-configs/{configKey}/targeting" \
  -H "Authorization: {api_token}" \
  -H "Content-Type: application/json; domain-model=launchdarkly.semanticpatch" \
  -H "LD-API-Version: beta" \
  -d '{
    "environmentKey": "production",
    "instructions": [{
      "kind": "addRule",
      "clauses": [{
        "contextKind": "user",
        "attribute": "selectedModel",
        "op": "contains",
        "values": ["sonnet"],
        "negate": false
      }],
      "variation": 0
    }]
  }'
```

**百分比发布：**

```bash
curl -X PATCH "..." \
  -d '{
    "environmentKey": "production",
    "instructions": [{
      "kind": "addRule",
      "clauses": [{
        "contextKind": "user",
        "attribute": "tier",
        "op": "in",
        "values": ["premium"],
        "negate": false
      }],
      "percentageRolloutConfig": {
        "contextKind": "user",
        "bucketBy": "key",
        "variations": [
          {"variation": 0, "weight": 60000},
          {"variation": 1, "weight": 40000}
        ]
      }
    }]
  }'
```

**设置回退（默认规则）：**

```bash
curl -X PATCH "..." \
  -d '{
    "environmentKey": "production",
    "instructions": [{
      "kind": "updateFallthroughVariationOrRollout",
      "variationId": "fallback-variation-uuid"
    }]
  }'
```

## Python 实现

```python
import requests
import os
from typing import Dict, List, Optional

class AIConfigTargeting:
    """配置目标定位规则的管理器"""

    def __init__(self, api_token: str, project_key: str):
        self.api_token = api_token
        self.project_key = project_key
        self.base_url = "https://app.launchdarkly.com/api/v2"

    def get_targeting(self, config_key: str) -> Optional[Dict]:
        """获取当前目标定位，包含变体 ID。"""
        url = f"{self.base_url}/projects/{self.project_key}/ai-configs/{config_key}/targeting"

        response = requests.get(url, headers={
            "Authorization": self.api_token,
            "LD-API-Version": "beta"
        })

        if response.status_code == 200:
            return response.json()
        print(f"[ERROR] {response.status_code}: {response.text}")
        return None

    def get_variation_id(self, config_key: str, variation_key: str) -> Optional[str]:
        """从键或名称查找变体 UUID。"""
        targeting = self.get_targeting(config_key)
        if targeting:
            for var in targeting.get("variations", []):
                if var.get("key") == variation_key or var.get("name") == variation_key:
                    return var.get("_id")
        return None

    def update_targeting(self, config_key: str, environment: str,
                         instructions: List[Dict], comment: str = "") -> Optional[Dict]:
        """发送语义补丁指令。"""
        url = f"{self.base_url}/projects/{self.project_key}/ai-configs/{config_key}/targeting"

        payload = {"environmentKey": environment, "instructions": instructions}
        if comment:
            payload["comment"] = comment

        response = requests.patch(url, headers={
            "Authorization": self.api_token,
            "Content-Type": "application/json; domain-model=launchdarkly.semanticpatch",
            "LD-API-Version": "beta"
        }, json=payload)

        if response.status_code == 200:
            return response.json()
        print(f"[ERROR] {response.status_code}: {response.text}")
        return None

    def enable_config(self, config_key: str, environment: str,
                      variation_key: str = "default") -> bool:
        """
        通过将回退设置为启用的变体来启用配置。

        注意：turnTargetingOn 对配置无效。相反，从禁用的变体（索引 0）设置回退到启用的变体。
        """
        variation_id = self.get_variation_id(config_key, variation_key)
        if not variation_id:
            print(f"[ERROR] 未找到变体 '{variation_key}'")
            return False
        return self.set_fallthrough(config_key, environment, variation_id)

    def add_rule(self, config_key: str, environment: str,
                 clauses: List[Dict], variation: int,
                 description: str = "") -> bool:
        """添加服务特定变体索引的目标定位规则。"""
        instruction = {
            "kind": "addRule",
            "clauses": clauses,
            "variation": variation
        }
        if description:
            instruction["description"] = description

        result = self.update_targeting(config_key, environment,
            [instruction], f"添加规则：{description}")
        if result:
            print(f"[OK] 规则已添加")
            return True
        return False

    def add_rollout_rule(self, config_key: str, environment: str,
                         clauses: List[Dict],
                         weights: List[Dict],
                         bucket_by: str = "key") -> bool:
        """
        添加百分比发布规则。

        weights: [{"variation": 0, "weight": 50000}, {"variation": 1, "weight": 50000}]
        """
        result = self.update_targeting(config_key, environment, [{
            "kind": "addRule",
            "clauses": clauses,
            "percentageRolloutConfig": {
                "contextKind": "user",
                "bucketBy": bucket_by,
                "variations": weights
            }
        }], "添加百分比发布")
        if result:
            print(f"[OK] 发布规则已添加")
            return True
        return False

    def set_fallthrough(self, config_key: str, environment: str,
                        variation_id: str) -> bool:
        """通过 UUID 设置默认（回退）变体。"""
        result = self.update_targeting(config_key, environment, [{
            "kind": "updateFallthroughVariationOrRollout",
            "variationId": variation_id
        }], "设置回退")
        if result:
            print(f"[OK] 回退已设置")
            return True
        return False

    def target_individuals(self, config_key: str, environment: str,
                          context_keys: List[str], variation: int,
                          context_kind: str = "user") -> bool:
        """定位特定的上下文键。"""
        result = self.update_targeting(config_key, environment, [{
            "kind": "addTargets",
            "variation": variation,
            "contextKind": context_kind,
            "values": context_keys
        }], f"添加 {len(context_keys)} 个个体目标")
        if result:
            print(f"[OK] 个体目标已添加")
            return True
        return False

    def target_segment(self, config_key: str, environment: str,
                      segment_keys: List[str], variation: int) -> bool:
        """定位分段。"""
        result = self.update_targeting(config_key, environment, [{
            "kind": "addRule",
            "clauses": [{
                "attribute": "segmentMatch",
                "contextKind": "",  # 留空表示分段
                "op": "segmentMatch",
                "values": segment_keys,
                "negate": False
            }],
            "variation": variation
        }], f"定位分段：{segment_keys}")
        if result:
            print(f"[OK] 分段目标定位已添加")
            return True
        return False

    def clear_rules(self, config_key: str, environment: str) -> bool:
        """删除所有目标定位规则。"""
        result = self.update_targeting(config_key, environment,
            [{"kind": "replaceRules", "rules": []}], "清除所有规则")
        if result:
            print(f"[OK] 所有规则已清除")
            return True
        return False
```

## 指令参考

> **注意**：`turnTargetingOn` 和 `turnTargetingOff` 对配置无效。配置默认启用目标定位。要“启用”配置，请使用 `updateFallthroughVariationOrRollout` 将回退设置为启用的变体。

### 规则
| 类型 | 描述 |
|------|------|
| `addRule` | 添加具有子句和变体/发布的规则 |
| `removeRule` | 通过规则 ID 删除 |
| `replaceRules` | 替换所有规则 |
| `reorderRules` | 更改评估顺序 |
| `updateRuleVariationOrRollout` | 更新规则服务的内容 |

### 回退
| 类型 | 描述 |
|------|------|
| `updateFallthroughVariationOrRollout` | 设置默认变体或发布 |

### 个体目标
| 类型 | 描述 |
|------|------|
| `addTargets` | 定位特定的上下文键 |
| `removeTargets` | 删除特定目标 |
| `replaceTargets` | 替换所有目标 |

## 运算符参考

| 运算符 | 描述 | 示例 |
|--------|------|------|
| `in` | 值在列表中 | `["premium", "enterprise"]` |
| `contains` | 字符串包含 | `["sonnet"]` |
| `startsWith` | 字符串前缀 | `["user-"]` |
| `endsWith` | 字符串后缀 | `[".edu"]` |
| `matches` | 正则表达式匹配 | `["^user-\\d+$"]` |
| `greaterThan` / `lessThan` | 数值比较 | `[100]` |
| `before` / `after` | 日期比较 | `["2024-12-31T00:00:00Z"]` |
| `semVerEqual` / `semVerGreaterThan` | 版本比较 | `["2.0.0"]` |
| `segmentMatch` | 分段成员资格 | `["beta-testers"]` |

## 子句结构

```json
{
  "contextKind": "user",
  "attribute": "email",
  "op": "endsWith",
  "values": [".edu"],
  "negate": false
}
```

- 多个子句 = AND（所有必须匹配）
- 多个值 = OR（任何一个都可以匹配）
- `negate: true` 会反转运算符

## 发布类型

### 手动百分比发布
```json
{
  "percentageRolloutConfig": {
    "contextKind": "user",
    "bucketBy": "key",
    "variations": [
      {"variation": 0, "weight": 50000},
      {"variation": 1, "weight": 50000}
    ]
  }
}
```

### 渐进式发布
```json
{
  "progressiveRolloutConfig": {
    "contextKind": "user",
    "controlVariation": 1,
    "endVariation": 0,
    "steps": [
      {"rolloutWeight": 1000, "duration": {"quantity": 4, "unit": "hour"}},
      {"rolloutWeight": 5000, "duration": {"quantity": 4, "unit": "hour"}},
      {"rolloutWeight": 10000, "duration": {"quantity": 4, "unit": "hour"}}
    ]
  }
}
```

### 受保护发布
```json
{
  "guardedRolloutConfig": {
    "randomizationUnit": "user",
    "stages": [
      {"rolloutWeight": 1000, "monitoringWindowMilliseconds": 17280000},
      {"rolloutWeight": 5000, "monitoringWindowMilliseconds": 17280000}
    ],
    "metrics": [{
      "metricKey": "error-rate",
      "onRegression": {"rollback": true},
      "regressionThreshold": 0.01
    }]
  }
}
```

## 常见模式

### 基于属性的模型路由
```python
# 基于selectedModel上下文属性进行路由
targeting.add_rule(
    config_key="model-selector",
    environment="production",
    clauses=[{
        "contextKind": "user",
        "attribute": "selectedModel",
        "op": "contains",
        "values": ["sonnet"],
        "negate": False
    }],
    variation=0,  # Sonnet 变体索引
    description="路由 sonnet 请求"
)
```

### 基于层级的变体
```python
targeting.add_rule(
    config_key="chat-assistant",
    environment="production",
    clauses=[{
        "contextKind": "user",
        "attribute": "tier",
        "op": "in",
        "values": ["premium", "enterprise"],
        "negate": False
    }],
    variation=0  # 高级模型变体
)
```

### 分段定位
```python
targeting.target_segment(
    config_key="chat-assistant",
    environment="production",
    segment_keys=["beta-testers"],
    variation=1  # 实验性变体
)
```

## 错误处理

| 状态 | 原因 | 解决方案 |
|------|------|------|
| 400 | 无效的语义补丁 | 检查指令格式，ops 必须为小写 |
| 403 | 权限不足 | 检查 API 令牌 |
| 404 | 配置未找到 | 验证 projectKey 和 configKey |
| 422 | 无效的变体 | 使用索引（0、1、2...）或从目标定位响应中获取 UUID |

## 下一步

配置目标定位后：

1. **提供配置 URL**：
   ```
   https://app.launchdarkly.com/projects/{projectKey}/ai-configs/{configKey}
   ```
2. **使用 `built-in-metrics` 监控性能**
3. **使用 `online-evals` 附加裁判**
4. **设置受保护发布**以进行自动回归检测

## 相关技能

- `configs-create` - 创建具有变体的配置
- `configs-variations` - 管理变体
- `online-evals` - 附加裁判
- `segments` - 创建用于定位的分段

## 其他资源

- [使用 AgentControl 进行定位](https://docs.launchdarkly.com/home/ai-configs/target.md)
- [定位规则](https://docs.launchdarkly.com/home/flags/target-rules.md)
- [JSON 定位](https://docs.launchdarkly.com/home/flags/json-targeting.md)
- [受保护发布](https://docs.launchdarkly.com/home/releases/guarded-rollouts.md)
