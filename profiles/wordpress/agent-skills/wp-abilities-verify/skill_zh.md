# WP 能力验证

验证 WordPress 插件的能力 API 注册情况。核心是**对抗性注解正确性检查**：一个 `readonly: true` 的能力实际上会写入（通过 `$wpdb->update`、`update_option`、非 GET 代理等）是一个安全和用户体验灾难，因为代理会根据它们introspected 的注解来计划操作。这项技能通过读取回调体并比较其行为与注解声明的行为来捕捉这些谎言。

这项技能还会验证 `wp-abilities-audit` 生成的审计文档，检查权限门和模式卫生，并可选地针对实时环境执行每个能力。

## 使用场景

- 插件中注册了能力但在 PR 提交之前。
- 作为已发布插件的健康检查（捕获重构将只读能力转换为写入能力的回归问题）。
- 在将审计文档交给实现者之前进行验证。

## 两种模式

- **静态模式** — 从插件检出运行。不需要环境。通过源代码检查枚举，运行对抗性正确性检查，运行模式和权限检查，并验证审计文档。
- **运行时模式** — 需要一个运行中的环境。做静态模式做的一切 PLUS：`wp_get_abilities()` 用于权威枚举，使用策划的输入执行每个能力，确认对真实用户的权限往返，并在 `idempotent: true` 能力上运行双调用启发式算法以标记待审核的候选者（返回值相等是一个信号，而不是一个裁决——核心将 idempotent 定义为“对环境没有附加影响”）。

两种模式都生成相同的结构化报告格式。

静态模式的通过意味着“没有明显的形状违规”，而不是“验证无写入”。对于高风险插件，在提交前运行运行时模式——它捕获静态无法捕获的引导顺序、权限往返和 idempotency 问题。参见 `references/annotation-correctness.md` 了解静态盲点。

## 需要的输入

1. **插件检出路径** — 要验证的工作树。
2. **模式** — `static` 或 `runtime`。如果未指定，默认为静态。
3. **(仅运行时) 环境启动命令** — 读取插件的 `AGENTS.md`。常见模式：`npm run wp-env start`、`npx wp-env start` 或基于 composer 的启动。具有自己开发工具的插件系列将记录自己的命令。不要假设 `npm run wp-env` 有效。
4. **(可选) 审计文档路径** — 启用审计和注册能力之间的交叉检查，并验证审计本身。
5. **报告输出路径** — 明确的路径，通常是用户的钱包。

## 前置条件

- `wp-project-triage` 已在插件上运行。
- 插件在源代码中至少有一个注册的能力。`wp_register_ability(` 没有命中 → 返回一个清晰的“未注册能力”报告，而不是空的通过。

## 程序

### 1. (如果提供审计) 验证审计文档

阅读 `references/audit-schema-validation.md`。根据 `wp-abilities-audit` 拥有的规范模式验证审计。暴露缺失的必填字段、多个 `reference_ability: true` 和 `backing: null` 条目（未与 `surfaced_gaps` 条目配对）。`backing: null` 单独是 WARN（有意输出的间隙），不是 FAIL。

### 2. 静态枚举能力

阅读 `references/static-enumeration.md`。找到每个 `wp_register_ability(` 调用，提取名称、注解块和执行回调位置。使用多行工具 (`rg --multiline --pcre2`) — 规范格式将调用跨行分割。记录每个能力的源文件 + 行 + 注解 + 回调字节范围。

### 3. (仅运行时) 通过 REST + wp-cli 枚举

阅读 `references/runtime-harness.md`。使用 `AGENTS.md` 中的命令启动环境，然后通过 wp-cli 的 `wp_get_abilities()` 进行枚举，并与静态清单交叉检查。仅源代码 → FAIL（注册未触发）。仅运行时 → WARN（动态注册路径）。

### 4. 注解正确性（对抗性核心）

阅读 `references/annotation-correctness.md`。读取每个回调体并验证它是否与注解声明匹配：

