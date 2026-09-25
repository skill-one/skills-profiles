# /printing-press-reprint

在当前机器上重新生成现有的打印CLI。用户给出CLI名称和（可选的）重新打印的原因。此技能确保先前的CLI在本地存在，建议是否重用或重新进行先前的研究，并将上下文交给`/printing-press`，供novel-features子代理需要协调先前功能与当前机器——保留、重新框架或删除并说明原因，绝不沉默。

```bash
/printing-press-reprint notion
/printing-press-reprint cal.com  新的MCP表面已发布，先前的CLI仅提供endpoint-mirror
/printing-press-reprint allrecipes
```

## 运行时机

- 显著的Printing Press升级（新的MCP表面、新的认证模式、新的传输方式、评分标准变更）将比手动优化更优先使用此CLI。
- 发布的CLI存在已知的系统级缺陷，重新打印可以修复。
- 用户希望先前的novel features根据当前机器和当前角色重新评估，而不是原封不动地继承。

对于一次性代码质量修复，优先使用`/printing-press-polish`——它不会重新进行研究或重建手稿。

## 配置

```bash
PRESS_HOME="${PRINTING_PRESS_HOME:-$HOME/printing-press}"
PRESS_LIBRARY="$PRESS_HOME/library"
PRESS_MANUSCRIPTS="$PRESS_HOME/manuscripts"

# 中间流程调用者可以在参数包中传递printing_press_bin: <绝对路径>。优先使用它，以便重新打印时继续使用父技能预选的二进制文件，而不是重新通过PATH解析。
PRINTING_PRESS_BIN="${PRINTING_PRESS_BIN:-}"
if [ -z "$PRINTING_PRESS_BIN" ] && [ -n "${ARGUMENTS:-}" ]; then
  PRINTING_PRESS_BIN="$(printf '%s\n' "$ARGUMENTS" | sed -nE 's/^[[:space:]]*printing_press_bin:[[:space:]]*(.+)$/\1/p' | head -1)"
fi
if [ -z "$PRINTING_PRESS_BIN" ]; then
  PRINTING_PRESS_BIN="$(command -v cli-printing-press 2>/dev/null || true)"
fi

if [ -z "$PRINTING_PRESS_BIN" ]; then
  echo "cli-printing-press二进制文件未找到。"
  echo "安装方式：  go install github.com/mvanhorn/cli-printing-press/v4/cmd/cli-printing-press@latest"
  return 1 2>/dev/null || exit 1
fi
echo "PRINTING_PRESS_BIN=$PRINTING_PRESS_BIN"
```

## 阶段A — 解析和协调存在

与`/printing-press-import`相同的方式解析用户参数：
一次性获取公共库`registry.json`，然后精确→标准化→模糊匹配。参数可以是API缩写（`notion`）、品牌名称（`cal.com`）、旧`<api>-pp-cli`形式或足够接近。

从匹配的注册条目中捕获：`API_SLUG`（来自`.name`）和`LIB_PATH`（来自`.path`，例如`library/productivity/cal-com`）。阶段B使用`$LIB_PATH`获取公共补丁。对于"存在|不存在"的未发布行，`$LIB_PATH`保持为空——阶段B的获取会短路。

然后检查本地存在情况，并通过读取两个来源清单的`run_id`和`generated_at`与公共库进行协调：

| 本地 | 公共注册 | 操作 |
|------|----------|------|
| 不存在 | 不存在 | 停止——无重新打印内容；建议使用`/printing-press <api>`进行全新打印 |
| 不存在 | 存在 | 调用`/printing-press-import <api>`，然后继续 |
| 存在 | 不存在 | 继续——未发布的本地CLI；跳过导入 |
| 存在，相同的`run_id` | 存在 | 继续不导入 |
| 存在，公共更新的`generated_at` | 存在 | 提供通过`AskUserQuestion`导入；用户决定 |
| 存在，本地更新的`generated_at` | 存在 | 停止——本地有未发布工作；告知用户先发布或丢弃 |

