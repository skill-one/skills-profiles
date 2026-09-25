# 迁移到 Runpod REST v2

将代码库从 **GraphQL API** (`api.runpod.io/graphql`) 和 **REST v1** (`rest.runpod.io/v1`) 迁移到 **REST v2** (`api.runpod.io/v2`)。

**收益，用一句话概括** — 你在步骤 6 向用户交付这些内容，并与他们的实际代码相匹配。现在不要复述它们：

- **租用前先看库存** — `GET /v2/catalog/gpus?include=AVAILABILITY&product=POD`。v1 完全没有目录，所以每个容量重试循环都是盲目的。
- **端点返回它们自己的作业 URL** — `requestUrls.run`，不再需要字符串构建。
- **真实的生命周期状态** — `PROVISIONING`/`STARTING`/`ERROR` 和一个 `actions` 列表，因此等待循环可以快速失败而不是超时。
- **错误会大声报告** — 未知请求字段会按名称被拒绝，并提供结构化错误和诚实的状态码。

完整列表，按 *如果他们的代码执行 X → v2 提供 Y* 的方式组织：
**[reference/unlocks.md](reference/unlocks.md)** — 在步骤 6 打开它。

## 在触摸任何代码之前

**推断范围，声明范围，然后迁移** — 不要以问卷开头：

| 用户说 | 范围 |
| --- | --- |
| "迁移到 v2" / 没有具体说明 | `all` — REST v1 **和** GraphQL |
| "只迁移 REST 部分"，"不要动 GraphQL" | `rest` — 仅 REST v1 |
| "让我们摆脱 GraphQL" | `graphql` — 仅 GraphQL |

该表格解决了每一种说法，所以范围不是要中断的事情。说出你匹配的行，然后继续。**需要问的问题是在稍后** — 在步骤 3，当清单显示代码依赖于 v2 移除的功能时。这是一个真正的分支，你不能为他们回答它。

有些东西 **没有 v2 对应物，并且无论如何都必须保留在 GraphQL 上**：
账户/计费身份 (`myself`)、密钥、斑点/可中断的 Pod、集群创建/删除。一个“完整”的迁移仍然保留这些调用，所以一开始就说明这一点，而不是让用户在最后发现它。

**永远不要重写无服务器作业 API。** `https://api.runpod.ai/v2/<endpointId>/run`、`/runsync`、`/status`、`/stream`、`/cancel` 是一个 *不同的 API*，它恰好在其路径中包含 `v2`。它没有改变并且不在范围内。清单将其单独报告，所以你不会触摸它。

## 工作流程

### 1. 清单 — 没有数过的东西不要迁移

扫描器与 **此文件一起提供**，在安装的技能目录中 — 不是在用户的代码库中。首先解决其路径；你的工作目录是他们的项目：

```bash
# 1. Claude 代码插件安装暴露插件根目录：
SCAN="$CLAUDE_PLUGIN_ROOT/skills/runpod-migrate/scripts/rp_api_inventory.py"
# 2. 否则，替换你加载此 SKILL.md 的目录 — 你知道的：
[ -f "$SCAN" ] || SCAN="<包含此 SKILL.md 的目录>/scripts/rp_api_inventory.py"
# 3. 最后的救济措施，搜索通常的安装根目录：
[ -f "$SCAN" ] || SCAN=$(find ~/.claude ~/.agents ~/.codex ~/.config -name rp_api_inventory.py 2>/dev/null | head -1)
python3 "$SCAN" --help >/dev/null || echo "扫描器未找到 — 在继续之前解决它"
```

然后，从用户的代码库的根目录：

```bash
python3 "$SCAN" . > runpod-api-inventory.md
python3 "$SCAN" . --json > runpod-api-inventory.json   # 如果你想要从它驱动编辑
python3 "$SCAN" . --scope rest                          # 仅 REST 迁移
```

`runpod-api-inventory.md` 落在用户的代码库中 — 提及它，并在交还迁移之前将其删除或添加到 gitignore 中。

