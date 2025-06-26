"""
Ford Bayesian Risk Score Engine - Core Bayesian Calculation Engine

This engine implements the Bayesian risk scoring using:
- Academic-validated priors from Argonne ANL-115925.pdf and cohorts.json
- Cohort-aware likelihood ratios with academic backing
- Dynamic cohort-based calculations
"""

import numpy as np
import logging
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
from dataclasses import dataclass

from ..models.schemas import (
    VehicleInputData, RiskScoreOutput, RiskScoreMetadata,
    BayesianPriors, LikelihoodRatios, SeverityBucket, CohortAssignment
)
from ..services.cohort_service import CohortService


logger = logging.getLogger(__name__)


class BayesianRiskEngine:
    """
    Core Bayesian risk calculation engine using academic cohort system
    """
    
    def __init__(self, cohorts_file: str = "data/cohorts.json"):
        self.cohort_service = CohortService(cohorts_file)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.model_version = "1.1"  # Updated for cohort integration
        
    async def calculate_risk_score(self, input_data: VehicleInputData) -> RiskScoreOutput:
        """
        Calculate Bayesian risk score using academic cohort system
        
        Uses the formula: P(Failure|Evidence) = P(Evidence|Failure) * P(Failure) / P(Evidence)
        Where Evidence comes from cohort-specific stressor analysis
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Decode VIN and match to cohort
            vehicle_info = self._decode_vin(input_data.vin)
            cohort = self.cohort_service.match_vehicle_to_cohort(vehicle_info)
            
            if not cohort:
                raise ValueError(f"No cohort found for VIN {input_data.vin}")
            
            # Step 2: Get academic prior probability
            prior_prob = cohort['prior']
            
            # Step 3: Analyze stressors and calculate likelihood ratios
            active_stressors = self._analyze_stressors(input_data, cohort)
            likelihood_ratio = self._calculate_cohort_likelihood_ratio(active_stressors)
            
            # Step 4: Apply Bayesian update with cohort-specific calculations
            posterior_prob = self._bayesian_update(prior_prob, likelihood_ratio)
            
            # Step 5: Determine severity and generate recommendations
            severity_bucket = self._classify_severity(posterior_prob)
            stressor_names = [s['name'] for s in active_stressors]
            recommended_action = self._generate_recommendation(severity_bucket, stressor_names)
            revenue_opportunity = self._estimate_revenue_opportunity(
                severity_bucket, cohort['cohort_id'], posterior_prob
            )
            
            # Step 6: Calculate confidence with academic backing
            confidence = self._calculate_confidence(cohort, len(active_stressors))
            
            # Step 7: Build metadata with academic sources
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
                cohort=f"{cohort['cohort_id']} ({cohort['region']} {cohort['vehicle_class']})",
                dominant_stressors=stressor_names,
                recommended_action=recommended_action,
                revenue_opportunity=revenue_opportunity,
                confidence=confidence,
                metadata=metadata,
                academic_sources=cohort.get('prior_source', 'Academic validation'),
                cohort_comparison=f"{posterior_prob/prior_prob:.1f}x above cohort average"
            )
            
        except Exception as e:
            self.logger.error(f"Risk calculation failed for VIN {input_data.vin}: {str(e)}")
            raise
    
    def _decode_vin(self, vin: str) -> Dict[str, str]:
        """Decode VIN to vehicle information for cohort matching"""
        vin_patterns = {
            '1FTFW1ET': {'make': 'Ford', 'model': 'F-150', 'class': 'Light Truck'},
            '1FMHK8D8': {'make': 'Ford', 'model': 'Explorer', 'class': 'SUV'}, 
            '1FTBF2A6': {'make': 'Ford', 'model': 'Super Duty', 'class': 'Midweight Truck'},
            '3FA6P0HR': {'make': 'Ford', 'model': 'Fusion', 'class': 'Passenger Car'},
            '1NM0ES7E': {'make': 'Ford', 'model': 'Transit', 'class': 'Midweight Truck'},
        }
        
        for pattern, info in vin_patterns.items():
            if vin.startswith(pattern):
                return info
        
        # Default fallback
        return {'make': 'Ford', 'model': 'F-150', 'class': 'Light Truck'}
    
    def _analyze_stressors(self, input_data: VehicleInputData, cohort: Dict) -> List[Dict]:
        """Analyze input data against cohort-specific stressors"""
        active_stressors = []
        
        for stressor_key, stressor_data in cohort['likelihood_ratios'].items():
            is_active = self._is_stressor_active(stressor_key, input_data)
            
            if is_active:
                active_stressors.append({
                    'name': stressor_key,
                    'lr_value': stressor_data['value'],
                    'definition': stressor_data['definition'],
                    'source': stressor_data['source']
                })
        
        return active_stressors
    
    def _is_stressor_active(self, stressor_key: str, input_data: VehicleInputData) -> bool:
        """Determine if a specific stressor is active based on academic thresholds"""
        
        # Temperature-related stressors
        if 'temp' in stressor_key.lower():
            return input_data.climate_stress_index >= 0.7
        
        # Trip/cycling related stressors (Argonne 6-mile rule)
        if 'trip' in stressor_key.lower() or 'short' in stressor_key.lower():
            return input_data.trip_cycles_weekly >= 40  # Frequent short trips
        
        # Ignition cycle stressors (Argonne ANL-115925.pdf validation)
        if 'ignition' in stressor_key.lower():
            return input_data.trip_cycles_weekly >= 50  # High ignition cycles
        
        # SOC/battery health stressors
        if 'soc' in stressor_key.lower():
            return input_data.soc_30day_trend <= -0.15  # 15% SOC decline
        
        # Maintenance-related stressors
        if 'maintenance' in stressor_key.lower():
            return input_data.maintenance_compliance < 0.6  # Poor maintenance
        
        # Mileage/usage stressors
        if 'mileage' in stressor_key.lower() or 'usage' in stressor_key.lower():
            return input_data.odometer_variance >= 0.8  # High usage variability
        
        # Salt/corrosion stressors
        if 'salt' in stressor_key.lower() or 'corrosion' in stressor_key.lower():
            return input_data.climate_stress_index >= 0.5  # Moderate climate stress
        
        # Default: moderate threshold
        return input_data.climate_stress_index >= 0.6
    
    def _calculate_cohort_likelihood_ratio(self, active_stressors: List[Dict]) -> float:
        """Calculate combined likelihood ratio from active stressors"""
        combined_lr = 1.0
        
        for stressor in active_stressors:
            combined_lr *= stressor['lr_value']
        
        self.logger.debug(f"Active stressors: {len(active_stressors)}, Combined LR: {combined_lr:.3f}")
        return combined_lr
    
    def _bayesian_update(self, prior: float, likelihood_ratio: float) -> float:
        """
        Apply Bayesian update using academic formula:
        P(Failure|Evidence) = (Prior * LR) / ((Prior * LR) + (1 - Prior))
        """
        numerator = prior * likelihood_ratio
        denominator = numerator + (1 - prior)
        posterior = numerator / denominator
        
        # Ensure bounds [0, 1]
        return max(0.0, min(1.0, posterior))
    
    def _classify_severity(self, risk_score: float) -> SeverityBucket:
        """Classify risk score into severity buckets"""
        if risk_score >= 0.50:
            return SeverityBucket.SEVERE
        elif risk_score >= 0.30:
            return SeverityBucket.CRITICAL
        elif risk_score >= 0.20:
            return SeverityBucket.HIGH
        elif risk_score >= 0.10:
            return SeverityBucket.MODERATE
        else:
            return SeverityBucket.LOW
    
    def _generate_recommendation(self, severity: SeverityBucket, stressors: List[str]) -> str:
        """Generate dealer workflow recommendation based on academic risk assessment"""
        if severity == SeverityBucket.SEVERE:
            return "CRITICAL: Contact customer immediately - battery replacement recommended within 48 hours"
        elif severity == SeverityBucket.CRITICAL:
            return "URGENT: Schedule battery diagnostic within 7 days - high failure probability"
        elif severity == SeverityBucket.HIGH:
            return "PRIORITY: Battery health check recommended within 2 weeks"
        elif severity == SeverityBucket.MODERATE:
            if any('maintenance' in s for s in stressors):
                return "MAINTENANCE: Schedule overdue service to address risk factors"
            else:
                return "MONITOR: Include battery check in next scheduled service"
        else:
            return "ROUTINE: Standard maintenance schedule sufficient"
    
    def _estimate_revenue_opportunity(self, severity: SeverityBucket, cohort_id: str, risk_score: float) -> Decimal:
        """Estimate revenue opportunity with cohort-specific multipliers"""
        base_revenue = {
            SeverityBucket.SEVERE: Decimal("1200"),
            SeverityBucket.CRITICAL: Decimal("800"),
            SeverityBucket.HIGH: Decimal("450"),
            SeverityBucket.MODERATE: Decimal("250"),
            SeverityBucket.LOW: Decimal("120")
        }
        
        revenue = base_revenue[severity]
        
        # Apply cohort-specific multipliers
        if 'commercial' in cohort_id:
            revenue *= Decimal("1.8")  # Commercial fleet premium
        elif 'truck' in cohort_id:
            revenue *= Decimal("1.4")  # Truck service premium
        
        # Risk-based multiplier
        risk_multiplier = Decimal(str(max(1.0, risk_score / 0.15)))  # Scale from 15% baseline
        revenue *= risk_multiplier
        
        return revenue
    
    def _calculate_confidence(self, cohort: Dict, active_stressor_count: int) -> float:
        """Calculate prediction confidence based on academic backing"""
        base_confidence = 0.85  # High base confidence due to academic sources
        
        # Boost confidence for well-researched cohorts
        if 'Argonne' in cohort.get('prior_source', ''):
            base_confidence *= 1.1
        
        # Boost confidence with more active stressors (more evidence)
        if active_stressor_count >= 3:
            base_confidence *= 1.05
        elif active_stressor_count >= 2:
            base_confidence *= 1.02
        
        return max(0.6, min(1.0, base_confidence))
    
    def _calculate_data_freshness(self, timestamp: datetime) -> int:
        """Calculate hours since data timestamp"""
        return int((datetime.utcnow() - timestamp).total_seconds() / 3600)


class BatchBayesianProcessor:
    """
    Batch processor for high-throughput risk scoring with cohort optimization
    """
    
    def __init__(self, engine: BayesianRiskEngine, batch_size: int = 1000):
        self.engine = engine
        self.batch_size = batch_size
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def process_batch(self, vehicles: List[VehicleInputData]) -> List[RiskScoreOutput]:
        """Process a batch of vehicles with cohort grouping optimization"""
        start_time = datetime.utcnow()
        
        # Group vehicles by cohort for optimized processing
        cohort_groups = {}
        for vehicle in vehicles:
            vehicle_info = self.engine._decode_vin(vehicle.vin)
            cohort = self.engine.cohort_service.match_vehicle_to_cohort(vehicle_info)
            cohort_id = cohort['cohort_id'] if cohort else 'default'
            
            if cohort_id not in cohort_groups:
                cohort_groups[cohort_id] = []
            cohort_groups[cohort_id].append(vehicle)
        
        # Process each cohort group
        results = []
        for cohort_id, cohort_vehicles in cohort_groups.items():
            self.logger.info(f"Processing {len(cohort_vehicles)} vehicles in cohort {cohort_id}")
            
            # Process cohort concurrently
            tasks = [self.engine.calculate_risk_score(vehicle) for vehicle in cohort_vehicles]
            cohort_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            for j, result in enumerate(cohort_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to process VIN {cohort_vehicles[j].vin}: {str(result)}")
                else:
                    results.append(result)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        rate = len(results) / processing_time if processing_time > 0 else 0
        
        self.logger.info(f"Processed {len(results)} vehicles in {processing_time:.2f}s "
                        f"({rate:.0f} vehicles/second) across {len(cohort_groups)} cohorts")
        
        return results 