调用`/printing-press-import`时，让其拥有备份、覆盖、构建验证和模块路径重写。等待它返回干净后再继续。

## 阶段B — 验证可协调的先前上下文

定位写作流程应知道的两个工件：研究（驱动novel-features Pass 2(d)）和补丁（由`/printing-press-amend`记录的发布后手动修复，例如未在规范中揭示的API怪癖）。

```bash
LIB_TARGET="$PRESS_LIBRARY/$API_SLUG"
LIB_RESEARCH="$LIB_TARGET/research.json"
MAN_RESEARCH=$(ls -1t "$PRESS_MANUSCRIPTS/$API_SLUG"/*/research.json 2>/dev/null | head -1)
```

### 研究不存在

如果两个研究路径都不存在，发布的CLI早于`research.json`来源。子代理将运行视为首次打印，Pass 2(d)重新协调不会触发——没有可读取的内容。提示并询问：

> 发布的`<api>`在`research.json`来源发布前构建。没有它，novel-features子代理将视此为首次打印——没有可协调的内容。继续作为降级重新打印（本质上是一个保留二进制名称的新打印）？

如果用户拒绝，退出。如果他们继续，记录缺失，以便手交提示注明这是一个降级重新打印。

### 补丁发现

当可达时，从公共刷新本地补丁索引，然后本地读取以使下游引用持久化。修正可能已针对公共副本发布而未触发重新生成，即使`run_id`匹配时本地副本也可能滞后；此步骤关闭了这一差距。

索引以两种形状之一提供：每个补丁目录`.printing-press-patches/`（当前）或遗留单个数组`.printing-press-patches.json`（较旧的CLI尚未标准化）。当可达时始终检查这两种形状。当包含补丁文件时优先使用目录，但绝不让缺失的遗留单个文件索引将`PATCH_COUNT=0`，直到目录回退已读取。

```bash
PATCHES_DIR="$LIB_TARGET/.printing-press-patches"
PATCHES_LEGACY="$LIB_TARGET/.printing-press-patches.json"
if [[ -n "$LIB_PATH" ]]; then
  # 如果存在，获取遗留形状，但不要将404视为不存在补丁的证据。当前库条目可能仅包含下面的每个补丁目录。
  tmp=$(mktemp)
  if gh api -H "Accept: application/vnd.github.v3.raw" \
       "repos/mvanhorn/printing-press-library/contents/$LIB_PATH/.printing-press-patches.json" \
       > "$tmp" 2>/dev/null; then
    mv "$tmp" "$PATCHES_LEGACY"
  else
    rm -f "$tmp"
  fi

  # 独立获取当前目录形状。当`.printing-press-patches.json`缺失时这是必需的回退。
  listing=$(gh api "repos/mvanhorn/printing-press-library/contents/$LIB_PATH/.printing-press-patches" 2>/dev/null || true)
  if jq -e 'type == "array"' <<<"$listing" >/dev/null 2>&1; then
    mkdir -p "$PATCHES_DIR"
    jq -r '.[] | select(.name | endswith(".json")) | "\(.name)\t\(.download_url)"' <<<"$listing" \
    | while IFS=$'\t' read -r name url; do
        tmp=$(mktemp)
        if curl -fsSL "$url" -o "$tmp" 2>/dev/null; then
          mv "$tmp" "$PATCHES_DIR/$name"   # 原子操作：中断传输不会留下损坏的JSON
        else
          rm -f "$tmp"
        fi
      done
  fi
fi

# 从第一个非空形状本地计数；PATCHES_SOURCE是阶段D读取的。
if [[ -d "$PATCHES_DIR" ]]; then
  DIR_PATCH_COUNT=$(find "$PATCHES_DIR" -maxdepth 1 -name '*.json' ! -name '_meta.json' | wc -l | tr -d ' ')
else
  DIR_PATCH_COUNT=0
fi
if [[ "$DIR_PATCH_COUNT" != "0" ]]; then
  PATCH_COUNT="$DIR_PATCH_COUNT"
  PATCHES_SOURCE="$PATCHES_DIR"
elif [[ -f "$PATCHES_LEGACY" ]]; then
  PATCH_COUNT=$(jq '(.patches // []) | length' "$PATCHES_LEGACY" 2>/dev/null || echo 0)
  PATCHES_SOURCE="$PATCHES_LEGACY"
else
  PATCH_COUNT=0
  PATCHES_SOURCE="$PATCHES_DIR"
fi
```

