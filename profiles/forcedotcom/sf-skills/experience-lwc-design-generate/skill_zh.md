<!-- adk-managed-skill -->

# 从设计创建 LWC 组件

从设计输入（Figma、PRD、Aura 源代码或用户描述）编排端到端创建新的 Lightning Web Component 的流程。这是顶层工作流技能——它按顺序调用每个阶段所属的专业子技能。组织感知数据（LDS 模式内省、设计框架检查）通过将任务交给 `experience-lds-data-requirements-generate` 或通过用户提供的设计工具 URL 来解决。

## 何时使用

- 从 Figma 框架、PRD 或书面规范构建全新的 LWC。
- 将 Aura 组件迁移到 LWC 作为全新构建（就地 Aura → LWC 迁移不在此技能的范围内）。
- 创建一个其需求部分隐含且需要在编码前提炼成 PRD 的组件。

**不要**使用此技能用于：
- 重构现有的 LWC（使用 `experience-lwc-generate`）。
- Aura → LWC 就地迁移（不在此技能的范围内）。
- 纯粹的样式或数据层工作（直接使用专业技能）。

## 前置条件

- 至少一个设计输入：Figma URL、PRD Markdown、Aura 组件源代码或文本规范。
- 新 LWC 的目标路径（模块文件夹）。
- 对于数据驱动组件：对组织的访问权限，以便 `experience-lds-data-requirements-generate` 和 `experience-lds-best-practices-apply` 可以解析模式和适配器形状。

## 知识库

- [references/prd-analysis-template.md](references/prd-analysis-template.md) — PRD 部分骨架（生成 PRD 时需原封不动地复制）。
- [references/figma-to-prd-blueprint.md](references/figma-to-prd-blueprint.md) — Figma 特定指南，用于将框架转换为 PRD 部分（componentName/tagName、contentRequirements、dataRequirements、interactions、componentCommunication、states、accessibility/responsiveness/styling/localization/security）。在第一阶段 1.2 输入为 Figma 设计时阅读此文档。

## 工作流（强制五阶段）

### 第一阶段 — 收集 PRD 和需求

**目标**：生成每个后续阶段都消费的整合 PRD。

1. **获取原始需求** — 收集 PRD、设计规范、Figma URL、Aura 源代码或用户文本。
2. **Figma → PRD**（如果适用）：遵循 [references/figma-to-prd-blueprint.md](references/figma-to-prd-blueprint.md) 进行完整的 Figma 框架分析和 PRD 部分指南。用户需要的输入：Figma URL、目标框架的截图，以及（如果 Dev Mode 可用）节点的元数据导出。使用 [references/prd-analysis-template.md](references/prd-analysis-template.md) 中的 PRD 骨架，并按照蓝图中的按部分指南进行转换。
3. **Aura → PRD**（如果迁移）：列举 Aura 组件必须保留的功能——标记、控制器/助手操作、事件、属性和有线数据——并将该清单作为显式需求输入到 PRD 中。（就地 Aura → LWC 迁移不在此范围内；此步骤仅捕获行为用于全新构建。）
4. **数据需求**（如果组件读取/写入数据）：交给 `experience-lds-data-requirements-generate`。该技能生成经过验证的数据规范（对象/字段 API 名称、推荐的 LDS API、实现方法）。将它的输出原封不动地粘贴到 PRD 中。
5. **适配器探索**：交给 `experience-lds-best-practices-apply` 进行适配器选择规则（UI API vs GraphQL vs Apex）和所选方法的推荐接线。
6. **命名**：`componentName` 必须是小驼峰式（例如，`productCard`），`tagName` 必须是其短横线式形式（例如，`product-card`）。用捆绑脚本进行验证——不要肉眼检查：

   ```bash
   "<skill_dir>/scripts/check-component-name.sh" <componentName> <tagName>
   ```

   如果任何名称格式不正确，或者 `componentName` 的短横线形式不等于 `tagName`，脚本将非零退出（并带有可操作的 stderr 消息）。

**交付物**：涵盖目的、内容、数据、交互、状态、a11y、响应式、样式方向、本地化和安全性的综合 PRD。将其检查到工作区中（例如，`packages/skills/<skill>-workspace/<iteration>/PRD.md`）。

### 第二阶段 — 生成组件代码

**目标**：初始 `.html`、`.js`、`.css`、`.js-meta.xml`，严格反映 PRD。

1. 将 PRD 内容作为规范交给 `experience-lwc-generate`。该技能拥有 PRD → 代码转换（事件、getter、`@api`、`.js-meta.xml`、AI 元数据）并是创作的权威来源。
2. 使用 `design-systems-slds-apply` 的 SLDS 决策层次结构：
   1. 优先使用匹配的 Lightning Base Component (`experience-lwc-base-components-integrate`)。
   2. 否则选择 SLDS 蓝图或实用类（根据 `design-systems-slds-apply`）。
   3. 否则使用 SLDS 样式钩子编写自定义 CSS（也在 `design-systems-slds-apply` 中涵盖）。
