# 库存检查（步骤 8）

ECS 规格已在步骤 6 从实时有货清单选定，`INSTANCE_TYPE` 与 `ZONE_ID` 均已确认，本步骤直接沿用、**跳过 ECS 库存查询**。
含 RDS 时，验证 RDS 规格在 ECS 有货可用区是否支持，取交集确定最终 `ZONE_ID`。

---

## RDS 可用区验证（仅含 RDS 时）

对 ECS 有货的可用区，验证所选 RDS 规格是否支持：

```bash
aliyun rds DescribeAvailableClasses \
  --RegionId "$REGION" --ZoneId "$ZONE_ID" \
  --Engine MySQL --EngineVersion 8.0 \
  --Category Basic --DBInstanceStorageType cloud_essd \
  --CommodityCode bards --OrderType BUY
```

返回中包含 `$DB_INSTANCE_CLASS` → 该区 RDS 可用。取 ECS ∩ RDS 可用区交集。

---

## 判断逻辑

| 结果 | 动作 |
|------|------|
| 无 RDS | 直接沿用步骤 6 的 `ZONE_ID`，继续 |
| 含 RDS 且交集非空 | 记录交集中的 `ZONE_ID`（取第一个），继续 |
| 含 RDS 且交集为空 | 给用户 2–3 个替代方案（换 RDS/ECS 规格、换地域），附代价说明 |

---

## 替代方案建议

交集为空时 Agent 自行查询替代方案的可用性：
- 回到步骤 6 换一个 ECS 有货规格
- 回到步骤 5 换一个 RDS 规格
- 换地域（如 `cn-shanghai`、`cn-beijing`），重跑受影响的步骤

> 上述任一改动都会改变步骤 5/6 的选择，因此继续步骤 8/9 前须重跑步骤 7，用新选择重新生成模板。
