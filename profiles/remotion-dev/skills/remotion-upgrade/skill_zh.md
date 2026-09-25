# 升级 Remotion

1. 检查项目的清单和锁文件，以识别包管理器和工作区。保留无关更改。
2. 确定 `@remotion/cli` 是否在本地可用。如果是，请运行：

   ```bash
   npx remotion upgrade
   ```

   这也将更新项目本地的 Remotion 技能。请跳过下方的手动升级。

3. 如果 `@remotion/cli` 不可用，则手动升级：
   - 使用 `npm view remotion version` 获取最新的稳定版 Remotion 版本。
   - 在项目中查找所有已安装的 `remotion` 和 `@remotion/*` 依赖，并将它们全部升级到该确切版本。保留它们各自的依赖部分以及项目的工作区或目录约定。
   - 使用 `npm view @remotion/studio@`dependencies --json` 读取目标 Remotion 版本的 `@remotion/studio` 依赖。将已安装的辅助包（如 `zod`、`mediabunny` 和 `@huggingface/transformers`）与列出的版本对齐。使用 `mediabunny` 版本来升级已安装的 `@mediabunny/*` 包。
   - 运行项目的包管理器以更新其锁文件。
4. 如果 `@remotion/cli` 不可用，则更新已安装的 Remotion 技能：

   ```bash
   npx skills update remotion-best-practices remotion-captions remotion-create remotion-docs remotion-interactivity remotion-maps remotion-markup remotion-multimedia remotion-render remotion-saas remotion-studio remotion-upgrade --yes
   ```

5. 审查清单和锁文件的差异。确保所有 Remotion 包使用同一版本，且已安装的辅助包使用推荐版本。如果 CLI 可用，运行 `npx remotion versions` 作为额外检查。

[Remotion 发布](https://github.com/remotion-dev/remotion/releases) 包含更新日志，在升级后进行总结相关变更时可能很有用。
