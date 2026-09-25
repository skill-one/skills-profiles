# Apache Airflow DAG 模式

适用于 Apache Airflow 的生产就绪模式，包括 DAG 设计、算子、传感器、测试和部署策略。

## 使用此技能的场景

- 使用 Airflow 创建数据管道编排
- 设计 DAG 结构和依赖关系
- 实现自定义算子和传感器
- 本地测试 Airflow DAG
- 在生产环境中设置 Airflow
- 调试失败的 DAG 运行

## 核心概念

### 1. DAG 设计原则

| 原则       | 描述                         |
| --------------- | ----------------------------------- |
| **幂等性**  | 运行两次产生相同结果  |
| **原子性**      | 任务成功或完全失败    |
| **增量性**      | 仅处理新/已更改的数据       |
| **可观察性**  | 每个步骤的日志、指标、警报 |

### 2. 任务依赖

```python
# 线性
task1 >> task2 >> task3

# 分支
task1 >> [task2, task3, task4]

# 合并
[task1, task2, task3] >> task4

# 复杂
task1 >> task2 >> task4
task1 >> task3 >> task4
```

## 快速入门

```python
# dags/example_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(hours=1),
}

with DAG(
    dag_id='example_etl',
    default_args=default_args,
    description='示例 ETL 管道',
    schedule='0 6 * * *',  # 每天早上 6 点
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', '示例'],
    max_active_runs=1,
) as dag:

    start = EmptyOperator(task_id='start')

    def extract_data(**context):
        execution_date = context['ds']
        # 提取逻辑
        return {'records': 1000}

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
    )

    end = EmptyOperator(task_id='end')

    start >> extract >> end
```

## 详细模式和工作示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

### 应该做

- **使用 TaskFlow API** - 代码更简洁，自动 XCom
- **设置超时** - 防止僵尸任务
- **使用 `mode='reschedule'`** - 对于传感器，释放工作节点
- **测试 DAG** - 单元测试和集成测试
- **幂等任务** - 安全重试

### 不应该做

- **不要使用 `depends_on_past=True`** - 创建瓶颈
- **不要硬编码日期** - 使用 `{{ ds }}` 宏
- **不要使用全局状态** - 任务应该是无状态的
- **不要盲目跳过 catchup** - 了解影响
- **不要在 DAG 文件中放置重逻辑** - 从模块导入
