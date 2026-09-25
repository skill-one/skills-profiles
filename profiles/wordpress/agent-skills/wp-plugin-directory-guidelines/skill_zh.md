## 概述

18个 WordPress.org 插件目录指南的权威参考。涵盖 GPL 许可证、插件命名/商标规则、试用软件限制以及所有其他提交要求。

## 何时使用

当您需要时使用此技能：
- 审查 WordPress 插件是否符合 WordPress.org 插件目录指南
- 检查插件或其捆绑库的 GPL 许可证兼容性
- 验证插件文件中的许可证头
- 在提交前识别常见的指南违规行为
- 回答有关 WordPress.org 上允许或不允许内容的问题
- 评估高级/追加流程、许可证检查或免费增值定位
- 审查“预告”或“预览”UI 以检查试用软件违规行为

## 需要的输入

- 插件源代码（或特定文件进行审查）
- 可选：插件自述文件和插件头部元数据，用于命名和许可证检查

## 程序

1. 将插件的许可证头与下文中的 **有效许可证头** 部分进行核对。
2. 逐步通过 **18 条指南** 检查清单，特别关注指南 1、4、5、7、8 和 17。
3. 使用 [指南审查检查清单.md](references/guideline-review-checklist.md) 中的清单确认试用软件/免费增值合规性（指南 5 部分）。
4. 对于捆绑的第三方代码，根据 **快速兼容 GPL 许可证** 下方进行许可证兼容性验证。
5. 标记 **快速常见 GPL 违规** 下方的内容。
6. 对于边缘情况，请参考详细参考文档和 [GNU GPL 常见问题解答](https://www.gnu.org/licenses/gpl-faq.html)。

## 18 条指南审查检查清单

使用详细的、按指南分项的检查清单 [指南审查检查清单.md](references/guideline-review-checklist.md)。仅在请求完整指南审核时加载此参考文件。

## GPL 合规性（指南 1 详细说明）

使用 [gpl-compliance.md](references/gpl-compliance.md) 获取完整的许可证表格、兼容性细微差别和示例。将此内联部分保留为快速决策辅助工具。

### 验证（许可证）

- 每个与许可证相关的 问题都必须引用 **指南 1**，并包括文件路径和确切的许可证字符串。
- 将兼容性声明与 **快速兼容 GPL 许可证** 进行核对，并对模糊的许可证进行升级。

### 失败模式（许可证）

- 如果许可证不明确为 GPL 兼容，不要猜测。请检查 [GNU 许可证列表](https://www.gnu.org/licenses/license-list.html)。
- 对于双许可证包，请验证两个许可证和再分发条款。

### 快速参考：WordPress GPL 要求

- WordPress 是 **GPLv2 或更高版本**。
- 在 WordPress.org 上分发的插件必须是 100% GPL 兼容（代码和资源）。
- 在主插件文件中包含有效的 `License:` 头和 `License URI:`。
- 不要添加与 GPL 自由相冲突的限制。

### 有效许可证头

## GPL 版本总结

| 版本 | 年份 | 关键新增 |
|------|------|----------|
| GPLv1 | 1989 | 基础 Copyleft：修改后的共享 alike |
| GPLv2 | 1991 | “自由或死亡”条款（第 7 节），更清晰的分发条款 |
| GPLv3 | 2007 | 反技术保护措施，明确的专利授权，兼容性条款 |

WordPress 使用 **GPLv2 或更高版本**，这意味着插件可以使用 GPLv2、GPLv3 或 “GPLv2 或更高版本”。

有关完整许可证文本，请参阅：
- [GNU 通用公共许可证 v1](https://www.gnu.org/licenses/gpl-1.0.html)
- [GNU 通用公共许可证 v2](https://www.gnu.org/licenses/gpl-2.0.html)
- [GNU 通用公共许可证 v3](https://www.gnu.org/licenses/gpl-3.0.html)

## 许可证合规性检查清单

在审查插件时，请验证：

- [ ] 主插件文件具有有效的 `License:` 头（例如，`GPL-2.0-or-later`、`GPL-2.0+`、`GPLv2 or later`）
- [ ] 主插件文件具有指向 GPL 文本的 `License URI:` 头
- [ ] 如果存在捆绑库，则每个库都具有 GPL 兼容的许可证
- [ ] 没有“分割许可证”（例如，代码 GPL 但高级功能专有）
- [ ] 没有超出 GPL 允许的额外限制
- [ ] 没有 限制商业使用、修改或再分发的条款
- [ ] 没有混淆代码（违反源代码可用性精神）

## WordPress 插件的有效许可证头

```
License: GPL-2.0-or-later
License URI: https://www.gnu.org/licenses/gpl-2.0.html
```

```text
License: GPL-3.0-or-later
License URI: https://www.gnu.org/licenses/gpl-3.0.html
```

```text
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html
```

### 快速兼容的 GPL 许可证

- 安全默认值：GPL-2.0-or-later、GPL-3.0-or-later。
- 常见的宽松许可证系列：MIT/Expat、BSD、ISC、zlib、Boost。
- 条件兼容性需要小心：Apache-2.0 和 MPL-2.0（验证使用上下文）。
- 对于完整接受和拒绝的标识符，请使用 [gpl-compliance.md](references/gpl-compliance.md)。

### 常见 GPL 违规（快速）

- 限制分发代码的分割许可证。
- 混淆或非对应的源代码分发。
- 限制性条款（非商业、不可转售、强制回链）。
- 捆绑 GPL 不兼容的库或资源。

## 插件命名规则（指南 17）

使用 [命名规则.md](references/naming-rules.md) 获取完整的商标列表、slug 块和命名示例。保留此内联检查清单用于快速筛选。

### 命名检查清单（快速）

- 名称不是占位符，至少有 5 个字母数字字符。
- 头部名称和自述文件名称一致。
- 名称具有特定性和功能相关性；避免关键词堆砌。
- 商标/项目名称仅在像 `for`、`with`、`using`、`and` 这样的连接词之后出现。
- 没有禁止/不鼓励的术语或商标混合词。
- Slug 为小写、连字符、<= 50 个字符，并避免受限制的术语。
