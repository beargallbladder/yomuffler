"""
Ford Bayesian Risk Score Engine - Cohort Schema Models

Production-ready schemas for the cohorts.json structure with:
- Academic sourcing validation
- Likelihood ratio definitions
- Regional and vehicle class specificity
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class RegionType(str, Enum):
    """Geographic regions for cohort classification"""
    MIDWEST = "Midwest"
    SOUTHWEST = "Southwest" 
    NORTHEAST = "Northeast"
    SOUTHEAST = "Southeast"
    WEST = "West"
    COMMERCIAL = "Commercial"  # Special region for commercial fleets


class VehicleClass(str, Enum):
    """Vehicle class categories"""
    LIGHT_TRUCK = "Light Truck"
    MIDWEIGHT_TRUCK = "Midweight Truck"
    HEAVY_TRUCK = "Heavy Truck"
    PASSENGER_CAR = "Passenger Car"
    SUV = "SUV"
    HYBRID = "Hybrid"


class PowertrainType(str, Enum):
    """Powertrain categories"""
    GAS = "Gas"
    HYBRID = "Hybrid"
    ELECTRIC = "Electric"
    DIESEL = "Diesel"


class LikelihoodRatio(BaseModel):
    """Individual likelihood ratio with academic justification"""
    value: float = Field(..., ge=0.1, le=10.0, description="Likelihood ratio value")
    definition: str = Field(..., min_length=10, description="Clear operational definition")
    source: str = Field(..., min_length=5, description="Academic or industry source")
    
    @validator('value')
    def validate_lr_bounds(cls, v):
        """Ensure likelihood ratios are within reasonable bounds"""
        if v < 0.1 or v > 10.0:
            raise ValueError("Likelihood ratios should be between 0.1 and 10.0")
        return v


class CohortDefinition(BaseModel):
    """Complete cohort definition with priors and likelihood ratios"""
    cohort_id: str = Field(..., description="Unique cohort identifier")
    region: RegionType = Field(..., description="Geographic region")
    vehicle_class: VehicleClass = Field(..., description="Vehicle classification")
    powertrain: PowertrainType = Field(..., description="Powertrain type")
    years_supported: List[int] = Field(..., min_items=1, description="Model years covered")
    makes: List[str] = Field(..., min_items=1, description="Vehicle makes")
    models: List[str] = Field(..., min_items=1, description="Vehicle models")
    
    # Prior probability with sourcing
    prior: float = Field(..., ge=0.001, le=0.5, description="Base failure probability")
    prior_source: str = Field(..., min_length=10, description="Academic source for prior")
    
    # Likelihood ratios dictionary
    likelihood_ratios: Dict[str, LikelihoodRatio] = Field(
        ..., 
        min_items=1,
        description="Dictionary of likelihood ratios with justification"
    )
    
    # Metadata
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0", description="Cohort definition version")
    
    @validator('years_supported')
    def validate_years(cls, v):
        """Ensure reasonable year ranges"""
        current_year = datetime.now().year
        for year in v:
            if year < 2010 or year > current_year + 2:
                raise ValueError(f"Year {year} outside reasonable range (2010-{current_year+2})")
        return sorted(v)
    
    @validator('prior')
    def validate_prior(cls, v):
        """Ensure prior is reasonable for automotive failure rates"""
        if v < 0.001:  # Less than 0.1% seems too low
            raise ValueError("Prior failure rate seems unrealistically low")
        if v > 0.5:    # Greater than 50% seems too high
            raise ValueError("Prior failure rate seems unrealistically high")
        return v


class CohortDatabase(BaseModel):
    """Complete cohort database structure"""
    metadata: Dict[str, Union[str, datetime]] = Field(
        default_factory=lambda: {
            "version": "1.0",
            "created_at": datetime.utcnow(),
            "source": "Ford Risk Score Engine",
            "total_cohorts": 0
        }
    )
    cohorts: List[CohortDefinition] = Field(..., min_items=1)
    
    @validator('cohorts')
    def validate_unique_cohort_ids(cls, v):
        """Ensure all cohort IDs are unique"""
        ids = [cohort.cohort_id for cohort in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Cohort IDs must be unique")
        return v
    
    def get_cohort_by_id(self, cohort_id: str) -> Optional[CohortDefinition]:
        """Find cohort by ID"""
        for cohort in self.cohorts:
            if cohort.cohort_id == cohort_id:
                return cohort
        return None
    
    def find_cohorts_by_criteria(
        self, 
        make: Optional[str] = None,
        model: Optional[str] = None,
        year: Optional[int] = None,
        region: Optional[RegionType] = None
    ) -> List[CohortDefinition]:
        """Find cohorts matching criteria"""
        results = []
        for cohort in self.cohorts:
            if make and make not in cohort.makes:
                continue
            if model and model not in cohort.models:
                continue
            if year and year not in cohort.years_supported:
                continue
            if region and cohort.region != region:
                continue
            results.append(cohort)
        return results


class CohortMatchResult(BaseModel):
    """Result of cohort matching for a specific vehicle"""
    vin: str = Field(..., description="Vehicle VIN")
    matched_cohort_id: str = Field(..., description="Best matching cohort ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Match confidence")
    fallback_used: bool = Field(default=False, description="Whether fallback cohort was used")
    match_criteria: Dict[str, str] = Field(..., description="Criteria used for matching")
    
    
class StressorAnalysis(BaseModel):
    """Analysis of vehicle stressors using cohort likelihood ratios"""
    vin: str = Field(..., description="Vehicle VIN")
    cohort_id: str = Field(..., description="Assigned cohort")
    active_stressors: List[str] = Field(..., description="Currently active stressor types")
    stressor_contributions: Dict[str, float] = Field(..., description="Individual LR contributions")
    combined_likelihood_ratio: float = Field(..., description="Combined LR")
    risk_factors: List[str] = Field(..., description="Human-readable risk factors") 