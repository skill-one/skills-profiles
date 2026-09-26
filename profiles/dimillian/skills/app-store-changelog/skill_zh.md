# App Store 更新日志

## 概述
从上次标签以来的 git 历史中生成全面的、面向用户的更新日志，然后将提交信息翻译成清晰的 App Store 发布说明。

## 工作流程

### 1) 收集变更
- 从仓库根目录运行 `scripts/collect_release_changes.sh` 来收集提交信息及修改过的文件。
- 如有需要，可以传递特定的标签或引用：`scripts/collect_release_changes.sh v1.2.3 HEAD`。
- 如果没有标签存在，脚本会回退到完整历史记录。

### 2) 评估用户影响
- 扫描提交信息及文件，以识别面向用户的变更。
- 按主题（新增、改进、修复）分组变更并消除重复。
- 掉用仅限内部的工作（构建脚本、重构、依赖升级、CI）。

### 3) 起草 App Store 说明
- 为每个面向用户的变更编写简短、以收益为重点的要点。
- 使用清晰的动词和简洁的语言；避免内部术语。
- 优先使用 5 到 10 个要点，除非用户要求不同长度。

### 4) 验证
- 确保每个要点都能对应到指定范围内的实际变更。
- 检查重复项和过于技术性的措辞。
- 如果任何变更模糊不清或可能仅限内部，则请求澄清。

## 提交信息到要点的示例

以下展示了原始提交信息如何翻译成 App Store 要点：

| 原始提交信息 | App Store 要点 |
|---|---|
| `fix(auth): resolve token refresh race condition on iOS 17` | • 修复了一个可能导致部分用户意外登出的登录问题。 |
| `feat(search): add voice input to search bar` | • 搜索您的库时无需动手，使用新的语音输入选项。 |
| `perf(timeline): lazy-load images to reduce scroll jank` | • 滚动您的时间线现在更平滑、更快。 |

被**掉用**的仅限内部提交（无用户影响）：
- `chore: upgrade fastlane to 2.219`
- `refactor(network): extract URLSession wrapper into module`
- `ci: add nightly build job`

## 示例输出

```
版本 3.4 新功能

• 搜索您的库时无需动手，使用新的语音输入选项。
• 滚动您的时间线现在更平滑、更快。
• 修复了一个可能导致部分用户意外登出的登录问题。
• 为设置屏幕添加了暗黑模式支持。
• 打开大型相册时的加载时间有所改进。
```

## 输出格式
- 标题（可选）："What's New" 或产品名称 + 版本。
- 仅要点列表；每个要点一个句子。
- 如果用户提供了限制，则遵守店面限制。

## 资源
- `scripts/collect_release_changes.sh`: 收集自上次标签以来的提交信息及修改过的文件。
- `references/release-notes-guidelines.md`: App Store 说明的语言、过滤和 QA 规则。
