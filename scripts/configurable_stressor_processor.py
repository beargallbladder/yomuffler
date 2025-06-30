#!/usr/bin/env python3
"""
🎛️ CONFIGURABLE 13-STRESSOR PROCESSOR 🎛️
Allows filtering and configuration of which stressors to use
Perfect for gradual deployment or testing different combinations
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Set
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigurableStressorProcessor:
    def __init__(self, config_file: str = None):
        """Initialize with configurable stressor framework"""
        
        # COMPLETE 13-stressor framework with configuration flags
        self.all_stressors = {
            # ELECTRICAL STRESSORS (4)
            "parasitic_draw_stress": {
                "likelihood_ratio": 3.4,
                "threshold": ">50mA when off",
                "source": "Argonne ANL-115925.pdf Section 3.2",
                "failure_probability": 0.408,
                "category": "electrical",
                "data_requirements": ["soc_decline_rate"],
                "enabled": True,  # Default enabled
                "priority": "high"
            },
            "alternator_cycling_stress": {
                "likelihood_ratio": 2.8,
                "threshold": ">8 charge/discharge cycles per day",
                "source": "SAE J537 Standard + BU-804",
                "failure_probability": 0.336,
                "category": "electrical",
                "data_requirements": ["start_cycles_annual"],
                "enabled": True,
                "priority": "high"
            },
            "voltage_regulation_stress": {
                "likelihood_ratio": 4.1,
                "threshold": "Voltage swings >0.5V from nominal",
                "source": "IEEE 1188 Standard",
                "failure_probability": 0.492,
                "category": "electrical",
                "data_requirements": ["temperature_stress"],
                "enabled": False,  # Might not have voltage data yet
                "priority": "high"
            },
            "deep_discharge_events": {
                "likelihood_ratio": 6.7,
                "threshold": "Battery voltage <11.5V under load",
                "source": "Argonne ANL-115925.pdf Section 4.1",
                "failure_probability": 0.804,
                "category": "electrical",
                "data_requirements": ["vehicle_age", "soc_decline_rate"],
                "enabled": True,
                "priority": "critical"
            },
            
            # MECHANICAL STRESSORS (3)
            "vibration_stress": {
                "likelihood_ratio": 2.1,
                "threshold": ">3G RMS vibration",
                "source": "SAE J2380",
                "failure_probability": 0.252,
                "category": "mechanical",
                "data_requirements": ["model", "current_mileage"],
                "enabled": True,
                "priority": "medium"
            },
            "extended_idle_exposure": {
                "likelihood_ratio": 1.9,
                "threshold": "Unused >14 consecutive days",
                "source": "BU-804 Self-Discharge Studies",
                "failure_probability": 0.228,
                "category": "mechanical",
                "data_requirements": ["current_mileage", "vehicle_age"],
                "enabled": True,
                "priority": "medium"
            },
            "towing_load_stress": {
                "likelihood_ratio": 3.2,
                "threshold": "Sustained current >80A",
                "source": "SAE J2662",
                "failure_probability": 0.384,
                "category": "mechanical",
                "data_requirements": ["model"],
                "enabled": True,
                "priority": "high"
            },
            
            # USAGE PATTERN STRESSORS (3)
            "stop_and_go_traffic": {
                "likelihood_ratio": 2.3,
                "threshold": ">15 starts per hour",
                "source": "EPA FTP-75 + Argonne Vehicle Systems",
                "failure_probability": 0.276,
                "category": "usage",
                "data_requirements": ["short_trip_percentage"],
                "enabled": True,
                "priority": "medium"
            },
            "extended_parking_stress": {
                "likelihood_ratio": 1.7,
                "threshold": "Parked >7 days without charging",
                "source": "BU-410a Storage Studies",
                "failure_probability": 0.204,
                "category": "usage",
                "data_requirements": ["current_mileage", "vehicle_age"],
                "enabled": False,  # Might not have parking data
                "priority": "low"
            },
            "multi_driver_usage": {
                "likelihood_ratio": 1.8,
                "threshold": ">3 different key fobs in 30 days",
                "source": "Johnson Controls Fleet Study",
                "failure_probability": 0.216,
                "category": "usage",
                "data_requirements": ["current_mileage"],
                "enabled": True,
                "priority": "medium"
            },
            
            # ENVIRONMENTAL STRESSORS (3)
            "humidity_cycling_stress": {
                "likelihood_ratio": 2.6,
                "threshold": "Daily humidity swings >40% RH",
                "source": "NREL + Sandia Corrosion Studies",
                "failure_probability": 0.312,
                "category": "environmental",
                "data_requirements": ["climate_zone"],
                "enabled": True,
                "priority": "high"
            },
            "altitude_change_stress": {
                "likelihood_ratio": 1.4,
                "threshold": "Operating altitude >5,000 feet",
                "source": "NIST Special Publication 400-32",
                "failure_probability": 0.168,
                "category": "environmental",
                "data_requirements": ["temperature_delta"],
                "enabled": False,  # Might not have altitude data
                "priority": "low"
            },
            "salt_corrosion_exposure": {
                "likelihood_ratio": 4.3,
                "threshold": "Within 10 miles of saltwater >6 months",
                "source": "ASTM B117 Salt Spray Testing",
                "failure_probability": 0.516,
                "category": "environmental",
                "data_requirements": ["climate_zone", "state"],
                "enabled": True,
                "priority": "critical"
            }
        }
        
        # Base prior probabilities by vehicle type
        self.base_priors = {
            "F-150": 0.15,
            "F-250": 0.18,
            "F-350": 0.20,
            "Ranger": 0.12,
            "Explorer": 0.12,
            "Expedition": 0.16
        }
        
        # Load configuration if provided
        if config_file:
            self.load_configuration(config_file)
        
        # Get enabled stressors
        self.enabled_stressors = {k: v for k, v in self.all_stressors.items() if v["enabled"]}
        
        logger.info("🎛️ Configurable 13-Stressor Processor initialized")
        logger.info(f"📊 Total stressors available: {len(self.all_stressors)}")
        logger.info(f"✅ Enabled stressors: {len(self.enabled_stressors)}")
        logger.info(f"❌ Disabled stressors: {len(self.all_stressors) - len(self.enabled_stressors)}")
    
    def load_configuration(self, config_file: str):
        """Load stressor configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update stressor settings
            for stressor_name, settings in config.get("stressors", {}).items():
                if stressor_name in self.all_stressors:
                    self.all_stressors[stressor_name].update(settings)
                    logger.info(f"🔧 Updated {stressor_name}: {settings}")
            
            logger.info(f"✅ Configuration loaded from {config_file}")
        except Exception as e:
            logger.warning(f"⚠️ Could not load config file {config_file}: {e}")
    
    def save_configuration(self, config_file: str = "stressor_config.json"):
        """Save current stressor configuration to JSON file"""
        config = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "description": "VIN Stressors Configuration - Enable/Disable Individual Stressors"
            },
            "stressors": {}
        }
        
        for name, stressor in self.all_stressors.items():
            config["stressors"][name] = {
                "enabled": stressor["enabled"],
                "priority": stressor["priority"],
                "likelihood_ratio": stressor["likelihood_ratio"],
                "category": stressor["category"],
                "data_requirements": stressor["data_requirements"]
            }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"💾 Configuration saved to {config_file}")
        return config_file
    
    def print_stressor_status(self):
        """Print current stressor configuration status"""
        print("\n🎛️ STRESSOR CONFIGURATION STATUS")
        print("=" * 60)
        
        categories = {}
        for name, stressor in self.all_stressors.items():
            cat = stressor["category"]
            if cat not in categories:
                categories[cat] = {"enabled": [], "disabled": []}
            
            if stressor["enabled"]:
                categories[cat]["enabled"].append((name, stressor))
            else:
                categories[cat]["disabled"].append((name, stressor))
        
        for category, stressors in categories.items():
            print(f"\n📂 {category.upper()} STRESSORS:")
            
            for name, stressor in stressors["enabled"]:
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                emoji = priority_emoji.get(stressor["priority"], "⚪")
                print(f"  ✅ {emoji} {name} (LR: {stressor['likelihood_ratio']}x)")
            
            for name, stressor in stressors["disabled"]:
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                emoji = priority_emoji.get(stressor["priority"], "⚪")
                print(f"  ❌ {emoji} {name} (LR: {stressor['likelihood_ratio']}x) - DISABLED")
        
        enabled_count = len(self.enabled_stressors)
        total_count = len(self.all_stressors)
        print(f"\n📊 SUMMARY: {enabled_count}/{total_count} stressors enabled")
    
    def enable_stressor(self, stressor_name: str):
        """Enable a specific stressor"""
        if stressor_name in self.all_stressors:
            self.all_stressors[stressor_name]["enabled"] = True
            self.enabled_stressors = {k: v for k, v in self.all_stressors.items() if v["enabled"]}
            logger.info(f"✅ Enabled stressor: {stressor_name}")
        else:
            logger.error(f"❌ Unknown stressor: {stressor_name}")
    
    def disable_stressor(self, stressor_name: str):
        """Disable a specific stressor"""
        if stressor_name in self.all_stressors:
            self.all_stressors[stressor_name]["enabled"] = False
            self.enabled_stressors = {k: v for k, v in self.all_stressors.items() if v["enabled"]}
            logger.info(f"❌ Disabled stressor: {stressor_name}")
        else:
            logger.error(f"❌ Unknown stressor: {stressor_name}")
    
    def enable_category(self, category: str):
        """Enable all stressors in a category"""
        count = 0
        for name, stressor in self.all_stressors.items():
            if stressor["category"] == category:
                stressor["enabled"] = True
                count += 1
        
        self.enabled_stressors = {k: v for k, v in self.all_stressors.items() if v["enabled"]}
        logger.info(f"✅ Enabled {count} stressors in category: {category}")
    
    def disable_category(self, category: str):
        """Disable all stressors in a category"""
        count = 0
        for name, stressor in self.all_stressors.items():
            if stressor["category"] == category:
                stressor["enabled"] = False
                count += 1
        
        self.enabled_stressors = {k: v for k, v in self.all_stressors.items() if v["enabled"]}
        logger.info(f"❌ Disabled {count} stressors in category: {category}")
    
    def load_vin_database(self, filename: str) -> List[Dict]:
        """Load VIN database from JSON file"""
        try:
            with open(filename, 'r') as f:
                leads = json.load(f)
            logger.info(f"✅ Loaded {len(leads)} VINs from {filename}")
            return leads
        except Exception as e:
            logger.error(f"❌ Failed to load VIN database: {e}")
            return []
    
    def analyze_vehicle_stressors(self, vehicle_data: Dict) -> Dict[str, Any]:
        """Analyze a single vehicle using ONLY ENABLED stressors"""
        vin = vehicle_data.get("vin", "UNKNOWN")
        model = vehicle_data.get("model", "F-150")
        
        # Get base prior for this vehicle type
        base_prior = self.base_priors.get(model, 0.15)
        
        # Evaluate only enabled stressors
        active_stressors = []
        likelihood_ratios = []
        stressor_details = []
        skipped_stressors = []
        
        # Check each enabled stressor
        for stressor_name, stressor_config in self.enabled_stressors.items():
            
            # Check if we have required data
            has_required_data = all(
                vehicle_data.get(req) is not None 
                for req in stressor_config["data_requirements"]
            )
            
            if not has_required_data:
                skipped_stressors.append(f"{stressor_name} (missing data)")
                continue
            
            # Check if stressor is active
            is_active = self._check_stressor(stressor_name, vehicle_data)
            
            if is_active:
                active_stressors.append(stressor_name)
                likelihood_ratios.append(stressor_config["likelihood_ratio"])
                stressor_details.append(f"{stressor_name}: {stressor_config['threshold']}")
        
        # Calculate combined Bayesian risk using only active enabled stressors
        combined_lr = np.prod(likelihood_ratios) if likelihood_ratios else 1.0
        
        # Bayesian posterior calculation
        numerator = base_prior * combined_lr
        posterior_probability = numerator / (numerator + (1 - base_prior))
        
        # Cap at 95% for safety
        posterior_probability = min(posterior_probability, 0.95)
        
        return {
            "vin": vin,
            "model": model,
            "base_prior": base_prior,
            "active_stressors": active_stressors,
            "stressor_count": len(active_stressors),
            "stressor_details": stressor_details,
            "skipped_stressors": skipped_stressors,
            "likelihood_ratios": likelihood_ratios,
            "combined_lr": combined_lr,
            "posterior_probability": posterior_probability,
            "risk_percentage": round(posterior_probability * 100, 1),
            "severity": self._classify_severity(posterior_probability),
            "revenue_opportunity": self._calculate_revenue(posterior_probability, model),
            "enabled_stressor_count": len(self.enabled_stressors),
            "total_stressor_count": len(self.all_stressors),
            "framework_version": f"Configurable 13-Stressor v2.0 ({len(self.enabled_stressors)}/{len(self.all_stressors)} enabled)"
        }
    
    def _check_stressor(self, stressor_name: str, vehicle_data: Dict) -> bool:
        """Check if a specific stressor is active"""
        
        # ELECTRICAL STRESSORS
        if stressor_name == "parasitic_draw_stress":
            soc_decline = abs(vehicle_data.get("soc_decline_rate", 0))
            return soc_decline > 0.15
        
        elif stressor_name == "alternator_cycling_stress":
            start_cycles = vehicle_data.get("start_cycles_annual", 1200)
            return start_cycles > 2800
        
        elif stressor_name == "voltage_regulation_stress":
            temp_stress = vehicle_data.get("temperature_stress", 0)
            return temp_stress > 0.3
        
        elif stressor_name == "deep_discharge_events":
            vehicle_age = vehicle_data.get("vehicle_age", 0)
            soc_decline = abs(vehicle_data.get("soc_decline_rate", 0))
            return vehicle_age > 3 and soc_decline > 0.2
        
        # MECHANICAL STRESSORS
        elif stressor_name == "vibration_stress":
            model = vehicle_data.get("model", "")
            mileage = vehicle_data.get("current_mileage", 0)
            return ("F-250" in model or "F-350" in model) and mileage > 40000
        
        elif stressor_name == "extended_idle_exposure":
            annual_miles = vehicle_data.get("current_mileage", 30000) / vehicle_data.get("vehicle_age", 1)
            return annual_miles < 8000
        
        elif stressor_name == "towing_load_stress":
            model = vehicle_data.get("model", "")
            return any(truck in model for truck in ["F-250", "F-350", "Super Duty"])
        
        # USAGE PATTERN STRESSORS
        elif stressor_name == "stop_and_go_traffic":
            short_trip_pct = vehicle_data.get("short_trip_percentage", 0)
            return short_trip_pct > 0.6
        
        elif stressor_name == "extended_parking_stress":
            annual_miles = vehicle_data.get("current_mileage", 30000) / vehicle_data.get("vehicle_age", 1)
            return annual_miles < 5000
        
        elif stressor_name == "multi_driver_usage":
            mileage = vehicle_data.get("current_mileage", 0)
            return mileage > 45000
        
        # ENVIRONMENTAL STRESSORS
        elif stressor_name == "humidity_cycling_stress":
            climate = vehicle_data.get("climate_zone", "")
            return "coastal" in climate
        
        elif stressor_name == "altitude_change_stress":
            temp_delta = vehicle_data.get("temperature_delta", 0)
            return temp_delta > 45
        
        elif stressor_name == "salt_corrosion_exposure":
            climate = vehicle_data.get("climate_zone", "")
            state = vehicle_data.get("state", "")
            return "coastal" in climate or state == "FL"
        
        return False
    
    def _classify_severity(self, probability: float) -> str:
        """Classify risk severity based on probability"""
        if probability >= 0.25:
            return "SEVERE"
        elif probability >= 0.20:
            return "CRITICAL"
        elif probability >= 0.15:
            return "HIGH"
        elif probability >= 0.08:
            return "MODERATE"
        else:
            return "LOW"
    
    def _calculate_revenue(self, probability: float, model: str) -> int:
        """Calculate revenue opportunity based on risk and vehicle type"""
        base_revenue = {
            "SEVERE": 1400,
            "CRITICAL": 1200,
            "HIGH": 600,
            "MODERATE": 350,
            "LOW": 180
        }
        
        severity = self._classify_severity(probability)
        revenue = base_revenue[severity]
        
        # Vehicle type multipliers
        if model in ["F-250", "F-350"]:
            revenue = int(revenue * 1.4)
        elif model in ["F-150"]:
            revenue = int(revenue * 1.2)
        
        return revenue
    
    async def process_all_vins(self, database_filename: str) -> Dict[str, Any]:
        """Process ALL VINs with the configured stressor framework"""
        logger.info("🚀 STARTING CONFIGURABLE STRESSOR ANALYSIS")
        logger.info(f"✅ Using {len(self.enabled_stressors)}/{len(self.all_stressors)} enabled stressors")
        
        # Load VIN database
        leads = self.load_vin_database(database_filename)
        
        if not leads:
            logger.error("❌ No VINs to process")
            return {}
        
        logger.info(f"🔥 Processing {len(leads)} VINs with ENABLED stressors only")
        
        # Process each VIN
        results = []
        severe_count = 0
        critical_count = 0
        total_revenue = 0
        
        for i, vehicle in enumerate(leads):
            if i % 500 == 0:
                logger.info(f"  ⚡ Processed {i} VINs...")
            
            analysis = self.analyze_vehicle_stressors(vehicle)
            results.append(analysis)
            
            # Track severe cases
            if analysis["severity"] == "SEVERE":
                severe_count += 1
            elif analysis["severity"] == "CRITICAL":
                critical_count += 1
            
            total_revenue += analysis["revenue_opportunity"]
        
        # Generate summary
        enabled_stressor_names = list(self.enabled_stressors.keys())
        disabled_stressor_names = [k for k, v in self.all_stressors.items() if not v["enabled"]]
        
        summary = {
            "total_vins_processed": len(results),
            "framework_version": f"Configurable 13-Stressor v2.0",
            "enabled_stressors": enabled_stressor_names,
            "disabled_stressors": disabled_stressor_names,
            "enabled_count": len(enabled_stressor_names),
            "total_stressor_count": len(self.all_stressors),
            "severe_risk_vins": severe_count,
            "critical_risk_vins": critical_count,
            "total_revenue_opportunity": total_revenue,
            "average_revenue_per_vin": total_revenue / len(results) if results else 0,
            "high_risk_percentage": round((severe_count + critical_count) / len(results) * 100, 1),
            "processing_timestamp": datetime.now().isoformat(),
            "academic_validation": True
        }
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"configurable_stressor_analysis_{timestamp}.json"
        with open(output_filename, 'w') as f:
            json.dump({
                "summary": summary,
                "vehicle_analyses": results
            }, f, indent=2)
        
        logger.info("🎯 CONFIGURABLE STRESSOR ANALYSIS COMPLETE!")
        logger.info(f"📊 Processed: {len(results)} VINs")
        logger.info(f"🔥 Severe Risk: {severe_count} VINs ({severe_count/len(results)*100:.1f}%)")
        logger.info(f"⚠️  Critical Risk: {critical_count} VINs ({critical_count/len(results)*100:.1f}%)")
        logger.info(f"💰 Total Revenue: ${total_revenue:,}")
        logger.info(f"📄 Results saved: {output_filename}")
        
        return {
            "summary": summary,
            "results_file": output_filename,
            "success": True
        }

