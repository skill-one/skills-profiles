---
name: home-assistant-best-practices
description: "高可用自动化、辅助工具、脚本和仪表板的最佳实践。  \n在以下情况下触发此技能：  \n- 创建或编辑自动化、脚本、场景、仪表板、蓝图  \n- 选择模板传感器、辅助工具或Jinja宏  \n- 重新构建触发器、条件或模式；按钮、遥控器或事件实体自动化  \n- 重命名实体或从device_id迁移到entity_id  \n- 查找卡片类型或域文档；编写AppDaemon应用程序  \n- 删除或恢复备份，或升级Core或操作系统  \n\n症状：  \n- 存在原生选项的Jinja2模板  \n- 使用device_id而不是entity_id  \n- 更改实体ID时未检查消费者  \n- 选择错误的自动化模式  \n- 应使用辅助工具的地方使用了原始传感器或硬编码值  \n- 直接编辑.storage文件，或生成YAML片段  \n- 要求用户为UI集成编辑configuration.yaml  \n- 硬编码蓝图实体或跳过选择器  \n- 未提供恢复路径的情况下更改现有状态  \n- 在模板之间直接复制粘贴Jinja"
---

# Home Assistant 最佳实践

**核心原则：** 尽可能使用 Home Assistant 的原生构造。模板会绕过验证，在运行时静默失败，并使调试变得不透明。

**没有工具可以访问 HA API？** 不要停下来询问访问权限。如果你可以在 HA 网页 UI 上驱动浏览器，就在那里进行更改，但首先向用户展示确切的更改，并在他们确认后再保存：批准点击不会显示他们写入的内容。否则，向用户提供可以在 UI 中创建的完整配置（对于自动化，编辑器的 **以 YAML 编辑** 模式的 YAML；对于辅助工具，其表单字段），并命名你假设的实体 ID。只能以 YAML 形式写入的配置使用文件编辑器应用（或在容器安装的配置文件夹中）进行编辑：首先保留文件副本，然后检查配置，并在 **YAML** 标签的 **工具**（在 2026.8 之前名为 **开发者工具**）中的 **YAML** 选项卡中运行匹配的重载（如果未列出，请重启）。

