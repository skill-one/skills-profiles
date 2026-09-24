# Caveman 帮助

当被调用时显示此参考卡片。一次性操作——请勿更改模式、写入标志文件或保存任何内容。以 caveman 风格输出。

## 模式

| 模式 | 触发 | 更改内容 |
|------|------|----------|
| **Lite** | `/caveman lite` | 删除填充词。保持句子结构。 |
| **Full** | `/caveman` | 删除冠词、填充词、客套话、委婉语。片段可以。默认模式。 |
| **Ultra** | `/caveman ultra` | 极端压缩。仅用片段。表格优于文字。 |
| **Wenyan-Lite** | `/caveman wenyan-lite` | 文言文风格，轻度压缩。 |
| **Wenyan-Full** | `/caveman wenyan` | 完整的文言文。极致文言精简。 |
| **Wenyan-Ultra** | `/caveman wenyan-ultra` | 极端。预算有限的古代学者。 |

模式保持到更改或会话结束。

## 技能

| 技能 | 触发 | 功能 |
|------|------|------|
| **caveman-commit** | `/caveman-commit` | 简洁的提交信息。遵循 Conventional Commits。主题不超过 50 个字符。 |
| **caveman-review** | `/caveman-review` | 一行 PR 评论：`L42: bug: user null. Add guard.` |
| **caveman-compress** | `/caveman-compress <file>` | 将 .md 文件压缩为 caveman 文字。节省约 46% 输入 token。 |
| **caveman-help** | `/caveman-help` | 此卡片。 |

## 停用

说“stop caveman”或“normal mode”。随时用 `/caveman` 恢复。

## 语言

默认保持用户的语言——以用户使用的语言回复，无论示例文本或多语言背景如何，绝不切换。压缩风格，而非语言。技术术语、代码、命令、提交类型以及精确的错
误字符串保持原样，除非用户要求翻译。

## 配置默认模式

默认模式 = `full`。更改方式：

**环境变量**（最高优先级）：
```bash
export CAVEMAN_DEFAULT_MODE=ultra
```

**配置文件**（`~/.config/caveman/config.json`）：
```json
{ "defaultMode": "lite" }
```

设置 `"off"` 可禁用会话启动时的自动激活。用户仍可使用 `/caveman` 手动激活。

解析优先级：环境变量 > 配置文件 > `full`。

## 更多信息

完整文档：https://github.com/JuliusBrussee/caveman
