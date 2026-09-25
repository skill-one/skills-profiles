# Ansible Automation

## 目录

- [概述](#概述)
- [使用场景](#使用场景)
- [快速入门](#快速入门)
- [参考指南](#参考指南)
- [最佳实践](#最佳实践)

## 概述

使用 Ansible playbooks、roles 和动态库存管理，在多台服务器上自动化基础设施配置、配置管理和应用程序部署。

## 使用场景

- 配置管理
- 应用程序部署
- 基础设施补丁和更新
- 多服务器编排
- 云实例配置
- 容器管理
- 数据库管理
- 安全合规自动化

## 快速入门

最小工作示例：

```yaml
# site.yml - 主 playbook
---
- name: 部署应用程序堆栈
  hosts: all
  gather_facts: yes
  serial: 1  # 滚动部署

  pre_tasks:
    - name: 显示主机信息
      debug:
        var: inventory_hostname
      tags: [always]

  roles:
    - common
    - docker
    - application

  post_tasks:
    - name: 验证部署
      uri:
        url: "http://{{ inventory_hostname }}:8080/health"
        status_code: 200
      retries: 3
      delay: 10
// ... (参考参考指南获取完整实现)
```

## 参考指南

`references/` 目录中的详细实现：

| 指南 | 内容 |
|---|---|
| [Playbook 结构和最佳实践](references/playbook-structure-and-best-practices.md) | Playbook 结构和最佳实践 |
| [库存和变量](references/inventory-and-variables.md) | 库存和变量 |
| [Ansible 部署脚本](references/ansible-deployment-script.md) | Ansible 部署脚本 |
| [配置模板](references/configuration-template.md) | 配置模板 |

## 最佳实践

### ✅ 应该

- 使用 roles 实现模块化
- 实现适当的错误处理
- 使用模板进行配置
- 利用 handlers 实现幂等性
- 使用 serial 部署进行滚动更新
- 实现健康检查
- 将库存存储在版本控制中
- 使用 vault 存储敏感数据

### ❌ 不应该

- 无条件使用 command/shell
- 无模板复制文件
- 首先以检查模式运行
- 在库存中混合环境
- 硬编码值
- 忽略错误处理
- 使用 shell 执行简单任务
