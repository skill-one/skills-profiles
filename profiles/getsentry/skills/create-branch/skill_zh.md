# 创建分支

按照 Sentry 的命名规范创建一个 git 分支。
除非用户明确要求手动选择名称，否则保持此工作流程非交互式。

## 工作流程

1.  解析工作描述：
   - 如果存在 `$ARGUMENTS`，则使用它
   - 否则检查：
     ```bash
     git diff
     git diff --cached
     git status --short
     ```
   - 如果存在本地更改，从 diff 中推导出简短描述
   - 如果没有本地更改，使用通用描述，如 `repo-maintenance`、`tooling-update` 或 `work-in-progress`

2.  分类分支类型：

| 类型 | 使用场景 |
|------|----------|
| `feat` | 新功能 |
| `fix` | 现在可以正常工作的错误行为 |
| `ref` | 行为保持不变，结构变化 |
| `chore` | 现有工具/配置的维护 |
| `perf` | 行为相同，速度更快 |
| `style` | 仅视觉或格式 |
| `docs` | 仅文档 |
| `test` | 仅测试 |
| `ci` | CI/CD 配置 |
| `build` | 构建系统 |
| `meta` | 仓库元数据 |
| `license` | 许可证更改 |

   不确定时：使用 `feat` 表示新事物，`ref` 表示重构，`chore` 表示维护。

3.  生成 `<类型>/<简短描述>`。
   保持 `<简短描述>` 使用连字符分隔的小写字母（kebab-case）、仅 ASCII 字符，并最好为 3 到 6 个单词。

4.  无需提示选择基础分支：
   ```bash
   git branch --show-current
   git remote | grep -qx origin && echo origin || git remote | head -1
   git symbolic-ref refs/remotes/<远程仓库名>/HEAD 2>/dev/null | sed 's|refs/remotes/<远程仓库名>/||' | tr -d '[:space:]'
   ```
   - 如果默认分支检测失败，则回退到 `main`，然后 `master`，然后当前分支
   - 如果处于 Detached HEAD 状态，则从当前提交创建分支
   - 如果已经在非默认分支上，则从当前分支创建分支
   - 只有在用户明确要求时才切换到默认分支

5.  通过追加 `-2`、`-3` 等直到本地和远程都不存在同名来避免冲突。

6.  创建分支：
   ```bash
   git checkout -b <分支名称>
   ```
   报告最终的分支名称，但不要停止以获取确认。

## 参考

- [Sentry 分支命名](https://develop.sentry.dev/sdk/getting-started/standards/code-submission/#branch-naming)
