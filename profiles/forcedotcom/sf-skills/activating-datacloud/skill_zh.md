# activating-datacloud：数据云激活阶段

当用户需要**下游交付工作**时（如激活、激活目标、数据操作或将数据云输出推送到其他系统），请使用此技能。

## 此技能负责任务的情况

当工作涉及以下内容时，请使用 `activating-datacloud`：
- `sf data360 activation *`
- `sf data360 activation-target *`
- `sf data360 data-action *`
- `sf data360 data-action-target *`
- 验证下游交付设置

当用户处于以下情况时，请将其委托给其他技能：
- 仍在构建受众或洞察 → [segmenting-datacloud](../segmenting-datacloud/SKILL.md)
- 探索查询/搜索或搜索索引 → [retrieving-datacloud](../retrieving-datacloud/SKILL.md)
- 设置基础连接或摄取 → [connecting-datacloud](../connecting-datacloud/SKILL.md), [preparing-datacloud](../preparing-datacloud/SKILL.md)

---

## 首先收集所需的上下文

询问或推断：
- 目标组织别名
- 目标平台或下游系统
- 段是否已存在并发布
- 用户是否需要创建、检查、更新或删除
- 任务是侧重激活还是侧重数据操作

---

## 核心操作规则

- 在创建下游交付资产之前，验证上游段或洞察是否健康。
- 在修改激活资产之前，运行共享就绪分类器：`node ../orchestrating-datacloud/scripts/diagnose-org.mjs -o <org> --phase act --json`。
- 在修改激活设置之前，检查可用的平台和目标。
- 尽可能使目标定义确定性和可重用。
- 将下游凭证和平台约束视为单独的验证问题。
- 当目标状态不明确时，优先进行只读检查。

---

## 推荐的工作流程

### 1. 对激活工作分类就绪情况
```bash
node ../orchestrating-datacloud/scripts/diagnose-org.mjs -o <org> --phase act --json
```

### 2. 首先检查目标
```bash
sf data360 activation platforms -o <org> 2>/dev/null
sf data360 activation-target list -o <org> 2>/dev/null
sf data360 data-action-target list -o <org> 2>/dev/null
```

### 3. 在激活之前创建目标
```bash
sf data360 activation-target create -o <org> -f target.json 2>/dev/null
sf data360 data-action-target create -o <org> -f target.json 2>/dev/null
```

### 4. 创建激活或数据操作
```bash
sf data360 activation create -o <org> -f activation.json 2>/dev/null
sf data360 data-action create -o <org> -f action.json 2>/dev/null
```

### 5. 验证下游就绪情况
```bash
sf data360 activation list -o <org> 2>/dev/null
sf data360 activation data -o <org> --name <activation> 2>/dev/null
```

---

## 高信号注意事项

- 激活设计依赖于健康的已发布上游段。
- 目标配置通常在激活创建之前。
- 下游凭证和平台约束可能仅存在于数据云CLI之外。
- 当目标设置不明确时，只读检查是最安全的初始步骤。
- `CdpActivationTarget` 或 `CdpActivationExternalPlatform` 表示当前组织/用户被限制激活表面；引导用户进行激活设置、权限和目标配置，而不是盲目重试。

---

## 输出格式

```text
激活任务： <激活 / 激活目标 / 数据操作 / 数据操作目标>
目标： <平台或目标>
目标组织： <别名>
工件： <定义文件 / 命令>
验证： <列出 / 创建 / 阻止>
下一步： <目标验证或下游测试>
```

---

## 参考

- [README.md](README.md)
- [../orchestrating-datacloud/assets/definitions/activation-target.template.json](../orchestrating-datacloud/assets/definitions/activation-target.template.json)
- [../orchestrating-datacloud/assets/definitions/activation.template.json](../orchestrating-datacloud/assets/definitions/activation.template.json)
- [../orchestrating-datacloud/assets/definitions/data-action-target.template.json](../orchestrating-datacloud/assets/definitions/data-action-target.template.json)
- [../orchestrating-datacloud/assets/definitions/data-action.template.json](../orchestrating-datacloud/assets/definitions/data-action.template.json)
- [../orchestrating-datacloud/UPSTREAM.md](../orchestrating-datacloud/UPSTREAM.md)
- [../orchestrating-datacloud/references/plugin-setup.md](../orchestrating-datacloud/references/plugin-setup.md)
- [../orchestrating-datacloud/references/feature-readiness.md](../orchestrating-datacloud/references/feature-readiness.md)
