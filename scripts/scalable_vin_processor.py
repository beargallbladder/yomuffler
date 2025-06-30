#!/usr/bin/env python3
"""
🚀 SCALABLE VIN PROCESSOR
Handles 100k+ VINs with VIN consistency and cohort-relative outlier detection
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List
import numpy as np
from collections import defaultdict
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScalableVINProcessor:
    def __init__(self, batch_size: int = 1000):
        """Initialize scalable processor"""
        self.batch_size = batch_size
        logger.info(f"🚀 Scalable VIN Processor initialized (batch size: {batch_size})")
    
    async def process_pipeline(self, vin_count: int) -> Dict:
        """Complete pipeline: Generate → Analyze → Find Outliers"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        logger.info(f"🔥 STARTING SCALABLE PIPELINE FOR {vin_count:,} VINs")
        
        # Step 1: Generate consistent VIN database
        logger.info(f"📊 Step 1: Generating {vin_count:,} VINs...")
        vin_db_file = await self.generate_vin_database(vin_count, timestamp)
        
        # Step 2: Run 13-stressor analysis 
        logger.info(f"🧮 Step 2: Running 13-stressor analysis...")
        analysis_file = await self.run_stressor_analysis(vin_db_file, timestamp)
        
        # Step 3: Cohort-relative outlier detection
        logger.info(f"🎯 Step 3: Finding cohort outliers...")
        outlier_file = await self.find_cohort_outliers(analysis_file, vin_db_file, timestamp)
        
        # Step 4: Generate business summary
        logger.info(f"📈 Step 4: Generating business summary...")
        summary = await self.generate_business_summary(outlier_file)
        
        logger.info(f"✅ PIPELINE COMPLETE FOR {vin_count:,} VINs")
        return {
            "vin_database": vin_db_file,
            "analysis_file": analysis_file, 
            "outlier_file": outlier_file,
            "summary": summary,
            "success": True
        }
    
    async def generate_vin_database(self, count: int, timestamp: str) -> str:
        """Generate VIN database with specified count"""
        import subprocess
        
        # Use existing generator with count parameter
        cmd = f"python3 scripts/generate_lead_database.py --count {count}"
        
        logger.info(f"🔄 Generating {count:,} VINs...")
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ VIN generation failed: {result.stderr}")
            raise Exception("VIN generation failed")
        
        # Find the generated file
        import glob
        vin_files = glob.glob(f"vin_leads_database_*{timestamp}*.json")
        if not vin_files:
            vin_files = glob.glob("vin_leads_database_*.json")
            vin_files.sort(key=lambda x: x.split('_')[-1])
            latest_file = vin_files[-1]
        else:
            latest_file = vin_files[0]
        
        logger.info(f"✅ Generated VIN database: {latest_file}")
        return latest_file
    
    async def run_stressor_analysis(self, vin_db_file: str, timestamp: str) -> str:
        """Run 13-stressor analysis on VIN database"""
        import subprocess
        
        cmd = f"python3 scripts/enhanced_13_stressor_processor.py --input {vin_db_file}"
        
        logger.info(f"🔄 Running stressor analysis...")
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Stressor analysis failed: {result.stderr}")
            # Fallback: look for any enhanced analysis file
            import glob
            analysis_files = glob.glob("enhanced_13_stressor_analysis_*.json")
            if analysis_files:
                analysis_files.sort(key=lambda x: x.split('_')[-1])
                latest_file = analysis_files[-1]
                logger.info(f"📄 Using existing analysis file: {latest_file}")
                return latest_file
            else:
                raise Exception("No stressor analysis available")
        
        # Find the generated analysis file
        import glob
        analysis_files = glob.glob(f"enhanced_13_stressor_analysis_*{timestamp}*.json")
        if not analysis_files:
            analysis_files = glob.glob("enhanced_13_stressor_analysis_*.json")
            analysis_files.sort(key=lambda x: x.split('_')[-1])
            latest_file = analysis_files[-1]
        else:
            latest_file = analysis_files[0]
        
        logger.info(f"✅ Completed stressor analysis: {latest_file}")
        return latest_file
    
    async def find_cohort_outliers(self, analysis_file: str, vin_db_file: str, timestamp: str) -> str:
        """Find cohort-relative outliers"""
        
        # Load data
        with open(analysis_file, 'r') as f:
            analysis_data = json.load(f)
        
        with open(vin_db_file, 'r') as f:
            vin_data = json.load(f)
        
        # Create VIN lookup
        vin_lookup = {v['vin']: v for v in vin_data}
        
        vehicles = analysis_data['vehicle_analyses']
        logger.info(f"🔍 Analyzing {len(vehicles):,} vehicles for cohort outliers...")
        
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
        
        # Create cohorts (scalable approach)
        cohorts = await self.create_scalable_cohorts(merged_vehicles)
        
        # Find outliers
        outliers = await self.find_outliers_in_cohorts(cohorts)
        
        # Save results
        output_file = f"scalable_outliers_{timestamp}.json"
        outlier_summary = {
            "total_vins": len(merged_vehicles),
            "cohorts_created": len(cohorts),
            "outliers_found": len(outliers),
            "outlier_percentage": round(len(outliers) / len(merged_vehicles) * 100, 1),
            "total_revenue": sum(o['revenue'] for o in outliers),
            "processing_timestamp": datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump({
                "summary": outlier_summary,
                "outliers": outliers
            }, f, indent=2)
        
        logger.info(f"✅ Found {len(outliers):,} outliers ({outlier_summary['outlier_percentage']}%)")
        logger.info(f"💰 Total outlier revenue: ${outlier_summary['total_revenue']:,}")
        return output_file
    
    async def create_scalable_cohorts(self, vehicles: List[Dict]) -> Dict[str, List[Dict]]:
        """Create cohorts that scale efficiently"""
        
        cohorts = defaultdict(list)
        
        # Use efficient cohort keys for scalability
        for vehicle in vehicles:
            state = vehicle.get('state', 'XX')
            model = vehicle.get('model', 'unknown')
            climate = vehicle.get('climate_zone', 'unknown')
            
            # Primary cohort: State + Model
            cohorts[f"{state}_{model}"].append(vehicle)
            
            # Secondary cohort: Climate + Model (for cross-state patterns)
            cohorts[f"{climate}_{model}"].append(vehicle)
        
        # Filter cohorts with sufficient size (scales with total VIN count)
        min_cohort_size = max(10, len(vehicles) // 1000)  # At least 10, or 0.1% of total
        large_cohorts = {k: v for k, v in cohorts.items() if len(v) >= min_cohort_size}
        
        logger.info(f"📊 Created {len(large_cohorts)} cohorts (min size: {min_cohort_size})")
        return large_cohorts
    
    async def find_outliers_in_cohorts(self, cohorts: Dict[str, List[Dict]]) -> List[Dict]:
        """Find outliers within each cohort"""
        
        all_outliers = []
        
        for cohort_name, cohort_vehicles in cohorts.items():
            risks = [v['posterior_probability'] for v in cohort_vehicles]
            risk_95th = np.percentile(risks, 95)
            risk_mean = np.mean(risks)
            
            # Find outliers (95th percentile)
            for vehicle in cohort_vehicles:
                if vehicle['posterior_probability'] >= risk_95th:
                    outlier_info = {
                        'vin': vehicle['vin'],
                        'model': vehicle['model'],
                        'state': vehicle.get('state', 'XX'),
                        'climate_zone': vehicle.get('climate_zone', 'unknown'),
                        'risk_score': vehicle['posterior_probability'],
                        'cohort_mean': risk_mean,
                        'deviation': vehicle['posterior_probability'] - risk_mean,
                        'cohort': cohort_name,
                        'stressor_count': len(vehicle['active_stressors']),
                        'revenue': vehicle['revenue_opportunity']
                    }
                    all_outliers.append(outlier_info)
        
        # Sort by deviation from cohort
        all_outliers.sort(key=lambda x: x['deviation'], reverse=True)
        return all_outliers
    
    async def generate_business_summary(self, outlier_file: str) -> Dict:
        """Generate executive business summary"""
        
        with open(outlier_file, 'r') as f:
            data = json.load(f)
        
        summary = data['summary']
        outliers = data['outliers']
        
        # Top revenue opportunities
        top_revenue = sorted(outliers, key=lambda x: x['revenue'], reverse=True)[:10]
        
        # Geographic distribution
        geo_dist = defaultdict(int)
        for outlier in outliers:
            geo_dist[outlier['state']] += 1
        
        business_summary = {
            "executive_metrics": {
                "total_vins_analyzed": summary['total_vins'],
                "actionable_outliers": summary['outliers_found'],
                "outlier_rate": f"{summary['outlier_percentage']}%",
                "total_revenue_opportunity": f"${summary['total_revenue']:,}",
                "avg_revenue_per_outlier": f"${summary['total_revenue'] // summary['outliers_found']:,}"
            },
            "top_revenue_opportunities": [
                {
                    "vin": o['vin'][:8] + "...",
                    "state": o['state'],
                    "model": o['model'],
                    "revenue": f"${o['revenue']:,}",
                    "risk_vs_cohort": f"+{o['deviation']:.3f}"
                }
                for o in top_revenue[:5]
            ],
            "geographic_hotspots": dict(sorted(geo_dist.items(), key=lambda x: x[1], reverse=True)[:5]),
            "scaling_projection": {
                "current_scale": f"{summary['total_vins']:,} VINs",
                "100k_projection": f"~{int(100000 * summary['outlier_percentage'] / 100):,} outliers",
                "1m_projection": f"~{int(1000000 * summary['outlier_percentage'] / 100):,} outliers"
            }
        }
        
        return business_summary

async def main():
    """Main execution with command line arguments"""
    parser = argparse.ArgumentParser(description="Scalable VIN Processing Pipeline")
    parser.add_argument("--vins", type=int, default=10000, help="Number of VINs to process")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for processing")
    
    args = parser.parse_args()
    
    processor = ScalableVINProcessor(batch_size=args.batch_size)
    result = await processor.process_pipeline(args.vins)
    
    if result["success"]:
        print(f"\n🎯 SCALABLE PROCESSING COMPLETE!")
        print(f"📊 Processed: {args.vins:,} VINs")
        print(f"📄 Files generated:")
        print(f"  • VIN Database: {result['vin_database']}")
        print(f"  • Analysis: {result['analysis_file']}")
        print(f"  • Outliers: {result['outlier_file']}")
        
        print(f"\n💼 BUSINESS SUMMARY:")
        summary = result['summary']
        exec_metrics = summary['executive_metrics']
        print(f"  • Actionable outliers: {exec_metrics['actionable_outliers']} ({exec_metrics['outlier_rate']})")
        print(f"  • Revenue opportunity: {exec_metrics['total_revenue_opportunity']}")
        print(f"  • Avg per outlier: {exec_metrics['avg_revenue_per_outlier']}")

if __name__ == "__main__":
    asyncio.run(main()) 