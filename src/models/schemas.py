"""
Ford Bayesian Risk Score Engine - Data Models & Schemas
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class SeverityBucket(str, Enum):
    """Risk severity classification"""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"
    SEVERE = "Severe"


class ServiceType(str, Enum):
    """Service types for swarm agents"""
    VH_TELEMETRY = "vh_telemetry"
    SOC_MONITOR = "soc_monitor"
    TRIP_CYCLE = "trip_cycle"
    CLIMATE_DATA = "climate_data"
    BAYESIAN_ENGINE = "bayesian_engine"
    COHORT_PROCESSOR = "cohort_processor"
    RISK_CALCULATOR = "risk_calculator"
    INDEX_BUILDER = "index_builder"
    API_GATEWAY = "api_gateway"


class CohortAssignment(BaseModel):
    """Vehicle cohort assignment for risk calculation"""
    model: str = Field(..., description="Vehicle model")
    powertrain: str = Field(..., description="Powertrain type")
    region: str = Field(..., description="Geographic region")
    mileage_band: str = Field(..., description="Mileage band classification")
    
    @property
    def cohort_key(self) -> str:
        """Generate cohort key for lookup"""
        return f"{self.model}|{self.powertrain}|{self.region}|{self.mileage_band}"


class VehicleInputData(BaseModel):
    """Input data model for vehicle risk assessment"""
    vin: str = Field(..., min_length=17, max_length=17, description="Vehicle identifier")
    soc_30day_trend: float = Field(..., ge=-1.0, le=0.0, description="Battery SOC decline over 30 days")
    trip_cycles_weekly: int = Field(..., ge=0, le=200, description="Weekly ignition on/off cycles")
    odometer_variance: float = Field(..., ge=0.0, le=1.0, description="Usage pattern irregularity")
    climate_stress_index: float = Field(..., ge=0.0, le=1.0, description="Temperature stress factor")
    maintenance_compliance: float = Field(..., ge=0.0, le=1.0, description="Service adherence score")
    cohort_assignment: CohortAssignment = Field(..., description="Vehicle cohort classification")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data timestamp")
    
    @validator('vin')
    def validate_vin(cls, v):
        """Validate VIN format"""
        if not v.isalnum():
            raise ValueError('VIN must be alphanumeric')
        return v.upper()


class RiskScoreMetadata(BaseModel):
    """Risk score calculation metadata"""
    scored_at: datetime = Field(default_factory=datetime.utcnow, description="Scoring timestamp")
    prior_failure_rate: float = Field(..., description="Cohort base failure rate")
    data_freshness: int = Field(..., description="Hours since last data update")
    model_version: str = Field(default="1.0", description="Risk model version")
    calculation_time_ms: float = Field(..., description="Calculation time in milliseconds")


class RiskScoreOutput(BaseModel):
    """Output data model for risk score results"""
    vin: str = Field(..., description="Vehicle identifier")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Failure probability (0.0-1.0)")
    severity_bucket: SeverityBucket = Field(..., description="Risk severity classification")
    cohort: str = Field(..., description="Vehicle cohort key")
    dominant_stressors: List[str] = Field(..., description="Primary risk factors")
    recommended_action: str = Field(..., description="Dealer workflow instruction")
    revenue_opportunity: Decimal = Field(..., description="Expected service revenue")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    metadata: RiskScoreMetadata = Field(..., description="Calculation metadata")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class BayesianPriors(BaseModel):
    """Industry benchmark priors for Bayesian calculation"""
    cohort_key: str = Field(..., description="Cohort identifier")
    base_failure_rate: float = Field(..., ge=0.0, le=1.0, description="Base failure probability")
    sample_size: int = Field(..., ge=1, description="Sample size for prior")
    confidence_interval: tuple[float, float] = Field(..., description="95% confidence interval")
    source: str = Field(..., description="Data source (Argon, NHTSA, etc.)")
    last_updated: datetime = Field(..., description="Last update timestamp")


class LikelihoodRatios(BaseModel):
    """Likelihood ratios for Bayesian updates"""
    soc_decline_given_failure: float = Field(..., description="P(SOC decline | failure)")
    soc_decline_given_no_failure: float = Field(..., description="P(SOC decline | no failure)")
    trip_cycling_given_failure: float = Field(..., description="P(high trip cycling | failure)")
    trip_cycling_given_no_failure: float = Field(..., description="P(high trip cycling | no failure)")
    climate_stress_given_failure: float = Field(..., description="P(climate stress | failure)")
    climate_stress_given_no_failure: float = Field(..., description="P(climate stress | no failure)")
    maintenance_skip_given_failure: float = Field(..., description="P(maintenance skip | failure)")
    maintenance_skip_given_no_failure: float = Field(..., description="P(maintenance skip | no failure)")


class ProcessingTask(BaseModel):
    """Task for swarm processing queue"""
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of processing task")
    vin: str = Field(..., description="Vehicle identifier")
    input_data: VehicleInputData = Field(..., description="Input data for processing")
    priority: int = Field(default=1, description="Task priority (1=highest)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    status: str = Field(default="pending", description="Task status")
    result: Optional[RiskScoreOutput] = None
    error_message: Optional[str] = None


class SwarmMetrics(BaseModel):
    """Swarm performance metrics"""
    service_type: ServiceType
    worker_id: str
    processed_count: int = 0
    error_count: int = 0
    avg_processing_time_ms: float = 0.0
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    queue_depth: int = 0


class APIRequest(BaseModel):
    """API request model"""
    vin: str = Field(..., min_length=17, max_length=17)
    include_metadata: bool = Field(default=False)
    force_recalculate: bool = Field(default=False)


class APIResponse(BaseModel):
    """API response model"""
    success: bool
    data: Optional[RiskScoreOutput] = None
    error: Optional[str] = None
    request_id: str
    processing_time_ms: float
    cached: bool = False


class BatchProcessingRequest(BaseModel):
    """Batch processing request"""
    vins: List[str] = Field(..., max_items=10000)
    priority: int = Field(default=1, ge=1, le=5)
    callback_url: Optional[str] = None
    batch_id: str = Field(..., description="Unique batch identifier")


class BatchProcessingResponse(BaseModel):
    """Batch processing response"""
    batch_id: str
    total_vins: int
    estimated_completion_time: datetime
    status: str = "queued"
    progress_url: str


class HealthCheck(BaseModel):
    """Health check response"""
    service: str
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    uptime_seconds: float
    dependencies: Dict[str, str]  # service_name -> status


class ConfigurationUpdate(BaseModel):
    """Configuration update message"""
    service_type: Optional[ServiceType] = None
    worker_id: Optional[str] = None
    config_key: str
    config_value: Any
    updated_by: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Database Models (SQLAlchemy-style for reference)
class VehicleRiskScore:
    """Database model for vehicle risk scores"""
    __tablename__ = 'vehicle_risk_scores'
    
    vin: str  # Primary key
    risk_score: float
    severity_bucket: str
    cohort: str
    dominant_stressors: List[str]  # JSON field
    recommended_action: str
    revenue_opportunity: Decimal
    confidence: float
    scored_at: datetime
    expires_at: datetime
    model_version: str
    
    # Indexes
    # - vin (primary)
    # - severity_bucket
    # - cohort
    # - scored_at
    # - expires_at


class ProcessingHistory:
    """Database model for processing history"""
    __tablename__ = 'processing_history'
    
    id: int  # Primary key
    vin: str
    task_id: str
    worker_id: str
    processing_time_ms: float
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    # Indexes
    # - vin
    # - task_id
    # - worker_id
    # - created_at


class SwarmWorkerStatus:
    """Database model for swarm worker status"""
    __tablename__ = 'swarm_worker_status'
    
    worker_id: str  # Primary key
    service_type: str
    status: str
    last_heartbeat: datetime
    processed_count: int
    error_count: int
    avg_processing_time_ms: float
    cpu_usage_percent: float
    memory_usage_mb: float
    queue_depth: int
    
    # Indexes
    # - service_type
    # - status
    # - last_heartbeat 