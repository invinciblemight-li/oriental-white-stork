# 架构设计

## 系统架构概览

东方白鹳采用分层架构设计，从下到上分为：存储层、核心引擎层、安全网关层和接入层。

```
┌─────────────────────────────────────────────────────────────┐
│                        接入层 (Access Layer)                 │
│         WebSocket (WSS)  |  REST API (HTTPS)                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     安全网关层 (Security Gateway)            │
│    TLS/SSL  |  JWT Auth  |  Rate Limit  |  Size Limit       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      核心引擎层 (Core Engine)                │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   消息总线       │  │  Agent注册中心   │                   │
│  │  MessageBroker  │  │  AgentRegistry  │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      存储层 (Storage Layer)                  │
│    PostgreSQL (持久化)  |  Redis (缓存/消息总线)              │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. Agent注册中心 (AgentRegistry)

负责管理所有Agent的生命周期：

- **注册/注销** - Agent加入或离开系统
- **能力发现** - 基于能力和类型的Agent查询
- **健康检查** - 心跳监控和状态管理
- **元数据管理** - Agent属性和标签

```python
class AgentRegistry:
    async def register(agent_data: dict) -> str
    async def unregister(agent_id: str)
    async def discover(capabilities: list) -> list
    async def heartbeat(agent_id: str)
```

### 2. 消息总线 (MessageBroker)

负责Agent间的消息传递：

- **消息路由** - 点对点、广播、组播
- **消息确认** - ACK/NACK机制
- **死信队列** - 处理失败消息
- **消息持久化** - 确保消息不丢失

```python
class MessageBroker:
    async def send_message(message: dict) -> str
    async def broadcast(content: dict, filter: dict)
    async def subscribe(agent_id: str, topics: list)
```

### 3. 安全网关 (SecurityGateway)

提供多层安全防护：

- **TLS/SSL** - 传输层加密
- **JWT认证** - Token身份验证
- **速率限制** - 防止滥用
- **消息验证** - 大小和内容检查

## 数据流

### Agent注册流程

```
1. Agent → POST /agents/register
2. SecurityGateway 验证Token
3. AgentRegistry 存储Agent信息
4. 返回注册成功响应
5. 开始心跳保活
```

### 消息发送流程

```
1. Agent A → POST /messages/send
2. SecurityGateway 验证和限流检查
3. MessageBroker 路由消息
4. 如果目标在线 → WebSocket推送
5. 如果目标离线 → 存储到PostgreSQL
6. 返回发送确认
```

### WebSocket通信流程

```
1. Agent 建立WebSocket连接
2. SecurityGateway 验证Token
3. MessageBroker 注册WebSocket
4. 双向实时通信
5. 连接断开时清理资源
```

## 存储设计

### PostgreSQL 表结构

**agents 表** - Agent信息
```sql
CREATE TABLE agents (
    agent_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'offline',
    capabilities JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP
);
```

**messages 表** - 消息存储
```sql
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id VARCHAR(255) REFERENCES agents(agent_id),
    recipient_id VARCHAR(255) REFERENCES agents(agent_id),
    message_type VARCHAR(20),
    content JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    delivered_at TIMESTAMP
);
```

### Redis 数据结构

**在线Agent集合**
```
SET online_agents: {agent_id1, agent_id2, ...}
```

**消息队列**
```
LIST message_queue:{agent_id}: [message1, message2, ...]
```

**分布式锁**
```
LOCK agent_registry:{agent_id}: {timestamp}
```

## 扩展性设计

### 水平扩展

通过多节点部署实现水平扩展：

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  负载均衡    │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
   │ Node 1  │◄──────►│ Node 2  │◄──────►│ Node 3  │
   └────┬────┘        └────┬────┘        └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────┴──────┐
                    │    Redis    │
                    │   消息总线   │
                    └─────────────┘
```

### 分区策略

- **按Agent ID哈希分区** - 分散负载
- **按时间分区** - 消息表按月分区
- **读写分离** - 主库写入，从库查询

## 高可用设计

### 故障转移

- **数据库** - PostgreSQL主从复制 + 自动故障转移
- **Redis** - Sentinel模式，自动切换主节点
- **应用节点** - 无状态设计，任意节点可替换

### 数据备份

- **全量备份** - 每日凌晨执行
- **增量备份** - 每小时WAL归档
- **异地备份** - 跨可用区复制

## 监控体系

### 指标收集

**应用指标**
- 请求QPS、延迟、错误率
- Agent在线数量
- 消息吞吐量

**系统指标**
- CPU、内存、磁盘使用率
- 网络IO
- 连接数

### 告警规则

- **P0** - 服务不可用，立即通知
- **P1** - 性能下降，5分钟内通知
- **P2** - 资源紧张，1小时内通知

## 安全设计

### 零信任架构

- 默认拒绝所有未认证请求
- 每层都有独立的安全检查
- 最小权限原则

### 数据加密

- **传输中** - TLS 1.3加密
- **存储中** - 敏感字段AES加密
- **备份** - 加密存储在对象存储

### 审计日志

记录所有关键操作：
- Agent注册/注销
- 消息发送记录
- 配置变更
- 管理员操作

## 部署架构

### Docker Compose（开发环境）

```yaml
services:
  postgres:  # 数据库
  redis:     # 缓存
  backend:   # 后端服务
  prometheus: # 监控
  grafana:   # 可视化
```

### Kubernetes（生产环境）

```yaml
# Deployment - 后端服务
# StatefulSet - 数据库
# DaemonSet - 监控代理
# Ingress - 流量入口
```

## 性能优化

### 缓存策略

- **L1** - 应用内存缓存（高频数据）
- **L2** - Redis缓存（中等频率）
- **L3** - 数据库（持久化）

### 连接池

- 数据库连接池：20-50连接
- Redis连接池：10-20连接
- HTTP连接池：复用TCP连接

### 异步处理

- 消息发送异步化
- 日志写入异步化
- 使用消息队列削峰
