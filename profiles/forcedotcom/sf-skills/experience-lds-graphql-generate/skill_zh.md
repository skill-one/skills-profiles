<!-- adk-managed-skill -->

# 构建LDS GraphQL

生成经过模式验证的Salesforce LDS GraphQL查询（读取或变更），可以是独立的查询，也可以通过`lightning/graphql`适配器连接到Lightning Web Component中。该技能端到端地编码了以模式为真实来源的工作流程。两个捆绑的bash脚本处理与组织相关的步骤——`scripts/fetch-lds-graphql-schema.sh`用于模式内省，`scripts/test-lds-graphql-query.sh`用于实时组织的验证。

## 使用场景

- 用户想要创建、修改或集成Salesforce GraphQL查询（标准对象、自定义对象或设置对象）。
- 构建或更新一个通过GraphQL消耗/变更LDS数据的LWC。
- 在编写查询之前内省组织的模式。
- 对连接的组织进行端到端验证生成的查询。

**不要**使用此技能：
- 基于REST的UI API（使用LDS线适配器；参见`experience-lds-best-practices-apply`）。
- Apex调用或自定义GraphQL端点——此技能仅限于LDS范围。
- 数据需求发现——那是`experience-lds-data-requirements-generate`。

## 前提条件

- 一个连接的Salesforce组织（用户名或别名）。用户必须在模式获取之前确认它——永远不要假设。
- 在shell中可用Salesforce CLI / `sf`，用于模式获取。
- 关于以下方面的决定：
  - **命名空间**——`uiapi`（默认：标准对象+自定义对象）或`setup`（设置对象，如权限集、配置文件）。
  - **查询类型**——`read`（默认）或`mutation`。
  - **输出格式**——`standalone`（原始GraphQL+变量）或`LWC集成`（完整组件连接）。

## 核心规则

这些适用于每个步骤——它们是此技能强制执行的规则：

1. **顺序执行**——步骤1→6按顺序运行。除非触发条件未满足，否则每个步骤都是强制性的。
2. **失败时硬停止**——一个失败的步骤会阻止后续步骤，直到修复完成。
3. **模式是单一真实来源**——每个实体名称、字段名称、字段类型和关系都必须来自`schema.graphql`内省。永远不要使用常见的Salesforce知识（例如，不要假设`Owner`是一个`User`——它可能是多态的）。
4. **报告每个步骤**——在使用提供的模板前进之前。
5. **错误报告**——分类错误；永远不要将原始工具输出回显到聊天中。

## 工作流程

完整规范工作流程位于[references/generation-guide.md](references/generation-guide.md)。开始之前阅读它。读取查询的具体内容在[references/generation-query.md](references/generation-query.md)；变更的具体内容在[references/generation-mutation.md](references/generation-mutation.md)。

### 步骤1 — 通用查询信息

收集并回显：

```text
查询类型:       [read | mutation]
命名空间:        [uiapi | setup]
输出格式:    [standalone | LWC集成]
```

如果任何项不明确，问一次并等待。

### 步骤2 — 获取模式

1. 请求`usernameOrAlias`。如果从上下文中推断出默认值，请呈现它并等待明确确认。
2. 运行`scripts/fetch-lds-graphql-schema.sh USERNAME_OR_ALIAS [OUTPUT_PATH] [API_VERSION]`，使用确认的别名。脚本将SDL写入`schema.graphql`（或您传递的路径），因此模式永远不会进入聊天上下文中。如果`OUTPUT_PATH`在`schema.graphql`中已经存在非空`schema.graphql`，脚本将提前退出（设置`LDS_FETCH_FORCE=1`以重新获取）。
3. 失败时：**硬停止**，报告类别，要求用户解决组织访问权限，然后重试。

#### 使用模式文件

模式有265,000多行。**永远**不要读取整个文件——仅使用有针对性的`grep`调用。

- 对象类型：`^type <ObjectName> implements Record`与`-A 100`。
- 过滤器：`^input <ObjectName>_Filter`与`-A 50`。
- 排序：`^input <ObjectName>_OrderBy`与`-A 30`。
- 变更输入：`^input <ObjectName>(Create|Update)Input`与`-A 50`。

**搜索预算**：每个实体最多4-5个`grep`调用。执行前计划。

### 步骤3 — 实体识别

1. 实体名称是大写驼峰式。
2. 如果名称未给出，从`^type <Name> implements Record`匹配中提取候选者。
3. 如果任何实体仍然未解决，请询问用户并等待。
4. 报告：
   ```text
   识别的实体：
   - EntityName (Field1, Field2, ...)
   未识别的实体：
   - <文本名称>
   步骤3状态：SUCCESS | FAILED
   ```
5. 如果`未识别的实体`非空 → 状态`FAILED` → 请求澄清 → 重新开始步骤3。

### 步骤4 — 迭代实体内省

迭代限制：**3个周期**（主实体→引用→子关系）。3次后硬停止。

每个周期：

