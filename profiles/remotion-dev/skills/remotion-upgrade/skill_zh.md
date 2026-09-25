# 升级 Remotion

1. 检查项目清单文件和锁定文件，以识别包管理器和工作区。保留无关的更改。
2. 确认 `@remotion/cli` 是否本地可用。如果可用，运行：

   ```bash
   npx remotion upgrade
   ```

   这也会更新项目本地的 Remotion 技能。跳过下面的手动升级步骤。
3. 如果 `@remotion/cli` 不可用，手动升级：
   - 使用 `npm view remotion version` 获取最新稳定版本的 Remotion。
   - 查找项目中所有已安装的 `remotion` 和 `@remotion/*` 依赖，并将它们全部升级到该确切版本。保留它们的依赖部分和项目的工作区或目录约定。
   - 使用 `npm view @remotion/studio@<version> dependencies --json` 读取目标 Remotion 版本的 `@remotion/studio` 依赖。将安装的辅助包（如 `zod`、`mediabunny` 和 `@huggingface/transformers`）与此处列出的版本对齐。使用 `mediabunny` 版本更新安装的 `@mediabunny/*` 包。
   - 运行项目的包管理器以更新其锁定文件。
4. 如果 `@remotion/cli` 不可用，更新已安装的 Remotion 技能：

   ```bash
   npx skills update remotion-best-practices remotion-captions remotion-create remotion-docs remotion-interactivity remotion-maps remotion-markup remotion-multimedia remotion-render remotion-saas remotion-studio remotion-upgrade --yes
   ```
5. 审查清单文件和锁定文件的差异。确保所有 Remotion 包使用同一版本，已安装的辅助包使用其推荐版本。如果 CLI 可用，运行 `npx remotion versions` 作为附加检查。

[Remotion 发布版本](https://github.com/remotion-dev/remotion/releases) 包含变更日志，升级后总结相关更改时可能有用。
