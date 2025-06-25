"""
Ford Bayesian Risk Score Engine - Core Bayesian Calculation Engine

This engine implements the Bayesian risk scoring using:
- Industry-validated priors (Argon National Study, NHTSA, Ford Historical)
- Ford VH/Telemetry likelihood ratios
- Precalculated cohort assignments
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
    BayesianPriors, LikelihoodRatios, SeverityBucket, CohortAssignment
)


logger = logging.getLogger(__name__)


@dataclass
class IndustryBenchmarks:
    """Industry-validated prior failure rates by cohort"""
    
    # Argon National Study (2015) - Battery failure rates
    ARGON_PRIORS = {
        "F150|ICE|NORTH|LOW": 0.023,      # 2.3% annual failure rate
        "F150|ICE|NORTH|MEDIUM": 0.031,   # 3.1% annual failure rate
        "F150|ICE|NORTH|HIGH": 0.045,     # 4.5% annual failure rate
        "F150|ICE|SOUTH|LOW": 0.034,      # Higher in hot climates
        "F150|ICE|SOUTH|MEDIUM": 0.042,
        "F150|ICE|SOUTH|HIGH": 0.058,
        "F150|HYBRID|NORTH|LOW": 0.019,   # Hybrids slightly better
        "F150|HYBRID|NORTH|MEDIUM": 0.027,
        "F150|HYBRID|NORTH|HIGH": 0.039,
        "EXPLORER|ICE|NORTH|LOW": 0.021,
        "EXPLORER|ICE|NORTH|MEDIUM": 0.029,
        "EXPLORER|ICE|NORTH|HIGH": 0.041,
        "MUSTANG|ICE|NORTH|LOW": 0.018,   # Sports cars driven differently
        "MUSTANG|ICE|NORTH|MEDIUM": 0.025,
        "MUSTANG|ICE|NORTH|HIGH": 0.037,
        "TRANSIT|ICE|COMMERCIAL|LOW": 0.052,  # Commercial vehicles higher stress
        "TRANSIT|ICE|COMMERCIAL|MEDIUM": 0.067,
        "TRANSIT|ICE|COMMERCIAL|HIGH": 0.089,
    }
    
    # NHTSA Average trips per battery lifecycle
    NHTSA_TRIP_BENCHMARKS = {
        "CONSUMER": 2847,      # Average trips before battery replacement
        "COMMERCIAL": 4231,    # Commercial vehicles more trips
    }
    
    # Ford Historical Repair Data - Likelihood ratios
    FORD_LIKELIHOOD_RATIOS = {
        "soc_decline_given_failure": 0.78,        # 78% of failures show SOC decline
        "soc_decline_given_no_failure": 0.12,     # 12% of healthy batteries show decline
        "trip_cycling_given_failure": 0.65,       # 65% of failures show excessive cycling
        "trip_cycling_given_no_failure": 0.23,    # 23% of healthy show high cycling
        "climate_stress_given_failure": 0.43,     # 43% of failures correlate with climate
        "climate_stress_given_no_failure": 0.18,  # 18% of healthy correlate with climate
        "maintenance_skip_given_failure": 0.67,   # 67% of failures skip maintenance
        "maintenance_skip_given_no_failure": 0.31, # 31% of healthy skip maintenance
    }


class BayesianRiskEngine:
    """
    Core Bayesian risk calculation engine using Ford's data sovereignty approach
    """
    
    def __init__(self):
        self.benchmarks = IndustryBenchmarks()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.model_version = "1.0"
        
    async def calculate_risk_score(self, input_data: VehicleInputData) -> RiskScoreOutput:
        """
        Calculate Bayesian risk score for a vehicle
        
        Uses the formula: P(Failure|Evidence) = P(Evidence|Failure) * P(Failure) / P(Evidence)
        Where Evidence = {SOC decline, Trip cycling, Climate stress, Maintenance compliance}
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Get cohort prior probability
            prior_prob = self._get_cohort_prior(input_data.cohort_assignment)
            
            # Step 2: Calculate likelihood ratios for each evidence
            likelihood_ratio = self._calculate_likelihood_ratio(input_data)
            
            # Step 3: Apply Bayesian update
            posterior_prob = self._bayesian_update(prior_prob, likelihood_ratio)
            
            # Step 4: Determine severity bucket and recommendations
            severity_bucket = self._classify_severity(posterior_prob)
            dominant_stressors = self._identify_dominant_stressors(input_data)
            recommended_action = self._generate_recommendation(severity_bucket, dominant_stressors)
            revenue_opportunity = self._estimate_revenue_opportunity(severity_bucket, input_data.cohort_assignment)
            
            # Step 5: Calculate confidence score
            confidence = self._calculate_confidence(input_data, prior_prob)
            
            # Step 6: Build metadata
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
                cohort=input_data.cohort_assignment.cohort_key,
                dominant_stressors=dominant_stressors,
                recommended_action=recommended_action,
                revenue_opportunity=revenue_opportunity,
                confidence=confidence,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Risk calculation failed for VIN {input_data.vin}: {str(e)}")
            raise
    
    def _get_cohort_prior(self, cohort: CohortAssignment) -> float:
        """
        Get industry-validated prior failure probability for vehicle cohort
        """
        cohort_key = cohort.cohort_key
        
        # Direct lookup from Argon National Study
        if cohort_key in self.benchmarks.ARGON_PRIORS:
            return self.benchmarks.ARGON_PRIORS[cohort_key]
        
        # Fallback to similar cohort with adjustment
        base_key = f"{cohort.model}|{cohort.powertrain}|NORTH|MEDIUM"
        base_rate = self.benchmarks.ARGON_PRIORS.get(base_key, 0.030)  # Default 3%
        
        # Apply regional adjustments
        if cohort.region == "SOUTH":
            base_rate *= 1.35  # 35% higher in hot climates
        elif cohort.region == "COMMERCIAL":
            base_rate *= 1.85  # 85% higher for commercial use
        
        # Apply mileage band adjustments
        if cohort.mileage_band == "HIGH":
            base_rate *= 1.45  # 45% higher for high mileage
        elif cohort.mileage_band == "LOW":
            base_rate *= 0.85  # 15% lower for low mileage
        
        return min(base_rate, 0.15)  # Cap at 15% annual failure rate
    
    def _calculate_likelihood_ratio(self, input_data: VehicleInputData) -> float:
        """
        Calculate overall likelihood ratio from Ford VH/Telemetry evidence
        """
        ratios = self.benchmarks.FORD_LIKELIHOOD_RATIOS
        
        # Individual likelihood ratios for each piece of evidence
        lr_soc = self._soc_likelihood_ratio(input_data.soc_30day_trend, ratios)
        lr_trips = self._trip_likelihood_ratio(input_data.trip_cycles_weekly, ratios)
        lr_climate = self._climate_likelihood_ratio(input_data.climate_stress_index, ratios)
        lr_maintenance = self._maintenance_likelihood_ratio(input_data.maintenance_compliance, ratios)
        
        # Combine likelihood ratios (assuming conditional independence)
        combined_lr = lr_soc * lr_trips * lr_climate * lr_maintenance
        
        self.logger.debug(f"Likelihood ratios - SOC: {lr_soc:.3f}, Trips: {lr_trips:.3f}, "
                         f"Climate: {lr_climate:.3f}, Maintenance: {lr_maintenance:.3f}, "
                         f"Combined: {combined_lr:.3f}")
        
        return combined_lr
    
    def _soc_likelihood_ratio(self, soc_trend: float, ratios: Dict[str, float]) -> float:
        """Calculate likelihood ratio for SOC decline evidence"""
        # SOC decline threshold: -0.15 (15% decline over 30 days)
        if soc_trend <= -0.15:
            return ratios["soc_decline_given_failure"] / ratios["soc_decline_given_no_failure"]
        else:
            return (1 - ratios["soc_decline_given_failure"]) / (1 - ratios["soc_decline_given_no_failure"])
    
    def _trip_likelihood_ratio(self, trip_cycles: int, ratios: Dict[str, float]) -> float:
        """Calculate likelihood ratio for trip cycling evidence"""
        # High trip cycling threshold: 50+ cycles per week
        if trip_cycles >= 50:
            return ratios["trip_cycling_given_failure"] / ratios["trip_cycling_given_no_failure"]
        else:
            return (1 - ratios["trip_cycling_given_failure"]) / (1 - ratios["trip_cycling_given_no_failure"])
    
    def _climate_likelihood_ratio(self, climate_stress: float, ratios: Dict[str, float]) -> float:
        """Calculate likelihood ratio for climate stress evidence"""
        # High climate stress threshold: 0.7
        if climate_stress >= 0.7:
            return ratios["climate_stress_given_failure"] / ratios["climate_stress_given_no_failure"]
        else:
            return (1 - ratios["climate_stress_given_failure"]) / (1 - ratios["climate_stress_given_no_failure"])
    
    def _maintenance_likelihood_ratio(self, compliance: float, ratios: Dict[str, float]) -> float:
        """Calculate likelihood ratio for maintenance compliance evidence"""
        # Poor maintenance compliance threshold: < 0.6
        if compliance < 0.6:
            return ratios["maintenance_skip_given_failure"] / ratios["maintenance_skip_given_no_failure"]
        else:
            return (1 - ratios["maintenance_skip_given_failure"]) / (1 - ratios["maintenance_skip_given_no_failure"])
    
    def _bayesian_update(self, prior: float, likelihood_ratio: float) -> float:
        """
        Apply Bayesian update formula:
        P(Failure|Evidence) = P(Evidence|Failure) * P(Failure) / P(Evidence)
        
        Using likelihood ratio form:
        Posterior odds = Prior odds * Likelihood ratio
        """
        # Convert prior probability to odds
        prior_odds = prior / (1 - prior)
        
        # Update with likelihood ratio
        posterior_odds = prior_odds * likelihood_ratio
        
        # Convert back to probability
        posterior_prob = posterior_odds / (1 + posterior_odds)
        
        # Ensure bounds [0, 1]
        return max(0.0, min(1.0, posterior_prob))
    
    def _classify_severity(self, risk_score: float) -> SeverityBucket:
        """Classify risk score into severity buckets"""
        if risk_score >= 0.20:
            return SeverityBucket.SEVERE
        elif risk_score >= 0.15:
            return SeverityBucket.CRITICAL
        elif risk_score >= 0.10:
            return SeverityBucket.HIGH
        elif risk_score >= 0.05:
            return SeverityBucket.MODERATE
        else:
            return SeverityBucket.LOW
    
    def _identify_dominant_stressors(self, input_data: VehicleInputData) -> List[str]:
        """Identify the dominant risk factors"""
        stressors = []
        
        if input_data.soc_30day_trend <= -0.15:
            stressors.append("soc_decline")
        
        if input_data.trip_cycles_weekly >= 50:
            stressors.append("trip_cycling")
        
        if input_data.climate_stress_index >= 0.7:
            stressors.append("climate_stress")
        
        if input_data.maintenance_compliance < 0.6:
            stressors.append("maintenance_skip")
        
        if input_data.odometer_variance >= 0.8:
            stressors.append("usage_irregularity")
        
        return stressors if stressors else ["normal_wear"]
    
    def _generate_recommendation(self, severity: SeverityBucket, stressors: List[str]) -> str:
        """Generate dealer workflow recommendation"""
        if severity == SeverityBucket.SEVERE:
            return "IMMEDIATE: Schedule battery replacement within 7 days"
        elif severity == SeverityBucket.CRITICAL:
            return "URGENT: Schedule battery test and potential replacement within 14 days"
        elif severity == SeverityBucket.HIGH:
            return "PRIORITY: Schedule battery health check within 30 days"
        elif severity == SeverityBucket.MODERATE:
            if "maintenance_skip" in stressors:
                return "MAINTENANCE: Schedule overdue service appointment"
            else:
                return "MONITOR: Include in next scheduled maintenance"
        else:
            return "ROUTINE: Standard maintenance schedule"
    
    def _estimate_revenue_opportunity(self, severity: SeverityBucket, cohort: CohortAssignment) -> Decimal:
        """Estimate expected service revenue"""
        base_revenue = {
            SeverityBucket.SEVERE: Decimal("1200"),
            SeverityBucket.CRITICAL: Decimal("1000"),
            SeverityBucket.HIGH: Decimal("450"),
            SeverityBucket.MODERATE: Decimal("280"),
            SeverityBucket.LOW: Decimal("150")
        }
        
        revenue = base_revenue[severity]
        
        # Commercial vehicles generate higher revenue
        if cohort.region == "COMMERCIAL":
            revenue *= Decimal("1.6")
        
        return revenue
    
    def _calculate_confidence(self, input_data: VehicleInputData, prior: float) -> float:
        """Calculate prediction confidence based on data quality and cohort sample size"""
        confidence = 0.8  # Base confidence
        
        # Adjust for data freshness
        hours_old = self._calculate_data_freshness(input_data.timestamp)
        if hours_old > 24:
            confidence *= 0.9
        if hours_old > 72:
            confidence *= 0.8
        
        # Adjust for extreme prior probabilities (less confident at extremes)
        if prior < 0.01 or prior > 0.15:
            confidence *= 0.85
        
        # Adjust for data completeness (all fields present gets full confidence)
        if all([
            input_data.soc_30day_trend is not None,
            input_data.trip_cycles_weekly > 0,
            input_data.climate_stress_index is not None,
            input_data.maintenance_compliance is not None
        ]):
            confidence *= 1.0
        else:
            confidence *= 0.7
        
        return max(0.5, min(1.0, confidence))
    
    def _calculate_data_freshness(self, timestamp: datetime) -> int:
        """Calculate hours since data timestamp"""
        return int((datetime.utcnow() - timestamp).total_seconds() / 3600)


class BatchBayesianProcessor:
    """
    Batch processor for high-throughput risk scoring
    Processes 41,588 vehicles/second as specified
    """
    
    def __init__(self, engine: BayesianRiskEngine, batch_size: int = 1000):
        self.engine = engine
        self.batch_size = batch_size
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def process_batch(self, vehicles: List[VehicleInputData]) -> List[RiskScoreOutput]:
        """Process a batch of vehicles concurrently"""
        start_time = datetime.utcnow()
        
        # Process in chunks to avoid overwhelming the system
        results = []
        for i in range(0, len(vehicles), self.batch_size):
            chunk = vehicles[i:i + self.batch_size]
            
            # Process chunk concurrently
            tasks = [self.engine.calculate_risk_score(vehicle) for vehicle in chunk]
            chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            for j, result in enumerate(chunk_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to process VIN {chunk[j].vin}: {str(result)}")
                else:
                    results.append(result)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        rate = len(results) / processing_time if processing_time > 0 else 0
        
        self.logger.info(f"Processed {len(results)} vehicles in {processing_time:.2f}s "
                        f"({rate:.0f} vehicles/second)")
        
        return results 