"""
Ford Bayesian Risk Score Engine - Swarm Orchestrator

Manages distributed processing across multiple worker nodes with:
- Dynamic load balancing
- Fault tolerance and recovery
- Auto-scaling based on queue depth
- Health monitoring and metrics collection
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import aioredis
from contextlib import asynccontextmanager

from ..models.schemas import (
    ProcessingTask, SwarmMetrics, ServiceType, VehicleInputData,
    RiskScoreOutput, HealthCheck
)
from ..engines.bayesian_engine import BayesianRiskEngine, BatchBayesianProcessor


logger = logging.getLogger(__name__)


class WorkerStatus(str, Enum):
    """Worker status states"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    SCALING_UP = "scaling_up"
    SCALING_DOWN = "scaling_down"


@dataclass
class WorkerNode:
    """Individual worker node in the swarm"""
    worker_id: str
    service_type: ServiceType
    status: WorkerStatus
    current_task: Optional[str] = None
    last_heartbeat: datetime = None
    processed_count: int = 0
    error_count: int = 0
    avg_processing_time_ms: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    
    def to_metrics(self) -> SwarmMetrics:
        """Convert to SwarmMetrics model"""
        return SwarmMetrics(
            service_type=self.service_type,
            worker_id=self.worker_id,
            processed_count=self.processed_count,
            error_count=self.error_count,
            avg_processing_time_ms=self.avg_processing_time_ms,
            last_heartbeat=self.last_heartbeat or datetime.utcnow(),
            cpu_usage_percent=self.cpu_usage_percent,
            memory_usage_mb=self.memory_usage_mb,
            queue_depth=0  # Set by orchestrator
        )


