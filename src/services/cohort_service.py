"""
Ford Bayesian Risk Score Engine - Cohort Service

Production-ready cohort management service that:
- Loads cohorts.json with validation
- Matches vehicles to appropriate cohorts
- Analyzes vehicle stressors using cohort-specific likelihood ratios
- Provides caching and performance optimization
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import re
from dataclasses import dataclass
import redis.asyncio as redis

from ..models.cohort_schemas import (
    CohortDatabase, CohortDefinition, CohortMatchResult, 
    StressorAnalysis, RegionType, VehicleClass, PowertrainType
)
from ..models.schemas import VehicleInputData


logger = logging.getLogger(__name__)


@dataclass
class VehicleProfile:
    """Extracted vehicle profile for cohort matching"""
    make: str
    model: str
    year: int
    vin: str
    region: Optional[str] = None
    estimated_class: Optional[str] = None
    powertrain: str = "Gas"  # Default assumption


class CohortService:
    """
    Production cohort management service with academic-sourced data
    """
    
    def __init__(self, cohorts_file: str = "data/cohorts.json", redis_client: Optional[redis.Redis] = None):
        self.cohorts_file = Path(cohorts_file)
        self.redis_client = redis_client
        self.cohort_database: Optional[CohortDatabase] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Region mapping for ZIP codes (simplified - could be expanded)
        self.zip_to_region = {
            # Midwest
            range(46000, 49999): "Midwest",  # Indiana, Illinois, Michigan, Ohio
            range(50000, 56999): "Midwest",  # Iowa, Minnesota, Wisconsin
            range(60000, 67999): "Midwest",  # Illinois, Missouri, Kansas
            
            # Southwest  
            range(85000, 86999): "Southwest",  # Arizona
            range(87000, 88999): "Southwest",  # New Mexico
            range(75000, 79999): "Southwest",  # Texas
            range(80000, 81999): "Southwest",  # Colorado
            
            # Northeast
            range(10000, 14999): "Northeast",  # New York
            range(20000, 26999): "Northeast",  # DC, Maryland, Virginia
            range(1000, 5999): "Northeast",    # Massachusetts, Connecticut, etc.
            
            # Default fallback
            "default": "Midwest"
        }
        
        # Vehicle class inference patterns
        self.class_patterns = {
            "Light Truck": ["F-150", "Ranger", "Silverado", "Canyon"],
            "Midweight Truck": ["Transit", "Super Duty", "F-250", "F-350"],
            "Heavy Truck": ["F-450", "F-550", "F-650"],
            "Passenger Car": ["Fusion", "Focus", "Fiesta", "Malibu", "Cruze"],
            "SUV": ["Explorer", "Expedition", "Escape", "Tahoe", "Suburban"],
            "Hybrid": ["Prius", "Fusion Hybrid", "Escape Hybrid"]
        }
    
    async def initialize(self) -> None:
        """Initialize the cohort service by loading and validating data"""
        try:
            await self._load_cohorts()
            self.logger.info(f"Cohort service initialized with {len(self.cohort_database.cohorts)} cohorts")
        except Exception as e:
            self.logger.error(f"Failed to initialize cohort service: {str(e)}")
            raise
    
    async def _load_cohorts(self) -> None:
        """Load and validate cohorts from JSON file"""
        if not self.cohorts_file.exists():
            raise FileNotFoundError(f"Cohorts file not found: {self.cohorts_file}")
        
        try:
            with open(self.cohorts_file, 'r') as f:
                data = json.load(f)
            
            # Validate and create cohort database
            self.cohort_database = CohortDatabase(**data)
            
            # Cache in Redis if available
            if self.redis_client:
                await self.redis_client.set(
                    "cohort_database", 
                    self.cohort_database.json(),
                    ex=86400  # 24 hours
                )
            
            self.logger.info(f"Loaded {len(self.cohort_database.cohorts)} cohorts successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading cohorts: {str(e)}")
            raise
    
    def _extract_vehicle_profile(self, vin: str, input_data: Optional[VehicleInputData] = None) -> VehicleProfile:
        """Extract vehicle profile from VIN and input data"""
        # VIN decoding (simplified - production would use full VIN decoder)
        year = self._decode_year_from_vin(vin)
        make = "Ford"  # Assuming Ford for this implementation
        
        # Model inference from VIN position 4-8 (simplified)
        model_code = vin[3:8] if len(vin) >= 8 else ""
        model = self._infer_model_from_code(model_code)
        
        # Region inference from additional data
        region = None
        if input_data and hasattr(input_data, 'zip_code'):
            region = self._infer_region_from_zip(input_data.zip_code)
        
        # Vehicle class inference
        estimated_class = self._infer_vehicle_class(model)
        
        return VehicleProfile(
            make=make,
            model=model,
            year=year,
            vin=vin,
            region=region,
            estimated_class=estimated_class
        )
    
    def _decode_year_from_vin(self, vin: str) -> int:
        """Decode model year from VIN (position 10)"""
        if len(vin) < 10:
            return 2020  # Default fallback
        
        year_char = vin[9].upper()
        
        # VIN year mapping (simplified)
        year_mapping = {
            'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013, 'E': 2014,
            'F': 2015, 'G': 2016, 'H': 2017, 'J': 2018, 'K': 2019,
            'L': 2020, 'M': 2021, 'N': 2022, 'P': 2023, 'R': 2024
        }
        
        return year_mapping.get(year_char, 2020)
    
    def _infer_model_from_code(self, model_code: str) -> str:
        """Infer model from VIN model code (simplified)"""
        # This would be much more sophisticated in production
        code_mapping = {
            "1FTFW": "F-150",
            "1FTRE": "Ranger", 
            "1FTBF": "Super Duty",
            "1FMSK": "Escape",
            "1FMHK": "Explorer",
            "1FMJK": "Expedition",
            "3FA6P": "Fusion",
            "1FADP": "Focus"
        }
        
        # Try partial matches
        for code, model in code_mapping.items():
            if model_code.startswith(code[:4]):
                return model
        
        return "F-150"  # Default fallback
    
    def _infer_region_from_zip(self, zip_code: str) -> Optional[str]:
        """Infer region from ZIP code"""
        try:
            zip_num = int(zip_code[:5])
            
            for zip_range, region in self.zip_to_region.items():
                if isinstance(zip_range, range) and zip_num in zip_range:
                    return region
            
            return self.zip_to_region["default"]
        except (ValueError, TypeError):
            return None
    
    def _infer_vehicle_class(self, model: str) -> Optional[str]:
        """Infer vehicle class from model name"""
        for vehicle_class, models in self.class_patterns.items():
            if any(pattern in model for pattern in models):
                return vehicle_class
        return None
    
    async def match_cohort(self, vin: str, input_data: Optional[VehicleInputData] = None) -> CohortMatchResult:
        """Match a vehicle to the most appropriate cohort"""
        if not self.cohort_database:
            await self.initialize()
        
        # Extract vehicle profile
        profile = self._extract_vehicle_profile(vin, input_data)
        
        # Find matching cohorts
        candidates = self.cohort_database.find_cohorts_by_criteria(
            make=profile.make,
            model=profile.model,
            year=profile.year,
            region=RegionType(profile.region) if profile.region else None
        )
        
        # If no exact matches, try broader criteria
        if not candidates:
            candidates = self.cohort_database.find_cohorts_by_criteria(
                make=profile.make,
                year=profile.year
            )
        
        # If still no matches, use fallback
        if not candidates:
            candidates = [self.cohort_database.cohorts[0]]  # First cohort as fallback
            fallback_used = True
        else:
            fallback_used = False
        
        # Score candidates and pick best match
        best_match = self._score_cohort_matches(profile, candidates)
        confidence = self._calculate_match_confidence(profile, best_match, len(candidates))
        
        return CohortMatchResult(
            vin=vin,
            matched_cohort_id=best_match.cohort_id,
            confidence=confidence,
            fallback_used=fallback_used,
            match_criteria={
                "make": profile.make,
                "model": profile.model,
                "year": str(profile.year),
                "region": profile.region or "unknown",
                "vehicle_class": profile.estimated_class or "unknown"
            }
        )
    
    def _score_cohort_matches(self, profile: VehicleProfile, candidates: List[CohortDefinition]) -> CohortDefinition:
        """Score cohort candidates and return best match"""
        best_score = -1
        best_match = candidates[0]
        
        for cohort in candidates:
            score = 0
            
            # Model match (highest weight)
            if profile.model in cohort.models:
                score += 10
            
            # Year match
            if profile.year in cohort.years_supported:
                score += 5
            
            # Region match
            if profile.region and profile.region == cohort.region.value:
                score += 3
            
            # Vehicle class match
            if profile.estimated_class and profile.estimated_class == cohort.vehicle_class.value:
                score += 2
            
            if score > best_score:
                best_score = score
                best_match = cohort
        
        return best_match
    
    def _calculate_match_confidence(self, profile: VehicleProfile, cohort: CohortDefinition, num_candidates: int) -> float:
        """Calculate confidence in the cohort match"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for exact matches
        if profile.model in cohort.models:
            confidence += 0.3
        if profile.year in cohort.years_supported:
            confidence += 0.2
        if profile.region and profile.region == cohort.region.value:
            confidence += 0.1
        
        # Reduce confidence if many candidates (ambiguous match)
        if num_candidates > 3:
            confidence *= 0.8
        
        return min(1.0, confidence)
    
    async def analyze_vehicle_stressors(self, vin: str, input_data: VehicleInputData) -> StressorAnalysis:
        """Analyze vehicle stressors using cohort-specific likelihood ratios"""
        # Get cohort match
        cohort_match = await self.match_cohort(vin, input_data)
        cohort = self.cohort_database.get_cohort_by_id(cohort_match.matched_cohort_id)
        
        if not cohort:
            raise ValueError(f"Cohort not found: {cohort_match.matched_cohort_id}")
        
        # Analyze each stressor
        active_stressors = []
        stressor_contributions = {}
        
        for stressor_name, lr_def in cohort.likelihood_ratios.items():
            is_active, contribution = self._evaluate_stressor(stressor_name, lr_def, input_data)
            
            stressor_contributions[stressor_name] = contribution
            
            if is_active:
                active_stressors.append(stressor_name)
        
        # Calculate combined likelihood ratio
        combined_lr = 1.0
        for stressor in active_stressors:
            combined_lr *= cohort.likelihood_ratios[stressor].value
        
        # Generate human-readable risk factors
        risk_factors = self._generate_risk_factors(active_stressors, cohort)
        
        return StressorAnalysis(
            vin=vin,
            cohort_id=cohort.cohort_id,
            active_stressors=active_stressors,
            stressor_contributions=stressor_contributions,
            combined_likelihood_ratio=combined_lr,
            risk_factors=risk_factors
        )
    
    def _evaluate_stressor(self, stressor_name: str, lr_def, input_data: VehicleInputData) -> Tuple[bool, float]:
        """Evaluate if a specific stressor is active for this vehicle"""
        # Temperature-related stressors
        if "temp_delta_high" in stressor_name:
            # Would need temperature data - using climate_stress_index as proxy
            is_active = input_data.climate_stress_index > 0.6
            contribution = lr_def.value if is_active else 1.0
            return is_active, contribution
        
        elif "temp_extreme_hot" in stressor_name:
            is_active = input_data.climate_stress_index > 0.8
            contribution = lr_def.value if is_active else 1.0
            return is_active, contribution
        
        elif "cold_extreme" in stressor_name:
            is_active = input_data.climate_stress_index > 0.7  # Cold stress proxy
            contribution = lr_def.value if is_active else 1.0
            return is_active, contribution
        
        # Trip-related stressors
        elif "short_trip" in stressor_name or "trip_duration_low" in stressor_name:
            is_active = input_data.trip_cycles_weekly > 45  # High frequency = short trips
            contribution = lr_def.value if is_active else 1.0
            return is_active, contribution
        
        elif "ignition_cycles_high" in stressor_name:
            is_active = input_data.trip_cycles_weekly > 40
            contribution = lr_def.value if is_active else 1.0
            return is_active, contribution
        
        # Usage pattern stressors
        elif "ign_off_to_on_under_1hr" in stressor_name:
            # Use SOC trend as proxy for insufficient recharge time
            is_active = input_data.soc_30day_trend < -0.1
            contribution = lr_def.value if is_active else 1.0
            return is_active, contribution
        
        elif "maintenance_deferred" in stressor_name:
            is_active = input_data.maintenance_compliance < 0.7
            contribution = lr_def.value if is_active else 1.0
            return is_active, contribution
        
        # Default case
        else:
            is_active = False
            contribution = 1.0
            return is_active, contribution
    
    def _generate_risk_factors(self, active_stressors: List[str], cohort: CohortDefinition) -> List[str]:
        """Generate human-readable risk factor descriptions"""
        risk_factors = []
        
        for stressor in active_stressors:
            if stressor in cohort.likelihood_ratios:
                definition = cohort.likelihood_ratios[stressor].definition
                risk_factors.append(definition)
        
        return risk_factors
    
    async def get_cohort_by_id(self, cohort_id: str) -> Optional[CohortDefinition]:
        """Get cohort definition by ID"""
        if not self.cohort_database:
            await self.initialize()
        
        return self.cohort_database.get_cohort_by_id(cohort_id)
    
    async def get_all_cohorts(self) -> List[CohortDefinition]:
        """Get all available cohorts"""
        if not self.cohort_database:
            await self.initialize()
        
        return self.cohort_database.cohorts
    
    async def refresh_cohorts(self) -> None:
        """Reload cohorts from file (useful for hot-swapping)"""
        await self._load_cohorts()
        self.logger.info("Cohorts refreshed successfully") 