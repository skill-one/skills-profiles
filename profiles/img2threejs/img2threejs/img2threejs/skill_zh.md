# img2threejs — 图像到程序化 Three.js

将参考图像中可见的对象重建为**纯代码**的程序化 Three.js 模型，通过分阶段的雕塑流程和 AI 视觉自我纠正循环进行控制。这是一种代码重建，**不是**摄影测量、网格提取或下载的艺术包。这一承诺规定了模型的构建方式——它对模型随后可以导出的文件格式**没有任何**说明；明确选择的发射目标 (`--target <kind>`) 是对已构建模型的终端、整件艺术品转换，经过对其自身声明的限制进行验证，**永远不是**构建的一种替代方式。

无代理：在 Claude Code、Codex 或 OpenCode 下工作。无论此文档中提到“代理视觉”或“代理浏览器工具”，都使用主机提供的任何内容——原生图像读取、浏览器 MCP（playwright/chrome-devtools）、项目预览或用户提供的屏幕截图。

此文件是始终加载的路由器：它包含操作顺序和每条硬性规则的顺序，作为一行。每个规则背后的完整合同存在于规则名称的 `grimoire/` 或 `docs/` 文件中——在您到达该阶段时阅读命名的文件，而不是之前。

## 标准共享检出

保留此存储库的一个检出，并让每个主机通过符号链接进入它，以便 Claude 和 Codex 执行相同的代码，而不是相互偏离：

```text
~/.claude/skills/img2threejs -> <your checkout>
~/.codex/skills/img2threejs  -> <your checkout>
```

## 何时使用

用户附加/指向一个对象图像，并希望获得程序化的 Three.js 模型、重建/动画/破坏计划、雕塑规范或代码。也用于材质研究、可行动的道具、游戏对象、植物学/机械部件和风格化重建。

## 核心承诺

从照片雕塑，按顺序——永远不要一次性处理网格：
1. **首先运行 `python3 forge/next.py --state .img2threejs/state.json [<spec>]`**，在每次启动、恢复和每次纠正迭代之前。它报告了按顺序的清单、确切的下一个命令、证据状态和有界纠正循环状态；它永远不会取代规范/通行证门。遵守硬性停止；永远不要从记忆中继续。
2. **验证**图像是否适合 3D 目标 (`grimoire/intake/validation_rubric.md`)。
3. **评估**对象类别+复杂性，然后在任何代码之前编写 `qualityContract`。
4. **规范**它：组件层次结构、材质、照明、枢轴、插座、动作锚点。
5. **按步骤构建**从块化→结构→形状→材质→照明→交互→优化。
6. **验证**每个步骤，将屏幕截图与参考进行比较；如果全局分数看起来很好，即使身份定义特征错误，也要失败一个步骤。

明确说明何时输出是近似/风格化/低多边形。单个图像无法揭示隐藏的侧面或保证精确的几何形状——与其假装有信心，不如这样说。

## 强制本地状态门

对话上下文是易失的；`.img2threejs/state.json` 是本地清单权威。每次重建初始化一次，然后通过它门控每个步骤：

```bash
python3 forge/state.py init --state .img2threejs/state.json --reference <img> --profile <generic|character|installed-domain> --spec object-sculpt-spec.json
python3 forge/next.py --state .img2threejs/state.json [object-sculpt-spec.json]
python3 forge/state.py mark <step-id> --state .img2threejs/state.json --evidence <path>
```

