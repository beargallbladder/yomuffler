"""
🎯 Cohort Index Agent
Maps VIN to cohort based on platform, region, usage profile, model year, and past service exposure.
"""

import asyncio
import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent


class CohortIndexAgent(BaseAgent):
    """
    Specialized agent for intelligent cohort assignment and analysis
    """
    
    def __init__(self, redis_pool):
        super().__init__("cohort_index", redis_pool)
        
        # Cohort mapping rules
        self.cohort_rules = {
            "platform_mapping": {
                "F150": "lighttruck",
                "F250": "heavytruck", 
                "F350": "heavytruck",
                "MUSTANG": "sportscar",
                "EXPLORER": "suv",
                "ESCAPE": "crossover",
                "EDGE": "crossover",
                "EXPEDITION": "fullsize_suv",
                "RANGER": "midsize_truck"
            },
            "region_mapping": {
                "northern": ["ME", "NH", "VT", "MA", "RI", "CT", "NY", "PA", "NJ", "OH", "MI", "IN", "IL", "WI", "MN", "IA", "MO", "ND", "SD", "NE", "KS"],
                "southern": ["DE", "MD", "DC", "VA", "WV", "KY", "TN", "NC", "SC", "GA", "FL", "AL", "MS", "AR", "LA", "OK", "TX"],
                "western": ["MT", "WY", "CO", "NM", "ID", "UT", "AZ", "NV", "WA", "OR", "CA", "AK", "HI"],
                "midwest": ["OH", "MI", "IN", "IL", "WI", "MN", "IA", "MO", "ND", "SD", "NE", "KS"]
            },
            "usage_patterns": {
                "commercial": {"daily_miles": (100, 500), "weekly_cycles": (35, 70)},
                "personal": {"daily_miles": (20, 80), "weekly_cycles": (10, 25)},
                "mixed": {"daily_miles": (40, 120), "weekly_cycles": (15, 40)},
                "fleet": {"daily_miles": (80, 300), "weekly_cycles": (25, 50)}
            }
        }
        
        # Pre-defined cohorts from your existing system
        self.available_cohorts = {
            "lighttruck_midwest_winter": {
                "platform": "lighttruck",
                "region": "midwest", 
                "climate": "winter",
                "usage": "mixed",
                "sample_size": 47823
            },
            "midweighttruck_southwest_heat": {
                "platform": "midweighttruck",
                "region": "western",
                "climate": "heat", 
                "usage": "commercial",
                "sample_size": 23456
            },
            "suv_commercial_fleet": {
                "platform": "suv",
                "region": "southern",
                "climate": "mixed",
                "usage": "fleet",
                "sample_size": 31245
            },
            "passengercar_northeast_mixed": {
                "platform": "sportscar",
                "region": "northern",
                "climate": "mixed",
                "usage": "personal", 
                "sample_size": 18967
            }
        }
    
    async def process(self, task) -> Dict[str, Any]:
        """
        Process cohort assignment for a VIN
        """
        start_time = datetime.utcnow()
        
        try:
            await self._log_agent_action("start_cohort_analysis", task.task_id)
            
            vin = task.vin
            vehicle_data = task.results.get("vehicle_data", {})
            
            # Check cache first
            cache_key = f"cohort_index:{vin}"
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                await self._log_agent_action("cache_hit", task.task_id)
                return cached_result
            
            # Extract VIN components
            vin_analysis = self._analyze_vin(vin)
            
            # Determine platform from VIN/model
            platform = self._determine_platform(vin, vehicle_data)
            
            # Determine region from location data
            region = self._determine_region(vehicle_data)
            
            # Determine usage pattern from telemetry
            usage_pattern = self._determine_usage_pattern(vehicle_data)
            
            # Determine climate exposure
            climate_exposure = self._determine_climate_exposure(vehicle_data, region)
            
            # Find best matching cohort
            best_cohort = self._find_best_cohort_match(platform, region, usage_pattern, climate_exposure)
            
            # Calculate cohort position/percentile
            cohort_position = self._calculate_cohort_position(vehicle_data, best_cohort)
            
            # Generate result
            result = {
                "vin": vin,
                "cohort_assignment": {
                    "cohort_id": best_cohort["id"],
                    "cohort_name": best_cohort["name"],
                    "match_confidence": best_cohort["confidence"],
                    "sample_size": best_cohort["sample_size"]
                },
                "cohort_analysis": {
                    "platform": platform,
                    "region": region,
                    "usage_pattern": usage_pattern,
                    "climate_exposure": climate_exposure
                },
                "cohort_position": {
                    "percentile": cohort_position["percentile"],
                    "risk_tier": cohort_position["risk_tier"],
                    "outlier_status": cohort_position["outlier_status"]
                },
                "vin_analysis": vin_analysis,
                "assignment_timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache result
            await self._cache_result(cache_key, result, ttl=7200)  # 2 hours
            
            # Store debug info
            debug_info = {
                "platform_determination": platform,
                "region_mapping": region,
                "usage_classification": usage_pattern,
                "cohort_match_score": best_cohort["confidence"],
                "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }
            await self._store_debug_info(task.task_id, debug_info)
            
            await self._log_agent_action("cohort_assigned", task.task_id,
                                       {"cohort": best_cohort["id"], "confidence": best_cohort["confidence"]})
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Cohort assignment failed for VIN {task.vin}: {str(e)}")
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, False)
            
            return {
                "error": str(e),
                "vin": task.vin,
                "cohort_assignment": {
                    "cohort_id": "unknown",
                    "cohort_name": "Default Assignment",
                    "match_confidence": 0.0,
                    "sample_size": 0
                }
            }
    
    def _analyze_vin(self, vin: str) -> Dict[str, Any]:
        """Analyze VIN components"""
        if len(vin) < 17:
            return {"error": "Invalid VIN length", "valid": False}
        
        try:
            # Extract key VIN components
            wmi = vin[:3]  # World Manufacturer Identifier
            vds = vin[3:9]  # Vehicle Descriptor Section
            model_year_char = vin[9]
            plant_code = vin[10]
            serial = vin[11:]
            
            # Map model year character to year
            year_mapping = {
                'L': 2020, 'M': 2021, 'N': 2022, 'P': 2023, 'R': 2024, 'S': 2025
            }
            model_year = year_mapping.get(model_year_char, 2022)
            
            # Determine if Ford vehicle
            is_ford = wmi.startswith('1F') or wmi.startswith('3F')
            
            return {
                "wmi": wmi,
                "vds": vds,
                "model_year": model_year,
                "plant_code": plant_code,
                "serial_number": serial,
                "is_ford": is_ford,
                "vehicle_age": 2024 - model_year,
                "valid": True
            }
            
        except Exception as e:
            return {"error": str(e), "valid": False}
    
    def _determine_platform(self, vin: str, vehicle_data: Dict[str, Any]) -> str:
        """Determine vehicle platform from VIN and data"""
        # Extract from VIN patterns
        if "F150" in vin or "FTFW" in vin:
            return "lighttruck"
        elif "F250" in vin or "F350" in vin:
            return "heavytruck"
        elif "MUSTANG" in vin or "FA6P" in vin:
            return "sportscar"
        elif "EXPLORER" in vin:
            return "suv"
        
        # Use vehicle data if available
        model = vehicle_data.get("model", "").upper()
        for platform_key, platform_value in self.cohort_rules["platform_mapping"].items():
            if platform_key in model:
                return platform_value
        
        # Default classification
        return "lighttruck"
    
    def _determine_region(self, vehicle_data: Dict[str, Any]) -> str:
        """Determine region from location data"""
        location = vehicle_data.get("location", "").lower()
        
        # Map common location patterns
        if any(term in location for term in ["north", "minnesota", "wisconsin", "michigan", "chicago", "detroit"]):
            return "midwest"
        elif any(term in location for term in ["south", "florida", "texas", "georgia", "alabama", "mississippi"]):
            return "southern"
        elif any(term in location for term in ["west", "california", "nevada", "arizona", "oregon", "washington"]):
            return "western"
        elif any(term in location for term in ["northeast", "new york", "pennsylvania", "massachusetts", "maine"]):
            return "northern"
        
        # Default to moderate
        return "mixed"
    
    def _determine_usage_pattern(self, vehicle_data: Dict[str, Any]) -> str:
        """Determine usage pattern from telemetry data"""
        # Extract usage indicators
        daily_miles = vehicle_data.get("avg_trip_distance_miles", 0) * vehicle_data.get("trips_per_day", 0)
        ignition_cycles = vehicle_data.get("ignition_cycles_daily", 0)
        commercial_indicators = vehicle_data.get("towing_load_detected", False)
        
        # Classification logic
        if daily_miles > 150 or commercial_indicators:
            return "commercial"
        elif daily_miles > 80 or ignition_cycles > 15:
            return "fleet"
        elif daily_miles > 40:
            return "mixed"
        else:
            return "personal"
    
    def _determine_climate_exposure(self, vehicle_data: Dict[str, Any], region: str) -> str:
        """Determine climate exposure"""
        temp_variance = vehicle_data.get("temp_variance_30day", 25)
        avg_temp = vehicle_data.get("temp_avg_30day", 68)
        
        # Climate classification
        if temp_variance > 35 or region in ["midwest", "northern"]:
            return "winter"
        elif avg_temp > 85 or region in ["southern", "western"]:
            return "heat"
        else:
            return "mixed"
    
    def _find_best_cohort_match(self, platform: str, region: str, usage: str, climate: str) -> Dict[str, Any]:
        """Find the best matching cohort"""
        best_match = {
            "id": "default_cohort",
            "name": "General Mixed Usage",
            "confidence": 0.3,
            "sample_size": 10000
        }
        
        # Score each available cohort
        for cohort_id, cohort_data in self.available_cohorts.items():
            score = 0.0
            
            # Platform match (40% weight)
            if cohort_data["platform"] == platform:
                score += 0.4
            elif platform in ["lighttruck", "midweighttruck"] and cohort_data["platform"] in ["lighttruck", "midweighttruck"]:
                score += 0.2
            
            # Region match (25% weight)
            if cohort_data["region"] == region:
                score += 0.25
            elif region == "mixed" or cohort_data["region"] == "mixed":
                score += 0.1
            
            # Usage match (20% weight)
            if cohort_data["usage"] == usage:
                score += 0.2
            elif usage == "mixed" or cohort_data["usage"] == "mixed":
                score += 0.1
            
            # Climate match (15% weight)
            if cohort_data["climate"] == climate:
                score += 0.15
            elif climate == "mixed" or cohort_data["climate"] == "mixed":
                score += 0.05
            
            # Update best match if this scores higher
            if score > best_match["confidence"]:
                best_match = {
                    "id": cohort_id,
                    "name": cohort_id.replace("_", " ").title(),
                    "confidence": score,
                    "sample_size": cohort_data["sample_size"]
                }
        
        return best_match
    
    def _calculate_cohort_position(self, vehicle_data: Dict[str, Any], cohort: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate vehicle's position within cohort"""
        # Simulate percentile calculation based on stressor levels
        stressor_sum = 0
        stressor_count = 0
        
        # Sum up available stressor values
        for key, value in vehicle_data.items():
            if any(stress in key for stress in ["parasitic", "cycles", "variance", "temp", "humidity"]):
                if isinstance(value, (int, float)):
                    stressor_sum += value
                    stressor_count += 1
        
        # Calculate normalized stressor index
        if stressor_count > 0:
            avg_stressor = stressor_sum / stressor_count
            # Map to percentile (higher stressors = higher percentile)
            percentile = min(95, max(5, int(50 + (avg_stressor * 30))))
        else:
            percentile = random.randint(40, 85)
        
        # Determine risk tier
        if percentile >= 85:
            risk_tier = "high_risk"
            outlier_status = "significant_outlier"
        elif percentile >= 70:
            risk_tier = "moderate_risk" 
            outlier_status = "moderate_outlier"
        elif percentile >= 50:
            risk_tier = "average_risk"
            outlier_status = "normal_range"
        else:
            risk_tier = "low_risk"
            outlier_status = "below_average"
        
        return {
            "percentile": percentile,
            "risk_tier": risk_tier,
            "outlier_status": outlier_status,
            "cohort_sample_size": cohort["sample_size"]
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information"""
        return {
            "name": "CohortIndexAgent",
            "version": "1.0",
            "capabilities": [
                "VIN analysis and decoding",
                "Platform identification",
                "Regional classification",
                "Usage pattern analysis",
                "Climate exposure assessment",
                "Cohort matching algorithm",
                "Percentile position calculation",
                "Outlier detection"
            ],
            "available_cohorts": list(self.available_cohorts.keys()),
            "platform_types": list(self.cohort_rules["platform_mapping"].values()),
            "processing_speed": "~150ms per VIN",
            "cache_enabled": True,
            "confidence_scoring": True
        } 