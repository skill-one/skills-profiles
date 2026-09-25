# 更新 Bicep 文件中的 Azure 认证模块

更新 Bicep 文件 `${file}` 以使用最新的 Azure 认证模块 (AVM) 版本。将进度更新限制为非破坏性变更。仅输出最终输出表格和摘要信息。

## 流程

1. **扫描**：从 `${file}` 中提取 AVM 模块和当前版本
1. **识别**：使用 `#search` 工具，通过匹配 `avm/res/{service}/{resource}` 列出所有使用的唯一 AVM 模块
1. **检查**：使用 `#fetch` 工具从 MCR 获取每个 AVM 模块的最新版本：`https://mcr.microsoft.com/v2/bicep/avm/res/{service}/{resource}/tags/list`
1. **比较**：解析语义版本以识别需要更新的 AVM 模块
1. **审查**：对于破坏性变更，使用 `#fetch` 工具从以下地址获取文档：`https://github.com/Azure/bicep-registry-modules/tree/main/avm/res/{service}/{resource}`
1. **更新**：使用 `#editFiles` 工具应用版本更新和参数变更
1. **验证**：使用 `#runCommands` 工具运行 `bicep lint` 和 `bicep build` 以确保合规性
1. **输出**：以表格格式总结变更，并在下方提供更新摘要。

## 工具使用

如果可用，始终使用工具 `#search`、`#searchResults`、`#fetch`、`#editFiles`、`#runCommands`、`#todos`。避免编写代码执行任务。

## 破坏性变更策略

⚠️ 如果更新涉及以下内容，则 **暂停以获取批准**：

- 不兼容的参数变更
- 安全/合规性修改
- 行为变更

## 输出格式

仅以带图标的表格形式显示结果：

```markdown
| 模块 | 当前 | 最新 | 状态 | 操作 | 文档 |
|------|------|------|------|------|------|
| avm/res/compute/vm | 0.1.0 | 0.2.0 | 🔄 | 已更新 | [📖](link) |
| avm/res/storage/account | 0.3.0 | 0.3.0 | ✅ | 当前 | [📖](link) |

### 更新摘要

描述所做的更新、任何需要手动审查的事项或遇到的问题。
```

## 图标

- 🔄 已更新
- ✅ 当前
- ⚠️ 需要手动审查
- ❌ 失败
- 📖 文档

## 要求

- 仅使用 MCR 标签 API 进行版本发现
- 解析 JSON 标签数组并按语义版本排序
- 维持 Bicep 文件的合法性和 linting 合规性