class SwarmOrchestrator:
    """
    Central orchestrator for the Ford Risk Score swarm
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_pool = None
        self.workers: Dict[str, WorkerNode] = {}
        self.task_queues: Dict[ServiceType, asyncio.Queue] = {}
        self.running = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize task queues for each service type
        for service_type in ServiceType:
            self.task_queues[service_type] = asyncio.Queue(maxsize=10000)
        
        # Swarm configuration
        self.config = {
            "heartbeat_interval": 30,  # seconds
            "worker_timeout": 120,     # seconds
            "max_queue_depth": 1000,   # tasks per worker
            "scale_up_threshold": 0.8, # queue utilization
            "scale_down_threshold": 0.2,
            "min_workers_per_service": 1,
            "max_workers_per_service": 10,
            "health_check_interval": 60,
        }
    
    async def start(self):
        """Start the swarm orchestrator"""
        self.logger.info("Starting Ford Risk Score Swarm Orchestrator")
        
        # Initialize Redis connection
        self.redis_pool = await aioredis.from_url(self.redis_url)
        
        self.running = True
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._heartbeat_monitor()),
            asyncio.create_task(self._task_dispatcher()),
            asyncio.create_task(self._auto_scaler()),
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._metrics_collector()),
        ]
        
        self.logger.info("Swarm orchestrator started successfully")
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Swarm orchestrator error: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the swarm orchestrator"""
        self.logger.info("Stopping swarm orchestrator")
        self.running = False
        
        if self.redis_pool:
            await self.redis_pool.close()
    
    async def register_worker(self, worker_id: str, service_type: ServiceType) -> bool:
        """Register a new worker with the swarm"""
        try:
            worker = WorkerNode(
                worker_id=worker_id,
                service_type=service_type,
                status=WorkerStatus.IDLE,
                last_heartbeat=datetime.utcnow()
            )
            
            self.workers[worker_id] = worker
            
            # Store in Redis for persistence
            await self.redis_pool.hset(
                "swarm:workers", 
                worker_id, 
                json.dumps(asdict(worker), default=str)
            )
            
            self.logger.info(f"Registered worker {worker_id} for service {service_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register worker {worker_id}: {str(e)}")
            return False
    
    async def unregister_worker(self, worker_id: str) -> bool:
        """Unregister a worker from the swarm"""
        try:
            if worker_id in self.workers:
                worker = self.workers[worker_id]
                worker.status = WorkerStatus.OFFLINE
                
                # Remove from active workers
                del self.workers[worker_id]
                
                # Remove from Redis
                await self.redis_pool.hdel("swarm:workers", worker_id)
                
                self.logger.info(f"Unregistered worker {worker_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to unregister worker {worker_id}: {str(e)}")
            return False
    
    async def submit_task(self, task: ProcessingTask) -> str:
        """Submit a task to the appropriate service queue"""
        try:
            # Determine service type based on task type
            service_type = self._get_service_type_for_task(task.task_type)
            
            # Add to appropriate queue
            await self.task_queues[service_type].put(task)
            
            # Store task in Redis for persistence
            await self.redis_pool.hset(
                "swarm:tasks:pending",
                task.task_id,
                json.dumps(task.dict(), default=str)
            )
            
            self.logger.debug(f"Submitted task {task.task_id} to {service_type.value} queue")
            return task.task_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit task {task.task_id}: {str(e)}")
            raise
    
    async def get_task_status(self, task_id: str) -> Optional[ProcessingTask]:
        """Get the status of a specific task"""
        try:
            # Check pending tasks
            task_data = await self.redis_pool.hget("swarm:tasks:pending", task_id)
            if task_data:
                return ProcessingTask.parse_raw(task_data)
            
            # Check completed tasks
            task_data = await self.redis_pool.hget("swarm:tasks:completed", task_id)
            if task_data:
                return ProcessingTask.parse_raw(task_data)
            
            # Check failed tasks
            task_data = await self.redis_pool.hget("swarm:tasks:failed", task_id)
            if task_data:
                return ProcessingTask.parse_raw(task_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get task status for {task_id}: {str(e)}")
            return None
    
    async def get_swarm_metrics(self) -> Dict[str, any]:
        """Get comprehensive swarm metrics"""
        try:
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_workers": len(self.workers),
                "workers_by_service": {},
                "queue_depths": {},
                "processing_rates": {},
                "error_rates": {},
                "system_health": "healthy"
            }
            
            # Workers by service type
            for service_type in ServiceType:
                service_workers = [w for w in self.workers.values() if w.service_type == service_type]
                metrics["workers_by_service"][service_type.value] = {
                    "total": len(service_workers),
                    "idle": len([w for w in service_workers if w.status == WorkerStatus.IDLE]),
                    "busy": len([w for w in service_workers if w.status == WorkerStatus.BUSY]),
                    "offline": len([w for w in service_workers if w.status == WorkerStatus.OFFLINE]),
                    "error": len([w for w in service_workers if w.status == WorkerStatus.ERROR])
                }
            
            # Queue depths
            for service_type, queue in self.task_queues.items():
                metrics["queue_depths"][service_type.value] = queue.qsize()
            
            # Processing rates and error rates
            for worker in self.workers.values():
                service = worker.service_type.value
                if service not in metrics["processing_rates"]:
                    metrics["processing_rates"][service] = []
                    metrics["error_rates"][service] = []
                
                if worker.processed_count > 0:
                    rate = worker.processed_count / max(1, worker.avg_processing_time_ms / 1000)
                    metrics["processing_rates"][service].append(rate)
                    
                    error_rate = worker.error_count / worker.processed_count
                    metrics["error_rates"][service].append(error_rate)
            
            # Calculate averages
            for service in metrics["processing_rates"]:
                rates = metrics["processing_rates"][service]
                metrics["processing_rates"][service] = sum(rates) / len(rates) if rates else 0
                
                error_rates = metrics["error_rates"][service]
                metrics["error_rates"][service] = sum(error_rates) / len(error_rates) if error_rates else 0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get swarm metrics: {str(e)}")
            return {"error": str(e)}
    
    async def _heartbeat_monitor(self):
        """Monitor worker heartbeats and mark offline workers"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                timeout_threshold = current_time - timedelta(seconds=self.config["worker_timeout"])
                
                offline_workers = []
                for worker_id, worker in self.workers.items():
                    if worker.last_heartbeat and worker.last_heartbeat < timeout_threshold:
                        worker.status = WorkerStatus.OFFLINE
                        offline_workers.append(worker_id)
                
                # Remove offline workers
                for worker_id in offline_workers:
                    await self.unregister_worker(worker_id)
                    self.logger.warning(f"Worker {worker_id} marked offline due to missed heartbeats")
                
                await asyncio.sleep(self.config["heartbeat_interval"])
                
            except Exception as e:
                self.logger.error(f"Heartbeat monitor error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _task_dispatcher(self):
        """Dispatch tasks to available workers"""
        while self.running:
            try:
                # Process each service type queue
                for service_type, queue in self.task_queues.items():
                    if queue.empty():
                        continue
                    
                    # Find available workers for this service
                    available_workers = [
                        w for w in self.workers.values()
                        if w.service_type == service_type and w.status == WorkerStatus.IDLE
                    ]
                    
                    if not available_workers:
                        continue
                    
                    # Dispatch tasks to available workers
                    for worker in available_workers:
                        if queue.empty():
                            break
                        
                        try:
                            task = await asyncio.wait_for(queue.get(), timeout=0.1)
                            await self._assign_task_to_worker(task, worker)
                        except asyncio.TimeoutError:
                            break
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Task dispatcher error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _assign_task_to_worker(self, task: ProcessingTask, worker: WorkerNode):
        """Assign a specific task to a worker"""
        try:
            worker.status = WorkerStatus.BUSY
            worker.current_task = task.task_id
            task.worker_id = worker.worker_id
            task.started_at = datetime.utcnow()
            task.status = "processing"
            
            # Update task in Redis
            await self.redis_pool.hset(
                "swarm:tasks:processing",
                task.task_id,
                json.dumps(task.dict(), default=str)
            )
            
            # Remove from pending
            await self.redis_pool.hdel("swarm:tasks:pending", task.task_id)
            
            # Send task to worker via Redis pub/sub
            await self.redis_pool.publish(
                f"swarm:worker:{worker.worker_id}:tasks",
                json.dumps(task.dict(), default=str)
            )
            
            self.logger.debug(f"Assigned task {task.task_id} to worker {worker.worker_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to assign task {task.task_id} to worker {worker.worker_id}: {str(e)}")
            # Reset worker status
            worker.status = WorkerStatus.IDLE
            worker.current_task = None
    
    async def _auto_scaler(self):
        """Auto-scale workers based on queue depth"""
        while self.running:
            try:
                for service_type, queue in self.task_queues.items():
                    service_workers = [w for w in self.workers.values() if w.service_type == service_type]
                    active_workers = [w for w in service_workers if w.status != WorkerStatus.OFFLINE]
                    
                    if not active_workers:
                        continue
                    
                    # Calculate queue utilization
                    queue_depth = queue.qsize()
                    worker_capacity = len(active_workers) * self.config["max_queue_depth"]
                    utilization = queue_depth / max(1, worker_capacity)
                    
                    # Scale up if needed
                    if (utilization > self.config["scale_up_threshold"] and 
                        len(active_workers) < self.config["max_workers_per_service"]):
                        
                        await self._request_worker_scale_up(service_type)
                    
                    # Scale down if needed
                    elif (utilization < self.config["scale_down_threshold"] and 
                          len(active_workers) > self.config["min_workers_per_service"]):
                        
                        await self._request_worker_scale_down(service_type, active_workers)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Auto-scaler error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _request_worker_scale_up(self, service_type: ServiceType):
        """Request scaling up workers for a service"""
        try:
            scale_request = {
                "action": "scale_up",
                "service_type": service_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "high_queue_utilization"
            }
            
            await self.redis_pool.publish("swarm:scaling:requests", json.dumps(scale_request))
            self.logger.info(f"Requested scale-up for {service_type.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to request scale-up for {service_type.value}: {str(e)}")
    
    async def _request_worker_scale_down(self, service_type: ServiceType, workers: List[WorkerNode]):
        """Request scaling down workers for a service"""
        try:
            # Find the least utilized worker
            idle_workers = [w for w in workers if w.status == WorkerStatus.IDLE]
            if not idle_workers:
                return
            
            # Select worker with lowest processed count (least utilized)
            worker_to_remove = min(idle_workers, key=lambda w: w.processed_count)
            
            scale_request = {
                "action": "scale_down",
                "service_type": service_type.value,
                "worker_id": worker_to_remove.worker_id,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "low_queue_utilization"
            }
            
            await self.redis_pool.publish("swarm:scaling:requests", json.dumps(scale_request))
            self.logger.info(f"Requested scale-down for {service_type.value}, worker {worker_to_remove.worker_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to request scale-down for {service_type.value}: {str(e)}")
    
    async def _health_monitor(self):
        """Monitor overall swarm health"""
        while self.running:
            try:
                health_status = await self._check_swarm_health()
                
                # Store health status in Redis
                await self.redis_pool.set(
                    "swarm:health",
                    json.dumps(health_status, default=str),
                    ex=300  # Expire after 5 minutes
                )
                
                if health_status["status"] != "healthy":
                    self.logger.warning(f"Swarm health issue detected: {health_status}")
                
                await asyncio.sleep(self.config["health_check_interval"])
                
            except Exception as e:
                self.logger.error(f"Health monitor error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _check_swarm_health(self) -> Dict[str, any]:
        """Check overall swarm health"""
        try:
            health = {
                "status": "healthy",
                "timestamp": datetime.utcnow(),
                "issues": [],
                "services": {}
            }
            
            # Check each service type
            for service_type in ServiceType:
                service_workers = [w for w in self.workers.values() if w.service_type == service_type]
                active_workers = [w for w in service_workers if w.status != WorkerStatus.OFFLINE]
                error_workers = [w for w in service_workers if w.status == WorkerStatus.ERROR]
                
                service_health = {
                    "total_workers": len(service_workers),
                    "active_workers": len(active_workers),
                    "error_workers": len(error_workers),
                    "queue_depth": self.task_queues[service_type].qsize(),
                    "status": "healthy"
                }
                
                # Check for issues
                if len(active_workers) == 0:
                    service_health["status"] = "critical"
                    health["issues"].append(f"No active workers for {service_type.value}")
                elif len(error_workers) > len(active_workers) * 0.5:
                    service_health["status"] = "degraded"
                    health["issues"].append(f"High error rate for {service_type.value}")
                elif self.task_queues[service_type].qsize() > 1000:
                    service_health["status"] = "overloaded"
                    health["issues"].append(f"High queue depth for {service_type.value}")
                
                health["services"][service_type.value] = service_health
            
            # Overall status
            if any(s["status"] == "critical" for s in health["services"].values()):
                health["status"] = "critical"
            elif any(s["status"] in ["degraded", "overloaded"] for s in health["services"].values()):
                health["status"] = "degraded"
            
            return health
            
        except Exception as e:
            return {
                "status": "error",
                "timestamp": datetime.utcnow(),
                "error": str(e)
            }
    
    async def _metrics_collector(self):
        """Collect and aggregate swarm metrics"""
        while self.running:
            try:
                metrics = await self.get_swarm_metrics()
                
                # Store metrics in Redis with timestamp
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
                await self.redis_pool.hset(
                    "swarm:metrics:history",
                    timestamp,
                    json.dumps(metrics, default=str)
                )
                
                # Keep only last 24 hours of metrics
                all_metrics = await self.redis_pool.hgetall("swarm:metrics:history")
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                cutoff_str = cutoff_time.strftime("%Y%m%d_%H%M")
                
                for timestamp_key in all_metrics.keys():
                    if timestamp_key.decode() < cutoff_str:
                        await self.redis_pool.hdel("swarm:metrics:history", timestamp_key)
                
                await asyncio.sleep(60)  # Collect metrics every minute
                
            except Exception as e:
                self.logger.error(f"Metrics collector error: {str(e)}")
                await asyncio.sleep(30)
    
    def _get_service_type_for_task(self, task_type: str) -> ServiceType:
        """Map task type to service type"""
        mapping = {
            "risk_calculation": ServiceType.BAYESIAN_ENGINE,
            "cohort_assignment": ServiceType.COHORT_PROCESSOR,
            "index_building": ServiceType.INDEX_BUILDER,
            "data_ingestion": ServiceType.VH_TELEMETRY,
        }
        
        return mapping.get(task_type, ServiceType.BAYESIAN_ENGINE) 