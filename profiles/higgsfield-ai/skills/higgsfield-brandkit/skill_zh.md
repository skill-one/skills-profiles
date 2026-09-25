# Higgsfield 品牌工具包

构建一致的身份及其所需的应用。将提供的品牌事实和官方资产视为固定的约束条件。

## 初始化

1. 解析 `SKILL_ROOT` 为此技能的安装目录，并创建一个持久的项目目录：

   ```bash
   BRANDKIT_WORKDIR="${PWD}/brandkit"
   BRANDKIT_STATE="${BRANDKIT_WORKDIR}/state.json"
   mkdir -p "${BRANDKIT_WORKDIR}"
   ```

2. 阅读 [先决条件](references/prerequisites.md)。在使用相关工具之前检查工具。未经用户许可，切勿安装系统包。
3. 如果 `higgsfield` 缺失，仅在获得许可后安装：

   ```bash
   curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
   ```

4. 如果 `higgsfield account status` 因身份验证或工作区错误而失败，请要求用户运行 `higgsfield auth login` 或选择一个工作区，然后等待。
5. 在付费生成之前检查实时模型合约：

   ```bash
   higgsfield model get recraft_v4_1 --json
   higgsfield model get seedream_v5_pro --json
   higgsfield model get gpt_image_2 --json
   ```

## CLI 映射

| 操作 | 命令 |
|---|---|
| 发现模型 | `higgsfield model get <model> --json` |
| 生成并轮询 | `higgsfield generate create <model> ... --wait --json` |
| 恢复任务 | `higgsfield generate wait <job_id> --json` |
| 上传本地资产 | `higgsfield upload create <path> --json` |
| 导入网站元数据 | `higgsfield marketing-studio brand-kits fetch --url <url> --wait --json` |
| 读取/写入审批状态 | `python3 "$SKILL_ROOT/scripts/brandkit.py" state ...` |
| 渲染评审板 | `python3 "$SKILL_ROOT/scripts/brandkit.py" preview ...` |
| 检查选定的标志 | `python3 "$SKILL_ROOT/scripts/brandkit.py" logo-inspect ...` |
| 导出标志文件 | `python3 "$SKILL_ROOT/scripts/brandkit.py" logo-export ...` |
| 构建品牌手册 | `python3 "$SKILL_ROOT/scripts/brandkit.py" brandbook-build ...` |

使用 `--image` 传递的本地图像路径将自动上传。除非用户明确需要托管副本，否则将 HTML、SVG、PPTX 和 PDF 交付品保留为本地项目文件。

## 用户界面行为

- 匹配用户的语言。保留设计大脑推理、提示、状态机制、脚本、模型查找和 QA 内部机制为私密。
- 每个可见生成批次最多发送一句简短的状态句子，然后在结果准备好之前保持安静。
- 提问一组紧凑的仅未解决的阻塞问题。切勿重复事实或强制为部分任务进行完整的身份问卷。
- 在每个调色板、标志、排版或下游评审之后，停止并等待普通用户反馈。
- 从沉默、成功生成或自己的偏好中切勿推断批准。
- 保留精确的用户文本。切勿编造定位、价值观、声明、成分、价格、认证、统计数据或监管内容。

## 核心工作流程

1. **分类请求。**
   - `apply-existing`：使用提供的官方资产，无需重新设计它们。
   - `extend-partial`：仅创建请求输出所需的缺失插槽。
   - `create-identity`：仅在明确请求时创建新标志或身份。
2. **读取状态。** 运行：

   ```bash
   python3 "$SKILL_ROOT/scripts/brandkit.py" state \
     --state-file "$BRANDKIT_STATE" --action get_status
   ```

   本地状态是持久的。当状态文件存在时，切勿粘贴、手动编辑或重新创建批准。
