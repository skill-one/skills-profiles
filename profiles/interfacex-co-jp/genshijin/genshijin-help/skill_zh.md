# genshijin 帮助

调用时显示此参考卡片。仅限一次 — 禁止模式更改、标志写入、状态持久化。输出为原始人模式。

## 强度等级

| 等级 | 触发器 | 更改内容 |
|------|--------|--------|
| **礼貌** | `/genshijin 礼貌` | 删除缓冲词和模糊处理。保持敬语。文末句号。商务简洁体 |
| **通常** | `/genshijin` | 落下敬语体言。可省略助词。关键词空格分隔。默认 |
| **极限** | `/genshijin 极限` | 无视日语语法。仅关键词。多用缩写。箭头因果 X→Y。最小句号 |

等级切换前或会话结束时保持。

## 子技能

| 技能 | 触发器 | 内容 |
|------|--------|------|
| **genshijin-commit** | `/genshijin-commit` | 简洁提交信息。Conventional Commits。标题≤50字符 |
| **genshijin-review** | `/genshijin-review` | 1行PR评论: `L42: 🔴 错误: user null。添加保护。` |
| **genshijin-help** | `/genshijin-help` | 此卡片 |

## 解除

输入「原始人停止」或「通常模式」解除。`/genshijin` 可重新启动。

## 默认模式设置

默认 = `通常`。更改方法:

**环境变量（最高优先级）:**
```bash
export GENSHIJIN_DEFAULT_MODE=极限
```

有效值: `礼貌`, `通常`, `极限`, `off`

**配置文件** (`~/.config/genshijin/config.json`):
```json
{ "defaultMode": "礼貌" }
```

`"off"` 可禁用会话开始时的自动启动。`/genshijin` 可手动启动。

优先级: 环境变量 > 配置文件 > `通常`

## 详细说明

原仓库: https://github.com/InterfaceX-co-jp/genshijin
