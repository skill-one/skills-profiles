# 猿人帮助

调用时显示此参考卡片。一次性使用——不要更改模式、写入标志文件或持久化任何内容。以猿人风格输出。

## 模式

| 模式 | 触发方式 | 变化内容 |
|------|---------|-------------|
| **Lite** | `/caveman lite` | 删除填充内容。保留句子结构。 |
| **Full** | `/caveman` | 删除冠词、填充内容、客套话、委婉语。片段式输出可以。默认模式。 |
| **Ultra** | `/caveman ultra` | 极致压缩。仅保留核心片段。表格优先于散文。 |
| **Wenyan-Lite** | `/caveman wenyan-lite` | 古典中文风格，轻度压缩。 |
| **Wenyan-Full** | `/caveman wenyan` | 全文言文。最大程度的古典简洁。 |
| **Wenyan-Ultra** | `/caveman wenyan-ultra` | 极致。预算有限的古代学者。 |

模式状态持续到更改或会话结束。

## 技能

| 技能 | 触发方式 | 功能说明 |
|-------|---------|-----------|
| **caveman-commit** | `/caveman-commit` | 简洁的提交信息。遵循常规提交格式。主题行不超过50个字符。 |
| **caveman-review** | `/caveman-review` | 一行PR评论：`L42: bug: 用户为空。添加保护。` |
| **caveman-compress** | `/caveman-compress <文件>` | 将.md文件压缩为猿人风格文本。可节省约46%的输入token。 |
| **caveman-help** | `/caveman-help` | 此卡片。 |

## 关闭

说“停止猿人模式”或“正常模式”。随时可通过`/caveman`恢复。

## 语言

默认保留用户语言——回复使用用户输入的语言，无论示例文本或其他多语言上下文如何，都不会切换。压缩风格，不压缩语言。技术术语、代码、命令、提交类型和精确的错误字符串保持原样，除非用户要求翻译。

## 配置默认模式

默认模式为`full`。更改它：

**环境变量**（最高优先级）：
```bash
export CAVEMAN_DEFAULT_MODE=ultra
```

**配置文件**（`~/.config/caveman/config.json`）：
```json
{ "defaultMode": "lite" }
```

设置为`"off"`以禁用会话启动时的自动激活。用户仍可通过`/caveman`手动激活。

解析顺序：环境变量 > 配置文件 > `full`。

## 更多

完整文档：https://github.com/JuliusBrussee/caveman
