#!/usr/bin/env python3
"""
Calculate Real Priors and Likelihood Ratios from VIN Leads Database
Validates Bayesian calculations line by line
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import json
from typing import Dict, List, Tuple

def load_vin_database() -> pd.DataFrame:
    """Load the VIN leads database"""
    print("🔍 Loading VIN leads database...")
    df = pd.read_csv('vin_leads_database_20250629_142452.csv')
    print(f"📊 Loaded {len(df)} records")
    return df

def calculate_base_priors(df: pd.DataFrame) -> Dict:
    """Calculate base priors by vehicle characteristics"""
    print("\n🧮 Calculating Base Priors...")
    
    priors = {
        'by_model': {},
        'by_age': {},
        'by_climate': {},
        'by_vehicle_type': {}
    }
    
    # By vehicle model
    model_priors = df.groupby('model')['base_prior'].agg(['mean', 'std', 'count'])
    for model, stats in model_priors.iterrows():
        priors['by_model'][model] = {
            'mean': stats['mean'],
            'std': stats['std'],
            'count': stats['count']
        }
    
    # By vehicle age
    age_priors = df.groupby('vehicle_age')['base_prior'].agg(['mean', 'std', 'count'])
    for age, stats in age_priors.iterrows():
        priors['by_age'][age] = {
            'mean': stats['mean'],
            'std': stats['std'],
            'count': stats['count']
        }
    
    # By climate zone
    climate_priors = df.groupby('climate_zone')['base_prior'].agg(['mean', 'std', 'count'])
    for climate, stats in climate_priors.iterrows():
        priors['by_climate'][climate] = {
            'mean': stats['mean'],
            'std': stats['std'],
            'count': stats['count']
        }
    
    # By vehicle type
    type_priors = df.groupby('vehicle_type')['base_prior'].agg(['mean', 'std', 'count'])
    for vtype, stats in type_priors.iterrows():
        priors['by_vehicle_type'][vtype] = {
            'mean': stats['mean'],
            'std': stats['std'],
            'count': stats['count']
        }
    
    return priors

def calculate_likelihood_ratios(df: pd.DataFrame) -> Dict:
    """Calculate likelihood ratios for different stressors"""
    print("\n🎯 Calculating Likelihood Ratios...")
    
    likelihood_ratios = {
        'temperature_stress': {},
        'short_trip_percentage': {},
        'start_cycles': {},
        'combined_patterns': {}
    }
    
    # Parse active_lrs column (it's a string representation of a list)
    df['parsed_lrs'] = df['active_lrs'].apply(lambda x: eval(x) if x and x != '[]' else [])
    df['lr_count'] = df['parsed_lrs'].apply(len)
    
    # Temperature stress ranges
    temp_ranges = [(0, 0.05), (0.05, 0.1), (0.1, 0.15), (0.15, 0.2), (0.2, 1.0)]
    for low, high in temp_ranges:
        mask = (df['temperature_stress'] >= low) & (df['temperature_stress'] < high)
        subset = df[mask]
        if len(subset) > 0:
            likelihood_ratios['temperature_stress'][f'{low}-{high}'] = {
                'mean_combined_lr': subset['combined_lr'].mean(),
                'count': len(subset),
                'avg_posterior': subset['posterior_probability'].mean()
            }
    
    # Short trip percentage ranges
    trip_ranges = [(0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
    for low, high in trip_ranges:
        mask = (df['short_trip_percentage'] >= low) & (df['short_trip_percentage'] < high)
        subset = df[mask]
        if len(subset) > 0:
            likelihood_ratios['short_trip_percentage'][f'{low}-{high}'] = {
                'mean_combined_lr': subset['combined_lr'].mean(),
                'count': len(subset),
                'avg_posterior': subset['posterior_probability'].mean()
            }
    
    # Start cycles analysis
    start_cycle_ranges = [(0, 1500), (1500, 2000), (2000, 2500), (2500, 3000), (3000, 5000)]
    for low, high in start_cycle_ranges:
        mask = (df['start_cycles_annual'] >= low) & (df['start_cycles_annual'] < high)
        subset = df[mask]
        if len(subset) > 0:
            likelihood_ratios['start_cycles'][f'{low}-{high}'] = {
                'mean_combined_lr': subset['combined_lr'].mean(),
                'count': len(subset),
                'avg_posterior': subset['posterior_probability'].mean()
            }
    
    # Combined patterns (multiple stressors)
    for lr_count in range(6):  # 0 to 5+ stressors
        mask = df['lr_count'] == lr_count
        subset = df[mask]
        if len(subset) > 0:
            likelihood_ratios['combined_patterns'][f'{lr_count}_stressors'] = {
                'mean_combined_lr': subset['combined_lr'].mean(),
                'count': len(subset),
                'avg_posterior': subset['posterior_probability'].mean()
            }
    
    return likelihood_ratios

def validate_bayesian_calculations(df: pd.DataFrame, sample_size: int = 100) -> Dict:
    """Validate Bayesian calculations line by line"""
    print(f"\n🔬 Validating Bayesian Calculations (sample size: {sample_size})...")
    
    # Sample random records for validation
    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42)
    
    validation_results = {
        'total_checked': 0,
        'correct_calculations': 0,
        'calculation_errors': [],
        'sample_validations': []
    }
    
    for idx, row in sample_df.iterrows():
        try:
            # Get the components
            base_prior = row['base_prior']
            adjusted_prior = row['adjusted_prior']
            combined_lr = row['combined_lr']
            posterior = row['posterior_probability']
            
            # Calculate expected posterior using Bayes' theorem
            # P(failure|evidence) = P(evidence|failure) * P(failure) / P(evidence)
            # Simplified: posterior = (prior * likelihood) / ((prior * likelihood) + ((1-prior) * 1))
            
            expected_posterior = (adjusted_prior * combined_lr) / (
                (adjusted_prior * combined_lr) + ((1 - adjusted_prior) * 1)
            )
            
            # Check if calculations match (within tolerance)
            tolerance = 0.001
            is_correct = abs(posterior - expected_posterior) < tolerance
            
            validation_results['total_checked'] += 1
            if is_correct:
                validation_results['correct_calculations'] += 1
            else:
                validation_results['calculation_errors'].append({
                    'index': idx,
                    'base_prior': base_prior,
                    'adjusted_prior': adjusted_prior,
                    'combined_lr': combined_lr,
                    'actual_posterior': posterior,
                    'expected_posterior': expected_posterior,
                    'difference': abs(posterior - expected_posterior)
                })
            
            # Store sample for detailed report
            if len(validation_results['sample_validations']) < 10:
                validation_results['sample_validations'].append({
                    'vin': row['vin'],
                    'model': row['model'],
                    'age': row['vehicle_age'],
                    'climate': row['climate_zone'],
                    'base_prior': base_prior,
                    'adjusted_prior': adjusted_prior,
                    'combined_lr': combined_lr,
                    'actual_posterior': posterior,
                    'expected_posterior': expected_posterior,
                    'is_correct': is_correct,
                    'difference': abs(posterior - expected_posterior)
                })
                
        except Exception as e:
            validation_results['calculation_errors'].append({
                'index': idx,
                'error': str(e)
            })
    
    validation_results['accuracy_percentage'] = (
        validation_results['correct_calculations'] / validation_results['total_checked'] * 100
    )
    
    return validation_results

def analyze_stressor_impact(df: pd.DataFrame) -> Dict:
    """Analyze the impact of different stressors on failure probability"""
    print("\n📈 Analyzing Stressor Impact...")
    
    stressor_analysis = {
        'temperature_impact': {},
        'short_trip_impact': {},
        'age_impact': {},
        'climate_impact': {}
    }
    
    # Temperature stress impact
    temp_bins = pd.cut(df['temperature_stress'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    temp_impact = df.groupby(temp_bins)['posterior_probability'].agg(['mean', 'std', 'count'])
    for bin_name, stats in temp_impact.iterrows():
        stressor_analysis['temperature_impact'][bin_name] = {
            'mean_posterior': stats['mean'],
            'std_posterior': stats['std'],
            'count': stats['count']
        }
    
    # Short trip impact
    trip_bins = pd.cut(df['short_trip_percentage'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    trip_impact = df.groupby(trip_bins)['posterior_probability'].agg(['mean', 'std', 'count'])
    for bin_name, stats in trip_impact.iterrows():
        stressor_analysis['short_trip_impact'][bin_name] = {
            'mean_posterior': stats['mean'],
            'std_posterior': stats['std'],
            'count': stats['count']
        }
    
    # Age impact
    age_impact = df.groupby('vehicle_age')['posterior_probability'].agg(['mean', 'std', 'count'])
    for age, stats in age_impact.iterrows():
        stressor_analysis['age_impact'][age] = {
            'mean_posterior': stats['mean'],
            'std_posterior': stats['std'],
            'count': stats['count']
        }
    
    # Climate impact
    climate_impact = df.groupby('climate_zone')['posterior_probability'].agg(['mean', 'std', 'count'])
    for climate, stats in climate_impact.iterrows():
        stressor_analysis['climate_impact'][climate] = {
            'mean_posterior': stats['mean'],
            'std_posterior': stats['std'],
            'count': stats['count']
        }
    
    return stressor_analysis

def generate_detailed_report(priors: Dict, likelihood_ratios: Dict, validation: Dict, stressor_analysis: Dict):
    """Generate a detailed mathematical report"""
    print("\n📋 Generating Detailed Report...")
    
    report = {
        'summary': {
            'total_records': validation['total_checked'],
            'calculation_accuracy': f"{validation['accuracy_percentage']:.2f}%",
            'correct_calculations': validation['correct_calculations'],
            'calculation_errors': len(validation['calculation_errors']),
            'priors_calculated': len(priors['by_model']),
            'likelihood_ratios_calculated': sum(len(lr_dict) for lr_dict in likelihood_ratios.values())
        },
        'priors': priors,
        'likelihood_ratios': likelihood_ratios,
        'validation': validation,
        'stressor_analysis': stressor_analysis
    }
    
    return report

def print_executive_summary(report: Dict):
    """Print executive summary of the analysis"""
    print("\n" + "="*80)
    print("🎯 FORD BAYESIAN RISK CALCULATOR - MATHEMATICAL VALIDATION")
    print("="*80)
    
    summary = report['summary']
    print(f"📊 Total Records Analyzed: {summary['total_records']:,}")
    print(f"🎯 Calculation Accuracy: {summary['calculation_accuracy']}")
    print(f"✅ Correct Calculations: {summary['correct_calculations']:,}")
    print(f"❌ Calculation Errors: {summary['calculation_errors']:,}")
    print(f"🔧 Vehicle Models Analyzed: {summary['priors_calculated']}")
    print(f"📈 Likelihood Ratios Calculated: {summary['likelihood_ratios_calculated']}")
    
    print("\n🚗 PRIOR PROBABILITIES BY MODEL:")
    for model, stats in report['priors']['by_model'].items():
        print(f"  {model}: {stats['mean']:.3f} ± {stats['std']:.3f} (n={stats['count']})")
    
    print("\n🌡️ LIKELIHOOD RATIOS BY TEMPERATURE STRESS:")
    for temp_range, stats in report['likelihood_ratios']['temperature_stress'].items():
        print(f"  {temp_range}: LR={stats['mean_combined_lr']:.2f}, Posterior={stats['avg_posterior']:.3f} (n={stats['count']})")
    
    print("\n🔬 SAMPLE VALIDATION RESULTS:")
    for i, sample in enumerate(report['validation']['sample_validations'][:5]):
        status = "✅ CORRECT" if sample['is_correct'] else "❌ ERROR"
        print(f"  {i+1}. {sample['vin'][:8]}... {sample['model']} ({sample['age']}yr): {status}")
        print(f"     Prior: {sample['adjusted_prior']:.3f}, LR: {sample['combined_lr']:.2f}")
        print(f"     Actual: {sample['actual_posterior']:.3f}, Expected: {sample['expected_posterior']:.3f}")
        print(f"     Difference: {sample['difference']:.6f}")
    
    print("\n📊 STRESSOR IMPACT ANALYSIS:")
    for impact_type, impacts in report['stressor_analysis'].items():
        print(f"\n  {impact_type.upper()}:")
        for category, stats in impacts.items():
            if not pd.isna(stats['mean_posterior']):
                print(f"    {category}: {stats['mean_posterior']:.3f} ± {stats['std_posterior']:.3f} (n={stats['count']})")

def main():
    """Main analysis function"""
    print("🔍 FORD BAYESIAN RISK CALCULATOR - MATHEMATICAL VALIDATION")
    print("="*70)
    
    # Load data
    df = load_vin_database()
    
    # Calculate priors
    priors = calculate_base_priors(df)
    
    # Calculate likelihood ratios
    likelihood_ratios = calculate_likelihood_ratios(df)
    
    # Validate calculations
    validation = validate_bayesian_calculations(df, sample_size=500)
    
    # Analyze stressor impact
    stressor_analysis = analyze_stressor_impact(df)
    
    # Generate report
    report = generate_detailed_report(priors, likelihood_ratios, validation, stressor_analysis)
    
    # Print executive summary
    print_executive_summary(report)
    
    # Save detailed report
    with open('bayesian_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Detailed report saved to: bayesian_validation_report.json")
    
    # Final verdict
    if validation['accuracy_percentage'] > 99:
        print("🎉 VERDICT: The math checks out! Bayesian calculations are mathematically sound.")
    elif validation['accuracy_percentage'] > 95:
        print("✅ VERDICT: The math is mostly correct with minor rounding differences.")
    else:
        print("⚠️  VERDICT: Mathematical errors detected. Review required.")
    
    return report

if __name__ == "__main__":
    report = main() 