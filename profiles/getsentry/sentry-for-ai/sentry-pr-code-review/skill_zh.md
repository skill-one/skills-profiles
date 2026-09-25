> [所有技能](../../SKILL_TREE.md) > [工作流](../sentry-workflow/SKILL.md) > PR 代码审查

# Sentry 代码审查

审查并修复由 Seer（由 Sentry 提供）在 GitHub PR 评论中识别出的问题。

## 调用此技能的场景

- 用户要求审查 PR 上的 "Sentry 评论" 或 "Sentry 问题"
- 用户分享 PR URL/编号并提及 Sentry 或 Seer 的反馈
- 用户要求 "处理 Sentry 审查" 或 "解决 Sentry 查找结果"
- 用户希望查找带有未解决 Sentry 评论的 PR

## 前置条件

- 已安装并认证 `gh` CLI
- 仓库已安装 [Seer by Sentry](https://github.com/apps/seer-by-sentry) GitHub 应用

**重要提示：** 下面解析的评论格式基于 Seer 当前输出。这不是 API 合约，可能会变更。请始终验证实际评论结构。

## 第一阶段：获取 Seer 评论

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments --paginate \
  --jq '.[] | select(.user.login == "seer-by-sentry[bot]") | {file: .path, line: .line, body: .body}'
```

**机器人登录名是 `seer-by-sentry[bot]`** — 不是 `sentry[bot]` 或 `sentry-io[bot]`。

如果未提供 PR 编号，则查找带有 Seer 评论的最新 PR：

```bash
gh pr list --state open --json number,title --limit 20 | \
  jq -r '.[].number' | while read pr; do
    count=$(gh api "repos/{owner}/{repo}/pulls/$pr/comments" --paginate \
      --jq '[.[] | select(.user.login == "seer-by-sentry[bot]")] | length')
    [ "$count" -gt 0 ] && echo "PR #$pr: $count Seer 评论"
  done
```

## 第二阶段：解析每条评论

从 Markdown 正文提取：
- **问题描述**：以 `**问题：**` 开头的行
- **严重程度/置信度**：在 `<sub>严重程度: X | 置信度: X.XX</sub>` 中
- **分析**：在 `<summary>🔍 <b>详细分析</b></summary>` 块内
- **建议修复**：在 `<summary>💡 <b>建议修复</b></summary>` 块内
- **AI 提示**：在 `<summary>🤖 <b>AI 代理提示</b></summary>` 块内

## 第三阶段：验证和修复

针对每个问题：
1. 在指定行读取文件
2. 确认问题在当前代码中仍然存在（未已在后续提交中修复）
3. 审查周边代码以评估是否为实际问题或误报
4. 实施修复（以建议修复为起点，或自行编写）
5. 考虑边缘情况和回归风险

## 第四阶段：总结并报告结果

```markdown
## Seer 审查：PR #[number]

### 已解决
| 文件:行 | 问题 | 严重程度 | 已应用修复 |
|---------|------|----------|-------------|
| path:123 | 描述 | 高       | 已完成     |

### 已跳过（误报或已修复）
| 文件:行 | 问题 | 原因 |
|---------|------|------|

**总结：** X 已解决，Y 已跳过
```

## Seer 审查触发器

| 触发器 | 当...时 |
|---------|--------|
| PR 设置为 "准备审查" | 自动错误预测 |
| 在 PR 准备状态下推送提交 | 重新运行预测 |
| `@sentry review` 评论 | 手动触发完整审查+建议 |
| 草稿 PR | 跳过 — 直至标记为准备后才审查 |

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 未找到 Seer 评论 | 验证 Seer GitHub 应用是否已安装在仓库 |
| 机器人名称不匹配 | 登录名是 `seer-by-sentry[bot]`，不是 `sentry[bot]` |
| 新 PR 上未显示评论 | PR 必须为 "准备审查"（非草稿） |
| `gh api` 返回部分结果 | 确保 `--paginate` 标志已包含 |

## 常见问题类型

| 类别 | 示例 |
|------|------|
| 类型安全 | 缺少空值检查，不安全的类型断言 |
| 错误处理 | 忽略错误，缺少边界 |
| 验证 | 允许性输入，缺少清理 |
| 配置 | 缺少环境变量，路径错误 |
