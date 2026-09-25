# 在 Experience Cloud 网站上嵌入消息小部件

将现有的嵌入式消息（MIAW）部署连接到 Experience Cloud 网站上，通过检索网站的包（LWR `DigitalExperienceBundle` 或 Aura `ExperienceBundle`），修补主页 JSON 以放置 `experience_messaging:embeddedMessaging` 组件，将包暂存到本地项目，部署它，发布网站并验证访客访问。

该操作是幂等的：如果组件已经存在，它将就地更新（保留其 `id`），因此使用不同的 ESD 坐标重新运行可以干净地更新。

## 范围

- **在范围内**：检测 LWR 与 Aura 包类型；搭建网站模板所需的缺失 LWR 模板路由（例如 `too-many-requests`）；修补所有 `sfdc_cms__themeLayout/*/content.json` 文件以在页脚区域（全局位置）插入或更新嵌入式消息组件；将包暂存到 `force-app`；异步部署并轮询；解决 `Network.Name` 并发布网站；访客 URL 烟雾测试；手动 Experience Builder 回退使用深度链接。
- **超出范围**：创建 `EmbeddedServiceConfig`（嵌入式服务部署）本身 — 使用 `service-digital-engagement-deployment-configure`；创建 `MessagingChannel` — 使用 `service-digital-engagement-channel-configure`；创建 Experience Cloud 网站本身 — 使用 `experience-lwr-site-generate`；为非 Experience 网站生成一个独立的 JS 片段。

---

## 澄清问题

在执行之前，如果还不清楚，请询问用户：

- **网站名称？** Experience Cloud 网站的 `DeveloperName`（在 `digitalExperiences/site/<siteName>/` 下或 `experiences/<siteName>/` 下的元数据文件夹名称）。
- **部署坐标？** `deploymentName`（嵌入式服务部署 `DeveloperName`）、`scrtUrl` 和 `siteEndpoint`（Experience 网站基本 URL）。这三个都来自发布的 `EmbeddedServiceConfig` — 如果未提供，则从 `service-digital-engagement-deployment-configure` 输出中获取。
- **目标 org 别名？** 用于 `sf` 命令。
- **URL 路径前缀？** 网站的 `UrlPathPrefix`（发布时用于解析 `Network.Name`，验证时用于访问访客 URL）。

---

## 必需的输入

在继续之前收集或推断：

- **网站名称** — 网站的 `DeveloperName`
- **部署名称** — `EmbeddedServiceConfig` 的 `DeveloperName`
- **scrtUrl** — 部署的 SCRT2 端点 URL
- **siteEndpoint** — Experience 网站的基本 URL
- **目标 org 别名**
- **URL 路径前缀** — 网站的公共 URL 路径段（例如 `esw-site`）

在写入时应用于组件属性的默认值：

- `isExpSiteAuthMode`: `false`
- `hideChatButtonOnLoad`: `"Default"`
- `clientVersion`: `"WebV1"`

---

## 工作流程

步骤是按顺序执行的。如果任何自动步骤失败，请继续手动回退（阶段 6），并且不要声称小部件是“在线的”，直到访客 URL 烟雾测试返回 `200` 或用户确认手动发布。

### 阶段 1 — 检测包类型

1. **将两个候选包检索到 `<retrieve-dir>`**。脚本仅执行确定性路径检查，因此检索调用必须首先运行：

   ```bash
   sf project retrieve start --metadata "DigitalExperienceBundle:site/<siteName>" \
     --target-org <org-alias> --target-metadata-dir <retrieve-dir>
   sf project retrieve start --metadata "ExperienceBundle:<siteName>" \
     --target-org <org-alias> --target-metadata-dir <retrieve-dir>
   ```

   任何调用都可能返回“未找到元数据”——这是预期的；缺失的包仅意味着网站是另一种类型。

2. **运行 `scripts/detect_bundle_type.sh <retrieve-dir> <siteName>`**。它向标准输出发出恰好一个标记：

   - `LWR` → 存在 LWR 标记文件（`digitalExperiences/site/<siteName>/sfdc_cms__view/home/content.json`）。转到阶段 2。
   - `AURA` → 存在 Aura 标记文件（`experiences/<siteName>/views/homeGuestLayout.json`）。转到阶段 3。
   - `UNKNOWN`（退出代码 1）→ 两个标记都不存在。跳转到阶段 6 的手动回退。

