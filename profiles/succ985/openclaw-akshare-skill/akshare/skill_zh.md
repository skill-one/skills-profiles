# AkShare - 中国金融数据

## 概述

AkShare 是一个免费、开源的 Python 库，用于访问中国金融市场数据。本指南提供了从中国交易所（包括上海证券交易所、深圳证券交易所、香港交易所等）获取数据的指导。

## 快速入门

安装 AkShare：
```bash
pip install akshare
```

基本股票行情：
```python
import akshare as ak
df = ak.stock_zh_a_spot_em()  # 实时 A 股数据
```

## 股票数据

### A 股

**实时行情：**
```python
# 所有 A 股实时数据
df = ak.stock_zh_a_spot_em()

# 单只股票实时行情
df = ak.stock_zh_a_spot()
```

**历史数据：**
```python
# 历史日线数据
df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", end_date="20241231", adjust="qfq")
```

**股票列表：**
```python
# 获取所有 A 股股票列表
df = ak.stock_info_a_code_name()
```

### 港股

**实时行情：**
```python
df = ak.stock_hk_spot_em()
```

**历史数据：**
```python
df = ak.stock_hk_hist(symbol="00700", period="daily", adjust="qfq")
```

### 美股

**实时数据：**
```python
df = ak.stock_us_spot_em()
```

## 期货数据 (期货)

**实时期货：**
```python
# 商品期货
df = ak.futures_zh_spot()
```

**历史期货：**
```python
df = ak.futures_zh_hist_sina(symbol="IF0")
```

## 基金数据 (基金)

**基金列表：**
```python
df = ak.fund_open_fund_info_em()
```

**基金历史数据：**
```python
df = ak.fund_open_fund_info_em(fund="000001", indicator="单位净值走势")
```

## 宏观经济指标 (宏观)

**GDP 数据：**
```python
df = ak.macro_china_gdp()
```

**CPI 数据：**
```python
df = ak.macro_china_cpi()
```

**PMI 数据：**
```python
df = ak.macro_china_pmi()
```

## 常用参数

**周期 (周期)：**
- `daily` - 日线
- `weekly` - 周线
- `monthly` - 月线

**复权 (复权)：**
- `qfq` - 前复权
- `hfq` - 后复权
- `""` - 不复权

## 小贴士

1. **数据缓存**：AkShare 不缓存数据，如有需要请自行实现缓存
2. **速率限制**：注意请求频率，避免被屏蔽
3. **数据格式**：返回 pandas DataFrame，易于处理
4. **错误处理**：可能发生网络错误，请实现重试逻辑

## 参考

有关完整的 API 文档和高级用法，请参阅：
- [references/akshare_api.md](references/akshare_api.md) - 详细 API 参考
- [references/common_functions.md](references/common_functions.md) - 常用函数
- [https://akshare.akfamily.xyz/](https://akshare.akfamily.xyz/) - 官方文档
