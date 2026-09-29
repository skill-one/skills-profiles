---
name: qianwen-update-check
description: "检查 qianwen-ai 更新，并在有新版本可用时通知用户。  \n触发条件：当用户要求检查更新、查询版本、询问“是否有新版本”、“最新版本”、“更新技能”、“检查更新”，或任何其他将 qwen 技能委托给此技能的情况，或用户通过名称显式调用此技能（例如使用 qianwen-update-check）。  \n不触发条件：非更新相关任务、关于其他软件的一般版本问题。"
---

# Qwen版本检查器

**QianWen-AI/qianwen-ai** 技能包的自动版本检查器。将本地安装版本与 GitHub 上的最新发布版本进行比较，并在有更新可用时通知用户。

所有其他 QianWen-AI/qianwen-ai 技能都会引用此技能。当任何技能运行时，它会检查此技能是否已安装，并将版本检查委托给此处。

## 工作原理

1. 从 `version.json`（随此技能捆绑的 `version` 字段）中读取安装版本。
2. 从远程仓库（GitHub 原始内容）获取最新版本。
3. 使用 semver 进行版本比较。如果存在更新版本，则返回 `{"has_update": true}`。
4. 在 `<repo_root>/.agents/state.json` 中记录检查时间戳（`last_interaction`），以限制网络请求每 24 小时一次。

## 使用方法

其他技能会自动调用此脚本。你也可以手动运行它：

```bash
python3 <此技能路径>/scripts/check_update.py --print-response
```

### 命令行参数

| 参数 | 描述 |
|------|------|
| `--print-response` | 将结果作为格式化的 JSON 打印到标准输出 |
| `--force` | 跳过 24 小时速率限制并立即检查 |

### 输出格式

```json
{
  "has_update": true
}
```

## 配置

| 环境变量 | 默认值 | 描述 |
|----------|--------|------|
| `QWEN_SKILLS_REPO` | `QianWen-AI/qianwen-ai` | 用于远程版本检查的 GitHub 仓库 |

## 状态文件

`last_interaction` 时间戳存储在 `<repo_root>/.agents/state.json` 中，用于速率限制。检查结果**不**在状态文件中缓存。此文件跨会话持久化，并与 `gossamer.py` 共享以进行疲劳控制。
