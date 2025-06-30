#!/usr/bin/env python3
"""
⚡ SCALABLE COHORT OUTLIER ENGINE ⚡
Built for 100k+ VINs with lightning performance

Core insight: "Normal salt corrosion in Florida is not news... 
the WORST of the salt corrosions is."

Focus: Top 5-10% outliers within each cohort
"""

import json
import numpy as np
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScalableCohortOutlierEngine:
    def __init__(self):
        """Initialize high-performance outlier detection engine"""
        
        # Cohort definition strategies - hierarchical for scalability
        self.cohort_hierarchy = {
            "primary": ["state", "model"],  # Most specific
            "secondary": ["climate_zone", "model"],  # Fallback
            "tertiary": ["model"],  # Broad fallback
            "fallback": ["climate_zone"]  # Last resort
        }
        
        # Minimum cohort sizes for statistical validity
        self.min_cohort_sizes = {
            "primary": 20,     # Needs 20+ for tight cohorts
            "secondary": 15,   # 15+ for medium cohorts  
            "tertiary": 30,    # 30+ for broad cohorts
            "fallback": 50     # 50+ for very broad cohorts
        }
        
        # Outlier detection thresholds (percentile within cohort)
        self.outlier_thresholds = {
            "severe": 97,      # Top 3% within cohort
            "high": 92,        # Top 8% within cohort
            "moderate": 85,    # Top 15% within cohort
        }
        
        # Expected patterns by cohort (what's NORMAL)
        self.normal_patterns = {
            "FL_coastal": ["salt_corrosion_exposure", "humidity_cycling_stress"],
            "FL_F150": ["salt_corrosion_exposure", "humidity_cycling_stress", "towing_load_stress"],
            "heavy_duty": ["towing_load_stress", "vibration_stress"],
            "urban": ["stop_and_go_traffic", "multi_driver_usage"],
            "old_vehicle": ["deep_discharge_events", "extended_idle_exposure"]
        }
        
        logger.info("⚡ Scalable Cohort Outlier Engine initialized")
        logger.info("🎯 Target: Top 5-10% outliers within cohorts at scale")
    
    def load_and_preprocess(self, filename: str) -> pd.DataFrame:
        """Load and preprocess data for high-performance analysis"""
        
        start_time = time.time()
        
        # Load JSON data
        with open(filename, 'r') as f:
            data = json.load(f)
        
        vehicles = data.get('vehicle_analyses', [])
        
        # Convert to pandas for vectorized operations
        df = pd.DataFrame(vehicles)
        
        # Add derived columns for cohort creation
        df['cohort_primary'] = df['state'].astype(str) + '_' + df['model'].astype(str)
        df['cohort_secondary'] = df['climate_zone'].astype(str) + '_' + df['model'].astype(str)
        df['cohort_tertiary'] = df['model'].astype(str)
        df['cohort_fallback'] = df['climate_zone'].astype(str)
        
        # Ensure numeric columns
        df['posterior_probability'] = pd.to_numeric(df['posterior_probability'], errors='coerce')
        df['stressor_count'] = pd.to_numeric(df['stressor_count'], errors='coerce')
        df['revenue_opportunity'] = pd.to_numeric(df['revenue_opportunity'], errors='coerce')
        
        load_time = time.time() - start_time
        logger.info(f"✅ Loaded and preprocessed {len(df)} vehicles in {load_time:.2f}s")
        
        return df
    
    def assign_cohorts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Efficiently assign vehicles to cohorts using hierarchical strategy"""
        
        start_time = time.time()
        
        # Count cohort sizes for each level
        cohort_counts = {}
        for level in self.cohort_hierarchy.keys():
            cohort_col = f'cohort_{level}'
            cohort_counts[level] = df[cohort_col].value_counts()
        
        # Assign best cohort for each vehicle
        def find_best_cohort(row):
            for level in ['primary', 'secondary', 'tertiary', 'fallback']:
                cohort_key = row[f'cohort_{level}']
                min_size = self.min_cohort_sizes[level]
                
                if cohort_counts[level].get(cohort_key, 0) >= min_size:
                    return cohort_key, level
            
            return 'insufficient_data', 'none'
        
        # Apply cohort assignment vectorized
        cohort_assignments = df.apply(find_best_cohort, axis=1)
        df['assigned_cohort'] = [x[0] for x in cohort_assignments]
        df['cohort_level'] = [x[1] for x in cohort_assignments]
        
        # Filter out vehicles without valid cohorts
        valid_df = df[df['cohort_level'] != 'none'].copy()
        
        assignment_time = time.time() - start_time
        logger.info(f"📊 Assigned cohorts to {len(valid_df)}/{len(df)} vehicles in {assignment_time:.2f}s")
        
        # Log cohort distribution
        cohort_summary = valid_df['assigned_cohort'].value_counts()
        logger.info(f"🎯 Created {len(cohort_summary)} valid cohorts")
        logger.info(f"📈 Largest cohort: {cohort_summary.iloc[0]} vehicles")
        logger.info(f"📉 Smallest cohort: {cohort_summary.iloc[-1]} vehicles")
        
        return valid_df
    
    def calculate_outlier_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate outlier scores efficiently using pandas groupby"""
        
        start_time = time.time()
        
        def calculate_percentiles(group):
            """Calculate percentile scores within each cohort"""
            
            # Risk score percentiles
            group['risk_percentile'] = group['posterior_probability'].rank(pct=True) * 100
            
            # Stressor count percentiles  
            group['stressor_percentile'] = group['stressor_count'].rank(pct=True) * 100
            
            # Revenue percentiles
            group['revenue_percentile'] = group['revenue_opportunity'].rank(pct=True) * 100
            
            # Combined outlier score (weighted average)
            group['outlier_score'] = (
                group['risk_percentile'] * 0.5 +
                group['stressor_percentile'] * 0.3 +
                group['revenue_percentile'] * 0.2
            )
            
            # Cohort statistics for context
            group['cohort_size'] = len(group)
            group['cohort_risk_mean'] = group['posterior_probability'].mean()
            group['cohort_risk_std'] = group['posterior_probability'].std()
            group['risk_vs_cohort'] = group['posterior_probability'] - group['cohort_risk_mean']
            
            return group
        
        # Apply calculations by cohort (vectorized)
        df_with_percentiles = df.groupby('assigned_cohort').apply(calculate_percentiles)
        
        calculation_time = time.time() - start_time
        logger.info(f"⚡ Calculated outlier scores in {calculation_time:.2f}s")
        
        return df_with_percentiles
    
    def classify_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify outliers based on cohort-relative percentiles"""
        
        start_time = time.time()
        
        # Vectorized outlier classification
        conditions = [
            (df['risk_percentile'] >= self.outlier_thresholds['severe']) & 
            (df['stressor_percentile'] >= 90),
            
            (df['risk_percentile'] >= self.outlier_thresholds['high']) & 
            (df['stressor_percentile'] >= 85),
            
            df['risk_percentile'] >= self.outlier_thresholds['moderate']
        ]
        
        choices = ['severe_outlier', 'high_outlier', 'moderate_outlier']
        
        df['outlier_classification'] = np.select(conditions, choices, default='normal_for_cohort')
        
        # Priority assignment
        priority_map = {
            'severe_outlier': 1,
            'high_outlier': 2, 
            'moderate_outlier': 3,
            'normal_for_cohort': 4
        }
        
        df['priority'] = df['outlier_classification'].map(priority_map)
        
        # Generate reasoning
        df['outlier_reasoning'] = df.apply(self._generate_reasoning, axis=1)
        
        classification_time = time.time() - start_time
        logger.info(f"🎯 Classified outliers in {classification_time:.2f}s")
        
        return df
    
    def _generate_reasoning(self, row) -> str:
        """Generate human-readable reasoning for outlier classification"""
        
        classification = row['outlier_classification']
        risk_pct = row['risk_percentile']
        stressor_pct = row['stressor_percentile']
        cohort = row['assigned_cohort']
        
        if classification == 'severe_outlier':
            return f"Top {100-risk_pct:.0f}% risk + top {100-stressor_pct:.0f}% stressor count in {cohort} cohort"
        elif classification == 'high_outlier':
            return f"Top {100-risk_pct:.0f}% risk in {cohort} cohort" 
        elif classification == 'moderate_outlier':
            return f"Above average risk in {cohort} cohort"
        else:
            return f"Normal variation within {cohort} cohort"
    
    def detect_unexpected_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect unexpected stressor patterns at scale"""
        
        start_time = time.time()
        
        # Convert active_stressors to set for efficient operations
        df['stressor_set'] = df['active_stressors'].apply(set)
        
        # Check for unexpected patterns
        def check_unexpected(row):
            stressors = row['stressor_set']
            state = row.get('state', '')
            climate = row.get('climate_zone', '')
            model = row.get('model', '')
            age = row.get('vehicle_age', 0)
            
            unexpected = []
            
            # Salt corrosion inland
            if 'salt_corrosion_exposure' in stressors and 'coastal' not in climate:
                unexpected.append("Salt corrosion inland")
            
            # Deep discharge in new vehicles
            if 'deep_discharge_events' in stressors and age <= 2:
                unexpected.append("Deep discharge in new vehicle")
            
            # Multiple electrical issues
            electrical = {'parasitic_draw_stress', 'alternator_cycling_stress', 
                         'voltage_regulation_stress', 'deep_discharge_events'}
            if len(stressors.intersection(electrical)) >= 3:
                unexpected.append("Multiple electrical issues")
            
            return unexpected
        
        df['unexpected_patterns'] = df.apply(check_unexpected, axis=1)
        df['has_unexpected'] = df['unexpected_patterns'].apply(lambda x: len(x) > 0)
        
        pattern_time = time.time() - start_time
        logger.info(f"🔍 Detected unexpected patterns in {pattern_time:.2f}s")
        
        return df
    
    def generate_actionable_alerts(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Generate final actionable alerts with business context"""
        
        start_time = time.time()
        
        # Filter to only actionable cases
        actionable_df = df[
            (df['outlier_classification'].isin(['severe_outlier', 'high_outlier'])) |
            (df['has_unexpected'] == True)
        ].copy()
        
        # Sort by priority
        actionable_df = actionable_df.sort_values(['priority', 'outlier_score'], ascending=[True, False])
        
        # Generate business summary
        total_vehicles = len(df)
        severe_outliers = len(df[df['outlier_classification'] == 'severe_outlier'])
        high_outliers = len(df[df['outlier_classification'] == 'high_outlier'])
        unexpected_patterns = len(df[df['has_unexpected'] == True])
        
        # Revenue analysis for actionable cases only
        actionable_revenue = actionable_df['revenue_opportunity'].sum()
        avg_actionable_revenue = actionable_df['revenue_opportunity'].mean() if len(actionable_df) > 0 else 0
        
        summary = {
            "total_vehicles_analyzed": total_vehicles,
            "actionable_alerts": len(actionable_df),
            "actionable_percentage": round((len(actionable_df) / total_vehicles) * 100, 1),
            "severe_outliers": severe_outliers,
            "high_outliers": high_outliers,
            "unexpected_patterns": unexpected_patterns,
            "total_actionable_revenue": int(actionable_revenue),
            "avg_revenue_per_actionable": int(avg_actionable_revenue),
            "analysis_method": "Scalable Cohort-Relative Outlier Detection",
            "processing_timestamp": datetime.now().isoformat()
        }
        
        generation_time = time.time() - start_time
        logger.info(f"📋 Generated actionable alerts in {generation_time:.2f}s")
        
        return actionable_df, summary
    
    def process_vehicles(self, filename: str) -> Dict[str, Any]:
        """Main processing pipeline for scalable outlier detection"""
        
        total_start = time.time()
        logger.info("🚀 STARTING SCALABLE COHORT OUTLIER ANALYSIS")
        
        # Step 1: Load and preprocess
        df = self.load_and_preprocess(filename)
        
        # Step 2: Assign cohorts
        df_with_cohorts = self.assign_cohorts(df)
        
        # Step 3: Calculate outlier scores
        df_with_scores = self.calculate_outlier_scores(df_with_cohorts)
        
        # Step 4: Classify outliers
        df_classified = self.classify_outliers(df_with_scores)
        
        # Step 5: Detect unexpected patterns
        df_with_patterns = self.detect_unexpected_patterns(df_classified)
        
        # Step 6: Generate actionable alerts
        actionable_df, summary = self.generate_actionable_alerts(df_with_patterns)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Full analysis results
        full_output_file = f"scalable_cohort_analysis_{timestamp}.json"
        df_with_patterns.to_json(full_output_file, orient='records', indent=2)
        
        # Actionable alerts only (for dealers)
        actionable_output_file = f"actionable_alerts_{timestamp}.json"
        actionable_data = {
            "summary": summary,
            "actionable_alerts": actionable_df.to_dict('records')
        }
        
        with open(actionable_output_file, 'w') as f:
            json.dump(actionable_data, f, indent=2)
        
        total_time = time.time() - total_start
        
        logger.info("🎯 SCALABLE COHORT ANALYSIS COMPLETE!")
        logger.info(f"⚡ Total processing time: {total_time:.2f}s")
        logger.info(f"📊 Processed: {len(df)} vehicles")
        logger.info(f"🔥 Actionable alerts: {len(actionable_df)} ({summary['actionable_percentage']}%)")
        logger.info(f"💰 Actionable revenue: ${summary['total_actionable_revenue']:,}")
        logger.info(f"📄 Full results: {full_output_file}")
        logger.info(f"🎯 Dealer alerts: {actionable_output_file}")
        
        return {
            "summary": summary,
            "full_results_file": full_output_file,
            "actionable_alerts_file": actionable_output_file,
            "processing_time": total_time,
            "success": True
        }

async def main():
    """Main execution function"""
    engine = ScalableCohortOutlierEngine()
    
    # Find latest analysis file
    import glob
    analysis_files = glob.glob("enhanced_13_stressor_analysis_*.json")
    if not analysis_files:
        logger.error("❌ No analysis files found. Run enhanced processor first.")
        return
    
    latest_file = max(analysis_files, key=lambda x: x.split('_')[-1])
    logger.info(f"📄 Using analysis file: {latest_file}")
    
    # Process vehicles
    result = engine.process_vehicles(latest_file)
    
    if result["success"]:
        logger.info("✅ SCALABLE OUTLIER DETECTION COMPLETE")
        logger.info("🎯 READY FOR 100K+ VIN DEPLOYMENT!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 