如果`$PATCH_COUNT == 0`或不存在索引（较旧的CLI早于补丁合同），跳过本小节的其余部分——没有补丁会阻塞手交。

如果`$PATCH_COUNT > 0`，在手交前向用户显示一行：

> 公共`<api>`有`$PATCH_COUNT`个记录的针对先前打印CLI的补丁。将它们作为观察列表带入简报。重新生成和发布验证现在读取记录，如果记录的文件或声明的调用位置/`pp:patch`标记已消失则失败关闭——不要将索引视为声称定制仍然交付。

保留`$PATCHES_SOURCE`和`$PATCH_COUNT`供阶段D使用。

## 阶段C — 新鲜度建议

从最新的先前`research.json`中拉取`researched_at`，从`.printing-press.json`中拉取`printing_press_version` + `generated_at`：

```bash
RESEARCHED_AT=$(jq -r '.researched_at // empty' "$MAN_RESEARCH" 2>/dev/null)
PRESS_VERSION=$(jq -r '.printing_press_version // empty' "$LIB_TARGET/.printing-press.json" 2>/dev/null)
GENERATED_AT=$(jq -r '.generated_at // empty' "$LIB_TARGET/.printing-press.json" 2>/dev/null)
```

使用`python3`计算研究的日历年龄，使其跨macOS/Linux保持可移植性，并容忍`generated_at`携带的微秒精度（BSD `date -f`拒绝分数秒；`python3`在所有支持平台上都有）：

```bash
AGE_DAYS=$(python3 -c "
from datetime import datetime, timezone
ts = '$RESEARCHED_AT'.replace('Z', '+00:00')
print(int((datetime.now(timezone.utc) - datetime.fromisoformat(ts)).total_seconds() // 86400))
" 2>/dev/null)
```

向用户展示这两个信号——研究年龄和先前的机器版本。年龄阈值只是经验法则，不是门槛：

- 30天以下 → 重用看起来安全
- 30–120天 → 重用可能；用户应在重新打印原因中提及任何已知的API更迭，以便子代理的Pass 2捕获
- 超过120天 → 建议重新进行

不要仅凭年龄预测API更迭——描述信号并让用户覆盖。`/printing-press`中的阶段0二进制版本提升重新验证独立处理机器差异侧；不要在此处重复它。

通过`AskUserQuestion`询问：

1. **重用先前研究**——保留先前简报；子代理重新对当前角色评分先前的novel features
2. **重新研究**——从头开始重新运行`/printing-press`的阶段1；子代理仍然将先前的novel features作为Pass 2(d)输入
3. **显示给我第一个**——显示先前简报的标题+novel-features列表，然后重新询问选项1和2之间

## 阶段D — 交接到`/printing-press`

在调用`/printing-press`之前，使用先前CLI的评分卡和清单决定重新打印是否应提供规范丰富，而首次打印无法使用。重新打印比新鲜打印有更好的证据：它们知道哪些结构维度较弱，哪个Printing Press版本生成了先前的CLI，以及用户命名为重新生成的原因。

找到先前手稿运行的最新的评分卡JSON。如果不存在评分卡工件，对本地库副本运行新的结构评分卡：

```bash
SCORECARD_SOURCE=$(ls -1t "$PRESS_MANUSCRIPTS/$API_SLUG"/*/proofs/scorecard.json 2>/dev/null | head -1)
SCORECARD_JSON=""
if [[ -n "$SCORECARD_SOURCE" ]]; then
  SCORECARD_JSON=$(cat "$SCORECARD_SOURCE" 2>/dev/null || true)
elif [[ -d "$LIB_TARGET" ]]; then
  SCORECARD_SOURCE=$(mktemp)
  if "$PRINTING_PRESS_BIN" scorecard --dir "$LIB_TARGET" --json > "$SCORECARD_SOURCE" 2>/dev/null; then
    SCORECARD_JSON=$(cat "$SCORECARD_SOURCE" 2>/dev/null || true)
  fi
  rm -f "$SCORECARD_SOURCE"
  SCORECARD_SOURCE=""
fi
```

