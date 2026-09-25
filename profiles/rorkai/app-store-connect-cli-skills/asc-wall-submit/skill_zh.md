# asc wall submit

使用此技能通过内置的 CLI 流程添加或更新应用墙条目。

## 使用场景

- 用户希望将应用提交至应用墙
- 用户希望更新现有的应用墙条目
- 用户需要精确的应用墙提交流程

## 必填输入

使用以下输入路径之一：

- 标准应用商店流程：`app` ID
- 手动/预发布流程：`link` 加上 `name`

## 提交工作流

1. 从 `App-Store-Connect-CLI` 仓库根目录运行命令。
2. 首先预览：
   - `asc apps wall submit --app "1234567890" --dry-run`
   - 或 `asc apps wall submit --link "https://testflight.apple.com/join/ABCDEFG" --name "My Beta App" --dry-run`
3. 确认提交：
   - `asc apps wall submit --app "1234567890" --confirm`
   - 或 `asc apps wall submit --link "https://testflight.apple.com/join/ABCDEFG" --name "My Beta App" --confirm`
4. 审核生成的 PR 计划以及 `docs/wall-of-apps.json` 的变更结果。

## 安全准则

- 不要修改 `docs/wall-of-apps.json` 中无关的条目。
- 如果因输入无效导致提交失败，请修正输入并重新运行 CLI 命令。
- 除非维护者定义了基于问题的输入流程，否则提交路径应基于 PR。

## 示例

添加新应用：

`asc apps wall submit --app "1234567890" --confirm`

提交非应用商店/TestFlight条目：

`asc apps wall submit --link "https://testflight.apple.com/join/ABCDEFG" --name "My Beta App" --confirm`