3. **运行摄入和资产分析。** 阅读 [摄入](references/intake.md)、[资产分析](references/asset-analysis.md)、[状态路由](references/handoff.md) 和 [精确状态有效负载](references/state-payloads.md)。立即锁定每个用户声明的官方标志、调色板和排版插槽。
4. **创建品牌锁定。** 阅读 [品牌锁定](references/brand-lock.md)。记录精确的拼写、官方资产、颜色、字体、布局/形状规则、请求输出和禁止的处理方式。
5. **仅要求输出使用的插槽。**
   - 仅标志 → 调色板 + 标志用于新标记；现有标记的官方标志
   - 仅调色板 → 调色板
   - 仅排版 → 排版
   - 无文本的模拟/商品 → 标志；仅在颜色/应用需要时添加调色板
   - 带文本的社交/包装/海报/标志 → 标志 + 调色板 + 排版
   - 品牌手册/套件 → 标志 + 调色板 + 排版
6. **构建缺失的基础插槽。** 阅读 [设计大脑](references/brandkit-design-brain.md)、[概念板](references/concept-boards.md)、[内联评审](references/inline-widgets.md)，以及仅需要的 [调色板](references/palette.md)、[标志](references/logo.md) 或 [排版](references/typography.md) 模块。
7. **尽快继续原始请求**，一旦其所需插槽被批准。切勿再次要求用户选择范围。
8. **仅加载请求的生产模块：**
   - [模拟](references/mockups.md)
   - [社交图形](references/social-templates.md)
   - [海报/横幅](references/posters-banners.md)
   - [包装](references/packaging.md)
   - [标志](references/signage.md)
   - [商品](references/merchandise.md)
   - [演示套件](references/presentation-deck.md)
   - [品牌手册](references/brandbook.md)
9. **QA 和批准。** 阅读 [QA 和迭代](references/qa-and-iteration.md)。仅修复失败的输出。仅在明确批准其精确的基础依赖项后，才保存下游元素。

## 新身份序列

### 1. 调色板

使用 [预览有效负载](references/preview-payloads.md) 渲染 2–3 个精确的调色板选项作为确定性 HTML。显示 PNG 截图，以及可编辑的 HTML 文件并等待。在生成标志之前，使用 `approve_palette` 保留选定的调色板。

### 2. SVG 标志

阅读 [标志提示增强器](references/logo-prompt-enhancer.md)。为每个生成三个不同的仅符号机制和一个 Recraft 提示。将每个长提示写入文件并单独提交：

```bash
higgsfield generate create recraft_v4_1 \
  --model_type vector \
  --colors @"${BRANDKIT_WORKDIR}/logo-colors.json" \
  --background_color '#F7F7F5' \
  --aspect_ratio 1:1 \
  --resolution 2k \
  --wait --json < "${BRANDKIT_WORKDIR}/logo-candidate-1.txt"
```

直接使用返回的 SVG URL 进行评审。选择后，检查精确的 SVG 而不更改它：

```bash
python3 "$SKILL_ROOT/scripts/brandkit.py" logo-inspect \
  --source "<选定的 Recraft SVG URL 或绝对本地路径>"
```

使用 `approve_logo` 保留精确的任务 ID、SVG URL、名称、调色板修订版和返回的规范几何指纹。

### 3. 排版

使用提供的字体或经过验证的 Google Fonts 提出两到三个独特的显示/正文对。通过预览脚本渲染实际品牌名称和样本文本。仅保留选定的对使用 `approve_typography`。

交互流程始终在调色板、标志和排版选择时停止。显式无问题模式可以选择并保留调色板，但它仍然显示所有三个 SVG 标志候选者，并在用户选择标志时停止；精确的品牌标记永远不会自我批准。

## 一致性不变量

- 在所有地方重用相同的已批准标志源。当确定性放置/导出可能时，切勿重新绘制官方或选定的 SVG。
- 生成的标志依赖于创建它时使用的调色板修订版。更改该调色板会使生成的标志及其依赖项失效；更改排版不会使符号标记失效。
- 更改基础插槽仅使列出该插槽的下游元素失效。
- 将相同的品牌锁定值复制到每个相关生成提示：精确的十六进制、字体角色、形状语言、定位、清晰空间、构图和禁止的处理方式。
- 仅使用 Recraft V4.1 向量模式生成新标志标记。
- 使用 Seedream 作为主要照片真实模拟生成器。仅使用 GPT Image 2 进行添加可读文本或精确图形细节的控制阶段。
- 使用本地确定性 SVG/PPTX/HTML 构建进行精确复制和可编辑布局。不要要求图像模型伪造可编辑文件。
- 不要承诺原生 Figma、Canva、PSD、AI 或 EPS 文件。

