"""
🔧 VIN DECODER WORKER 🔧
Real-time VIN decoding using NHTSA VPIC API
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

class VINDecoderWorker:
    """
    🎯 VIN DECODING SPECIALIST
    Connects to NHTSA VPIC API for official vehicle information
    """
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.logger = logging.getLogger(f"VINDecoder-{worker_id}")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # NHTSA VPIC API endpoints
        self.vpic_base_url = "https://vpic.nhtsa.dot.gov/api/vehicles"
        self.decode_endpoint = f"{self.vpic_base_url}/DecodeVinValues"
        self.decode_batch_endpoint = f"{self.vpic_base_url}/DecodeVinValuesBatch"
        
        # API configuration
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.retry_attempts = 3
        self.retry_delay = 1
        
        self.logger.info(f"🚀 VIN Decoder Worker {worker_id} initialized")
    
    async def start(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        self.logger.info("🔗 HTTP session initialized")
    
    async def stop(self):
        """Clean shutdown"""
        if self.session:
            await self.session.close()
            self.logger.info("🛑 HTTP session closed")
    
    async def decode_vin(self, vin: str, model_year: Optional[int] = None) -> Dict[str, Any]:
        """
        Decode single VIN using NHTSA VPIC API
        
        Args:
            vin: 17-character VIN
            model_year: Optional model year for validation
            
        Returns:
            Decoded vehicle information
        """
        if not self.session:
            await self.start()
        
        # Validate VIN format
        if not self._validate_vin(vin):
            return {
                "error": "Invalid VIN format",
                "vin": vin,
                "success": False
            }
        
        # Build API URL
        url = f"{self.decode_endpoint}/{vin}"
        params = {"format": "json"}
        if model_year:
            params["modelyear"] = model_year
        
        # Attempt API call with retries
        for attempt in range(self.retry_attempts):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_vpic_response(vin, data)
                    else:
                        self.logger.warning(f"❌ API returned status {response.status} for VIN {vin}")
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"⏰ Timeout on attempt {attempt + 1} for VIN {vin}")
            except Exception as e:
                self.logger.error(f"🚨 Error on attempt {attempt + 1} for VIN {vin}: {str(e)}")
            
            if attempt < self.retry_attempts - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        return {
            "error": "Failed to decode VIN after retries",
            "vin": vin,
            "success": False
        }
    
    async def decode_vin_batch(self, vins: list[str]) -> Dict[str, Any]:
        """
        Decode multiple VINs in batch using NHTSA VPIC API
        
        Args:
            vins: List of VINs to decode (max 50 per batch)
            
        Returns:
            Batch decode results
        """
        if not self.session:
            await self.start()
        
        # Validate batch size
        if len(vins) > 50:
            self.logger.warning(f"⚠️ Batch size {len(vins)} exceeds limit, splitting")
            # Split into smaller batches
            results = {}
            for i in range(0, len(vins), 50):
                batch = vins[i:i+50]
                batch_result = await self.decode_vin_batch(batch)
                results.update(batch_result.get("results", {}))
            return {
                "total_processed": len(vins),
                "results": results,
                "success": True
            }
        
        # Filter valid VINs
        valid_vins = [vin for vin in vins if self._validate_vin(vin)]
        if len(valid_vins) != len(vins):
            self.logger.warning(f"⚠️ {len(vins) - len(valid_vins)} invalid VINs filtered out")
        
        if not valid_vins:
            return {
                "error": "No valid VINs provided",
                "total_processed": 0,
                "success": False
            }
        
        # Prepare batch request data
        batch_data = ";".join(valid_vins)
        post_data = {
            "DATA": batch_data,
            "format": "json"
        }
        
        # Attempt batch API call with retries
        for attempt in range(self.retry_attempts):
            try:
                async with self.session.post(self.decode_batch_endpoint, data=post_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_batch_vpic_response(valid_vins, data)
                    else:
                        self.logger.warning(f"❌ Batch API returned status {response.status}")
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"⏰ Batch timeout on attempt {attempt + 1}")
            except Exception as e:
                self.logger.error(f"🚨 Batch error on attempt {attempt + 1}: {str(e)}")
            
            if attempt < self.retry_attempts - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        return {
            "error": "Failed to decode VIN batch after retries",
            "total_processed": 0,
            "success": False
        }
    
    def _validate_vin(self, vin: str) -> bool:
        """Validate VIN format"""
        if not vin or len(vin) != 17:
            return False
        
        # Remove spaces and convert to uppercase
        vin = vin.replace(" ", "").upper()
        
        # Check for valid characters (no I, O, Q)
        valid_chars = "0123456789ABCDEFGHJKLMNPRSTUVWXYZ"
        if not all(c in valid_chars for c in vin):
            return False
        
        return True
    
    async def _process_vpic_response(self, vin: str, response_data: Dict) -> Dict[str, Any]:
        """Process single VIN VPIC API response"""
        try:
            if "Results" not in response_data or not response_data["Results"]:
                return {
                    "error": "No results from VPIC API",
                    "vin": vin,
                    "success": False
                }
            
            result_data = response_data["Results"][0]
            
            # Extract key vehicle information
            decoded_info = {
                "vin": vin,
                "make": result_data.get("Make", "Unknown"),
                "model": result_data.get("Model", "Unknown"),
                "model_year": result_data.get("ModelYear", "Unknown"),
                "vehicle_type": result_data.get("VehicleType", "Unknown"),
                "body_class": result_data.get("BodyClass", "Unknown"),
                "engine_number_of_cylinders": result_data.get("EngineNumberOfCylinders", "Unknown"),
                "engine_displacement_l": result_data.get("DisplacementL", "Unknown"),
                "engine_displacement_ci": result_data.get("DisplacementCI", "Unknown"),
                "fuel_type_primary": result_data.get("FuelTypePrimary", "Unknown"),
                "manufacturer_name": result_data.get("ManufacturerName", "Unknown"),
                "plant_city": result_data.get("PlantCity", "Unknown"),
                "plant_state": result_data.get("PlantState", "Unknown"),
                "plant_country": result_data.get("PlantCountry", "Unknown"),
                "series": result_data.get("Series", "Unknown"),
                "trim": result_data.get("Trim", "Unknown"),
                "drive_type": result_data.get("DriveType", "Unknown"),
                "transmission_style": result_data.get("TransmissionStyle", "Unknown"),
                "gross_vehicle_weight_rating": result_data.get("GrossVehicleWeightRating", "Unknown"),
                "error_code": result_data.get("ErrorCode", "0"),
                "error_text": result_data.get("ErrorText", ""),
                "decoded_at": datetime.now().isoformat(),
                "source": "NHTSA_VPIC",
                "success": True
            }
            
            # Add battery/electrical system intelligence
            decoded_info["battery_intelligence"] = await self._extract_battery_intelligence(decoded_info)
            
            # Add stressor analysis context
            decoded_info["stressor_context"] = await self._analyze_stressor_context(decoded_info)
            
            self.logger.info(f"✅ Successfully decoded VIN {vin} - {decoded_info['make']} {decoded_info['model']} {decoded_info['model_year']}")
            
            return decoded_info
            
        except Exception as e:
            self.logger.error(f"🚨 Error processing VPIC response for VIN {vin}: {str(e)}")
            return {
                "error": f"Processing error: {str(e)}",
                "vin": vin,
                "success": False
            }
    
    async def _process_batch_vpic_response(self, vins: list[str], response_data: Dict) -> Dict[str, Any]:
        """Process batch VIN VPIC API response"""
        try:
            if "Results" not in response_data:
                return {
                    "error": "No results from batch VPIC API",
                    "total_processed": 0,
                    "success": False
                }
            
            results = {}
            processed_count = 0
            
            for result_data in response_data["Results"]:
                vin = result_data.get("VIN", "").upper()
                if vin:
                    # Process each VIN result
                    mock_response = {"Results": [result_data]}
                    decoded = await self._process_vpic_response(vin, mock_response)
                    results[vin] = decoded
                    processed_count += 1
            
            self.logger.info(f"✅ Successfully processed batch of {processed_count} VINs")
            
            return {
                "total_processed": processed_count,
                "results": results,
                "processed_at": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"🚨 Error processing batch VPIC response: {str(e)}")
            return {
                "error": f"Batch processing error: {str(e)}",
                "total_processed": 0,
                "success": False
            }
    
    async def _extract_battery_intelligence(self, vehicle_info: Dict) -> Dict[str, Any]:
        """Extract battery/electrical system intelligence from vehicle data"""
        battery_intel = {
            "estimated_battery_type": "Lead Acid 12V",  # Standard default
            "electrical_system_voltage": 12,
            "alternator_rating": "Unknown",
            "cold_cranking_amps_estimate": "Unknown",
            "battery_group_size": "Unknown"
        }
        
        # Vehicle-specific battery intelligence
        make = vehicle_info.get("make", "").upper()
        model = vehicle_info.get("model", "").upper()
        year = vehicle_info.get("model_year", "")
        
        try:
            year_int = int(year) if year.isdigit() else 0
            
            # Heavy duty vehicles typically need higher CCA
            if any(truck in model for truck in ["F-250", "F-350", "F-450", "SUPER DUTY"]):
                battery_intel.update({
                    "estimated_battery_type": "Heavy Duty Lead Acid 12V",
                    "cold_cranking_amps_estimate": "750-850",
                    "battery_group_size": "Group 65 or 78",
                    "alternator_rating": "157-220A"
                })
            
            # Light trucks
            elif any(truck in model for truck in ["F-150", "RANGER", "MAVERICK"]):
                battery_intel.update({
                    "estimated_battery_type": "Standard Lead Acid 12V",
                    "cold_cranking_amps_estimate": "590-750",
                    "battery_group_size": "Group 65 or 48",
                    "alternator_rating": "130-157A"
                })
            
            # SUVs
            elif any(suv in model for suv in ["EXPLORER", "EXPEDITION", "BRONCO", "ESCAPE"]):
                battery_intel.update({
                    "estimated_battery_type": "Standard Lead Acid 12V",
                    "cold_cranking_amps_estimate": "650-750",
                    "battery_group_size": "Group 65",
                    "alternator_rating": "130-157A"
                })
            
            # Hybrid vehicles (if detected)
            fuel_type = vehicle_info.get("fuel_type_primary", "").upper()
            if "HYBRID" in fuel_type or "ELECTRIC" in fuel_type:
                battery_intel.update({
                    "estimated_battery_type": "AGM 12V + High Voltage",
                    "electrical_system_voltage": "12V/300V+",
                    "cold_cranking_amps_estimate": "590-650",
                    "special_requirements": "Hybrid battery system"
                })
            
            # Performance vehicles typically need higher CCA
            if any(perf in model for perf in ["MUSTANG", "GT", "SHELBY"]):
                battery_intel.update({
                    "estimated_battery_type": "Performance Lead Acid 12V",
                    "cold_cranking_amps_estimate": "650-750",
                    "battery_group_size": "Group 96R",
                    "alternator_rating": "130-200A"
                })
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error in battery intelligence extraction: {str(e)}")
        
        return battery_intel
    
    async def _analyze_stressor_context(self, vehicle_info: Dict) -> Dict[str, Any]:
        """Analyze vehicle characteristics for stressor vulnerability"""
        stressor_context = {
            "cold_weather_vulnerability": "medium",
            "hot_weather_vulnerability": "medium", 
            "high_mileage_vulnerability": "medium",
            "commercial_use_likelihood": "low",
            "urban_driving_impact": "medium",
            "stressor_notes": []
        }
        
        try:
            make = vehicle_info.get("make", "").upper()
            model = vehicle_info.get("model", "").upper() 
            year = vehicle_info.get("model_year", "")
            body_class = vehicle_info.get("body_class", "").upper()
            
            year_int = int(year) if year.isdigit() else 0
            vehicle_age = datetime.now().year - year_int if year_int > 0 else 0
            
            # Heavy duty vehicles - higher commercial use, higher stress
            if any(truck in model for truck in ["F-250", "F-350", "F-450", "SUPER DUTY"]):
                stressor_context.update({
                    "cold_weather_vulnerability": "high",
                    "commercial_use_likelihood": "high",
                    "high_mileage_vulnerability": "high"
                })
                stressor_context["stressor_notes"].append("Heavy duty vehicle - increased electrical load")
            
            # Light trucks - moderate stress patterns
            elif any(truck in model for truck in ["F-150", "RANGER"]):
                stressor_context.update({
                    "cold_weather_vulnerability": "high",
                    "commercial_use_likelihood": "medium"
                })
                stressor_context["stressor_notes"].append("Light truck - cold weather vulnerable")
            
            # SUVs - family use patterns
            elif any(suv in model for suv in ["EXPLORER", "EXPEDITION", "BRONCO"]):
                stressor_context.update({
                    "urban_driving_impact": "high",
                    "commercial_use_likelihood": "low"
                })
                stressor_context["stressor_notes"].append("SUV - stop-start driving patterns")
            
            # Compact vehicles - urban stress
            elif any(compact in model for compact in ["ESCAPE", "FOCUS", "FIESTA"]):
                stressor_context.update({
                    "urban_driving_impact": "high",
                    "hot_weather_vulnerability": "high"
                })
                stressor_context["stressor_notes"].append("Compact vehicle - urban heat stress")
            
            # Age-based vulnerability
            if vehicle_age >= 3:
                stressor_context["high_mileage_vulnerability"] = "high"
                stressor_context["stressor_notes"].append(f"Vehicle age {vehicle_age} years - increased failure risk")
            
            # Body class insights
            if "PICKUP" in body_class or "TRUCK" in body_class:
                stressor_context["commercial_use_likelihood"] = "high"
                stressor_context["stressor_notes"].append("Pickup truck configuration")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error in stressor context analysis: {str(e)}")
        
        return stressor_context
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """Get current worker status"""
        return {
            "worker_id": self.worker_id,
            "worker_type": "vin_decoder",
            "session_active": self.session is not None,
            "api_endpoint": self.vpic_base_url,
            "status": "ready" if self.session else "not_initialized",
            "last_updated": datetime.now().isoformat()
        }

# Example usage
async def test_vin_decoder():
    """Test the VIN decoder worker"""
    worker = VINDecoderWorker("test_worker_1")
    
    try:
        await worker.start()
        
        # Test single VIN decode
        test_vin = "1FTFW1ET0LFA12345"  # Example F-150 VIN format
        result = await worker.decode_vin(test_vin)
        print(f"🔧 Single VIN decode result: {json.dumps(result, indent=2)}")
        
        # Test batch decode
        test_vins = [
            "1FTFW1ET0LFA12345",  # F-150
            "1FMHK8D83LGA89012",  # Explorer  
            "3FA6P0HR8LR345678"   # Fusion
        ]
        batch_result = await worker.decode_vin_batch(test_vins)
        print(f"🔧 Batch VIN decode result: {json.dumps(batch_result, indent=2)}")
        
        # Worker status
        status = await worker.get_worker_status()
        print(f"📊 Worker status: {json.dumps(status, indent=2)}")
        
    finally:
        await worker.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_vin_decoder()) 