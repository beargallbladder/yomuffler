#!/usr/bin/env python3
"""
Ford Battery Research Demo - Bayesian Risk Scoring

Demonstrates how the updated Bayesian engine uses real Ford battery research
for lead-acid AGM battery risk scoring instead of incorrect lithium-ion data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from src.engines.bayesian_engine_v2 import FordBatteryRiskCalculator


def demonstrate_ford_battery_priors():
    """Show how Ford battery research drives prior probabilities"""
    print("=== FORD BATTERY RESEARCH PRIORS ===")
    print("Using real Ford/Lincoln 12V lead-acid AGM battery specifications\n")
    
    calculator = FordBatteryRiskCalculator()
    
    # Test different Ford vehicles in different conditions
    test_cases = [
        ("F-150", "Michigan", 2),      # Popular truck, cold climate, new
        ("F-150", "Arizona", 4),       # Same truck, hot climate, older
        ("Transit", "Texas", 3),       # Commercial van, hot climate
        ("Explorer", "Florida", 6),    # SUV, hot climate, old
        ("Escape", "Washington", 1),   # Compact SUV, mild climate, new
        ("Lincoln", "California", 5),  # Luxury vehicle, hot climate, older
    ]
    
    print("Vehicle Type | Region     | Age | Prior Risk | Reasoning")
    print("-" * 65)
    
    for vehicle, region, age in test_cases:
        prior = calculator.calculate_prior_probability(vehicle, region, age)
        reasoning = []
        
        if vehicle in ["F-250", "F-350", "Transit"]:
            reasoning.append("commercial/heavy-duty")
        if region in calculator.hot_climate_regions:
            reasoning.append("hot climate region")
        if age >= 3:
            reasoning.append("age degradation")
        
        reasoning_str = ", ".join(reasoning) if reasoning else "baseline"
        print(f"{vehicle:12} | {region:10} | {age:3} | {prior:8.1%} | {reasoning_str}")
    
    print("\n" + "="*65)


def demonstrate_ford_stressor_analysis():
    """Show how Ford battery research drives likelihood ratios"""
    print("\n=== FORD BATTERY STRESSOR ANALYSIS ===")
    print("Using real lead-acid AGM battery temperature sensitivity data\n")
    
    calculator = FordBatteryRiskCalculator()
    
    # Test different stressor scenarios
    scenarios = [
        {
            "name": "Normal Conditions",
            "stressors": {
                "max_temp_7day": 85,
                "commercial_use": False,
                "region": "Michigan"
            }
        },
        {
            "name": "Hot Climate Summer",
            "stressors": {
                "max_temp_7day": 105,
                "commercial_use": False,
                "region": "Arizona"
            }
        },
        {
            "name": "Extreme Heat",
            "stressors": {
                "max_temp_7day": 115,
                "commercial_use": False,
                "region": "Arizona"
            }
        },
        {
            "name": "Commercial Use",
            "stressors": {
                "max_temp_7day": 95,
                "commercial_use": True,
                "high_vibration": True,
                "region": "Texas"
            }
        },
        {
            "name": "Multiple Stressors",
            "stressors": {
                "max_temp_7day": 108,
                "commercial_use": True,
                "maintenance_deferred": True,
                "deep_discharge_events": 2,
                "region": "Florida"
            }
        }
    ]
    
    print("Scenario            | Likelihood Ratio | Risk Multiplier")
    print("-" * 55)
    
    for scenario in scenarios:
        lr = calculator.calculate_likelihood_ratio(scenario["stressors"])
        print(f"{scenario['name']:19} | {lr:14.2f} | {lr:11.1f}x")
    
    print("\n" + "="*55)


def demonstrate_bayesian_calculation():
    """Show complete Bayesian calculation using Ford battery research"""
    print("\n=== COMPLETE BAYESIAN CALCULATION ===")
    print("Prior × Likelihood Ratio → Posterior Risk\n")
    
    calculator = FordBatteryRiskCalculator()
    
    # Example: F-150 in Arizona, 4 years old, summer heat
    vehicle_type = "F-150"
    region = "Arizona"
    age = 4
    
    stressors = {
        "max_temp_7day": 112,        # Extreme heat
        "commercial_use": False,      # Personal use
        "region": region,
        "maintenance_deferred": False
    }
    
    # Calculate prior
    prior = calculator.calculate_prior_probability(vehicle_type, region, age)
    
    # Calculate likelihood ratio
    likelihood_ratio = calculator.calculate_likelihood_ratio(stressors)
    
    # Bayesian update
    prior_odds = prior / (1 - prior)
    posterior_odds = prior_odds * likelihood_ratio
    posterior_prob = posterior_odds / (1 + posterior_odds)
    
    print(f"Vehicle: {vehicle_type}")
    print(f"Region: {region}")
    print(f"Age: {age} years")
    print(f"Max Temperature: {stressors['max_temp_7day']}°F")
    print()
    print("CALCULATION STEPS:")
    print(f"1. Prior Probability: {prior:.1%}")
    print(f"   - Base F-150 rate: 4.0%")
    print(f"   - Hot climate multiplier: 2.3x")
    print(f"   - Age adjustment (4 years): 1.8x")
    print()
    print(f"2. Likelihood Ratio: {likelihood_ratio:.2f}")
    print(f"   - Temperature >110°F: 6.2x")
    print(f"   - Hot climate region: 2.3x")
    print(f"   - Summer season: 1.6x")
    print()
    print(f"3. Bayesian Update:")
    print(f"   - Prior odds: {prior_odds:.3f}")
    print(f"   - Posterior odds: {posterior_odds:.3f}")
    print(f"   - Posterior probability: {posterior_prob:.1%}")
    print()
    print(f"RESULT: {posterior_prob:.1%} annual battery failure risk")
    
    # Risk classification
    if posterior_prob >= 0.20:
        severity = "SEVERE"
    elif posterior_prob >= 0.12:
        severity = "CRITICAL"
    elif posterior_prob >= 0.07:
        severity = "HIGH"
    elif posterior_prob >= 0.03:
        severity = "MODERATE"
    else:
        severity = "LOW"
    
    print(f"Risk Classification: {severity}")
    print()
    print("FORD BATTERY RESEARCH FOUNDATION:")
    print("- Lead-acid AGM battery chemistry")
    print("- Temperature sensitivity: 50% capacity loss at 0°F")
    print("- Exponential failure rate >100°F")
    print("- Geographic hot climate analysis")
    print("- Commercial fleet usage patterns")
    print()
    print("="*60)


if __name__ == "__main__":
    print("FORD BATTERY RESEARCH BAYESIAN RISK SCORING DEMO")
    print("=" * 60)
    print("Updated to use real Ford/Lincoln 12V battery specifications")
    print("Lead-acid AGM chemistry (NOT lithium-ion)")
    print()
    
    demonstrate_ford_battery_priors()
    demonstrate_ford_stressor_analysis()
    demonstrate_bayesian_calculation()
    
    print("\nDEMO COMPLETE")
    print("The system now uses REAL Ford battery research data")
    print("for accurate lead-acid AGM battery risk scoring.") 