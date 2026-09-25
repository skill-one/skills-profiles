# 处理破坏性变更

通过 `destructiveChanges` 元数据清单与 Salesforce 组织进行元数据删除协调。运行分为三个阶段：范围界定 → 验证 → 执行，生产环境需更严格的限制措施。

## 第 1 阶段 — 范围界定

### 第 1a 步 — 收集待删除组件

询问用户（或从上下文中推断）要删除哪些组件。对每个组件捕获：
- 元数据类型（例如 `CustomObject`、`CustomField`、`ApexClass`、`Flow`、`PermissionSet`）
- API 名称（例如 `Project__c`、`Account.Status__c`、`MyController`）

### 第 1b 步 — 本地依赖扫描（尽力而为）

在生成清单前，扫描本地项目中的每个组件引用。使用 Grep 对 `force-app/` 目录进行扫描：

```bash
grep -rn "<componentApiName>" force-app/ --include='*.cls' --include='*.trigger' --include='*.xml' --include='*.js' --include='*.html'
```

如果发现引用：
- 列出这些引用给用户
- 建议先更新这些引用，或在同一破坏性部署中删除它们
- 不要静默处理 — 提示依赖风险

### 第 1c 步 — 生成 `destructiveChanges.xml`

写入 `manifest/destructiveChangesPre.xml`（用于部署前删除）或 `manifest/destructiveChangesPost.xml`（用于部署后删除）。使用标准的 Salesforce 元数据格式：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>Project__c</members>
        <members>OldThing__c</members>
        <name>CustomObject</name>
    </types>
    <types>
        <members>Account.Status__c</members>
        <name>CustomField</name>
    </types>
    <version>62.0</version>
</Package>
```

使用 `sfdx-project.json` 中的 `sourceApiVersion` 中的 API 版本。

按元数据类型分组组件（每种类型一个 `<types>` 块）。对于命名空间字段，使用 `Object.Field` 表示法。

## 第 2 阶段 — 验证

执行破坏性部署前 **必须** 验证：

```bash
sf project deploy validate \
  --pre-destructive-changes manifest/destructiveChangesPre.xml \
  --manifest manifest/package.xml \
  --target-org <alias> \
  --test-level RunLocalTests \
  --json
```

（对于部署后破坏性：使用 `--post-destructive-changes`。）

如果 `package.xml` 不存在，创建一个空的清单文件（删除-only 部署需要清单描述符）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <version>62.0</version>
</Package>
```

如果验证失败，显示错误并停止。常见失败模式：
- "无法删除：被 Apex/Flow/布局引用" → 组件仍有引用
- "无法删除：需要许可证" → 管理包或许可证依赖
- "权限不足" → 用户没有删除权限

## 第 3 阶段 — 执行

### 生产环境路径

执行前确认目标是否为生产环境。可靠的检查是门的分类器（返回 `production|sandbox|scratch|trial|devhub|unknown`）：

```bash
sf org display --target-org <alias> --json | "${CLAUDE_PLUGIN_ROOT}/scripts/sf-deploy-gate" classify
```

如果分类器返回 `production`：
1. 显示破坏性确认横幅（镜像 `platform-quick-deploy`）
2. 列出将要删除的每个组件
3. 要求明确 "是，从生产环境删除" 确认
4. 除非用户明确输入，否则拒绝 `--purge-on-delete`

`PreToolUse` 钩子 (`sf-deploy-gate destructive`) 会阻止对生产的裸破坏命令 — 向用户显示该拒绝，不要绕过它。

### 沙盒/草稿环境路径

```bash
sf project deploy start \
  --pre-destructive-changes manifest/destructiveChangesPre.xml \
  --manifest manifest/package.xml \
  --target-org <alias> \
  --json \
  --wait 30
```

只有在用户明确要求永久删除（跳过回收站）时才添加 `--purge-on-delete`。

## 第 4 阶段 — 删除后清理

成功执行破坏性部署后：
- 建议不要使用 `sf project retrieve start --metadata <Type>:<Name>`（组件已不存在） — 相反建议清理本地源：
  ```bash
  # 删除已删除的本地文件以保持源跟踪准确
  rm -rf force-app/main/default/<path-to-component>
  ```
- 如果删除带数据的自定义字段，提醒用户数据已丢失（或仍在回收站中，直到被清除）
- 建议运行测试以确认无运行时回归

## 规则

- **必须** 先验证；**绝不** 跳过第 2 阶段
- **必须** 扫描本地引用；**绝不** 盲目删除
- **必须** 用明确用户确认来限制生产环境
- **绝不** 在未明确用户请求的情况下添加 `--purge-on-delete`
- **绝不** 在破坏性部署中使用 `--ignore-errors`
- **必须** 使用 `sfdx-project.json` 中的 API 版本，而不是硬编码值
- 如果用户正在删除带 `required="true"` 或用于 `RecordType` 选择列表值的字段，在继续前显示级联影响
