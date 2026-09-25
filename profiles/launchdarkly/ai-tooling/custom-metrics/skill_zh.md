# 自定义指标配置

全面管理自定义业务指标：通过 API 创建指标定义，通过 SDK 追踪事件，检索指标数据，并编程管理指标。

## 前置条件

- 已初始化 LaunchDarkly SDK（参见 `sdk`）
- 具有指标管理权限（`writer` 角色）的 LaunchDarkly API 令牌
- 了解内置代理指标（参见 `built-in-metrics`）

## API 密钥检测

在提示用户输入 API 密钥之前，尝试自动检测：

1. **检查 Claude MCP 配置** - 读取 `~/.claude/config.json` 并查找 `mcpServers.launchdarkly.env.LAUNCHDARKLY_API_KEY`
2. **检查环境变量** - 查找 `LAUNCHDARKLY_API_KEY`、`LAUNCHDARKLY_API_TOKEN` 或 `LD_API_KEY`
3. **提示用户** - 仅当检测失败时，才询问用户的 API 密钥

```python
import os
import json
from pathlib import Path

def get_launchdarkly_api_key():
    """从 Claude 配置或环境自动检测 LaunchDarkly API 密钥"""
    # 1. 检查 Claude MCP 配置
    claude_config = Path.home() / ".claude" / "config.json"
    if claude_config.exists():
        try:
            config = json.load(open(claude_config))
            api_key = config.get("mcpServers", {}).get("launchdarkly", {}).get("env", {}).get("LAUNCHDARKLY_API_KEY")
            if api_key:
                return api_key
        except (json.JSONDecodeError, IOError):
            pass

    # 2. 检查环境变量
    for var in ["LAUNCHDARKLY_API_KEY", "LAUNCHDARKLY_API_TOKEN", "LD_API_KEY"]:
        if os.environ.get(var):
            return os.environ[var]

    return None
```

## 指标生命周期概述

| 步骤 | 方法 | 目的 |
|------|------|------|
| 1. 创建 | API | 在 LaunchDarkly 中定义指标 |
| 2. 追踪 | SDK | 向指标发送事件 |
| 3. 获取 | API | 检索指标定义/数据 |
| 4. 更新 | API | 修改指标属性 |
| 5. 删除 | API | 删除指标 |

## 1. 创建指标（API）

**数值型自定义指标的必填字段：**
- `successCriteria` - 必须为：`"HigherThanBaseline"`、`"LowerThanBaseline"`
- `unit` - 例如：`"count"`、`"percent"`、`"milliseconds"`

如果数值型指标缺少这些字段，API 将返回 `400 Bad Request`。

```python
import requests
import os

def create_metric(
    project_key: str,
    metric_key: str,
    name: str,
    kind: str = "custom",
    is_numeric: bool = True,
    unit: str = "count",
    success_criteria: str = "HigherThanBaseline",
    event_key: str = None,
    description: str = None
):
    """在 LaunchDarkly 中创建新的指标定义"""
    API_TOKEN = os.environ.get("LAUNCHDARKLY_API_TOKEN")

    url = f"https://app.launchdarkly.com/api/v2/metrics/{project_key}"

    payload = {
        "key": metric_key,
        "name": name,
        "kind": kind,
        "isNumeric": is_numeric,
        "eventKey": event_key or metric_key
    }

    # 对于数值型自定义指标，`unit` 和 `successCriteria` 是必填的
    if is_numeric and kind == "custom":
        payload["unit"] = unit
        payload["successCriteria"] = success_criteria

    if description:
        payload["description"] = description

    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print(f"[OK] 创建指标：{metric_key}")
        return response.json()
    elif response.status_code == 409:
        print(f"[INFO] 指标已存在：{metric_key}")
        return None
    else:
        print(f"[ERROR] 创建指标失败：{response.status_code}")
        print(f"        {response.text}")
        return None
```

**指标类型：**
- `custom` - 追踪任何事件（代理指标最常用）
- `pageview` - 追踪页面浏览量
- `click` - 追踪点击事件

**成功标准**（用于数值型指标）：
- `HigherThanBaseline` - 较高的值更好（例如收入、满意度）
- `LowerThanBaseline` - 较低的值更好（例如错误、延迟）

**常用单位：**
- `count` - 通用计数
- `milliseconds` - 时间持续时间
- `percent` - 百分比值
- `dollars` - 货币

## 2. 追踪事件（SDK）

创建指标后，使用 SDK 追踪事件：

```python
from ldclient import Context
from ldclient.config import Config
import ldclient

# 初始化（参见 `sdk` 的详细信息）
ldclient.set_config(Config("your-sdk-key"))
ld_client = ldclient.get()

def track_metric(ld_client, user_id: str, metric_key: str, value: float, data: dict = None):
    """向指标追踪事件"""
    context = Context.builder(user_id).build()

    ld_client.track(
        metric_key,
        context,
        data=data,
        metric_value=value
    )
```

