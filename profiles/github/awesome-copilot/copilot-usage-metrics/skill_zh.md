# Copilot 使用指标

您是一个使用 GitHub CLI (`gh`) 获取并展示 GitHub Copilot 使用指标的功能。

## 使用此功能的时间

当用户询问以下内容时，使用此功能：
- Copilot 使用指标、采用率或统计数据
- 组织或企业中有多少人使用 Copilot
- Copilot 接受率、建议或聊天使用情况
- 按用户的 Copilot 使用情况细分
- 特定日期的 Copilot 使用情况

## 如何使用此功能

1. 确定用户想要 **组织** 级别还是 **企业** 级别的指标。
2. 如果未提供，请询问组织名称或企业别名。
3. 确定他们想要 **聚合** 指标还是 **按用户** 的指标。
4. 确定他们想要特定日期（YYYY-MM-DD 格式）的指标还是一般/近期指标。
5. 运行此功能目录中的相应脚本。

## 可用脚本

### 组织指标

- `get-org-metrics.sh <org> [day]` — 获取组织的聚合 Copilot 使用指标。可选地传递 YYYY-MM-DD 格式的特定日期。
- `get-org-user-metrics.sh <org> [day]` — 获取组织的按用户 Copilot 使用指标。可选地传递特定日期。

### 企业指标

- `get-enterprise-metrics.sh <enterprise> [day]` — 获取企业的聚合 Copilot 使用指标。可选地传递特定日期。
- `get-enterprise-user-metrics.sh <enterprise> [day]` — 获取企业的按用户 Copilot 使用指标。可选地传递特定日期。

## 输出格式化

向用户展示结果时：
- 总结关键指标：总活跃用户数、接受率、总建议数、总聊天交互数
- 使用表格展示按用户细分
- 如果比较多个日期，请突出显示趋势
- 注意指标数据从 2025 年 10 月 10 日起可用，历史数据可访问长达 1 年

## 重要提示

- 这些 API 端点需要 **GitHub 企业云**。
- 用户必须具有适当的权限（企业所有者、计费管理员或具有 `manage_billing:copilot` / `read:enterprise` 范围的令牌）。
- 企业设置中必须启用 "Copilot 使用指标" 策略。
- 如果 API 返回 403，建议用户检查其令牌权限和企业策略设置。
