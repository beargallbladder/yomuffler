"""
Ford Bayesian Risk Score Engine V2 - Academic-Sourced Implementation

This upgraded engine uses:
- Dynamic cohort matching from cohorts.json
- Academic-sourced priors (Argonne, BU, SAE standards)
- Cohort-specific likelihood ratios with full justification
- Hot-swappable cohort definitions
- Enhanced stressor analysis
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
from dataclasses import dataclass

from ..models.schemas import (
    VehicleInputData, RiskScoreOutput, RiskScoreMetadata,
    SeverityBucket, CohortAssignment
)
from ..models.cohort_schemas import CohortDefinition, StressorAnalysis
from ..services.cohort_service import CohortService


logger = logging.getLogger(__name__)


@dataclass
class BayesianCalculationTrace:
    """Detailed trace of Bayesian calculation for auditability"""
    vin: str
    cohort_id: str
    prior_probability: float
    prior_source: str
    active_stressors: List[str]
    likelihood_ratios: Dict[str, float]
    combined_likelihood_ratio: float
    posterior_probability: float
    calculation_method: str = "Bayesian Update with Academic Priors"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class BayesianRiskEngineV2:
    """
    Advanced Bayesian risk calculation engine using academic-sourced cohorts
    """
    
    def __init__(self, cohort_service: CohortService):
        self.cohort_service = cohort_service
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.model_version = "2.0-Academic"
        
        # Initialize cohort service
        asyncio.create_task(self.cohort_service.initialize())
        
    async def calculate_risk_score(self, input_data: VehicleInputData) -> RiskScoreOutput:
        """
        Calculate Bayesian risk score using academic-sourced cohort data
        
        Enhanced formula with cohort-specific parameters:
        P(Failure|Evidence) = P(Evidence|Failure) * P(Failure) / P(Evidence)
        
        Where:
        - P(Failure) comes from academic studies (Argonne, etc.)
        - P(Evidence|Failure) uses cohort-specific likelihood ratios
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Match vehicle to appropriate cohort
            cohort_match = await self.cohort_service.match_cohort(input_data.vin, input_data)
            cohort = await self.cohort_service.get_cohort_by_id(cohort_match.matched_cohort_id)
            
            if not cohort:
                raise ValueError(f"Failed to match vehicle {input_data.vin} to any cohort")
            
            # Step 2: Get academic-sourced prior probability
            prior_prob = cohort.prior
            
            # Step 3: Analyze vehicle stressors using cohort-specific definitions
            stressor_analysis = await self.cohort_service.analyze_vehicle_stressors(
                input_data.vin, input_data
            )
            
            # Step 4: Apply Bayesian update with cohort-specific likelihood ratios
            posterior_prob = self._bayesian_update(prior_prob, stressor_analysis.combined_likelihood_ratio)
            
            # Step 5: Determine severity and recommendations
            severity_bucket = self._classify_severity(posterior_prob)
            recommended_action = self._generate_recommendation(severity_bucket, stressor_analysis)
            revenue_opportunity = self._estimate_revenue_opportunity(severity_bucket, cohort)
            
            # Step 6: Calculate confidence with cohort match quality
            confidence = self._calculate_confidence(
                input_data, prior_prob, cohort_match.confidence, stressor_analysis
            )
            
            # Step 7: Create calculation trace for auditability
            trace = BayesianCalculationTrace(
                vin=input_data.vin,
                cohort_id=cohort.cohort_id,
                prior_probability=prior_prob,
                prior_source=cohort.prior_source,
                active_stressors=stressor_analysis.active_stressors,
                likelihood_ratios=stressor_analysis.stressor_contributions,
                combined_likelihood_ratio=stressor_analysis.combined_likelihood_ratio,
                posterior_probability=posterior_prob
            )
            
            # Step 8: Build enhanced metadata
            calculation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            metadata = RiskScoreMetadata(
                scored_at=start_time,
                prior_failure_rate=prior_prob,
                data_freshness=self._calculate_data_freshness(input_data.timestamp),
                model_version=self.model_version,
                calculation_time_ms=calculation_time
            )
            
            return RiskScoreOutput(
                vin=input_data.vin,
                risk_score=posterior_prob,
                severity_bucket=severity_bucket,
                cohort=cohort_match.matched_cohort_id,
                dominant_stressors=stressor_analysis.active_stressors,
                recommended_action=recommended_action,
                revenue_opportunity=revenue_opportunity,
                confidence=confidence,
                metadata=metadata,
                # Enhanced fields for V2
                cohort_match_confidence=cohort_match.confidence,
                academic_sources=self._extract_academic_sources(cohort, stressor_analysis),
                risk_factors=stressor_analysis.risk_factors,
                calculation_trace=trace
            )
            
        except Exception as e:
            self.logger.error(f"Risk calculation failed for VIN {input_data.vin}: {str(e)}")
            raise
    
    def _bayesian_update(self, prior: float, likelihood_ratio: float) -> float:
        """
        Apply Bayesian update using likelihood ratio form
        
        More numerically stable than direct probability form:
        Posterior odds = Prior odds × Likelihood ratio
        """
        # Convert to odds (handles edge cases better)
        prior_odds = prior / (1 - prior + 1e-10)  # Small epsilon to avoid division by zero
        
        # Apply likelihood ratio
        posterior_odds = prior_odds * likelihood_ratio
        
        # Convert back to probability
        posterior_prob = posterior_odds / (1 + posterior_odds)
        
        # Ensure bounds and handle edge cases
        return max(0.001, min(0.999, posterior_prob))
    
    def _classify_severity(self, risk_score: float) -> SeverityBucket:
        """Enhanced severity classification with academic justification"""
        # Thresholds based on Argonne study recommendations
        if risk_score >= 0.25:  # >25% annual failure probability
            return SeverityBucket.SEVERE
        elif risk_score >= 0.20:  # 20-25% range
            return SeverityBucket.CRITICAL
        elif risk_score >= 0.15:  # 15-20% range
            return SeverityBucket.HIGH
        elif risk_score >= 0.08:  # 8-15% range
            return SeverityBucket.MODERATE
        else:  # <8%
            return SeverityBucket.LOW
    
    def _generate_recommendation(self, severity: SeverityBucket, stressor_analysis: StressorAnalysis) -> str:
        """Generate enhanced recommendations based on specific stressors"""
        base_recommendations = {
            SeverityBucket.SEVERE: "IMMEDIATE: Battery failure imminent - Replace within 3-7 days",
            SeverityBucket.CRITICAL: "URGENT: High failure probability - Test and likely replace within 14 days",
            SeverityBucket.HIGH: "PRIORITY: Schedule comprehensive battery test within 30 days",
            SeverityBucket.MODERATE: "MONITOR: Include in next maintenance visit",
            SeverityBucket.LOW: "ROUTINE: Standard maintenance schedule"
        }
        
        base_action = base_recommendations[severity]
        
        # Add stressor-specific guidance
        if "temp_extreme_hot" in stressor_analysis.active_stressors:
            base_action += " - Recommend cooling system check"
        
        if "maintenance_deferred" in stressor_analysis.active_stressors:
            base_action += " - Address overdue maintenance items"
        
        if "high_mileage_annual" in stressor_analysis.active_stressors:
            base_action += " - Consider upgraded battery for high-mileage usage"
        
        if "multi_driver_usage" in stressor_analysis.active_stressors:
            base_action += " - Educate drivers on battery-friendly practices"
        
        return base_action
    
    def _estimate_revenue_opportunity(self, severity: SeverityBucket, cohort: CohortDefinition) -> Decimal:
        """Enhanced revenue estimation with cohort-specific factors"""
        base_revenue = {
            SeverityBucket.SEVERE: Decimal("1400"),
            SeverityBucket.CRITICAL: Decimal("1200"),
            SeverityBucket.HIGH: Decimal("600"),
            SeverityBucket.MODERATE: Decimal("350"),
            SeverityBucket.LOW: Decimal("180")
        }
        
        revenue = base_revenue[severity]
        
        # Cohort-specific multipliers
        if cohort.region.value == "Commercial":
            revenue *= Decimal("1.8")  # Commercial vehicles higher value
        elif "Truck" in cohort.vehicle_class.value:
            revenue *= Decimal("1.4")  # Trucks generally higher revenue
        elif cohort.vehicle_class.value == "Passenger Car":
            revenue *= Decimal("0.9")  # Passenger cars slightly lower
        
        # Model-specific adjustments
        if any(model in ["F-150", "Super Duty"] for model in cohort.models):
            revenue *= Decimal("1.2")  # Premium models
        
        return revenue
    
    def _calculate_confidence(
        self, 
        input_data: VehicleInputData, 
        prior: float, 
        cohort_confidence: float,
        stressor_analysis: StressorAnalysis
    ) -> float:
        """Enhanced confidence calculation incorporating multiple factors"""
        
        # Base confidence from cohort matching
        confidence = cohort_confidence
        
        # Adjust for data quality
        data_quality_score = self._assess_data_quality(input_data)
        confidence *= data_quality_score
        
        # Adjust for number of active stressors (more stressors = higher confidence)
        num_stressors = len(stressor_analysis.active_stressors)
        if num_stressors >= 3:
            confidence *= 1.1  # High confidence with multiple stressors
        elif num_stressors == 0:
            confidence *= 0.8  # Lower confidence with no stressors
        
        # Adjust for extreme prior probabilities
        if prior < 0.02 or prior > 0.30:
            confidence *= 0.9  # Less confident at extremes
        
        # Adjust for likelihood ratio magnitude
        lr_magnitude = stressor_analysis.combined_likelihood_ratio
        if lr_magnitude > 5.0 or lr_magnitude < 0.2:
            confidence *= 0.85  # Very high/low LRs are less reliable
        
        return max(0.3, min(1.0, confidence))
    
    def _assess_data_quality(self, input_data: VehicleInputData) -> float:
        """Assess quality of input data"""
        quality_score = 1.0
        
        # Data freshness
        hours_old = self._calculate_data_freshness(input_data.timestamp)
        if hours_old > 48:
            quality_score *= 0.9
        if hours_old > 168:  # 1 week
            quality_score *= 0.8
        
        # Data completeness
        required_fields = [
            input_data.soc_30day_trend,
            input_data.trip_cycles_weekly,
            input_data.climate_stress_index,
            input_data.maintenance_compliance
        ]
        
        completeness = sum(1 for field in required_fields if field is not None) / len(required_fields)
        quality_score *= completeness
        
        # Data reasonableness checks
        if input_data.soc_30day_trend and abs(input_data.soc_30day_trend) > 0.5:
            quality_score *= 0.9  # Unusually large SOC changes
        
        if input_data.trip_cycles_weekly and input_data.trip_cycles_weekly > 100:
            quality_score *= 0.9  # Unusually high trip frequency
        
        return quality_score
    
    def _extract_academic_sources(self, cohort: CohortDefinition, stressor_analysis: StressorAnalysis) -> List[str]:
        """Extract all academic sources used in calculation"""
        sources = [cohort.prior_source]
        
        for stressor in stressor_analysis.active_stressors:
            if stressor in cohort.likelihood_ratios:
                sources.append(cohort.likelihood_ratios[stressor].source)
        
        return list(set(sources))  # Remove duplicates
    
    def _calculate_data_freshness(self, timestamp: datetime) -> int:
        """Calculate hours since data timestamp"""
        return int((datetime.utcnow() - timestamp).total_seconds() / 3600)
    
    async def get_cohort_summary(self, cohort_id: str) -> Dict:
        """Get summary of cohort for API responses"""
        cohort = await self.cohort_service.get_cohort_by_id(cohort_id)
        
        if not cohort:
            return {}
        
        return {
            "cohort_id": cohort.cohort_id,
            "description": f"{cohort.vehicle_class.value} in {cohort.region.value}",
            "models_covered": cohort.models,
            "years_covered": cohort.years_supported,
            "base_failure_rate": cohort.prior,
            "academic_source": cohort.prior_source,
            "num_stressor_types": len(cohort.likelihood_ratios),
            "last_updated": cohort.last_updated.isoformat()
        }
    
    async def explain_calculation(self, vin: str, trace: BayesianCalculationTrace) -> Dict:
        """Provide detailed explanation of calculation for transparency"""
        return {
            "vin": vin,
            "calculation_method": trace.calculation_method,
            "step_by_step": {
                "1_cohort_assignment": {
                    "cohort_id": trace.cohort_id,
                    "academic_source": trace.prior_source
                },
                "2_prior_probability": {
                    "value": trace.prior_probability,
                    "interpretation": f"{trace.prior_probability:.1%} base failure rate from academic study"
                },
                "3_stressor_analysis": {
                    "active_stressors": trace.active_stressors,
                    "likelihood_ratios": trace.likelihood_ratios,
                    "combined_lr": trace.combined_likelihood_ratio
                },
                "4_bayesian_update": {
                    "prior_odds": trace.prior_probability / (1 - trace.prior_probability),
                    "posterior_odds": (trace.prior_probability / (1 - trace.prior_probability)) * trace.combined_likelihood_ratio,
                    "posterior_probability": trace.posterior_probability
                },
                "5_final_result": {
                    "risk_score": trace.posterior_probability,
                    "interpretation": f"{trace.posterior_probability:.1%} probability of battery failure"
                }
            },
            "academic_validation": True,
            "timestamp": trace.timestamp.isoformat()
        }


