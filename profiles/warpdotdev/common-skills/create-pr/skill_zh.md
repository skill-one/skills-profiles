# create-pr

## 概述

本指南涵盖了在 warp 仓库中创建拉取请求的最佳实践，包括合并主分支、高效验证更改、链接 Linear 任务、确保适当的测试覆盖率以及为有效审查构建 PR 结构。

## 相关技能

- `write-pr-description` - 编写 PR 正文：模板部分、散文和审阅者指导
- `fix-errors` - 在打开 PR 之前修复有针对性的编译、测试、代码检查或格式化失败
- `warp-integration-test` - 为用户可见流程、回归和 P0 用例添加或更新集成覆盖
- `add-feature-flag` - 使用功能标志来控制更改

## PR 前检查清单

### 1. 将主分支合并到你的特性分支

**在开始审查过程之前，始终将主分支合并到你的特性分支。**

```bash
git fetch origin
git merge origin/master
```

在打开 PR 之前，本地解决任何合并冲突。

### 2. 审查你的更改

在创建 PR 之前，审查你即将提交的更改：

```bash
# 查看你分支中的提交（与基础分支进行比较）
git --no-pager log <base-branch>..HEAD --oneline

# 查看更改的文件统计信息
git --no-pager diff <base-branch>...HEAD --stat

# 查看完整差异
git --no-pager diff <base-branch>...HEAD
```

这有助于你：
- 验证所有预期的更改都已包含
- 在审查前捕获未预期的更改
- 编写准确的 PR 描述
- 确保你与正确的基准分支进行比较
- **测试：** 在需要时包含测试——错误修复（回归测试）、算法代码（单元测试）、UI 组件（布局测试）、P0 用例（集成测试）。见下文测试要求。

### 3. 尊重实现代理验证

PR 创建不是一个验证边界。如果实现工作流已经完成了它的测试、代码检查和最终格式化，并且候选者没有变化，就不要重新运行它们。

如果合并主分支或准备 PR 改变了源代码、测试、清单、生成代码或配置，按以下顺序验证新候选者：

1. 运行相关测试并修复代码，直到它们通过。
2. 运行适用的 Clippy 和其他代码检查、类型检查或构建检查，并修复它们的发现。只有在修复实质上改变了行为时才返回受影响的测试。
3. 在所有其他代码更改完成后，运行一次 `./script/format`。

格式化后不要重新运行测试或代码检查，除非用户、任务或批准的规范明确要求运行 `./script/presubmit`。CI 负责超出目标本地覆盖范围的罕见失败。仅文档更改不需要 Rust 测试、Clippy 或格式化。

### 4. 链接到 Linear 任务

在可能的情况下，PR 应与一个 Linear 任务相关联。使用 Linear MCP 工具（如果可用）查找相应的问题。

**分支命名约定：**
远程分支应以前缀你的名字（例如，`zheng/feature`、`alice/fix-bug`）。

**如何将 PR 链接到 Linear：**
在创建 PR 之前，在 PR 标题中包含问题 ID（例如，`[WARP-1234] 添加新功能`）。这样做可以自动链接。

### 5. 打开 PR

在打开 PR 时使用 `.github/pull_request_template.md` 中的 PR 模板。

在适当的时候使用 PR 模板底部的格式添加变更日志条目。一些示例：
- 功能： "在当前目录的文件中全局搜索。使用 CMD-F/CTRL-SHIFT-F 打开。"
- 改进： "在跳转到行/列时添加水平自动滚动。"
- 错误修复： "修复了当代理运行命令时会清除会话查看器输入。"

**CLI 工作流程：**

- **检查当前分支是否存在 PR：**
  ```bash
  gh pr view --json number,url
  ```
  如果 PR 存在，退出码为 0，否则为 1。

- **创建新的 PR：**
  ```bash
  # 带标题和正文
  gh pr create --title "标题" --body "描述" --draft

  # 从提交中自动填充
  gh pr create --fill --draft

  # 使用 PR 模板文件
  gh pr create --body-file .github/pull_request_template.md --title "标题" --draft
  ```
  关键标志：`--draft` / `-d`、`--fill` / `-f`、`--body-file` / `-F`、`--web` / `-w`