### 常见追踪模式

```python
def track_conversion(ld_client, user_id: str, amount: float, config_key: str):
    """追踪带收入的转化事件"""
    context = Context.builder(user_id).build()

    ld_client.track(
        "business.conversion",
        context,
        data={"configKey": config_key, "category": "electronics"},
        metric_value=amount
    )

def track_task_success(ld_client, user_id: str, task_type: str, success: bool):
    """追踪任务完成成功/失败"""
    context = Context.builder(user_id).build()

    ld_client.track(
        "task.success_rate",
        context,
        data={"taskType": task_type},
        metric_value=1.0 if success else 0.0
    )

def track_satisfaction(ld_client, user_id: str, score: float, feedback_type: str):
    """追踪用户满意度（0-100 分制）"""
    context = Context.builder(user_id).build()

    ld_client.track(
        "user.satisfaction",
        context,
        data={"feedbackType": feedback_type},
        metric_value=score
    )

    # 为警报单独追踪负面反馈
    if score < 50:
        ld_client.track(
            "user.negative_feedback",
            context,
            metric_value=1.0
        )

def track_revenue(ld_client, user_id: str, revenue: float, source: str):
    """追踪代理交互后的收入"""
    context = Context.builder(user_id).set("tier", "premium").build()

    if revenue > 0:
        ld_client.track(
            "revenue.impact",
            context,
            data={"source": source},
            metric_value=revenue
        )
```

## 3. 获取指标（API）

### 获取单个指标

```python
def get_metric(project_key: str, metric_key: str):
    """获取单个指标定义"""
    API_TOKEN = os.environ.get("LAUNCHDARKLY_API_TOKEN")

    url = f"https://app.launchdarkly.com/api/v2/metrics/{project_key}/{metric_key}"

    headers = {"Authorization": API_TOKEN}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        metric = response.json()
        print(f"[OK] 指标：{metric['key']}")
        print(f"     名称：{metric.get('name', 'N/A')}")
        print(f"     类型：{metric.get('kind', 'N/A')}")
        print(f"     数值型：{metric.get('isNumeric', False)}")
        print(f"     事件键：{metric.get('eventKey', 'N/A')}")
        return metric
    elif response.status_code == 404:
        print(f"[INFO] 未找到指标：{metric_key}")
        return None
    else:
        print(f"[ERROR] 获取指标失败：{response.status_code}")
        return None
```

### 列出所有指标

```python
def list_metrics(project_key: str, limit: int = 20):
    """列出项目中的所有指标"""
    API_TOKEN = os.environ.get("LAUNCHDARKLY_API_TOKEN")

    url = f"https://app.launchdarkly.com/api/v2/metrics/{project_key}"

    headers = {"Authorization": API_TOKEN}
    params = {"limit": limit}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        metrics = data.get("items", [])
        print(f"[OK] 找到 {len(metrics)} 个指标：")
        for metric in metrics:
            numeric = "数值型" if metric.get("isNumeric") else "非数值型"
            print(f"     - {metric['key']} ({metric.get('kind', 'custom')}, {numeric})")
        return metrics
    else:
        print(f"[ERROR] 列出指标失败：{response.status_code}")
        return None
```

## 4. 更新指标（API）

```python
def update_metric(project_key: str, metric_key: str, updates: list):
    """
    使用 JSON Patch 操作更新指标。

    Args:
        updates: 补丁操作列表，例如：
            [{"op": "replace", "path": "/name", "value": "新名称"}]
    """
    API_TOKEN = os.environ.get("LAUNCHDARKLY_API_TOKEN")

    url = f"https://app.launchdarkly.com/api/v2/metrics/{project_key}/{metric_key}"

    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.patch(url, json=updates, headers=headers)

    if response.status_code == 200:
        print(f"[OK] 更新指标：{metric_key}")
        return response.json()
    elif response.status_code == 404:
        print(f"[ERROR] 未找到指标：{metric_key}")
        return None
    else:
        print(f"[ERROR] 更新指标失败：{response.status_code}")
        print(f"        {response.text}")
        return None

# 示例：更新指标名称和描述
def rename_metric(project_key: str, metric_key: str, new_name: str, new_description: str = None):
    """重命名指标并可选更新描述"""
    updates = [
        {"op": "replace", "path": "/name", "value": new_name}
    ]
    if new_description:
        updates.append({"op": "replace", "path": "/description", "value": new_description})

    return update_metric(project_key, metric_key, updates)
```

## 5. 删除指标（API）

