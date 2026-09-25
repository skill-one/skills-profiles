# 生成模拟数据集

生成用于测试的可定制列、约束和输出格式（CSV、JSON、SQL、Python脚本）的逼真模拟数据集。创建可执行脚本或直接数据文件，以便立即使用。

**使用场景：** 创建测试数据、生成样本数据集、为开发构建逼真的模拟数据，或填充测试环境。

**参数：**
- `$PRODUCT`：产品或系统名称
- `$DATASET_TYPE`：数据类型（例如，客户反馈、交易、用户资料）
- `$ROWS`：要生成的行数（默认：100）
- `$COLUMNS`：要包含的特定列或字段
- `$FORMAT`：输出格式（CSV、JSON、SQL、Python脚本）
- `$CONSTRAINTS`：附加约束或业务规则

## 分步流程

1. **确定数据集类型** - 了解数据域
2. **定义列规范** - 名称、数据类型和值范围
3. **确定行数** - 需要多少个样本记录
4. **选择输出格式** - CSV、JSON、SQL INSERT或Python脚本
5. **应用逼真模式** - 确保数据看起来真实有效
6. **添加业务约束** - 遵循业务逻辑和关系
7. **生成或脚本数据** - 创建可执行输出
8. **验证输出** - 确保数据质量和完整性

## 模板：Python脚本输出

```python
import csv
import json
from datetime import datetime, timedelta
import random

# 配置
ROWS = $ROWS
FILENAME = "$DATASET_TYPE.csv"

# 列定义与逼真值生成器
columns = {
    "id": "auto-increment",
    "name": "first_last_name",
    "email": "email",
    "created_at": "timestamp",
    # 添加更多列...
}

def generate_dataset():
    """生成逼真模拟数据集"""
    data = []
    for i in range(1, ROWS + 1):
        record = {
            "id": f"U{i:06d}",
            # 根据列定义生成值
        }
        data.append(record)
    return data

def save_as_csv(data, filename):
    """保存数据集为CSV"""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    dataset = generate_dataset()
    save_as_csv(dataset, FILENAME)
    print(f"已生成 {len(dataset)} 条记录在 {FILENAME}")
```

## 示例数据集规范

**数据集类型：** 客户反馈

**列：**
- feedback_id (自动递增，U001、U002...)
- customer_name (逼真姓名)
- email (有效邮箱格式)
- feedback_date (过去90天的日期)
- rating (1-5星)
- category (Bug、功能请求、投诉、表扬)
- text (逼真反馈)
- product (电子产品、服装、家居)

**约束：**
- 评分偏斜：40% 5星，30% 4星，20% 3星，10% 1-2星
- Bug类别仅限1-3星评分
- 功能请求仅限3-5星评分
- 邮箱域名逼真 (gmail、yahoo、company.com)

## 输出交付物

- 可执行的Python脚本或直接数据文件
- 带有正确标题和格式的CSV文件
- 具有有效结构和类型的JSON文件
- 用于数据库填充的SQL INSERT语句
- 数据验证和约束合规
- 逼真、适合业务的值
- 数据生成逻辑文档
- 使用数据集的快速入门说明

## 输出格式

**CSV：** 扁平表格格式，易于导入到电子表格和数据库

**JSON：** 嵌套结构，适合API和NoSQL数据库

**SQL：** INSERT语句，可直接在关系数据库上执行

**Python脚本：** 可执行的生成器，用于自定义或大型数据集
