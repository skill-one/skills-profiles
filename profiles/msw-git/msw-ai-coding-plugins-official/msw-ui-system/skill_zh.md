# msw-ui-system

MSW `.ui` 单入口点 — **设计指南 + 组件API + 构建器调用 + 运行时模式** 集成于一个技能中。

与现有技能的角色分工：

| 技能 | 责任 |
|------|------|
| `msw-ui-system`（此技能） | 所有 `.ui` — 设计（什么/何时/为何）、组件API/枚举（什么）、构建器调用（如何变异）、运行时mlua模式。**`.ui`变异必须始终通过此技能的构建器进行** |
| `references/templates/` | 预构建的样式包 — `.ui` + ruid-map + 按钮处理器包 |

---

## 0. 路由

根据请求关键词分支到子参考文档。

| 触发器 | 参考文档 |
|--------|----------|
| "anchor/pivot/coordinates/why is the position wrong", "RectTransform", "stretch" | [`references/ui-fundamentals.md`](references/ui-fundamentals.md) §1–§8 |
| "mobile", "safe area", "1920", "MobileOnly", "ActivePlatform", "touch size", "PC reserved zone", "font size by device" | [`references/ui-fundamentals.md`](references/ui-fundamentals.md) §9 |
| "UIGroup", "above popup", "z-order", "displayOrder", "CanvasGroup", "opacity propagation", "Enable vs Visible" | [`references/ui-hierarchy.md`](references/ui-hierarchy.md)；对于运行时兄弟重新排序也请阅读 [`references/runtime-patterns.md`](references/runtime-patterns.md) §7 |
| "which component", "Sprite vs Text vs Button", "9-slice", "scroll list", "GridView vs ScrollLayoutGroup" | [`references/component-api.md`](references/component-api.md) §"Component Selection Guide" |
| "sprite pivot", "9-slice border", "slice boundary", "set sliced asset metadata", "resource storage properties" | 通过 `msw-mcp` `asset_update_resource_storage_info` 直接设置资源端元数据；对于 `.ui` 端请查看 [`references/component-api.md`](references/component-api.md) §"SpriteGUIRenderer — ImageType Selection" |
| "make a HUD", "popup placement", "toast", "menu", "inventory grid", "scroll list" | [`references/layout-recipes.md`](references/layout-recipes.md) |
| "connect .mlua after building with .ui builder", "property default UUID", "binding without drag" | [`../msw-general/references/builder-protocol-ui.md`](../msw-general/references/builder-protocol-ui.md) §3.6 Binding Injection (统一入口点 — 使用 [`builder-protocol.md`](../msw-general/references/builder-protocol.md) 核心) |
| 运行时UI组件字段读写、组件属性名称/类型 (`ButtonComponent.Colors`, `TextGUIRendererComponent.Overflow`, `SpriteGUIRendererComponent.FillAmount`…) | [`references/component-api.md`](references/component-api.md) **在每次 `.mlua` 访问UI组件字段前必须先阅读** |
| 枚举值 (`AlignmentType`, `TextOverflowMode`, `ImageType`, `UIBasicParticleType`…) | [`references/component-api.md`](references/component-api.md) §Enums |
| 运行时mlua模式（弹窗打开/关闭、toast淡出、血条、GridView、拖拽、标签、冷却），运行时UI注意事项（客户端独有、服务器端nil等） | [`references/runtime-patterns.md`](references/runtime-patterns.md) |
| **`.ui` 构建器调用方法**（UIBuilder API、锚点预设、自动校验、组件添加/补丁/删除） | [`../msw-general/references/builder-protocol-ui.md`](../msw-general/references/builder-protocol-ui.md) §3 UIBuilder (统一入口点 — 使用 [`builder-protocol.md`](../msw-general/references/builder-protocol.md) 核心；`.map` MapBuilder / `.model` ModelBuilder 位于兄弟的每个构建器文件中) |
| "sound", "sfx", "click sound", "hover sound", "button audio", "PlaySound" | [`references/ui-sound.md`](references/ui-sound.md) |

---

## 1. 基本工作流程

