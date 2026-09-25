您根据 [elevenlabs-dx](https://github.com/elevenlabs/elevenlabs-dx) 中的合并周变更日志更新 ElevenLabs 代理技能。不要阅读 GitHub 问题。当技能文件发生变化时，在这个仓库中打开一个拉取请求。

技能文件是当前行为的永续源真实现象文档。使用变更日志来发现发生了什么变化，但将最终的 `SKILL.md` 和 `references/*.md` 内容编写为永恒的现在时态文档。

技能文件是用于与 ElevenLabs 合作的高级、任务导向的指导。它们并不是为了镜像变更日志或 API 参考中的每个细微差别。优先记录主要工作流、核心功能和重要配置表面。通常省略边缘情况、优先级链、持久化机制、回退顺序、实现细节和狭窄的例外，除非省略它们会使技能实质上误导或无法使用。

## 工作流

1. 从自动化触发或用户消息中解析 `CHANGELOG_DATE`。
2. 从 `elevenlabs-dx` 的 `main` 获取合并的变更日志。
3. 应用相关性过滤器。如果没有技能受影响，则停止。
4. 读取每个受影响的技能文件和参考文件。
5. 验证每个候选更新与规范源文档。
6. 仅应用通过适配门控的针对性、永续的技能编辑。
7. 自检所有编辑。
8. 创建 `skills-update/YYYY-MM-DD`，提交、推送并打开一个 PR。

不要修改变更日志未提及的技能。

## 第 1 步：获取变更日志

从自动化触发或用户消息中确定 `CHANGELOG_DATE` (`YYYY-MM-DD`)。

获取合并的变更日志文件：

```bash
gh api "repos/elevenlabs/elevenlabs-dx/contents/fern/docs/pages/changelog/${CHANGELOG_DATE}.md?ref=main" \
  --jq '.content' | base64 -d > "/tmp/changelog-${CHANGELOG_DATE}.md"
```

如果文件不存在，则停止并报告该日期没有找到合并的变更日志。

在需要时也读取已发布的页面：

`https://elevenlabs.io/docs/changelog#${CHANGELOG_DATE}T00:00:00.000Z`

## 第 2 步：应用相关性过滤器

读取 `/tmp/changelog-${CHANGELOG_DATE}.md` 并将变更映射到以下技能：

| 技能 | 触发更新的内容 |
| --- | --- |
| `text-to-speech` | 新/弃用的模型、新的 TTS 参数、语音设置更改、输出格式更改、SDK 方法签名更改 `text_to_speech.convert()` |
| `speech-to-text` | 新的转录模型、新参数、响应模式更改、SDK 方法更改 |
| `agents` | 新的 LLM 提供者/模型、新的工具类型、新的代理配置字段、对话配置模式更改、新的 CLI 命令、小部件更改、过程端点/字段/类型更改、结构化过程验证规则、编译或发布行为、SDK 方法更改 `conversational_ai.agents.procedures` 或 `conversationalAi.agents.procedures` |
| `sound-effects` | 新的生成参数、模型更改、SDK 方法更改 |
| `music` | 新的端点、新参数、模型更改 |
| `voice-isolator` | 新参数、模型更改、SDK 方法更改 `audio_isolation.convert()` |
| `speech-engine` | 语音引擎 WebSocket API 更改、对话令牌更改、SDK 方法更改实时语音对话 |
| `voice-changer` | 新的语音到语音参数、模型更改、SDK 方法更改 `speech_to_speech.convert()` 或 `speechToSpeech.convert()` |
| `setup-api-key` | 身份验证流程更改、API 密钥仪表板更改、环境变量指导 |

如果变更影响模型表、代码示例、参数文档、配置表或 CLI 命令，则该变更是相关的。

如果变更仅影响内部/管理 API、没有使用级影响的可选字段、向后兼容的重命名或与 API 密钥设置流程无关的定价/仪表板 UI，则该变更是不相关的。

如果没有技能受影响，则成功停止，无需打开拉取请求。报告 `No skills-relevant changes for CHANGELOG_DATE`。

对于每个相关的项，记录受影响的技能和受影响的区域，例如模型表、代码示例、LLM 提供者表、工具部分、CLI 部分、参数文档或配置表。

## 第 3 步：读取当前技能文件

对于每个受影响的技能，读取：

- `{skill}/SKILL.md`
- `{skill}/references/` 中的所有文件

技能目录：

- `text-to-speech/` (`SKILL.md` 加上 `references/installation.md`、`references/streaming.md`、`references/voice-settings.md`)
- `speech-to-text/` (`SKILL.md` 加上 `references/installation.md`、`references/transcription-options.md`、`references/realtime-server-side.md`、`references/realtime-client-side.md`、`references/realtime-commit-strategies.md`、`references/realtime-events.md`)
- `agents/` (`SKILL.md` 加上 `references/installation.md`、`references/agent-configuration.md`、`references/client-tools.md`、`references/widget-embedding.md`、`references/outbound-calls.md`、`references/using-procedure-api.md`、`references/writing-procedures.md`)
- `sound-effects/` (`SKILL.md` 加上 `references/installation.md`)
- `music/` (`SKILL.md` 加上 `references/installation.md`、`references/api_reference.md`)
- `voice-isolator/` (`SKILL.md` 加上 `references/installation.md`)
- `speech-engine/` (`SKILL.md` 加上 `references/installation.md`、`references/javascript-sdk-reference.md`、`references/python-sdk-reference.md`)
- `voice-changer/` (`SKILL.md` 加上 `references/installation.md`)
- `setup-api-key/` (`SKILL.md` 仅)

## 第 4 步：验证源文档

编辑之前，获取并读取实际源材料。变更日志告诉您发生了什么变化；API/参考文档告诉您应如何记录当前行为。

对于常见区域，从以下开始：

- 代理：`https://elevenlabs.io/docs/api-reference/agents/create`、`https://elevenlabs.io/docs/api-reference/agents/update`
- TTS：`https://elevenlabs.io/docs/api-reference/text-to-speech/convert`
- STT：`https://elevenlabs.io/docs/api-reference/speech-to-text/convert`

对于每个记录的字段、参数、模式、枚举、端点、模型 ID 或 SDK 方法：

- 在源文档中验证确切的字段名、类型、嵌套、允许值和方法签名。
- 不要从变更日志措辞中推断模式。
- 如果一个功能出现在变更日志中但源文档没有提供足够的模式细节，则不要为其编写字段表或代码示例。将其放在报告中的 `Needs Manual Authoring` 下。

## 第 5 步：判断每个项是否适用

在编辑每个变更日志项之前运行这个适配门控：

1. 映射到现有部分、表格、列表或示例中的自然位置。
2. 仅包括主要功能、常见工作流或重要顶级配置概念。
3. 跳过次要细节：边缘情况、优先级规则、持久化细节、回退顺序、实现细节、狭窄的例外或弃用说明。
4. 优先无操作而不是强制结构。如果不存在自然位置，则保持技能文件不变，并在报告中报告 `No Skill Change Needed`。
5. 只有当概念是重要的、可重用的、用户面、高级的，并且当前结构中明显缺失时，才添加新部分。
6. 优先当前路径。如果一个字段、端点、模型、包或模式替换了另一个，记录当前支持的方式并保留弃用上下文在报告中。

好的匹配：

- 向现有模型表中添加一个新的支持模型行。
- 向现有参数表中添加一个新的顶级参数。
- 当方法签名更改时，更新现有的 Python、JavaScript 和 CLI 示例。

不好的匹配：

- 仅仅为了提及变更日志项而在不相关的部分之间插入一个独立的句子。
- 添加弃用的字段、移除的枚举值、旧包名或迁移警告，除非技能已经有明确的迁移/故障排除部分，并且需要在此处进行更改。
- 记录内部优先级、本地持久化行为、回退链或罕见例外行为。

## 第 6 步：进行针对性编辑

将最小的有用更改应用到正确的文件和部分。匹配现有的标题级别、表格格式、代码块语言、缩进和命名风格。

更新模式：

- **模型表**：在相关的 `SKILL.md` 模型表中添加、删除或修改行。验证模型 ID 和描述。
- **代码示例**：更新方法签名、导入和重要参数。当所有都存在时，保持 Python、JavaScript 和 CLI 示例一致。
- **LLM 提供者表**：更新 `agents/SKILL.md` 或 `agents/references/agent-configuration.md`。
- **工具部分**：使用现有风格在 `agents/SKILL.md` 中更新新的工具类型。
- **CLI 部分**：更新 `agents/` 文件中现有的 CLI 示例。
- **参数文档**：将验证的参数添加到相关参数列表或表格。
- **配置表**：更新参考文件（如 `agent-configuration.md` 或 `voice-settings.md`）中的字段表。
- **输出格式表**：更新 `text-to-speech/SKILL.md` 中的输出格式表。

硬规则：

- 不要编造字段名、类型、模式、模型 ID、配置名、端点路径或示例值。
- 不要在没有验证确切 API 形状的情况下为新的功能编写代码示例。
- 将变更日志视为发现输入，而不是技能文件文本。
- 技能文件必须是永续的。不要在 `SKILL.md` 或 `references/*.md` 中提及变更日志、问题、PR、发布日期、“添加于”、“引入于”、“自”、“现在支持”。
- 记录当前积极的工作流，而不是负面历史。
- 不要仅仅因为变更日志有一个要点就创建一个新部分。
- 不要插入孤儿内容。
- 保持表格专注于当前支持的字段。
- 如果 SDK 版本升级没有方法签名更改，则只有在此类评论已经存在的情况下才更新版本特定评论。

## 第 7 步：提交前自检

审查每个更改并验证：

1. 每个编辑的字段名在步骤 4 中读取的源文档中。
2. 每个代码示例使用验证的参数名和嵌套。
3. 没有单独从变更日志措辞中推断的内容。
4. 没有编造的值。
5. 没有编辑的技能文件引用变更日志、问题、PR、发布日期或发布历史措辞。
6. 每个新标题或部分都有步骤 5 的理由。
7. 没有孤立的句子或强制性的单个部分。
8. 没有编辑的内容记录弃用的、移除的或替换的字段仅作为负面指导。
9. 每个相关的变更日志项都作为以下之一进行记录：文档更新、合理的新闻部分、`No Skill Change Needed` 或 `Needs Manual Authoring`。

如果任何更改未通过此检查，请撤销该编辑并将该项移至 `Needs Manual Authoring` 或 `No Skill Change Needed`。

## 第 8 步：分支、提交和拉取请求

使用分支名 `skills-update/YYYY-MM-DD`。

在创建分支之前，检查是否存在打开的 PR，如果存在则停止：

```bash
gh pr list --repo elevenlabs/skills --head "skills-update/${CHANGELOG_DATE}" --state open --json number --jq 'length == 0'
```

从当前的 `origin/main` 创建分支，只有在文件更改时才提交，并推送：

```bash
git fetch origin main
git checkout -b "skills-update/${CHANGELOG_DATE}" origin/main
git add -A
git diff --cached --quiet || git commit -m "Update skills from changelog ${CHANGELOG_DATE}"
git push -u origin "skills-update/${CHANGELOG_DATE}"
```

将报告写入 `/tmp/skills-update-report.md`，然后打开 PR：

```bash
gh pr create --repo elevenlabs/skills \
  --base main \
  --head "skills-update/${CHANGELOG_DATE}" \
  --title "Update skills from changelog ${CHANGELOG_DATE}" \
  --body-file /tmp/skills-update-report.md
```

如果分析后没有文件更改，则不要推送或打开 PR。报告 `No skill file changes needed for CHANGELOG_DATE` 并在 `No Skill Change Needed` 下记录相关项。

## 报告和 PR 正文要求

编写此报告并将其用作 PR 正文：

```markdown
# Skills Update Report

## 结果

- 变更日志：`YYYY-MM-DD`
- 分支：`skills-update/YYYY-MM-DD`
- 提交：`<提交哈希或"No commit created">`
- 拉取请求：`<PR URL或"No PR created">`
- 结果：`<更新技能 | 没有技能更改需要 | 部分更新>`

## 摘要

根据合并的每周变更日志更新技能。

如果变更日志描述了破坏 API 或 SDK 的更改，请在此处添加简短警告，描述哪些示例或文档可能需要迁移指导。

### 更改

- **skill-name**：对更改的简要描述。

### 验证

- `field_or_area` in `file.md` - 验证对 [API 参考页面](url)

### 需要手动编写

列出未应用因模式无法验证的变更日志项。包括变更日志中的内容、无法验证的原因以及稍后检查的源链接。

如果没有适用项，请写 "None."

### 没有技能更改需要

列出故意未添加到技能文件中的已验证变更日志项，因为它们没有自然位置或太低级。包括更改内容、为什么不适用编辑以及源链接。

如果没有适用项，请写 "None."

### 开放性问题

列出阻塞项、模糊的源材料或后续项。

如果没有适用项，请写 "None."

### 源

[变更日志 YYYY-MM-DD](https://elevenlabs.io/docs/changelog#YYYY-MM-DDT00:00:00.000Z)
[GitHub 上的变更日志文件](https://github.com/elevenlabs/elevenlabs-dx/blob/main/fern/docs/pages/changelog/YYYY-MM-DD.md)
```

在具有仓库写入访问权限的自动化/无头代理环境中运行时，除非没有技能文件更改，否则打开拉取请求是必需的。除非用户明确要求额外的评论，否则仅在最终响应中返回完成的 Markdown 报告。

## 重要

- 除非变更日志明确要求，否则不要更改技能文件中的 YAML 前置内容。
- 仅在报告/PR 上下文中保留变更日志日期和发布历史措辞。
- 当变更日志项没有自然位置时，优先无操作而不是强制结构。
- 错误的代码示例比缺失的代码示例更糟。
- 如果变更日志覆盖仅提供功能名称和高级描述，而没有源文档或模式细节，请将这些项放在 `Needs Manual Authoring` 下。
