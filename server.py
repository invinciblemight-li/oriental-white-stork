"""
东方白鹳 - 主服务器入口
改进版本：更好的错误处理、日志记录和配置管理
"""

import os
import sys
import asyncio
import logging
import signal
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 导入核心模块
from core.config import get_settings, get_server_config, get_security_config
from core.security import SecurityGateway
from core.agent_registry import AgentRegistry
from core.message_broker import MessageBroker
from core.database import DatabaseManager


# 配置日志
def setup_logging():
    """配置日志系统"""
    config = get_server_config()
    
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format=config.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/stork-server.log", encoding="utf-8")
        ]
    )
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    return logging.getLogger(__name__)


logger = setup_logging()


# 全局组件实例
class AppState:
    """应用状态管理"""
    def __init__(self):
        self.db: Optional[DatabaseManager] = None
        self.registry: Optional[AgentRegistry] = None
        self.broker: Optional[MessageBroker] = None
        self.security: Optional[SecurityGateway] = None
        self.running = False
    
    async def initialize(self):
        """初始化所有组件"""
        try:
            logger.info("Initializing application components...")
            
            # 初始化数据库
            logger.info("Connecting to database...")
            self.db = DatabaseManager()
            await self.db.connect()
            logger.info("Database connected successfully")
            
            # 初始化安全网关
            logger.info("Initializing security gateway...")
            self.security = SecurityGateway()
            
            # 初始化Agent注册中心
            logger.info("Initializing agent registry...")
            self.registry = AgentRegistry(self.db)
            
            # 初始化消息代理
            logger.info("Initializing message broker...")
            self.broker = MessageBroker(self.db, self.registry)
            await self.broker.initialize()
            
            self.running = True
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}", exc_info=True)
            raise
    
    async def shutdown(self):
        """关闭所有组件"""
        try:
            logger.info("Shutting down application...")
            self.running = False
            
            if self.broker:
                await self.broker.close()
                logger.info("Message broker closed")
            
            if self.db:
                await self.db.close()
                logger.info("Database connection closed")
            
            logger.info("Application shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    try:
        await app_state.initialize()
        yield
    finally:
        # 关闭
        await app_state.shutdown()


# 创建FastAPI应用
settings = get_settings()
server_config = get_server_config()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="东方白鹳 - Agent连接系统",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=server_config.cors_origins,
    allow_credentials=server_config.cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.debug else None
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "status_code": exc.status_code,
            "message": exc.detail
        }
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy" if app_state.running else "unhealthy",
        "version": settings.app_version,
        "components": {
            "database": app_state.db is not None and await app_state.db.is_connected(),
            "registry": app_state.registry is not None,
            "broker": app_state.broker is not None and app_state.broker.is_running
        }
    }


@app.get("/ready")
async def readiness_check():
    """就绪检查"""
    if not app_state.running:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    checks = {
        "database": await app_state.db.is_connected() if app_state.db else False,
        "registry": app_state.registry is not None,
        "broker": app_state.broker.is_running if app_state.broker else False
    }
    
    if not all(checks.values()):
        raise HTTPException(
            status_code=503,
            detail={"message": "Some components are not ready", "checks": checks}
        )
    
    return {"status": "ready", "checks": checks}


# API路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "东方白鹳 - Agent连接系统",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/api/v1/agents")
async def list_agents():
    """获取Agent列表"""
    try:
        agents = await app_state.registry.list_agents()
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Failed to list agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/agents/register")
async def register_agent(agent_data: dict):
    """注册Agent"""
    try:
        agent_id = await app_state.registry.register(agent_data)
        logger.info(f"Agent registered: {agent_id}")
        return {"agent_id": agent_id, "status": "registered"}
    except Exception as e:
        logger.error(f"Failed to register agent: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/messages/send")
async def send_message(message: dict):
    """发送消息"""
    try:
        message_id = await app_state.broker.send_message(message)
        logger.info(f"Message sent: {message_id}")
        return {"message_id": message_id, "status": "sent"}
    except Exception as e:
        logger.error(f"Failed to send message: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


# WebSocket端点
@app.websocket("/ws/agents/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str):
    """Agent WebSocket连接"""
    try:
        await websocket.accept()
        logger.info(f"Agent WebSocket connected: {agent_id}")
        
        # 注册WebSocket连接
        await app_state.broker.register_websocket(agent_id, websocket)
        
        try:
            while app_state.running:
                # 接收消息
                data = await websocket.receive_json()
                
                # 处理消息
                await app_state.broker.handle_websocket_message(agent_id, data)
                
        except WebSocketDisconnect:
            logger.info(f"Agent WebSocket disconnected: {agent_id}")
        except Exception as e:
            logger.error(f"WebSocket error for agent {agent_id}: {e}", exc_info=True)
        finally:
            # 注销WebSocket连接
            await app_state.broker.unregister_websocket(agent_id)
            
    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection: {e}", exc_info=True)
        await websocket.close(code=1011)


def signal_handler(sig, frame):
    """信号处理器"""
    logger.info(f"Received signal {sig}, initiating shutdown...")
    sys.exit(0)


# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    config = get_server_config()
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Server: {config.host}:{config.port}")
    logger.info(f"Workers: {config.workers}")
    logger.info(f"Debug: {settings.debug}")
    
    uvicorn.run(
        "server:app",
        host=config.host,
        port=config.port,
        workers=config.workers if not config.reload else 1,
        reload=config.reload,
        log_level=config.log_level.lower(),
        access_log=True
    )
