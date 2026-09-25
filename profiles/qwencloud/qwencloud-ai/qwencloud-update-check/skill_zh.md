# Qwen版本检查器

**qwencloud/qwencloud-ai** 技能包的自动版本检查器。将本地安装的版本与 GitHub 上的最新发布版本进行比较，并在有更新可用时通知用户。

所有其他 qwencloud/qwencloud-ai 都引用此技能。当任何技能运行时，它会检查此技能是否已安装，并将版本检查委托给此处。

## 工作原理

1. 从 `version.json` 中读取已安装版本（随此技能捆绑的 `version` 字段）。
2. 从远程仓库（GitHub 原始内容）获取最新版本。
3. 使用 semver 比较版本。如果存在更新的版本，则返回 `{"has_update": true}`。
4. 在 `<repo_root>/.agents/state.json` 中记录检查时间戳 (`last_interaction`)，以限制网络请求每小时最多一次。

## 使用方法

其他技能会自动调用此脚本。你也可以手动运行它：

```bash
python3 <此技能的路径>/scripts/check_update.py --print-response
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
| `QWEN_SKILLS_REPO` | `qwencloud/qwencloud-ai` | 用于远程版本检查的 GitHub 仓库 |

## 状态文件

`last_interaction` 时间戳存储在 `<repo_root>/.agents/state.json` 中，用于速率限制。检查结果**不**在状态文件中缓存。此文件跨会话持久化，并与 `gossamer.py` 共享，用于疲劳控制。
