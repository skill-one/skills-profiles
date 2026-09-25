# GCP 云运行

在 GCP 上构建生产就绪的无服务器应用程序的专业技能。
涵盖云运行服务（容器化）、云运行函数（事件驱动）、冷启动优化以及使用 Pub/Sub 的事件驱动架构。

## 详细指南

执行此技能前，请阅读 [详细指南](references/detailed-guide.md)。它保留了完整流程和参考材料。将其安全性、先决条件和验证要求视为强制性。对于专注工作，加载相关章节；对于端到端工作，完整阅读指南。

## 计算 /tmp 使用情况下的内存

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'my-service'
      - '--memory=1Gi'  # 包含 /tmp 开销
      - '--image=gcr.io/$PROJECT_ID/my-service'
```

## 监控内存使用情况

```python
import psutil
import logging

def log_memory():
    memory = psutil.virtual_memory()
    logging.info(f"内存: {memory.percent}% 使用率, "
                f"{memory.available / 1024 / 1024:.0f}MB 可用")
```

### 并发=1 导致扩展瓶颈

严重性：高

情况：为请求隔离设置并发为 1

症状：
自动扩展创建大量容器实例。
流量高峰期间延迟高。
冷启动增加。
实例更多导致成本更高。

原因：
将并发设置为 1 意味着每个容器一次只能处理一个请求。在流量高峰期间：

- 100 个并发请求 = 100 个容器实例
- 每个实例都有冷启动开销
- 实例更多 = 成本更高
- 扩展需要时间，请求排队

这种情况仅应在以下情况下使用：
- 处理真正单线程
- 每个请求内存密集型
- 使用线程不安全库

推荐修复方案：

## 使用场景
当请求明确匹配上述能力和模式时，使用此技能。

## 限制
- 仅当任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必需输入、权限、安全边界或成功标准，请停止并请求澄清。
