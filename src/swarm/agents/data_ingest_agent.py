"""
📊 Data Ingestion Agent
Pulls VH telemetry, weather deltas, dealer distribution, sales density, trip logs, 
ignition cycles, and known stressors per VIN.
"""

import asyncio
import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
from .base_agent import BaseAgent


class DataIngestAgent(BaseAgent):
    """
    Specialized agent for ingesting and processing multi-source vehicle data
    """
    
    def __init__(self, redis_pool):
        super().__init__("data_ingest", redis_pool)
        
        # Data source configurations
        self.data_sources = {
            "vh_telemetry": {"weight": 0.3, "reliability": 0.95},
            "weather_data": {"weight": 0.2, "reliability": 0.92},
            "dealer_data": {"weight": 0.15, "reliability": 0.88},
            "trip_logs": {"weight": 0.2, "reliability": 0.90},
            "ignition_cycles": {"weight": 0.15, "reliability": 0.93}
        }
        
        # Stressor definitions from Ford's 13-stressor framework
        self.stressor_definitions = {
            "parasitic_draw": {"threshold": 50, "unit": "mA"},
            "alternator_cycling": {"threshold": 8, "unit": "cycles/day"},
            "voltage_regulation": {"threshold": 0.5, "unit": "V"},
            "deep_discharge": {"threshold": 11.5, "unit": "V"},
            "vibration_stress": {"threshold": 3, "unit": "G"},
            "extended_idle": {"threshold": 14, "unit": "days"},
            "towing_load": {"threshold": 80, "unit": "A"},
            "stop_go_traffic": {"threshold": 15, "unit": "starts/hour"},
            "extended_parking": {"threshold": 7, "unit": "days"},
            "multi_driver": {"threshold": 3, "unit": "drivers"},
            "humidity_cycling": {"threshold": 40, "unit": "%RH"},
            "altitude_change": {"threshold": 5000, "unit": "ft"},
            "salt_corrosion": {"threshold": 10, "unit": "miles_to_coast"}
        }
    
    async def process(self, task) -> Dict[str, Any]:
        """
        Process data ingestion for a VIN
        """
        start_time = datetime.utcnow()
        
        try:
            await self._log_agent_action("start_ingestion", task.task_id)
            
            vin = task.vin
            input_data = task.input_data
            
            # Check cache first
            cache_key = f"data_ingest:{vin}"
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                await self._log_agent_action("cache_hit", task.task_id)
                return cached_result
            
            # Ingest data from multiple sources
            ingestion_results = await asyncio.gather(
                self._ingest_vh_telemetry(vin, input_data),
                self._ingest_weather_data(vin, input_data),
                self._ingest_dealer_data(vin, input_data),
                self._ingest_trip_logs(vin, input_data),
                self._ingest_ignition_cycles(vin, input_data),
                return_exceptions=True
            )
            
            # Combine results
            combined_data = {}
            source_quality = {}
            
            for i, result in enumerate(ingestion_results):
                source_name = list(self.data_sources.keys())[i]
                
                if isinstance(result, Exception):
                    self.logger.warning(f"Failed to ingest {source_name}: {str(result)}")
                    source_quality[source_name] = 0.0
                else:
                    combined_data.update(result)
                    source_quality[source_name] = result.get("quality_score", 0.8)
            
            # Detect active stressors
            active_stressors = self._detect_active_stressors(combined_data)
            
            # Calculate data quality score
            overall_quality = self._calculate_data_quality(source_quality)
            
            # Prepare result
            result = {
                "vin": vin,
                "ingestion_timestamp": datetime.utcnow().isoformat(),
                "data_sources": list(source_quality.keys()),
                "data_quality_score": overall_quality,
                "source_quality": source_quality,
                "vehicle_data": combined_data,
                "active_stressors": active_stressors,
                "raw_stressor_values": self._extract_stressor_values(combined_data),
                "data_completeness": len(combined_data) / 20  # Expect ~20 data points
            }
            
            # Cache result
            await self._cache_result(cache_key, result, ttl=3600)  # 1 hour
            
            # Store debug info
            debug_info = {
                "ingestion_sources": len(source_quality),
                "quality_scores": source_quality,
                "stressor_count": len(active_stressors),
                "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }
            await self._store_debug_info(task.task_id, debug_info)
            
            await self._log_agent_action("ingestion_complete", task.task_id, 
                                       {"quality_score": overall_quality})
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Data ingestion failed for VIN {task.vin}: {str(e)}")
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, False)
            
            return {
                "error": str(e),
                "vin": task.vin,
                "data_quality_score": 0.0,
                "active_stressors": [],
                "vehicle_data": {}
            }
    
    async def _ingest_vh_telemetry(self, vin: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest VH/Telemetry data"""
        # Simulate VH telemetry ingestion
        base_mileage = input_data.get("miles", 45000)
        vehicle_age = self._estimate_vehicle_age(vin)
        
        # Simulate realistic telemetry data
        telemetry_data = {
            "soc_current": random.uniform(0.6, 1.0),
            "soc_30_day_avg": random.uniform(0.65, 0.95),
            "voltage_avg": random.uniform(12.2, 14.4),
            "voltage_variance": random.uniform(0.1, 0.8),
            "parasitic_draw_ma": random.uniform(20, 120),
            "alternator_cycles_daily": random.uniform(3, 25),
            "quality_score": 0.92
        }
        
        # Add age-based degradation
        if vehicle_age > 5:
            telemetry_data["soc_current"] *= 0.9
            telemetry_data["voltage_avg"] -= 0.3
            telemetry_data["parasitic_draw_ma"] *= 1.2
        
        return telemetry_data
    
    async def _ingest_weather_data(self, vin: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest weather and climate data"""
        location = input_data.get("location", "moderate")
        
        # Simulate weather data based on location
        weather_patterns = {
            "southeast": {"temp_avg": 78, "temp_variance": 25, "humidity_avg": 65},
            "northeast": {"temp_avg": 58, "temp_variance": 35, "humidity_avg": 55},
            "southwest": {"temp_avg": 85, "temp_variance": 20, "humidity_avg": 35},
            "midwest": {"temp_avg": 62, "temp_variance": 40, "humidity_avg": 60},
            "moderate": {"temp_avg": 68, "temp_variance": 25, "humidity_avg": 50}
        }
        
        pattern = weather_patterns.get(location, weather_patterns["moderate"])
        
        weather_data = {
            "temp_avg_30day": pattern["temp_avg"] + random.uniform(-10, 10),
            "temp_variance_30day": pattern["temp_variance"] + random.uniform(-5, 5),
            "humidity_avg": pattern["humidity_avg"] + random.uniform(-15, 15),
            "humidity_variance": random.uniform(20, 60),
            "coastal_distance_miles": random.uniform(5, 500),
            "altitude_feet": random.uniform(0, 8000),
            "quality_score": 0.89
        }
        
        return weather_data
    
    async def _ingest_dealer_data(self, vin: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest dealer and service data"""
        # Simulate dealer data
        dealer_data = {
            "last_service_days": random.randint(30, 400),
            "service_compliance_score": random.uniform(0.3, 1.0),
            "dealer_density_score": random.uniform(0.2, 0.9),
            "avg_service_interval_days": random.randint(90, 300),
            "total_service_visits": random.randint(0, 15),
            "quality_score": 0.85
        }
        
        return dealer_data
    
    async def _ingest_trip_logs(self, vin: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest trip pattern and usage data"""
        base_mileage = input_data.get("miles", 45000)
        
        # Simulate trip patterns
        trip_data = {
            "avg_trip_distance_miles": random.uniform(2, 50),
            "trips_per_day": random.uniform(1, 12),
            "short_trips_percent": random.uniform(0.2, 0.8),
            "highway_percent": random.uniform(0.1, 0.7),
            "idle_time_percent": random.uniform(0.05, 0.4),
            "stop_start_events_hour": random.uniform(5, 25),
            "quality_score": 0.91
        }
        
        return trip_data
    
    async def _ingest_ignition_cycles(self, vin: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest ignition cycle and electrical data"""
        # Simulate ignition cycle data
        ignition_data = {
            "ignition_cycles_daily": random.uniform(2, 20),
            "cold_start_percent": random.uniform(0.2, 0.8),
            "deep_discharge_events": random.randint(0, 5),
            "extended_idle_days": random.randint(0, 30),
            "multi_driver_keys": random.randint(1, 5),
            "towing_load_detected": random.choice([True, False]),
            "quality_score": 0.94
        }
        
        return ignition_data
    
    def _detect_active_stressors(self, data: Dict[str, Any]) -> List[str]:
        """Detect which stressors are active based on ingested data"""
        active_stressors = []
        
        # Check each stressor
        if data.get("parasitic_draw_ma", 0) > self.stressor_definitions["parasitic_draw"]["threshold"]:
            active_stressors.append("parasitic_draw")
        
        if data.get("alternator_cycles_daily", 0) > self.stressor_definitions["alternator_cycling"]["threshold"]:
            active_stressors.append("alternator_cycling")
        
        if data.get("voltage_variance", 0) > self.stressor_definitions["voltage_regulation"]["threshold"]:
            active_stressors.append("voltage_regulation")
        
        if data.get("voltage_avg", 13) < self.stressor_definitions["deep_discharge"]["threshold"]:
            active_stressors.append("deep_discharge")
        
        if data.get("stop_start_events_hour", 0) > self.stressor_definitions["stop_go_traffic"]["threshold"]:
            active_stressors.append("stop_go_traffic")
        
        if data.get("extended_idle_days", 0) > self.stressor_definitions["extended_parking"]["threshold"]:
            active_stressors.append("extended_parking")
        
        if data.get("multi_driver_keys", 1) > self.stressor_definitions["multi_driver"]["threshold"]:
            active_stressors.append("multi_driver")
        
        if data.get("humidity_variance", 0) > self.stressor_definitions["humidity_cycling"]["threshold"]:
            active_stressors.append("humidity_cycling")
        
        if data.get("altitude_feet", 0) > self.stressor_definitions["altitude_change"]["threshold"]:
            active_stressors.append("altitude_change")
        
        if data.get("coastal_distance_miles", 100) < self.stressor_definitions["salt_corrosion"]["threshold"]:
            active_stressors.append("salt_corrosion")
        
        return active_stressors
    
    def _extract_stressor_values(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract raw stressor values for analysis"""
        return {
            "parasitic_draw_ma": data.get("parasitic_draw_ma", 0),
            "alternator_cycles_daily": data.get("alternator_cycles_daily", 0),
            "voltage_variance": data.get("voltage_variance", 0),
            "voltage_avg": data.get("voltage_avg", 13),
            "stop_start_events_hour": data.get("stop_start_events_hour", 0),
            "extended_idle_days": data.get("extended_idle_days", 0),
            "multi_driver_keys": data.get("multi_driver_keys", 1),
            "humidity_variance": data.get("humidity_variance", 0),
            "altitude_feet": data.get("altitude_feet", 0),
            "coastal_distance_miles": data.get("coastal_distance_miles", 100),
            "temp_variance_30day": data.get("temp_variance_30day", 25),
            "service_compliance_score": data.get("service_compliance_score", 0.8)
        }
    
    def _calculate_data_quality(self, source_quality: Dict[str, float]) -> float:
        """Calculate overall data quality score"""
        if not source_quality:
            return 0.0
        
        # Weighted average based on source reliability
        total_weight = 0
        weighted_sum = 0
        
        for source, quality in source_quality.items():
            if source in self.data_sources:
                weight = self.data_sources[source]["weight"]
                weighted_sum += quality * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _estimate_vehicle_age(self, vin: str) -> int:
        """Estimate vehicle age from VIN (simplified)"""
        try:
            # Simple heuristic: use VIN characters to estimate age
            year_char = vin[9] if len(vin) >= 10 else 'M'
            year_map = {
                'L': 2020, 'M': 2021, 'N': 2022, 'P': 2023, 'R': 2024, 'S': 2025
            }
            year = year_map.get(year_char, 2022)
            return max(0, 2024 - year)
        except:
            return 3  # Default to 3 years
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Return agent information"""
        return {
            "name": "DataIngestAgent",
            "version": "1.0",
            "capabilities": [
                "VH/Telemetry data ingestion",
                "Weather data correlation",
                "Dealer service data integration",
                "Trip pattern analysis",
                "Ignition cycle monitoring",
                "Multi-source data fusion",
                "Real-time stressor detection"
            ],
            "data_sources": list(self.data_sources.keys()),
            "stressor_definitions": self.stressor_definitions,
            "processing_speed": "~200ms per VIN",
            "cache_enabled": True,
            "quality_validation": True
        } 