1. 从列表中移除已内省的实体。
2. 使用上述模式模式对剩余实体的字段进行`grep`。
3. 提取标准字段类型。
4. 识别**引用字段**（`Owner: User`）。不同实体上的同名字段可能有不同类型——独立检查每个实体。如果字段解析为多个实体类型，将其标记为**多态**，并计划使用内联片段（`... on TypeA`，`... on TypeB`）。
5. 识别**子关系**（连接类型，例如，`Contacts: ContactConnection`）。将新实体添加到未知列表。
6. 如果未知列表不为空且迭代次数<3，则循环。
7. 报告：
   ```text
   [PASS|FAIL] EntityName
     - 标准字段：FieldName (type), ...
     - 引用字段：FieldName → TargetType, ...
     - 多态字段：FieldName → [TypeA, TypeB], ...
     - 子关系：RelationshipName → ChildType, ...
     - 未知字段：FieldName, ...
   内省周期使用：N/3
   步骤4状态：SUCCESS | FAILED
   ```
8. 如果任何实体是`[FAIL]` → 全局`FAILED` → 修复 → 从周期开始恢复。

### 步骤5 — 读取查询生成（仅当查询类型为`read`时）

根据[references/generation-query.md](references/generation-query.md)编写读取查询，输入内省数据、实体列表、字段类型、输出格式和`usernameOrAlias`。

应用[references/generation-query.md](references/generation-query.md)中的规则——涵盖：
- 查询根/命名空间选择（`uiapi.query` vs `setup.query`）。
- 字段选择纪律（仅请求实际需要的字段——每个字段都是计费的扫描）。
- 过滤运算符（`eq`，`ne`，`in`，`nin`，`gt`，`gte`，`lt`，`lte`，`like`，`contains`）。
- 排序（按字段方向）。
- 分页（`first`，`after`，`last`，`before`；`edges.node`，`pageInfo`）。
- 多态内联片段。
- 别名和变量占位符。
- 独立输出 vs LWC输出（来自`lightning/graphql`的线适配器，`gql`标记模板，`refreshGraphQL`用于命令式刷新）。

如果工具返回错误，分类错误并询问用户如何继续。

### 步骤6 — 变更查询生成（仅当查询类型为`mutation`时）

根据[references/generation-mutation.md](references/generation-mutation.md)编写变更——涵盖：
- `create`，`update`，`delete`操作形状。
- 输入类型（`<Entity>CreateInput`，`<Entity>UpdateInput`）通过`input``grep`模式发现。
- 必填字段 vs 可选字段（来自模式的`!`注释）。
- 使用`Id`仅更新引用字段。
- 返回选择——变更后读取的内容以驱动缓存一致性。
- 错误处理（`record.errors[]`）。
- LWC集成：通过`graphqlMutate`从`lightning/graphql`进行命令式变更。

### 步骤7 — 测试查询

运行`scripts/test-lds-graphql-query.sh USERNAME_OR_ALIAS 'QUERY' '<VARIABLES_JSON>'`，针对确认的`usernameOrAlias`并呈现响应形状/样本给用户。错误被分类，而不是直接回显。

## 交叉引用

- 捆绑脚本：
  - `scripts/fetch-lds-graphql-schema.sh` — 通过对组织的`/services/data/vX/graphql`端点的GraphQL内省查询获取模式（LDS不暴露`/graphql/sdl`路由）；在查询编写前对每个组织/会话调用一次。
  - `scripts/test-lds-graphql-query.sh` — 对生成的查询进行基于组织的验证，针对`/services/data/vX/graphql`。
- 相关技能：
  - `experience-lds-best-practices-apply` — 通用LDS原则、缓存语义和线vs命令式选择。
  - `experience-lds-data-requirements-generate` — 在此技能决定*如何*之前决定*什么*要查询的预工作。
  - `experience-lwc-generate` — 干净地托管生成的线适配器。

## 示例

**独立读取——最小**

```graphql
query Accounts($limit: Int = 10) {
  uiapi {
    query {
      Account(first: $limit) {
        edges {
          node {
            Id
            Name { value }
          }
        }
      }
    }
  }
}
```

**LWC集成——读取带线**

```javascript
import { LightningElement, wire } from 'lwc';
import { gql, graphql } from 'lightning/graphql';

export default class AccountList extends LightningElement {
    @wire(graphql, {
        query: gql`
            query Accounts($limit: Int = 10) {
                uiapi {
                    query {
                        Account(first: $limit) {
                            edges { node { Id Name { value } } }
                        }
                    }
                }
            }
        `,
        variables: '$variables'
    })
    accounts;

    variables = { limit: 10 };

    get records() {
        return this.accounts?.data?.uiapi?.query?.Account?.edges ?? [];
    }
}
```

## 验证

- 在步骤4之前`Step 3 status: SUCCESS`；在步骤5/6之前`Step 4 status: SUCCESS`。
- 生成的查询中的每个字段都出现在内省报告中（没有虚构的字段）。
- 多态字段使用内联片段；非多态字段不使用。
- 对于变更，每个必填输入字段（模式中的`!`注释）都存在。
- `scripts/test-lds-graphql-query.sh`无错误返回；或，在错误情况下，显示分类的修复建议。
- 如果输出格式是`LWC集成`，组件从`lightning/graphql`导入，使用`gql`标记模板，并通过getter（而不是直接在HTML中）暴露数据。
