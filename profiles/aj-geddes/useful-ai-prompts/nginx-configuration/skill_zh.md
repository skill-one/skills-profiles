# Nginx 配置

## 目录

- [概述](#概述)
- [使用场景](#使用场景)
- [快速入门](#快速入门)
- [参考指南](#参考指南)
- [最佳实践](#最佳实践)

## 概述

掌握 Nginx 配置，为生产级 Web 服务器、反向代理、负载均衡、SSL 终端、缓存和 API 网关模式进行高级性能调优。

## 使用场景

- 反向代理设置
- 后端服务之间的负载均衡
- SSL/TLS 终端
- HTTP/2 和 gRPC 支持
- 缓存和压缩
- 流量限制和 DDoS 保护
- URL 重写和路由
- API 网关功能

## 快速入门

最小工作示例：

```nginx
# /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
worker_rlimit_nofile 65535;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志记录
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    log_format upstream_time '$remote_addr - $remote_user [$time_local] '
                            '"$request" $status $body_bytes_sent '
                            '"$http_referer" "$http_user_agent" '
// ... (参考指南中提供完整实现)
```

## 参考指南

`references/` 目录中的详细实现：

| 指南 | 内容 |
|---|---|
| [生产环境 Nginx 配置](references/production-nginx-configuration.md) | 生产环境 Nginx 配置 |
| [带负载均衡的 HTTPS 服务器](references/https-server-with-load-balancing.md) | 带负载均衡的 HTTPS 服务器 |
| [Nginx 配置脚本](references/nginx-configuration-script.md) | Nginx 配置脚本 |
| [Nginx 监控配置](references/nginx-monitoring-configuration.md) | Nginx 监控配置 |

## 最佳实践

### ✅ 应该做

- 使用 HTTP/2 提高性能
- 启用强密码的 SSL/TLS
- 实施适当的缓存策略
- 使用上游连接池
- 使用 stub_status 或 prometheus 进行监控
- 设置流量限制防止滥用
- 添加安全头部
- 使用 least_conn 负载均衡
- 将错误日志与访问日志分开

### ❌ 不应该做

- 禁用 gzip 压缩
- 使用弱密码的 SSL
- 缓存经过身份验证的响应
- 允许直接访问后端
- 忽略上游健康检查
- 未重定向的情况下混合 HTTP 和 HTTPS
- 生产环境中使用默认错误页面
- 缓存敏感的用户数据