- `next.py` 打印当前步骤、通行证、不完整的强制步骤、确切的下一个命令和 `loop/max`。退出代码 3 或 `status=stopped` 是硬性停止：报告原因并请求输入。永远不要通过重建聊天历史来绕过它。
- 每个完成的步骤都需要证据；仅使用 `--reason` 将不适用步骤标记为 `skipped`——禁止沉默遗漏。循环计数来自 `reviewHistory` 操作 (`refine-spec`/`refine-code`)，而不是代理内存。默认值：每个通行证 3 次纠正，总共 6 次。
- 一个域配置文件的步骤、门和参考材料来自**注册**：存储库中的模块 (`character`) 和安装的插件 (`cs2`，`animated-character` 来自 `plugin-character`) 相同地注册，并且 `forge/state.py init` 指出可用的内容。配置文件添加强制门，而不会改变核心顺序——一个域插件通常需要一个权威的分类、一个输入清单和一个机器可读的域审查，然后才是 AI 审查；`character` 要求角色合同和地标证据；`animated-character`（需要安装的 `plugin-character`）添加 `character` 的全部内容加上九个 Stage R 步骤 (`grimoire/readiness/animation_contract.md`)。每当 rig 必须移动时，请选择它——在 `character` 上，Stage R 门是缺失的，构建在没有运行它们的情况下完成，这就是动画以前损坏的方式。它的顺序是承重：修复网格，冻结它，附加地绑定，然后验证一致性。每个配置文件记录了适用性、投影适用性和
材料证据适用性。状态文件是一个可恢复的索引，而不是视觉证据：渲染、规范、审查历史和确定性门仍然是权威工件。

## 必需的输入

- 一个图像路径 / 屏幕截图 / URL / 附加图像（如果缺失或不可以读取，请询问）
- 预期用途：道具、游戏对象、英雄渲染、可玩/可破坏的对象、动画 rig
  （默认：实时浏览器道具，具有交互式性能）
- 当域插件提供项目时，其输入步骤要求的一切，或者明确要求用户/视觉提供者提供；仅靠启发式检测不足以选择几何适配器

## 循环（脚本执行强制；代理视觉执行判断）

从技能根目录（`forge/...`）运行脚本。纯 Python 3.10+ 标准库，无需 pip 安装。
完整标志：`grimoire/scripts.md`。永远不要让脚本*评分*视觉效果——那是代理的工作。

1. **首先分析图像**（代理视觉，在任何脚本之前）：工作 `grimoire/intake/image_analysis.md` 中的分层观察协议——识别/分类，分解宏观→中观→微观，映射部件关系，用 PBR 术语命名材质，列出定义身份的特征，并标记单个视图隐藏的内容。观察先于推断；受控的 3D 词汇；3D 对象空间而不是 2D 图像空间。然后探测本地图像：
   `forge/stage1_intake/probe_image.py <image>`（仅元数据，不是视觉检查）。
1a. **本地规范搜索**——在图像分析之后，在编写或细化规范之前，拉取本地域证据（解剖学/PBR/磨损/几何/运行时/物理）而不是发明它：
   `python3 forge/stage2_spec/new_pre_spec_assessment.py "Name" --image <img> --out assessment.json`
   （自动运行 BM25 over `core_3d` 集合，或声明的域贡献的集合——集合永远不会根据目标名称猜测；写入 `localSpecSearch` 套件，`new_sculpt_spec.py --assessment` 将其带入规范）。完整查询扩展配方（双语术语，聚焦 `search_specs.py` 检索，缓存规则）：
   `grimoire/intake/local_spec_search.md`。在重试不完整或域特定查询之前，必须阅读它。
1b. **域输入**——当域插件提供项目时，在预规范编写之前完成其输入步骤（录取、启发式信号、分类、家族/路线解决）。
   必须阅读其步骤名称的合同，完全，然后创建清单并运行预规范评估。