纯标准库 Python，无需安装。它按生成版本对每个调用位置进行分组报告 — GraphQL、REST v1、v1/GraphQL **字段名**、REST v2 **已**、无服务器作业 API、SDK/CLI 包装器 — 以及建议的按文件顺序。

**在编辑任何东西之前向用户展示清单表。** 用户通常不知道他们正在使用什么：代理几个月前为他们选择了一个版本，并且没有记录下来。“v1 上有 3 个文件，GraphQL 上有 2 个，v2 上有 1 个，作业 API 上有 2 个 — 留下这些不要动” 通常是这项技能最有用的输出。

#### 它能检测到什么，以及它不能检测到什么

它是正则表达式行扫描，但分类使其可用 — 纯 `grep -r runpod` 会主动做两件错事：

- **`api.runpod.ai/v2` 与 `api.runpod.io/v2`。** 只差一个字母。`.ai` 是无服务器作业 API，不能被触摸；`.io` 是你要迁移的控制平面。
  `v2` 告诉你代码库已经“迁移”了，但实际上没有。
- **在两个版本中都合法的名称。** `/pods` 是 v1 路径 *和* v2 路径；`["pods"]` 是 v2 封装解包；`idleTimeout` 在 v1 中是顶层，在 v2 中嵌套在 `workers` 下。扫描器在包含 v2 上下文的行上抑制命中，所以它报告剩余的工作而不是每个单词的出现。

它还在寻找 **字段名，而不仅仅是 URL**，这就是它捕获那些从未拼写“runpod”的文件的原因：一个模块从包装器的返回值中读取 `p["costPerHr"]` 没有 URL、没有导入、没有操作名 — 恰好是 v2 重命名会无声破坏的东西。

有四件事它确实无法解决。每次手动检查它们：

| 盲点 | 如何解决它 |
| --- | --- |
| **基础 URL 存在于配置中，而不是代码中** (`settings.yaml`，`.env`，ConfigMap，Terraform) | 扫描器确实读取这些文件，所以 URL 会显示出来 — 但使用它的调用位置在别处。搜索读取该配置键的人。 |
| **由辅助程序组装的路径** — `_url("pods", pod_id, "stop")` | 报告在 *可能的间接调用位置* 下。建议，因为 `resp.json()["pods"]` 看起来相同。打开每一个。 |
| **SDK 包装器** (`import runpod`) | API 生成是安装 *版本* 的属性，而不是代码。检查 `requirements.txt` / 锁文件和 SDK 自己的发布说明。 |
| **生成的客户端** | OpenAPI/GraphQL 文档是真正的来源。从 v2 规范重新生成，而不是编辑生成的文件。 |

然后阅读扫描器标记的代码。它找到调用位置；它不理解你的包装器。跟踪谁调用它们 — 像重命名的响应字段 `costPerHr → cost` 会破坏每个调用者，而不仅仅是请求构建者。这是这一步中代码图或 LSP 索引值得其价值的地方，如果已经可用的话。

### 2. 简要说明破坏性变更 — 在 diff 之前，而不是之后

阅读 **[reference/breaking-changes.md](reference/breaking-changes.md)** 并告诉用户哪些实际适用于 *他们的* 代码。两类，第二类是他们害怕的：

1. **重命名和移动** — 响亮。v2 会用 `422` 拒绝未知的请求字段，并按名称列出它们，所以遗漏的重命名不会悄悄地进入生产。
2. **相同名称，不同含义** — 安静，并且是绿色测试套件不是证明的原因。参考文档枚举了每一个；其中两个咬人最狠：
   `flashboot` 从布尔值变为三值枚举，v1 的 `/billing/endpoints`（无服务器支出）是 v2 的 `/billing/serverless` — v2 的 `/billing/endpoints` 计费 *不同的产品*（公共端点），并以正确的总额回答 `200`，这不是调用者要的产品。

### 3. 计划，分为必需和清理

在编辑之前写下计划，并在整个过程中保持这些桶分开，直到最终总结：

