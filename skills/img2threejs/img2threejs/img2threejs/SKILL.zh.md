---
name: img2threejs
description: 将一个对象或角色参考图像转换为代码构建的高质量门控、动画就绪的Three.js程序化模型。用于图像到3D重建、细节精确的对象重建、风格化/相似度最大化的人像角色、雕刻规格以及分阶段代码生成。
---

# img2threejs — 图像到程序化 Three.js

将参考图像中可见的对象重建为**纯代码**的程序化 Three.js 模型，通过分阶段的雕刻流程和 AI 视觉自我纠正循环进行控制。这是一种代码驱动的重建，**不是**摄影测量、网格提取或下载的艺术包。这一承诺规定了模型的*构建方式*——它对模型随后可以*导出*到哪些文件格式没有任何说明；明确选择的发射目标 (`--target <kind>`) 是对已构建模型的终端、整件艺术品转换，经过对其声明的限制进行验证，绝不可能是构建的一种替代方式。

跨代理：在 Claude Code、Codex 或 OpenCode 下工作。无论本文档中提到“代理视觉”或“代理浏览器工具”，都使用主机提供的任何工具——原生图像读取、浏览器 MCP（playwright/chrome-devtools）、项目预览或用户提供的屏幕截图。

此文件是始终加载的路由器：它包含操作顺序和每条硬性规则的顺序，每一条规则都作为一行。每条规则背后的完整合同存在于命名规则的 `grimoire/` 或 `docs/` 文件中——在您到达该阶段时阅读命名的文件，而不是之前。

## 标准共享检出

保留此存储库的一个检出，并让每个主机通过符号链接进入它，以便 Claude 和 Codex 执行相同的代码，而不是相互偏离：

```text
~/.claude/skills/img2threejs -> <your checkout>
~/.codex/skills/img2threejs  -> <your checkout>
```

## 何时使用

用户附加/指向一个对象图像，并希望获得程序化的 Three.js 模型、重建/动画/破坏计划、雕刻规范或代码。也适用于材质研究、可操作的道具、游戏对象、植物/机械部件和风格化重建。

## 核心承诺

从照片雕刻，按顺序——永远不要一次性生成网格：
1. **首先运行 `python3 forge/next.py --state .img2threejs/state.json [<spec>]`**，在每次启动、恢复和每次纠正迭代之前。它报告有序清单、确切的下一个命令、证据状态和有界纠正循环状态；它永远不会取代规范/通行证门禁。遵守硬性停止；不要从记忆中继续。
2. **验证**图像是否为合适的 3D 目标 (`grimoire/intake/validation_rubric.md`)。
3. **评估**对象类别+复杂性，然后在任何代码之前编写 `qualityContract`。
4. **规范**它：组件层次结构、材质、光照、枢轴、插座、动作锚点。
5. **按步骤构建**从块状模型→结构→形状→材质→光照→交互→优化。
6. **验证**每个步骤，通过将屏幕截图与参考进行比较；如果全局分数看起来很好，但定义身份的特征是错误的，则失败该步骤。

明确说明输出何时是近似/风格化/低多边形。单个图像无法揭示隐藏的侧面或保证精确的几何形状——与其假装自信，不如这样说。

## 强制本地状态门禁

对话上下文是易失的；`.img2threejs/state.json` 是本地清单权威。每次重建初始化一次，然后通过它门禁每个步骤：

```bash
python3 forge/state.py init --state .img2threejs/state.json --reference <img> --profile <generic|character|installed-domain> --spec object-sculpt-spec.json
python3 forge/next.py --state .img2threejs/state.json [object-sculpt-spec.json]
python3 forge/state.py mark <step-id> --state .img2threejs/state.json --evidence <path>
```

