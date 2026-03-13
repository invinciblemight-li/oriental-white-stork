# 更新日志

所有 notable 的变化都会记录在这个文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2024-01-15

### 新增

- 🎉 项目初始发布
- 🌐 Agent连接协议 - 支持WebSocket和REST API
- 🔐 安全网关 - JWT认证、速率限制、消息大小验证
- 🎨 可视化组件 - 8种主题、网络拓扑图
- 📊 监控系统 - Prometheus + Grafana集成
- 🐳 Docker支持 - 一键部署
- 🧪 完整测试 - 单元测试和集成测试
- 📚 完整文档 - API文档、架构设计、部署指南

### 技术栈

- **后端**: Python 3.8+, FastAPI, PostgreSQL, Redis
- **前端**: TypeScript, React 18+, Canvas API
- **运维**: Docker, Docker Compose, Prometheus, Grafana

### 特性

- Agent注册与发现
- 点对点、广播、组播消息
- 消息持久化和确认机制
- 分布式部署支持
- 实时监控和告警
- 多语言SDK支持

## [Unreleased]

### 计划

- [ ] WebSocket重连机制
- [ ] 消息加密传输
- [ ] 更多可视化组件
- [ ] Kubernetes Helm Chart
- [ ] 管理后台界面
- [ ] 消息队列支持（Kafka/RabbitMQ）
- [ ] 分布式链路追踪
- [ ] 更多主题样式

---

## 版本说明

### 版本号格式

版本号格式：主版本号.次版本号.修订号

1. **主版本号**：做了不兼容的API修改
2. **次版本号**：做了向下兼容的功能性新增
3. **修订号**：做了向下兼容的问题修正

### 标签说明

- `Added` - 新功能
- `Changed` - 功能变更
- `Deprecated` - 即将移除的功能
- `Removed` - 移除的功能
- `Fixed` - 问题修复
- `Security` - 安全相关
