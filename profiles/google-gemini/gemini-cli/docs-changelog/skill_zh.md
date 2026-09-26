# 程序：更新新版本发布日志

## 目标

标准化基于自动化发布信息更新日志文件（`latest.md`、`preview.md`、`index.md`）的过程。

## 输入

- **version**：发布版本字符串（例如，`v0.28.0`、`v0.29.0-preview.2`）。
- **TIME**：发布时间戳（例如，`2026-02-12T20:33:15Z`）。
- **BODY**：原始 Markdown 发布说明，包含“变更内容”部分和“完整变更日志”链接。

## `latest.md` 和 `preview.md` 突出显示指南

- 目标是 **3-5 个关键突出显示点**。
- 每个突出显示点必须以粗体标题开头，总结变更（例如，`**新功能：** 简要描述...`）。
- **优先**总结新功能，而不是其他如错误修复或常规任务等变更。
- **避免**在稳定发布中提及“实验性”或“预览”中的功能。
- **不要**在这些突出显示中包含 PR 编号、链接或作者名称。
- 参考 `.gemini/skills/docs-changelog/references/highlights_examples.md` 获取正确的风格和语气。

## 初始处理

1.  **分析版本**：根据 `version` 字符串确定发布路径。
    - 如果 `version` 包含“nightly”，**停止**。不进行任何更改。
    - 如果 `version` 以 `.0` 结尾，遵循 **路径 A：新次版本** 程序。
    - 如果 `version` 不以 `.0` 结尾，遵循 **路径 B：补丁版本** 程序。
2.  **处理时间**：将 `TIME` 输入转换为两种格式以供后续使用：`yyyy-mm-dd` 和 `Month dd, yyyy`。
3.  **处理 BODY**：
    - 将传入的 `BODY` 内容保存到临时文件以进行处理。
    - 在临时文件的“变更内容”部分中，将所有拉取请求 URL 重新格式化为 Markdown 链接，PR 编号为文本（例如，`[#12345](URL)`）。
    - 如果存在“新贡献者”部分，则删除它。
    - 保留“**完整变更日志**”链接。此临时文件的已处理内容将用于后续步骤。

---

## 路径 A：新次版本

*如果版本号以 `.0` 结尾，请使用此路径。*

**重要提示**：根据版本，您必须选择遵循稳定发布的部分 A.1 或预览发布的部分 A.2。不要遵循另一部分的说明。

### A.1：稳定发布（例如，`v0.28.0`）

对于稳定发布，您将根据日志生成两个不同的摘要：主日志页面的简洁**公告**和更详细的发布特定页面的**突出显示**部分。

1.  **为 `index.md` 创建公告**：
    - 生成一个简洁的公告，总结最重要的变更。
        每个公告条目必须以总结变更的粗体标题开头。
    - **重要提示**：此公告的格式是独特的。您**必须**使用 `docs/changelogs/index.md` 中的现有公告和 `.gemini/skills/docs-changelog/references/index_template.md` 中的示例作为您的指南。此格式包括 PR 链接和作者。坚持 1 或 2 个 PR 链接和作者。
    - 将此新公告添加到 `docs/changelogs/index.md` 的顶部。

2.  **创建突出显示并更新 `latest.md`**：
    - 生成一个全面的“突出显示”部分，遵循上述“`latest.md` 和 `preview.md` 突出显示指南”中的指南。
    - 从 `.gemini/skills/docs-changelog/references/latest_template.md` 获取内容。
    - 使用 `version`、`release_date`、生成的 `highlights` 和从临时文件中处理的内
    容填充模板。
    - **完全替换** `docs/changelogs/latest.md` 的内容为填充的模板。

### A.2：预览发布（例如，`v0.29.0-preview.0`）

1.  **更新 `preview.md`**：
    - 生成一个全面的“突出显示”部分，遵循突出显示指南。
    - 从 `.gemini/skills/docs-changelog/references/preview_template.md` 获取内容。
    - 使用 `version`、`release_date`、生成的 `highlights` 和从临时文件中处理的内
    容填充模板。
    - **完全替换** `docs/changelogs/preview.md` 的内容为填充的模板。

---

## 路径 B：补丁版本

*如果版本号**不**以 `.0` 结尾，请使用此路径。*

**重要提示**：根据版本，您必须选择遵循稳定补丁的部分 B.1 或预览补丁的部分 B.2。不要遵循另一部分的说明。

### B.1：稳定补丁（例如，`v0.28.1`）

- **目标文件**：`docs/changelogs/latest.md`
- 对目标文件执行以下编辑：
    1.  更新主标题中的版本。该行应读取，`# Latest stable release: {{version}}`
    2.  更新发布日期。该行应读取，`Released: {{release_date_month_dd_yyyy}}`
    3.  确定临时文件中是否存在“变更内容”部分
        如果存在，继续到步骤 4。否则，跳到步骤 5。
    4.  **前置**从临时文件中处理的“变更内容”列表到 `latest.md` 中现有的“变更内容”列表。不要更改或替换现有列表，**仅添加**到其开头。
    5.  在“完整变更日志”中，仅编辑 URL 的末尾。识别看起来像 `...{previous_version}` 的 URL 的最后一部分，并将其更新为 `...{version}`。

        示例：假设补丁版本是 `v0.29.1`。将 `Full Changelog: https://github.com/google-gemini/gemini-cli/compare/v0.28.2…v0.29.0` 更改为
        `Full Changelog: https://github.com/google-gemini/gemini-cli/compare/v0.28.2…v0.29.1`

### B.2：预览补丁（例如，`v0.29.0-preview.3`）

- **目标文件**：`docs/changelogs/preview.md`
- 对目标文件执行以下编辑：
    1.  更新主标题中的版本。该行应读取，`# Preview release: {{version}}`
    2.  更新发布日期。该行应读取，`Released: {{release_date_month_dd_yyyy}}`
    3.  确定临时文件中是否存在“变更内容”部分
        如果存在，继续到步骤 4。否则，跳到步骤 5。
    4.  **前置**从临时文件中处理的“变更内容”列表到 `preview.md` 中现有的“变更内容”列表。不要更改或替换现有列表，**仅添加**到其开头。
    5.  在“完整变更日志”中，仅编辑 URL 的末尾。识别看起来像 `...{previous_version}` 的 URL 的最后一部分，并将其更新为 `...{version}`。

        示例：假设补丁版本是 `v0.29.0-preview.1`。将 `Full Changelog: https://github.com/google-gemini/gemini-cli/compare/v0.28.2…v0.29.0-preview.0` 更改为
        `Full Changelog: https://github.com/google-gemini/gemini-cli/compare/v0.28.2…v0.29.0-preview.1`

---

## 完成

- 更改后，如果 `npm run format` 失败，可能需要先运行 `npm install` 以确保所有格式化依赖项可用。然后，运行 `npm run format` 以确保一致性。
- 删除在过程中创建的任何临时文件。
