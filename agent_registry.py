"""
东方白鹳 - Agent注册中心
"""

from typing import Dict, List, Any, Optional


class AgentRegistry:
    """Agent注册中心"""
    
    def __init__(self, db):
        self.db = db
        self.agents: Dict[str, Dict[str, Any]] = {}
    
    async def register(self, agent_data: Dict[str, Any]) -> str:
        """注册Agent"""
        agent_id = agent_data.get("agent_id")
        self.agents[agent_id] = agent_data
        return agent_id
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """获取Agent列表"""
        return list(self.agents.values())
