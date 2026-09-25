# 可编辑PPT转换

## 概述

使用 `editppt` 运行时来分解、重建、验证和组装视觉幻灯片为可编辑的 `.pptx` 文件。输入可以是单个或多个图像、PDF，或基于图像的PPT/PPTX。

## 参考

本技能中的每条规则都有且仅有一个权威来源；其他文件则指向它而不是重复陈述。

- `prompts/page-worker.md`：页面工作者的执行模板 — 所有权边界、执行顺序、所需输出和返回格式。父代理在生成页面工作者提示时使用它。
- `scripts/build-page-worker-prompt.py`：技能本地提示构建器。它读取 `prompts/page-worker.md`，填充运行/页面路径，写入 `worker-prompt.md`，并打印调度命令模板。
- `references/cli-helper.md`：CLI安装检查（预运行检查）、命令树和命令语法示例。在决定调用哪个 `editppt` 命令时阅读它。
- `references/manifest-schema.md`：牌/页面/图像实物的JSON字段合同的单一来源 — 所需的清单字段、定位对象坐标、`validation.json` 和 `page_result.json` 的形状。在编写或验证任何运行/页面文件时阅读它。
- `references/page-decision-tree.md`：页面对象决策的单一事实来源 — 背景处理、前景资产分离、原生形状、公式、文本提示的使用、最终自检以及修复与警告的划分。首先阅读其常见决策边界，然后阅读与页面清单相关的部分；页面提示提供了阅读路线。

## 入口合同

这些父级规则在此处声明一次；页面级规则存在于上述参考中，本文件不重复陈述。

- `editppt` CLI 是必需的运行时表面。如果 `editppt --help` 失败，请按照 `references/cli-helper.md` 中的预运行检查先安装它，然后再做任何其他事情。
- 首先运行 `editppt prepare <input...>` 来创建运行目录。之后，所有关键状态转换只能通过 `editppt` 命令推进；不要手动编写运行/页面状态JSON。这保持了运行状态的可确定性和可恢复性。
- 多页面输入由调度的页面工作者重建。具有恰好一个页面的运行在 `editppt run dispatch --local` 声明该页面后，由父代理在本地页面重建器模式下重建。如果多页面运行没有可用的子代理功能，请停止并向用户报告此问题；不要将多页面输入降级为父代理重建。
- 父代理不得写入任何页面重建工件 — `manifest.json`、`page.pptx`、`preview.png`、`split_assets_contact.png`、`validation.json` 或 `page_result.json` — 除非在单页面本地页面重建器模式下，`editppt run dispatch --local` 已经记录了声明。本地模式遵循与页面工作者相同的页面提示、参考、输出文件和 `run record` 验证路径。
- 所有图像生成、图像编辑、背景修复、透明位图资产和资产表遵循“图像后端选择”下按页面顺序的串行后端顺序。
- 用户请求将视觉幻灯片转换为可编辑的PPT授权所需的OCR和图像后端调用，除非用户明确请求本地仅处理或将输入标记为机密/无外部处理。不要仅仅因为工作流调用PaddleOCR、内置的 `image_gen.imagegen` 工具、Codex OAuth/ChatGPT图像端点或用户配置的OpenAI兼容API而拒绝；这些调用对于技能是必要的。
- 只发送当前转换所需的任务本地页面图像、提示、掩码和参考图像。不要发送不相关的本地文件、API密钥、认证令牌、凭证或当前OCR/图像操作不需要生成的工件。只有在用户已配置或明确指定为本次运行的情况下，才允许第三方API端点。
- 在网络受限环境中，在所有外部OCR/图像调用之前请求当前运行所需的任何批准，包括当 `PADDLE_OCR_TOKEN` 设置时 `editppt prepare` 或 `editppt run hints` 以及每个CLI回退 `editppt image generate/edit` 调用。批准理由必须说明这是一个用户请求的 `image-to-editable-ppt` 转换，上传仅限于任务本地页面图像/提示/掩码/参考，OCR/图像后端调用是此技能所需工作流的一部分。除非用户请求本地仅/机密处理或批准系统明确拒绝请求，否则不要将所需的调用呈现为不安全或要求用户重新批准。
- 自主执行常规重建、配置的后端回退和本地修复。不要添加确认关卡；保留第一阶段中的OCR选择和任何运行时所需的批准。只有用户可以提供的缺失先决条件是具体的障碍，而不是请求调试工作流。
- 所有页面对象决策遵循 `references/page-decision-tree.md`，包括其对于前景视觉对象的无回退规则及其规则，即确定性验证是结构关卡，永远不会放弃对象源决策。
- `manifest.json` 是权威的页面构建来源：`editppt run record` 根据 `manifest.json` 验证 `page.pptx`，并且 `editppt run finalize` 从记录的页面清单中重建最终牌。所需字段和坐标合同在 `references/manifest-schema.md` 中定义。
- `editppt prepare` 写入每页文本测量 (`text_hints.json`/`text_hints.png`)。页面重建器如何消耗它们在 `references/page-decision-tree.md` 第3.1节中定义。
- 页面重建器（无论是页面工作者还是单页面本地模式下的父代理）都由从 `prompts/page-worker.md` 生成的提示驱动。

