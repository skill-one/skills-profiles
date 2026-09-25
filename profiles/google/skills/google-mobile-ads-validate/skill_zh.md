# 验证 Google 移动广告 SDK 集成

验证一个项目的 Google 移动广告 (GMA) SDK 集成，可以作为一个完整的审计，也可以针对特定的请求检查。

-   **完整审计**：如果用户请求一般验证或完整审计，则评估所有清单项目。
-   **特定检查**：如果用户要求仅验证特定区域（例如，广告预加载），则仅评估相关检查项，而无需运行整个清单。

## 评分规则

对于每个检查项，应用以下状态之一：

-   **通过**：未满足警告、失败或 N/A 的任何标准。
-   **警告**、**失败** 或 **N/A**：满足每个相应状态下描述的条件。

## 验证清单

阅读要执行的每个检查项的参考指南：

-   项目中没有测试应用 ID，格式正确：`references/application-id.md`
-   项目中没有测试广告单元，格式正确：`references/ad-units.md`
-   已实现所有 Google SKAdNetwork ID：`references/google-skadnetwork-ids.md`
-   中介适配器兼容性：`references/mediation-adapter-compatibility.md`
-   广告预加载验证检查：`references/ad-preloading.md`

## 最终输出

生成以下格式的 Markdown 报告。**仅**包含实际检查项的结果。

| 检查项 | 状态 | 结果 | 下一步 |
| :--- | :---: | :--- | :--- |
| 项目中没有测试应用 ID，格式正确 | {{status_1}} | {{findings_1}} | {{next_steps_1}} |
| 项目中没有测试广告单元，格式正确 | {{status_2}} | {{findings_2}} | {{next_steps_2}} |
| 已实现所有 Google SKAdNetwork ID | {{status_3}} | {{findings_3}} | {{next_steps_3}} |
| 中介适配器兼容性 | {{status_4}} | {{findings_4}} | {{next_steps_4}} |
| 广告预加载验证检查 | {{status_5}} | {{findings_5}} | {{next_steps_5}} |
