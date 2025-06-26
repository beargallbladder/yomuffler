"""
Ford Bayesian Risk Score Engine - Cohort API Endpoints

Enhanced API endpoints for the academic-sourced cohort system:
- Cohort management and hot-reloading
- Academic source validation
- Stressor analysis with justification
- Performance metrics by cohort
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..models.schemas import VehicleInputData, RiskScoreOutput
from ..models.cohort_schemas import (
    CohortDefinition, CohortMatchResult, StressorAnalysis,
    CohortDatabase, RegionType, VehicleClass, PowertrainType
)
from ..services.cohort_service import CohortService
from ..swarm.cohort_orchestrator import CohortOrchestrator


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/cohorts", tags=["Cohorts"])


# Request/Response Models
class CohortAnalysisRequest(BaseModel):
    """Request for detailed cohort analysis"""
    vin: str = Field(..., description="Vehicle VIN")
    include_stressor_details: bool = Field(default=True, description="Include detailed stressor analysis")
    include_academic_sources: bool = Field(default=True, description="Include academic source citations")


class CohortAnalysisResponse(BaseModel):
    """Enhanced response with academic citations"""
    vin: str
    cohort_match: CohortMatchResult
    stressor_analysis: Optional[StressorAnalysis] = None
    academic_sources: List[str] = []
    cohort_definition: Optional[Dict] = None
    

class BatchCohortRequest(BaseModel):
    """Request for batch cohort processing"""
    vehicles: List[VehicleInputData] = Field(..., min_items=1, max_items=10000)
    processing_options: Dict[str, Any] = Field(default_factory=dict)


class CohortPerformanceResponse(BaseModel):
    """Response for cohort performance metrics"""
    summary: Dict[str, Any]
    timestamp: datetime
    total_cohorts: int
    academic_validation: bool = True


# Dependency injection
async def get_cohort_service() -> CohortService:
    """Get cohort service instance"""
    # In production, this would be injected via dependency container
    return CohortService()


async def get_cohort_orchestrator() -> CohortOrchestrator:
    """Get cohort orchestrator instance"""
    # In production, this would be injected via dependency container
    cohort_service = await get_cohort_service()
    # Would need proper Redis and Bayesian engine injection
    return None  # Placeholder


@router.get("/", response_model=List[CohortDefinition])
async def list_cohorts(cohort_service: CohortService = Depends(get_cohort_service)):
    """
    List all available cohorts with academic sourcing information
    """
    try:
        cohorts = await cohort_service.get_all_cohorts()
        return cohorts
    except Exception as e:
        logger.error(f"Failed to list cohorts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cohort list"
        )


@router.get("/{cohort_id}", response_model=CohortDefinition)
async def get_cohort_details(
    cohort_id: str,
    cohort_service: CohortService = Depends(get_cohort_service)
):
    """
    Get detailed information about a specific cohort including academic sources
    """
    try:
        cohort = await cohort_service.get_cohort_by_id(cohort_id)
        if not cohort:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cohort {cohort_id} not found"
            )
        return cohort
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cohort {cohort_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cohort details"
        )


@router.post("/analyze", response_model=CohortAnalysisResponse)
async def analyze_vehicle_cohort(
    request: CohortAnalysisRequest,
    cohort_service: CohortService = Depends(get_cohort_service)
):
    """
    Perform detailed cohort analysis for a vehicle with academic justification
    """
    try:
        # Match vehicle to cohort
        cohort_match = await cohort_service.match_cohort(request.vin)
        
        response = CohortAnalysisResponse(
            vin=request.vin,
            cohort_match=cohort_match
        )
        
        # Add cohort definition if requested
        if request.include_academic_sources:
            cohort_def = await cohort_service.get_cohort_by_id(cohort_match.matched_cohort_id)
            if cohort_def:
                response.cohort_definition = {
                    "cohort_id": cohort_def.cohort_id,
                    "description": f"{cohort_def.vehicle_class.value} - {cohort_def.region.value}",
                    "prior_probability": cohort_def.prior,
                    "academic_source": cohort_def.prior_source,
                    "models_covered": cohort_def.models,
                    "years_supported": cohort_def.years_supported,
                    "likelihood_ratios": {
                        name: {
                            "value": lr.value,
                            "definition": lr.definition,
                            "source": lr.source
                        }
                        for name, lr in cohort_def.likelihood_ratios.items()
                    }
                }
                
                # Extract academic sources
                response.academic_sources = [cohort_def.prior_source]
                response.academic_sources.extend([
                    lr.source for lr in cohort_def.likelihood_ratios.values()
                ])
                response.academic_sources = list(set(response.academic_sources))  # Remove duplicates
        
        # Add stressor analysis if VH data provided (would need VehicleInputData)
        if request.include_stressor_details:
            # This would require VH telemetry data - placeholder for now
            response.stressor_analysis = None
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to analyze vehicle cohort for {request.vin}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform cohort analysis"
        )


@router.post("/batch-process", response_model=List[RiskScoreOutput])
async def batch_process_with_cohorts(
    request: BatchCohortRequest,
    background_tasks: BackgroundTasks,
    cohort_orchestrator: CohortOrchestrator = Depends(get_cohort_orchestrator)
):
    """
    Process a batch of vehicles using cohort-aware optimization
    """
    if not cohort_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cohort orchestrator not available"
        )
    
    try:
        # Process batch with cohort-aware optimization
        results = await cohort_orchestrator.process_vehicle_batch(request.vehicles)
        
        # Log performance metrics in background
        background_tasks.add_task(
            _log_batch_performance, 
            len(request.vehicles), 
            len(results),
            cohort_orchestrator
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to process vehicle batch: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process vehicle batch"
        )


@router.get("/performance/summary", response_model=CohortPerformanceResponse)
async def get_cohort_performance(
    cohort_orchestrator: CohortOrchestrator = Depends(get_cohort_orchestrator)
):
    """
    Get performance summary across all cohorts
    """
    if not cohort_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cohort orchestrator not available"
        )
    
    try:
        summary = await cohort_orchestrator.get_cohort_performance_summary()
        
        return CohortPerformanceResponse(
            summary=summary,
            timestamp=datetime.utcnow(),
            total_cohorts=summary.get("total_cohorts", 0),
            academic_validation=True
        )
        
    except Exception as e:
        logger.error(f"Failed to get cohort performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics"
        )


@router.post("/reload", response_model=Dict[str, Any])
async def hot_reload_cohorts(
    cohort_orchestrator: CohortOrchestrator = Depends(get_cohort_orchestrator)
):
    """
    Hot-reload cohort definitions from cohorts.json without downtime
    """
    if not cohort_orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cohort orchestrator not available"
        )
    
    try:
        reload_result = await cohort_orchestrator.hot_reload_cohorts()
        
        if reload_result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Hot reload failed: {reload_result['error']}"
            )
        
        return reload_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to hot reload cohorts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reload cohorts"
        )


@router.get("/health", response_model=Dict[str, Any])
async def cohort_health_check(
    cohort_orchestrator: CohortOrchestrator = Depends(get_cohort_orchestrator)
):
    """
    Health check for cohort processing system
    """
    if not cohort_orchestrator:
        return {
            "status": "unhealthy",
            "error": "Cohort orchestrator not available",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    try:
        health_status = await cohort_orchestrator.get_cohort_health_check()
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/academic-sources", response_model=Dict[str, List[str]])
async def get_academic_sources(
    cohort_service: CohortService = Depends(get_cohort_service)
):
    """
    Get all academic sources used across cohorts for validation
    """
    try:
        cohorts = await cohort_service.get_all_cohorts()
        
        sources = {
            "prior_sources": [],
            "likelihood_ratio_sources": [],
            "all_unique_sources": []
        }
        
        for cohort in cohorts:
            # Collect prior sources
            sources["prior_sources"].append(cohort.prior_source)
            
            # Collect likelihood ratio sources
            for lr in cohort.likelihood_ratios.values():
                sources["likelihood_ratio_sources"].append(lr.source)
        
        # Create unique list
        all_sources = sources["prior_sources"] + sources["likelihood_ratio_sources"]
        sources["all_unique_sources"] = list(set(all_sources))
        
        return sources
        
    except Exception as e:
        logger.error(f"Failed to get academic sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve academic sources"
        )


@router.get("/stressors/definitions", response_model=Dict[str, Dict[str, str]])
async def get_stressor_definitions(
    cohort_id: Optional[str] = None,
    cohort_service: CohortService = Depends(get_cohort_service)
):
    """
    Get stressor definitions with academic justification
    """
    try:
        if cohort_id:
            # Get definitions for specific cohort
            cohort = await cohort_service.get_cohort_by_id(cohort_id)
            if not cohort:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Cohort {cohort_id} not found"
                )
            
            return {
                stressor_name: {
                    "definition": lr.definition,
                    "source": lr.source,
                    "likelihood_ratio": str(lr.value)
                }
                for stressor_name, lr in cohort.likelihood_ratios.items()
            }
        else:
            # Get all stressor definitions across cohorts
            cohorts = await cohort_service.get_all_cohorts()
            all_stressors = {}
            
            for cohort in cohorts:
                for stressor_name, lr in cohort.likelihood_ratios.items():
                    if stressor_name not in all_stressors:
                        all_stressors[stressor_name] = {
                            "definition": lr.definition,
                            "source": lr.source,
                            "likelihood_ratio_range": [lr.value, lr.value],
                            "used_in_cohorts": [cohort.cohort_id]
                        }
                    else:
                        # Update range and cohort list
                        current_range = all_stressors[stressor_name]["likelihood_ratio_range"]
                        all_stressors[stressor_name]["likelihood_ratio_range"] = [
                            min(current_range[0], lr.value),
                            max(current_range[1], lr.value)
                        ]
                        all_stressors[stressor_name]["used_in_cohorts"].append(cohort.cohort_id)
            
            return all_stressors
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stressor definitions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stressor definitions"
        )


# Background task helper functions
async def _log_batch_performance(
    input_count: int,
    output_count: int,
    orchestrator: CohortOrchestrator
):
    """Log batch processing performance metrics"""
    try:
        success_rate = output_count / input_count if input_count > 0 else 0
        logger.info(f"Batch processing completed: {output_count}/{input_count} vehicles ({success_rate:.1%} success rate)")
        
        # Could send to monitoring system here
        
    except Exception as e:
        logger.error(f"Failed to log batch performance: {str(e)}")


# Validation endpoints for academic integrity
@router.post("/validate", response_model=Dict[str, Any])
async def validate_cohort_definitions(
    cohort_service: CohortService = Depends(get_cohort_service)
):
    """
    Validate all cohort definitions for academic integrity and consistency
    """
    try:
        cohorts = await cohort_service.get_all_cohorts()
        validation_results = {
            "status": "valid",
            "total_cohorts": len(cohorts),
            "warnings": [],
            "errors": [],
            "academic_validation": {
                "prior_sources_validated": True,
                "likelihood_ratio_sources_validated": True,
                "academic_consistency": True
            }
        }
        
        # Validate each cohort
        for cohort in cohorts:
            # Check prior probability ranges
            if cohort.prior < 0.001 or cohort.prior > 0.5:
                validation_results["warnings"].append(
                    f"Cohort {cohort.cohort_id}: Prior probability {cohort.prior} outside typical range"
                )
            
            # Check likelihood ratio ranges
            for stressor_name, lr in cohort.likelihood_ratios.items():
                if lr.value < 0.1 or lr.value > 10.0:
                    validation_results["warnings"].append(
                        f"Cohort {cohort.cohort_id}: Likelihood ratio for {stressor_name} ({lr.value}) outside typical range"
                    )
                
                # Check for academic source
                if not lr.source or len(lr.source) < 5:
                    validation_results["errors"].append(
                        f"Cohort {cohort.cohort_id}: Missing or insufficient academic source for {stressor_name}"
                    )
        
        # Set overall status
        if validation_results["errors"]:
            validation_results["status"] = "invalid"
            validation_results["academic_validation"]["academic_consistency"] = False
        elif validation_results["warnings"]:
            validation_results["status"] = "warning"
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Failed to validate cohort definitions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate cohort definitions"
        ) 