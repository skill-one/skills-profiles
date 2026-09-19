# 规格选择（步骤 6）

拓扑固定为单机（1 ECS + EIP + VPC + SG）。规格从**当前地域实时有货**的清单里选。

---

## 拉取实时有货规格

先查该地域按量付费真实有货的规格 ID：

```bash
aliyun ecs DescribeAvailableResource \
  --RegionId "$REGION" \
  --DestinationResource InstanceType \
  --InstanceChargeType PostPaid
```

从 `AvailableZones.AvailableZone[]` 收集 `StatusCategory` 为 `WithStock` 的
`SupportedResources.SupportedResource[].Value`（规格 ID），并记下其所在 `ZoneId`（一个规格可能多区有货）。

再补齐每个规格的 vCPU / 内存：

```bash
aliyun ecs DescribeInstanceTypes --RegionId "$REGION"
```

按 `InstanceTypeId` 关联，取 `CpuCoreCount`（vCPU）与 `MemorySize`（GiB）。

---

## 降噪过滤

只呈现适合轻量单机部署的常规规格，滤掉噪声：

- **保留**：通用型、计算型、内存型、共享/突发性能型（`ecs.g*` / `ecs.c*` / `ecs.r*` / `ecs.e*` / `ecs.u*` / `ecs.t*` / `ecs.s*` 等）。
- **排除**：GPU / FPGA（`ecs.gn*`、`ecs.vgn*`、`ecs.f*`）、裸金属（`ecs.ebm*`、含 `.metal`）、
  vCPU > 16 或内存 > 32 GiB 的超大规格、非 x86 特殊架构。
- 保留结果去重后按 vCPU→内存升序排序，逐条完整呈现。

若过滤后为空（该地域常规规格均无货），按「步骤 8 · 替代方案」给出换地域/换规格建议。

---

## 呈现与选择（AskUserQuestion）

把过滤排序后的规格逐条列出，每条展示 `规格 ID · vCPU/内存`，让用户选一个。
价格不在此展示（以步骤 9 实时询价为准），避免呈现会漂移的估值。

---

## 产出

- `INSTANCE_TYPE`：用户选择的 ECS 规格 ID
- `ZONE_ID`：该规格有货的可用区（多区有货时取其一）

---

## 注意事项

- 呈现的规格均来自实时有货结果，用户选定即已通过库存校验；步骤 8 直接复用，不重复查 ECS 库存。
- 实际价格以步骤 9 询价结果为准。
