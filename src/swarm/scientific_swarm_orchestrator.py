"""
🧠 Scientific VIN Insight Swarm Orchestrator
Bayesian-Verified, Dealer-Tuned, LLM-Augmented Multi-Agent System
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import numpy as np

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class SwarmTask:
    """Task for swarm processing"""
    task_id: str
    vin: str
    input_data: Dict[str, Any]
    required_agents: List[str]
    priority: int = 1
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.results is None:
            self.results = {}


@dataclass
class SwarmResult:
    """Final swarm processing result"""
    task_id: str
    vin: str
    risk_score: float
    confidence: float
    top_stressors: List[str]
    cohort_match: str
    dealer_message: str
    customer_message: str
    validation_tags: List[str]
    processing_time_ms: float
    agent_contributions: Dict[str, Any]


class ScientificSwarmOrchestrator:
    """
    Orchestrates multi-agent VIN intelligence processing with:
    - Parallel agent execution
    - Quality validation chains
    - Real-time result aggregation
    - Intelligent load balancing
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_pool = None
        self.agents = {}
        self.running = False
        self.logger = logging.getLogger(f"{__name__}.ScientificSwarm")
        
        # Task queues
        self.task_queue = asyncio.Queue(maxsize=10000)
        self.result_queue = asyncio.Queue(maxsize=10000)
        
        # Agent types and their dependencies
        self.agent_dependencies = {
            "data_ingest": [],
            "cohort_index": ["data_ingest"],
            "stress_validation": ["data_ingest", "cohort_index"],
            "bayes_score": ["stress_validation"],
            "research_priors": [],
            "lead_likelihood": ["bayes_score"],
            "veracity_inspector": ["lead_likelihood"],
            "llm_message": ["veracity_inspector"],
            "ux_guardrail": ["llm_message"],
            "insight_reviewer": ["ux_guardrail"],
            "promotion_path": ["insight_reviewer"]
        }
        
        # Performance metrics
        self.metrics = {
            "tasks_processed": 0,
            "avg_processing_time": 0.0,
            "success_rate": 0.0,
            "agent_utilization": {},
            "quality_scores": []
        }
    
    async def start(self):
        """Start the swarm orchestrator"""
        self.logger.info("🐝 Starting Scientific VIN Swarm Orchestrator")
        
        # Initialize Redis
        self.redis_pool = await redis.from_url(self.redis_url)
        
        # Initialize all agents
        await self._initialize_agents()
        
        self.running = True
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._task_processor()),
            asyncio.create_task(self._result_aggregator()),
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._metrics_collector()),
            asyncio.create_task(self._quality_validator())
        ]
        
        self.logger.info("🚀 Scientific Swarm is OPERATIONAL")
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"❌ Swarm orchestrator error: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the swarm orchestrator"""
        self.logger.info("🛑 Stopping Scientific VIN Swarm")
        self.running = False
        
        if self.redis_pool:
            await self.redis_pool.close()
    
    async def process_vin(self, vin: str, input_data: Dict[str, Any], priority: int = 1) -> SwarmResult:
        """Process a single VIN through the swarm"""
        task_id = f"swarm_{uuid.uuid4().hex[:8]}"
        
        task = SwarmTask(
            task_id=task_id,
            vin=vin,
            input_data=input_data,
            required_agents=list(self.agent_dependencies.keys()),
            priority=priority
        )
        
        # Submit to swarm
        await self.task_queue.put(task)
        
        # Wait for result (with timeout)
        timeout = 30.0  # 30 seconds
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            try:
                # Check Redis for result
                result_data = await self.redis_pool.get(f"swarm:result:{task_id}")
                if result_data:
                    result_dict = json.loads(result_data)
                    return SwarmResult(**result_dict)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error checking result for {task_id}: {str(e)}")
                break
        
        raise TimeoutError(f"Swarm processing timeout for VIN {vin}")
    
    async def process_batch(self, vins_data: List[Tuple[str, Dict[str, Any]]]) -> List[SwarmResult]:
        """Process batch of VINs through swarm"""
        self.logger.info(f"🔄 Processing batch of {len(vins_data)} VINs")
        
        # Submit all tasks
        tasks = []
        for vin, input_data in vins_data:
            task = asyncio.create_task(self.process_vin(vin, input_data))
            tasks.append(task)
        
        # Process all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Failed to process VIN {vins_data[i][0]}: {str(result)}")
            else:
                valid_results.append(result)
        
        self.logger.info(f"✅ Batch complete: {len(valid_results)}/{len(vins_data)} successful")
        return valid_results
    
    async def _initialize_agents(self):
        """Initialize all swarm agents"""
        from .agents.data_ingest_agent import DataIngestAgent
        from .agents.cohort_index_agent import CohortIndexAgent
        from .agents.stress_validation_agent import StressValidationAgent
        from .agents.bayes_score_agent import BayesScoreAgent
        from .agents.research_priors_agent import ResearchPriorsAgent
        from .agents.lead_likelihood_agent import LeadLikelihoodAgent
        from .agents.veracity_inspector_agent import VeracityInspectorAgent
        from .agents.llm_message_agent import LLMMessageAgent
        from .agents.ux_guardrail_agent import UXGuardrailAgent
        from .agents.insight_reviewer_agent import InsightReviewerAgent
        from .agents.promotion_path_agent import PromotionPathAgent
        
        self.agents = {
            "data_ingest": DataIngestAgent(self.redis_pool),
            "cohort_index": CohortIndexAgent(self.redis_pool),
            "stress_validation": StressValidationAgent(self.redis_pool),
            "bayes_score": BayesScoreAgent(self.redis_pool),
            "research_priors": ResearchPriorsAgent(self.redis_pool),
            "lead_likelihood": LeadLikelihoodAgent(self.redis_pool),
            "veracity_inspector": VeracityInspectorAgent(self.redis_pool),
            "llm_message": LLMMessageAgent(self.redis_pool),
            "ux_guardrail": UXGuardrailAgent(self.redis_pool),
            "insight_reviewer": InsightReviewerAgent(self.redis_pool),
            "promotion_path": PromotionPathAgent(self.redis_pool)
        }
        
        self.logger.info(f"✅ Initialized {len(self.agents)} intelligent agents")
    
    async def _task_processor(self):
        """Main task processing loop"""
        while self.running:
            try:
                # Get next task
                task = await self.task_queue.get()
                
                # Process through agent pipeline
                await self._process_task_through_pipeline(task)
                
            except Exception as e:
                self.logger.error(f"Task processor error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_task_through_pipeline(self, task: SwarmTask):
        """Process task through the agent pipeline"""
        start_time = datetime.utcnow()
        task.started_at = start_time
        task.status = "processing"
        
        try:
            # Stage 1: Parallel data ingestion and research
            stage1_tasks = [
                self.agents["data_ingest"].process(task),
                self.agents["research_priors"].process(task)
            ]
            stage1_results = await asyncio.gather(*stage1_tasks, return_exceptions=True)
            
            # Merge results
            for result in stage1_results:
                if not isinstance(result, Exception):
                    task.results.update(result)
            
            # Stage 2: Sequential validation chain
            for agent_name in ["cohort_index", "stress_validation", "bayes_score", "lead_likelihood"]:
                agent_result = await self.agents[agent_name].process(task)
                task.results.update(agent_result)
            
            # Stage 3: Quality and messaging pipeline
            for agent_name in ["veracity_inspector", "llm_message", "ux_guardrail"]:
                agent_result = await self.agents[agent_name].process(task)
                task.results.update(agent_result)
            
            # Stage 4: Final review and promotion tracking
            final_agents = ["insight_reviewer", "promotion_path"]
            final_tasks = [self.agents[agent].process(task) for agent in final_agents]
            final_results = await asyncio.gather(*final_tasks, return_exceptions=True)
            
            for result in final_results:
                if not isinstance(result, Exception):
                    task.results.update(result)
            
            # Create final result
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            swarm_result = SwarmResult(
                task_id=task.task_id,
                vin=task.vin,
                risk_score=task.results.get("risk_score", 0.0),
                confidence=task.results.get("confidence", 0.0),
                top_stressors=task.results.get("top_stressors", []),
                cohort_match=task.results.get("cohort_match", "unknown"),
                dealer_message=task.results.get("dealer_message", ""),
                customer_message=task.results.get("customer_message", ""),
                validation_tags=task.results.get("validation_tags", []),
                processing_time_ms=processing_time,
                agent_contributions=task.results.get("agent_debug", {})
            )
            
            # Store result in Redis
            await self.redis_pool.setex(
                f"swarm:result:{task.task_id}",
                300,  # 5 minute expiry
                json.dumps(asdict(swarm_result), default=str)
            )
            
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            
            self.logger.debug(f"✅ Task {task.task_id} completed in {processing_time:.1f}ms")
            
        except Exception as e:
            task.status = "failed"
            self.logger.error(f"❌ Task {task.task_id} failed: {str(e)}")
            
            # Store error result
            error_result = SwarmResult(
                task_id=task.task_id,
                vin=task.vin,
                risk_score=0.0,
                confidence=0.0,
                top_stressors=[],
                cohort_match="error",
                dealer_message="Processing error occurred",
                customer_message="Unable to analyze vehicle at this time",
                validation_tags=["error"],
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                agent_contributions={"error": str(e)}
            )
            
            await self.redis_pool.setex(
                f"swarm:result:{task.task_id}",
                60,  # 1 minute expiry for errors
                json.dumps(asdict(error_result), default=str)
            )
    
    async def _result_aggregator(self):
        """Aggregate and analyze swarm results"""
        while self.running:
            try:
                # Process results from Redis
                keys = await self.redis_pool.keys("swarm:result:*")
                
                if keys:
                    results_data = await self.redis_pool.mget(keys)
                    
                    valid_results = []
                    for data in results_data:
                        if data:
                            try:
                                result = json.loads(data)
                                valid_results.append(result)
                            except json.JSONDecodeError:
                                continue
                    
                    # Update metrics
                    if valid_results:
                        await self._update_metrics(valid_results)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Result aggregator error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _health_monitor(self):
        """Monitor swarm health"""
        while self.running:
            try:
                health_status = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "swarm_status": "operational",
                    "agents": {},
                    "queue_depths": {
                        "tasks": self.task_queue.qsize(),
                        "results": self.result_queue.qsize()
                    },
                    "metrics": self.metrics
                }
                
                # Check each agent
                for agent_name, agent in self.agents.items():
                    try:
                        agent_health = await agent.health_check()
                        health_status["agents"][agent_name] = agent_health
                    except Exception as e:
                        health_status["agents"][agent_name] = {
                            "status": "error",
                            "error": str(e)
                        }
                
                # Store health status
                await self.redis_pool.setex(
                    "swarm:health",
                    120,  # 2 minute expiry
                    json.dumps(health_status, default=str)
                )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Health monitor error: {str(e)}")
                await asyncio.sleep(15)
    
    async def _metrics_collector(self):
        """Collect swarm performance metrics"""
        while self.running:
            try:
                # Collect metrics from all agents
                agent_metrics = {}
                for agent_name, agent in self.agents.items():
                    try:
                        metrics = await agent.get_metrics()
                        agent_metrics[agent_name] = metrics
                    except Exception as e:
                        agent_metrics[agent_name] = {"error": str(e)}
                
                # Store aggregated metrics
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
                await self.redis_pool.hset(
                    "swarm:metrics:history",
                    timestamp,
                    json.dumps(agent_metrics, default=str)
                )
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                self.logger.error(f"Metrics collector error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _quality_validator(self):
        """Validate swarm output quality"""
        while self.running:
            try:
                # Get recent results for quality analysis
                keys = await self.redis_pool.keys("swarm:result:*")
                
                if len(keys) > 10:  # Only validate if we have enough data
                    sample_keys = keys[-10:]  # Last 10 results
                    results_data = await self.redis_pool.mget(sample_keys)
                    
                    quality_scores = []
                    for data in results_data:
                        if data:
                            try:
                                result = json.loads(data)
                                quality_score = self._calculate_quality_score(result)
                                quality_scores.append(quality_score)
                            except:
                                continue
                    
                    # Update quality metrics
                    if quality_scores:
                        avg_quality = sum(quality_scores) / len(quality_scores)
                        self.metrics["avg_quality_score"] = avg_quality
                        
                        # Alert if quality drops
                        if avg_quality < 0.7:
                            self.logger.warning(f"⚠️ Quality score dropped to {avg_quality:.2f}")
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                self.logger.error(f"Quality validator error: {str(e)}")
                await asyncio.sleep(60)
    
    def _calculate_quality_score(self, result: Dict[str, Any]) -> float:
        """Calculate quality score for a swarm result"""
        score = 0.0
        
        # Risk score validity (0-1 range)
        risk_score = result.get("risk_score", 0)
        if 0 <= risk_score <= 1:
            score += 0.2
        
        # Confidence validity
        confidence = result.get("confidence", 0)
        if 0 <= confidence <= 1:
            score += 0.2
        
        # Message quality (non-empty)
        if result.get("dealer_message") and result.get("customer_message"):
            score += 0.2
        
        # Validation tags presence
        validation_tags = result.get("validation_tags", [])
        if validation_tags and len(validation_tags) > 0:
            score += 0.2
        
        # Processing time efficiency (<1000ms is good)
        processing_time = result.get("processing_time_ms", 0)
        if processing_time < 1000:
            score += 0.2
        
        return score
    
    async def _update_metrics(self, results: List[Dict[str, Any]]):
        """Update swarm performance metrics"""
        if not results:
            return
        
        # Processing time
        processing_times = [r.get("processing_time_ms", 0) for r in results]
        avg_time = sum(processing_times) / len(processing_times)
        
        # Success rate
        successful = len([r for r in results if r.get("risk_score", 0) > 0])
        success_rate = successful / len(results)
        
        # Update metrics
        self.metrics.update({
            "tasks_processed": self.metrics["tasks_processed"] + len(results),
            "avg_processing_time": avg_time,
            "success_rate": success_rate,
            "last_updated": datetime.utcnow().isoformat()
        })
    
    async def get_swarm_status(self) -> Dict[str, Any]:
        """Get current swarm status"""
        try:
            health_data = await self.redis_pool.get("swarm:health")
            if health_data:
                return json.loads(health_data)
            
            return {
                "status": "unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            } 