- `readonly: true` → 回调不能写入数据库、选项表、帖子 / 用户 / 术语 / 评论数据、文件系统、cron 或通过非 GET HTTP / REST 代理。
- `destructive: false` → 回调不能删除、退款、作废、取消或丢弃。
- `idempotent: true` → 使用相同输入的重复调用对环境没有附加影响（根据 `idempotent` 注解的 `class-wp-ability.php` 中的 docblock）。静态捕获计数写入和每次调用的 cron 计划；运行时添加双调用启发式算法以检测可见状态变化。

参考列表将常见的写入模式作为起始集，而不是清单——插件词汇各异，代理扩展了特定于正在验证的插件的动词。

误报通过在 `references/annotation-correctness.md` 中的内联 `// verify-ignore: <annotation> -- <reason>` 注释来抑制。

### 5. 权限往返

阅读 `references/permission-roundtrip.md`。静态：将每个 `permission_callback` 对应到六个形状（首选 Shape A `current_user_can(...)`；在 Shape B-坏 `WP_REST_Request` 模式或 Shape E 字面量 `true` 上失败）。运行时：匿名和订阅者拒绝；管理员允许（除非故意公开）。当提供了审计时，交叉检查注册的 cap 与审计声明的门。

### 6. 模式检查

阅读 `references/schema-lints.md`。将六个小原则应用于每个能力的 `input_schema`：对象模式声明 `additionalProperties`；必填字段有描述；枚举非空；没有 `$ref`；默认值是静态常量（包括 `(object) array()`）；参考能力没有必填输入。

交叉参考 `../wp-abilities-api/references/input-schema-gotchas.md` 了解四个运行时陷阱（在属性级路径上未注入默认值、分页键漂移、字符串 ID 的 `empty()`、直接与间接调用的严格性）。

### 7. 错误码词汇

交叉参考 `../wp-abilities-api/references/error-code-vocabulary.md`。检查每个回调的 `WP_Error` 返回；非词汇代码 → WARN。

## 验证

运行生成用户指定路径的结构化 markdown 报告：

```
---
最后更新: <YYYY-MM-DD HH:MM>
---

# <插件> 能力验证 — <静态|运行时> 模式

## 状态: <PASS|WARN|FAIL>

## 审计文档验证 (如果提供)

## 静态清单

## 注解正确性
| 能力 | 声明 | 结果 | 证据 |
|---|---|---|---|

## 权限门

## 模式检查

## 错误码词汇
```

每个能力都是 OK、WARN 或 FAIL。单个 FAIL → 顶行 FAIL；没有 FAIL 的 WARNs → WARN；否则 PASS。

## 失败模式 / 调试

- **环境不可达 (运行时)** — 环境启动失败或 Docker 没有运行。重新运行 `wp-project-triage`，然后修复环境。不要在报告中无声地回退到静态。
- **源代码中无能力** — 返回一个清晰的“无验证内容”报告。
- **审计模式不匹配** — 指向 `references/audit-schema-validation.md`；不要自动修复审计。
- **只读写入的误报** — 参见 `references/annotation-correctness.md` 中的 `// verify-ignore` 机制。记录每个抑制的合法性原因。
- **运行时枚举小于静态** — 注册钩子未触发。检查初始化钩子时间、激活状态、自动加载器顺序。

## 升级

- 在多个插件中反复触发对抗性检查的合法模式 → 提议将其添加到 `annotation-correctness.md` 中的抑制指南。不要推测性地放宽候选模式列表规范。
- 审计模式验证器拒绝合法审计 → `../wp-abilities-audit/references/audit-schema.md` 中的规范模式已演变。更新 `references/audit-schema-validation.md` 以匹配。

## 不在范围内

令牌预算测量是一个独立的验证轴——一个注解干净、模式干净、运行时通过的能力集仍然可能无法发布，如果它的 `tools/list` 形式消耗了代理的上下文预算。该轴单独跟踪。不要将手动或外部测量聚合到这项技能的 PASS / FAIL 裁决中。
