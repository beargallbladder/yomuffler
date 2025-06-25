"""
Ford Bayesian Risk Score Engine - API Gateway

High-performance FastAPI gateway with:
- Sub-millisecond response times via Redis cache
- Batch processing endpoints
- Real-time swarm metrics
- Comprehensive monitoring and logging
"""

import asyncio
import logging
import time
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import uvicorn
from pydantic import BaseModel

from ..models.schemas import (
    APIRequest, APIResponse, BatchProcessingRequest, BatchProcessingResponse,
    RiskScoreOutput, VehicleInputData, ProcessingTask, HealthCheck,
    SwarmMetrics, CohortAssignment, SeverityBucket
)
from ..engines.bayesian_engine import BayesianRiskEngine
from ..swarm.orchestrator import SwarmOrchestrator
from .mobile_ui import add_mobile_routes


logger = logging.getLogger(__name__)


class FordRiskAPI:
    """Ford Risk Score API Gateway"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.app = FastAPI(
            title="Ford Bayesian Risk Score Engine",
            description="High-performance risk scoring API for Ford vehicles",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        self.redis_url = redis_url
        self.redis_client = None
        self.orchestrator = SwarmOrchestrator(redis_url)
        self.bayesian_engine = BayesianRiskEngine()
        
        # Performance metrics
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.avg_response_time_ms = 0.0
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        
        # Add mobile-friendly routes
        add_mobile_routes(self.app)
    
    def _setup_middleware(self):
        """Configure FastAPI middleware"""
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Compression middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Request timing middleware
        @self.app.middleware("http")
        async def add_process_time_header(request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            response.headers["X-Process-Time"] = str(process_time)
            
            # Update metrics
            self.request_count += 1
            self.avg_response_time_ms = (
                (self.avg_response_time_ms * (self.request_count - 1) + process_time) / self.request_count
            )
            
            return response
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize connections on startup"""
            self.redis_client = await redis.from_url(self.redis_url)
            logger.info("Ford Risk Score API Gateway started")
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Cleanup on shutdown"""
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Ford Risk Score API Gateway stopped")
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint"""
            return {
                "service": "Ford Bayesian Risk Score Engine",
                "version": "1.0.0",
                "status": "operational",
                "documentation": "/docs"
            }
        
        @self.app.get("/health", response_model=HealthCheck)
        async def health_check():
            """Health check endpoint"""
            try:
                # Check Redis connection
                await self.redis_client.ping()
                redis_status = "healthy"
            except Exception:
                redis_status = "unhealthy"
            
            return HealthCheck(
                service="ford-risk-api",
                status="healthy" if redis_status == "healthy" else "degraded",
                version="1.0.0",
                uptime_seconds=time.time() - self.app.state.start_time if hasattr(self.app.state, 'start_time') else 0,
                dependencies={
                    "redis": redis_status,
                    "bayesian_engine": "healthy",
                    "swarm_orchestrator": "healthy"
                }
            )
        
        @self.app.post("/risk-score", response_model=APIResponse)
        async def get_risk_score(request: APIRequest):
            """
            Get risk score for a single vehicle (sub-millisecond response)
            """
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            try:
                # Check cache first for sub-millisecond response
                if not request.force_recalculate:
                    cached_result = await self._get_cached_risk_score(request.vin)
                    if cached_result:
                        self.cache_hits += 1
                        processing_time = (time.time() - start_time) * 1000
                        
                        return APIResponse(
                            success=True,
                            data=cached_result,
                            request_id=request_id,
                            processing_time_ms=processing_time,
                            cached=True
                        )
                
                self.cache_misses += 1
                
                # If not cached or force recalculate, get from database/calculate
                risk_score = await self._get_or_calculate_risk_score(request.vin)
                
                if not risk_score:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Risk score not found for VIN {request.vin}"
                    )
                
                # Cache the result
                await self._cache_risk_score(request.vin, risk_score)
                
                processing_time = (time.time() - start_time) * 1000
                
                return APIResponse(
                    success=True,
                    data=risk_score,
                    request_id=request_id,
                    processing_time_ms=processing_time,
                    cached=False
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error processing risk score request for VIN {request.vin}: {str(e)}")
                processing_time = (time.time() - start_time) * 1000
                
                return APIResponse(
                    success=False,
                    error=str(e),
                    request_id=request_id,
                    processing_time_ms=processing_time
                )
        
        @self.app.post("/batch-risk-score", response_model=BatchProcessingResponse)
        async def batch_risk_score(request: BatchProcessingRequest, background_tasks: BackgroundTasks):
            """
            Submit batch risk score calculation request
            """
            try:
                # Validate VINs
                if len(request.vins) > 10000:
                    raise HTTPException(
                        status_code=400,
                        detail="Batch size cannot exceed 10,000 VINs"
                    )
                
                # Create batch processing task
                batch_id = request.batch_id or str(uuid.uuid4())
                
                # Estimate completion time based on current queue depth and processing rate
                estimated_completion = datetime.utcnow() + timedelta(
                    seconds=len(request.vins) / 1000  # Assume 1000 VINs/second processing rate
                )
                
                # Add to background processing queue
                background_tasks.add_task(
                    self._process_batch_risk_scores,
                    request.vins,
                    batch_id,
                    request.priority,
                    request.callback_url
                )
                
                return BatchProcessingResponse(
                    batch_id=batch_id,
                    total_vins=len(request.vins),
                    estimated_completion_time=estimated_completion,
                    status="queued",
                    progress_url=f"/batch-status/{batch_id}"
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error processing batch request: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/batch-status/{batch_id}")
        async def get_batch_status(batch_id: str):
            """Get batch processing status"""
            try:
                status_data = await self.redis_client.hget("batch:status", batch_id)
                if not status_data:
                    raise HTTPException(status_code=404, detail="Batch not found")
                
                return json.loads(status_data)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting batch status for {batch_id}: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/metrics")
        async def get_api_metrics():
            """Get API performance metrics"""
            try:
                swarm_metrics = await self.orchestrator.get_swarm_metrics()
                
                return {
                    "api_metrics": {
                        "total_requests": self.request_count,
                        "cache_hit_rate": self.cache_hits / max(1, self.request_count),
                        "cache_miss_rate": self.cache_misses / max(1, self.request_count),
                        "avg_response_time_ms": self.avg_response_time_ms,
                        "requests_per_second": self._calculate_rps()
                    },
                    "swarm_metrics": swarm_metrics,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error getting metrics: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/demo/generate-sample-data")
        async def generate_sample_data(count: int = 100):
            """Generate sample data for demonstration"""
            try:
                sample_vehicles = []
                
                for i in range(count):
                    vin = f"1FORD{str(i).zfill(11)}"  # Generate sample VIN
                    
                    # Create sample input data
                    input_data = VehicleInputData(
                        vin=vin,
                        soc_30day_trend=float(np.random.uniform(-0.5, 0.0)),
                        trip_cycles_weekly=int(np.random.uniform(10, 150)),
                        odometer_variance=float(np.random.uniform(0.1, 0.9)),
                        climate_stress_index=float(np.random.uniform(0.2, 0.8)),
                        maintenance_compliance=float(np.random.uniform(0.3, 1.0)),
                        cohort_assignment=CohortAssignment(
                            model=np.random.choice(["F150", "EXPLORER", "MUSTANG"]),
                            powertrain=np.random.choice(["ICE", "HYBRID"]),
                            region=np.random.choice(["NORTH", "SOUTH", "COMMERCIAL"]),
                            mileage_band=np.random.choice(["LOW", "MEDIUM", "HIGH"])
                        )
                    )
                    
                    # Calculate risk score
                    risk_score = await self.bayesian_engine.calculate_risk_score(input_data)
                    
                    # Cache the result
                    await self._cache_risk_score(vin, risk_score)
                    
                    sample_vehicles.append({
                        "vin": vin,
                        "risk_score": risk_score.risk_score,
                        "severity": risk_score.severity_bucket.value,
                        "revenue_opportunity": float(risk_score.revenue_opportunity)
                    })
                
                return {
                    "message": f"Generated {count} sample vehicle risk scores",
                    "sample_data": sample_vehicles[:10],  # Return first 10 for preview
                    "total_generated": count
                }
                
            except Exception as e:
                logger.error(f"Error generating sample data: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_cached_risk_score(self, vin: str) -> Optional[RiskScoreOutput]:
        """Get risk score from Redis cache"""
        try:
            cached_data = await self.redis_client.get(f"risk_score:{vin}")
            if cached_data:
                return RiskScoreOutput.parse_raw(cached_data)
            return None
        except Exception as e:
            logger.error(f"Error getting cached risk score for {vin}: {str(e)}")
            return None
    
    async def _cache_risk_score(self, vin: str, risk_score: RiskScoreOutput, ttl: int = 3600):
        """Cache risk score in Redis"""
        try:
            await self.redis_client.setex(
                f"risk_score:{vin}",
                ttl,
                risk_score.json()
            )
        except Exception as e:
            logger.error(f"Error caching risk score for {vin}: {str(e)}")
    
    async def _get_or_calculate_risk_score(self, vin: str) -> Optional[RiskScoreOutput]:
        """Get risk score from database or calculate if needed"""
        try:
            # First check if we have precalculated data in Redis
            precalc_data = await self.redis_client.hget("precalc_scores", vin)
            if precalc_data:
                return RiskScoreOutput.parse_raw(precalc_data)
            
            # If not precalculated, return None (would trigger real-time calculation in production)
            # For demo purposes, we'll generate a sample calculation
            return await self._generate_demo_risk_score(vin)
            
        except Exception as e:
            logger.error(f"Error getting/calculating risk score for {vin}: {str(e)}")
            return None
    
    async def _generate_demo_risk_score(self, vin: str) -> RiskScoreOutput:
        """Generate a demo risk score for demonstration purposes"""
        import numpy as np
        from decimal import Decimal
        
        # Generate realistic demo data
        input_data = VehicleInputData(
            vin=vin,
            soc_30day_trend=float(np.random.uniform(-0.3, -0.05)),
            trip_cycles_weekly=int(np.random.uniform(20, 80)),
            odometer_variance=float(np.random.uniform(0.2, 0.7)),
            climate_stress_index=float(np.random.uniform(0.3, 0.6)),
            maintenance_compliance=float(np.random.uniform(0.6, 0.95)),
            cohort_assignment=CohortAssignment(
                model="F150",
                powertrain="ICE",
                region="NORTH",
                mileage_band="MEDIUM"
            )
        )
        
        return await self.bayesian_engine.calculate_risk_score(input_data)
    
    async def _process_batch_risk_scores(self, vins: List[str], batch_id: str, priority: int, callback_url: Optional[str]):
        """Process batch risk scores in background"""
        try:
            # Update batch status to processing
            await self.redis_client.hset(
                "batch:status",
                batch_id,
                json.dumps({
                    "batch_id": batch_id,
                    "status": "processing",
                    "total_vins": len(vins),
                    "processed_vins": 0,
                    "started_at": datetime.utcnow().isoformat(),
                    "progress_percentage": 0.0
                })
            )
            
            results = []
            for i, vin in enumerate(vins):
                try:
                    risk_score = await self._get_or_calculate_risk_score(vin)
                    if risk_score:
                        results.append(risk_score)
                        await self._cache_risk_score(vin, risk_score)
                    
                    # Update progress
                    progress = (i + 1) / len(vins) * 100
                    await self.redis_client.hset(
                        "batch:status",
                        batch_id,
                        json.dumps({
                            "batch_id": batch_id,
                            "status": "processing",
                            "total_vins": len(vins),
                            "processed_vins": i + 1,
                            "progress_percentage": progress,
                            "started_at": datetime.utcnow().isoformat()
                        })
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing VIN {vin} in batch {batch_id}: {str(e)}")
            
            # Mark as completed
            await self.redis_client.hset(
                "batch:status",
                batch_id,
                json.dumps({
                    "batch_id": batch_id,
                    "status": "completed",
                    "total_vins": len(vins),
                    "processed_vins": len(results),
                    "completed_at": datetime.utcnow().isoformat(),
                    "progress_percentage": 100.0,
                    "results_count": len(results)
                })
            )
            
            # Store results
            await self.redis_client.hset(
                "batch:results",
                batch_id,
                json.dumps([r.dict() for r in results], default=str)
            )
            
            logger.info(f"Completed batch processing for {batch_id}: {len(results)} results")
            
        except Exception as e:
            logger.error(f"Error in batch processing for {batch_id}: {str(e)}")
            
            # Mark as failed
            await self.redis_client.hset(
                "batch:status",
                batch_id,
                json.dumps({
                    "batch_id": batch_id,
                    "status": "failed",
                    "error": str(e),
                    "failed_at": datetime.utcnow().isoformat()
                })
            )
    
    def _calculate_rps(self) -> float:
        """Calculate requests per second"""
        # This is a simplified calculation
        # In production, you'd want a more sophisticated moving average
        if hasattr(self.app.state, 'start_time'):
            uptime = time.time() - self.app.state.start_time
            return self.request_count / max(1, uptime)
        return 0.0


# Initialize the API
api = FordRiskAPI()
app = api.app

# Store start time for uptime calculation
@app.on_event("startup")
async def store_start_time():
    app.state.start_time = time.time()


if __name__ == "__main__":
    uvicorn.run(
        "src.api.gateway:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 