阅读 `references/bundle_detection.md` 以获取检索命令形状和故障排除信息。

### 阶段 2 — 修补 LWR 包

3. **在修补之前搭建任何缺失的 LWR 模板路由**（通常 `too-many-requests`）——缺失的路由会导致部署失败。路由+视图搭建由 `experience-lwr-site-generate` 拥有（请参阅其 `configure-content-route.md`、`configure-content-view.md` 和 `handle-component-and-region-ids.md`）。将搭建委托给该技能；此技能仅提供与消息相关的上下文（部署抱怨的路由，并确认搭建的对应对解决特定的部署错误）。请参阅 `references/lwr_route_scaffolding.md` 以获取委托指针。

4. **通过运行修补所有主题布局文件**：

   ```bash
   scripts/patch_lwr_bundle.sh \
     <retrieve-dir>/digitalExperiences/site/<siteName> \
     <deploymentName> <scrtUrl> <siteEndpoint>
   ```

   脚本迭代每个 `sfdc_cms__themeLayout/*/content.json` 文件。对于每个文件，它在 `.contentBody.component.children[]` 中定位 `footer` 区域，进入现有的 `community_layout:section` 包装器的内部插槽区域，并就地更新现有的 `experience_messaging:embeddedMessaging` 组件（保留其 `id`）或追加一个新鲜组件节点。针对主题布局页脚使小部件全局（每个页面的浮动覆盖层），相当于 Aura 主题Footer放置。请参阅 `references/lwr_patch.md` 以获取 JSON 形状和如何验证。

5. 继续转到阶段 4。

### 阶段 3 — 修补 Aura 包

6. **通过运行修补主页访客布局**：

   ```bash
   scripts/patch_aura_bundle.sh \
     <retrieve-dir>/experiences/<siteName>/views/homeGuestLayout.json \
     <deploymentName> <scrtUrl> <siteEndpoint>
   ```

   脚本迭代 `.regions[]`，选择第一个 `.components[]` 非空的区域，递归遍历任何 `forceCommunity:section` 包装器，并就地更新现有的 `.componentName == "experience_messaging:embeddedMessaging"` 组件（保留 `id`）或追加一个新鲜的 `forceCommunity:section` 包装器。Aura 使用 `componentName` / `componentAttributes`（不是 `definition` / `attributes`），并且没有 `dxpStyle`。请参阅 `references/aura_patch.md` 以获取 JSON 形状和验证步骤。

7. 继续转到阶段 4。

### 阶段 4 — 暂存和部署

8. **将修改后的包复制到项目的默认包中**。使用 `cp -R` 以确保未更改的文件与修改后的文件一起传输：

   - LWR: `cp -R <retrieve-dir>/digitalExperiences force-app/main/default/`
   - Aura: `cp -R <retrieve-dir>/experiences force-app/main/default/` **并且还必须复制** 兄弟文件 `<siteName>.site-meta.xml` — Aura 部署没有它将被拒绝。

9. **异步部署并轮询**：

    ```bash
    sf project deploy start --source-dir force-app/main/default \
      --target-org <org-alias> --async
    ```

    每 15 秒轮询一次，最多 10 分钟：

    ```bash
    sf project deploy report --job-id <job-id> --target-org <org-alias>
    ```

    状态为 `Succeeded`、`Failed`、`SucceededPartial` 或 `Canceled` 时停止。失败时，显示部署报告并且不要继续发布。请参阅 `references/deploy_and_publish.md` 以获取完整的轮询循环和常见失败模式。

### 阶段 5 — 发布和验证

10. **解析 `Network.Name`**。`Network.Name` 经常与网站的 `DeveloperName` 不同，因此通过 URL 路径前缀查询它而不是猜测：

    ```bash
    sf data query --query \
      "SELECT Name FROM Network WHERE UrlPathPrefix='<urlPath>' LIMIT 1" \
      --target-org <org-alias>
    ```

11. **使用解析的名称发布社区**：

    ```bash
    sf community publish --name "<resolved-Name>" --target-org <org-alias>
    ```

