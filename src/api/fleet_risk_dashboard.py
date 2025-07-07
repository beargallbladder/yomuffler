"""
Ford Pro Fleet Risk Intelligence Dashboard API
Real-time behavioral stressor analysis with weather data source controls
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
from dataclasses import dataclass
from decimal import Decimal

import os

# Get the directory containing this file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to get to the project root
project_root = os.path.dirname(os.path.dirname(current_dir))
template_dir = os.path.join(project_root, 'templates')

app = Flask(__name__, template_folder=template_dir)
CORS(app)

@dataclass
class FleetVehicle:
    vin: str
    make: str
    model: str
    year: int
    location: Dict[str, str]  # city, state, zip
    trip_data: Dict[str, float]
    maintenance_data: Dict[str, Any]
    cohort: str

@dataclass
class StressorConfig:
    name: str
    enabled: bool
    likelihood_ratio: float
    definition: str
    source: str

class FleetRiskEngine:
    """
    Fleet Risk Intelligence Engine with Interactive Stressor Controls
    """
    
    def __init__(self):
        self.stressor_configs = {
            "short_trip_behavior": StressorConfig(
                name="Short Trip Behavior",
                enabled=True,
                likelihood_ratio=2.0,
                definition="Average trip <1-2 miles - chronic undercharging",
                source="MDPI 2021 - 1,454 battery study shows 2x failure rate"
            ),
            "temp_extreme_hot": StressorConfig(
                name="Temperature Extreme Hot",
                enabled=True,
                likelihood_ratio=1.8,
                definition="Average temperature >90°F - accelerated chemical reactions",
                source="BCI Survey - Hot climates show 20% shorter battery life"
            ),
            "ignition_cycles_high": StressorConfig(
                name="Ignition Cycles High", 
                enabled=True,
                likelihood_ratio=2.3,
                definition="≥40 starts/30 days with insufficient recharge",
                source="Argonne National Lab - High cycle validation"
            ),
            "cold_extreme": StressorConfig(
                name="Cold Extreme",
                enabled=False,
                likelihood_ratio=1.2,
                definition="Average temperature <20°F - reduced capacity",
                source="BCI Survey - Cold reduces capacity 35% at 0°C"
            ),
            "commercial_duty_cycle": StressorConfig(
                name="Commercial Duty Cycle",
                enabled=True,
                likelihood_ratio=1.4,
                definition="Commercial stop-start with heavy accessory loads",
                source="Idaho National Lab - Commercial vehicle analysis"
            ),
            "maintenance_deferred": StressorConfig(
                name="Maintenance Deferred",
                enabled=True,
                likelihood_ratio=2.1,
                definition="Maintenance intervals exceeded by >20%",
                source="University of Stuttgart - Maintenance correlation"
            ),
            "temp_delta_high": StressorConfig(
                name="Temperature Cycling",
                enabled=False,
                likelihood_ratio=2.0,
                definition="Daily temperature swings ≥30°F",
                source="MDPI 2021 - Thermal cycling analysis"
            )
        }
        
        # Weather data source controls
        self.weather_config = {
            "use_live_weather": True,
            "use_historical_weather": False,
            "historical_months": 3,
            "live_api_key": "demo_key"
        }
        
        # Cohort priors from academic sources
        self.cohort_priors = {
            "lighttruck_commercial": 0.18,  # Commercial F-150s
            "midweighttruck_commercial": 0.22,  # Commercial Transit/Super Duty
            "suv_commercial": 0.20,  # Commercial Explorer/Expedition
            "van_commercial": 0.25  # Commercial Transit Connect
        }
        
    def generate_mock_fleet(self, fleet_size: int = 1000) -> List[FleetVehicle]:
        """Generate realistic commercial fleet data for demo"""
        fleet = []
        
        # Commercial vehicle types
        vehicle_types = [
            {"make": "Ford", "model": "F-150", "cohort": "lighttruck_commercial", "weight": 40},
            {"make": "Ford", "model": "Transit", "cohort": "midweighttruck_commercial", "weight": 25},
            {"make": "Ford", "model": "F-250", "cohort": "midweighttruck_commercial", "weight": 15},
            {"make": "Ford", "model": "Explorer", "cohort": "suv_commercial", "weight": 10},
            {"make": "Ford", "model": "Transit Connect", "cohort": "van_commercial", "weight": 10}
        ]
        
        # Commercial hotspots
        locations = [
            {"city": "Miami", "state": "FL", "zip": "33101", "climate": "hot", "weight": 20},
            {"city": "Phoenix", "state": "AZ", "zip": "85001", "climate": "extreme_hot", "weight": 15},
            {"city": "Dallas", "state": "TX", "zip": "75201", "climate": "hot", "weight": 15},
            {"city": "Houston", "state": "TX", "zip": "77001", "climate": "hot_humid", "weight": 12},
            {"city": "Atlanta", "state": "GA", "zip": "30301", "climate": "moderate", "weight": 10},
            {"city": "Las Vegas", "state": "NV", "zip": "89101", "climate": "extreme_hot", "weight": 8},
            {"city": "Tampa", "state": "FL", "zip": "33601", "climate": "hot_humid", "weight": 8},
            {"city": "Austin", "state": "TX", "zip": "73301", "climate": "hot", "weight": 7},
            {"city": "San Antonio", "state": "TX", "zip": "78201", "climate": "hot", "weight": 5}
        ]
        
        for i in range(fleet_size):
            # Select vehicle type based on weights
            vehicle_type = self._weighted_choice(vehicle_types)
            location = self._weighted_choice(locations)
            
            # Generate realistic VIN
            vin = f"1FT{random.choice(['FW', 'BW', 'NX'])}{random.randint(10000, 99999):05d}"
            
            # Generate usage patterns based on commercial reality
            if "hot" in location["climate"]:
                avg_temp = random.uniform(85, 105)
                temp_stress_multiplier = 1.5
            else:
                avg_temp = random.uniform(70, 85)
                temp_stress_multiplier = 1.0
                
            # Commercial vehicles do more short trips
            total_trips = random.randint(45, 120)
            short_trip_ratio = random.uniform(0.4, 0.8)  # 40-80% short trips
            avg_trip_distance = random.uniform(0.8, 3.5)
            
            # Maintenance patterns for commercial fleets
            days_since_service = random.randint(30, 300)
            scheduled_interval = 120  # 4 months for commercial
            maintenance_overdue = days_since_service > scheduled_interval
            
            vehicle = FleetVehicle(
                vin=vin,
                make=vehicle_type["make"],
                model=vehicle_type["model"],
                year=random.randint(2019, 2024),
                location=location,
                trip_data={
                    "total_trips": total_trips,
                    "avg_trip_distance": avg_trip_distance,
                    "short_trips_under_2_miles": int(total_trips * short_trip_ratio),
                    "ignition_cycles": int(total_trips * random.uniform(0.7, 1.3)),
                    "avg_temp": avg_temp,
                    "temp_delta": random.uniform(15, 35)
                },
                maintenance_data={
                    "days_since_service": days_since_service,
                    "scheduled_interval": scheduled_interval,
                    "overdue": maintenance_overdue,
                    "compliance": "deferred" if maintenance_overdue else "compliant"
                },
                cohort=vehicle_type["cohort"]
            )
            
            fleet.append(vehicle)
            
        return fleet
    
    def _weighted_choice(self, choices: List[Dict]) -> Dict:
        """Select item based on weight"""
        total_weight = sum(choice["weight"] for choice in choices)
        r = random.uniform(0, total_weight)
        upto = 0
        for choice in choices:
            if upto + choice["weight"] >= r:
                return choice
            upto += choice["weight"]
        return choices[-1]
    
    def analyze_vehicle_stressors(self, vehicle: FleetVehicle, enabled_stressors: Dict[str, bool]) -> Dict:
        """Analyze individual vehicle against enabled stressors"""
        active_stressors = []
        likelihood_ratios = []
        stressor_details = []
        
        # Short trip analysis
        if enabled_stressors.get("short_trip_behavior", False):
            short_trip_ratio = vehicle.trip_data["short_trips_under_2_miles"] / vehicle.trip_data["total_trips"]
            if short_trip_ratio > 0.6:  # >60% short trips
                active_stressors.append("short_trip_behavior")
                likelihood_ratios.append(self.stressor_configs["short_trip_behavior"].likelihood_ratio)
                stressor_details.append(f"{short_trip_ratio:.1%} short trips (<2 miles)")
        
        # Temperature analysis
        if enabled_stressors.get("temp_extreme_hot", False):
            if vehicle.trip_data["avg_temp"] > 90:
                active_stressors.append("temp_extreme_hot") 
                likelihood_ratios.append(self.stressor_configs["temp_extreme_hot"].likelihood_ratio)
                stressor_details.append(f"Hot climate: {vehicle.trip_data['avg_temp']:.1f}°F avg")
                
        if enabled_stressors.get("cold_extreme", False):
            if vehicle.trip_data["avg_temp"] < 30:
                active_stressors.append("cold_extreme")
                likelihood_ratios.append(self.stressor_configs["cold_extreme"].likelihood_ratio)
                stressor_details.append(f"Cold climate: {vehicle.trip_data['avg_temp']:.1f}°F avg")
        
        # Ignition cycle analysis  
        if enabled_stressors.get("ignition_cycles_high", False):
            cycles_per_day = vehicle.trip_data["ignition_cycles"] / 30
            if cycles_per_day > 1.3:  # >40 cycles per month
                active_stressors.append("ignition_cycles_high")
                likelihood_ratios.append(self.stressor_configs["ignition_cycles_high"].likelihood_ratio)
                stressor_details.append(f"High ignition cycles: {cycles_per_day:.1f}/day")
        
        # Commercial duty cycle
        if enabled_stressors.get("commercial_duty_cycle", False):
            if vehicle.trip_data["total_trips"] > 60:  # High commercial usage
                active_stressors.append("commercial_duty_cycle")
                likelihood_ratios.append(self.stressor_configs["commercial_duty_cycle"].likelihood_ratio)
                stressor_details.append(f"Heavy commercial use: {vehicle.trip_data['total_trips']} trips/month")
        
        # Maintenance deferred
        if enabled_stressors.get("maintenance_deferred", False):
            if vehicle.maintenance_data["overdue"]:
                active_stressors.append("maintenance_deferred")
                likelihood_ratios.append(self.stressor_configs["maintenance_deferred"].likelihood_ratio)
                days_overdue = vehicle.maintenance_data["days_since_service"] - vehicle.maintenance_data["scheduled_interval"]
                stressor_details.append(f"Maintenance overdue: {days_overdue} days")
        
        # Temperature cycling
        if enabled_stressors.get("temp_delta_high", False):
            if vehicle.trip_data["temp_delta"] > 30:
                active_stressors.append("temp_delta_high")
                likelihood_ratios.append(self.stressor_configs["temp_delta_high"].likelihood_ratio)
                stressor_details.append(f"High temp cycling: {vehicle.trip_data['temp_delta']:.1f}°F delta")
        
        # Calculate combined likelihood ratio
        combined_lr = 1.0
        for lr in likelihood_ratios:
            combined_lr *= lr
            
        return {
            "active_stressors": active_stressors,
            "likelihood_ratios": likelihood_ratios,
            "combined_lr": combined_lr,
            "stressor_details": stressor_details
        }
    
    def calculate_fleet_risk(self, fleet: List[FleetVehicle], enabled_stressors: Dict[str, bool]) -> Dict:
        """Calculate risk for entire fleet with current stressor configuration"""
        
        risk_categories = {
            "severe": [],      # ≥25%
            "critical": [],    # 20-25%  
            "high": [],        # 15-20%
            "moderate": [],    # 8-15%
            "low": []          # <8%
        }
        
        total_revenue_opportunity = 0
        
        for vehicle in fleet:
            # Get cohort prior
            prior = self.cohort_priors.get(vehicle.cohort, 0.15)
            
            # Analyze stressors
            stressor_analysis = self.analyze_vehicle_stressors(vehicle, enabled_stressors)
            
            # Bayesian calculation
            if stressor_analysis["combined_lr"] > 1.0:
                prior_odds = prior / (1 - prior + 1e-10)
                posterior_odds = prior_odds * stressor_analysis["combined_lr"]
                risk_score = posterior_odds / (1 + posterior_odds)
            else:
                risk_score = prior
                
            # Ensure bounds
            risk_score = max(0.01, min(0.99, risk_score))
            
            # Calculate revenue opportunity
            revenue = self._calculate_revenue_opportunity(risk_score, vehicle)
            total_revenue_opportunity += revenue
            
            # Categorize risk
            vehicle_risk = {
                "vehicle": vehicle,
                "risk_score": risk_score,
                "revenue_opportunity": revenue,
                "stressor_analysis": stressor_analysis,
                "dealer_message": self._generate_dealer_message(vehicle, stressor_analysis)
            }
            
            if risk_score >= 0.25:
                risk_categories["severe"].append(vehicle_risk)
            elif risk_score >= 0.20:
                risk_categories["critical"].append(vehicle_risk)
            elif risk_score >= 0.15:
                risk_categories["high"].append(vehicle_risk)
            elif risk_score >= 0.08:
                risk_categories["moderate"].append(vehicle_risk)
            else:
                risk_categories["low"].append(vehicle_risk)
        
        # Sort each category by risk score (highest first)
        for category in risk_categories.values():
            category.sort(key=lambda x: x["risk_score"], reverse=True)
            
        return {
            "risk_categories": risk_categories,
            "total_revenue_opportunity": total_revenue_opportunity,
            "fleet_size": len(fleet),
            "high_risk_count": len(risk_categories["severe"]) + len(risk_categories["critical"]),
            "enabled_stressors": enabled_stressors
        }
    
    def _calculate_revenue_opportunity(self, risk_score: float, vehicle: FleetVehicle) -> float:
        """Calculate revenue opportunity based on risk score and vehicle type"""
        
        # Base revenue by risk level
        if risk_score >= 0.25:
            base_revenue = 1400
        elif risk_score >= 0.20:
            base_revenue = 1200
        elif risk_score >= 0.15:
            base_revenue = 800
        elif risk_score >= 0.08:
            base_revenue = 450
        else:
            base_revenue = 200
            
        # Commercial multiplier
        if "commercial" in vehicle.cohort:
            base_revenue *= 1.6
            
        # Vehicle type multiplier
        if vehicle.model in ["F-250", "F-350", "Super Duty"]:
            base_revenue *= 1.3
        elif vehicle.model == "Transit":
            base_revenue *= 1.2
            
        return base_revenue
    
    def _generate_dealer_message(self, vehicle: FleetVehicle, stressor_analysis: Dict) -> str:
        """Generate dealer-ready engagement message"""
        
        if not stressor_analysis["active_stressors"]:
            return f"Your {vehicle.model} shows normal wear patterns. Routine maintenance schedule recommended."
            
        # Primary stressor
        primary = stressor_analysis["active_stressors"][0]
        stressor_config = self.stressor_configs[primary]
        
        # Location context
        location_str = f"{vehicle.location['city']}, {vehicle.location['state']}"
        
        # Build message
        if primary == "short_trip_behavior":
            message = f"Your {vehicle.model} in {location_str} shows extensive short-trip usage. "
            message += "Short trips prevent full battery recharge, causing 2x normal wear. "
        elif primary == "temp_extreme_hot":
            message = f"Your {vehicle.model} operates in hot climate ({location_str}). "
            message += "Hot weather reduces battery life by 20% through accelerated chemical reactions. "
        elif primary == "maintenance_deferred":
            days_overdue = vehicle.maintenance_data["days_since_service"] - vehicle.maintenance_data["scheduled_interval"]
            message = f"Your {vehicle.model} maintenance is {days_overdue} days overdue. "
            message += "Deferred maintenance significantly increases component failure risk. "
        else:
            message = f"Your {vehicle.model} shows {len(stressor_analysis['active_stressors'])} stress patterns. "
            
        # Add scientific backing
        message += f"This assessment is based on {stressor_config.source}. "
        
        # Call to action
        message += "Consider scheduling preventive maintenance to avoid unexpected failures."
        
        return message

# Initialize global fleet engine
fleet_engine = FleetRiskEngine()
demo_fleet = fleet_engine.generate_mock_fleet(1000)

@app.route('/api/v1/stressor-configs', methods=['GET'])
def get_stressor_configs():
    """Get available stressor configurations"""
    configs = {}
    for key, config in fleet_engine.stressor_configs.items():
        configs[key] = {
            "name": config.name,
            "enabled": config.enabled,
            "likelihood_ratio": config.likelihood_ratio,
            "definition": config.definition,
            "source": config.source
        }
    return jsonify(configs)

@app.route('/api/v1/weather-config', methods=['GET'])
def get_weather_config():
    """Get weather data source configuration"""
    return jsonify(fleet_engine.weather_config)

@app.route('/api/v1/weather-config', methods=['POST'])
def update_weather_config():
    """Update weather data source configuration"""
    config = request.json
    fleet_engine.weather_config.update(config)
    return jsonify({"status": "updated", "config": fleet_engine.weather_config})

@app.route('/api/v1/fleet-risk', methods=['POST'])
def calculate_fleet_risk():
    """Calculate fleet risk with selected stressors"""
    
    enabled_stressors = request.json.get('enabled_stressors', {})
    
    # Update stressor configs
    for key, enabled in enabled_stressors.items():
        if key in fleet_engine.stressor_configs:
            fleet_engine.stressor_configs[key].enabled = enabled
    
    # Calculate fleet risk
    risk_analysis = fleet_engine.calculate_fleet_risk(demo_fleet, enabled_stressors)
    
    # Format response for dashboard
    response = {
        "risk_summary": {
            "severe": len(risk_analysis["risk_categories"]["severe"]),
            "critical": len(risk_analysis["risk_categories"]["critical"]),
            "high": len(risk_analysis["risk_categories"]["high"]), 
            "moderate": len(risk_analysis["risk_categories"]["moderate"]),
            "low": len(risk_analysis["risk_categories"]["low"])
        },
        "total_revenue_opportunity": f"${risk_analysis['total_revenue_opportunity']:,.0f}",
        "fleet_size": risk_analysis["fleet_size"],
        "high_risk_count": risk_analysis["high_risk_count"],
        "top_risk_vehicles": []
    }
    
    # Get top 10 highest risk vehicles
    all_high_risk = (risk_analysis["risk_categories"]["severe"] + 
                     risk_analysis["risk_categories"]["critical"])
    
    for vehicle_risk in all_high_risk[:10]:
        vehicle = vehicle_risk["vehicle"]
        response["top_risk_vehicles"].append({
            "vin": vehicle.vin,
            "model": vehicle.model,
            "location": f"{vehicle.location['city']}, {vehicle.location['state']}",
            "risk_score": f"{vehicle_risk['risk_score']:.1%}",
            "revenue_opportunity": f"${vehicle_risk['revenue_opportunity']:,.0f}",
            "primary_stressors": vehicle_risk["stressor_analysis"]["active_stressors"][:2],
            "dealer_message": vehicle_risk["dealer_message"]
        })
    
    return jsonify(response)

@app.route('/api/v1/fleet-details/<risk_level>', methods=['GET'])
def get_fleet_details(risk_level):
    """Get detailed vehicle list for specific risk level"""
    
    # Use last calculated risk analysis
    enabled_stressors = {key: config.enabled for key, config in fleet_engine.stressor_configs.items()}
    risk_analysis = fleet_engine.calculate_fleet_risk(demo_fleet, enabled_stressors)
    
    if risk_level not in risk_analysis["risk_categories"]:
        return jsonify({"error": "Invalid risk level"}), 400
        
    vehicles = risk_analysis["risk_categories"][risk_level]
    
    response = {
        "risk_level": risk_level,
        "count": len(vehicles),
        "vehicles": []
    }
    
    for vehicle_risk in vehicles:
        vehicle = vehicle_risk["vehicle"]
        response["vehicles"].append({
            "vin": vehicle.vin,
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "location": vehicle.location,
            "risk_score": vehicle_risk["risk_score"],
            "revenue_opportunity": vehicle_risk["revenue_opportunity"],
            "active_stressors": vehicle_risk["stressor_analysis"]["active_stressors"],
            "stressor_details": vehicle_risk["stressor_analysis"]["stressor_details"],
            "dealer_message": vehicle_risk["dealer_message"],
            "maintenance_status": vehicle.maintenance_data
        })
    
    return jsonify(response)

@app.route('/dashboard')
def dashboard():
    """Serve the Fleet Risk Intelligence Dashboard"""
    return render_template('fleet_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 