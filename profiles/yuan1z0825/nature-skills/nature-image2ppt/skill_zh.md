# Nature Image2PPT

将此目录用作完整的运行时环境。仅通过以下方式运行确定性操作：

```bash
python <image2ppt-root>/cli/image2ppt/cli.py <command> ...
```

使用 Python 3.10 或更高版本，并安装 `requirements.txt`。当存在专用环境时，在 macOS/Linux 上将 `<image2ppt-root>/.venv/bin/python` 替换每个 `python` 命令，在 Windows 上将 `<image2ppt-root>/.venv/Scripts/python.exe` 替换每个 `python` 命令。在 `doctor` 失败后不要继续；仅安装报告的缺失依赖项，然后重新运行。

不要发现或调用其他技能、CLI、提示、模式、模块或状态机。

## 逐步读取本地合约

始终读取 `references/workflow.md`。仅在设置或 `doctor` 失败时读取 `references/runtime-dependencies.md`，并在选择或排除 OCR 时读取 `references/ocr-text-hints-contract.md`。

在编写页面清单之前，读取 `references/page-decision-tree.md` 和 `references/manifest-schema.md`。仅添加该页面所需的参考：

- 结构化或复合页面：`references/region-decomposition.md` 和 `references/object-routing.md`；
- 箭头：`references/manifest-arrow-extension.md`；
- 光栅资源或图像后端工作：`references/assets-provenance-contract.md`。

在接收或交付输出之前，读取 `references/qa-contract.md`。

## 保持单一事实来源

- 将 `page_jobs.json` 视为唯一的页面状态来源。
- 将每个 `pages/page_NNN/manifest.json` 视为唯一的页面内容来源。
- 将 `deck_manifest.json` 视为最终组装来源。
- 仅使用 `prepare`、`run next/dispatch/record/reset/hints/finalize` 和本地 CLI 中的页面命令进行状态生命周期操作。
- 将语义区域证据保存在 `manifest.json.image2ppt_region_decomposition` 中。
- 不要创建第二个作业文件、重建计划、OCR 正常化器、页面控制器、打包器或最终路径。
- 让补充 QA 报告失败；不要让它改变生命周期状态。

## 将每个写入操作保留在其所属目录内

- 页面构建、验证、提示和 QA 可能仅在该页面目录内读取和写入。清单路径、记录的资产、公式、报告、预览和 `--out` 覆盖必须不使用 `..`、符号链接或绝对路径来脱离它。唯一的外部输入例外是显式图像工具结果提供给 `image import` 或作为 `process-sheet --asset-sheet-source`；它在成为构建依赖项之前被复制到页面中。
- 运行级清单和最终输出必须保留在准备好的运行目录内。最终化会重建到同一目录的临时文件中，并在成功构建后原子性地发布它。
- 将任何边界拒绝视为硬失败；不要将拒绝的文件复制回作用域并作为运行时输出呈现。

## 保持迁移前行为

- 将自包含视为路径/导入/入口点迁移，而不是重建行为的重新设计。
- 从完整本地基础层加上保留的 Image2PPT 配置文件层生成每个工作提示。不要压缩、重新解释或替换任何层。
- 当多个路径满足合约时，优先使用先前验证的视觉策略。保持简单的测量对象原生，并在原生重绘会降低保真度的任何地方保留有界的复杂资产。
- 不要重新编写接受的基线页面，仅仅是为了证明运行时独立性。

## 运行工作流

### 图像后端选择

当代理运行时暴露 `image_gen.imagegen` 时使用 `builtin-imagegen`；它是首选后端，因为工作器可以检查编辑输入并导入显式的本地结果。当内置工具不可用、出错、无法读取输入或返回没有有效本地输出时，才使用 CLI 图像合约。缺少可选参数（如模型、掩码、大小、质量或输出路径）从未授权回退。在 `imagegen-jobs.json` 中记录实际生产者和允许的回退原因。

CLI 图像合约在传输边界上是提供者中立的。仅当 GPT 图像模型 ID 时选择 `codex-oauth`。为任何提供者特定模型选择 `openai-compatible-api`，其端点实现 OpenAI 图像兼容的 `/images/generations` 和/或 `/images/edits` 模式。不要从任务的语言模型推断图像后端。当来源重要时使用显式后端；`auto` 仅用于兼容的 GPT 图像 ID，否则选择配置的 API，而不会将 Codex OAuth 凭据发送给第三方。

### 1. 预检查和 OCR 选择

```bash
python <image2ppt-root>/cli/image2ppt/cli.py doctor --json
```

当配置了 Baidu AI Studio `PADDLE_OCR_TOKEN` 时使用它。如果它不存在，请告诉用户一次，本地 `builtin-ink` 回退测量文本几何形状但不识别字符；在 `references/ocr-text-hints-contract.md` 中提供配置路径。尊重仅离线选择。

### 2. 准备一个运行