12. **通过访问公共 URL 进行烟雾测试访客访问**：

    ```bash
    curl -sL -o /dev/null -w "%{http_code}" \
      https://<domainHostname>/<urlPath>
    ```

    只有在响应为 `200` 时才报告成功。

### 阶段 6 — 手动回退

13. 如果任何自动步骤失败（包无法检测、修补写入被阻止、部署失败、发布失败或访客 URL 不是 `200`），请打印 Experience Builder 深度链接和 `references/manual_fallback.md` 中的逐字指令。**不要**声称小部件是“在线的”，直到用户确认。

    深度链接是：

    ```text
    https://<MyDomain>.lightning.force.com/sfsites/picasso/core/config/commeditor.apexp?...networkId=<Network.Id>
    ```

    通过 `sf org display --target-org <org-alias>` 解析 `<MyDomain>`，通过：

    ```bash
    sf data query --query \
      "SELECT Id FROM Network WHERE UrlPathPrefix='<urlPath>' LIMIT 1" \
      --target-org <org-alias>
    ```

    解析 `<Network.Id>`。

    **不要**硬编码任何值。指示用户打开 Experience Builder，将嵌入式消息组件拖放到目标页面，从属性面板中选择部署，然后点击发布。

---

## 规则 / 约束

| 约束 | 理由 |
|-----------|-----------|
| 从检索输出检测包类型，不要假设 | LWR 和 Aura 网站需要用不同的键名修补不同的文件 |
| 更新时保留现有的组件 `id` | 确保幂等性；Experience 运行时依赖于 `id` |
| 每个新的 `id` 必须是一个全新的 UUID | 重复的 ID 会破坏布局并可能导致渲染失败 |
| LWR 使用 `definition` / `attributes`；Aura 使用 `componentName` / `componentAttributes` | 错误的键名会静默地丢弃渲染中的组件 |
| LWR `community_layout:section` `sectionConfig` 作为一个 JSON 字符串存在于 `.attributes` 中（不是顶级属性，也不是嵌套对象） | 顶级放置违反了 `additionalProperties: false` 的模式约束；序列化器也期望一个字符串而不是一个对象 |
| Aura 兄弟 `<siteName>.site-meta.xml` 必须与包一起复制 | 没有它部署将被拒绝 |
| 轮询异步部署；不要火并忘记 | 只有在部署成功后才能运行发布 |
| 从 `UrlPathPrefix` 解析 `Network.Name`，不要重用网站 `DeveloperName` | 这两个经常不同 |
| 在访客 URL 返回 `200` 或用户确认之前，不要声称“网站在线” | 发布是异步的；过早的成功报告会误导 |
| 在手动回退链接中永远不要硬编码 `MyDomain` 或 `Network.Id` | 值是 org 特定的，必须查询 |
| 幂等性：使用新的 ESD 坐标重新运行必须就地更新 | 用户在设置期间迭代 `deploymentName`、`scrtUrl`、`siteEndpoint` |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| `too-many-requests` 路由在 LWR 部署期间缺失 | 根据 `references/lwr_route_scaffolding.md` 搭建缺失的路由+视图对 |
| Aura 部署因缺少网站元数据而被拒绝 | 从检索目录复制兄弟 `<siteName>.site-meta.xml` |
| 组件追加但未渲染 | 确认区域包装器使用正确的 `type: "region"` 键，并且 Aura 组件使用 `componentName`（不是 `definition`） |
| `sf community publish` 因“社区未找到”而失败 | `Network.Name` 与网站 `DeveloperName` 不同；通过 `UrlPathPrefix` 查询解决 |
| 发布后访客 URL 返回 `403` 或 `503` | 发布是异步的 — 在 60 秒后重试烟雾测试，然后再回退到手动 |
| 重新运行添加了第二个消息组件 | 递归搜索匹配了错误的键名；组件检测必须使用 `definition`（LWR）或 `componentName`（Aura） |
| 部署成功但小部件未出现在所有页面上 | 对于 LWR，确认组件是否被注入到 `sfdc_cms__themeLayout/*/content.json` 页脚（不是 `sfdc_cms__view/home/content.json` — 那是页面特定的）。对于 Aura，确认是否修补了 `homeGuestLayout.json`（主题Footer区域）。 |
| `sectionConfig` 写作为一个对象 | 将其序列化为一个 JSON 字符串；CMS 解析器不会接受一个对象 |

