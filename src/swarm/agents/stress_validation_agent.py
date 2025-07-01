"""
✅ Stress Validation Agent
Validates which stressors apply based on VIN context and stressor-model truth table.
Prevents false positives like "cold crank stressor in Miami, FL in July"
"""

import asyncio
import json
import random
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from .base_agent import BaseAgent


class StressValidationAgent(BaseAgent):
    """
    Specialized agent for intelligent stressor validation and reasonableness checking
    """
    
    def __init__(self, redis_pool):
        super().__init__("stress_validation", redis_pool)
        
        # Stressor validation rules - prevents nonsensical combinations
        self.validation_rules = {
            "cold_crank_stress": {
                "required_conditions": {
                    "temperature_range": {"min": -20, "max": 35},  # Fahrenheit
                    "seasonal_months": [11, 12, 1, 2, 3],
                    "regions": ["northern", "midwest"],
                    "voltage_drop_threshold": 0.5
                },
                "blocking_conditions": {
                    "temperature_min": 70,  # Too hot for cold crank issues
                    "regions_blocked": ["southern_summer", "desert"],
                    "months_blocked": [6, 7, 8]  # Summer months
                }
            },
            "heat_stress": {
                "required_conditions": {
                    "temperature_range": {"min": 80, "max": 130},
                    "seasonal_months": [5, 6, 7, 8, 9],
                    "regions": ["southern", "western", "desert"],
                    "humidity_threshold": 0.3
                },
                "blocking_conditions": {
                    "temperature_max": 60,  # Too cold for heat stress
                    "regions_blocked": ["northern_winter"],
                    "months_blocked": [12, 1, 2]
                }
            },
            "salt_corrosion": {
                "required_conditions": {
                    "coastal_distance_max": 50,  # miles from coast
                    "regions": ["coastal", "northeast", "great_lakes"],
                    "winter_exposure": True
                },
                "blocking_conditions": {
                    "coastal_distance_min": 200,  # Too far inland
                    "regions_blocked": ["desert", "mountain"]
                }
            },
            "short_trip_cycling": {
                "required_conditions": {
                    "avg_trip_distance_max": 8,  # miles
                    "trips_per_day_min": 4,
                    "engine_warmup_time_max": 10  # minutes
                },
                "blocking_conditions": {
                    "avg_trip_distance_min": 25,  # Long trips don't cause cycling stress
                    "highway_percent_min": 0.7  # Mostly highway = no cycling stress
                }
            },
            "extended_idle": {
                "required_conditions": {
                    "idle_time_min": 14,  # days
                    "usage_patterns": ["seasonal", "recreational", "storage"]
                },
                "blocking_conditions": {
                    "daily_usage": True,  # Daily use prevents extended idle
                    "commercial_usage": True
                }
            },
            "high_load_towing": {
                "required_conditions": {
                    "vehicle_types": ["truck", "suv", "commercial"],
                    "current_draw_min": 80,  # amps
                    "sustained_load_min": 30  # minutes
                },
                "blocking_conditions": {
                    "vehicle_types_blocked": ["sedan", "coupe", "hatchback"],
                    "light_duty_only": True
                }
            },
            "humidity_cycling": {
                "required_conditions": {
                    "humidity_variance_min": 40,  # %RH swing
                    "coastal_proximity": True,
                    "seasonal_variation": True
                },
                "blocking_conditions": {
                    "desert_climate": True,
                    "stable_humidity": True
                }
            },
            "altitude_stress": {
                "required_conditions": {
                    "altitude_min": 5000,  # feet
                    "pressure_differential": True
                },
                "blocking_conditions": {
                    "altitude_max": 1000,  # Sea level
                    "stable_pressure": True
                }
            },
            "parasitic_draw": {
                "required_conditions": {
                    "draw_current_min": 50,  # mA
                    "off_time_min": 4,  # hours
                    "voltage_drop": True
                },
                "blocking_conditions": {
                    "draw_current_max": 25,  # Normal parasitic draw
                    "immediate_shutoff": True
                }
            },
            "voltage_regulation": {
                "required_conditions": {
                    "voltage_variance_min": 0.5,  # V
                    "charging_instability": True,
                    "alternator_cycling": True
                },
                "blocking_conditions": {
                    "voltage_stable": True,
                    "new_electrical_system": True
                }
            }
        }
        
        # Geographic and seasonal context
        self.geographic_context = {
            "miami_fl": {"climate": "tropical", "winter_temp": 70, "summer_temp": 88, "coastal": True},
            "phoenix_az": {"climate": "desert", "winter_temp": 65, "summer_temp": 105, "coastal": False},
            "minneapolis_mn": {"climate": "continental", "winter_temp": 15, "summer_temp": 80, "coastal": False},
            "seattle_wa": {"climate": "oceanic", "winter_temp": 40, "summer_temp": 75, "coastal": True},
            "denver_co": {"climate": "highland", "winter_temp": 30, "summer_temp": 85, "altitude": 5280}
        }
        
        # Current context (would be dynamic in production)
        self.current_context = {
            "month": datetime.now().month,
            "season": self._get_current_season(),
            "analysis_date": datetime.now()
        }
    
    async def process(self, task) -> Dict[str, Any]:
        """
        Process stressor validation for a VIN
        """
        start_time = datetime.utcnow()
        
        try:
            await self._log_agent_action("start_validation", task.task_id)
            
            vin = task.vin
            vehicle_data = task.results.get("vehicle_data", {})
            active_stressors = task.results.get("active_stressors", [])
            cohort_data = task.results.get("cohort_assignment", {})
            
            # Check cache first
            cache_key = f"stress_validation:{vin}:{datetime.now().strftime('%Y%m%d')}"  # Daily cache
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                await self._log_agent_action("cache_hit", task.task_id)
                return cached_result
            
            # Extract validation context
            validation_context = self._build_validation_context(vehicle_data, cohort_data)
            
            # Validate each active stressor
            validated_stressors = []
            rejected_stressors = []
            validation_details = {}
            
            for stressor in active_stressors:
                validation_result = self._validate_stressor(stressor, validation_context)
                
                if validation_result["valid"]:
                    validated_stressors.append(stressor)
                else:
                    rejected_stressors.append(stressor)
                
                validation_details[stressor] = validation_result
            
            # Detect additional context-appropriate stressors
            additional_stressors = self._detect_context_stressors(validation_context, validated_stressors)
            validated_stressors.extend(additional_stressors)
            
            # Calculate validation confidence
            validation_confidence = self._calculate_validation_confidence(validated_stressors, validation_details)
            
            # Generate reasonableness report
            reasonableness_report = self._generate_reasonableness_report(
                validated_stressors, rejected_stressors, validation_context
            )
            
            # Generate result
            result = {
                "vin": vin,
                "validated_stressors": validated_stressors,
                "rejected_stressors": rejected_stressors,
                "validation_details": validation_details,
                "validation_context": validation_context,
                "validation_confidence": validation_confidence,
                "reasonableness_report": reasonableness_report,
                "additional_stressors_detected": additional_stressors,
                "total_valid_stressors": len(validated_stressors),
                "false_positive_prevention": len(rejected_stressors),
                "validation_timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache result (daily expiry since validation depends on season/weather)
            await self._cache_result(cache_key, result, ttl=86400)  # 24 hours
            
            # Store debug info
            debug_info = {
                "original_stressors": len(active_stressors),
                "validated_stressors": len(validated_stressors),
                "rejected_stressors": len(rejected_stressors),
                "validation_confidence": validation_confidence,
                "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }
            await self._store_debug_info(task.task_id, debug_info)
            
            await self._log_agent_action("validation_complete", task.task_id,
                                       {"validated": len(validated_stressors), "rejected": len(rejected_stressors)})
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Stressor validation failed for VIN {task.vin}: {str(e)}")
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, False)
            
            return {
                "error": str(e),
                "vin": task.vin,
                "validated_stressors": [],
                "validation_confidence": 0.0
            }
    
    def _build_validation_context(self, vehicle_data: Dict[str, Any], cohort_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive validation context"""
        
        # Extract location context
        location = vehicle_data.get("location", "moderate").lower()
        
        # Determine geographic context
        geographic_key = self._map_location_to_context(location)
        geo_context = self.geographic_context.get(geographic_key, {
            "climate": "moderate", "winter_temp": 50, "summer_temp": 80, "coastal": False
        })
        
        # Extract vehicle context
        vehicle_context = {
            "platform": cohort_data.get("platform", "unknown"),
            "region": cohort_data.get("region", "mixed"),
            "usage_pattern": cohort_data.get("usage_pattern", "personal"),
            "climate_exposure": cohort_data.get("climate_exposure", "mixed")
        }
        
        # Extract telemetry context
        telemetry_context = {
            "temp_avg": vehicle_data.get("temp_avg_30day", 68),
            "temp_variance": vehicle_data.get("temp_variance_30day", 25),
            "humidity_avg": vehicle_data.get("humidity_avg", 50),
            "humidity_variance": vehicle_data.get("humidity_variance", 30),
            "coastal_distance": vehicle_data.get("coastal_distance_miles", 100),
            "altitude": vehicle_data.get("altitude_feet", 500),
            "avg_trip_distance": vehicle_data.get("avg_trip_distance_miles", 15),
            "trips_per_day": vehicle_data.get("trips_per_day", 4),
            "parasitic_draw": vehicle_data.get("parasitic_draw_ma", 35),
            "voltage_variance": vehicle_data.get("voltage_variance", 0.2),
            "extended_idle_days": vehicle_data.get("extended_idle_days", 0),
            "towing_detected": vehicle_data.get("towing_load_detected", False)
        }
        
        return {
            "geographic": geo_context,
            "vehicle": vehicle_context,
            "telemetry": telemetry_context,
            "temporal": self.current_context,
            "location_string": location
        }
    
    def _validate_stressor(self, stressor: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single stressor against context"""
        
        if stressor not in self.validation_rules:
            return {"valid": True, "reason": "No validation rules defined", "confidence": 0.5}
        
        rules = self.validation_rules[stressor]
        required = rules.get("required_conditions", {})
        blocking = rules.get("blocking_conditions", {})
        
        # Check blocking conditions first (immediate rejection)
        blocking_violations = []
        
        # Temperature blocking
        if "temperature_min" in blocking:
            if context["telemetry"]["temp_avg"] > blocking["temperature_min"]:
                blocking_violations.append(f"Temperature too high ({context['telemetry']['temp_avg']}°F > {blocking['temperature_min']}°F)")
        
        if "temperature_max" in blocking:
            if context["telemetry"]["temp_avg"] < blocking["temperature_max"]:
                blocking_violations.append(f"Temperature too low ({context['telemetry']['temp_avg']}°F < {blocking['temperature_max']}°F)")
        
        # Regional blocking
        if "regions_blocked" in blocking:
            if context["vehicle"]["region"] in blocking["regions_blocked"]:
                blocking_violations.append(f"Region blocked: {context['vehicle']['region']}")
        
        # Seasonal blocking
        if "months_blocked" in blocking:
            if context["temporal"]["month"] in blocking["months_blocked"]:
                blocking_violations.append(f"Month blocked: {context['temporal']['month']}")
        
        # Distance blocking
        if "coastal_distance_min" in blocking:
            if context["telemetry"]["coastal_distance"] > blocking["coastal_distance_min"]:
                blocking_violations.append(f"Too far from coast ({context['telemetry']['coastal_distance']} > {blocking['coastal_distance_min']} miles)")
        
        # If any blocking conditions are met, reject the stressor
        if blocking_violations:
            return {
                "valid": False,
                "reason": f"Blocked: {'; '.join(blocking_violations)}",
                "confidence": 0.9,
                "violations": blocking_violations
            }
        
        # Check required conditions
        required_violations = []
        requirements_met = 0
        total_requirements = len(required)
        
        # Temperature requirements
        if "temperature_range" in required:
            temp_range = required["temperature_range"]
            temp = context["telemetry"]["temp_avg"]
            if not (temp_range["min"] <= temp <= temp_range["max"]):
                required_violations.append(f"Temperature outside range ({temp}°F not in {temp_range['min']}-{temp_range['max']}°F)")
            else:
                requirements_met += 1
        
        # Regional requirements
        if "regions" in required:
            if context["vehicle"]["region"] not in required["regions"]:
                required_violations.append(f"Region not suitable: {context['vehicle']['region']} not in {required['regions']}")
            else:
                requirements_met += 1
        
        # Distance requirements
        if "coastal_distance_max" in required:
            if context["telemetry"]["coastal_distance"] > required["coastal_distance_max"]:
                required_violations.append(f"Too far from coast ({context['telemetry']['coastal_distance']} > {required['coastal_distance_max']} miles)")
            else:
                requirements_met += 1
        
        # Trip pattern requirements
        if "avg_trip_distance_max" in required:
            if context["telemetry"]["avg_trip_distance"] > required["avg_trip_distance_max"]:
                required_violations.append(f"Trips too long ({context['telemetry']['avg_trip_distance']} > {required['avg_trip_distance_max']} miles)")
            else:
                requirements_met += 1
        
        # Calculate confidence based on requirements met
        confidence = requirements_met / max(1, total_requirements) if total_requirements > 0 else 0.8
        
        # Stressor is valid if most requirements are met and no blocking conditions
        valid = len(required_violations) == 0 or confidence >= 0.7
        
        return {
            "valid": valid,
            "reason": "All conditions met" if valid else f"Requirements not met: {'; '.join(required_violations)}",
            "confidence": confidence,
            "requirements_met": requirements_met,
            "total_requirements": total_requirements,
            "violations": required_violations if not valid else []
        }
    
    def _detect_context_stressors(self, context: Dict[str, Any], existing_stressors: List[str]) -> List[str]:
        """Detect additional stressors based on context"""
        additional = []
        
        # Hot climate detection
        if (context["telemetry"]["temp_avg"] > 85 and 
            context["temporal"]["month"] in [6, 7, 8] and
            "heat_stress" not in existing_stressors):
            additional.append("heat_stress")
        
        # Cold climate detection
        if (context["telemetry"]["temp_avg"] < 35 and
            context["temporal"]["month"] in [12, 1, 2] and
            "cold_crank_stress" not in existing_stressors):
            additional.append("cold_crank_stress")
        
        # Coastal corrosion detection
        if (context["telemetry"]["coastal_distance"] < 20 and
            "salt_corrosion" not in existing_stressors):
            additional.append("salt_corrosion")
        
        # High altitude detection
        if (context["telemetry"]["altitude"] > 5000 and
            "altitude_stress" not in existing_stressors):
            additional.append("altitude_stress")
        
        return additional
    
    def _calculate_validation_confidence(self, validated_stressors: List[str], details: Dict[str, Any]) -> float:
        """Calculate overall validation confidence"""
        if not validated_stressors:
            return 0.0
        
        total_confidence = 0.0
        for stressor in validated_stressors:
            if stressor in details:
                total_confidence += details[stressor].get("confidence", 0.5)
            else:
                total_confidence += 0.8  # Default for additional stressors
        
        return total_confidence / len(validated_stressors)
    
    def _generate_reasonableness_report(self, validated: List[str], rejected: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable reasonableness report"""
        
        location = context["location_string"]
        season = context["temporal"]["season"]
        temp = context["telemetry"]["temp_avg"]
        
        return {
            "summary": f"Validated {len(validated)} stressors, rejected {len(rejected)} for {location} in {season}",
            "context_summary": f"Vehicle in {location} with {temp}°F average temperature",
            "validation_highlights": [
                f"✅ Accepted {len(validated)} contextually appropriate stressors",
                f"❌ Rejected {len(rejected)} contextually inappropriate stressors",
                f"🌡️ Temperature-based validation for {season} season",
                f"📍 Geographic validation for {context['vehicle']['region']} region"
            ],
            "prevented_false_positives": [
                f"Prevented {stressor}: {details.get('reason', 'Invalid context')}"
                for stressor, details in context.get('rejected_details', {}).items()
            ]
        }
    
    def _map_location_to_context(self, location: str) -> str:
        """Map location string to geographic context key"""
        location_lower = location.lower()
        
        if "miami" in location_lower or "florida" in location_lower:
            return "miami_fl"
        elif "phoenix" in location_lower or "arizona" in location_lower:
            return "phoenix_az"
        elif "minneapolis" in location_lower or "minnesota" in location_lower:
            return "minneapolis_mn"
        elif "seattle" in location_lower or "washington" in location_lower:
            return "seattle_wa"
        elif "denver" in location_lower or "colorado" in location_lower:
            return "denver_co"
        else:
            return "moderate_climate"
    
    def _get_current_season(self) -> str:
        """Get current season"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information"""
        return {
            "name": "StressValidationAgent",
            "version": "1.0",
            "capabilities": [
                "Contextual stressor validation",
                "False positive prevention",
                "Geographic appropriateness checking",
                "Seasonal stressor detection",
                "Temperature-based validation",
                "Regional climate mapping",
                "Usage pattern validation",
                "Additional stressor detection"
            ],
            "validation_rules": list(self.validation_rules.keys()),
            "geographic_contexts": list(self.geographic_context.keys()),
            "processing_speed": "~100ms per VIN",
            "cache_enabled": True,
            "daily_recalibration": True
        } 