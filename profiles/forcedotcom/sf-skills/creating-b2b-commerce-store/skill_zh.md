# 创建 Commerce B2B 店铺

交互式工作流程，用于在 Salesforce 中创建 Commerce B2B 店铺，并将自动生成的店铺元数据检索到您的存储库中。

## 关键概念

Commerce B2B = 店铺（后端数据）+ 店铺（前端元数据）。**必须先在组织中创建店铺**以自动生成店铺。切勿手动创建店铺元数据。

> 参考：[店铺与店铺参考](references/store-vs-storefront.md)

## 何时使用此技能

在用户请求以下内容时触发：
- "创建 B2B 商务店铺"
- "构建 Commerce 店铺"
- "设置 Commerce B2B"
- "创建 B2B 商务"
- "检索 Commerce 店铺元数据"
- "部署 B2B 店铺"

## 始终适用的规则

1. **始终遵循交互式流程。** 切勿跳过步骤。每个步骤在继续之前都需要用户确认。

2. **切勿手动创建店铺元数据。** Commerce 设置向导会生成数百个配置值。手动创建将失败。

3. **始终在检索前列出站点。** 店铺名称会添加下划线和数字后缀（例如，"我的 B2B 店铺" → "My_B2B_Store1"）。让用户从实际列表中选择。

4. **始终使用 `--json` 标志。** 在所有 Salesforce CLI 命令中包含 `--json` 以获取可解析的输出。

## 交互式工作流程：7 步骤

### 第 1 步：解释 Commerce B2B 概念

**代理解释：** Commerce 包含店铺（数据）+ 店铺（元数据）。必须先创建店铺。

> 参考：[店铺与店铺参考](references/store-vs-storefront.md)

---

### 第 2 步：指导用户创建 B2B 店铺

**代理提供以下步骤：**

1. 导航到 **设置 → 商务 → 店铺**
   - 或：**应用启动器 → 商务 → 创建店铺**

2. 点击 **"创建店铺"** 或 **"设置新店铺"**

3. 选择 **"Commerce 店铺"** 作为店铺类型

4. 按照向导：
   - **店铺名称**：选择描述性名称（例如，"我的 B2B 店铺"）
     - 重要提示：空格将在文件夹名称中转换为下划线
   - **站点 URL**：站点的唯一 URL 名称

5. 完成向导 - 它会创建：
   - WebStore 记录
   - 默认的购买组和授权策略
   - 关联的 Digital Experience (LWR 站点)

6. 可选：配置支付网关、税务提供者和运输

**代理随后询问：**
"您是否已在您的组织中完成创建 B2B 店铺？准备好时回复 'yes' 并提供您使用的店铺名称。"

---

### 第 3 步：获取用户确认

**代理等待：** 用户确认和店铺名称

**代理验证：** 店铺名称格式（不能包含特殊字符，空格将显示为下划线）

**代理确认：** "太好了！让我列出您组织中的可用店铺..."

---

### 第 4 步：列出可用 LWR 站点

**代理执行：**
```bash
sf org list metadata --metadata-type DigitalExperienceConfig --json
```

**代理应：**
- 解析 JSON 输出以提取站点名称
- 以编号列表显示
- 解释命名规则（下划线、数字后缀）

**示例输出：**
```
可用的 Digital Experience 站点：
1. My_B2B_Store1
2. Partner_Portal
3. Customer_Community
```

---

### 第 5 步：让用户选择店铺

**代理询问：**
"哪个站点对应您的 B2B 店铺？请选择站点名称："

**代理验证：** 选择是否与可用站点匹配

**代理确认：** "好的！我将为 [站点名称] 检索元数据..."

---

### 第 6 步：检索店铺元数据

**代理执行：**
```bash
sf project retrieve start -m DigitalExperienceBundle:site/<选择的站点名称> --json
```

**代理应：**
- 显示检索进度
- 确认检索成功
- 列出检索的目录结构

**预期输出：**
```
检索成功：force-app/main/default/digitalExperiences/site/My_B2B_Store1/
├── My_B2B_Store1.digitalExperience-meta.xml
├── sfdc_cms__view/ (主页、当前购物车、detail_*, list_*, 等.)
├── sfdc_cms__site/
├── sfdc_cms__route/
└── [其他 sfdc_cms__* 目录]
```

---

### 第 7 步：提供后续步骤

**代理提供：**

✅ **元数据检索成功！**

**后续步骤：**
- 使用自定义 LWC 或品牌更改进行定制
- 部署：`sf project deploy start --source-dir force-app/main/default/digitalExperiences/site/My_B2B_Store1/ --json`

**资源：** [DigitalExperienceBundle 文档](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_digitalexperiencebundle.htm)、[B2B 商务指南](https://developer.salesforce.com/docs/atlas.en-us.b2b_commerce_dev_guide.meta/b2b_commerce_dev_guide/)

---

## 参考

- **[store-vs-storefront.md](references/store-vs-storefront.md)** - 关于店铺与店铺的技术细节、源代码控制以及为何手动创建失败

---

## 注意

**先创建店铺（生成店铺）→ 检索 → 定制**