```bash
python <image2ppt-root>/cli/image2ppt/cli.py prepare <input...> \
  --out-root output/image2ppt --image-backend builtin-imagegen
```

要为可审计的来源固定配置的第三方提供者/模型，使用 `--image-backend openai-compatible-api` 准备。运行合约记录来自活动项目配置或环境的精确 `IMAGE2PPT_IMAGE_MODEL`；它不会仅仅因为未传递 `--model` 标志而替换 GPT 图像默认值。

仅在有意禁用 OCR 处理时使用 `--no-text-hints`。当需要时，无需创建新的运行即可重新生成提示：

```bash
python <image2ppt-root>/cli/image2ppt/cli.py run hints <run-dir>
```

### 3. 前进和声明页面

```bash
python <image2ppt-root>/cli/image2ppt/cli.py run next <run-dir> --json
python <image2ppt-root>/scripts/build_page_worker_prompt.py \
  <run-dir> --page <page-id> --out <absolute-page-dir>/worker-prompt.md
python <image2ppt-root>/cli/image2ppt/cli.py run dispatch \
  <run-dir> --page <page-id> --agent-id <id> --prompt-file <absolute-prompt>
```

对于恰好一个页面，使用 `--local` 声明它并在当前代理中重建它。对于多个页面，最多可派遣独立页面工作器，直到 `page_jobs.json` 中的容量。不要因为工作器速度慢而重置活动工作器。

### 4. 重建和通过每个页面

将结构化页面计划为 3-5 个语义区域，并独立路由每个区域。使用测量的复合图表：测量每个节点、关系和受保护的锚点。保持可测量的圆圈、卡片、直线/虚线关系和简单连接器原生。仅使用有界透明资源表示复杂的本地子部分。

将细箭头表示为一个连接器，其箭头在同一对象上。将填充箭头表示为一个 Arrow AutoShape，其中居中的标签文本在同一对象内。永远不要从线和三角形构建普通箭头，也永远不要将整个知识图谱扁平化为一个图像。

使用 `schema_version: 2` 写入新的页面清单。使用具有显式 `kind` 和 `representation` 值的结构化 `visual_inventory` 项，并为每个必需的质量检查写入具体的 `quality_evidence` 观察。公式渲染是一个硬门：缺少引擎、转换器或编译失败必须使页面失败，除非用户明确批准该确切公式例外，并且清单记录了 `user_approved_exception: true` 和具体的 `approval_note`。

工作器提示执行确定性序列。其最终门是：

```bash
python <image2ppt-root>/cli/image2ppt/cli.py page build <page-dir>
python <image2ppt-root>/scripts/run_image2ppt_qa.py <page-dir>
# 第一次运行会写入 visual-review-evidence.template.json 并保持挂起。
# 对照 source.png 和 render/rendered.png 检查源图像，复制并完成模板作为 visual-review-evidence.json，
# 如有必要进行修复，然后：
python <image2ppt-root>/scripts/run_image2ppt_qa.py <page-dir> \
  --visual-review-status reviewed \
  --visual-review-evidence <page-dir>/visual-review-evidence.json
python <image2ppt-root>/cli/image2ppt/cli.py page contact-sheet <page-dir>
```

证据文件必须涵盖当前源/渲染哈希值和每个必需检查的具体观察。`--visual-review-notes` 是可选的上下文，不能替代证据文件。

在标准验证和 Image2PPT 区域、箭头和渲染门通过后记录：

```bash
python <image2ppt-root>/cli/image2ppt/cli.py run record \
  <run-dir> --page <page-id> --agent-id <id>
```

使用相同的 `run reset` → 派遣 → 记录生命周期来修复拒绝的页面。

### 5. 最终化和重新验证重建的演示文稿

当 `run next` 报告 `finalize` 时运行：

```bash
python <image2ppt-root>/cli/image2ppt/cli.py run finalize <run-dir>
python <image2ppt-root>/scripts/run_final_image2ppt_qa.py <run-dir>
# 第一次运行会写入 final/visual-review-evidence.template.json 并保持挂起。
# 检查每个渲染幻灯片，完成 final/visual-review-evidence.json，然后：
python <image2ppt-root>/scripts/run_final_image2ppt_qa.py <run-dir> \
  --visual-review-status reviewed \
  --visual-review-evidence <run-dir>/final/visual-review-evidence.json
```

最终化会从页面清单重建，保留源演讲者笔记，验证包，并写入 `deck_manifest.json` 记录的输出。最终 QA 会重新应用清单箭头，验证箭头原子性和复合结构，渲染每个幻灯片，检查演讲者笔记完整性，并写入 `final/image2ppt_qa.json`。

## 交付

返回最终 PPTX 路径、标准最终验证和 `final/image2ppt_qa.json`。报告哪些复杂视觉仍然可替换为位图资源。在页面/最终门挂起或失败时不要调用演示文稿完成。