class BatchBayesianProcessorV2:
    """
    Enhanced batch processor with cohort-aware processing
    """
    
    def __init__(self, engine: BayesianRiskEngineV2, batch_size: int = 1000):
        self.engine = engine
        self.batch_size = batch_size
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def process_batch(self, vehicles: List[VehicleInputData]) -> List[RiskScoreOutput]:
        """Process batch with cohort-aware optimization"""
        start_time = datetime.utcnow()
        
        # Group vehicles by likely cohort for optimization
        cohort_groups = await self._group_by_cohort(vehicles)
        
        results = []
        for cohort_id, vehicle_group in cohort_groups.items():
            self.logger.info(f"Processing {len(vehicle_group)} vehicles for cohort {cohort_id}")
            
            # Process cohort group
            tasks = [self.engine.calculate_risk_score(vehicle) for vehicle in vehicle_group]
            group_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            for i, result in enumerate(group_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to process VIN {vehicle_group[i].vin}: {str(result)}")
                else:
                    results.append(result)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        rate = len(results) / processing_time if processing_time > 0 else 0
        
        self.logger.info(f"Processed {len(results)} vehicles in {processing_time:.2f}s "
                        f"({rate:.0f} vehicles/second) across {len(cohort_groups)} cohorts")
        
        return results
    
    async def _group_by_cohort(self, vehicles: List[VehicleInputData]) -> Dict[str, List[VehicleInputData]]:
        """Group vehicles by likely cohort for batch optimization"""
        cohort_groups = {}
        
        for vehicle in vehicles:
            # Quick cohort prediction (simplified)
            likely_cohort = await self._predict_cohort(vehicle)
            
            if likely_cohort not in cohort_groups:
                cohort_groups[likely_cohort] = []
            
            cohort_groups[likely_cohort].append(vehicle)
        
        return cohort_groups
    
    async def _predict_cohort(self, vehicle: VehicleInputData) -> str:
        """Quickly predict likely cohort without full analysis"""
        # This could be optimized with ML models in production
        cohort_match = await self.engine.cohort_service.match_cohort(vehicle.vin)
        return cohort_match.matched_cohort_id 