3. 在继续之前，通过执行 `experience-lwc-generate` 检查清单来重新确认创作基线。
4. 将每个 PRD 数据需求转换为有线适配器（UIAPI / GraphQL）或显式的 TODO。
5. 严格遵循 PRD：
   - 仅包含 PRD 描述的功能和行为。
   - 用 `// TODO:` 注释标记不确定区域，并引用 PRD 语言以引起歧义。
   - 添加详细的代码注释以解释意图。
   - 不要将组件拆分为比 PRD 暗示的更多子组件。

**交付物**：目标路径中的第一版 LWC 套件。

### 第三阶段 — 优化组件

**目标**：应用性能、可维护性和最佳实践修复。

1. 在任何其他审查之前，执行优化检查清单：
   - 单一职责、封装、可重用性。
   - 最小化 DOM 操作；通过属性分批更新。
   - 审查事件处理程序和生命周期钩子使用（`renderedCallback` 守卫）。
   - 考虑对重型子组件进行懒加载。
2. 交给 `experience-lwc-generate` 进行 LWC 最佳实践审查（反模式、反应性、组合）。
3. 交给合规套件进行预发布审查——`experience-accessibility-validate`（a11y）、`experience-lwc-security-validate`（LWS + 产品安全）和 `experience-lwc-rtl-validate`（RTL i18n）。一起运行以进行完整质量检查。
4. 如果组件涉及数据，交给 `experience-lds-best-practices-apply` 进行缓存/一致性和引用完整性检查。
5. 应用所有接受的发现。以 PRD 为源真相——不要以优化的名义增加范围。

### 第四阶段 — 代码检查、格式化、编译检查

条件：仅在项目中配置了工具的步骤运行。

1. **检测项目工具** — 从项目根目录调用捆绑的检测脚本并读取其 `<tool>=yes|no` 行。不要肉眼检查 `package.json` / dotfiles 在文本中：

   ```bash
   "<skill_dir>/scripts/detect-project-tools.sh" <projectRoot>
   ```

   示例输出：

   ```text
   eslint=yes
   prettier=yes
   cursor-rules=no
   lwc-compiler=yes
   ```

   仅对报告为 `yes` 的工具运行下面的子步骤；跳过其余部分。
2. **ESLint**（如果 `eslint=yes`）— 运行并修复所有违规。
3. **Prettier**（如果 `prettier=yes`）— 运行以保持格式一致。
4. **Cursor 规则**（如果 `cursor-rules=yes`）— 应用项目提供的每个规则。
5. **LWC 编译器**（如果 `lwc-compiler=yes`）— 通过本地开发服务器或 SFDX 运行；在继续之前解决所有语法/模板错误。

**交付物**：干净、经过验证的组件代码。

### 第五阶段 — 创建测试

交给 `experience-lwc-accessibility-jest-run` 进行自动化的可访问性 Jest 覆盖；在相同过程中添加通用 Jest 覆盖，遵循 `experience-lwc-generate` 的测试指南，如果团队需要，还生成 UTAM 页面对象。

**交付物**：带有通过测试套件的 LWC 套件，覆盖率高于或等于项目的阈值。

## 完成

只有当以下所有项目都为真时，通过此工作流构建的新组件才“完成”。将其视为权威的待办事项清单——将其复制到 PR 描述中，以便审查者可以确认每一行。

**代码完成** — 无实现差距：

1. 每个 PRD 需求要么已实现，要么用 `TODO:` 注释明确标记并链接到跟踪项。没有沉默的差距。
2. 没有 `TODO`、`FIXME` 或 `console.log` / `console.table` / `alert()` 留在生产路径中。
3. 没有注释掉的代码块，没有空的函数体，没有占位符值，没有虚拟数据，没有未引用的导入。
4. 没有 `lwc:dom="manual"` 区域或第三方库的逃生通道，没有解释为什么未使用原生 LWC 模式。

**合规性和质量**：

5. `.js-meta.xml` AI 元数据通过 `experience-lwc-generate` 的审计（组件范围的 `<ai><description>` 设置，以及为每个通过 `<targetConfig>` 暴露的 `@api` 成员添加的 `<ai><property name="…" aiDescription="…"/></ai>` 条目；没有营销语言）。
6. SLDS 样式通过 `design-systems-slds-apply` 验证——没有原始十六进制/像素值，只有样式钩子和 SLDS 实用类。
7. 可访问性通过完成：`experience-accessibility-validate` 源代码审查 + `experience-lwc-accessibility-jest-run` 自动化测试，两者均为绿色。
8. 安全 + RTL 通过完成：`experience-lwc-security-validate` + `experience-lwc-rtl-validate`，两者均为绿色。

**数据 + 测试**：

