# VS Code 扩展本地化

这项技能可以帮助你本地化 VS Code 扩展的各个方面

## 何时使用这项技能

当你需要时使用这项技能：
- 本地化新的或现有的贡献配置（设置）、命令、菜单、视图或引导
- 本地化扩展源代码中包含的新或现有的消息或其他字符串资源，这些资源会显示给最终用户

# 指令

VS Code 本地化由三种不同的方法组成，具体取决于正在本地化的资源。当创建或更新新的可本地化资源时，必须为所有当前可用的语言创建/更新相应的本地化内容。

1. 在 `package.json` 中定义的设置、命令、菜单、视图、`ViewsWelcome`、引导标题和描述等配置
  -> 一个专属的 `package.nls.LANGID.json` 文件，例如巴西葡萄牙语（`pt-br`）本地化的 `package.nls.pt-br.json`
2. 引导内容（定义在其自身的 `Markdown` 文件中）
  -> 一个专属的 `Markdown` 文件，例如巴西葡萄牙语本地化的 `walkthrough/someStep.pt-br.md`
3. 扩展源代码中（JavaScript 或 TypeScript 文件）的消息和字符串
  -> 一个专属的巴西葡萄牙语本地化 `bundle.l10n.pt-br.json`