**在回答之前，先阅读匹配的参考文件。** 本页仅总结 [参考文件](#参考文件) 中的文件；确切的键、字段和工作示例在它们中。阅读与任务行匹配的每个文件，并且仅限于这些文件：不要预先加载所有参考文件。

## 决策工作流

创建任何自动化时，请遵循以下顺序：

### 0. 门控：修改现有配置？

如果你的更改会影响实体 ID、显示名称或跨组件引用——重命名实体或设备、用辅助工具替换模板传感器、转换设备触发器或重构自动化——请先阅读 [safe-refactoring](references/safe-refactoring.md)。该参考文件涵盖了影响分析、设备兄弟发现、显示名称覆盖和更改后的验证。在继续之前，请完成其工作流。

下面的步骤 1-5 适用于新配置或模式评估。

### 1. 检查是否有特定目的的触发器/条件，然后是通用的原生触发器/条件

自 2026.7 版本起，默认构建块是特定目的的触发器/条件——`<domain>.<name>` 键（如运动检测、电量低、门打开）带有区域/楼层/标签目标。首先检查是否有匹配意图的特定目的触发器，然后是通用原生触发器/条件，然后才是模板。在编写触发器之前，请阅读 [triggers-and-conditions #purpose-specific-triggers--conditions-default-since-20267](references/triggers-and-conditions.md#purpose-specific-triggers--conditions-default-since-20267)。

特定目的的触发器在其 `target:` 中也接受 `entity_id`，所以一个已知的传感器并不是回退到 `trigger: state` 的理由。使用特定目的的触发器编写自动化；不要仅将其作为可选升级提供。

**常见替换：**
- 运动传感器、占用传感器或门 `binary_sensor` 上的 `trigger: state` → `motion.detected`/`motion.cleared`、`occupancy.detected`/`occupancy.cleared` 或 `door.opened`/`door.closed`，带有 `target: {entity_id: ...}`，或在区域已知时使用 `area_id`
- 触发器中的单个传感器实体列表 → 一个带有区域/楼层/标签 `target:` 的特定目的触发器
- 在 `motion.detected` 后面的延迟，用于“N 分钟内任何地方都没有运动” → `motion.cleared`，带有 `options: {behavior: all, for: ...}`，它将在每个目标传感器已清除该时长后触发一次（`unavailable` 和 `unknown` 传感器不计入统计）
- `{{ states('x') | float > 25 }}` → `numeric_state` 条件，带有 `above: 25`
- `{{ is_state('x', 'on') and is_state('y', 'on') }}` → `condition: and`，带有状态条件
- `{{ now().hour >= 9 }}` → `condition: time`，带有 `after: "09:00:00"`
- `wait_template: "{{ is_state(...) }}"` → `wait_for_trigger`，带有状态触发器（注意：当状态已经为真时行为不同——见 [safe-refactoring #trigger-restructuring](references/safe-refactoring.md#trigger-restructuring))

### 2. 检查是否有内置辅助工具或 Template Helper

在创建模板传感器之前，请阅读 [helper-selection](references/helper-selection.md)。

**常见替换：**
- 汇总和平均多个传感器 → `min_max` 集成
- 任何-开/全部-开逻辑 → `group` 辅助工具
- 变化率 → `derivative` 集成
- 跨阈值检测 → `threshold` 集成
- 消费跟踪 → `utility_meter` 辅助工具

**如果没有内置辅助工具适用，请使用 Template Helper——而不是 YAML。**
通过 HA 配置流程创建（编程方式或在 UI 中：
设置 → 设备和服务 → 辅助工具 → 创建辅助工具 → 模板）。通过流程创建的辅助工具是 UI 可编辑的；`template:` YAML 条目需要 `template.reload`，并且不可编辑。

在用户要求时、当两种路径都不可用时，或当配置需要流程没有字段的键时（触发器模板和 `attributes:` 是常见的）编写 `template:` YAML。然后使用受管理的 YAML 编辑（[yaml-only-integrations](references/yaml-only-integrations.md)），而不是手动编辑。

### 3. 选择正确的自动化模式

默认 `single` 模式通常是错误的。见 [automation-actions #automation-modes](references/automation-actions.md#automation-modes)。

| 场景 | 模式 |
|------|------|
| 带有超时的运动灯 | `restart` |
| 顺序处理（门锁） | `queued` |
| 每个实体的独立操作 | `parallel` |
| 单次通知 | `single` |

### 4. 使用 entity_id 而不是 device_id

`device_id` 在设备重新添加时会失效。见 [device-control](references/device-control.md)。

**例外：** Zigbee2MQTT 自动发现的设备触发器是可以接受的。

### 5. 对于按钮和遥控器
- **任何暴露 `event.*` 实体的集成：** 使用 `event.received` 针对该实体（见下方的反模式行）
- **ZHA：** 没有事件实体——使用带有 `device_ieee`（持久）的 `event` 触发器
- **Z2M：** 事件实体是实验性的，默认关闭——使用 `device` 触发器（自动发现）或 `mqtt` 触发器

在编写触发器之前，请阅读 [device-control #buttonremote-patterns](references/device-control.md#buttonremote-patterns)。

---

## 严重反模式

| 反模式 | 使用替代方案 | 原因 | 参考 |
|--------|------------|------|-------|
| `condition: template` with `float > 25` | `condition: numeric_state` | 加载时验证，而非运行时 | [triggers-and-conditions #native-conditions](references/triggers-and-conditions.md#native-conditions) |
| `wait_template: "{{ is_state(...) }}"` | `wait_for_trigger` with state trigger | 事件驱动，非轮询；等待*变化*（参见 [safe-refactoring #trigger-restructuring](references/safe-refactoring.md#trigger-restructuring) 以了解语义差异） | [automation-actions #wait-actions](references/automation-actions.md#wait-actions) |
| `device_id` in triggers | `entity_id`（或 `device_ieee` for ZHA） | device_id 在重新添加时失效 | [device-control #entity-id-vs-device-id](references/device-control.md#entity-id-vs-device-id) |
| `event` trigger on an integration's bus event (e.g. `hue_event`) for a button that has an `event.*` entity | `event.received` targeting that entity，并从其 `event_types` 属性读取值 | 实体可以被重命名，并且在集成保持稳定唯一ID时可以存活；总线事件数据因集成而异 | [device-control #buttonremote-patterns](references/device-control.md#buttonremote-patterns) |
| `numeric_state` trigger driving a costly action, unguarded | 在 `trigger.from_state` 中拒绝 `unavailable`/`unknown` 的条件 | 重启或闪烁会重新触发，因此未变化的值会触发而无需跨越（该保护措施也会丢弃实际跨越） | [triggers-and-conditions #unavailable-arms-a-numeric-state-trigger](references/triggers-and-conditions.md#unavailable-arms-a-numeric-state-trigger) |
| `mode: single` for motion lights | `mode: restart` | 重新触发必须重置计时器 | [automation-actions #automation-modes](references/automation-actions.md#automation-modes) |
| `enabled: false` as a top-level key in `automations.yaml` | `automation.turn_off`（临时）或禁用实体注册表（永久） | 不是一个有效的顶级键——在模式验证期间被拒绝；自动化加载为 `unavailable` | [automation-actions #disabling-automations](references/automation-actions.md#disabling-automations) |
| Template sensor for sum/mean | `min_max` helper | 声明式，处理不可用状态 | [helper-selection #numeric-aggregation](references/helper-selection.md#numeric-aggregation) |
| Template binary sensor with threshold | `threshold` helper | 内置迟滞支持 | [helper-selection #threshold](references/helper-selection.md#threshold) |
| Renaming entity IDs without impact analysis | 遵循 [safe-refactoring](references/safe-refactoring.md) 工作流 | 重命名会破坏仪表板、脚本、场景、Config-Entry 数据和存储仪表板，且无声 | [safe-refactoring #entity-renames](references/safe-refactoring.md#entity-renames) |
| Renaming members of Config-Entry-based groups (UI groups) without updating membership | 通过选项流程在注册表重命名后更新组成员资格 | 实体注册表重命名不会更新 Config Entry 中的 `options.entities`——组会无声失效 | [safe-refactoring #config-entry-groups](references/safe-refactoring.md#config-entry-groups) |
| Renaming entities used by Min/Max helpers or custom Config-Entry integrations (e.g. Better Thermostat) without checking their Config-Entry data | 扫描配置条目的 `data`+`options`；在 Min/Max 选项流程中重新选择重命名的实体。一个将其保存在 `data` 中的集成（Better Thermostat）没有API修复：在重命名前告知用户并完整备份。它们在 Config Entry 中存储实体ID，而注册表重命名不会更新它们；单源助手（如 Threshold（自 2025.6 起）和 Generic Thermostat）会自动更新自身 | [safe-refactoring #config-entry-data--blind-spots-for-entity-registry-renames](references/safe-refactoring.md#config-entry-data--blind-spots-for-entity-registry-renames) |
| `template:` sensor/binary sensor in YAML | 通过配置流程使用模板助手 | 流程助手原地重新加载并保持UI可编辑；`template:` 条目需要配置重新加载且不可。例外情况真实——基于触发的模板和 `attributes:` 没有流程字段 | [helper-selection #template-helpers](references/helper-selection.md#template-helpers) |
| Editing `.storage/` files or other HA internal state directly | 使用 HA REST/WebSocket API 管理状态和配置条目 | `.storage/` 文件是HA的内部状态数据库；直接编辑绕过验证、风险损坏，且可能被HA无声覆盖 | — |
| Writing raw YAML to `configuration.yaml` by hand for YAML-only integrations | 使用带备份和验证的托管YAML配置编辑 | 未管理写入有语法错误风险、无备份、跳过 `check_config`——托管编辑提供所有这些功能 | [yaml-only-integrations](references/yaml-only-integrations.md) |
| Generating YAML snippets for automations/scripts/scenes | 使用HA配置API以编程方式创建自动化/脚本；无API访问时，提供配置给UI编辑器 | API调用验证配置、避免语法错误，且无需手动文件编辑或重启 | [triggers-and-conditions](references/triggers-and-conditions.md), [automation-actions](references/automation-actions.md), [examples.yaml](references/examples.yaml) |
| Telling user to edit `configuration.yaml` for integrations | 直接将用户引导至HA UI的“设置 > 设备与服务” | 大多数集成是UI配置的；YAML集成配置是罕见且特定于集成的 | — |
| Referring to HA "add-ons" | 使用术语“Apps” | HA在2026.2中将add-ons重命名为Apps——“Apps是与Home Assistant一起运行的独立应用程序” | — |
| `vacuum.send_command` with vendor room IDs | `vacuum.clean_area` with HA area IDs in `cleaning_area_id`（如果段被映射） | 使用原生HA区域，跨集成工作——但需要先在实体设置中进行段到区域的映射 | [device-control #vacuum-control](references/device-control.md#vacuum-control) |
| Using `color_temp` (mireds) in light actions | 使用 `color_temp_kelvin` 并将值转换为：Kelvin = 1,000,000 ÷ mireds（500 mireds = 2000 K） | `color_temp` 参数在2026.3中被移除；仅支持Kelvin，HA接受任何正数，因此跨复制的mireds值被视为Kelvin（500 mireds变为500 K） | [device-control #lights](references/device-control.md#lights) |
| Saving states or attributes in `variables:`, or hard-coding values, to put devices back after a temporary change | `scene.create` with `snapshot_entities` 在更改前，然后在该场景上 `scene.turn_on` | 快照保留每个实体的状态，包括之前关闭的灯，在一个调用中；变量需要每个属性一个模板，每个实体一个恢复步骤 | [scenes #snapshot--restore-scenecreate](references/scenes.md#snapshot--restore-scenecreate) |
| Person/Device Tracker `entered_home`/`left_home` device triggers or `is_home`/`is_not_home` conditions | `state` trigger `to: home` / `to: not_home`，或 `state` condition | 这些在2026.5中被移除——状态触发和条件是正确的替代方案 | [triggers-and-conditions #presence-and-person-triggers-and-conditions-removed-in-20265](references/triggers-and-conditions.md#presence-and-person-triggers-and-conditions-removed-in-20265) |
| Entity list in a trigger where an area/floor/label target fits | 专用触发器，使用 `target: {area_id: ...}` | 自动化跟随设备变化的区域成员资格——没有陈旧的实体列表 | [triggers-and-conditions #purpose-specific-triggers--conditions-default-since-20267](references/triggers-and-conditions.md#purpose-specific-triggers--conditions-default-since-20267) |
| Old purpose-specific keys (`battery.low`, `vacuum.docked`, `timer.time_remaining`, ...) 或触发 `behavior: any`/`last` | 2026.7重命名的键 (`battery.became_low`, ...) 和 `behavior: each`/`all`（2026.6重命名） | 旧键不再加载；旧行为值引发修复问题并面临移除 | [triggers-and-conditions #purpose-specific-triggers--conditions-default-since-20267](references/triggers-and-conditions.md#purpose-specific-triggers--conditions-default-since-20267) |
| AppDaemon: callbacks in `__init__`, uncancelled `run_in` timers, state in instance variables, hardcoded entity IDs | 在 `initialize()` 中注册，取消后再重新调度，通过 `input_*` 助手持久化，通过 `self.args` 传递ID | 每个都会无声失败、在重新加载时重置或阻止重用 | [appdaemon #appdaemon-specific-anti-patterns](references/appdaemon.md#appdaemon-specific-anti-patterns) |
| Blueprints: hardcoded entities, free text where a selector belongs, `!input` inside a template, missing `source_url` | 带有类型检查的 `!input` 选择器；在模板化前将输入绑定到 `variables:`；始终设置 `source_url` | 硬编码会破坏重用，文本允许拼写错误，而 `!input` 是YAML标签而非模板值 | [blueprint-guide #common-pitfalls](references/blueprint-guide.md#common-pitfalls) |
| Backups: full restore to undo one object edit, no backup before an irreversible operation (registry deletion, integration removal, Core/OS upgrade), calling an action "reversible" without naming its inverse | 单个对象回滚；在不可逆操作（注册表删除、集成移除、Core/OS升级）前备份；命名精确的逆操作或将其视为不可逆 | 完整恢复会撤销自以来的所有无关更改并重启HA；之后的备份会捕获损坏 | [backups #when-a-full-backup-earns-its-cost](references/backups.md#when-a-full-backup-earns-its-cost) |
| Restoring a backup, deleting a backup, 或升级Core或OS而不进行明确用户确认 | 每次都询问、命名具体效果并等待回答——备份或否 | 完整恢复会丢弃所有恢复部分自存档以来的所有更改并重启HA；Supervisor部分恢复仅覆盖选定的存档部分；删除会销毁恢复点；Core/OS升级影响很大，其恢复路径就是升级前的备份 | [backups](references/backups.md) |
| The same non-trivial Jinja expression repeated across templates | 一旦排除了原生触发器/条件和内置助手，就在 `config/custom_templates/*.jinja` 中将它们定义为宏一次，并导入它 | 当规则变化时，只需修复一次定义，而不是分散的副本 | [template-guidelines #reusable-macros](references/template-guidelines.md#reusable-macros) |
| `trigger`, `this`, `value_json` 或 `{% set %}` 变量在导入的宏内部使用 | 将其作为参数传递给宏 | 导入不会携带调用者的上下文——宏内部的变量未定义，因此渲染为空，且对其任何属性访问都会报错（HA自己的函数如 `states` 是全局的且有效） | [template-guidelines #imports-do-not-carry-the-callers-context](references/template-guidelines.md#imports-do-not-carry-the-callers-context) |

---

## 参考文件

在回答之前，读取与任务匹配的每个文件：

| 文件 | 何时读取 |
|------|----------|
| [safe-refactoring](references/safe-refactoring.md) | 重命名实体或其显示名称、替换助手、重构自动化或对现有配置的任何修改 |
| [triggers-and-conditions](references/triggers-and-conditions.md) | 编写自动化的触发器或条件：专用触发器和原生触发器/条件、`for:` 持续时间、触发器ID |
| [automation-actions](references/automation-actions.md) | 编写自动化或脚本的行动，或选择其模式：等待、变量、捕获行动响应、`continue_on_error`、脚本中的 `admin-only` 行动（`Unauthorized`）、停止序列、重复、if/then vs choose、并行；记录/注释步骤；禁用自动化 |
| [helper-selection](references/helper-selection.md) | 决定是否使用内置助手而非模板传感器——聚合、变化率、阈值、状态持续时间、计数/计时、调度、分组、概率推理、平滑、气候、域转换、决策矩阵 |
| [template-guidelines](references/template-guidelines.md) | 确认模板是否适用于用例；使用 `custom_templates` 宏在模板之间共享Jinja逻辑 |
| [yaml-only-integrations](references/yaml-only-integrations.md) | 创建或编辑没有配置流程的YAML-only集成（例如 `command_line`、基于平台的 `mqtt`、`rest`） |
| [device-control](references/device-control.md) | 编写行动、按钮/遥控器自动化或使用 `target:` |
| [scenes](references/scenes.md) | 编写或激活场景；快照/恢复模式，包括在临时更改后将设备恢复原状；快照与脚本的区别 |
| [dashboard-guide](references/dashboard-guide.md) | 设计或修改Lovelace仪表板——布局、视图类型、策略、部分、卡片、徽章、CSS样式、HACS |
| [dashboard-cards](references/dashboard-cards.md) | 查找可用卡片类型或获取特定卡片的文档 |
| [domain-docs](references/domain-docs.md) | 查找集成/域文档，或特定触发器、条件或行动的专用文档页面 |
| [examples.yaml](references/examples.yaml) | 需要组合多个最佳实践的组合示例 |
| [appdaemon](references/appdaemon.md) | AppDaemon应用：何时使用原生HA，应用结构、行动、调度、错误处理、安全重构影响 |
| [blueprint-guide](references/blueprint-guide.md) | 编写可重用蓝图：元数据 & `source_url`、输入 & 选择器、`target` vs `entity`、默认值、输入部分、`!input` 模板化、版本控制 |
| [backups](references/backups.md) | 决定操作是否需要先备份；选择完整恢复、部分恢复和回滚单个对象之间的差异；存档实际包含什么；加密密钥和紧急工具包；恢复验证；HA保护和未保护的内容；是否git配置仓库取代完整备份 |
