#!/usr/bin/env python3
"""
🎯 QUICK COHORT OUTLIER DEMO
Shows how Bayesian scores enable meaningful sorting
"""

import json
import numpy as np
from collections import defaultdict

def quick_outlier_demo():
    # Load the enhanced analysis
    with open('enhanced_13_stressor_analysis_20250629_142715.json', 'r') as f:
        analysis_data = json.load(f)
    
    # Load the original VIN database with geographic data (use the matching file)
    with open('vin_leads_database_20250626_154547.json', 'r') as f:
        vin_data = json.load(f)
    
    # Create lookup for VIN to geographic data
    vin_lookup = {v['vin']: v for v in vin_data}
    
    vehicles = analysis_data['vehicle_analyses']
    print(f"🔍 Analyzing {len(vehicles)} vehicles for cohort outliers")
    
    # Merge analysis with geographic data
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
    
    # Create simple cohorts
    cohorts = defaultdict(list)
    for vehicle in merged_vehicles:
        state = vehicle.get('state', 'XX')
        model = vehicle.get('model', 'unknown')
        cohort_key = f"{state}_{model}"
        cohorts[cohort_key].append(vehicle)
    
    # Filter cohorts with at least 20 vehicles
    large_cohorts = {k: v for k, v in cohorts.items() if len(v) >= 20}
    print(f"📊 Created {len(large_cohorts)} cohorts with 20+ vehicles each")
    
    # Show cohort details
    print(f"\n📈 COHORT BREAKDOWN:")
    for cohort_name, cohort_vehicles in large_cohorts.items():
        risks = [v['posterior_probability'] for v in cohort_vehicles]
        print(f"  {cohort_name}: {len(cohort_vehicles)} vehicles, avg risk: {np.mean(risks):.3f}")
    
    # Analyze outliers
    all_outliers = []
    
    for cohort_name, cohort_vehicles in large_cohorts.items():
        risks = [v['posterior_probability'] for v in cohort_vehicles]
        risk_95th = np.percentile(risks, 95)
        risk_mean = np.mean(risks)
        
        # Find outliers (95th percentile)
        for vehicle in cohort_vehicles:
            if vehicle['posterior_probability'] >= risk_95th:
                outlier_info = {
                    'vin': vehicle['vin'],
                    'model': vehicle['model'], 
                    'state': vehicle['state'],
                    'climate_zone': vehicle['climate_zone'],
                    'risk_score': vehicle['posterior_probability'],
                    'cohort_mean': risk_mean,
                    'vs_cohort': vehicle['posterior_probability'] - risk_mean,
                    'percentile': 95,
                    'cohort': cohort_name,
                    'stressors': len(vehicle['active_stressors']),
                    'revenue': vehicle['revenue_opportunity'],
                    'stressor_details': vehicle.get('stressor_details', [])
                }
                all_outliers.append(outlier_info)
    
    # Sort by deviation from cohort
    all_outliers.sort(key=lambda x: x['vs_cohort'], reverse=True)
    
    print(f"\n🎯 COHORT-RELATIVE OUTLIERS FOUND: {len(all_outliers)}")
    print(f"📊 Outlier percentage: {len(all_outliers)/len(merged_vehicles)*100:.1f}% (much more reasonable!)")
    print(f"💰 Total outlier revenue: ${sum(o['revenue'] for o in all_outliers):,}")
    
    print(f"\n🔥 TOP 10 OUTLIERS (Biggest deviation from their cohort):")
    for i, outlier in enumerate(all_outliers[:10]):
        print(f"{i+1:2d}. VIN: {outlier['vin'][:8]}... | {outlier['model']} | {outlier['state']} | {outlier['climate_zone']}")
        print(f"    Risk: {outlier['risk_score']:.3f} vs cohort avg {outlier['cohort_mean']:.3f}")
        print(f"    Deviation: +{outlier['vs_cohort']:.3f} ({outlier['stressors']} stressors)")
        print(f"    Revenue: ${outlier['revenue']:,}")
        if outlier['stressor_details']:
            print(f"    Stressors: {', '.join(outlier['stressor_details'][:2])}")
        print()
    
    # Show normal vehicles for comparison
    print(f"✅ NORMAL EXAMPLES (Within cohort range):")
    normal_count = 0
    for cohort_name, cohort_vehicles in large_cohorts.items():
        if normal_count >= 3:
            break
        risks = [v['posterior_probability'] for v in cohort_vehicles]
        risk_mean = np.mean(risks)
        
        for vehicle in cohort_vehicles:
            if abs(vehicle['posterior_probability'] - risk_mean) < 0.05:
                print(f"   VIN: {vehicle['vin'][:8]}... | {vehicle['model']} | {vehicle['state']}")
                print(f"    Risk: {vehicle['posterior_probability']:.3f} (normal for {cohort_name})")
                normal_count += 1
                break
    
    print(f"\n🎯 THE BUSINESS INSIGHT:")
    print(f"❌ OLD WAY: Alert on {analysis_data['summary']['severe_risk_vins']} 'high risk' vehicles (73%) - USELESS")
    print(f"✅ NEW WAY: Alert on {len(all_outliers)} cohort outliers ({len(all_outliers)/len(merged_vehicles)*100:.1f}%) - ACTIONABLE!")
    print(f"\n🚀 THIS IS WHY BAYESIAN SCORES ENABLE THE SORT:")
    print(f"   • Every vehicle gets a precise probability score (0.000 to 1.000)")
    print(f"   • We can rank vehicles WITHIN their cohort")
    print(f"   • Only the TRUE OUTLIERS get dealer attention")
    print(f"   • Salt corrosion in Florida = normal")
    print(f"   • Salt corrosion in Michigan = OUTLIER!")

if __name__ == "__main__":
    quick_outlier_demo() 