- `next.py` 打印当前步骤、步骤、不完整的强制步骤、确切的下一个命令和 `loop/max`。退出代码 3 或 `status=stopped` 是硬性停止：报告原因并请求输入。不要通过从聊天历史中重建进度来绕过它。
- 每个完成的步骤都需要证据；仅使用 `--reason` 将不适用步骤标记为 `skipped`——禁止沉默遗漏。循环计数来自 `reviewHistory` 操作 (`refine-spec`/`refine-code`)，而不是代理内存。默认值：每个步骤 3 次纠正，总共 6 次。
- 域配置文件的步骤、门禁和参考材料来自**注册中心**：存储库中的模块（`character`）和安装的插件（`cs2`、`animated-character` 来自 plugin-character）相同地注册，并且 `forge/state.py init` 指出可用内容。配置文件添加强制门禁而不改变核心顺序——域插件通常需要权威分类、摄入清单和机器可读的域审查，然后才是 AI 审查；`character` 需要角色合同和地标证据；`animated-character`（需要安装的 plugin-character）添加了 `character` 的所有内容加上九个 Stage R 步骤（`grimoire/readiness/animation_contract.md`）。每当 rig 必须移动时选择它——在 `character` 上 Stage R 门禁不存在，构建完成而从未运行它们，这就是动画以前以损坏状态发货的方式。其顺序是承重的：修复网格，冻结它，加性绑定，然后验证一致性。每个配置文件记录适用性、投影适用性和材料证据适用性。状态文件是可恢复索引，而不是视觉证据：渲染、规范、审查历史和确定性门禁仍然是权威工件。

## 必须的输入

- 一个图像路径 / 屏幕截图 / URL / 附加图像（如果缺失或不可读，请询问）
- 预期用途：道具、游戏对象、英雄渲染、可玩/可破坏对象、动画 rig
  （默认：实时浏览器道具具有交互式性能）
- 当域插件提供项目时，其摄入步骤要求的所有权威记录，或明确要求用户/视觉提供者提供一条记录；仅靠启发式检测不足以选择几何适配器

## 循环（脚本执行强制；代理视觉执行判断）

从技能根目录运行脚本 (`forge/...`)。纯 Python 3.10+ 标准库，无需 pip 安装。
完整标志：`grimoire/scripts.md`。永远不要让脚本*评分*视觉效果——那是代理的工作。

1. **先分析图像**（代理视觉，任何脚本之前）：在 `grimoire/intake/image_analysis.md` 中工作分层观察协议——识别/分类，宏观→中观→微观分解，映射部分关系，用PBR术语命名材料，列出定义身份的特征，并标记单视图隐藏的内容。观察先于推断；受控的3D词汇；3D对象空间而非2D图像空间。然后探测局部图像：
   `forge/stage1_intake/probe_image.py <image>`（仅元数据，非视觉检查）。
1a. **本地规范搜索**——图像分析后，在编写或完善规范之前，拉取本地域证据（解剖/PBR/磨损/几何/运行时/物理）而不是发明它：
   `python3 forge/stage2_spec/new_pre_spec_assessment.py "Name" --image <img> --out assessment.json`
   （自动在 `core_3d` 集合上运行BM25，或声明的域贡献的集合——集合永远不会从目标名称猜测；写入 `localSpecSearch` 套件，`new_sculpt_spec.py --assessment` 将其带入规范）。完整的查询扩展配方（双语术语，专注 `search_specs.py` 检索，缓存规则）：
   `grimoire/intake/local_spec_search.md`。在重试不完整或特定域的查询之前，必须阅读它。