- **更新现有的 PR：**
  ```bash
  gh pr edit --title "新标题" --body "新正文"
  gh pr edit --add-reviewer username --add-label bug
  ```

- **标记 PR 准备审查：**
  ```bash
  gh pr ready
  ```

### 6. 包括共同作者归属

在提交更改时，将归属作为提交消息末尾的跟踪器包含——永远不要在 PR 描述中包含——如果提交已经有一个，就不要添加第二个 Warp/Oz 共同作者跟踪器：

```
Co-Authored-By: Warp Agent <agent@warp.dev>
```

## 测试要求

### 错误修复需要回归测试

**所有错误修复都应附带回归测试。** 这有助于防止重新破坏已经破坏过一次的东西。

测试应：
- 复现原始错误（在修复之前会失败）
- 在应用修复后通过
- 清晰命名，以表明它防止了什么错误

### 算法代码需要单元测试

具有非平凡逻辑的代码应具有单元测试来验证功能：

**需要单元测试的示例：**
- 自定义数据结构（例如，`SumTree`）
- 应该返回给定查询预期结果的搜索相关 API
- UI 框架中的核心布局代码
- 任何算法或计算逻辑

**不需要：**
- 足够简单的函数
- 简单的 getter/setter

遵循仓库的本地测试约定，以获取编写单元测试的指导。

### UI 组件需要布局验证测试

**所有 UI 组件（`View` 的实现）都应该有一个简单的单元测试**来验证它们可以在没有恐慌的情况下布局。

这提供了对渲染“安全性”（尽管不是“正确性”）的高级覆盖范围：

```rust
#[test]
fn test_component_can_layout() {
    use warpui::App;
    use warp::test_util::{terminal::initialize_app_for_terminal_view, add_window_with_terminal};
    
    App::test((), |mut app| async move {
        initialize_app_for_terminal_view(&mut app);
        let term = add_window_with_terminal(&mut app, None);
        
        // 渲染组件——不应恐慌
        term.update(&mut app, |view, ctx| {
            // 创建和布局你的组件
        });
    })
}
```

### 在跳过集成覆盖之前先询问

如果 PR 改变了用户可见流程、修复了端到端回归或看起来会从集成覆盖中受益，请在创建或更新 PR 之前使用 `ask_user_question` 工具询问用户是否希望在此次工作中添加集成测试。

优先选择直接的选项，例如：

- 是的，在创建 PR 之前添加集成测试
- 否，不添加集成测试

如果用户选择添加，请使用 `warp-integration-test` 技能。

### P0 用例需要集成测试

**所有“P0 用例”都需要一个集成测试**来覆盖相关行为/流程。

**“P0 用例”的定义是：** 任何如果被破坏，将需要额外发布的应用程序行为。

集成测试应：
- 执行完整用户可见流程
- 验证端到端功能
- 放在 `integration/` 目录中

使用 `warp-integration-test` 技能获取实现细节、测试注册步骤和验证工作流程。

## PR 描述指南

使用 `write-pr-description` 技能编写正文。它涵盖了遵循仓库的模板、散文基线以及何时添加阅读顺序和审阅者关注区域。

## 打开 PR 之后

1. **监控 CI 检查** - 确保所有自动化检查通过
2. **回复审查评论** - 及时处理反馈
3. **保持 PR 更新** - 如果出现冲突，合并主分支
4. **验证更改后的候选者** - 在审查反馈导致代码更改后，运行受影响的测试，然后运行代码检查，然后运行一次 `./script/format`。不要重复验证 PR 元数据或未更改的候选者。

## 最佳实践

- **保持 PR 聚焦** - 尽可能每个 PR 一个逻辑更改
- **编写清晰的提交消息** - 解释是什么和为什么，而不仅仅是是什么
- **先自我审查** - 在请求审查之前审查你自己的差异
- **更新测试** - 确保测试覆盖率反映了你的更改
- **记录破坏性更改** - 指出任何 API 更改或破坏性修改
- **使用功能标志** - 在适当的时候使用功能标志来控制有风险的更改（见 `add-feature-flag` 技能）
