# Home Assistant 最佳实践

**核心原则**：尽可能使用 Home Assistant 的原生构造。模板会绕过验证，在运行时静默失败，并使调试变得不透明。

## 决策工作流

创建任何自动化时，请遵循以下顺序：

### 0. 门控：修改现有配置？

如果你的更改会影响实体 ID、显示名称或跨组件引用——重命名实体或设备、用辅助工具替换模板传感器、转换设备触发器或重构自动化——请先阅读 [safe-refactoring](references/safe-refactoring.md)。该参考涵盖了影响分析、设备兄弟发现、显示名称覆盖和变更后验证。在继续之前，请完成其工作流。

以下 1-5 步适用于新配置或模式评估。

### 1. 检查是否有特定用途的，然后是通用原生的触发器/条件
自 2026.7 版本起，默认构建块是特定用途的触发器/条件——`<domain>.<name>` 键（检测到运动、电量低、门已打开）并具有区域/楼层/标签目标。首先检查是否有匹配意图的特定用途触发器/条件，然后是通用原生触发器/条件，最后才是模板。参见 [automation-patterns #purpose-specific-triggers--conditions-default-since-20267](references/automation-patterns.md#purpose-specific-triggers--conditions-default-since-20267)。

**常见替换：**
- 触发器中列出单个传感器实体 → 一个具有区域/楼层/标签 `target:` 的特定用途触发器
- `{{ states('x') | float > 25 }}` → `numeric_state` 条件，`above: 25`
- `{{ is_state('x', 'on') and is_state('y', 'on') }}` → 使用状态条件的 `condition: and`
- `{{ now().hour >= 9 }}` → `condition: time`，`after: "09:00:00"`
- `wait_template: "{{ is_state(...) }}"` → 使用状态触发器的 `wait_for_trigger`（注意：当状态已为真时行为不同——参见 [safe-refactoring #trigger-restructuring](references/safe-refactoring.md#trigger-restructuring)）

### 2. 检查是否有内置辅助工具或 Template Helper
在创建模板传感器之前，请检查 [helper-selection](references/helper-selection.md)。

**常见替换：**
- 汇总/平均多个传感器 → `min_max` 集成
- 二进制任一开/全部开逻辑 → `group` 辅助工具
- 变化速率 → `derivative` 集成
- 跨阈值检测 → `threshold` 集成
- 消费跟踪 → `utility_meter` 辅助工具

**如果没有内置辅助工具适用，请使用 Template Helper，而不是 YAML。**
通过 HA 配置流程创建（编程方式或 UI 中：
设置 → 设备与服务 → 辅助工具 → 创建辅助工具 → 模板）。通过流程创建的辅助工具是 UI 可编辑的；`template:` YAML 条目需要 `template.reload`，且不可编辑。

当用户要求时、当两种路径都不适用时，或当配置需要流程没有的字段时（如基于触发器的模板和 `attributes:`）写入 `template:` YAML。然后使用受管理的 YAML 编辑（[yaml-only-integrations](references/yaml-only-integrations.md)），而不是手动编辑。

### 3. 选择正确的自动化模式
默认 `single` 模式通常不正确。参见 [automation-patterns #automation-modes](references/automation-patterns.md#automation-modes)。

| 情景 | 模式 |
|----------|------|
| 带超时的运动灯 | `restart` |
| 顺序处理（门锁） | `queued` |
| 每个实体独立操作 | `parallel` |
| 单次通知 | `single` |

### 4. 使用 entity_id 而不是 device_id
`device_id` 在设备重新添加时会失效。参见 [device-control](references/device-control.md)。

**例外：** Zigbee2MQTT 自动发现的设备触发器是可接受的。

### 5. 对于按钮和遥控器
- **任何暴露 `event.*` 实体的集成：** 使用 `event.received` 针对该实体——一个普通实体，因此可以重命名，并在集成保持稳定唯一 ID 时重新添加时存活
- **ZHA：** 没有事件实体——使用 `event` 触发器，`device_ieee`（持久）
- **Z2M：** 事件实体是实验性的，默认关闭——使用 `device` 触发器（自动发现）或 `mqtt` 触发器

参见 [device-control #buttonremote-patterns](references/device-control.md#buttonremote-patterns)。

---

## 严重反模式

| 反模式 | 使用替代方案 | 原因 | 参考 |
|--------------|-------------|-----|-----------|
| `condition: template` with `float > 25` | `condition: numeric_state` | 在加载时验证，而不是运行时 | [automation-patterns #native-conditions](references/automation-patterns.md#native-conditions) |
| `wait_template: "{{ is_state(...) }}"` | `wait_for_trigger` with state trigger | 事件驱动，不是轮询；等待 *变更*（参见 [safe-refactoring #trigger-restructuring](references/safe-refactoring.md#trigger-restructuring) 的语义差异） | [automation-patterns #wait-actions](references/automation-patterns.md#wait-actions) |
| `device_id` in triggers | `entity_id`（或 `device_ieee` for ZHA） | device_id 在重新添加时失效 | [device-control #entity-id-vs-device-id](references/device-control.md#entity-id-vs-device-id) |
| `numeric_state` 触发器驱动高成本操作，无保护 | 在 `trigger.from_state` 中使用拒绝 `unavailable`/`unknown` 的条件 | 重启或闪烁会重新触发，因此未变更的值会触发而没有跨越（保护也会丢弃真实跨越） | [automation-patterns #unavailable-arms-a-numeric-state-trigger](references/automation-patterns.md#unavailable-arms-a-numeric-state-trigger) |
| `mode: single` for motion lights | `mode: restart` | 重新触发必须重置计时器 | [automation-patterns #automation-modes](references/automation-patterns.md#automation-modes) |
| `enabled: false` 作为 `automations.yaml` 顶层键 | `automation.turn_off`（临时）或实体注册表禁用（永久） | 不是一个有效的顶层键——在模式验证期间被拒绝；自动化加载为 `unavailable` | [automation-patterns #disabling-automations](references/automation-patterns.md#disabling-automations) |
| 模板传感器用于求和/平均值 | `min_max` 辅助工具 | 声明式，处理不可用状态 | [helper-selection #numeric-aggregation](references/helper-selection.md#numeric-aggregation) |
| 模板二进制传感器带阈值 | `threshold` 辅助工具 | 内置迟滞支持 | [helper-selection #threshold](references/helper-selection.md#threshold) |
| 未进行影响分析就重命名实体 ID | 遵循 [safe-refactoring](references/safe-refactoring.md) 工作流 | 重命名会破坏仪表板、脚本、场景、Config-Entry 数据和存储仪表板，且静默失效 | [safe-refactoring #entity-renames](references/safe-refactoring.md#entity-renames) |
| 未更新成员就重命名 Config-Entry 基于的组（UI 组） | 通过选项流程在注册表重命名后更新组成员 | 实体注册表重命名不会更新 Config Entry 中的 `options.entities`——组会静默失效 | [safe-refactoring #config-entry-groups](references/safe-refactoring.md#config-entry-groups) |
| 未修补 Config-Entry 数据就重命名 Config-Entry 集成使用的实体（Better/Generic Thermostat、Min/Max、Threshold） | 扫描并修补 `core.config_entries` `data`+`options` 字段 | 这些集成将实体 ID 存储在 Config Entry 中——实体注册表重命名不会更新 | [safe-refactoring #config-entry-data--blind-spots-for-entity-registry-renames](references/safe-refactoring.md#config-entry-data--blind-spots-for-entity-registry-renames) |
| YAML 中的 `template:` 传感器/二进制传感器 | 通过配置流程的 Template Helper | 流程创建的辅助工具原地重新加载并保持 UI 可编辑；`template:` 条目需要配置重新加载且不可编辑。例外情况真实——基于触发器的模板和 `attributes:` 没有流程字段 | [helper-selection #template-helpers](references/helper-selection.md#template-helpers) |
| 直接编辑 `.storage/` 文件或其他 HA 内部状态 | 使用 HA REST/WebSocket API 管理状态和配置条目 | `.storage/` 文件是 HA 的内部状态数据库；直接编辑会绕过验证、风险损坏，并可能被 HA 静默覆盖 | — |
| 手动将原始 YAML 写入 `configuration.yaml`（仅限 YAML 集成） | 使用受管理的 YAML 配置编辑，带备份和验证 | 未管理写入有语法错误风险、没有备份、跳过 `check_config`——受管理编辑提供所有这些 | [yaml-only-integrations](references/yaml-only-integrations.md) |
| 为自动化/脚本/场景生成 YAML 片段 | 使用 HA 配置 API 以编程方式创建自动化/脚本 | API 调用验证配置，避免语法错误，且不需要手动文件编辑或重启 | [automation-patterns](references/automation-patterns.md), [examples.yaml](references/examples.yaml) |
| 告知用户编辑 `configuration.yaml`（集成） | 直接将用户引导至 HA UI 的设置 > 设备与服务 | 大多数集成是 UI 配置的；YAML 集成配置是罕见的且特定于集成的 | — |
| 提及 HA "add-ons" | 使用术语 "Apps" | HA 在 2026.2 中将 add-ons 重命名为 Apps——"Apps 是在 Home Assistant 旁边运行的独立应用程序" | — |
| `vacuum.send_command` 使用供应商房间 ID | `vacuum.clean_area` 使用 HA `area_id`（如果段已映射） | 使用原生 HA 区域，跨集成工作——但需要先在实体设置中进行段到区域的映射 | [device-control #vacuum-control](references/device-control.md#vacuum-control) |
| 在灯操作中使用 `color_temp`（mireds） | 使用 `color_temp_kelvin` | `color_temp` 参数在 2026.3 中已移除；仅支持开尔文 | [device-control #lights](references/device-control.md#lights) |
| Person/Device Tracker `entered_home`/`left_home` 设备触发器或 `is_home`/`is_not_home` 条件 | `state` 触发器 `to: home` / `to: not_home`，或 `state` 条件 | 这些在 2026.5 中已移除——状态触发器和条件是正确的替代方案 | [automation-patterns #presence-and-person-triggers-and-conditions-removed-in-20265](references/automation-patterns.md#presence-and-person-triggers-and-conditions-removed-in-20265) |
| 触发器中的实体列表，其中区域/楼层/标签目标适用 | 具有区域目标的特定用途触发器 `target: {area_id: ...}` | 自动化随设备变化遵循区域成员资格——没有陈旧的实体列表 | [automation-patterns #purpose-specific-triggers--conditions-default-since-20267](references/automation-patterns.md#purpose-specific-triggers--conditions-default-since-20267) |
| 旧的特定用途键（`battery.low`、`vacuum.docked`、`timer.time_remaining`、...）或触发器 `behavior: any`/`last` | 2026.7 重命名的键（`battery.became_low`、...）和 `behavior: each`/`all` | 旧键不再加载；旧行为值引发修复问题并面临移除 | [automation-patterns #purpose-specific-triggers--conditions-default-since-20267](references/automation-patterns.md#purpose-specific-triggers--conditions-default-since-20267) |
| AppDaemon：`__init__` 中的回调、未取消的 `run_in` 定时器、实例变量中的状态、硬编码的实体 ID | 在 `initialize()` 中注册，取消再重新调度前，通过 `input_*` 辅助工具持久化，通过 `self.args` 传递 ID | 每个都会静默失效、在重新加载时重置或阻止重用 | [appdaemon #appdaemon-specific-anti-patterns](references/appdaemon.md#appdaemon-specific-anti-patterns) |
| Blueprints：硬编码实体、选择器位置的自由文本、模板中的 `!input`、缺少 `source_url` | 带有类型 `!input` 的选择器；在模板之前将输入绑定到 `variables:`；始终设置 `source_url` | 硬编码会破坏重用，文本允许拼写错误，而 `!input` 是 YAML 标签而不是模板值 | [blueprint-guide #common-pitfalls](references/blueprint-guide.md#common-pitfalls) |
| 备份：完整恢复以撤销单个对象编辑、在不可逆操作（注册表删除、集成移除、Core/OS 升级）之前没有备份、调用操作为“可逆”而不命名其逆操作 | 单个对象回滚；在之前备份；命名精确的逆操作或视为不可逆 | 完整恢复会撤销自以来的所有无关更改并重启 HA；之后的备份会捕获损坏 | [backups #when-a-full-backup-earns-its-cost](references/backups.md#when-a-full-backup-earns-its-cost) |
| 恢复备份、删除备份或升级 Core 或 OS 而没有明确的用户确认 | 每次都询问、命名具体效果并等待答案——备份或否 | 完整恢复会丢弃所有恢复部分自存档以来的更改并重启 HA；Supervisor 部分恢复仅覆盖选定的存档部分；删除会销毁恢复点；Core/OS 升级影响很大，其恢复路径就是升级前的备份 | [backups](references/backups.md) |
| 在模板中重复的非平凡 Jinja 表达式 | 在原生触发器/条件和内置辅助工具被排除后，在 `config/custom_templates/*.jinja` 中定义一次为宏，并导入它 | 当规则更改时，只需修复一次定义，而不是逐渐分化的副本 | [template-guidelines #reusable-macros](references/template-guidelines.md#reusable-macros) |
| 在导入的宏中使用 `trigger`、`this`、`value_json` 或 `{% set %}` 变量 | 将其作为参数传递给宏 | 导入不会携带调用者的上下文——宏中的变量未定义，因此渲染为空，且对其任何属性访问都会出错（HA 自身的函数如 `states` 是全局的并有效） | [template-guidelines #imports-do-not-carry-the-callers-context](references/template-guidelines.md#imports-do-not-carry-the-callers-context) |

---

## 参考文件

当你需要详细信息时，请阅读这些文件：

| 文件 | 何时阅读 |
|------|--------------|
| [safe-refactoring](references/safe-refactoring.md) | 重命名实体或其显示名称、替换辅助工具、重构自动化或任何现有配置的修改 |
| [automation-patterns](references/automation-patterns.md) | 编写触发器、条件、等待、变量或选择自动化模式；捕获操作响应；记录/注释步骤；禁用自动化；`continue_on_error`、管理员仅操作（`Unauthorized`）在脚本中、停止序列、重复、if/then vs choose、并行、触发器 ID |
| [helper-selection](references/helper-selection.md) | 决定是否使用内置辅助工具还是模板传感器——聚合、变化速率、阈值、时间在状态、计数/计时、调度、分组、概率推理、平滑、气候、域转换、决策矩阵 |
| [template-guidelines](references/template-guidelines.md) | 确认模板是否适用于用例；使用 `custom_templates` 宏在模板之间共享 Jinja 逻辑 |
| [yaml-only-integrations](references/yaml-only-integrations.md) | 创建或编辑没有配置流程的 YAML 仅集成（例如 `command_line`、基于平台的 `mqtt`、`rest`） |
| [device-control](references/device-control.md) | 编写操作、按钮/遥控器自动化或使用 `target:` |
| [scenes](references/scenes.md) | 编写或激活场景；快照/恢复模式；快照与脚本的区别 |
| [dashboard-guide](references/dashboard-guide.md) | 设计或修改 Lovelace 仪表板——布局、视图类型、策略、部分、卡片、徽章、CSS 样式、HACS |
| [dashboard-cards](references/dashboard-cards.md) | 查找可用卡片类型或获取特定卡片的文档 |
| [domain-docs](references/domain-docs.md) | 查找集成/域文档，或特定触发器、条件或操作的专用文档页面 |
| [examples.yaml](references/examples.yaml) | 需要组合多个最佳实践的复合示例 |
| [appdaemon](references/appdaemon.md) | AppDaemon 应用：何时使用 vs. 原生 HA，应用结构、操作、调度、错误处理、安全重构影响 |
| [blueprint-guide](references/blueprint-guide.md) | 编写可重用蓝图：元数据 & `source_url`，输入 & 选择器，`target` vs `entity`，默认值，输入部分，`!input` 模板化，版本控制 |
| [backups](references/backups.md) | 决定操作是否需要先备份；选择完整恢复、部分恢复和回滚单个对象之间的差异；存档实际包含什么；加密密钥和紧急工具包；恢复验证；HA 在删除备份时保护和不保护的方面；是否 git 配置仓库取代了完整备份 |
