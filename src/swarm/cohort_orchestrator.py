"""
Ford Bayesian Risk Score Engine - Cohort-Aware Swarm Orchestrator

Enhanced orchestrator that:
- Integrates cohorts.json academic data 
- Provides cohort-specific worker scaling
- Manages dynamic cohort updates
- Optimizes processing by cohort groups
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import redis.asyncio as redis

from ..models.schemas import VehicleInputData, RiskScoreOutput, ProcessingTask
from ..models.cohort_schemas import CohortDefinition, CohortMatchResult
from ..services.cohort_service import CohortService
from ..engines.bayesian_engine import BayesianRiskEngine


logger = logging.getLogger(__name__)


@dataclass
class CohortWorkload:
    """Workload distribution by cohort"""
    cohort_id: str
    pending_vehicles: int
    processing_vehicles: int
    completed_vehicles: int
    avg_processing_time: float
    specialized_workers: int
    
    @property
    def total_vehicles(self) -> int:
        return self.pending_vehicles + self.processing_vehicles + self.completed_vehicles
    
    @property
    def completion_rate(self) -> float:
        if self.total_vehicles == 0:
            return 0.0
        return self.completed_vehicles / self.total_vehicles


class CohortOrchestrator:
    """
    Enhanced orchestrator with cohort-aware processing and academic data integration
    """
    
    def __init__(self, 
                 redis_client: redis.Redis,
                 cohort_service: CohortService,
                 bayesian_engine: BayesianRiskEngine):
        self.redis_client = redis_client
        self.cohort_service = cohort_service
        self.bayesian_engine = bayesian_engine
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Cohort-specific worker pools
        self.cohort_workers: Dict[str, Set[str]] = {}
        self.cohort_workloads: Dict[str, CohortWorkload] = {}
        
        # Performance tracking
        self.cohort_metrics: Dict[str, Dict] = {}
        
    async def initialize(self) -> None:
        """Initialize cohort orchestrator"""
        try:
            # Initialize cohort service
            await self.cohort_service.initialize()
            
            # Load all cohorts and initialize worker pools
            cohorts = await self.cohort_service.get_all_cohorts()
            for cohort in cohorts:
                self.cohort_workers[cohort.cohort_id] = set()
                self.cohort_workloads[cohort.cohort_id] = CohortWorkload(
                    cohort_id=cohort.cohort_id,
                    pending_vehicles=0,
                    processing_vehicles=0,
                    completed_vehicles=0,
                    avg_processing_time=0.0,
                    specialized_workers=0
                )
                self.cohort_metrics[cohort.cohort_id] = {
                    "total_processed": 0,
                    "avg_risk_score": 0.0,
                    "dominant_stressors": {},
                    "revenue_generated": 0.0
                }
            
            self.logger.info(f"Cohort orchestrator initialized with {len(cohorts)} cohorts")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cohort orchestrator: {str(e)}")
            raise
    
    async def process_vehicle_batch(self, vehicles: List[VehicleInputData]) -> List[RiskScoreOutput]:
        """Process vehicle batch with cohort-aware optimization"""
        start_time = datetime.utcnow()
        
        # Step 1: Group vehicles by cohort for optimized processing
        cohort_groups = await self._group_vehicles_by_cohort(vehicles)
        
        # Step 2: Allocate workers based on cohort workload
        await self._allocate_cohort_workers(cohort_groups)
        
        # Step 3: Process each cohort group
        all_results = []
        processing_tasks = []
        
        for cohort_id, vehicle_group in cohort_groups.items():
            task = asyncio.create_task(
                self._process_cohort_group(cohort_id, vehicle_group)
            )
            processing_tasks.append(task)
        
        # Step 4: Gather all results
        cohort_results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        for result in cohort_results:
            if isinstance(result, Exception):
                self.logger.error(f"Cohort processing failed: {str(result)}")
            else:
                all_results.extend(result)
        
        # Step 5: Update metrics and workload tracking
        await self._update_cohort_metrics(cohort_groups, all_results)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        self.logger.info(f"Processed {len(all_results)} vehicles across {len(cohort_groups)} cohorts in {processing_time:.2f}s")
        
        return all_results
    
    async def _group_vehicles_by_cohort(self, vehicles: List[VehicleInputData]) -> Dict[str, List[VehicleInputData]]:
        """Group vehicles by their matched cohort"""
        cohort_groups = {}
        
        # Process in parallel for speed
        match_tasks = [
            self.cohort_service.match_cohort(vehicle.vin, vehicle) 
            for vehicle in vehicles
        ]
        
        matches = await asyncio.gather(*match_tasks, return_exceptions=True)
        
        for vehicle, match_result in zip(vehicles, matches):
            if isinstance(match_result, Exception):
                self.logger.warning(f"Failed to match cohort for {vehicle.vin}, using fallback")
                cohort_id = "lighttruck_midwest_winter"  # Fallback cohort
            else:
                cohort_id = match_result.matched_cohort_id
            
            if cohort_id not in cohort_groups:
                cohort_groups[cohort_id] = []
            
            cohort_groups[cohort_id].append(vehicle)
        
        # Log distribution
        for cohort_id, group in cohort_groups.items():
            self.logger.info(f"Cohort {cohort_id}: {len(group)} vehicles")
        
        return cohort_groups
    
    async def _allocate_cohort_workers(self, cohort_groups: Dict[str, List[VehicleInputData]]) -> None:
        """Dynamically allocate workers based on cohort workload"""
        total_vehicles = sum(len(group) for group in cohort_groups.values())
        
        for cohort_id, vehicle_group in cohort_groups.items():
            workload_ratio = len(vehicle_group) / total_vehicles
            
            # Update workload tracking
            if cohort_id in self.cohort_workloads:
                self.cohort_workloads[cohort_id].pending_vehicles = len(vehicle_group)
            
            # Calculate optimal worker allocation
            base_workers = max(1, int(workload_ratio * 8))  # Scale to available workers
            
            # Adjust based on cohort complexity (more stressors = more processing time)
            cohort_def = await self.cohort_service.get_cohort_by_id(cohort_id)
            if cohort_def:
                complexity_multiplier = min(1.5, len(cohort_def.likelihood_ratios) / 4)
                optimal_workers = max(1, int(base_workers * complexity_multiplier))
            else:
                optimal_workers = base_workers
            
            self.logger.debug(f"Allocated {optimal_workers} workers for cohort {cohort_id} ({len(vehicle_group)} vehicles)")
    
    async def _process_cohort_group(self, cohort_id: str, vehicles: List[VehicleInputData]) -> List[RiskScoreOutput]:
        """Process a group of vehicles from the same cohort"""
        start_time = datetime.utcnow()
        
        # Update processing status
        if cohort_id in self.cohort_workloads:
            self.cohort_workloads[cohort_id].processing_vehicles = len(vehicles)
            self.cohort_workloads[cohort_id].pending_vehicles = 0
        
        try:
            # Process vehicles in parallel
            processing_tasks = [
                self.bayesian_engine.calculate_risk_score(vehicle)
                for vehicle in vehicles
            ]
            
            results = await asyncio.gather(*processing_tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to process vehicle {vehicles[i].vin}: {str(result)}")
                else:
                    valid_results.append(result)
            
            # Update completion status
            if cohort_id in self.cohort_workloads:
                self.cohort_workloads[cohort_id].processing_vehicles = 0
                self.cohort_workloads[cohort_id].completed_vehicles += len(valid_results)
                
                # Update average processing time
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                self.cohort_workloads[cohort_id].avg_processing_time = processing_time / len(vehicles)
            
            self.logger.info(f"Cohort {cohort_id}: Processed {len(valid_results)}/{len(vehicles)} vehicles successfully")
            
            return valid_results
            
        except Exception as e:
            self.logger.error(f"Failed to process cohort group {cohort_id}: {str(e)}")
            return []
    
    async def _update_cohort_metrics(self, 
                                   cohort_groups: Dict[str, List[VehicleInputData]], 
                                   results: List[RiskScoreOutput]) -> None:
        """Update performance metrics for each cohort"""
        
        # Group results by cohort
        results_by_cohort = {}
        for result in results:
            cohort_id = result.cohort
            if cohort_id not in results_by_cohort:
                results_by_cohort[cohort_id] = []
            results_by_cohort[cohort_id].append(result)
        
        # Update metrics
        for cohort_id, cohort_results in results_by_cohort.items():
            if cohort_id not in self.cohort_metrics:
                continue
            
            metrics = self.cohort_metrics[cohort_id]
            
            # Update totals
            metrics["total_processed"] += len(cohort_results)
            
            # Calculate average risk score
            risk_scores = [float(result.risk_score) for result in cohort_results]
            if risk_scores:
                metrics["avg_risk_score"] = sum(risk_scores) / len(risk_scores)
            
            # Track dominant stressors
            for result in cohort_results:
                for stressor in result.dominant_stressors:
                    if stressor not in metrics["dominant_stressors"]:
                        metrics["dominant_stressors"][stressor] = 0
                    metrics["dominant_stressors"][stressor] += 1
            
            # Calculate revenue
            revenue = sum(float(result.revenue_opportunity) for result in cohort_results)
            metrics["revenue_generated"] += revenue
            
            # Cache updated metrics in Redis
            await self.redis_client.hset(
                "cohort_metrics",
                cohort_id,
                json.dumps(metrics)
            )
    
    async def get_cohort_performance_summary(self) -> Dict:
        """Get performance summary across all cohorts"""
        summary = {
            "total_cohorts": len(self.cohort_workloads),
            "cohort_details": {},
            "overall_metrics": {
                "total_vehicles_processed": 0,
                "avg_processing_time": 0.0,
                "total_revenue_opportunity": 0.0
            }
        }
        
        total_processing_time = 0.0
        total_vehicles = 0
        
        for cohort_id, workload in self.cohort_workloads.items():
            # Get cohort definition for context
            cohort_def = await self.cohort_service.get_cohort_by_id(cohort_id)
            metrics = self.cohort_metrics.get(cohort_id, {})
            
            cohort_summary = {
                "workload": {
                    "total_vehicles": workload.total_vehicles,
                    "completion_rate": workload.completion_rate,
                    "avg_processing_time": workload.avg_processing_time
                },
                "performance": metrics,
                "configuration": {
                    "prior_rate": cohort_def.prior if cohort_def else 0.0,
                    "num_stressors": len(cohort_def.likelihood_ratios) if cohort_def else 0,
                    "models_covered": cohort_def.models if cohort_def else [],
                    "academic_source": cohort_def.prior_source if cohort_def else "Unknown"
                }
            }
            
            summary["cohort_details"][cohort_id] = cohort_summary
            
            # Aggregate overall metrics
            total_vehicles += workload.total_vehicles
            total_processing_time += workload.avg_processing_time * workload.total_vehicles
            summary["overall_metrics"]["total_revenue_opportunity"] += metrics.get("revenue_generated", 0.0)
        
        # Calculate overall averages
        if total_vehicles > 0:
            summary["overall_metrics"]["total_vehicles_processed"] = total_vehicles
            summary["overall_metrics"]["avg_processing_time"] = total_processing_time / total_vehicles
        
        return summary
    
    async def hot_reload_cohorts(self) -> Dict:
        """Hot-reload cohorts without stopping processing"""
        try:
            self.logger.info("Starting hot reload of cohort definitions...")
            
            # Refresh cohort service
            await self.cohort_service.refresh_cohorts()
            
            # Get updated cohorts
            updated_cohorts = await self.cohort_service.get_all_cohorts()
            
            # Update worker pools for new cohorts
            for cohort in updated_cohorts:
                if cohort.cohort_id not in self.cohort_workers:
                    self.cohort_workers[cohort.cohort_id] = set()
                    self.cohort_workloads[cohort.cohort_id] = CohortWorkload(
                        cohort_id=cohort.cohort_id,
                        pending_vehicles=0,
                        processing_vehicles=0,
                        completed_vehicles=0,
                        avg_processing_time=0.0,
                        specialized_workers=0
                    )
                    self.cohort_metrics[cohort.cohort_id] = {
                        "total_processed": 0,
                        "avg_risk_score": 0.0,
                        "dominant_stressors": {},
                        "revenue_generated": 0.0
                    }
            
            self.logger.info(f"Hot reload completed successfully. {len(updated_cohorts)} cohorts active.")
            
            return {
                "status": "success",
                "cohorts_loaded": len(updated_cohorts),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Hot reload failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_cohort_health_check(self) -> Dict:
        """Health check for all cohort processing"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "cohorts": {}
        }
        
        for cohort_id, workload in self.cohort_workloads.items():
            cohort_health = {
                "status": "healthy",
                "workload_utilization": 0.0,
                "avg_processing_time": workload.avg_processing_time,
                "completion_rate": workload.completion_rate
            }
            
            # Check for unhealthy conditions
            if workload.avg_processing_time > 5.0:  # > 5 seconds per vehicle
                cohort_health["status"] = "slow"
                health_status["status"] = "degraded"
            
            if workload.completion_rate < 0.95:  # < 95% completion rate
                cohort_health["status"] = "failing"
                health_status["status"] = "unhealthy"
            
            health_status["cohorts"][cohort_id] = cohort_health
        
        return health_status 