1b. **域摄入**——当域插件提供项目时，在预规范创作之前完成其摄入步骤（接纳、启发式信号、分类、家族/路线解析）。必须在其步骤名称完全阅读合同之前创建清单或运行预规范评估。
1c. **可选保真度证据适配器**——仅当它们改进观察到的弱点时；stdlib核心仍然是权威的。薄/复杂掩码→本地SAM2；角色面部/姿态→MediaPipe；弱前后线索→Depth Anything V2
   (`forge/stage1_intake/run_vision_adapter.py <segment|landmarks|depth> ...`; 每个适配器都发出来源；单目深度仅相对）。**MCP仅场景突变永远不会被视为实现**——将已更改的来源写回规范或TypeScript，重新构建，重新捕获。
   完全适配器+MCP路由和权威边界：
   `docs/integrations/reference_fidelity_tooling.md`。
2. **预规范评估门**——分类+评分复杂性+编写质量合同：
   `forge/stage2_spec/new_pre_spec_assessment.py "Name" --image <img> --complexity <简单|中等|复杂|超复杂> --out assessment.json`。规则：`grimoire/intake/quality_contract.md`。
   设置 `objectClass.primaryDomain` (`对象` | `角色` | `混合`) 并填充种子 `detailInventory`（其 `targetMinDetails` 随复杂性缩放）。域插件可以通过其增强**提高**这些底线——合并夹紧，所以插件永远不会降低一个（皮肤的完成/磨损/硬件是项目，所以这样的域被保持在最高的保真度标准。制作过程几何，但将完成路由到步骤2c中的投影路径——对于图案化皮肤的程序化完成（多普勒/伽马/大理石/褪色）在参考面前看起来明显错误。域插件提供自己的完成规则簿和纹理获取指南；阅读其清单步骤名称。
2b. **细节清单**（不要为详细主题跳过）——扫描区域并枚举每个定义身份的小细节（光泽、倒角、紧固件、线画、轮廓、污渍）：
   `forge/stage1_intake/build_detail_inventory.py <image> --mode grid-3x3 --out-dir <dir> --out di.json`。
   每个细节必须映射到 `component.localFeatures` 或 `material.localOverrides` 条目——绝不只有散文。分类+3D术语配方：
   `grimoire/intake/detail_inventory.md`。
2c. **投影优先保真度**（角色和参考匹配的表面——绘制的皮肤、贴花、绘制的图案）——当目标是匹配特定参考的表面时，将照片自己的像素放在网格上，而不是用程序化方法近似它们。这是最大的保真度杠杆；对于图案化表面的程序化材料是 #1 重建失败。配方（`grimoire/character/likeness_maximization.md`——其两个杠杆概括了过去的角色）：解决相机（`stage1_intake/solve_camera_pose.py` → `referenceCamera`），**去光**参考（`stage1_intake/delight_albedo.py`，硬性要求——去光化是使投影安全的东西），然后投影去光裁剪并将其烘焙到UV中
   (`stage3_build/bake_projected_texture.py --mesh-id <id>`）。对于绘制的皮肤，投影去光裁剪就是完成——没有程序化多普勒材料。对于角色，首先捕获关键点（`stage1_intake/extract_landmarks.py --out anatomy.json`），填充 `preSpecAssessment.anatomy`，路由 `grimoire/character/reconstruction.md`。单视图不能显示隐藏的侧面——当它重要时报告每个区域的置信度并请求更多视图。
   角色子路线，按顺序——决定存在哪些部分之前塑造任何东西，并在头发之前塑造头部：
   - **部分** — `grimoire/character/structure_decomposition.md`
   - **头部** — `grimoire/character/head_construction.md`（像似性门读取的内容）
   - **头发** — `grimoire/character/stylized_hair_threejs.md` + 参数合同在
     `grimoire/character/threejs_hair_parameter_contract.json`。只有轮廓审查通过后锁定拓扑：材料调整无法修复错误的锁定拓扑。
2d. **无参考的人形**——一个没有参考图像的通用人物没有任何可衡量的东西，所以从公共规范填充解剖：
   `forge/stage2_spec/humanoid_proportions.py <spec> --style-heads 8 --in-place`。它写入 `anatomy.source: "canon-table"` 所以规范永远不会被误认为是测量，当规范命名参考图像时拒绝运行，并命名任何语料库没有提供的东西而不是插值它。
3. 从评估中编写规范：
   `forge/stage2_spec/new_sculpt_spec.py "Name" --image <img> --assessment assessment.json --augmentation spec-augmentation.json --domain <profile> --out object-sculpt-spec.json`（清单步骤携带解析的标志）。
   替换通用的起始 `featureReviewTargets` 为对象的真正定义身份的系统（≤5关键，≤3每个通过）；对于角色添加 `anatomy-proportion`，`face-landmark-placement`，`pose-silhouette`，`outfit-and-palette`。仅使用3D图形术语（`grimoire/glossary/3d_vocabulary.md`），绝不使用“漂亮/光滑/闪亮”。根据 `grimoire/intake/surface_topology.md` 对每个组件的 `topologyClass`/`topologyRationale` 分类之前选择 `primitive`——这是防止连续有机形式被选为盒子的原因。
4. 当材料保真度重要且存在源图像时，分析每个材料的**完成**，然后提取参考PBR证据，两者都按裁剪（验证裁剪是否在您认为的部分上）：
   - `forge/stage1_intake/analyze_texture.py <crop> --spec spec.json --material-id <id> --in-place`
     分类完成，提取梯度调色板，并将基于文档的 MeshPhysicalMaterial 标量写入材料。配方+Three.js纹理/PBR规则：
     `grimoire/build/threejs_texture_reference.md`。经验法则：**平面涂料的纯反照率，图案化完成的真实参考裁剪**。
   - `forge/stage1_intake/extract_pbr_evidence.py <crop> --out-dir <dir> --material-id <id> --target-threshold 0.7`。
     置信度 < 0.7 是停止/完善输入信号，不是通过。它是推理，不是逆渲染。
   - 对于多个命名区域：`forge/stage1_intake/material_region_analysis.py --manifest regions.json --out-dir material-evidence --out material-analysis.json`，
     从 `docs/materials/material-reference.json` 解决每个分配，用 `forge/stage2_spec/apply_material_analysis.py` 线路它。
   - 发出受控的材料相机/裁剪合同 (`forge/stage4_review/material_views.py`)，
     比较可见足迹裁剪 (`material_comparator.py`)，仅应用受限于材料范围的更正 (`material_feedback.py`)，并记录阻塞结果 (`material_gate.py`)。
5. 验证，然后在生成代码之前严格验证：
   `forge/stage2_spec/validate_sculpt_spec.py object-sculpt-spec.json` 然后 `--strict-quality`。
   严格阻止浅层规范（一个复杂对象有一个根，没有重复系统，没有局部覆盖，没有微组不是实现就绪的，即使JSON验证）。
6. **锁定构建通过**——仅触摸当前未锁定的通过：
   `forge/stage3_build/orchestrate_passes.py status object-sculpt-spec.json`
   `forge/stage3_build/generate_threejs_factory.py object-sculpt-spec.json --out src/createObjectModel.ts`
   生成器是失败关闭的：`strict-quality` 必须通过才能写入任何工厂，并且未来的 `--pass-id` 在先前的通过被审查 `continue` 之前失败。如果受阻，保留 `BLOCKED` 资产并完善特定主题的规范；不要用通用模板替换。
   本地状态仅在新通过或 `refine-spec` 时添加 `--force`；`refine-code` 编辑当前资产而不重新生成它。在覆盖之前，将有效的手动完善带回到规范中；生成的代码不能是重建决策的唯一副本。
6a. **达到三角形预算**。`performanceBudget.targetTriangles` 为每个具有段计数的 `primitive` 选择细分级别（低 ≤6k，标准 ≤60k，否则英雄）并限制隐式表面采样网格。当一个级别不够精确时，向该组件添加
   `geometryDescriptor.decimate: {"targetRatio": 0.4}`——在生成的工厂中执行二次折叠，在皮肤绑定之前运行，以便在保留的顶点上计算权重。它只保留 `position`（法线重新计算），所以它被拒绝在编写的/展开的 `uvStrategy` 上。离线LOD级别：
   `forge/stage3_build/decimate.py <mesh.json> --ratio <r> --json`。
7. 在浏览器/预览中渲染当前通过，在审查视点捕获屏幕截图。
7a. **偏轴和放置门——单个审查视点不是模型证据。**
   捕获一个转盘，而不是一帧，并运行所有三个；每个都捕获构造上老门遗漏的缺陷类别（一个穿过头骨的洞，一顶在臀部高度的头饰和一个漂浮的护身符都通过了八个仅前视图的审查轮）：
   `forge/stage4_review/turntable_gate.py --capture 0=front.png --capture 90=right.png --capture 180=rear.png --capture 270=left.png --json`
   `node runtime/scripts/export_mesh_geometry.mjs --url <preview> --out meshes.json` 然后
   `forge/stage4_review/self_intersection.py meshes.json --json`
   `forge/stage4_review/attachment_anchor.py object-sculpt-spec.json --measured measured.json --json`
   三个都退出 `0` 清洁 / `1` 门失败 / `2` 错误。失败会阻止 `continue` 即使全局保真度分数通过。在相信清洁裁决之前阅读 `sampledVertexCount` / `unmeasuredAttachments` /
   `missingAzimuths`：每个都命名门没有查看的内容。
8. **在AI视觉之前运行确定性门**。必须完全阅读
   `grimoire/review/gates_reference.md` 和 `grimoire/review/self_correction.md`。运行
   `forge/stage4_review/diagnose_render.py` 并记录通过 Tier 1 的结果与
   `--spec object-sculpt-spec.json --pass-id <pass> --in-place`；对于非平面形式也运行
   `forge/stage4_review/diagnose_render_multi_angle.py` 使用固定视图并在至少两个有意义的轨道视图中。然后运行
   `forge/stage3_build/orchestrate_passes.py check object-sculpt-spec.json --pass-id <pass>`。
9. 打包一个并排表，然后用代理视觉检查它：
   `forge/stage4_review/make_comparison_sheet.py --reference <img> --render <shot> --out cmp.png --json`。
10. 记录审查（整体+每层+每特征分数+决定）：
    `forge/stage4_review/append_review.py object-sculpt-spec.json --pass-id <pass> --fidelity <0-1> --action <继续|完善规范|完善代码|请求输入|停止> --summary "..." --render-screenshot <shot> --comparison-image cmp.png --ai-vision-score <0-1> --layer-scores-json '{...}' --feature-reviews-json <f.json> --in-place`。
    当域插件贡献一个审查门时，首先用该插件的审查步骤名称的命令生成其版本报告，然后附加它
    `--domain-review-json <report>.json --review-scene-json <the plugin's scene fixture>`。清单步骤携带解析的路径。
    失败的家庭、绘制区域、投影覆盖、关键细节或轨道门会阻塞 `continue` 即使全局分数通过。查看插件的自己的审查门文档。
11. 在手动审查编辑后同步管道状态，记录清单证据，然后在另一个更正或通过之前重新运行本地状态门：
    `forge/stage3_build/orchestrate_passes.py sync object-sculpt-spec.json --in-place`
    `python3 forge/next.py --state .img2threejs/state.json object-sculpt-spec.json`。
12. 在声明完成之前运行
    `forge/stage4_review/check_part_coverage.py --spec object-sculpt-spec.json --manifest parts.json`
    并验证行动就绪的层次结构。仅在有证据的情况下标记 `part-coverage` 和 `action-ready`。

## GLB介导的v2渲染保真度轨道（1.5 alpha）

当用户提供一个GLB作为中间参考时，浏览器渲染的GLB是独立编写的程序化工厂的结构和视觉基线。原始GLB永远不会是像素证据，其拓扑/材料永远不会被复制到工厂中。在任何工厂编辑之前——完整的合同在 `grimoire/build/python_threejs_render_bridge.md`，机器可读模式在 `docs/specs/render-profile.v2.schema.json` (+示例；失败关闭验证）：

1. `forge/stage1_intake/probe_glb.py` 首先执行。一个合并的单节点/单网格资产对于语义标签来说是 `insufficient`；在声称精确区域之前请求一个多部分GLB或浏览器语义-ID通过。
2. 作者一个共享的 `render-profile.v2` (`forge/stage4_review/validate_render_profile.py`) 由GLB和程序化路线使用。区域ID是主题特定的，永远不会从示例配置继承；在 `extensions.requiredSemanticRegions` 中声明所需集，遗漏是一个硬验证错误。
3. 捕获每个承认视图的六个通过（`beauty`，`alpha-silhouette`，`semantic-id`，`depth`，`normal`，`roughness-material-id`）；用 `forge/stage4_review/compare_region_passes.py` 评分。缺少语义-ID数据会阻塞每个区域的置信度，而不是回落到整图分数。
4. 使用区域特定的连续几何——当区域的轮廓需要连续表面时，永远不要用浮动的基元替换面部/头部体积、布料外壳或尾巴。
5. 运行每个循环的**一个**更正组，按顺序：`相机 → 轮廓 → 面部 → 衣服 → 配件
   → 材料 → 照明`；捕获完整的通过集后记录更改的组、散列和分数。在诊断改进时永不组合组。
## 门（不要跳过）

在任何视觉审查或 `continue` 决策之前，必须阅读 `grimoire/review/gates_reference.md` 中的完整门到门合同（神圣之眼，VLM救援，多角度，室内差异，左右，头发，域审查，有界更正，神圣之眼适配，屏幕截图反馈，组装，
   附件，材料，细节清单，rig负载，角色跟踪）。简而言之：

- 首先验证引用（`grimoire/intake/validation_rubric.md`，`check_reference_admission.py`）。
- `divine_eye.py` 是以确定性优先的；VLM（`vlm_gate.py`）是一个门控最后一层，在硬门控失败时从不被咨询。
- 非平面形状必须从 ≥2 个角度保持（`diagnose_render_multi_angle.py`）。
- 每次视觉遍历都在轮廓内部进行测量（`interior_difference.py`）。轮廓 IoU 读取约等于图形单元的 11%：一个删除了面部的模型得分与完成的面部相同，都是 0.8803。
- 每个 `-l`/`-r` 对都是镜像，不是旋转——在规范时间很难（`validate_chirality`）。在两侧都以相同方式错误的配对仍然可以通过，并且需要 `medial_lateral_bias` 与参考进行比较。
- 发丝主题：`scalp_exposure.py` 是硬性的，在渲染之前的几何体上运行；`hair_gate.py` 是软性的，从属于它。覆盖率不足永远不会授权扩大体积。
- 具有硬边界平坦色区域（火焰/布料/袜子，制服条纹，绘画标记）是身份特征，因此它们的边界在几何体上被门控：`vertex_region_gate.py`。永远不会是纹理——这个管道发出代码；形状谓词存在于 `_shared/vertex_paint.py` 中。
- 曲线声明（“卷成钩形，而不是直圆锥”）需要 `swept_arc_gate.py`：轮廓 IoU 通过一个占据大致正确单元的直圆锥。
- 角色构建在绑定 `THREE.Skeleton` 之前验证 rig 负载（`stage5_rig/validate_rig_payload.py`）；它只证明负载完整性，从不证明姿势压力或相似性。
- 必须移动的 rig 运行动画门控（`grimoire/readiness/animation_contract.md`；检查表步骤和门控来自已安装的插件-角色——`stage5_rig/` 仍然在这个存储库中作为发射器的库，而不是检查表的权威）。存在的剪辑不是播放的剪辑：只有 G1（`maxSampledBindingDelta <= 2^-23`）区分两者，输入缺失的门控报告 `unevaluated`，永远不会通过。在附加模式下在 IDENTITY 绑定，并仅从网格边界获取显示偏移；循环由 `poseReturn` 决定，而不是由行程决定。
- 域插件的审查门控也针对其版本化的场景固定件运行。
- 本地状态强制执行每次遍历 3 次修正，默认总共 6 次；达到任一限制都是硬停止。`correction_loop.py` 可能因重复缺陷、振荡或平台而提前停止。
- `continue` 需要渲染 + 比较表 + AI 视觉分数 ≥ 阈值，每个关键特征 ≥ 自身的阈值（`grimoire/feedback/render_capture.md`）。
- 每个模型都应可爆炸并且可点击——这是一个结构门控，而不是像素（`check_part_coverage.py`，`grimoire/build/geometry_patterns.md`）。
- 动作就绪、附件、材质/灯光、细节清单和角色跟踪要求：`grimoire/readiness/action_rigging.md`，`grimoire/readiness/joint_attachment.md`，`grimoire/feedback/shading_realism.md`，`grimoire/intake/quality_contract.md`，`grimoire/intake/validation_rubric.md`。

## 自我纠正

每次遍历后，精确决定一个：`continue | refine-spec | refine-code | request-input | stop`。
`refine-spec` 修复错误/缺失/浅层的规范（重新验证，不要围绕它修补代码）；`refine-code` 修复与良好规范不匹配的几何体/材质/灯光。在做出决定之前，必须阅读根原因指南 + 保真度量表在 `grimoire/review/self_correction.md` 中，记录决定，并重新运行本地状态门控。

**小特征需要不同的工具。** Divine Eye 的 SSIM/色调/边缘信号在 64×64 亮度网格上运行，所以在任何比较发生之前，几像素宽的细节是缺失的。当保真度取决于单个撕裂、稀疏、fangs 或眼睛时，使用四级显微镜：
`grimoire/review/divine_eye_microscope.md`。它从其中建立的两个经验规则：在组件的**可见足迹**（全帧减去组件隐藏帧）上测量保真度，永远不会在隔离渲染上测量；永远不会对**凹形**特征进行颜色门控，其中暗度比例捕获凹槽阴影而不是材质。

## 透明度和过程调试

报告每次遍历的变化并提供证据（精确值/坐标），命名仍然不匹配的内容，并且在只有“改进”时永远不会声称“完成”。通过的门控不是 3D 真实性的证明。完整规则 + 示例：`grimoire/review/self_correction.md`。

## 左和右

一个左/右对是**反射**，不是旋转：取横向轴的负值，其他不变，`(x, y, z) → (-x, y, z)`。使用 `forward: +Z`，Y 向上，并使用右手框架，角色的左是 **+X**。该约定作为代码存在于 `forge/_shared/chirality.py`
(`CHARACTER_LEFT_SIGN`)，有两个不同的门控用于从错误中获取的两个缺陷：`validate_chirality` 在规范时间捕获错误地认为旋转为反射，而 `medial_lateral_bias` 与参考比较捕获在两侧都以相同方式错误的配对。
反射也会反转三角形绕行——在镜像的侧面翻转它，或者 `flatShading` 使肢体像从后面照亮一样。完整说明与测量的缺陷：
`grimoire/scripts.md`（“左和右”）。

## 发丝

发丝有自己的子系统，因为它有其他门控看不到的失败模式。完整合同、测量和非目标：`docs/HAIR_PIPELINE.md`。硬规则：

- 根绑定到头皮为 `(u, v)`，永远不会是绝对位置（硬验证错误）。
- `standProud` 由生成器强制执行，不是建议性的。
- `scalp_exposure.py` 是几何体在任何渲染之前的硬门控；覆盖率不足永远不会单独授权扩大体积。
- 默认表示层是 `shell`，不是锁；发丝印象来自分面和材质（`hair.human.code-only`），因为这项技能不发出纹理。
- `plane-card` 被拒绝用于发丝（需要这项技能无法发出的 alpha 纹理）。
- 发丝是严格父级的，永远不会平滑着色（地测场穿过头骨）。

## 域插件

域插件使运行精确，否则这个管道会推断。它贡献自己的检查表步骤和门控，并发布一个 `spec-augmentation.json`，这个管道在 `spec-authoring` 时拉取。如果没有插件为项目服务，这里不会发生任何变化：编写骨架并从参考中推断形状，就像任何其他对象一样。

- 插件贡献的步骤出现在检查表中，有自己的 ids 和解析路径。阅读每个步骤的名称——插件发出自己的合同，并管理自己的域。
- 插件可以**提高**这个管道的质量底线，并且永远不会降低一个；合并夹紧。
- 不为项目服务的插件不发布增强。这不是错误，也不是阻塞运行：它是通用路径，重建通过推断进行。
- 这个管道不命名域。如果规则是域特定的，它存在于该域的插件中。

### The img2 harness

插件由 `img2` harness
([img2threejs/img2](https://github.com/img2threejs/img2)) 安装和管理，这是一个独立的依赖无关的 CLI（Node 启动器，Python 核心）。这项技能本身不安装任何东西：当 `state.py init` 命名一个配置不可用时，命名 `img2 add` 命令来安装它并停止——永远不要用域逻辑来供应商化。

```bash
img2 add img2threejs/plugin-<id> --ref <tag>      # 在一个标签（例如 plugin-cs2）安装插件
img2 doctor                                       # 每个主机解析了什么：基础技能路径 + 版本，插件门控
img2 capabilities --from-kind image --to-kind glb # 哪个已安装的插件服务于边缘
```

设置和完整 CLI 参考存在于 README 快速启动和 harness 存储库的文档中。

## Forge 运行时合同

细分运行时测试将生成的 TypeScript 与展示检查出。设置
`IMG2THREEJS_SHOWCASE_ROOT` 为该检查出；没有它，本地运行时测试会跳过带有可操作消息，而静态合同仍然运行。CI 应该设置 `IMG2THREEJS_REQUIRE_SHOWCASE=1`
将缺失的展示检查出转换为测试失败。

```bash
IMG2THREEJS_SHOWCASE_ROOT=/path/to/img2threejs-showcase python3 forge/tests/test_subdivision.py
IMG2THREEJS_SHOWCASE_ROOT=/path/to/img2threejs-showcase python3 -m unittest discover -s forge/tests
IMG2THREEJS_SHOWCASE_ROOT=/path/to/img2threejs-showcase python3 forge/tests/test_showcase_tsc_smoke.py
```

## 实现规则（简述）

TypeScript + 纯 Three.js，除非项目使用包装器。`Group` 工厂
`createObjectNameModel(spec, options)`，重建数据与渲染器对象分开，所有程序性噪声使用确定性种子。优先使用基本类型 / `Shape` 挤出 / 曲线+管 / 实例化 / 位移 / 生成的画布纹理，而不是任何外部艺术。完整几何体 & 材质配方 + 艰难获得的失败模式：`grimoire/build/geometry_patterns.md`。

### 可选 Python ↔ Three.js 渲染桥接

当请求 Python 进行角色渲染时，将其用作围绕浏览器 Three.js 运行的确定性工作/证据层：相机批处理清单，源/输出哈希，就绪和解决检查，屏幕截图持久性，掩码，诊断，和比较包装。目标 Three.js 浏览器路由仍然是渲染权威。不要无声地用 Blender/VRM/GLB 输出替换程序性 TypeScript 工厂。完整路由，清单字段，和失败规则：
`grimoire/build/python_threejs_render_bridge.md`。

### 标准角色管道（合并 1.5 beta + alpha）

使用 `grimoire/readiness/standard_character_pipeline.md` 进行角色工作。Beta 拥有严格的雕塑/构建/审查门控；alpha 拥有确定性相机清单，浏览器屏幕截图证据和 UniRig 形状的 rig 验证。CharacterGen，Tripo，VRM 和其他神经/资产系统是可选的适配器，具有源，检查点，许可证，坐标转换和输出哈希。它们永远不会无声地替换程序性 TypeScript 工厂。图像到网格系统发出一个没有骨架的静态网格，所以它们的输出永远不会是动画就绪的，无论它看起来多么好。
可执行入口点：`forge/stage4_review/render_bridge.py` 和
`scripts/capture_threejs_playwright.py` (`init → 浏览器捕获 → 验证 → 诊断`；捕获必须在真实的展示/浏览器路由上操作，并在工作区留下可读的 PNG）。

## 输出

- **仅分析**：适用性裁决 + 分数，对象提取，宏观→微观层次，几何策略，材质/灯光配方，动画/破坏可行性，计划 + 风险。
- **实现**：上述简要，然后编辑代码；使用类型检查/构建 + 屏幕截图进行验证。
- **不可行**：命名障碍，请求更多视图 / 更干净的图像 / 接受的风格化 / 更窄的目标。“这个图像无法达到请求的保真度”是一个有效结果。