## 确定性脚本

在 `"$BRANDKIT_WORKDIR"` 下创建 JSON 输入文件；切勿将用户文本直接插入 shell 参数。

```bash
python3 "$SKILL_ROOT/scripts/brandkit.py" preview \
  --input "$BRANDKIT_WORKDIR/reviews.json" \
  --output-dir "$BRANDKIT_WORKDIR/reviews"

python3 "$SKILL_ROOT/scripts/brandkit.py" logo-export \
  --input "$BRANDKIT_WORKDIR/logo-export.json" \
  --output-dir "$BRANDKIT_WORKDIR/logo"

python3 "$SKILL_ROOT/scripts/brandkit.py" brandbook-build \
  --state-file "$BRANDKIT_STATE" \
  --input "$BRANDKIT_WORKDIR/brandbook.json" \
  --output-dir "$BRANDKIT_WORKDIR/brandbook"
```

对于标志导出，加载 [标志导出有效负载](references/logo-export-payloads.md)。对于品牌手册，仅使用捆绑的构建器；在确定性合同失败后，切勿替换临时的 PowerPoint 或 PDF 生成器。

## 失败策略

- 重新尝试一次失败的 Recraft 或图像生成请求，使用相同的锁定概念和修正的合同。在第二次等效失败后停止。
- 如果预览或标志导出失败两次，报告具体错误；切勿用临时的 SVG 重写替换它。
- 如果品牌手册模板、字体或转换合同失败，立即停止。不要生成视觉上不同的备用方案并称其为规范。
- 如果无法保留精确的排版或官方标志保真度，则披露限制，而不是声称完成。
- 从未在文件、日志或聊天中暴露原始身份验证令牌或凭证。

## 交付

对于品牌手册，遵循 [品牌手册](references/brandbook.md) 中的严格响应合同：PPTX 链接/路径、PDF 链接/路径和字体安装警告。

对于其他输出返回：

1. 请求的视觉文件和预览。
2. 紧凑的品牌锁定摘要。
3. 可编辑与扁平化格式标签。
4. 所需字体/导入限制。
5. 针对性修订的稳定变体名称。

## 参考索引

- [先决条件](references/prerequisites.md) — 阶段特定的本地依赖项和安装命令。
- [摄入](references/intake.md) — 最小问题和输入路由。
- [资产分析](references/asset-analysis.md) — 官方/参考分类和测量。
- [状态路由](references/handoff.md) 和 [状态有效负载](references/state-payloads.md) — 持久批准。
- [品牌锁定](references/brand-lock.md) — 规范视觉约束。
- [设计大脑](references/brandkit-design-brain.md) — 私密的艺术指导。
- [概念板](references/concept-boards.md)、[预览有效负载](references/preview-payloads.md) 和 [内联评审](references/inline-widgets.md) — 选择阶段。
- [标志](references/logo.md)、[标志提示增强器](references/logo-prompt-enhancer.md) 和 [标志导出有效负载](references/logo-export-payloads.md) — SVG 生成和确定性变体。
- [调色板](references/palette.md) 和 [排版](references/typography.md) — 基础插槽。
- [模拟](references/mockups.md)、[社交图形](references/social-templates.md)、[海报/横幅](references/posters-banners.md)、[包装](references/packaging.md)、[标志](references/signage.md) 和 [商品](references/merchandise.md) — 应用。
- [演示套件](references/presentation-deck.md) 和 [品牌手册](references/brandbook.md) — 可编辑文档。
- [QA 和迭代](references/qa-and-iteration.md) — 预飞行、修复、批准和交付清单。
