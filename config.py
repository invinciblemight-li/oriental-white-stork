"""
东方白鹳 - 配置管理模块
使用 Pydantic Settings 进行配置验证和管理
"""

import os
from typing import List, Optional
from functools import lru_cache
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    name: str = Field(default="oriental_white_stork", env="DB_NAME")
    user: str = Field(default="stork_user", env="DB_USER")
    password: str = Field(default="", env="DB_PASSWORD")
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    class Config:
        env_prefix = "DB_"


class RedisConfig(BaseSettings):
    """Redis配置"""
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_prefix = "REDIS_"


class SecurityConfig(BaseSettings):
    """安全配置"""
    jwt_secret: str = Field(default="your-secret-key-change-in-production", env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration: int = Field(default=3600, env="JWT_EXPIRATION")  # 1小时
    
    # 速率限制
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # 秒
    
    # 消息大小限制 (MB)
    max_message_size: int = Field(default=1, env="MAX_MESSAGE_SIZE")
    
    # TLS配置
    tls_enabled: bool = Field(default=True, env="TLS_ENABLED")
    tls_cert_path: Optional[str] = Field(default=None, env="TLS_CERT_PATH")
    tls_key_path: Optional[str] = Field(default=None, env="TLS_KEY_PATH")
    
    @validator('jwt_secret')
    def validate_jwt_secret(cls, v):
        if v == "your-secret-key-change-in-production":
            import warnings
            warnings.warn(
                "WARNING: Using default JWT secret. Please set JWT_SECRET environment variable in production!",
                RuntimeWarning
            )
        return v
    
    class Config:
        env_prefix = "SECURITY_"


class ServerConfig(BaseSettings):
    """服务器配置"""
    host: str = Field(default="0.0.0.0", env="SERVER_HOST")
    port: int = Field(default=8000, env="SERVER_PORT")
    workers: int = Field(default=1, env="SERVER_WORKERS")
    reload: bool = Field(default=False, env="SERVER_RELOAD")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # 跨域配置
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        env_prefix = "SERVER_"


class MessageBrokerConfig(BaseSettings):
    """消息代理配置"""
    # 消息保留时间 (小时)
    message_retention_hours: int = Field(default=24, env="MESSAGE_RETENTION_HOURS")
    
    # 死信队列配置
    dead_letter_enabled: bool = Field(default=True, env="DEAD_LETTER_ENABLED")
    dead_letter_max_retries: int = Field(default=3, env="DEAD_LETTER_MAX_RETRIES")
    
    # 消息确认超时 (秒)
    ack_timeout: int = Field(default=30, env="ACK_TIMEOUT")
    
    class Config:
        env_prefix = "BROKER_"


class Settings(BaseSettings):
    """全局配置"""
    # 应用信息
    app_name: str = Field(default="Oriental White Stork", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # 子配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    broker: MessageBrokerConfig = Field(default_factory=MessageBrokerConfig)
    
    # 节点配置 (分布式部署)
    node_id: str = Field(default="node-1", env="NODE_ID")
    node_name: str = Field(default="Primary Node", env="NODE_NAME")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置实例（单例模式）
    
    Returns:
        Settings: 全局配置对象
    """
    return Settings()


# 便捷访问函数
def get_db_config() -> DatabaseConfig:
    """获取数据库配置"""
    return get_settings().database


def get_redis_config() -> RedisConfig:
    """获取Redis配置"""
    return get_settings().redis


def get_security_config() -> SecurityConfig:
    """获取安全配置"""
    return get_settings().security


def get_server_config() -> ServerConfig:
    """获取服务器配置"""
    return get_settings().server


# 示例环境变量文件内容
ENV_EXAMPLE = """
# 应用配置
DEBUG=false
APP_NAME=Oriental White Stork
APP_VERSION=1.0.0

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=oriental_white_stork
DB_USER=stork_user
DB_PASSWORD=your_secure_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 安全配置（生产环境必须修改！）
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
MAX_MESSAGE_SIZE=1
TLS_ENABLED=true

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_WORKERS=1
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# 消息代理配置
MESSAGE_RETENTION_HOURS=24
DEAD_LETTER_ENABLED=true
DEAD_LETTER_MAX_RETRIES=3
ACK_TIMEOUT=30

# 节点配置
NODE_ID=node-1
NODE_NAME=Primary Node
"""


if __name__ == "__main__":
    # 测试配置加载
    settings = get_settings()
    print(f"App Name: {settings.app_name}")
    print(f"Database URL: {settings.database.url}")
    print(f"Redis URL: {settings.redis.url}")
    print(f"Server: {settings.server.host}:{settings.server.port}")
    print(f"JWT Expiration: {settings.security.jwt_expiration}s")
