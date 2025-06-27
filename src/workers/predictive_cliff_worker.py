"""
📈 PREDICTIVE CLIFF ANALYTICS WORKER 📈
Shows the cliff: High cranks + temperature drops = battery death incoming
MISSION: Visual stressor convergence analysis - warn before the cliff!
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import numpy as np
from dataclasses import dataclass

@dataclass
class StressorPattern:
    """Individual stressor pattern data"""
    stressor_type: str
    current_value: float
    baseline_value: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    cliff_distance: int   # Days until critical threshold
    severity: str        # "low", "medium", "high", "critical"

@dataclass
class CliffPrediction:
    """Predictive cliff analysis result"""
    vin: str
    days_to_cliff: int
    cliff_probability: float
    primary_stressors: List[str]
    convergence_score: float
    recommended_action: str
    visual_data: Dict[str, Any]

class PredictiveCliffWorker:
    """
    🎯 CLIFF PREDICTION SPECIALIST
    Analyzes stressor convergence patterns to predict battery failure cliffs
    MISSION: Show dealers the cliff before their customers fall off it
    """
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.logger = logging.getLogger(f"CliffAnalytics-{worker_id}")
        
        # Argonne National Laboratory cliff thresholds (ANL-115925.pdf)
        self.cliff_thresholds = {
            "ignition_cycles_daily": {
                "baseline": 8,      # Normal daily starts
                "warning": 15,      # Elevated usage
                "critical": 25,     # Extreme short-trip pattern
                "cliff": 35         # Battery death zone
            },
            "temperature_delta_forecast": {
                "baseline": 20,     # Normal seasonal swing
                "warning": 35,      # Moderate stress
                "critical": 45,     # High stress environment
                "cliff": 60         # Extreme thermal cycling
            },
            "soc_decline_rate": {
                "baseline": 0.02,   # 2% annual decline
                "warning": 0.05,    # 5% decline - monitor
                "critical": 0.10,   # 10% decline - intervene
                "cliff": 0.20       # 20% decline - immediate action
            },
            "recharge_opportunity": {
                "baseline": 0.80,   # 80% of trips >6 miles
                "warning": 0.60,    # 60% proper recharge
                "critical": 0.40,   # 40% proper recharge
                "cliff": 0.20       # 20% proper recharge - cliff edge
            }
        }
        
        # Convergence patterns that predict cliff events
        self.convergence_patterns = {
            "winter_death_spiral": {
                "primary_stressors": ["temperature_delta_forecast", "ignition_cycles_daily"],
                "pattern": "Both increasing as winter approaches",
                "cliff_accelerator": 3.2,  # Multiplies cliff approach speed
                "description": "Cold weather + frequent starts = rapid battery death"
            },
            "short_trip_degradation": {
                "primary_stressors": ["ignition_cycles_daily", "recharge_opportunity"],
                "pattern": "High starts + low recharge opportunities",
                "cliff_accelerator": 2.8,
                "description": "Urban driving pattern preventing battery recharge"
            },
            "thermal_cycling_fatigue": {
                "primary_stressors": ["temperature_delta_forecast", "soc_decline_rate"],
                "pattern": "Extreme temperatures + accelerated SOC decline",
                "cliff_accelerator": 2.5,
                "description": "Temperature extremes causing internal battery damage"
            },
            "commercial_fleet_overuse": {
                "primary_stressors": ["ignition_cycles_daily", "soc_decline_rate"],
                "pattern": "Very high daily usage + rapid capacity loss",
                "cliff_accelerator": 4.1,
                "description": "Fleet vehicle overuse pattern"
            }
        }
        
        # Seasonal forecast data (30-day weather prediction simulation)
        self.seasonal_forecasts = {
            "October": {"avg_temp_drop": 15, "cold_snap_probability": 0.25},
            "November": {"avg_temp_drop": 25, "cold_snap_probability": 0.45},
            "December": {"avg_temp_drop": 35, "cold_snap_probability": 0.70},
            "January": {"avg_temp_drop": 40, "cold_snap_probability": 0.85},
            "February": {"avg_temp_drop": 38, "cold_snap_probability": 0.80}
        }
        
        self.logger.info(f"🚀 Predictive Cliff Analytics Worker {worker_id} initialized - CLIFF DETECTION ACTIVE")
    
    async def analyze_cliff_risk(self, vin: str, vehicle_data: Dict[str, Any], 
                               telemetry_data: Dict[str, Any]) -> CliffPrediction:
        """
        MAIN CLIFF ANALYSIS - Predict when this VIN will hit the battery cliff
        
        Args:
            vin: Vehicle VIN
            vehicle_data: Decoded vehicle information
            telemetry_data: Current stressor measurements
            
        Returns:
            Comprehensive cliff prediction with visual data
        """
        self.logger.info(f"🔍 CLIFF ANALYSIS STARTING - VIN: {vin}")
        
        try:
            # Extract current stressor patterns
            stressor_patterns = await self._extract_stressor_patterns(vin, vehicle_data, telemetry_data)
            
            # Analyze convergence patterns
            convergence_analysis = await self._analyze_convergence_patterns(stressor_patterns)
            
            # Generate cliff prediction
            cliff_prediction = await self._predict_cliff_event(vin, stressor_patterns, convergence_analysis)
            
            # Generate visualization data
            visual_data = await self._generate_cliff_visualization(vin, stressor_patterns, cliff_prediction)
            cliff_prediction.visual_data = visual_data
            
            self.logger.info(f"✅ CLIFF ANALYSIS COMPLETE - {cliff_prediction.days_to_cliff} days to cliff")
            
            return cliff_prediction
            
        except Exception as e:
            self.logger.error(f"🚨 Cliff analysis error for VIN {vin}: {str(e)}")
            
            # Return safe fallback prediction
            return CliffPrediction(
                vin=vin,
                days_to_cliff=365,  # Default to 1 year
                cliff_probability=0.15,
                primary_stressors=["unknown"],
                convergence_score=0.0,
                recommended_action="Schedule routine maintenance",
                visual_data={}
            )
    
    async def _extract_stressor_patterns(self, vin: str, vehicle_data: Dict, 
                                       telemetry_data: Dict) -> List[StressorPattern]:
        """Extract individual stressor patterns from vehicle data"""
        
        patterns = []
        
        # Ignition cycles analysis
        current_daily_starts = telemetry_data.get("daily_ignition_cycles", 8)
        baseline_starts = self.cliff_thresholds["ignition_cycles_daily"]["baseline"]
        
        ignition_pattern = StressorPattern(
            stressor_type="ignition_cycles_daily",
            current_value=current_daily_starts,
            baseline_value=baseline_starts,
            trend_direction=self._calculate_trend("ignition", current_daily_starts, baseline_starts),
            cliff_distance=self._calculate_cliff_distance("ignition_cycles_daily", current_daily_starts),
            severity=self._calculate_severity("ignition_cycles_daily", current_daily_starts)
        )
        patterns.append(ignition_pattern)
        
        # Temperature forecast analysis (next 30 days)
        current_month = datetime.now().strftime("%B")
        location = vehicle_data.get("location", "moderate")
        temp_forecast = await self._generate_temperature_forecast(location, current_month)
        
        temp_pattern = StressorPattern(
            stressor_type="temperature_delta_forecast",
            current_value=temp_forecast["max_delta"],
            baseline_value=self.cliff_thresholds["temperature_delta_forecast"]["baseline"],
            trend_direction="increasing" if temp_forecast["trend"] > 0 else "decreasing",
            cliff_distance=self._calculate_cliff_distance("temperature_delta_forecast", temp_forecast["max_delta"]),
            severity=self._calculate_severity("temperature_delta_forecast", temp_forecast["max_delta"])
        )
        patterns.append(temp_pattern)
        
        # SOC decline rate analysis
        current_soc_decline = telemetry_data.get("soc_decline_rate", 0.023)  # Argonne baseline
        baseline_soc = self.cliff_thresholds["soc_decline_rate"]["baseline"]
        
        soc_pattern = StressorPattern(
            stressor_type="soc_decline_rate",
            current_value=current_soc_decline,
            baseline_value=baseline_soc,
            trend_direction=self._calculate_trend("soc", current_soc_decline, baseline_soc),
            cliff_distance=self._calculate_cliff_distance("soc_decline_rate", current_soc_decline),
            severity=self._calculate_severity("soc_decline_rate", current_soc_decline)
        )
        patterns.append(soc_pattern)
        
        # Recharge opportunity analysis (6-mile rule from Argonne)
        short_trips_pct = telemetry_data.get("short_trip_percentage", 0.30)
        recharge_opportunity = 1.0 - short_trips_pct  # Inverse relationship
        baseline_recharge = self.cliff_thresholds["recharge_opportunity"]["baseline"]
        
        recharge_pattern = StressorPattern(
            stressor_type="recharge_opportunity",
            current_value=recharge_opportunity,
            baseline_value=baseline_recharge,
            trend_direction=self._calculate_trend("recharge", recharge_opportunity, baseline_recharge),
            cliff_distance=self._calculate_cliff_distance("recharge_opportunity", recharge_opportunity),
            severity=self._calculate_severity("recharge_opportunity", recharge_opportunity)
        )
        patterns.append(recharge_pattern)
        
        return patterns
    
    async def _analyze_convergence_patterns(self, stressor_patterns: List[StressorPattern]) -> Dict[str, Any]:
        """Analyze how multiple stressors are converging toward cliff events"""
        
        convergence_analysis = {
            "detected_patterns": [],
            "convergence_score": 0.0,
            "primary_drivers": [],
            "pattern_descriptions": []
        }
        
        # Create stressor lookup for pattern matching
        stressor_lookup = {pattern.stressor_type: pattern for pattern in stressor_patterns}
        
        # Check each convergence pattern
        for pattern_name, pattern_config in self.convergence_patterns.items():
            pattern_stressors = pattern_config["primary_stressors"]
            
            # Check if all required stressors are present and elevated
            pattern_active = True
            pattern_severity_sum = 0.0
            
            for stressor_type in pattern_stressors:
                if stressor_type in stressor_lookup:
                    stressor = stressor_lookup[stressor_type]
                    severity_score = self._severity_to_score(stressor.severity)
                    pattern_severity_sum += severity_score
                    
                    # Pattern only active if stressor is at least "medium" severity
                    if severity_score < 2:
                        pattern_active = False
                        break
                else:
                    pattern_active = False
                    break
            
            if pattern_active:
                # Calculate pattern convergence strength
                avg_severity = pattern_severity_sum / len(pattern_stressors)
                accelerator = pattern_config["cliff_accelerator"]
                pattern_score = avg_severity * accelerator
                
                convergence_analysis["detected_patterns"].append({
                    "pattern_name": pattern_name,
                    "pattern_score": pattern_score,
                    "stressors_involved": pattern_stressors,
                    "description": pattern_config["description"],
                    "cliff_accelerator": accelerator
                })
                
                convergence_analysis["convergence_score"] += pattern_score
        
        # Sort patterns by severity
        convergence_analysis["detected_patterns"].sort(key=lambda x: x["pattern_score"], reverse=True)
        
        # Extract primary drivers
        if convergence_analysis["detected_patterns"]:
            primary_pattern = convergence_analysis["detected_patterns"][0]
            convergence_analysis["primary_drivers"] = primary_pattern["stressors_involved"]
            convergence_analysis["pattern_descriptions"] = [p["description"] for p in convergence_analysis["detected_patterns"]]
        
        return convergence_analysis
    
    async def _predict_cliff_event(self, vin: str, stressor_patterns: List[StressorPattern], 
                                 convergence_analysis: Dict) -> CliffPrediction:
        """Generate the actual cliff prediction"""
        
        # Find the shortest cliff distance from all stressors
        min_cliff_distance = min(pattern.cliff_distance for pattern in stressor_patterns)
        
        # Apply convergence acceleration
        convergence_score = convergence_analysis["convergence_score"]
        if convergence_score > 0:
            # Higher convergence = cliff approaches faster
            acceleration_factor = min(convergence_score / 10.0, 0.8)  # Max 80% acceleration
            accelerated_distance = int(min_cliff_distance * (1.0 - acceleration_factor))
            days_to_cliff = max(accelerated_distance, 7)  # Minimum 7 days warning
        else:
            days_to_cliff = min_cliff_distance
        
        # Calculate cliff probability
        if days_to_cliff <= 30:
            cliff_probability = min(0.95, 0.30 + (convergence_score * 0.1))
        elif days_to_cliff <= 90:
            cliff_probability = min(0.80, 0.15 + (convergence_score * 0.08))
        else:
            cliff_probability = min(0.50, 0.05 + (convergence_score * 0.05))
        
        # Primary stressors driving the cliff
        primary_stressors = convergence_analysis.get("primary_drivers", [])
        if not primary_stressors:
            # Fall back to highest severity individual stressors
            critical_stressors = [p for p in stressor_patterns if p.severity in ["critical", "high"]]
            primary_stressors = [p.stressor_type for p in critical_stressors[:2]]
        
        # Generate recommended action
        recommended_action = await self._generate_cliff_action(days_to_cliff, cliff_probability, primary_stressors)
        
        return CliffPrediction(
            vin=vin,
            days_to_cliff=days_to_cliff,
            cliff_probability=cliff_probability,
            primary_stressors=primary_stressors,
            convergence_score=convergence_score,
            recommended_action=recommended_action,
            visual_data={}  # Will be populated later
        )
    
    async def _generate_temperature_forecast(self, location: str, current_month: str) -> Dict[str, Any]:
        """Generate 30-day temperature forecast for cliff prediction"""
        
        # Get seasonal data
        seasonal_data = self.seasonal_forecasts.get(current_month, {"avg_temp_drop": 10, "cold_snap_probability": 0.1})
        
        # Location modifiers
        location_modifiers = {
            "north": 1.3,    # Colder regions
            "south": 0.7,    # Warmer regions
            "moderate": 1.0, # Baseline
            "commercial": 1.1  # Urban heat islands
        }
        
        location_factor = location_modifiers.get(location.lower(), 1.0)
        
        # Calculate forecast
        base_temp_drop = seasonal_data["avg_temp_drop"] * location_factor
        cold_snap_probability = seasonal_data["cold_snap_probability"]
        
        # Add random variation for realism
        temp_variation = np.random.normal(0, 5)  # ±5°F standard deviation
        max_delta = base_temp_drop + temp_variation
        
        # Cold snap adjustment
        if np.random.random() < cold_snap_probability:
            max_delta += np.random.normal(15, 5)  # Cold snap adds 15±5°F
        
        return {
            "max_delta": max(max_delta, 10),  # Minimum 10°F delta
            "trend": 1 if current_month in ["October", "November", "December"] else -1,
            "cold_snap_risk": cold_snap_probability,
            "location_factor": location_factor
        }
    
    def _calculate_trend(self, stressor_type: str, current: float, baseline: float) -> str:
        """Calculate trend direction for stressor"""
        ratio = current / baseline if baseline > 0 else 1.0
        
        if ratio > 1.2:
            return "increasing"
        elif ratio < 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_cliff_distance(self, stressor_type: str, current_value: float) -> int:
        """Calculate days until this stressor reaches cliff threshold"""
        
        thresholds = self.cliff_thresholds[stressor_type]
        cliff_threshold = thresholds["cliff"]
        critical_threshold = thresholds["critical"]
        
        if stressor_type == "recharge_opportunity":
            # Lower values are worse for recharge opportunity
            if current_value <= cliff_threshold:
                return 0  # Already at cliff
            elif current_value <= critical_threshold:
                return 30  # Close to cliff
            else:
                # Linear interpolation
                distance_factor = (current_value - cliff_threshold) / (critical_threshold - cliff_threshold)
                return int(365 * distance_factor)
        else:
            # Higher values are worse for other stressors
            if current_value >= cliff_threshold:
                return 0  # Already at cliff
            elif current_value >= critical_threshold:
                return 30  # Close to cliff
            else:
                # Linear interpolation
                distance_factor = (cliff_threshold - current_value) / (cliff_threshold - critical_threshold)
                return int(365 * distance_factor)
    
    def _calculate_severity(self, stressor_type: str, current_value: float) -> str:
        """Calculate severity level for stressor"""
        
        thresholds = self.cliff_thresholds[stressor_type]
        
        if stressor_type == "recharge_opportunity":
            # Lower values are worse for recharge opportunity
            if current_value <= thresholds["cliff"]:
                return "critical"
            elif current_value <= thresholds["critical"]:
                return "high"
            elif current_value <= thresholds["warning"]:
                return "medium"
            else:
                return "low"
        else:
            # Higher values are worse for other stressors
            if current_value >= thresholds["cliff"]:
                return "critical"
            elif current_value >= thresholds["critical"]:
                return "high"
            elif current_value >= thresholds["warning"]:
                return "medium"
            else:
                return "low"
    
    def _severity_to_score(self, severity: str) -> float:
        """Convert severity to numeric score for calculations"""
        return {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(severity, 1)
    
    async def _generate_cliff_action(self, days_to_cliff: int, cliff_probability: float, 
                                   primary_stressors: List[str]) -> str:
        """Generate recommended action based on cliff prediction"""
        
        if days_to_cliff <= 7:
            return "URGENT: Schedule immediate battery inspection"
        elif days_to_cliff <= 30:
            return "HIGH PRIORITY: Contact customer for proactive service"
        elif days_to_cliff <= 90:
            return "MEDIUM: Schedule preventive maintenance"
        elif cliff_probability > 0.50:
            return "MONITOR: Watch for pattern changes"
        else:
            return "ROUTINE: Include in next scheduled service"
    
    async def _generate_cliff_visualization(self, vin: str, stressor_patterns: List[StressorPattern], 
                                          cliff_prediction: CliffPrediction) -> Dict[str, Any]:
        """Generate data for cliff visualization charts"""
        
        # Stressor convergence chart data
        stressor_chart_data = []
        for pattern in stressor_patterns:
            stressor_chart_data.append({
                "name": pattern.stressor_type.replace("_", " ").title(),
                "current": pattern.current_value,
                "baseline": pattern.baseline_value,
                "severity": pattern.severity,
                "cliff_distance": pattern.cliff_distance,
                "trend": pattern.trend_direction
            })
        
        # Cliff timeline chart (30-day projection)
        timeline_data = []
        for day in range(0, min(cliff_prediction.days_to_cliff + 30, 365), 7):
            # Simulate risk progression
            risk_factor = 1.0 - (cliff_prediction.days_to_cliff - day) / cliff_prediction.days_to_cliff
            risk_factor = max(0.1, min(1.0, risk_factor))
            
            timeline_data.append({
                "day": day,
                "risk_level": risk_factor * cliff_prediction.cliff_probability,
                "event": "Battery Cliff" if day == cliff_prediction.days_to_cliff else None
            })
        
        # Pattern convergence visualization
        convergence_data = {
            "convergence_score": cliff_prediction.convergence_score,
            "primary_stressors": cliff_prediction.primary_stressors,
            "cliff_probability": cliff_prediction.cliff_probability,
            "days_remaining": cliff_prediction.days_to_cliff
        }
        
        return {
            "stressor_patterns": stressor_chart_data,
            "cliff_timeline": timeline_data,
            "convergence_analysis": convergence_data,
            "generated_at": datetime.now().isoformat(),
            "vin": vin
        }
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """Get current cliff analytics worker status"""
        return {
            "worker_id": self.worker_id,
            "worker_type": "predictive_cliff_analytics",
            "mission": "CLIFF_PREDICTION_AND_EARLY_WARNING",
            "cliff_patterns_monitored": len(self.convergence_patterns),
            "stressor_thresholds": len(self.cliff_thresholds),
            "seasonal_forecasts": len(self.seasonal_forecasts),
            "status": "CLIFF_GUARDIAN_ACTIVE",
            "last_updated": datetime.now().isoformat()
        }

# Example usage
async def test_cliff_analytics():
    """Test the predictive cliff analytics worker"""
    worker = PredictiveCliffWorker("cliff_guardian_1")
    
    # Test vehicle data
    vehicle_data = {
        "make": "Ford",
        "model": "F-150",
        "year": 2022,
        "location": "north",
        "vin": "1FTFW1ET0LFA12345"
    }
    
    # Test telemetry data (high-risk scenario)
    telemetry_data = {
        "daily_ignition_cycles": 22,      # High - lots of short trips
        "soc_decline_rate": 0.08,         # High - battery degrading fast
        "short_trip_percentage": 0.70,    # High - not following 6-mile rule
        "avg_trip_distance": 3.2          # Short trips
    }
    
    # Analyze cliff risk
    cliff_prediction = await worker.analyze_cliff_risk(
        "1FTFW1ET0LFA12345",
        vehicle_data,
        telemetry_data
    )
    
    print(f"🔍 CLIFF ANALYSIS RESULTS:")
    print(f"Days to Cliff: {cliff_prediction.days_to_cliff}")
    print(f"Cliff Probability: {cliff_prediction.cliff_probability:.1%}")
    print(f"Primary Stressors: {cliff_prediction.primary_stressors}")
    print(f"Convergence Score: {cliff_prediction.convergence_score:.2f}")
    print(f"Recommended Action: {cliff_prediction.recommended_action}")
    
    # Worker status
    status = await worker.get_worker_status()
    print(f"📊 Cliff Worker Status: {json.dumps(status, indent=2)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_cliff_analytics()) 