```
(1) 明确意图       布局草图（ASCII或口头）+ 要附加的组
(2) 检查设计指南   至少匹配 ui-fundamentals / ui-hierarchy / component-api §Component Selection Guide 之一
(3) 构建器预检     阅读 ../msw-general/references/builder-protocol.md (核心) + builder-protocol-ui.md §3 (统一调用协议入口)
(4) 匹配配方       从 layout-recipes.md 选择最接近的模板
(5) 调用构建器     通过 scripts/msw_ui_builder.cjs 创建/补丁（协议：builder-protocol-ui.md §3）
(6) 注入绑定       通过 b.write(path, { bind: {...} }) 或 b.injectBindings(...) 自动注入 .mlua 属性默认UUID（builder-protocol-ui.md §3.6 Binding Injection）
(7) 自我验证       write() 自动运行 scripts/ui_lint.cjs（严格模式默认开启）
(8) 预览           通过 scripts/preview_ui_layout.cjs 进行视觉检查
(9) 音效校验       对于任何交互式按钮，提供点击/悬停SFX连线（references/ui-sound.md）
(10) Maker刷新      应用到引擎
```

## 2. 全局规则

### 绝不

1. **不要直接编辑 `.ui` JSON** — `.ui` 的创建/修改 **必须** 通过 `scripts/msw_ui_builder.cjs`。手动编辑会破坏 UUID·ValueType·`@components` 的一致性并导致静默丢失。
2. **通过构建器读取现有的 `.ui` 文件** — 通过 `UIBuilder.read(filepath)` / `.find()` / `.listEntities()` 查询。不要直接grep/解析原始JSON。
   - `.ui` 直接 `Read` 和 shell 命令（如 `cat` / `type` / `Get-Content` / `rg` / `grep` / `sed` / `awk` / `cp` / `mv`）被注册的守卫阻止。使用 `UIBuilder.read/load/snapshot` 进行读取，使用 `b.write()` 进行写入。删除整个 `.ui` 文件没有构建器API — 使用 `node -e "require('fs').unlinkSync('ui/<File>.ui')"` 然后刷新（shell `rm`/`cat` 被守卫阻止；`node -e` 构建器调用不受影响）。
3. 直接设置 `Position` — 仅使用 `anchoredPosition`（Position 由引擎管理）
4. 通过固定锚点的 OffsetMin/Max 表达尺寸（AnchorsMin == AnchorsMax）的同时也使用 `anchoredPosition` — 不要混合两种模式
5. 构建器创建新的UUID，但 `.mlua` 属性默认值未更新 — 绑定中断

### 始终

1. **构建器协议预检 — [`../msw-general/references/builder-protocol.md`](../msw-general/references/builder-protocol.md) (核心) + [`../msw-general/references/builder-protocol-ui.md`](../msw-general/references/builder-protocol-ui.md) §3 在任何 `.ui` 变异前必须处于上下文中**（仅在会话未加载或因压缩丢失时才读取）** (UIBuilder API, 写入自动校验, 位置/锚点规则, 绑定注入, 覆盖间隙)。核心包含共享契约和跨构建器流程；`.map` MapBuilder / `.model` ModelBuilder 位于兄弟的每个构建器文件中 — 统一入口点因为跨流程是相互交错的。
2. 调用构建器前至少检查一个设计指南（`ui-fundamentals` / `ui-hierarchy` / `component-api` §Component Selection Guide）
3. 首先匹配配方；仅作为最后手段才从头构建
4. 对于边缘位置使用公式：`pos = ±(margin + size/2)`
5. 将弹窗和toast分离到它们**各自的 `.ui` 根 UIGroup**，独立显示/隐藏；使用 `empty()` / `panel()` 作为内部容器，永远不要嵌套 `group()`
6. 验证文本 `Alignment` 默认为 `UpperLeft(0)` — 95% 的 "我居中但它粘在左边" 问题是此问题
7. 按钮触摸目标 ≥ 88×88（移动端支持）
8. **创建任何交互式按钮后** — 主动建议通过 [`references/ui-sound.md`](references/ui-sound.md) 连接点击/悬停SFX（默认UI SFX RUIDs可用）。仅当用户明确选择退出或按钮纯粹装饰时才跳过。
9. **构建嵌套的树，而不是扁平的。** 单元（窗口+标题/关闭、行+芯片/值、槽+图标/计数）的控制必须通过 `"Parent/Child"` 路径共享父级，以便它们作为一个整体移动/淡入淡出/切换/绑定。在创建子级之前创建每个父级；缺少父级会导致校验失败（`L025` ERROR）。
10. **不要将根级文本堆叠在兄弟框上。** `ui_lint` 报告此为 `L030` WARN。将文本嵌套在框下，使用 `button()` 为可点击的标记框，或通过 `panel()` / `sprite()` 的 `text` 选项直接在它们上放置标签。