---

## 验证检查清单

### 包检测
- [ ] 是否恰好找到一个 `sfdc_cms__view/home/content.json`（LWR）或 `views/homeGuestLayout.json`（Aura）？
- [ ] 如果两个都没有找到，工作流是否路由到手动回退？

### 修补正确性
- [ ] 对于 LWR，消息组件的键是否为 `definition` 和 `attributes`？
- [ ] 对于 Aura，键是否为 `componentName` 和 `componentAttributes`？
- [ ] 更新时，是否保留了现有的 `id`？
- [ ] 追加时，所有新的 `id` 值是否都是全新的 UUID？
- [ ] 对于 LWR，脚本是否修补了每个 `sfdc_cms__themeLayout/*/content.json`（不仅仅是 `home/content.json`）？
- [ ] 对于 LWR，消息节点是否出现在每个主题布局的 `footer` 区域的子树中？
- [ ] 对于 LWR，消息节点属性中的 `clientVersion` 是否设置为 `"WebV2"`？

### 部署
- [ ] 对于 Aura，是否将 `<siteName>.site-meta.xml` 与包一起复制？
- [ ] 是否轮询异步部署，直到终端状态？
- [ ] 在继续发布之前，终端状态是否为 `Succeeded` 或 `SucceededPartial`？

### 发布
- [ ] 是否通过 `UrlPathPrefix` 解析 `Network.Name`，而不是重用网站 `DeveloperName`？
- [ ] `sf community publish` 是否无错误完成？

### 验证
- [ ] 访客 URL curl 是否返回 `200`？
- [ ] 工作流是否在观察到 `200` 或用户确认手动发布之前 refrain 从声称成功？

---

## 输出预期

交付物：

- 修改后的 `sfdc_cms__themeLayout/*/content.json` 文件（每个主题布局一个）在检索目录和 `force-app/main/default/...`（LWR）；或修改后的 `homeGuestLayout.json`（Aura）
- （LWR 仅限，如果需要）新的 `sfdc_cms__route/<RouteApiName>/` + `sfdc_cms__view/<viewId>/` 对，用于任何搭建的缺失路由
- 部署 `job-id` 和最终的部署报告
- 发布确认
- 访客 URL 烟雾测试 HTTP 状态
- 失败时：Experience Builder 深度链接和手动说明

不要生成 `EmbeddedServiceConfig` 或 `MessagingChannel` 元数据 — 那些是部署和通道技能的责任。

---

## 跨技能集成

| 需要 | 委托给 |
|------|-------------|
| 创建或更新嵌入式服务部署 | `service-digital-engagement-deployment-configure` |
| 创建底层的 MIAW 消息通道 | `service-digital-engagement-channel-configure` |
| 创建 Experience Cloud LWR 网站本身 | `experience-lwr-site-generate` |
| 搭建缺失的 LWR 路由 + 视图对（例如 `too-many-requests`） | `experience-lwr-site-generate`（路由/视图创建，ID 处理） |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/bundle_detection.md` | 阶段 1 — LWR 与 Aura 检索和消除歧义 |
| `references/lwr_route_scaffolding.md` | 阶段 2 — 搭建缺失 LWR 模板路由的委托指针（由 `experience-lwr-site-generate` 拥有） |
| `references/lwr_patch.md` | 阶段 2 — `patch_lwr_bundle.sh` 的操作和如何验证其输出 |
| `references/aura_patch.md` | 阶段 3 — `patch_aura_bundle.sh` 的操作和如何验证其输出 |
| `references/deploy_and_publish.md` | 阶段 4–5 — 暂存到 `force-app`，异步部署轮询，发布，和访客 URL 烟雾测试 |
| `references/manual_fallback.md` | 阶段 6 — Experience Builder 深度链接和手动拖放发布说明 |
| `scripts/detect_bundle_type.sh` | 阶段 1 — 检测 LWR/Aura/UNKNOWN |
| `scripts/patch_lwr_bundle.sh` | 阶段 2 — LWR `content.json` 幂等修补（就地插入或更新） |
| `scripts/patch_aura_bundle.sh` | 阶段 3 — Aura `homeGuestLayout.json` 幂等修补（就地插入或更新） |