如果`SCORECARD_JSON`为空，继续不进行丰富提示，并说明重新打印没有先前的评分证据。不要仅凭重新打印原因发明提示。

当`SCORECARD_JSON`可用时，只检查映射到生成前规范编辑的维度，跳过已评分10/10的维度：

- 低于10分的`mcp_remote_transport`、`mcp_token_efficiency`、`mcp_tool_design`和`mcp_surface_strategy`可以通过`/printing-press`阶段2的**生成前MCP丰富**提升。示例：
  - 远程传输低于10分：在重新生成前提供`mcp.transport: [stdio, http]`或OpenAPI的`x-mcp.transport`等效项。
  - token效率、工具设计或表面策略低于10分：提供`/printing-press`阶段2的MCP表面决策，包括清晰多步骤工作流的意图或大型表面的Cloudflare模式。
- 低于10分的`auth_protocol`，或先前清单证据表明CLI使用了派生自slug的环境变量，而生态系统中有一个规范环境变量，可以通过**生成前认证丰富**提升。提供将规范`auth.env_vars`或OpenAPI的`x-auth-env-vars`指导带入规范。
- 低于10分的`data_pipeline_integrity`仅在先前的CLI或研究显示有同步资源的条件下才是丰富机会。在这种情况下，将手交指向相关的`/printing-press`阶段2同步/缓存丰富决策，而不是单独将评分视为本地存储存在的证据。

在每次具体机会前使用`AskUserQuestion`。围绕评分卡证据和规范章节提问，而不是自由形式的改写。示例：

> 先前评分卡显示`mcp_remote_transport: 5/10`。在重新生成前提供MCP传输丰富，使用`/printing-press`阶段2的**生成前MCP丰富**作为真实来源？

选项：

1. **将丰富应用于手交** - 将选定的规范编辑包含在`/printing-press`提示中，以便阶段2可以在生成前更新规范。
2. **跳过本次重新打印** - 留下此维度的规范不变。
3. **先显示评分证据** - 打印相关的评分卡行，然后重新询问选项1和2之间。

不要自动应用丰富。如果先前的评分卡已有`mcp_remote_transport: 10/10`，不要询问冗余的MCP传输问题。如果用户接受任何机会，在`/printing-press`手交中添加`## 重新打印规范丰富`部分。保持简短：命名薄弱维度、接受的丰富和要执行的规范`/printing-press`阶段2章节。不要在此处重复规范丰富文本。

调用`/printing-press <api>`并将这些捆绑到提示中：

