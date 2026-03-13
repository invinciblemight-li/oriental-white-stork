# API 文档

## 概述

东方白鹳 API 基于 RESTful 设计，使用 JSON 格式进行数据交换。

**基础 URL:** `https://api.oriental-white-stork.example.com/v1`

**认证方式:** JWT Token (Bearer)

---

## 认证

### 获取 Token

```http
POST /auth/token
Content-Type: application/json

{
  "agent_id": "your_agent_id",
  "secret": "your_secret"
}
```

**响应:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 使用 Token

在请求头中添加：
```http
Authorization: Bearer <your_token>
```

---

## Agent 管理

### 注册 Agent

```http
POST /agents/register
Authorization: Bearer <token>
Content-Type: application/json

{
  "agent_id": "unique_agent_id",
  "name": "Agent Name",
  "type": "service",
  "capabilities": ["text_processing", "data_analysis"],
  "metadata": {
    "version": "1.0.0",
    "author": "your_name"
  }
}
```

**响应:**
```json
{
  "agent_id": "unique_agent_id",
  "status": "registered",
  "registered_at": "2024-01-15T10:30:00Z"
}
```

### 获取 Agent 列表

```http
GET /agents
Authorization: Bearer <token>
```

**查询参数:**
- `type` - 按类型筛选
- `status` - 按状态筛选 (online/offline/busy)
- `capability` - 按能力筛选

**响应:**
```json
{
  "agents": [
    {
      "agent_id": "agent_001",
      "name": "Data Processor",
      "type": "service",
      "status": "online",
      "capabilities": ["data_analysis"],
      "last_seen": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### 获取 Agent 详情

```http
GET /agents/{agent_id}
Authorization: Bearer <token>
```

### 注销 Agent

```http
DELETE /agents/{agent_id}
Authorization: Bearer <token>
```

---

## 消息传递

### 发送消息

```http
POST /messages/send
Authorization: Bearer <token>
Content-Type: application/json

{
  "sender_id": "agent_001",
  "recipient_id": "agent_002",
  "message_type": "direct",
  "content": {
    "text": "Hello!",
    "data": {"key": "value"}
  },
  "priority": 1,
  "ttl": 3600
}
```

**消息类型:**
- `direct` - 点对点消息
- `broadcast` - 广播消息
- `group` - 组播消息

**响应:**
```json
{
  "message_id": "msg_abc123",
  "status": "sent",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 获取消息历史

```http
GET /messages/history
Authorization: Bearer <token>
```

**查询参数:**
- `agent_id` - Agent ID
- `start_time` - 开始时间 (ISO 8601)
- `end_time` - 结束时间 (ISO 8601)
- `limit` - 返回数量限制

---

## WebSocket 实时通信

### 连接

```javascript
const ws = new WebSocket(
  'wss://api.oriental-white-stork.example.com/ws/agents/{agent_id}?token=<jwt_token>'
);
```

### 发送消息

```javascript
ws.send(JSON.stringify({
  type: 'send_message',
  recipient_id: 'target_agent_id',
  content: { text: 'Hello!' }
}));
```

### 接收消息

```javascript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### 消息格式

**客户端 → 服务器:**
```json
{
  "type": "send_message",
  "recipient_id": "agent_002",
  "content": {},
  "priority": 1
}
```

**服务器 → 客户端:**
```json
{
  "type": "message",
  "message_id": "msg_abc123",
  "sender_id": "agent_001",
  "content": {},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request is invalid",
    "details": {
      "field": "agent_id",
      "issue": "Agent ID already exists"
    }
  }
}
```

### 错误代码

| 代码 | HTTP 状态 | 说明 |
|------|----------|------|
| `UNAUTHORIZED` | 401 | 未授权，Token无效或过期 |
| `FORBIDDEN` | 403 | 禁止访问，权限不足 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `RATE_LIMITED` | 429 | 请求过于频繁 |
| `INVALID_REQUEST` | 400 | 请求参数错误 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

---

## 速率限制

- 认证端点: 5 次/分钟
- 普通 API: 100 次/分钟
- WebSocket: 1000 条消息/分钟

响应头中包含限制信息:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642231200
```

---

## SDK 使用示例

### Python SDK

```python
from oriental_white_stork import Agent, MessageBroker

# 创建 Agent
agent = Agent(
    agent_id="my_agent",
    name="My Agent",
    secret="your_secret"
)

# 连接到系统
broker = MessageBroker()
broker.connect(agent)

# 发送消息
broker.send_message(
    recipient="target_agent",
    content={"text": "Hello!"}
)

# 接收消息
@agent.on_message
def handle_message(message):
    print(f"Received: {message.content}")
```

### JavaScript SDK

```javascript
import { StorkAgent } from '@stork-viz/sdk';

const agent = new StorkAgent({
  agentId: 'my_agent',
  name: 'My Agent',
  secret: 'your_secret'
});

await agent.connect();

// 发送消息
await agent.sendMessage({
  recipient: 'target_agent',
  content: { text: 'Hello!' }
});

// 接收消息
agent.onMessage((message) => {
  console.log('Received:', message.content);
});
```
