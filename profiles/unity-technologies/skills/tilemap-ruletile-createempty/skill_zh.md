# Tilemap 规则瓦片 创建空瓦片

## 工作流程

### 第一步：验证无精灵输入
**等待** - 确认用户未指定任何精灵或精灵表。此技能仅用于创建空的规则瓦片。如果用户指定了精灵或精灵表，请使用 `tilemap-ruletile-createfromsegment` 技能。

### 第二步：确定规则瓦片类型
根据用户请求，确定要创建的规则瓦片类型：
- **RuleTile**：标准矩形网格
- **HexagonalRuleTile**：六边形网格布局
- **IsometricRuleTile**：等距网格布局

### 第三步：创建空的 TilingRules
对于每个 TilingRule，确保精灵数组中有一个 `null` 条目。

## 分支逻辑（规则瓦片类型）

### 路径 A：RuleTile
- 使用来自 `resources/ruletile.md` 的模板。

### 路径 B：HexagonalRuleTile
- 使用来自 `resources/hexagonalruletile.md` 的模板。

### 路径 C：IsometricRuleTile
- 创建适用于等距布局的空规则，并设置正确的相邻位置。

## 重要提示

- **TilingRuleOutput.Neighbor.This**：用于识别相同的规则瓦片（匹配相邻位置）。
- **TilingRuleOutput.Neighbor.NotThis**：除非用户明确指定忽略特定位置的瓦片，否则请勿使用。