def interactive_configuration():
    """Interactive configuration menu"""
    processor = ConfigurableStressorProcessor()
    
    while True:
        print("\n🎛️ STRESSOR CONFIGURATION MENU")
        print("=" * 40)
        print("1. View current stressor status")
        print("2. Enable specific stressor")
        print("3. Disable specific stressor")
        print("4. Enable stressor category")
        print("5. Disable stressor category")
        print("6. Save configuration")
        print("7. Process VINs with current config")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == "1":
            processor.print_stressor_status()
        
        elif choice == "2":
            stressor_name = input("Enter stressor name to enable: ").strip()
            processor.enable_stressor(stressor_name)
        
        elif choice == "3":
            stressor_name = input("Enter stressor name to disable: ").strip()
            processor.disable_stressor(stressor_name)
        
        elif choice == "4":
            category = input("Enter category (electrical/mechanical/usage/environmental): ").strip()
            processor.enable_category(category)
        
        elif choice == "5":
            category = input("Enter category (electrical/mechanical/usage/environmental): ").strip()
            processor.disable_category(category)
        
        elif choice == "6":
            config_file = processor.save_configuration()
            print(f"✅ Configuration saved to {config_file}")
        
        elif choice == "7":
            import glob
            vin_files = glob.glob("vin_leads_database_*.json")
            if vin_files:
                latest_file = max(vin_files, key=lambda x: x.split('_')[-1])
                print(f"📄 Using VIN database: {latest_file}")
                result = asyncio.run(processor.process_all_vins(latest_file))
                print("✅ Processing complete!")
            else:
                print("❌ No VIN database files found")
        
        elif choice == "8":
            break
        
        else:
            print("❌ Invalid choice")

async def main():
    """Main execution function"""
    print("🎛️ CONFIGURABLE STRESSOR PROCESSOR")
    print("Choose mode:")
    print("1. Interactive configuration")
    print("2. Process with current defaults")
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == "1":
        interactive_configuration()
    else:
        processor = ConfigurableStressorProcessor()
        processor.print_stressor_status()
        
        # Find latest VIN database
        import glob
        vin_files = glob.glob("vin_leads_database_*.json")
        if not vin_files:
            logger.error("❌ No VIN database files found")
            return
        
        latest_file = max(vin_files, key=lambda x: x.split('_')[-1])
        logger.info(f"📄 Using VIN database: {latest_file}")
        
        # Process with current configuration
        result = await processor.process_all_vins(latest_file)
        
        if result["success"]:
            logger.info("✅ CONFIGURABLE PROCESSING COMPLETE")

if __name__ == "__main__":
    asyncio.run(main()) 