1c. **可选保真度证据适配器**——只有在它们改进观察到的薄弱点时；stdlib 核心仍然是权威的。薄/复杂掩码→本地 SAM2；角色面部/姿势→MediaPipe；弱前/后线索→Depth Anything V2
   (`forge/stage1_intake/run_vision_adapter.py <segment|landmarks|depth> ...`; 每个适配器都发出可追溯性；单目深度是相对的）。**MCP 仅场景突变永远不会被视为实现**——将证明的更改写回规范或 TypeScript，重新构建，重新捕获。
   完整适配器+MCP 路由和权威边界：
   `docs/integrations/reference_fidelity_tooling.md`。
2. **预规范评估门**——分类+评分复杂性+在编写任何代码之前编写质量合同：
   `forge/stage2_spec/new_pre_spec_assessment.py "Name" --image <img> --complexity <simple|moderate|complex|ultra-complex> --out assessment.json`。规则：`grimoire/intake/quality_contract.md`。
   设置 `objectClass.primaryDomain` (`object` | `character` | `hybrid`) 并填充种子 `detailInventory`（其 `targetMinDetails` 随复杂性缩放）。域插件可以**提高**这些地板通过其增强——合并夹具，所以插件永远不会降低一个（皮肤的完成/磨损/硬件是项目，所以这种域被保持在最高的保真度条。程序化几何形状，但将完成路由通过步骤 2c 中的投影路径——对于带有图案的皮肤（Doppler/Gamma/Marble/Fade）的程序化完成对于参考来说是可见的。域插件提供自己的完成规则簿和纹理获取指南；阅读其清单步骤名称。
2b. **细节清单**（对于详细主题不要跳过）——扫描区域并列举每个定义身份的小细节（光泽、倒角、紧固件、线条、轮廓、污渍）：
   `forge/stage1_intake/build_detail_inventory.py <image> --mode grid-3x3 --out-dir <dir> --out di.json`。
   每个细节必须映射到 `component.localFeatures` 或 `material.localOverrides` 条目——永远不要只有散文。分类+3D-术语配方：`grimoire/intake/detail_inventory.md`。
2c. **投影优先保真度**（角色和参考匹配的表面——绘制的皮肤、贴花、绘制的图案）——当目标是匹配特定参考的表面时，将照片自己的像素放在网格上，而不是程序化地近似它们。这是保真度的最大杠杆；对于带有图案的表面，程序化材质是重建的 #1 失败。配方（`grimoire/character/likeness_maximization.md`——它的两个杠杆概括了过去的角色）：解决相机（`stage1_intake/solve_camera_pose.py` → `referenceCamera`），**去光**参考（`stage1_intake/delight_albedo.py`，硬性要求——去光化是使投影安全的原因），然后投影去光裁剪并将其烘焙到 UV 中
   (`stage3_build/bake_projected_texture.py --mesh-id <id>`）。对于绘制的皮肤，投影去光裁剪就是完成——没有程序化的 Doppler 材质。对于角色，首先捕获地标
   (`stage1_intake/extract_landmarks.py --out anatomy.json`), 填充 `preSpecAssessment.anatomy`，路由 `grimoire/character/reconstruction.md`。单个视图无法显示隐藏的侧面——当它很重要时，报告每个区域的置信度并请求更多视图。
   角色子路线，按顺序——在塑造任何部分之前决定哪些部分存在，并且在头发之前塑造头部：
   - **部件** — `grimoire/character/structure_decomposition.md`
   - **头部** — `grimoire/character/head_construction.md`（ likeness 门读取的）
   - **头发** — `grimoire/character/stylized_hair_threejs.md` + 参数合同在
     `grimoire/character/threejs_hair_parameter_contract.json` 中。只有在轮廓审查通过后才能锁定拓扑——材质调整无法修复错误的锁拓扑。
2d. **无参考的人形**——一个没有参考图像的通用人物没有任何可衡量的，所以从公共规范填充解剖学：
   `forge/stage2_spec/humanoid_proportions.py <spec> --style-heads 8 --in-place`. 它写入 `anatomy.source: "canon-table"`，所以规范永远不会被误认为是测量，当规范命名参考图像时，它拒绝运行，并且它命名任何规范不提供的内容，而不是插值它。
3. 从评估中编写规范：
   `forge/stage2_spec/new_sculpt_spec.py "Name" --image <img> --assessment assessment.json --augmentation spec-augmentation.json --domain <profile> --out object-sculpt-spec.json`（清单步骤携带解析的标志）。
   用对象的真正定义系统（≤5 关键，≤3 每个通行证重要）替换通用的起始 `featureReviewTargets`；对于角色添加 `anatomy-proportion`，
   `face-landmark-placement`，`pose-silhouette`，`outfit-and-palette`。只使用 3D-图形术语（`grimoire/glossary/3d_vocabulary.md`），永远不要“漂亮/光滑/闪亮”。在挑选 `primitive` 之前，为每个组件分类 `topologyClass`/`topologyRationale`，根据 `grimoire/intake/surface_topology.md`。选择 `primitive` — 这是防止连续有机形状被选为盒子的原因。
4. 当材质保真度很重要并且存在源图像时，分析每个材质的**完成**，然后提取参考 PBR 证据，两者都是每个裁剪（验证裁剪是否在您认为的部件上）：
   - `forge/stage1_intake/analyze_texture.py <crop> --spec spec.json --material-id <id> --in-place`
     分类完成，提取渐变调色板，并将基于文档的
     MeshPhysicalMaterial 标量写入材质。配方+Three.js 纹理/PBR 规则：
     `grimoire/build/threejs_texture_reference.md`。经验法则：**实心反照率用于平面绘画，真实参考裁剪用于图案化完成**。
   - `forge/stage1_intake/extract_pbr_evidence.py <crop> --out-dir <dir> --material-id <id> --target-threshold 0.7`.
     置信度 < 0.7 是停止/细化输入信号，不是通过。这是推断，不是反向渲染。
   - 对于多个命名区域：`forge/stage1_intake/material_region_analysis.py --manifest regions.json --out-dir material-evidence --out material-analysis.json`，
     从 `docs/materials/material-reference.json` 中解析每个分配，使用 `forge/stage2_spec/apply_material_analysis.py` 将其连接起来。
   - 发射受控材质相机/裁剪合同 (`forge/stage4_review/material_views.py`),
     比较可见足迹裁剪 (`material_comparator.py`), 仅应用有界材质范围的校正 (`material_feedback.py`), 并记录阻塞结果 (`material_gate.py`)。
5. 验证，然后在生成代码之前进行严格验证：
   `forge/stage2_spec/validate_sculpt_spec.py object-sculpt-spec.json` 然后 `--strict-quality`。
   严格阻止浅规范（一个复杂对象只有一个根，没有重复系统，没有本地覆盖，没有微组是**不**实施就绪的，即使 JSON 验证通过）。
6. **锁定构建通行证**——仅触摸当前未解锁的通行证：
   `forge/stage3_build/orchestrate_passes.py status object-sculpt-spec.json`
   `forge/stage3_build/generate_threejs_factory.py object-sculpt-spec.json --out src/createObjectModel.ts`
   生成器是失败关闭的：`strict-quality` 必须通过它才写入任何工厂，并且未来的 `--pass-id` 在先前的通行证被审查 `continue` 之前才会失败。如果受阻，保留 `BLOCKED` 工件并细化主题特定规范；不要用通用模板替换。
   本地状态仅在新通行证或 `refine-spec` 时才添加 `--force`；`refine-code` 编辑当前工件而不重新生成它。在覆盖之前，将有效的手工细化带回到规范；生成的代码不能是重建决策的唯一副本。
6a. **达到三角形预算**。 `performanceBudget.targetTriangles` 为每个具有段计数的 `primitive` 选择细分级别（低 ≤6k，标准 ≤60k，否则英雄）并限制隐式表面采样网格。如果一个级别不够精确，添加
   `geometryDescriptor.decimate: {"targetRatio": 0.4}` 到该组件——在生成的工厂中执行四边形折叠，在皮肤绑定之前运行，以便在剩余顶点上计算权重。它只保留 `position`（法线重新计算），所以它被拒绝在编写的/展开的 `uvStrategy` 上。离线 LOD 级别：
   `forge/stage3_build/decimate.py <mesh.json> --ratio <r> --json`.
7. 在浏览器/预览中渲染当前通行证，在审查视点捕获屏幕截图。
7a. **偏轴和放置门**——单个审查视点不是关于模型证据。捕获一个转盘，而不是一帧，并运行所有三个；每个都捕获了老门构建时被忽略的缺陷类别（头骨上的一个洞，帽子在臀部和漂浮的护身符都通过了八次仅前视图审查）：
   `forge/stage4_review/turntable_gate.py --capture 0=front.png --capture 90=right.png --capture 180=rear.png --capture 270=left.png --json`
   `node runtime/scripts/export_mesh_geometry.mjs --url <preview> --out meshes.json` 然后执行
   `forge/stage4_review/self_intersection.py meshes.json --json`
   `forge/stage4_review/attachment_anchor.py object-sculpt-spec.json --measured measured.json --json`
   所有三个都退出 `0` 清洁 / `1` 门失败 / `2` 错误。失败会阻止 `continue` 即使全局保真度分数通过。阅读 `sampledVertexCount` / `unmeasuredAttachments` /
   `missingAzimuths` 在相信一个干净的裁决之前：每个都命名门没有查看的内容。
8. **在 AI 视觉之前运行确定性门**。必须完全阅读
   `grimoire/review/gates_reference.md` 和 `grimoire/review/self_correction.md`。运行
   `forge/stage4_review/diagnose_render.py` 并使用 `--spec object-sculpt-spec.json --pass-id <pass> --in-place` 记录通过 Tier 1 的结果；对于非平面形式，还运行
   `forge/stage4_review/diagnose_render_multi_angle.py` 使用固定视图和至少两个有意义的轨道视图。然后运行
   `forge/stage3_build/orchestrate_passes.py check object-sculpt-spec.json --pass-id <pass>`.
9. 打包一个并排表，然后使用代理视觉检查它：
   `forge/stage4_review/make_comparison_sheet.py --reference <img> --render <shot> --out cmp.png --json`.
10. 记录审查（整体+每层+每特征评分+决策）:
    `forge/stage4_review/append_review.py object-sculpt-spec.json --pass-id <pass> --fidelity <0-1> --action <continue|refine-spec|refine-code|request-input|stop> --summary "..." --render-screenshot <shot> --comparison-image cmp.png --ai-vision-score <0-1> --layer-scores-json '{...}' --feature-reviews-json <f.json> --in-place`.
    当域插件贡献一个审查门时，首先使用该插件审查步骤名称的命令生成其版本化报告，然后使用
    `--domain-review-json <report>.json --review-scene-json <the plugin's scene fixture>` 附加它。清单步骤携带解析的路径。
    一个失败的家族、绘制的区域、投影覆盖、关键细节或轨道门会阻止 `continue` 即使全局分数通过。查看插件的审查门文档。
11. 同步管道状态后手动审查编辑，记录清单证据，然后在另一个纠正或通行证之前重新运行本地状态门：
    `forge/stage3_build/orchestrate_passes.py sync object-sculpt-spec.json --in-place`
    `python3 forge/next.py --state .img2threejs/state.json object-sculpt-spec.json`.
12. 在声明完成之前，运行
    `forge/stage4_review/check_part_coverage.py --spec object-sculpt-spec.json --manifest parts.json`
    并验证动作就绪的层次结构。仅使用证据标记 `part-coverage` 和 `action-ready`。

## GLB 介导的 v2 渲染保真度轨道（1.5 alpha）

当用户提供一个 GLB 作为中间参考时，浏览器渲染的 GLB 是独立编写的程序化工厂的结构和视觉基线。原始 GLB 永远不是像素证据，其拓扑/材质永远不会复制到工厂中。在任何工厂编辑之前——完整合同在 `grimoire/build/python_threejs_render_bridge.md` 中，机器可读模式在 `docs/specs/render-profile.v2.schema.json` 中 (+ 示例；失败关闭验证）：

1. `forge/stage1_intake/probe_glb.py` 首先运行。一个合并的单一节点/单一网格资产是 `insufficient` 用于语义标签；在声称精确区域之前请求一个多部分 GLB 或一个浏览器语义-ID 通过：`forge/stage1_intake/probe_glb.py`（元数据仅，不是视觉检查）。
2. 编写一个共享的 `render-profile.v2`（`forge/stage4_review/validate_render_profile.py`）由 GLB 和程序化路线使用。区域 ID 是主题特定的，永远不会继承自示例配置文件；在 `extensions.requiredSemanticRegions` 中声明所需的集合，以便遗漏是一个硬验证错误。
3. 捕获每个允许视图的六个通行证（`beauty`，`alpha-silhouette`，`semantic-id`，`depth`，
   `normal`，`roughness-material-id`）；使用 `forge/stage4_review/compare_region_passes.py` 进行评分。缺少语义-ID 数据会阻塞每个区域的置信度，而不是回退到整张图像的分数。
4. 使用区域特定的连续几何形状——当区域的轮廓需要连续表面时，永远不要用浮点原语替换面部/头部体积、布料外壳或尾巴。
5. 每次循环运行一个纠正组，按顺序：`camera → silhouette → face → clothing → accessory
   → materials → lighting`; 每次组后重新捕获完整通行证集并记录更改的组、哈希和分数。永远不要组合组进行诊断。

## 门（不要跳过）

在任何视觉审查或 `continue` 决策之前，必须阅读 `grimoire/review/gates_reference.md` 中的完整门到门的合同（Divine Eye, VLM rescue, 多角度, 内部差异,
对映, 头发, 域审查, 有界纠正, Divine Eye fit, 屏幕截图反馈, 组装,
附件, 材质, 细节清单, rig 负载, 角色跟踪）。简而言之：

- 首先验证参考（`grimoire/intake/validation_rubric.md`, `check_reference_admission.py`）。
- `divine_eye.py` 是确定性第一的；VLM (`vlm_gate.py`) 是一个受门控的最后一层，永远不会在硬门失败时咨询。
- 非平面形式必须在 ≥2 个角度上保持（`diagnose_render_multi_angle.py`）。
- 每个视觉通行证都在轮廓内部测量 (`interior_difference.py`)。轮廓 IoU 读取 ~11% 的角色单元：一个面部被删除的模型与完成的面部得分相同 0.8803。
- 每个 `-l`/`-r` 对都是镜像，而不是旋转——在规范时间就是硬性的 (`validate_chirality`)。两个方面以相同的方式错误地通过仍然通过，并且需要 `medial_lateral_bias` 与参考进行比较。
- 头发主题：`scalp_exposure.py` 是几何形状的硬门，在任何渲染之前运行；覆盖率不足永远不会单独授权扩大质量。
- 默认表示级别是 `shell`，而不是锁； Strand 印象来自面元和材质 (`hair.human.code-only`), 因为这个技能不会发出纹理。
- `plane-card` 对于头发是拒绝的（需要一个代理纹理这个技能无法发出）。
- 头发是刚性父代，永远不会平滑着色（geodesic field 运行通过头骨）。

## 域插件

域插件使运行精确，此管道会推断。它贡献自己的清单步骤和门，并发布此管道在 `spec-authoring` 时拉取 `spec-augmentation.json`，该管道在规范编写时使用。如果没有插件服务项目，这里没有任何变化：编写骨架并从参考推断形状，就像任何其他对象一样。

- 插件贡献的步骤出现在清单中，它们有自己的 ids 和解析的路径。阅读每个步骤名称——插件将其自己的合同发送，它控制其自己的域。
- 插件可以**提高**此管道的质量地板，并且永远不会降低一个；合并夹具。
- 不为项目服务的插件不发布任何增强。这不是错误，也不是受阻运行：它是通用路径，重建通过推断进行。

### The img2 harness

插件由 `img2 harness
([img2threejs/img2](https://github.com/img2threejs/img2))` 安装和管理，这是一个独立的、无依赖的 CLI（Node 启动器，Python 核心）。此技能
永远不会自己安装任何东西：当 `state.py init` 命名配置文件不可用时，命名 `img2 add` 命令来安装它并停止——永远不要用域逻辑替换供应商。

```bash
img2 add img2threejs/plugin-<id> --ref <tag>      # 在标签处安装插件 (例如 plugin-cs2)
img2 doctor                                       # 每个主机解析的内容：基础技能路径 + 版本, 插件门
img2 capabilities --from-kind image --to-kind glb # 哪个安装的插件服务于边缘
```

设置和完整 CLI 参考 位于 README 快速启动和 harness 仓库的文档中。

## Forge 运行时合同

细分运行时测试将生成的 TypeScript 与展示 checkout 进行编译。设置
`IMG2THREEJS_SHOWCASE_ROOT` 为该 checkout；如果没有它，本地运行时测试将带有可操作的提示消息跳过，而静态合同仍然运行。CI 应该设置 `IMG2THREEJS_REQUIRE_SHOWCASE=1`
以将缺少展示 checkout 转换为测试失败。

```bash
IMG2THREEJS_SHOWCASE_ROOT=/path/to/img2threejs-showcase python3 forge/tests/test_subdivision.py
IMG2THREEJS_SHOWCASE_ROOT=/path/to/img2threejs-showcase python3 -m unittest discover -s forge/tests
IMG2THREEJS_SHOWCASE_ROOT=/path/to/img2threejs-showcase python3 forge/tests/test_showcase_tsc_smoke.py
```

## 实现规则（简略）

除非项目使用包装器，否则使用 TypeScript + 纯 Three.js。`Group` 工厂
`createObjectNameModel(spec, options)`，重建数据与渲染器对象分开保存，所有程序化噪声使用确定性种子。优先使用基元 / `Shape` 挤压 / 曲线+tube /
实例化 / 位移 / 生成的画布纹理，而不是任何外部艺术。完整几何形状 & 材质配方 + 艰难获得的失败模式：`grimoire/build/geometry_patterns.md`。

### 可选 Python ↔ Three.js 渲染桥接

当请求使用 Python 进行角色渲染时，将其用作围绕浏览器 Three.js 运行的确定性工作/证据层：相机批处理清单、源/输出哈希、就绪和解决检查、屏幕截图持久性、掩码、诊断和比较包装。目标 Three.js 浏览器路线仍然是渲染权威。不要默默地用 Blender/VRM/GLB 输出替换程序化 TypeScript 工厂。完整路由、清单字段和失败规则：
`grimoire/build/python_threejs_render_bridge.md`。

### 标准角色管道（合并 1.5 beta + alpha）

使用 `grimoire/readiness/standard_character_pipeline.md` 进行角色工作。Beta 拥有严格的雕塑/构建/审查门；alpha 拥有确定性相机清单、浏览器屏幕截图证据和 UniRig 形式的 rig 验证。CharacterGen、Tripo、VRM 和其他神经/资产系统是可选适配器，具有源、检查点、许可证、坐标转换和输出哈希。它们永远不会默默地替换程序化 TypeScript 工厂。图像到网格系统发出静态网格，没有骨架，所以其输出永远不会是动画就绪的，无论它看起来多么好。可执行入口点：`forge/stage4_review/render_bridge.py` 和
`scripts/capture_threejs_playwright.py` (`init → 浏览器捕获 → 验证 → 诊断`; 捕获必须操作在真实的 showcase/浏览器路线，并在工作空间中留下可读的 PNGs)。

## 输出

- **仅分析**：适用性裁决 + 分数，对象提取，宏观→中观→微观层次结构，
  几何策略，材质/照明配方，动画/破坏可行性，计划 + 风险。
- **实施**：以上简要，然后编辑代码；验证类型检查/构建 + 屏幕截图。
- **不可行**：命名阻塞器，询问更多视图 / 更干净的图像 / 接受的风格化 / 更窄的目标。 “此图像无法从此图像达到所需的保真度”是一个有效结果。