---

## 3. 子文档

- [`references/ui-fundamentals.md`](references/ui-fundamentals.md) — 坐标系、RectTransform 3元素、锚点模式确定（§1–§8）+ 分辨率·安全区域·PC保留区域·触摸目标·字体大小·平台分离（§9）
- [`references/ui-hierarchy.md`](references/ui-hierarchy.md) — UIGroup / displayOrder / CanvasGroup / Enable vs Visible
- [`references/component-api.md`](references/component-api.md) — §"Component Selection Guide" (什么/何时/为何) + 完整组件属性/方法/事件表（什么）+ 所有UI相关的枚举值（§Enums）
- [`references/layout-recipes.md`](references/layout-recipes.md) — 布局模板集合
- [`references/runtime-patterns.md`](references/runtime-patterns.md) — `.mlua` 运行时模式（弹窗/toast/血条/grid/拖拽…）+ 运行时UI注意事项
- [`references/ui-sound.md`](references/ui-sound.md) — UI音效集成（`_SoundService:PlaySound`、点击/悬停钩子、默认UI SFX RUIDs）
- [`../msw-general/references/builder-protocol-ui.md`](../msw-general/references/builder-protocol-ui.md) §3 — **`.ui` CJS构建器调用协议（统一入口点 — 使用 [`builder-protocol.md`](../msw-general/references/builder-protocol.md) 核心）** — `.map` MapBuilder / `.model` ModelBuilder 位于兄弟的每个构建器文件中。panel / text / sprite / button / slider / scroll / script / group / mask / grid / avatar / touchReceive / skeleton / areaParticle / basicParticle, 组件CRUD, 锚点预设, 写入自动校验, 和 `.mlua` 属性UUID自动绑定都位于 §3 + §3.6。
- [`references/templates/templates.md`](references/templates/templates.md) — 预构建样式包索引（`style-N-*` `.ui`, [`ruid-map.md`](references/templates/style-1-black/ruid-map.md), `Popupbutton.mlua`）

## 4. 脚本

- `scripts/msw_ui_builder.cjs` — `.ui` 构建器核心（UIBuilder类）。使用前请阅读 [`../msw-general/references/builder-protocol.md`](../msw-general/references/builder-protocol.md) (核心) + [`../msw-general/references/builder-protocol-ui.md`](../msw-general/references/builder-protocol-ui.md) §3 (统一入口点)。
- `scripts/preview_ui_layout.cjs` — `.ui` 布局视觉检查 + 触摸目标警告
- `scripts/ui_lint.cjs` — `.ui` 文件自我验证（自动由 `write()` 调用）
- `scripts/ui_recipe.cjs` — 基于配方的脚手架

---

## 不在范围内

- `.map` / `.model` / `.tileset` 构建器 — 不在此技能的范围内
- `.ui` JSON模式（原始字段形状、`@type`/`@components` 包装、AlignmentOption 0–15映射等）— 由构建器内部处理。用户/AI不需要直接了解
- 无障碍模式（替代文本、屏幕阅读器提示、焦点顺序）— 未涵盖
- 错误状态UI模式（禁用按钮样式超出 `Transition.Disabled`、验证消息、加载旋转器）— 未涵盖；按项目设计
- 自动化UI测试/布局断言超出 `ui_lint.cjs` 和 `preview_ui_layout.cjs` — 未提供
- 自定义着色器材质（`MaterialId`）— 字段公开但编写着色器在此技能的范围内