1. **标题行**声明用户已选择重新生成，因此`/printing-press`阶段0的库检查应选择“生成全新CLI”而不是重新提示新鲜vs改进。
2. **研究模式**来自阶段C（`reuse`或`redo`）。`/printing-press`阶段0的现有重用逻辑消耗此内容。
3. **用户的自由形式重新打印原因**，逐字，在`User context`块中。这传播到简报作为`## 用户愿景`，并成为novel-features子代理的Pass 2(e)输入——这是“我想更好的MCP支持”→相应偏置头脑风暴的正确钩子。
4. **重新打印规范丰富**——仅当上述评分卡驱动提示找到接受的机遇时。在`## 重新打印规范丰富`标题下包含。
5. **先前补丁**——仅当阶段B找到`$PATCH_COUNT > 0`。在`## 先前补丁`标题下包含。

   以此框架句子开头，逐字：

   > 以下是对先前打印CLI的手动修复。它们是信息性的——机器可能自补丁应用以来已吸收其中一些内容。保持警惕，以便新鲜代码不会无声地回归底层API真相或架构模式，但不要将其视为重新应用清单。

   然后总结来自`$PATCHES_SOURCE`的补丁。以补丁的*实质*（API真相、架构模式、跨文件约定）开头，从每个补丁的`reason`和`validated_outcome`中提取，而不是仅`summary`。补丁元数据（`id`、`files`）可以作为括号上下文，但永远不要作为标题。

   根据补丁数量调整部分：

   - **1–3个补丁**：每个补丁一个简短段落——先实质，然后如何体现。参考：
     > Linear的个人API密钥放在`Authorization: lin_api_…`原始中，不带`Bearer`前缀；OAuth令牌使用`Authorization: Bearer <token>`。先前的CLI仅提供`auth set-token`（Bearer默认），并在发布后修复以添加`auth set-api-key`以及`config.go`中的原始头路径（`linear-auth-api-key-vs-oauth-token`）。
   - **4–9个补丁**：每个补丁一个紧凑句子，相同的实质优先形状。
   - **10+个补丁**：按类别（认证、分页、查询编码、MCP添加、助手、分类器、错误信封）进行主题总结。每个主题两到三句话，引用2–3个补丁`id`作为证据。不要内联列出所有条目。

   在部分末尾添加一个指针，以便下游代理在相关工作区域中可以钻入任何特定补丁：

   > 完整补丁详情：`$PATCHES_SOURCE`下的每个补丁文件（每个`<id>.json`是一个自包含的补丁；遗留的单数组`.printing-press-patches.json`在`patches[]`下携带相同的字段）。

不要传递单独的“这是一个重新打印”标记。novel-features子代理在每次打印时都无条件运行，并通过其自己的发现片段发现先前研究。阶段A填充的路径是它检查的路径；Pass 2(d)在存在先前的`research.json`时始终触发。

库保留合同由`/printing-press`阶段5.6（“提升至库”）拥有，而不是由此技能拥有。当现有库在其清单中`novel_features > 0`（或手写文件在`internal/cli/`、`internal/syncer/`或`internal/store/`下）时，阶段5.6首先运行`"$PRINTING_PRESS_BIN" regen-merge "$LIB_TARGET" --fresh "$CLI_WORK_DIR"
--json`以决定新鲜树是否重建了先前的novels。如果新鲜树包含所有先前的novel工作，阶段5.6使用交换路径，并将生成文件版本差异视为预期的覆盖。否则它通过`regen-merge --apply`路由促进，以便仍然独特的手动编写的novels在重新打印中幸存，而真实的`NOVEL-COLLISION`/缺失引用情况将暂停审查。这尊重了**手写编辑必须可regen-merge**部分在`/printing-press`阶段3中的指导。如果未来对该阶段的编辑改变了路由规则，请在同一PR中更新此段落——重新打印技能是触发它的主要入口点。

在手交前，比较重新生成的清单文件与跟踪发布的树。如果`$LIB_TARGET/manifest.json`或
`$LIB_TARGET/tools-manifest.json`存在，将每个文件与`$CLI_WORK_DIR`下重新生成的对应文件进行比较，并在手交提示中显示非空差异。将差异视为协调检查点，而不是自动覆盖批准：操作员必须决定是否保留跟踪的手动编辑，将其折叠到规范/研究输入中，或有意接受重新生成的值。不要在跟踪清单字段、工具元数据或描述将被丢弃时静默继续。

归因也由`/printing-press`拥有：手交运行与相同的API缩写生成，生成/促进路径必须保留现有库清单的永久`creator`，同时在它们不同时将重新打印者添加到`contributors[]`。不要通过手动编辑`creator`、`contributors[]`、README署名、SKILL `author:`或NOTICE来修复——使用当前的Printing Press二进制重新运行，以便清单优先的守卫一致地重写工作树和促进树。

## 手交后

Printing Press流程驱动其余部分。不要总结其工作——让用户看到实时阶段。

如果`/printing-press`因子代理的预检HALT（简报缺少具体的`Users` / `Top Workflows`内容）而停止，则重用的先前简报早于子代理所需的架构。建议在阶段C选择**重新研究**。