- **必需** — 没有它，v2 上无法工作。
- **清理** — 无论哪种方式都可以工作，但 v2 允许你删除代码（手工构建的作业 URL、手工构建的可用性重试、现在可以用 SSE 的轮询循环）。
- **用户必须做出的决定** — 代码依赖于 v2 直接移除的东西：
  斑点/可中断的 Pod、储蓄计划、`dockerEntrypoint`、放置约束 (`countryCodes`，`minRAMPerGPU`，…)、Pod `reset`、每个 Pod 的 GPU 回退。查看
  [breaking-changes.md](reference/breaking-changes.md) 类 3 — 并且检查它，而不是从记忆中工作，因为随着 v2 的发展，东西会离开这个桶。CUDA 固定、`templateId` 和 CPU 端点写入现在都不在这里了。

**在为第三个桶编写代码之前停下来提问** — 但带上替代方案。其中一些有可工作的重建，而另一些则确实没有，这决定了你要问什么。在存在重建的情况下（`countryCodes` →
[目录过滤器 + `dataCenterIds` + 放置
断言](reference/breaking-changes.md#replacing-countrycodes-and-the-rest-of-the-placement-constraints)，
每个 Pod 的 GPU 回退 →
[一个可用性排序的循环](reference/breaking-changes.md#replacing-the-gpu-fallback-list-pods-only))，展示它并问那个会改变它的唯一问题 — 对于 `countryCodes`，限制是偏好还是合规要求。在不存在重建的情况下，选项是接受行为变化、保留 v1/GraphQL 上的调用，或围绕它重新设计，只有用户才能选择。

无论如何，当存在重建时，不要将删除呈现为死胡同 — 这会迫使用户保留他们不需要保留的 v1 调用。并且永远不要带有 `# 没有 v2 对应物` 注释丢弃字段：这个桶存在就是为了防止这种无声的行为变化。如果桶是空的，就说出来 — 这令人放心，并且只需要一行。

### 4. 迁移，每个提交一个文件

在扫描器建议的顺序（调用位置最少优先）中工作 — **有一个例外：如果多个调用位置共享一个传输辅助程序，首先迁移辅助程序**，无论其计数如何。扫描器按调用位置计数排序，但看不到导入，所以它会很高兴地将消费者放在它导入客户端的模块之前。首先迁移消费者意味着你在使用一个即将更改的接口编写代码。

每个文件：

- 使用 **[reference/rest-v1-to-v2.md](reference/rest-v1-to-v2.md)** 或 **[reference/graphql-to-v2.md](reference/graphql-to-v2.md)** 映射路径和字段。如果字段不在表中，或者 API 与它们不一致，请直接查看规范 —
  [真实情况](#ground-truth-check-the-spec-yourself)。
- **`gpuTypeIds` + `gpuTypePriority` 在一个 *Pod* 上意味着你正在编写新代码，而不是重命名字段。** 一个 v2 Pod 只接受一个 GPU 类型，所以服务器端回退变成了客户端循环遍历目录。工作实现：
  [breaking-changes.md → Replacing the GPU fallback list](reference/breaking-changes.md#replacing-the-gpu-fallback-list-pods-only)。
  **端点不需要循环** — `gpu.pools` 已经是一个列表，工作者会落在列出的池中具有容量的那个上。
- **始终在目录读取中请求可用性 — 带有 `product`。** 任何
  `GET /v2/catalog/gpus`、`/catalog/cpus` 或 `/catalog/datacenters` 这个迁移引入的调用都会得到 `include=AVAILABILITY` (`GPU_AVAILABILITY`/`CPU_AVAILABILITY` 对于数据中心)。可用性是每个 Runpod 用户最关心的问题，调用成本相同。不要因为当前代码没有请求它就省略它 — v1 无法。

  **`include=AVAILABILITY` 单独就是 `400`。** 在 `/catalog/gpus` 和 `/catalog/cpus` 上，`product` 与它一起是必需的，没有它就是无效的 — 无论如何都是 `400`。没有默认值，故意如此：同一个 GPU 可以在 `POD` 上稀缺，在 `SERVERLESS` 上充足，所以上下文必须声明。选择与你要创建的内容匹配的（`POD`、`SERVERLESS` 或 `CLUSTER`；CPU 取 `POD` 或 `SERVERLESS`）：

  ```
  GET /v2/catalog/gpus?include=AVAILABILITY&product=POD
  ```
- 提供回滚标志 (`RUNPOD_API_V1=1`)，当 v2 对他们来说还是新的时候：
  **[reference/rollback-flag.md](reference/rollback-flag.md)**。对于生产中的服务来说值得；对于一次性脚本则跳过它。
- **永远不要在同一提交中更改行为和 API 版本** — 包括 v2 使其成为可能改进。在 `status == "ERROR"` 时快速失败而不是超时是一个真正的胜利，它属于 *下一个* 提交；将其合并到迁移提交中意味着回滚必须放弃两者。将这些放在 **清理** 桶中，单独处理。

一个真实客户端的完整前后示例 — 创建 Pod 带有 GPU 回退，创建端点带有内联的容器配置，GraphQL 仪表板 — 在
**[reference/worked-example.md](reference/worked-example.md)** 中。

### 5. 与实时 API 验证

静态审查是不够的；v2 的验证器是严格的，并且它的错误是精确的。重新运行扫描器以证明调用位置已消失，然后实际使用路径：

```bash
python3 "$SCAN" . --scope rest --fail-on-legacy   # 如果 v1 仍然存在则退出 1
```

两个标记，它们意味着不同的事情 — 不要抓住错误的那个：

| 标记 | 用于 |
| --- | --- |
| `rp-migrate: keep-v1` | 有意保留的遗留代码 — `RUNPOD_API_V1` 回滚分支，或没有 v2 对应物的 GraphQL 调用。报告在 *有意保留* 下。 |
| `rp-migrate: ignore` | **误报** 在代码已经正确的情况下。说“这不是遗留”，而不是“这是遗留我正在保留”。报告在 *标记为误报* 下。 |

两者都接受 `line`、`start`/`end` 区域或 `file` 范围，并且两者都会从计划中删除，并且会从 `--fail-on-legacy` 中删除。使用 `keep-v1` 来抑制误报会在报告中记录一个谎言 — 在那里使用 `ignore`。

**门仍然可能出错的地方。** 步骤 1 中的相同盲点在迁移后反转：之前它们隐藏了 v1 代码；之后它们可能会标记正确的 v2 代码。扫描器处理两个常见情况 — 残留的 `# was imageName` 注释，以及基 URL 存储在常量中 (`f"{BASE}/pods"` 其中 `BASE` 是文件中定义的 v2 URL 任何地方)。除此之外 — 从另一个模块导入的基 URL，或在运行时从配置构建的 — 它仍然可能将正确的代码误读为遗留。在相信退出代码之前，阅读被标记的行，并使用 `ignore` 而不是削弱门来标记真正的误报。

- **读取** 是免费的 — 列出 Pod、端点、卷、目录。确认你解包了新的封装 (`{"pods": [...]}`，而不是裸数组)。
- **写入** 花钱。在证明形状的最小事物上创建 → 断言 → 删除，在用户已经拥有的资源上测试。永远不要针对用户已经拥有的资源进行测试。
- 解码 `422`s 使用
  [reference/breaking-changes.md](reference/breaking-changes.md#reading-a-422) 中的表格 — 包括那个令人困惑的情况，其中 *缺少必需字段* 使验证器报告你的 *有效* 字段为“不允许的附加属性”。

### 6. 总结 — 这是他们实际会阅读的工件

大多数用户阅读总结而不是 diff。按以下方式结构化：

```
## 迁移所需的
<文件:行> — 改变的原因

## v2 使清理成为可能
<文件:行> — 删除或简化的内容

## 要注意的行为变化
适用相同的名称，不同含义的项目

## 仍然在 GraphQL 上（没有 v2 对应物）
myself / secrets / 斑点 Pod / 集群 — 以及原因

## 解锁：你现在可以构建什么
与这个代码库已经做什么相关联
```

最后一个部分是最高价值部分。不要粘贴一个通用的功能列表 — 查看用户一直在构建和挣扎的东西，包括你从会话中已经知道的任何东西，并命名 v2 如何改变它。“你的 `wait_until_running` 循环在失败的 Pod 上超时；v2 的 `ERROR` 状态允许它在几秒钟内失败” 比起“v2 有更丰富的状态值”更有用。[reference/unlocks.md](reference/unlocks.md) 按照这样的方式组织 *如果代码执行 X → v2 提供 Y* 正是为了这个。

## 真实情况：自己检查规范

`reference/` 中的映射表是在 **2026-08-10** 对实时 API 进行验证的。v2 正在积极开发中，所以将它们视为快速路径，而不是权威。两个规范都是公开的，无需身份验证：

```bash
curl -s https://api.runpod.io/v2/openapi.json  -o /tmp/rp-v2.json
curl -s https://rest.runpod.io/v1/openapi.json -o /tmp/rp-v1.json
```

**请求体实际接受的内容，以及需要的内容** (`*`)。在编写任何创建调用之前运行它 — 它解决了 `allOf` 组合，这可能是对原始 JSON 的简单读取所遗漏的：

```bash
python3 - CreateEndpointRequest <<'PY'
import json, sys
S = json.load(open("/tmp/rp-v2.json"))["components"]["schemas"]
def merge(n, acc=None):
    acc = acc if acc is not None else {"props": {}, "req": set()}
    if "$ref" in n: return merge(S[n["$ref"].split("/")[-1]], acc)
    for sub in n.get("allOf", []): merge(sub, acc)
    acc["props"].update(n.get("properties", {})); acc["req"].update(n.get("required", []))
    return acc
def kind(v):
    if "$ref" in v: return v["$ref"].split("/")[-1]
    if "allOf" in v: return kind(v["allOf"][0])
    return v.get("type", "?")
m = merge(S[sys.argv[1]])
for k, v in sorted(m["props"].items()):
    print(f"  {'*' if k in m['req'] else ' '} {k:16} {kind(v)}")
PY
```

将参数交换为 `CreatePodRequest`、`UpdatePodRequest`、`CreateTemplateRequest`、`CreateNetworkVolumeRequest`，… **哪些模式提到字段** — 当 `422` 命名你无法放置的东西时有用：

```bash
python3 -c 'import json,sys; S=json.load(open("/tmp/rp-v2.json"))["components"]["schemas"]; [print(" ",n) for n,s in S.items() if sys.argv[1] in json.dumps(s)]' flashboot
```

### 源不一致时的优先级

**观察到的实时行为 > 规范 > 这些表。** 规范并不总是正确的，参考文档在哪里知道它是错误的 — `timeout` 被记录为默认为 `300000` 毫秒，但返回 `0`。如果你遇到运行时 API 与规范矛盾的情况，相信 API，并 **在你的总结中说明**，这样用户知道一个记录的默认值不能被依赖。

如果你发现 `reference/` 中的映射不再与规范匹配，修复调用并标记漂移 — 表格包含验证日期，正好是为了检测过时而不是无声。

对于 GraphQL 没有机器可读模式（ introspection 被禁用），所以那一边不能以这种方式检查 — 见
[reference/graphql-to-v2.md](reference/graphql-to-v2.md) 中的注意事项。

## 工具说明

清单扫描器故意是一个 **grep 类脚本，而不是代码图索引**：
API 生成是 URL 字符串和字段名的属性，它必须在任何语言中的任意客户代码库中工作，并且必须为零设置提供相同的答案。代码智能索引（LSP，或者如果已经运行，则是一个 MCP 图服务器）在第一步 *爆炸半径* 问题时值得其价值 — 不是在检测时。如果已经可用，使用它；不要为了这个而建立它。