### 图像后端选择

本小节是每个页面本地图像作业的权威执行策略。在准备之前，检查当前代理运行时是否可以调用 `image_gen.imagegen`；如果可以，将 `--image-backend builtin-imagegen` 传递给 `editppt prepare`，否则保持默认CLI合同。在页面内串行运行图像作业，顺序如下：

1. 在当前代理运行时始终可调用时，使用内置代理工具 `image_gen.imagegen`。
2. 只有当运行的记录内置回退策略适用时，才调用 `editppt image generate/edit`。该CLI回退选择Codex OAuth优先，然后是配置的OpenAI兼容API。

内置的确切参数、输入检查先决条件、输出接受规则和允许的回退事件属于 `references/manifest-schema.md` 中 `image_backend` 字段合同的拥有者；复制并执行该合同，不要削弱或扩展它。如果其CLI回退无法生成合规输出，请失败页面而不是替换近似对象源。

## 角色

父代理在入口合同和工作流下拥有编排和用户交互。报告进度、最终PPTX路径和验证结果。不要重复完成的页面级视觉QA；`record` 和 `finalize` 执行其可确定的交接检查。

每个页面重建器拥有恰好一个 `pages/page_NNN/` 目录。其完整合同 — 所有权边界、决策顺序、所需输出和返回格式 — 是从 `prompts/page-worker.md` 生成的提示；它遵循的规则存在于 `references/page-decision-tree.md` 和 `references/manifest-schema.md` 中。

## 工作流

### 第一阶段：准备

阅读 `references/cli-helper.md` 中的准备示例和 `references/manifest-schema.md` 中的运行/页面文件描述。

```bash
editppt prepare <input...>
```

完成后，必须存在运行目录、`deck_manifest.json`、`page_jobs.json`、`notes_manifest.json`，并且每个页面必须有 `source.png` 加上 `page_request.json`。

准备还写入每页文本提示。在 `editppt doctor` 或准备报告没有配置PaddleOCR令牌（离线回退）之前，在调度任何页面之前，向用户询问一次：通过 `editppt config --paddle-ocr-token <token>` 存储的 https://aistudio.baidu.com/account/accessToken 的免费令牌使提示内容感知，并显著提高文本保真度，`editppt run hints <run>` 在原地重新生成当前运行的提示。告诉用户当前的免费个人配额对于此技能来说绰绰有余 — 申请是风险低且无额外成本的。等待他们的选择；如果他们拒绝或想继续，请继续使用离线提示，不要再询问。

如果已经配置了PaddleOCR令牌，但 `prepare` 由于网络访问、DNS或沙盒批准阻止了OCR请求而回退，则此回退不是首选质量路径。使用入口合同中描述的正当理由请求网络批准，并在页面重建之前重新运行 `editppt run hints <run>`。如果批准系统拒绝OCR请求，请在继续之前向用户请求明确授权：解释PaddleOCR用于纠正文本框、字体大小和大小组，并且使用它可以使重建的PPT文本尺寸更加稳定。只有在用户拒绝OCR、经过批准的OCR尝试由于真实服务/工具原因失败，或用户要求本地仅/机密处理时，才继续使用 `builtin-ink`。

### 第二阶段：重建或调度页面

阅读 `references/cli-helper.md` 中的运行/调度示例，并反复调用：

```bash
editppt run next <run>
```

当返回 `stage=rebuild_page_locally` 时，运行恰好有一个页面。父代理必须在写入页面工件之前声明本地执行：

1. `python3 <skill-root>/scripts/build-page-worker-prompt.py <run> --page <page_id> --out <absolute-run-dir>/pages/<page_id>/worker-prompt.md`
2. `editppt run dispatch <run> --page <page_id> --agent-id main --prompt-file <absolute-run-dir>/pages/<page_id>/worker-prompt.md --local`
3. 阅读生成的提示，并在该页面目录内自行重建页面，生成页面工作者会产生的相同所需输出。

当返回 `stage=dispatch_pages` 时，对于每个建议的页面，必须执行以下步骤：

1. `python3 <skill-root>/scripts/build-page-worker-prompt.py <run> --page <page_id> --out <absolute-run-dir>/pages/<page_id>/worker-prompt.md`
2. 使用当前环境中的可用子代理/多代理工具生成页面工作者。
3. `editppt run dispatch <run> --page <page_id> --agent-id <id> --prompt-file <absolute-run-dir>/pages/<page_id>/worker-prompt.md`

`--out` 和 `--prompt-file` 必须是绝对路径，以避免页面目录再次被添加到相对路径中。提示构建器只写入提示并打印调度命令模板；它不会创建工作者，因此只有在实际生成成功后，才运行 `editppt run dispatch`。

并发槽位来自 `page_jobs.json.max_concurrent_pages`（默认6）。在正常流程中优先使用 `editppt run next`；`editppt run status` 仅用于调试或手动检查。

