---
name: codex-theme-switcher
description: 使用一条命令从本地 ~/.codexthemes 库中应用、切换和恢复 Codex 桌面主题，并报告当前活动的主题。当用户要求应用或激活他们创建或安装的主题、在安装的主题之间切换、恢复原生 Codex 界面，或检查或调试当前应用的主题时使用。
---

# 切换活动 Codex 主题

将 `~/.codexthemes/themes/<theme-id>/` 管理的本地库中的主题应用于正在运行的 Codex 桌面应用程序，切换已安装的主题，恢复原生外观，并验证实际活动的主题。这项技能是独立的：其 TypeScript 脚本拥有可逆注入运行时。它不会创建或编辑主题（codex-theme-creator），从画廊安装主题（codex-theme-installer），或发布主题（codex-theme-submitter）。唯一需要的本地工具是 Node.js 20+、`npx` 和官方 Codex 桌面应用程序。

从已安装技能目录运行所有命令。运行时仅在 Codex 的仅环回调试端点上注入一个所属的 `<style>` 元素；它永远不会修改签名的应用程序包，并且会主题 **所有** 打开的 Codex 页面，而不仅仅是单个窗口。

## 第 1 步：选择主题

```bash
npx tsx scripts/switch-theme.ts list
```

列出所有已安装的主题（id、名称、布局模式）以及当前活动的主题。主题从 codex-theme-creator（本地创建）或 codex-theme-installer（从 codexthemes.ai 下载）到达库中。如果用户想要的主题未列出，则将任务交接给那些技能，而不是猜测路径。

## 第 2 步：应用或切换

```bash
npx tsx scripts/switch-theme.ts apply <theme-id>
```

- 如果 Codex 已经暴露其调试端点（在之前的任何主题化启动之后都是这样），则此操作会在每个打开的页面上原地热切换主题——无需重启，输出 `{"status": "active", "pagesThemed": n}`。
- 如果没有端点（此应用程序会话的第一个应用，或者 Codex 已完全退出），则请求用户明确允许重启 Codex，然后使用 `--launch` 重新运行：

```bash
npx tsx scripts/switch-theme.ts apply <theme-id> --launch
```

`--launch` 打印 `{"status": "scheduled"}` 并将退出 → 重启 → 注入序列交给一个在重启后仍然存活的分离助手（Codex 内部托管的一个代理会随它一起死亡；预期工具调用会被中断）。永远不要构建自己的重启机制——不要 shell 包装器、launchd 或计划任务，或脚本副本；助手已经能在重启后存活。

启动器支持 macOS 和 Windows。在 Windows 上，它会找到 Codex/ChatGPT 可执行文件（运行进程路径、`%LOCALAPPDATA%\Programs\...`，或 WindowsApps 执行别名——如果检测失败，请使用 `--app` 传递完整的 `.exe` 路径），使用 `taskkill` 优雅地关闭它（永远不要使用 `/F`），然后使用调试标志重新启动它。如果重启后端点从未出现，那么已安装的构建（例如 Microsoft Store 包）会丢弃调试标志——明确报告该限制；永远不要修改 `WindowsApps` 或安装目录下的文件。

## 内置的可读性门禁

每次应用都会在注入后测量实际渲染的像素（基于可见文本的截图对比度）。如果主题使文本无法阅读，应用将 **自动还原** 到之前活动的主题（或原生外观），并报告 `{"status": "reverted", "failures": [...]}` 以及测量的证据。告诉用户主题在出厂时就有问题，并建议使用 codex-theme-creator 修复它；只有在用户明确表示无论如何都要保留无法阅读的主题时，才传递 `--force`。

## 第 3 步：验证——`scheduled` 不是成功

```bash
npx tsx scripts/switch-theme.ts status
```

`status` 探测每个活动的 Codex 页面，并报告 `active`（所有页面都已主题化，一个主题 id）、`partial`（页面不一致——重新应用以使它们收敛）或 `inactive`，以及每页的证据。只有在 `status` 显示预期主题 id 的 `active` 时才向用户报告成功。如果 `--launch` 后仍然 `inactive`，请读取 `~/.codexthemes/state/launch.log` 获取助手的結果。

如果 **旧主题在成功热切换后仍然回来**（来自先前任务的陈旧会话仍然在注入它，并且其注册无法从该会话外部移除），则获取用户的重启权限并强制干净重启——永远不要要求用户手动退出应用程序：

```bash
npx tsx scripts/switch-theme.ts apply <theme-id> --launch --relaunch
```

`--relaunch` 即使端点已经活动也会重启 Codex，这将清除所有陈旧会话，然后注入请求的主题。它遵循相同的 `scheduled` → `status` 验证流程。

## 第 4 步：始终给用户逃生通道

每个成功的应用报告都必须声明 `active` 输出的背景范围，以便用户永远不会对艺术作品仅限于主页感到惊讶。以 plain language 传递 `backgroundScopeNote`，例如： "背景艺术作品仅在主页上显示；颜色适用于每个页面。要在对话页面上也显示它，请要求 codex-theme-creator 使用 backgroundScope: workspace 重新构建。" 然后以撤销提示结束，例如： "回复 `rollback` 以返回您之前拥有的主题，或 `restore` 以恢复原生 Codex 外观——完全退出 Codex 也会移除主题。" 不喜欢结果的用户永远不需要询问如何撤销或如何更改范围。

每次应用都会记录之前活动的主题。当用户回复 `rollback`（或说新主题有缺陷、难看或不是他们想要的）：

```bash
npx tsx scripts/switch-theme.ts rollback
```

这将重新应用之前活动的主题，或者在没有活动主题时恢复原生外观。它通过相同的应 用流程运行，因此可读性门禁和 `status` 验证仍然适用。（一个未通过可读性门禁的主题永远不需要手动撤销——应用会自动还原。）

当用户要求原生外观（或回复 `restore`）：

```bash
npx tsx scripts/switch-theme.ts restore
```

从每个页面上移除注入的样式和页面标记并清除运行时状态——无需重启。完全退出应用程序也会移除主题；当用户想要它时使用 `--launch` 重新应用。如果恢复后主题仍然出现，则陈旧会话正在注入它——使用第 2 步的 `--launch --relaunch` 流程并获取用户许可，或者让他们完全退出并重新打开 Codex。

## 边界

- 在任何重启之前请求许可；热切换只需要用户切换请求的许可。
- 涉及重启时，永远不要单独根据 `apply` 输出就声称主题是活动的——用 `status` 验证。
- 永远不要修改 `app.asar`、签名的应用程序包、用户任务或认证数据。
- 不要在此处编辑主题源；将设计更改路由到 codex-theme-creator。
