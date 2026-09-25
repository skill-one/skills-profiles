# 分布式追踪

使用 Jaeger 和 Tempo 实现分布式追踪，以实现微服务间请求流的可见性。

## 目的

追踪分布式系统中的请求，以了解延迟、依赖关系和故障点。

## 使用场景

- 调试延迟问题
- 理解服务依赖关系
- 识别瓶颈
- 追踪错误传播
- 分析请求路径

## 详细模式和示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 最佳实践

1. **适当采样**（生产环境中为 1-10%）
2. **添加有意义的标签**（user_id, request_id）
3. **跨所有服务边界传播上下文**
4. **在跨度中记录异常**
5. **为操作使用一致的命名**
6. **监控追踪开销**（CPU 影响小于 1%）
7. **为追踪错误设置警报**
8. **实现分布式上下文**（袋装信息）
9. **使用跨度事件**记录重要里程碑
10. **记录仪器化标准**

## 与日志集成

### 相关日志

```python
import logging
from opentelemetry import trace

logger = logging.getLogger(__name__)

def process_request():
    span = trace.get_current_span()
    trace_id = span.get_span_context().trace_id

    logger.info(
        "Processing request",
        extra={"trace_id": format(trace_id, '032x')}
    )
```

## 故障排除

**没有出现追踪：**

- 检查收集器端点
- 验证网络连接
- 检查采样配置
- 查看应用程序日志

**高延迟开销：**

- 降低采样率
- 使用批量跨度处理器
- 检查导出器配置

## 相关技能

- `prometheus-configuration` - 用于指标
- `grafana-dashboards` - 用于可视化
- `slo-implementation` - 用于延迟 SLO