9. 数据层与参考的 LDS 适配器验证（PRD 的数据部分中记录的每个有线/命令式调用都匹配 `experience-lds-best-practices-apply` 或 `experience-lds-data-requirements-generate` 中的一个适配器）。
10. Jest 测试达到项目要求的覆盖率水平。新测试覆盖每个 `@api` 表面、每个派发的事件和每个错误路径（失败的线、失败的上司、验证拒绝）。
11. 为需要跨组件浏览器级测试的任何 UI 流生成 UTAM 页面对象（如果不需要则跳过）。

## 交叉引用

- 此工作流按阶段顺序链式连接的技能：
  - `experience-lds-data-requirements-generate` — 第一阶段 1.4 数据规范（以及与 `experience-lds-best-practices-apply` 一起进行的阶段 1.5 适配器探索）。
  - `design-systems-slds-apply`、`experience-lwc-base-components-integrate` — 第二阶段样式决策。
  - `experience-lwc-generate` — 第二阶段创作基线 + 第三阶段最佳实践审查 + 第五阶段 AI 元数据审计。
  - `experience-lds-best-practices-apply` — 第二阶段/第三阶段数据层适配器选择和一致性审查。
  - `experience-accessibility-validate`、`experience-lwc-security-validate`、`experience-lwc-rtl-validate` — 第三阶段 a11y/安全/RTL 审查。
  - `experience-lwc-accessibility-jest-run` — 第五阶段自动化 a11y 测试生成。
  - 可选：组件稳定后，作为单独的步骤添加 o11y 仪器。
  - `experience-lwc-typescript-migrate` — JS 变绿后可选。
  - 新组件在启用标志后发布时，在发布期间使用功能标志进行门控。
  - 一旦公共 API 稳定，生成 API 表面文档（目前还没有专门的技能为此）。
- 此工作流使用的组织感知输入：
  - Figma URL + 截图（如果可用，则开发者 Dev Mode 元数据导出）——第一阶段 1.2 Figma 输入。
  - `experience-lds-data-requirements-generate` 拥有在组件需要组织支持数据时在第一阶段使用的 org-schema 内省和数据规范验证——将其交给该技能，而不是在此重复其工作。

## 示例

**第一阶段 PRD 骨架（从 Figma/PRD/Aura 输入填充）**

```text
组件：productCard (<product-card>)
目的：渲染产品紧凑摘要，带快速操作。

内容需求
- 英雄图像 (Product.HeroImage__c)
- 标题 (Product.Name)
- 副标题 (Product.Tagline__c)
- 主要 CTA 按钮 ("添加到购物车")
- 次要 CTA 图标按钮 ("收藏")

数据需求
- 输入：@api recordId (产品 Id)
- 适配器：getRecord (UIAPI) 带字段 Name、Tagline__c、HeroImage__c
- 事件输出：addtocart{detail.recordId}, favorite{detail.recordId, detail.value}

状态
- 加载（数据尚未解析）
- 错误（适配器错误）
- 空白（未找到记录）
- 默认

可访问性
- 标题使用 <h3>
- 仅图标的按钮带有 aria-label="Favorite"
- 卡片是标记区域（role="group", aria-labelledby）

响应式
- 宽度 < 480px 全宽
- >= 480px 图像 + 文本并排

样式
- 使用 lightning-card 包装器
- 表面颜色：--slds-g-color-surface-container-1
- 阴影：--slds-g-shadow-1
```

**第二阶段骨架**

```javascript
import { LightningElement, api, wire } from 'lwc';
import { getRecord } from 'lightning/uiRecordApi';
import NAME from '@salesforce/schema/Product__c.Name';
import TAGLINE from '@salesforce/schema/Product__c.Tagline__c';
import HERO from '@salesforce/schema/Product__c.HeroImage__c';

const FIELDS = [NAME, TAGLINE, HERO];

export default class ProductCard extends LightningElement {
    @api recordId;

    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    record;

    get hasRecord() { return this.record?.data != null; }
    get isLoading() { return !this.record; }
    get hasError()  { return !!this.record?.error; }
    get name()      { return this.record?.data?.fields?.Name?.value ?? ''; }
    get tagline()   { return this.record?.data?.fields?.Tagline__c?.value ?? ''; }
    get heroUrl()   { return this.record?.data?.fields?.HeroImage__c?.value ?? ''; }

    handleAddToCart() {
        this.dispatchEvent(new CustomEvent('addtocart', { detail: { recordId: this.recordId }, bubbles: true, composed: true }));
    }
    handleFavorite(event) {
        this.dispatchEvent(new CustomEvent('favorite', { detail: { recordId: this.recordId, value: event.detail.value }, bubbles: true, composed: true }));
    }
}
```

## 验证

- 每个 PRD 部分至少可追溯到一段代码或一个显式的 TODO。
- 执行了阶段 1–5，按顺序执行；没有跳过任何步骤。
- 可访问性、SLDS、数据层和 AI 元数据审查均通过。
- 覆盖率符合或超过项目的阈值。
- 组件在 `experience-lwc-runtime-observe` 中正确渲染，覆盖 PRD 中列出的响应式断点。
