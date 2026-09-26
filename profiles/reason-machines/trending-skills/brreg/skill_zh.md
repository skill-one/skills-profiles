# 挪威商业注册 (Brreg)

> 由 [ara.so](https://ara.so) 提供 — 2026每日技能集

通过 Brønnøysundregistrene 官方开放API，搜索和检索挪威所有注册公司信息。

## 使用场景

- 当用户询问关于挪威公司时
- 当在挪威搜索公司信息时
- 当查询组织编号 (organisasjonsnummer) 时
- 当按名称、地点、行业或其他标准查找公司时
- 当检查公司状态（破产、解散等）时

## API基础URL

```
https://data.brreg.no/enhetsregisteret/api
```

## 关键端点

### 搜索公司 (Enheter)

```bash
curl "https://data.brreg.no/enhetsregisteret/api/enheter?navn=SEARCH_TERM&size=20"
```

**常用参数:**
| 参数 | 描述 |
|-----------|-------------|
| `navn` | 公司名称（部分匹配） |
| `organisasjonsnummer` | 9位组织编号（多个用逗号分隔） |
| `organisasjonsform` | 组织类型：AS、ENK、NUF、ANS、DA等 |
| `naeringskode` | 行业代码（NACE） |
| `kommunenummer` | 4位市镇代码 |
| `postadresse.postnummer` | 邮政编码 |
| `forretningsadresse.postnummer` | 营业地址邮政编码 |
| `konkurs` | true/false - 破产状态 |
| `underAvvikling` | true/false - 解散状态 |
| `registrertIMvaregisteret` | true/false - 增值税注册 |
| `fraAntallAnsatte` | 最少员工数 |
| `tilAntallAnsatte` | 最多员工数 |
| `fraRegistreringsdatoEnhetsregisteret` | 注册日期从 (YYYY-MM-DD) |
| `tilRegistreringsdatoEnhetsregisteret` | 注册日期至 (YYYY-MM-DD) |
| `size` | 每页结果数（默认：20，最大深度：10000） |
| `page` | 页码（0索引） |

### 通过组织编号获取公司

```bash
curl "https://data.brreg.no/enhetsregisteret/api/enheter/123456789"
```

### 搜索子实体 (Underenheter)

分支机构及部门：

```bash
curl "https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=123456789"
```

### 获取组织形式

列出所有有效组织类型：

```bash
curl "https://data.brreg.no/enhetsregisteret/api/organisasjonsformer"
```

**常用组织形式:**
| 代码 | 描述 |
|------|-------------|
| AS | 股份有限公司（私营公司） |
| ASA | 股份有限公司（上市公司） |
| ENK | 个人企业（独资企业） |
| NUF | 挪威注册的外国企业（外国企业） |
| ANS | 责任公司（普通合伙企业） |
| DA | 共同责任公司（连带责任合伙企业） |
| SA | 合作社 |
| STI | 基金会 |

### 获取最新更新

追踪新注册和变更：

```bash
curl "https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter?dato=2024-01-01T00:00:00.000Z"
```

## 批量下载

完整数据集（每晚约05:00 AM更新）：

| 格式 | URL |
|--------|-----|
| JSON (gzip压缩) | https://data.brreg.no/enhetsregisteret/api/enheter/lastned |
| CSV | https://data.brreg.no/enhetsregisteret/api/enhetsregisteret/api/enheter/lastned/csv |
| Excel | https://data.brreg.no/enhetsregisteret/api/enhetsregisteret/api/enhetsregisteret/api/enhetsregisteret/lastned/regneark |

## 示例查询

### 查找奥斯陆所有员工超过50人的AS公司

```bash
curl "https://data.brreg.no/enhetsregisteret/api/enheter?organisasjonsform=AS&kommunenummer=0301&fraAntallAnsatte=50&size=100"
```

### 搜索科技公司

```bash
curl "https://data.brreg.no/enhetsregisteret/api/enheter?navn=tech&size=50"
```

### 查找今年注册的公司

```bash
curl "https://data.brreg.no/enhetsregisteret/api/enheter?fraRegistreringsdatoEnhetsregisteret=2024-01-01&size=100"
```

### 获取某公司的所有子公司

```bash
curl "https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=923609016"
```

## 响应格式

响应为HAL+JSON格式，`_embedded` 包含结果，`page` 包含分页信息：

```json
{
  "_embedded": {
    "enheter": [
      {
        "organisasjonsnummer": "123456789",
        "navn": "Company Name AS",
        "organisasjonsform": {
          "kode": "AS",
          "beskrivelse": "Aksjeselskap"
        },
        "antallAnsatte": 50,
        "forretningsadresse": {
          "adresse": ["Street 1"],
          "postnummer": "0150",
          "poststed": "OSLO",
          "kommune": "OSLO",
          "kommunenummer": "0301"
        },
        "naeringskode1": {
          "kode": "62.010",
          "beskrivelse": "编程服务"
        }
      }
    ]
  },
  "page": {
    "size": 20,
    "totalElements": 150,
    "totalPages": 8,
    "number": 0
  }
}
```

## 注意事项

- API免费且开放（NLOD许可）
- 公开数据无需认证
- 高频使用可能有限速
- 每次查询结果限制为10,000条（完整数据请使用批量下载）
- 工作时间内持续更新数据

## 文档

- 官方API文档：https://data.brreg.no/enhetsregisteret/api/dokumentasjon/en/index.html
- OpenAPI规范：https://raw.githubusercontent.com/brreg/openAPI/master/specs/enhetsregisteret.json