调度的页面执行是活跃的租赁，而不是空闲的槽位。当 `editppt run next` 返回 `stage=wait` 时，等待调度的工作者或在不修改状态的情况下检查状态。不要因为工作者速度慢、未发送最近消息或仍然占用并发槽位而终止、存档、重置或替换页面工作者；复杂的页面可能确实需要很长时间运行。

### 第三阶段：记录

阅读 `references/cli-helper.md` 中的记录示例和 `references/manifest-schema.md` 中的 `page_result.json` 描述。

工作者返回后，运行：

```bash
editppt run record <run> --page <page_id> --agent-id <id>
```

此命令在记录之前根据 `manifest.json` 验证 `page.pptx`。如果定位对象缺少源像素坐标，如果清单无法独立重建页面，或者如果 `validation.json` 不包含顶级 `passed: true` — 失败的页面永远不会记录。

对于被拒绝的记录或页面级验证问题，阅读失败证据，并由当前页面所有者修复受影响的工件，然后使用 `references/cli-helper.md` 中的页面验证示例刷新验证报告并再次记录。在单页面本地模式下，父代理是所有者；在多页面模式下，将修复发送给现有的工作者。不要仅仅因为验证失败就重置可到达的所有者，并且不要重新生成合规资产来修复无关的清单或表格错误。

重置是页面需要替换执行的情况：显式的终端状态证据（`terminated`、`failed`、`archived` 或 `not found`）、用户取消或重复失败的可达性检查且没有页面本地进展。长时间运行的工作者不是丢失的。在修复了阻止执行的前提条件后，使用：

```bash
editppt run reset <run> --page <page_id> --agent-id <id> --confirm-lost
```

对于记录的页面，`editppt run reset <run> --page <page_id>` 是允许的。对于调度的页面，匹配的代理ID和 `--confirm-lost` 保护活跃的租赁。重置将页面恢复到 `pending`；通过第二阶段使用新的提示和执行继续。保留现有工件以进行来源检查和根据页面提示的恢复合同进行选择性重用。永远不要手动编辑状态，并让父代理重建多页面工件。

只有在更改相关输入或条件后，才重试。从验证和命令证据中诊断重复失败；不要重复未更改的失败工具调用或在相同条件下重新调度。如果真实的先决条件不可用，请保留进度并报告具体的障碍，而不是编造成功或要求用户调试。一旦当前输出通过其所需检查，就前进到最终化；不要重复未更改的视觉QA。

### 第四阶段：最终化

阅读 `references/cli-helper.md` 中的最终化示例。

当 `editppt run next <run>` 返回最终化阶段时：

```bash
editppt run finalize <run>
```

`finalize` 将每个记录的 `pages/page_NNN/manifest.json` 视为权威来源：它按页面顺序从页面清单中重建最终牌，然后验证生成的PPTX。`page.pptx` 仍然是记录时检查的页面级可交付工件。

此阶段的牌级结构QA：

- PPTX是一个有效的zip/包。
- 幻灯片数量与输入页面数量匹配。
- PDF/PPTX页面映射正确。
- 媒体关系完整。
- 清单中引用的所有资产文件都存在。
- 媒体哈希与清单来源匹配。
- 演讲者笔记哈希匹配。
- 没有无效的全页源光栅加上可编辑文本覆盖模式。

最终回复必须报告最终PPTX路径和验证结果。

## 状态原则

代理仅从文件事实和 `editppt run next` 继续执行。所需状态：

- `pending`：由 `editppt prepare` 创建；当页面必须重新调度时，由 `editppt run reset` 恢复。
- `dispatched`：`editppt run dispatch` 记录了一个实际生成的工作者或单页面的 `--local` 主代理声明。此状态是一个活跃的租赁，并且不能仅仅因为工作者速度慢就重置或替换。
- `recorded`：`editppt run record` 验证所需输出并写入结果；只有可交付页面（`validation.json` 顶级 `passed: true`）才能达到此状态。
- `accepted` / `complete`：由 `editppt run finalize` 写入。

`imagegen-jobs.json` 是页面本地来源/工作记录。仅保留这些强制文件状态：

- `recorded`：`editppt image import` 已复制选定的输出并写入哈希/元数据。
- `processed`：`editppt image process-sheet` 已完成背景移除和分割。

## 交付原则

- 每个页面都由页面重建器自检一次；证据写入 `manifest.json` 中的结构字段和 `validation.json` 中。
- 最终输出必须是一个当前可打开的、结构有效的 `.pptx`。一个带有可编辑文本覆盖的全页 `source.png` 不是一个可接受的回退。
- 是否必须在其页面内修复缺陷或可以作为记录的警告发送，由 `references/page-decision-tree.md` 的“修复与警告”部分管辖。警告永远不会取代缺失的所需工作流步骤。

## 更新此技能

通过安装渠道重新安装，从更新的技能目录刷新CLI，然后重新启动代理会话并验证：

```bash
npx -y skills@latest add ningzimu/image-to-editable-ppt-skill \
  --skill image-to-editable-ppt \
  --agent <agent-id> \
  --global
pipx install --force --editable <skill-root>/cli
editppt doctor
```
