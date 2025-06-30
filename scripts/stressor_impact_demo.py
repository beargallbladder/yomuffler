#!/usr/bin/env python3
"""
🎛️ STRESSOR IMPACT DEMO
Shows how outlier percentages change as you enable/disable stressors
Critical for understanding business impact of incremental deployment
"""

import json
import numpy as np
from collections import defaultdict

def stressor_impact_analysis():
    """Analyze how different stressor configurations affect outlier rates"""
    
    # Load the enhanced analysis data
    with open('enhanced_13_stressor_analysis_20250629_142715.json', 'r') as f:
        analysis_data = json.load(f)
    
    # Load VIN database for geographic data
    with open('vin_leads_database_20250626_154547.json', 'r') as f:
        vin_data = json.load(f)
    
    # Create VIN lookup
    vin_lookup = {v['vin']: v for v in vin_data}
    
    vehicles = analysis_data['vehicle_analyses']
    print(f"🔍 Analyzing impact of stressor configurations on {len(vehicles):,} vehicles")
    
    # Merge with geographic data
    merged_vehicles = []
    for vehicle in vehicles:
        vin = vehicle['vin']
        if vin in vin_lookup:
            geo_data = vin_lookup[vin]
            merged_vehicle = {
                **vehicle,
                'state': geo_data.get('state', 'XX'),
                'climate_zone': geo_data.get('climate_zone', 'unknown')
            }
            merged_vehicles.append(merged_vehicle)
    
    print(f"✅ Merged {len(merged_vehicles)} vehicles with geographic data")
    
    # Define different stressor configurations
    configurations = {
        "all_13_stressors": {
            "enabled": ["parasitic_draw_stress", "alternator_cycling_stress", "voltage_regulation_stress",
                       "deep_discharge_events", "vibration_stress", "extended_idle_exposure", 
                       "towing_load_stress", "stop_and_go_traffic", "extended_parking_stress",
                       "multi_driver_usage", "humidity_cycling_stress", "altitude_change_stress",
                       "salt_corrosion_exposure"],
            "description": "Full 13-stressor academic framework"
        },
        "basic_4_stressors": {
            "enabled": ["alternator_cycling_stress", "towing_load_stress", "multi_driver_usage", 
                       "salt_corrosion_exposure"],
            "description": "Basic deployment - easily detectable stressors"
        },
        "electrical_only": {
            "enabled": ["parasitic_draw_stress", "alternator_cycling_stress", "voltage_regulation_stress",
                       "deep_discharge_events"],
            "description": "Electrical stressors only"
        },
        "environmental_only": {
            "enabled": ["humidity_cycling_stress", "salt_corrosion_exposure"],
            "description": "Environmental stressors only (weather-based)"
        },
        "high_confidence_only": {
            "enabled": ["alternator_cycling_stress", "towing_load_stress", "multi_driver_usage",
                       "salt_corrosion_exposure", "humidity_cycling_stress"],
            "description": "High-confidence stressors with good data sources"
        }
    }
    
    print(f"\n🎛️ TESTING {len(configurations)} STRESSOR CONFIGURATIONS:")
    print("=" * 70)
    
    # Base likelihood ratios for recalculation
    stressor_lrs = {
        "parasitic_draw_stress": 3.4,
        "alternator_cycling_stress": 2.8,
        "voltage_regulation_stress": 4.1,
        "deep_discharge_events": 6.7,
        "vibration_stress": 2.1,
        "extended_idle_exposure": 1.9,
        "towing_load_stress": 3.2,
        "stop_and_go_traffic": 2.3,
        "extended_parking_stress": 1.7,
        "multi_driver_usage": 1.8,
        "humidity_cycling_stress": 2.6,
        "altitude_change_stress": 1.4,
        "salt_corrosion_exposure": 4.3
    }
    
    results = {}
    
    for config_name, config in configurations.items():
        print(f"\n📊 Configuration: {config_name.upper()}")
        print(f"    Description: {config['description']}")
        print(f"    Enabled stressors: {len(config['enabled'])}/13")
        
        # Recalculate risk scores with this configuration
        recalc_vehicles = []
        for vehicle in merged_vehicles:
            # Get active stressors for this vehicle that are also enabled in config
            vehicle_stressors = vehicle.get('active_stressors', [])
            enabled_active_stressors = [s for s in vehicle_stressors if s in config['enabled']]
            
            if enabled_active_stressors:
                # Recalculate combined likelihood ratio
                combined_lr = 1.0
                for stressor in enabled_active_stressors:
                    if stressor in stressor_lrs:
                        combined_lr *= stressor_lrs[stressor]
                
                # Recalculate posterior probability
                base_prior = vehicle.get('base_prior', 0.15)
                numerator = base_prior * combined_lr
                new_posterior = numerator / (numerator + (1 - base_prior))
                new_posterior = min(new_posterior, 0.95)  # Cap at 95%
            else:
                # No active stressors in this config
                new_posterior = vehicle.get('base_prior', 0.15)
            
            recalc_vehicle = {
                **vehicle,
                'recalc_posterior': new_posterior,
                'recalc_stressor_count': len(enabled_active_stressors),
                'enabled_stressors': enabled_active_stressors
            }
            recalc_vehicles.append(recalc_vehicle)
        
        # Find outliers with this configuration
        outliers = find_outliers_with_config(recalc_vehicles)
        
        # Calculate statistics
        total_vehicles = len(recalc_vehicles)
        outlier_count = len(outliers)
        outlier_percentage = (outlier_count / total_vehicles) * 100
        
        # Risk distribution analysis
        risk_scores = [v['recalc_posterior'] for v in recalc_vehicles]
        avg_risk = np.mean(risk_scores)
        max_risk = np.max(risk_scores)
        
        # Revenue calculation
        total_revenue = sum(calculate_revenue_from_risk(o['recalc_posterior'], o['model']) for o in outliers)
        
        results[config_name] = {
            'enabled_stressors': len(config['enabled']),
            'outlier_count': outlier_count,
            'outlier_percentage': outlier_percentage,
            'avg_risk_score': avg_risk,
            'max_risk_score': max_risk,
            'total_revenue': total_revenue,
            'avg_revenue_per_outlier': total_revenue / outlier_count if outlier_count > 0 else 0
        }
        
        print(f"    Results:")
        print(f"      • Outliers found: {outlier_count:,} ({outlier_percentage:.1f}%)")
        print(f"      • Avg risk score: {avg_risk:.3f}")
        print(f"      • Max risk score: {max_risk:.3f}")
        print(f"      • Total revenue: ${total_revenue:,}")
        if outlier_count > 0:
            print(f"      • Avg revenue/outlier: ${total_revenue // outlier_count:,}")
    
    # Comparison analysis
    print(f"\n🔍 CONFIGURATION COMPARISON:")
    print("=" * 70)
    print(f"{'Configuration':<20} {'Stressors':<10} {'Outliers':<10} {'%':<6} {'Avg Risk':<10} {'Revenue':<12}")
    print("-" * 70)
    
    for config_name, result in results.items():
        print(f"{config_name:<20} {result['enabled_stressors']:<10} {result['outlier_count']:<10} "
              f"{result['outlier_percentage']:<6.1f} {result['avg_risk_score']:<10.3f} ${result['total_revenue']:<11,}")
    
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"1. MORE STRESSORS ≠ MORE OUTLIERS necessarily")
    print(f"2. Configuration affects OUTLIER QUALITY and REVENUE")
    print(f"3. You can tune alerting rate by stressor selection")
    print(f"4. Some stressors contribute more to outlier detection than others")
    
    # Show impact on specific cohorts
    print(f"\n🌎 COHORT-SPECIFIC IMPACT (FL F-250 example):")
    fl_f250_vehicles = [v for v in merged_vehicles if v.get('state') == 'FL' and v.get('model') == 'F-250']
    if fl_f250_vehicles:
        print(f"    FL F-250 cohort: {len(fl_f250_vehicles)} vehicles")
        
        for config_name in ['basic_4_stressors', 'all_13_stressors']:
            config = configurations[config_name]
            cohort_outliers = 0
            
            for vehicle in fl_f250_vehicles:
                vehicle_stressors = vehicle.get('active_stressors', [])
                enabled_active = [s for s in vehicle_stressors if s in config['enabled']]
                
                if len(enabled_active) >= 2:  # Simple outlier criteria
                    cohort_outliers += 1
            
            print(f"    {config_name}: {cohort_outliers} outliers ({cohort_outliers/len(fl_f250_vehicles)*100:.1f}%)")

