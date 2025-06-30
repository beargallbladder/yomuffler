#!/usr/bin/env python3
"""
🎯 COHORT-RELATIVE OUTLIER DETECTOR 🎯
FIXES THE "EVERYTHING IS HIGH RISK" PROBLEM

Key insight: A coastal Florida F-150 with salt + humidity is NORMAL
But an inland Michigan F-150 with the same pattern is an OUTLIER

Only flag vehicles that are statistical outliers within their cohort
"""

import json
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CohortRelativeOutlierDetector:
    def __init__(self):
        """Initialize cohort-relative analysis system"""
        
        # Define meaningful cohorts for comparison
        self.cohort_definitions = {
            "geographic_climate": ["state", "climate_zone"],
            "vehicle_type": ["model"],
            "usage_pattern": ["vehicle_age", "current_mileage"],
            "combined": ["state", "model", "climate_zone"]
        }
        
        # Expected stressor combinations (NOT outliers)
        self.expected_combinations = {
            "coastal_normal": ["humidity_cycling_stress", "salt_corrosion_exposure"],
            "heavy_duty_normal": ["towing_load_stress", "vibration_stress"],
            "urban_normal": ["stop_and_go_traffic", "multi_driver_usage"],
            "age_related_normal": ["deep_discharge_events", "extended_idle_exposure"]
        }
        
        # Outlier thresholds
        self.outlier_thresholds = {
            "severe_outlier": 95,    # 95th percentile within cohort
            "moderate_outlier": 85,  # 85th percentile within cohort
            "worth_attention": 75    # 75th percentile within cohort
        }
        
        logger.info("🎯 Cohort-Relative Outlier Detector initialized")
        logger.info("📊 Focus: Statistical outliers, not absolute high risk")
    
    def load_analysis_data(self, filename: str) -> Dict:
        """Load previous analysis results"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            logger.info(f"✅ Loaded analysis data from {filename}")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to load analysis data: {e}")
            return {}
    
    def create_cohorts(self, vehicles: List[Dict]) -> Dict[str, List[Dict]]:
        """Create cohorts for relative comparison"""
        
        cohorts = defaultdict(list)
        
        for vehicle in vehicles:
            # Geographic-climate cohort
            geo_key = f"{vehicle.get('state', 'XX')}_{vehicle.get('climate_zone', 'unknown')}"
            cohorts[f"geo_{geo_key}"].append(vehicle)
            
            # Vehicle type cohort  
            model_key = vehicle.get('model', 'unknown')
            cohorts[f"model_{model_key}"].append(vehicle)
            
            # Usage pattern cohort (age + mileage bands)
            age = vehicle.get('vehicle_age', 0)
            mileage = vehicle.get('current_mileage', 0)
            age_band = "new" if age <= 2 else "mid" if age <= 4 else "old"
            mileage_band = "low" if mileage < 35000 else "medium" if mileage < 50000 else "high"
            usage_key = f"{age_band}_{mileage_band}"
            cohorts[f"usage_{usage_key}"].append(vehicle)
            
            # Combined cohort (most specific)
            combined_key = f"{vehicle.get('state', 'XX')}_{model_key}_{vehicle.get('climate_zone', 'unknown')}"
            cohorts[f"combined_{combined_key}"].append(vehicle)
        
        # Filter out cohorts with too few vehicles
        filtered_cohorts = {k: v for k, v in cohorts.items() if len(v) >= 10}
        
        logger.info(f"📊 Created {len(filtered_cohorts)} cohorts (min 10 vehicles each)")
        return filtered_cohorts
    
    def calculate_cohort_statistics(self, cohort_vehicles: List[Dict]) -> Dict[str, Any]:
        """Calculate statistical distribution for a cohort"""
        
        if len(cohort_vehicles) < 3:
            return {"insufficient_data": True}
        
        # Extract key metrics for comparison
        risk_scores = [v.get('posterior_probability', 0) for v in cohort_vehicles]
        stressor_counts = [v.get('stressor_count', 0) for v in cohort_vehicles]
        revenue_opps = [v.get('revenue_opportunity', 0) for v in cohort_vehicles]
        
        stats_data = {
            "cohort_size": len(cohort_vehicles),
            "risk_score_stats": {
                "mean": float(np.mean(risk_scores)),
                "median": float(np.median(risk_scores)),
                "std": float(np.std(risk_scores)),
                "percentiles": {
                    "75th": float(np.percentile(risk_scores, 75)),
                    "85th": float(np.percentile(risk_scores, 85)),
                    "95th": float(np.percentile(risk_scores, 95))
                }
            },
            "stressor_count_stats": {
                "mean": float(np.mean(stressor_counts)),
                "median": float(np.median(stressor_counts)),
                "max": int(np.max(stressor_counts))
            },
            "revenue_stats": {
                "mean": float(np.mean(revenue_opps)),
                "median": float(np.median(revenue_opps)),
                "percentiles": {
                    "75th": float(np.percentile(revenue_opps, 75)),
                    "85th": float(np.percentile(revenue_opps, 85)),
                    "95th": float(np.percentile(revenue_opps, 95))
                }
            }
        }
        
        return stats_data
    
    def detect_outliers_in_cohort(self, vehicle: Dict, cohort_vehicles: List[Dict], 
                                 cohort_stats: Dict) -> Dict[str, Any]:
        """Detect if a vehicle is an outlier within its cohort"""
        
        if cohort_stats.get("insufficient_data"):
            return {"outlier_status": "insufficient_cohort_data"}
        
        vehicle_risk = vehicle.get('posterior_probability', 0)
        vehicle_stressors = vehicle.get('stressor_count', 0)
        vehicle_revenue = vehicle.get('revenue_opportunity', 0)
        
        # Calculate percentile rankings within cohort
        cohort_risks = [v.get('posterior_probability', 0) for v in cohort_vehicles]
        cohort_stressor_counts = [v.get('stressor_count', 0) for v in cohort_vehicles]
        cohort_revenues = [v.get('revenue_opportunity', 0) for v in cohort_vehicles]
        
        risk_percentile = stats.percentileofscore(cohort_risks, vehicle_risk)
        stressor_percentile = stats.percentileofscore(cohort_stressor_counts, vehicle_stressors)
        revenue_percentile = stats.percentileofscore(cohort_revenues, vehicle_revenue)
        
        # Determine outlier status
        outlier_analysis = {
            "risk_percentile_in_cohort": round(risk_percentile, 1),
            "stressor_count_percentile": round(stressor_percentile, 1),
            "revenue_percentile": round(revenue_percentile, 1),
            "cohort_size": len(cohort_vehicles),
            "cohort_risk_mean": round(cohort_stats["risk_score_stats"]["mean"], 3),
            "vehicle_vs_cohort_risk": round(vehicle_risk - cohort_stats["risk_score_stats"]["mean"], 3)
        }
        
        # Classification logic - MUCH MORE RESTRICTIVE
        if risk_percentile >= 95 and stressor_percentile >= 90:
            outlier_analysis["outlier_status"] = "severe_outlier"
            outlier_analysis["priority"] = "IMMEDIATE"
            outlier_analysis["reasoning"] = f"Top 5% risk + top 10% stressor count in cohort"
        elif risk_percentile >= 90 and stressor_percentile >= 85:
            outlier_analysis["outlier_status"] = "moderate_outlier" 
            outlier_analysis["priority"] = "HIGH"
            outlier_analysis["reasoning"] = f"Top 10% risk + top 15% stressor count in cohort"
        elif risk_percentile >= 85:
            outlier_analysis["outlier_status"] = "worth_attention"
            outlier_analysis["priority"] = "MONITOR"
            outlier_analysis["reasoning"] = f"Top 15% risk in cohort"
        else:
            outlier_analysis["outlier_status"] = "normal_for_cohort"
            outlier_analysis["priority"] = "ROUTINE"
            outlier_analysis["reasoning"] = f"Normal variation within cohort"
        
        return outlier_analysis
    
    def check_unexpected_stressor_combinations(self, vehicle: Dict) -> Dict[str, Any]:
        """Check for unexpected stressor combinations that deserve attention"""
        
        active_stressors = set(vehicle.get('active_stressors', []))
        vehicle_state = vehicle.get('state', '')
        vehicle_climate = vehicle.get('climate_zone', '')
        vehicle_model = vehicle.get('model', '')
        
        unexpected_patterns = []
        
        # Salt corrosion inland (unexpected)
        if 'salt_corrosion_exposure' in active_stressors and 'coastal' not in vehicle_climate:
            unexpected_patterns.append("Salt corrosion detected inland - investigate source")
        
        # Humidity cycling in dry climates (unexpected)
        if 'humidity_cycling_stress' in active_stressors and vehicle_state in ['AZ', 'NV', 'NM']:
            unexpected_patterns.append("Humidity cycling in dry climate - unusual pattern")
        
        # Deep discharge in new vehicles (unexpected)
        if 'deep_discharge_events' in active_stressors and vehicle.get('vehicle_age', 0) <= 2:
            unexpected_patterns.append("Deep discharge in new vehicle - possible defect")
        
        # Towing stress in non-truck vehicles (unexpected)
        if 'towing_load_stress' in active_stressors and 'F-' not in vehicle_model:
            unexpected_patterns.append("Heavy towing loads in non-truck vehicle")
        
        # Multiple electrical stressors (concerning)
        electrical_stressors = {'parasitic_draw_stress', 'alternator_cycling_stress', 
                              'voltage_regulation_stress', 'deep_discharge_events'}
        electrical_count = len(active_stressors.intersection(electrical_stressors))
        if electrical_count >= 3:
            unexpected_patterns.append(f"Multiple electrical issues ({electrical_count}) - systematic problem")
        
        return {
            "unexpected_pattern_count": len(unexpected_patterns),
            "unexpected_patterns": unexpected_patterns,
            "needs_investigation": len(unexpected_patterns) > 0
        }
    
    def analyze_all_vehicles(self, analysis_data: Dict) -> Dict[str, Any]:
        """Perform cohort-relative outlier analysis on all vehicles"""
        
        vehicles = analysis_data.get('vehicle_analyses', [])
        if not vehicles:
            logger.error("❌ No vehicle analysis data found")
            return {}
        
        logger.info(f"🔍 Analyzing {len(vehicles)} vehicles for cohort-relative outliers")
        
        # Create cohorts
        cohorts = self.create_cohorts(vehicles)
        
        # Calculate cohort statistics
        cohort_stats = {}
        for cohort_name, cohort_vehicles in cohorts.items():
            cohort_stats[cohort_name] = self.calculate_cohort_statistics(cohort_vehicles)
        
        # Analyze each vehicle relative to its cohorts
        outlier_results = []
        true_outliers = 0
        attention_worthy = 0
        unexpected_patterns = 0
        
        for vehicle in vehicles:
            vin = vehicle.get('vin', 'UNKNOWN')
            
            # Find best cohort match for this vehicle
            best_cohort = self._find_best_cohort(vehicle, cohorts)
            
            if best_cohort:
                cohort_analysis = self.detect_outliers_in_cohort(
                    vehicle, cohorts[best_cohort], cohort_stats[best_cohort]
                )
            else:
                cohort_analysis = {"outlier_status": "no_suitable_cohort"}
            
            # Check for unexpected patterns
            pattern_analysis = self.check_unexpected_stressor_combinations(vehicle)
            
            # Combine analyses
            vehicle_outlier_analysis = {
                **vehicle,  # Original vehicle data
                "cohort_analysis": cohort_analysis,
                "pattern_analysis": pattern_analysis,
                "best_cohort": best_cohort,
                "final_recommendation": self._generate_final_recommendation(
                    cohort_analysis, pattern_analysis
                )
            }
            
            outlier_results.append(vehicle_outlier_analysis)
            
            # Count true outliers
            outlier_status = cohort_analysis.get("outlier_status", "normal")
            if outlier_status == "severe_outlier":
                true_outliers += 1
            elif outlier_status in ["moderate_outlier", "worth_attention"]:
                attention_worthy += 1
            
            if pattern_analysis.get("needs_investigation"):
                unexpected_patterns += 1
        
        # Generate summary
        total_vehicles = len(vehicles)
        outlier_summary = {
            "total_vehicles_analyzed": total_vehicles,
            "cohorts_created": len(cohorts),
            "true_severe_outliers": true_outliers,
            "attention_worthy_vehicles": attention_worthy,
            "unexpected_pattern_vehicles": unexpected_patterns,
            "severe_outlier_percentage": round((true_outliers / total_vehicles) * 100, 1),
            "actionable_percentage": round(((true_outliers + attention_worthy) / total_vehicles) * 100, 1),
            "processing_timestamp": datetime.now().isoformat(),
            "analysis_method": "Cohort-Relative Statistical Outlier Detection"
        }
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"cohort_relative_outliers_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                "summary": outlier_summary,
                "cohort_statistics": cohort_stats,
                "vehicle_outlier_analyses": outlier_results
            }, f, indent=2)
        
        logger.info("🎯 COHORT-RELATIVE ANALYSIS COMPLETE!")
        logger.info(f"📊 Total vehicles: {total_vehicles}")
        logger.info(f"🔥 TRUE SEVERE OUTLIERS: {true_outliers} ({outlier_summary['severe_outlier_percentage']}%)")
        logger.info(f"⚠️  Attention worthy: {attention_worthy}")
        logger.info(f"🔍 Unexpected patterns: {unexpected_patterns}")
        logger.info(f"🎯 ACTIONABLE ALERTS: {outlier_summary['actionable_percentage']}% (much more reasonable!)")
        logger.info(f"📄 Results saved: {output_file}")
        
        return {
            "summary": outlier_summary,
            "results_file": output_file,
            "success": True
        }
    
    def _find_best_cohort(self, vehicle: Dict, cohorts: Dict[str, List[Dict]]) -> str:
        """Find the best cohort match for a vehicle"""
        
        # Try combined cohort first (most specific)
        state = vehicle.get('state', 'XX')
        model = vehicle.get('model', 'unknown')
        climate = vehicle.get('climate_zone', 'unknown')
        
        combined_key = f"combined_{state}_{model}_{climate}"
        if combined_key in cohorts and len(cohorts[combined_key]) >= 10:
            return combined_key
        
        # Try geographic cohort
        geo_key = f"geo_{state}_{climate}"
        if geo_key in cohorts and len(cohorts[geo_key]) >= 10:
            return geo_key
        
        # Try model cohort
        model_key = f"model_{model}"
        if model_key in cohorts and len(cohorts[model_key]) >= 10:
            return model_key
        
        # Try usage cohort
        age = vehicle.get('vehicle_age', 0)
        mileage = vehicle.get('current_mileage', 0)
        age_band = "new" if age <= 2 else "mid" if age <= 4 else "old"
        mileage_band = "low" if mileage < 35000 else "medium" if mileage < 50000 else "high"
        usage_key = f"usage_{age_band}_{mileage_band}"
        if usage_key in cohorts and len(cohorts[usage_key]) >= 10:
            return usage_key
        
        return None
    
    def _generate_final_recommendation(self, cohort_analysis: Dict, pattern_analysis: Dict) -> Dict:
        """Generate final recommendation based on all analyses"""
        
        outlier_status = cohort_analysis.get("outlier_status", "normal")
        has_unexpected = pattern_analysis.get("needs_investigation", False)
        
        if outlier_status == "severe_outlier" or has_unexpected:
            return {
                "action": "IMMEDIATE",
                "priority": 1,
                "reasoning": "Statistical outlier in cohort OR unexpected pattern detected"
            }
        elif outlier_status == "moderate_outlier":
            return {
                "action": "HIGH_PRIORITY",
                "priority": 2,
                "reasoning": "Significant deviation from cohort normal"
            }
        elif outlier_status == "worth_attention":
            return {
                "action": "MONITOR",
                "priority": 3,
                "reasoning": "Above average for cohort but not extreme"
            }
        else:
            return {
                "action": "ROUTINE",
                "priority": 4,
                "reasoning": "Normal variation within cohort"
            }

async def main():
    """Main execution function"""
    detector = CohortRelativeOutlierDetector()
    
    # Find latest analysis file
    import glob
    analysis_files = glob.glob("enhanced_13_stressor_analysis_*.json")
    if not analysis_files:
        logger.error("❌ No analysis files found. Run enhanced processor first.")
        return
    
    latest_file = max(analysis_files, key=lambda x: x.split('_')[-1])
    logger.info(f"📄 Using analysis file: {latest_file}")
    
    # Load and analyze
    analysis_data = detector.load_analysis_data(latest_file)
    result = detector.analyze_all_vehicles(analysis_data)
    
    if result["success"]:
        logger.info("✅ COHORT-RELATIVE OUTLIER DETECTION COMPLETE")
        logger.info("🎯 NOW YOU HAVE ACTIONABLE INTELLIGENCE!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 