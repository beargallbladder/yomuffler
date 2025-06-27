"""
🧠 MASTER SWARM ORCHESTRATOR 🧠
Privacy-first coordinator of all intelligence workers
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

class MasterSwarmOrchestrator:
    """Coordinates all intelligence workers with privacy compliance"""
    
    def __init__(self, orchestrator_id: str):
        self.orchestrator_id = orchestrator_id
        self.logger = logging.getLogger(f"MasterSwarm-{orchestrator_id}")
        
        # Available intelligence workers
        self.available_stressors = [
            "battery_degradation",
            "weather_environmental", 
            "nhtsa_intelligence",
            "ignition_cycle",
            "predictive_cliff",
            "vin_decoding"
        ]
        
        # Swarm metrics
        self.metrics = {
            "total_analyses": 0,
            "privacy_evaluations": 0,
            "cliff_predictions": 0,
            "privacy_blocks": 0
        }
        
        self.logger.info(f"🚀 Master Swarm Orchestrator {orchestrator_id} - SWARM ACTIVE")
    
    async def comprehensive_analysis(self, vin: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main swarm analysis with privacy protection"""
        
        self.logger.info(f"🧠 SWARM ANALYSIS - VIN: {vin}")
        
        # Initialize report
        report = {
            "vin": vin,
            "timestamp": datetime.now().isoformat(),
            "swarm_status": "PROCESSING",
            "intelligence_sources": [],
            "privacy_compliance": {},
            "predictions": {},
            "recommendations": []
        }
        
        try:
            # Step 1: Privacy evaluation (always first)
            from ..workers.privacy_intelligence_worker import PrivacyIntelligenceWorker
            privacy_worker = PrivacyIntelligenceWorker("privacy_check")
            
            privacy_eval = await privacy_worker.evaluate_stressor_permissions(
                vin, customer_data, self.available_stressors
            )
            
            report["privacy_compliance"] = privacy_eval
            allowed_stressors = privacy_eval.get("allowed_stressors", [])
            
            if not allowed_stressors:
                self.metrics["privacy_blocks"] += 1
                report["swarm_status"] = "PRIVACY_RESTRICTED"
                return report
            
            # Step 2: VIN Decoding (if allowed)
            if "vin_decoding" in allowed_stressors:
                from ..workers.vin_decoder_worker import VINDecoderWorker
                vin_worker = VINDecoderWorker("vin_decode")
                await vin_worker.start()
                
                vin_result = await vin_worker.decode_vin(vin)
                report["vehicle_intelligence"] = vin_result
                report["intelligence_sources"].append("NHTSA_VPIC")
                
                await vin_worker.stop()
            
            # Step 3: Cliff Prediction (if allowed)
            if "predictive_cliff" in allowed_stressors:
                from ..workers.predictive_cliff_worker import PredictiveCliffWorker
                cliff_worker = PredictiveCliffWorker("cliff_predict")
                
                # Prepare basic telemetry data
                telemetry = {
                    "daily_ignition_cycles": 12,
                    "soc_decline_rate": 0.05,
                    "short_trip_percentage": 0.4
                }
                
                vehicle_data = report.get("vehicle_intelligence", {})
                cliff_result = await cliff_worker.analyze_cliff_risk(vin, vehicle_data, telemetry)
                
                report["predictions"]["cliff"] = {
                    "days_to_cliff": cliff_result.days_to_cliff,
                    "cliff_probability": cliff_result.cliff_probability,
                    "recommended_action": cliff_result.recommended_action
                }
                report["intelligence_sources"].append("CLIFF_ANALYTICS")
                self.metrics["cliff_predictions"] += 1
            
            # Step 4: NHTSA Intelligence (if allowed)
            if "nhtsa_intelligence" in allowed_stressors:
                from ..workers.nhtsa_intelligence_worker import NHTSAIntelligenceWorker
                nhtsa_worker = NHTSAIntelligenceWorker("nhtsa_intel")
                await nhtsa_worker.start()
                
                vehicle_data = report.get("vehicle_intelligence", {})
                make = vehicle_data.get("make", "Ford")
                model = vehicle_data.get("model", "F-150")
                year = int(vehicle_data.get("model_year", 2020))
                
                nhtsa_result = await nhtsa_worker.protect_family_vehicle(vin, make, model, year)
                report["government_intelligence"] = nhtsa_result
                report["intelligence_sources"].append("NHTSA_GOVERNMENT")
                
                await nhtsa_worker.stop()
            
            # Generate recommendations
            report["recommendations"] = self._generate_recommendations(report)
            report["swarm_status"] = "COMPLETED"
            
            self.metrics["total_analyses"] += 1
            self.logger.info(f"✅ SWARM ANALYSIS COMPLETE - {len(allowed_stressors)} stressors")
            
            return report
            
        except Exception as e:
            self.logger.error(f"🚨 Swarm error: {str(e)}")
            report["swarm_status"] = "ERROR"
            report["error"] = str(e)
            return report
    
    def _generate_recommendations(self, report: Dict) -> List[Dict[str, Any]]:
        """Generate actionable recommendations from swarm analysis"""
        
        recommendations = []
        
        # Cliff-based recommendations
        cliff_data = report.get("predictions", {}).get("cliff", {})
        if cliff_data.get("days_to_cliff", 365) <= 30:
            recommendations.append({
                "type": "URGENT",
                "title": "Battery Cliff Alert",
                "description": f"Battery failure in {cliff_data.get('days_to_cliff')} days",
                "action": cliff_data.get("recommended_action"),
                "priority": "CRITICAL"
            })
        
        # Government intelligence recommendations
        gov_data = report.get("government_intelligence", {})
        if gov_data.get("protection_status") == "ACTIVE":
            recommendations.append({
                "type": "SAFETY",
                "title": "Government Safety Alert",
                "description": "NHTSA safety concerns detected",
                "action": "Review government recommendations",
                "priority": "HIGH"
            })
        
        return recommendations
    
    async def get_swarm_status(self) -> Dict[str, Any]:
        """Get current swarm status"""
        return {
            "orchestrator_id": self.orchestrator_id,
            "available_stressors": len(self.available_stressors),
            "metrics": self.metrics,
            "status": "OPERATIONAL",
            "last_updated": datetime.now().isoformat()
        }

# Example usage
async def test_master_swarm():
    """Test the master swarm orchestrator"""
    orchestrator = MasterSwarmOrchestrator("swarm_command_1")
    
    try:
        # Test customer data
        customer_data = {
            "zip_code": "33101",
            "state": "FL", 
            "country": "US",
            "mileage": 65000,
            "consent": {
                "telemetry_data": True,
                "location_data": True,
                "predictive_models": True
            }
        }
        
        # Run comprehensive analysis
        swarm_result = await orchestrator.comprehensive_analysis(
            "1FTFW1ET0LFA12345",
            customer_data
        )
        
        print(f"🧠 SWARM ANALYSIS COMPLETE:")
        print(f"Status: {swarm_result['swarm_status']}")
        print(f"Intelligence Sources: {swarm_result['intelligence_sources']}")
        print(f"Recommendations: {len(swarm_result['recommendations'])}")
        
        # Get swarm status
        status = await orchestrator.get_swarm_status()
        print(f"📊 Swarm Status: {status['status']}")
        
    finally:
        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_master_swarm()) 