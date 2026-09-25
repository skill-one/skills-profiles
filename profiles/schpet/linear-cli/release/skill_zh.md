# 发布流程

该技能为 linear-cli 项目提供了一套系统化的发布流程，用于创建和发布版本。它处理版本日志管理、版本号更新、测试和打标签。

## 使用场景

在准备发布 linear-cli 的新版本时使用此技能。该流程确保所有变更都有文档记录、测试通过，并在发布前正确打标签。

## 前置条件

确保以下工具可用：

- `changelog` 技能用于版本日志管理
- `svbump` 用于版本号更新（已安装）
- `jj` 用于版本控制操作
- `just` 用于运行发布任务

## 发布流程

### 第 1 步：查看自上次发布以来的提交

确定自上次发布以来所做的提交：

```bash
jj log --ignore-working-copy --git -r 'tags()..@' --no-graph
```

这显示了从最新标签到当前提交的所有提交。

### 第 2 步：添加版本日志条目

对于上述每个提交，评估它是否值得添加版本日志条目。重点关注面向用户的变更：

**包含在版本日志中的内容：**

- 新功能
- 修复的 Bug
- 不兼容变更
- 显著改进
- 废弃

**排除在版本日志之外的变更：**

- 没有用户影响的内部重构
- 仅文档变更
- 构建/CI 配置变更
- 日常维护提交（除非有重大影响）

使用版本日志 CLI 添加条目。使用 `--attribute-pr` 与提交 SHA 结合，自动查找关联的 PR 并添加归属，排除 `schpet` 和 `schpetbot`：

```bash
changelog add --type <类型> "<描述>" --attribute-pr <提交 SHA> --exclude-users schpet,schpetbot
```

对于没有关联 PR 的提交或归属不相关的情况，省略 `--attribute-pr`。

类型与 Keep a Changelog 类别匹配：

- `added` - 新功能
- `changed` - 现有功能的变更
- `deprecated` - 即将被移除的功能
- `removed` - 已移除的功能
- `fixed` - 修复的 Bug
- `security` - 安全改进

### 第 3 步：与用户验证版本日志

添加所有相关版本日志条目后，向用户展示 `CHANGELOG.md` 的未发布部分并请求他们进行审查：

1. 阅读 `CHANGELOG.md` 文件
2. 展示 `[Unreleased]` 部分
3. 询问："请审查这些版本日志条目。在发布前是否需要任何变更？"
4. 进行任何请求的调整

### 第 4 步：确定 Semver 变更

根据版本日志中的变更类型，确定并建议适当的语义版本号变更：

**主版本 (X.0.0)：**

- 不兼容变更
- 已移除的功能
- 显著的 API 变更

**次版本 (0.X.0)：**

- 新功能（added）
- 废弃
- 向后兼容的功能添加

**补丁版本 (0.0.X)：**

- 修复的 Bug
- 安全修复
- 没有新功能的微小改进

向用户展示建议：

```
根据版本日志条目，我建议进行 <主版本/次版本/补丁版本> 版本号变更，因为：
- [原因 1]
- [原因 2]

当前版本：<当前版本>
建议版本：<建议版本>

是否继续进行此版本号变更？
```

在用户确认之前不要继续。

### 第 5 步：运行版本日志发布

一旦用户确认版本号变更，使用适当的 Semver 级别运行版本日志发布命令：

```bash
changelog release <主版本|次版本|补丁版本>
```

这会更新 `CHANGELOG.md`，将未发布部分转换为版本化的发布。

### 第 6 步：执行标签流程

版本日志发布后，执行 justfile 中的完整标签流程。这包括：

1. **运行质量检查：**
   ```bash
   deno check src/main.ts
   deno fmt --check
   deno lint
   deno task test
   ```

2. **更新版本文件：**
   ```bash
   # 从版本日志获取最新版本
   LATEST_VERSION=$(changelog version latest)

   # 将版本写入 deno.json
   svbump write "$LATEST_VERSION" version deno.json

   # 从 deno.json 读取版本并写入 dist-workspace.toml
   DENO_VERSION=$(svbump read version deno.json)
   svbump write "$DENO_VERSION" package.version dist-workspace.toml
   ```

3. **重新生成技能文档：**
   ```bash
   # 生成更新的技能文档（包含 deno.json 中的版本号）
   deno task generate-skill-docs

   # 更新 Claude Code 插件版本
   FINAL_VERSION=$(svbump read version deno.json)
   svbump write "$FINAL_VERSION" version .claude-plugin/plugin.json
   svbump write "$FINAL_VERSION" version .claude-plugin/marketplace.json
   # marketplace.json 还在 plugins[0] 中包含版本号 — svbump 无法处理数组路径，
   # 因此使用 jq 或手动编辑以匹配
   ```

4. **创建提交和标签：**
   ```bash
   # 获取最终版本
   FINAL_VERSION=$(svbump read version deno.json)

   # 创建提交
   jj commit -m "chore: 发布 linear-cli 版本 $FINAL_VERSION"

   # 将 main 标记设置为父提交
   jj bookmark set main -r @-

   # 在父提交上创建标签
   jj tag set "v$FINAL_VERSION" -r @-
   ```

5. **推送到远程仓库：**
   ```bash
   # 推送标记
   jj git push --bookmark main

   # 推送标签（使用 git）
   git push origin --tags
   ```

6. **报告完成：**
   ```
   成功发布 v$FINAL_VERSION！
   ```

## 错误处理

如果任何步骤失败：

- **质量检查失败：** 修复问题后再继续。如果测试失败或存在 linting 错误，不要继续发布。
- **版本号更新失败：** 验证版本格式和文件是否存在。
- **推送失败：** 检查认证和远程访问。

始终明确报告错误。如果关键步骤失败，永远不要继续发布流程。

## 重要提示

- justfile 的 `tag` 菜单处理从第 5 行到第 21 行的完整流程
- 使用 `jj` 进行所有版本控制操作（按项目 CLAUDE.md）
- 对于只读 jj 操作，始终使用 `--ignore-working-copy`
- 该流程在父提交 (@-) 上创建提交，然后创建新的工作提交
- 需要 `jj git push` 和 `git push origin --tags`（jj 用于标记，git 用于标签）

## 发布后

发布成功后：

1. 验证 GitHub 上是否出现标签
2. 检查 GitHub Actions 发布工作流是否触发（如果配置了）
3. 确认新版本已发布

## 参考

参考 `justfile` 第 5 行到第 21 行的完整标签菜单实现。