def find_outliers_with_config(vehicles):
    """Find outliers using recalculated risk scores"""
    # Create simple cohorts
    cohorts = defaultdict(list)
    for vehicle in vehicles:
        state = vehicle.get('state', 'XX')
        model = vehicle.get('model', 'unknown')
        cohort_key = f"{state}_{model}"
        cohorts[cohort_key].append(vehicle)
    
    # Filter cohorts with sufficient size
    large_cohorts = {k: v for k, v in cohorts.items() if len(v) >= 20}
    
    outliers = []
    for cohort_name, cohort_vehicles in large_cohorts.items():
        risks = [v['recalc_posterior'] for v in cohort_vehicles]
        risk_95th = np.percentile(risks, 95)
        
        for vehicle in cohort_vehicles:
            if vehicle['recalc_posterior'] >= risk_95th:
                outliers.append(vehicle)
    
    return outliers

def calculate_revenue_from_risk(risk_score, model):
    """Calculate revenue based on risk score and model"""
    if risk_score >= 0.25:
        base = 1400
    elif risk_score >= 0.20:
        base = 1200
    elif risk_score >= 0.15:
        base = 600
    elif risk_score >= 0.08:
        base = 350
    else:
        base = 180
    
    # Model multiplier
    if model in ["F-250", "F-350"]:
        base = int(base * 1.4)
    elif model == "F-150":
        base = int(base * 1.2)
    
    return base

if __name__ == "__main__":
    stressor_impact_analysis() 