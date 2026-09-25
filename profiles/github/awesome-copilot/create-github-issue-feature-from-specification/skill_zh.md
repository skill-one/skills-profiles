# 从规范创建 GitHub 问题

为位于 `${file}` 的规范创建 GitHub 问题。

## 流程

1. 分析规范文件以提取需求
2. 使用 `search_issues` 检查现有问题
3. 使用 `create_issue` 创建新问题，或使用 `update_issue` 更新现有问题
4. 使用 `feature_request.yml` 模板（若无则使用默认模板）

## 要求

- 一个问题对应完整的规范
- 标题清晰标识规范
- 仅包含规范要求的变化
- 创建前验证现有问题

## 问题内容

- 标题：规范中的功能名称
- 描述：问题描述、建议解决方案和背景
- 标签：feature、enhancement（根据情况添加）
