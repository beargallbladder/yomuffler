"""
🤖 Base Agent Class
Foundation for all swarm intelligence agents
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod
import redis.asyncio as redis


class BaseAgent(ABC):
    """Base class for all swarm agents"""
    
    def __init__(self, agent_name: str, redis_pool: redis.Redis):
        self.agent_name = agent_name
        self.redis_pool = redis_pool
        self.agent_id = f"{agent_name}_{uuid.uuid4().hex[:8]}"
        self.logger = logging.getLogger(f"SwarmAgent.{agent_name}")
        
        # Agent metrics
        self.metrics = {
            "tasks_processed": 0,
            "avg_processing_time": 0.0,
            "success_rate": 0.0,
            "error_count": 0,
            "last_active": datetime.utcnow()
        }
        
        # Agent status
        self.status = "idle"
        self.current_task = None
        
        self.logger.info(f"🤖 Agent {self.agent_name} initialized")
    
    @abstractmethod
    async def process(self, task) -> Dict[str, Any]:
        """
        Process a task and return results
        Must be implemented by each agent
        """
        pass
    
    @abstractmethod
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Return agent information and capabilities
        Must be implemented by each agent
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health"""
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "status": self.status,
            "last_active": self.metrics["last_active"].isoformat(),
            "tasks_processed": self.metrics["tasks_processed"],
            "success_rate": self.metrics["success_rate"],
            "health": "healthy" if self.status != "error" else "degraded"
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            "agent_name": self.agent_name,
            "metrics": self.metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _update_metrics(self, processing_time: float, success: bool):
        """Update agent performance metrics"""
        self.metrics["tasks_processed"] += 1
        
        # Update average processing time
        current_avg = self.metrics["avg_processing_time"]
        count = self.metrics["tasks_processed"]
        self.metrics["avg_processing_time"] = ((current_avg * (count - 1)) + processing_time) / count
        
        # Update success rate
        if not success:
            self.metrics["error_count"] += 1
        
        self.metrics["success_rate"] = 1.0 - (self.metrics["error_count"] / count)
        self.metrics["last_active"] = datetime.utcnow()
    
    async def _store_debug_info(self, task_id: str, debug_data: Dict[str, Any]):
        """Store debug information for a task"""
        try:
            await self.redis_pool.hset(
                f"swarm:debug:{task_id}",
                self.agent_name,
                json.dumps(debug_data, default=str)
            )
            # Expire debug data after 1 hour
            await self.redis_pool.expire(f"swarm:debug:{task_id}", 3600)
        except Exception as e:
            self.logger.warning(f"Failed to store debug info: {str(e)}")
    
    async def _log_agent_action(self, action: str, task_id: str, details: Dict[str, Any] = None):
        """Log agent actions for audit trail"""
        log_entry = {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "action": action,
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        try:
            await self.redis_pool.lpush(
                f"swarm:audit:{task_id}",
                json.dumps(log_entry, default=str)
            )
            # Keep audit trail for 24 hours
            await self.redis_pool.expire(f"swarm:audit:{task_id}", 86400)
        except Exception as e:
            self.logger.warning(f"Failed to log action: {str(e)}")
    
    def _validate_input_data(self, task, required_fields: List[str]) -> bool:
        """Validate that task has required input fields"""
        if not hasattr(task, 'input_data') or not task.input_data:
            return False
        
        for field in required_fields:
            if field not in task.input_data:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def _safe_get(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Safely get value from dictionary"""
        try:
            return data.get(key, default)
        except (AttributeError, TypeError):
            return default
    
    async def _cache_result(self, cache_key: str, result: Dict[str, Any], ttl: int = 3600):
        """Cache agent result"""
        try:
            await self.redis_pool.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)
            )
        except Exception as e:
            self.logger.warning(f"Failed to cache result: {str(e)}")
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached agent result"""
        try:
            cached_data = await self.redis_pool.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            self.logger.warning(f"Failed to get cached result: {str(e)}")
            return None 