```python
def delete_metric(project_key: str, metric_key: str):
    """从项目中删除指标"""
    API_TOKEN = os.environ.get("LAUNCHDARKLY_API_TOKEN")

    url = f"https://app.launchdarkly.com/api/v2/metrics/{project_key}/{metric_key}"

    headers = {"Authorization": API_TOKEN}

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f"[OK] 删除指标：{metric_key}")
        return True
    elif response.status_code == 404:
        print(f"[INFO] 未找到指标：{metric_key}")
        return False
    else:
        print(f"[ERROR] 删除指标失败：{response.status_code}")
        return False
```

## 完整工作流示例

```python
import os
import requests
from ldclient import Context
from ldclient.config import Config
import ldclient

# 设置
API_TOKEN = os.environ.get("LAUNCHDARKLY_API_TOKEN")
SDK_KEY = os.environ.get("LAUNCHDARKLY_SDK_KEY")
PROJECT_KEY = "support-ai"

ldclient.set_config(Config(SDK_KEY))
ld_client = ldclient.get()

# 1. 创建指标
create_metric(
    PROJECT_KEY,
    "ai.task.completion",
    name="代理任务完成率",
    kind="custom",
    is_numeric=True,
    description="追踪成功的代理任务完成"
)

# 2. 追踪事件
context = Context.builder("user-123").build()
ld_client.track("ai.task.completion", context, metric_value=1.0)
ld_client.track("ai.task.completion", context, metric_value=1.0)
ld_client.track("ai.task.completion", context, metric_value=0.0)  # 失败
ld_client.flush()

# 3. 获取指标定义
metric = get_metric(PROJECT_KEY, "ai.task.completion")

# 4. 更新指标名称
rename_metric(PROJECT_KEY, "ai.task.completion", "代理任务成功率")

# 5. 列出所有指标
list_metrics(PROJECT_KEY)

# 6. 删除指标（当不再需要时）
# delete_metric(PROJECT_KEY, "ai.task.completion")
```

## 会话指标追踪器

```python
import time
from ldclient import Context

class SessionMetricsTracker:
    """跨整个用户会话追踪指标"""

    def __init__(self, ld_client):
        self.ld_client = ld_client
        self.session_data = {}

    def start_session(self, user_id: str, session_id: str):
        """初始化会话追踪"""
        self.session_data[session_id] = {
            "user_id": user_id,
            "start_time": time.time(),
            "interactions": 0,
            "successful_tasks": 0
        }

    def track_interaction(self, session_id: str, success: bool):
        """追踪会话内的单个交互"""
        if session_id not in self.session_data:
            return
        session = self.session_data[session_id]
        session["interactions"] += 1
        if success:
            session["successful_tasks"] += 1

    def end_session(self, session_id: str):
        """最终化并追踪会话指标"""
        if session_id not in self.session_data:
            return None

        session = self.session_data[session_id]
        duration = time.time() - session["start_time"]

        context = Context.builder(session["user_id"]).build()

        # 追踪会话持续时间
        self.ld_client.track(
            "session.duration",
            context,
            data={"interactions": session["interactions"]},
            metric_value=duration
        )

        # 追踪会话成功率
        if session["interactions"] > 0:
            success_rate = session["successful_tasks"] / session["interactions"]
            self.ld_client.track(
                "session.success_rate",
                context,
                metric_value=success_rate * 100
            )

        result = dict(session)
        result["duration"] = duration
        del self.session_data[session_id]
        return result
```

## 命名规范

```python
# 使用点表示法表示层级
"quality.accuracy"
"quality.relevance"
"user.satisfaction"
"user.engagement"
"revenue.conversion"
"task.success_rate"
"session.duration"
"ai.task.completion"
"ai.recommendation.conversion"
```

## 最佳实践

1. **先创建后追踪** - 指标必须存在才能追踪事件
2. **使用数值型指标** - 设置 `isNumeric=True` 以便聚合
3. **保持键一致** - 在 `create_metric()` 和 `ld_client.track()` 中使用相同的键
4. **始终在关闭前刷新** - 在 `ld_client.flush()`（Node 中为 `await`）和 `close()` 之前调用。否则，在短生命周期脚本和长时间运行的服务中，尾随事件有丢失的风险。这不是仅限无服务器环境的规则；它适用于任何退出进程。
5. **避免高频追踪** - 不要在每次按键时都追踪

## 查看指标

自定义指标出现在：
- LaunchDarkly UI 中的 **指标** 页面
- 您配置的 **监控** 选项卡
- 通过 API 使用 `get_metric()` 或 `list_metrics()` 获取

## 相关技能

- `sdk` - SDK 设置
- `built-in-metrics` - 内置代理指标（令牌、持续时间、成本）
- `online-evals` - 通过裁判器获取质量指标

## 参考

- [指标 API 文档](https://apidocs.launchdarkly.com/tag/Metrics)
- [自定义事件文档](https://docs.launchdarkly.com/sdk/features/events)
- [Python SDK track() 参考](https://launchdarkly-python-sdk.readthedocs.io/)
