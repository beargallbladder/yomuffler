"""
🚨 NHTSA INTELLIGENCE WORKER 🚨
Real-time government data integration for recalls, complaints, and TSBs
MISSION: Protect Ford families through government intelligence
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from urllib.parse import urlencode

class NHTSAIntelligenceWorker:
    """
    🎯 GOVERNMENT INTELLIGENCE SPECIALIST
    Connects to NHTSA APIs for recalls, complaints, and technical service bulletins
    MISSION: Early warning system for Ford family protection
    """
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.logger = logging.getLogger(f"NHTSAIntel-{worker_id}")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # NHTSA API endpoints
        self.nhtsa_base_url = "https://api.nhtsa.gov"
        self.recalls_endpoint = f"{self.nhtsa_base_url}/recalls/recallsByVehicle"
        self.complaints_endpoint = f"{self.nhtsa_base_url}/complaints/complaintsByVehicle" 
        self.tsb_endpoint = f"{self.nhtsa_base_url}/TSBs/TSBByVehicle"
        self.investigations_endpoint = f"{self.nhtsa_base_url}/investigations/investigationsByVehicle"
        
        # Alternative endpoints (backup)
        self.vpic_recall_endpoint = "https://vpic.nhtsa.dot.gov/api/vehicles/GetRecallsByVehicle"
        
        # API configuration
        self.timeout = aiohttp.ClientTimeout(total=45)
        self.retry_attempts = 3
        self.retry_delay = 2
        self.rate_limit_delay = 1  # Respect NHTSA rate limits
        
        # Cache for recently fetched data
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        self.logger.info(f"🚀 NHTSA Intelligence Worker {worker_id} initialized - READY TO PROTECT FAMILIES")
    
    async def start(self):
        """Initialize HTTP session with proper headers"""
        headers = {
            'User-Agent': 'Ford-VIN-Stressors-Platform/1.0 (Family Protection System)',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        }
        
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=headers
        )
        self.logger.info("🔗 NHTSA Intelligence session initialized - FAMILY PROTECTION ACTIVE")
    
    async def stop(self):
        """Clean shutdown"""
        if self.session:
            await self.session.close()
            self.logger.info("🛑 NHTSA Intelligence session closed")
    
    async def protect_family_vehicle(self, vin: str, make: str, model: str, model_year: int) -> Dict[str, Any]:
        """
        FAMILY PROTECTION MODE - Complete intelligence for one VIN
        
        Args:
            vin: Vehicle VIN (the family's vehicle)
            make: Vehicle make
            model: Vehicle model  
            model_year: Model year
            
        Returns:
            Complete family protection intelligence report
        """
        self.logger.info(f"🛡️ FAMILY PROTECTION ACTIVATED - VIN: {vin} ({make} {model} {model_year})")
        
        family_protection_report = {
            "family_vehicle": {
                "vin": vin,
                "make": make,
                "model": model,
                "model_year": model_year
            },
            "protection_status": "ACTIVE",
            "threat_assessment": {},
            "immediate_actions": [],
            "recommendations": [],
            "generated_at": datetime.now().isoformat()
        }
        
        try:
            # Deploy all intelligence workers for this family
            protection_tasks = [
                self.get_family_recalls(vin, make, model, model_year),
                self.get_family_safety_complaints(make, model, model_year),
                self.get_family_technical_bulletins(make, model, model_year),
                self.get_family_investigations(make, model, model_year)
            ]
            
            results = await asyncio.gather(*protection_tasks, return_exceptions=True)
            
            family_protection_report.update({
                "recall_intelligence": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "safety_complaints": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
                "technical_bulletins": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
                "safety_investigations": results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])}
            })
            
            # Generate family threat assessment
            threat_assessment = await self._assess_family_threats(family_protection_report)
            family_protection_report["threat_assessment"] = threat_assessment
            
            # Generate immediate protective actions
            immediate_actions = await self._generate_immediate_actions(threat_assessment)
            family_protection_report["immediate_actions"] = immediate_actions
            
            # Generate family recommendations
            recommendations = await self._generate_family_recommendations(family_protection_report)
            family_protection_report["recommendations"] = recommendations
            
            self.logger.info(f"✅ FAMILY PROTECTION COMPLETE - Threat Level: {threat_assessment.get('threat_level', 'UNKNOWN')}")
            
            return family_protection_report
            
        except Exception as e:
            self.logger.error(f"🚨 FAMILY PROTECTION ERROR for VIN {vin}: {str(e)}")
            family_protection_report.update({
                "protection_status": "ERROR",
                "error": str(e)
            })
            return family_protection_report
    
    async def get_family_recalls(self, vin: str, make: str, model: str, model_year: int) -> Dict[str, Any]:
        """Get recall intelligence for family vehicle"""
        if not self.session:
            await self.start()
        
        cache_key = f"family_recalls_{vin}"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.logger.info(f"📦 Cache hit for family recalls: {vin}")
            return cached_result
        
        # Build API request
        params = {
            'make': make.upper(),
            'model': model.upper(),
            'modelYear': model_year
        }
        
        recall_data = await self._fetch_nhtsa_data(self.recalls_endpoint, params, "family_recalls")
        
        if recall_data.get("success"):
            # Process recalls with family protection focus
            family_recalls = await self._process_family_recalls(recall_data, vin, make, model, model_year)
            self._cache_result(cache_key, family_recalls)
            return family_recalls
        
        # Fallback to VPIC API
        return await self._get_recalls_fallback(make, model, model_year, vin)
    
    async def get_family_safety_complaints(self, make: str, model: str, model_year: int) -> Dict[str, Any]:
        """Get safety complaints that could affect this family"""
        if not self.session:
            await self.start()
        
        cache_key = f"family_complaints_{make}_{model}_{model_year}"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        # Focus on safety-critical complaints
        safety_components = [
            "ELECTRICAL SYSTEM",
            "ENGINE",
            "POWER TRAIN",
            "FUEL SYSTEM",
            "BRAKES"
        ]
        
        complaint_tasks = []
        for component in safety_components:
            params = {
                'make': make.upper(),
                'model': model.upper(),
                'modelYear': model_year,
                'component': component
            }
            complaint_tasks.append(self._fetch_nhtsa_data(self.complaints_endpoint, params, f"complaints_{component}"))
        
        complaint_results = await asyncio.gather(*complaint_tasks, return_exceptions=True)
        
        # Process all complaint data
        family_complaints = await self._process_family_complaints(complaint_results, make, model, model_year)
        self._cache_result(cache_key, family_complaints)
        return family_complaints
    
    async def get_family_technical_bulletins(self, make: str, model: str, model_year: int) -> Dict[str, Any]:
        """Get technical service bulletins relevant to family vehicle"""
        if not self.session:
            await self.start()
        
        cache_key = f"family_tsbs_{make}_{model}_{model_year}"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            'make': make.upper(),
            'model': model.upper(),
            'modelYear': model_year
        }
        
        tsb_data = await self._fetch_nhtsa_data(self.tsb_endpoint, params, "family_tsbs")
        
        if tsb_data.get("success"):
            family_tsbs = await self._process_family_tsbs(tsb_data, make, model, model_year)
            self._cache_result(cache_key, family_tsbs)
            return family_tsbs
        
        return tsb_data
    
    async def get_family_investigations(self, make: str, model: str, model_year: int) -> Dict[str, Any]:
        """Get NHTSA investigations that could affect family"""
        if not self.session:
            await self.start()
        
        cache_key = f"family_investigations_{make}_{model}_{model_year}"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            'make': make.upper(),
            'model': model.upper(),
            'modelYear': model_year
        }
        
        investigation_data = await self._fetch_nhtsa_data(self.investigations_endpoint, params, "family_investigations")
        
        if investigation_data.get("success"):
            family_investigations = await self._process_family_investigations(investigation_data, make, model, model_year)
            self._cache_result(cache_key, family_investigations)
            return family_investigations
        
        return investigation_data
    
    async def _fetch_nhtsa_data(self, endpoint: str, params: Dict, data_type: str) -> Dict[str, Any]:
        """Fetch data from NHTSA API with family protection priority"""
        
        # Rate limiting for family protection
        await asyncio.sleep(self.rate_limit_delay)
        
        for attempt in range(self.retry_attempts):
            try:
                url = f"{endpoint}?{urlencode(params)}"
                self.logger.info(f"🌐 Family Protection Request: {data_type}")
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data,
                            "endpoint": endpoint,
                            "params": params,
                            "family_protection": True,
                            "fetched_at": datetime.now().isoformat()
                        }
                    elif response.status == 429:  # Rate limited
                        wait_time = 10 * (attempt + 1)
                        self.logger.warning(f"🚦 Rate limited, waiting {wait_time}s (family protection)")
                        await asyncio.sleep(wait_time)
                    else:
                        self.logger.warning(f"❌ API returned status {response.status} for {data_type}")
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"⏰ Timeout on attempt {attempt + 1} for {data_type}")
            except Exception as e:
                self.logger.error(f"🚨 Error on attempt {attempt + 1} for {data_type}: {str(e)}")
            
            if attempt < self.retry_attempts - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        return {
            "success": False,
            "error": f"Failed to fetch {data_type} after {self.retry_attempts} attempts",
            "endpoint": endpoint,
            "params": params,
            "family_protection": True
        }
    
    async def _process_family_recalls(self, recall_data: Dict, vin: str, make: str, model: str, model_year: int) -> Dict[str, Any]:
        """Process recalls with family protection focus"""
        try:
            raw_data = recall_data.get("data", {})
            results = raw_data.get("results", []) if isinstance(raw_data.get("results"), list) else []
            
            # Categorize recalls by threat level to family
            critical_recalls = []
            safety_recalls = []
            all_recalls = []
            
            for recall in results:
                recall_info = {
                    "nhtsa_recall_id": recall.get("NHTSARecallId", "Unknown"),
                    "recall_date": recall.get("RecallDate", "Unknown"),
                    "component": recall.get("Component", "Unknown"),
                    "summary": recall.get("Summary", "Unknown"),
                    "consequence": recall.get("Consequence", "Unknown"),
                    "remedy": recall.get("Remedy", "Unknown"),
                    "manufacturer": recall.get("Manufacturer", "Unknown"),
                    "report_date": recall.get("ReportDate", "Unknown"),
                    "family_threat_level": "LOW"
                }
                
                all_recalls.append(recall_info)
                
                # Assess family threat level
                component = recall_info["component"].upper()
                summary = recall_info["summary"].upper()
                consequence = recall_info["consequence"].upper()
                
                # Critical threats to family safety
                if any(term in consequence for term in ["FIRE", "INJURY", "CRASH", "DEATH", "ACCIDENT"]):
                    recall_info["family_threat_level"] = "CRITICAL"
                    critical_recalls.append(recall_info)
                
                # Safety threats that could strand family
                elif any(term in component or term in summary for term in [
                    "BATTERY", "ELECTRICAL", "ENGINE", "FUEL", "BRAKES", "STEERING",
                    "POWER", "CHARGING", "STARTING", "IGNITION"
                ]):
                    recall_info["family_threat_level"] = "HIGH"
                    safety_recalls.append(recall_info)
            
            # Family protection analysis
            family_analysis = {
                "total_recalls": len(all_recalls),
                "critical_threats": len(critical_recalls),
                "safety_threats": len(safety_recalls),
                "immediate_action_required": len(critical_recalls) > 0,
                "family_safety_status": "AT_RISK" if len(critical_recalls) > 0 else "MONITOR",
                "last_recall_date": max([r.get("recall_date", "1900-01-01") for r in all_recalls], default="None")
            }
            
            return {
                "success": True,
                "family_vehicle": f"{make} {model} {model_year}",
                "vin": vin,
                "critical_recalls": critical_recalls,
                "safety_recalls": safety_recalls,
                "all_recalls": all_recalls,
                "family_analysis": family_analysis,
                "family_actions": await self._generate_family_recall_actions(family_analysis, critical_recalls + safety_recalls),
                "fetched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"🚨 Error processing family recalls for VIN {vin}: {str(e)}")
            return {
                "success": False,
                "error": f"Family recall processing error: {str(e)}",
                "vin": vin,
                "family_vehicle": f"{make} {model} {model_year}"
            }
    
    async def _process_family_complaints(self, complaint_results: List, make: str, model: str, model_year: int) -> Dict[str, Any]:
        """Process complaints with family safety focus"""
        try:
            all_complaints = []
            safety_incidents = 0
            battery_electrical_issues = 0
            recent_surge = 0
            
            for result in complaint_results:
                if isinstance(result, Exception):
                    continue
                    
                if not result.get("success"):
                    continue
                
                raw_data = result.get("data", {})
                results = raw_data.get("results", []) if isinstance(raw_data.get("results"), list) else []
                
                for complaint in results:
                    complaint_info = {
                        "nhtsa_id": complaint.get("NHTSAId", "Unknown"),
                        "date_received": complaint.get("DateReceived", "Unknown"),
                        "incident_date": complaint.get("IncidentDate", "Unknown"),
                        "component": complaint.get("Component", "Unknown"),
                        "summary": complaint.get("Summary", "Unknown"),
                        "crashed": complaint.get("Crashed", False),
                        "fire": complaint.get("Fire", False),
                        "injured": complaint.get("Injured", 0),
                        "deaths": complaint.get("Deaths", 0),
                        "mileage": complaint.get("Mileage", "Unknown"),
                        "family_risk_level": "LOW"
                    }
                    
                    all_complaints.append(complaint_info)
                    
                    # Assess family risk
                    if complaint_info["crashed"] or complaint_info["fire"] or complaint_info["injured"] > 0:
                        safety_incidents += 1
                        complaint_info["family_risk_level"] = "CRITICAL"
                    
                    component = complaint_info["component"].upper()
                    summary = complaint_info["summary"].upper()
                    
                    if any(term in component or term in summary for term in [
                        "BATTERY", "ELECTRICAL", "POWER", "CHARGING", "DEAD", "START", "IGNITION"
                    ]):
                        battery_electrical_issues += 1
                        if complaint_info["family_risk_level"] == "LOW":
                            complaint_info["family_risk_level"] = "MEDIUM"
                    
                    if self._is_recent_date(complaint_info.get("date_received")):
                        recent_surge += 1
            
            # Family safety analysis
            family_complaint_analysis = {
                "total_complaints": len(all_complaints),
                "safety_incidents": safety_incidents,
                "battery_electrical_issues": battery_electrical_issues,
                "recent_surge": recent_surge,
                "family_alert_level": "HIGH" if safety_incidents > 0 else ("MEDIUM" if battery_electrical_issues > 3 else "LOW"),
                "trend_status": "SURGE" if recent_surge > len(all_complaints) * 0.4 else "STABLE"
            }
            
            return {
                "success": True,
                "family_vehicle": f"{make} {model} {model_year}",
                "all_complaints": all_complaints,
                "family_analysis": family_complaint_analysis,
                "family_recommendations": await self._generate_family_complaint_actions(family_complaint_analysis),
                "fetched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"🚨 Error processing family complaints: {str(e)}")
            return {
                "success": False,
                "error": f"Family complaint processing error: {str(e)}",
                "family_vehicle": f"{make} {model} {model_year}"
            }
    
    async def _process_family_tsbs(self, tsb_data: Dict, make: str, model: str, model_year: int) -> Dict[str, Any]:
        """Process TSBs with family vehicle focus"""
        try:
            raw_data = tsb_data.get("data", {})
            results = raw_data.get("results", []) if isinstance(raw_data.get("results"), list) else []
            
            family_critical_tsbs = []
            all_tsbs = []
            
            for tsb in results:
                tsb_info = {
                    "tsb_number": tsb.get("TSBNumber", "Unknown"),
                    "date": tsb.get("Date", "Unknown"),
                    "component": tsb.get("Component", "Unknown"),
                    "summary": tsb.get("Summary", "Unknown"),
                    "manufacturer": tsb.get("Manufacturer", "Unknown"),
                    "family_relevance": "LOW"
                }
                
                all_tsbs.append(tsb_info)
                
                # Check for family-critical issues
                component = tsb_info["component"].upper()
                summary = tsb_info["summary"].upper()
                
                if any(term in component or term in summary for term in [
                    "BATTERY", "ELECTRICAL", "CHARGING", "STARTING", "POWER",
                    "ENGINE", "FUEL", "SAFETY", "FIRE", "RECALL"
                ]):
                    tsb_info["family_relevance"] = "HIGH"
                    family_critical_tsbs.append(tsb_info)
            
            family_tsb_analysis = {
                "total_tsbs": len(all_tsbs),
                "family_critical_tsbs": len(family_critical_tsbs),
                "recent_tsbs": len([t for t in all_tsbs if self._is_recent_date(t.get("date"))]),
                "action_required": len(family_critical_tsbs) > 0
            }
            
            return {
                "success": True,
                "family_vehicle": f"{make} {model} {model_year}",
                "family_critical_tsbs": family_critical_tsbs,
                "all_tsbs": all_tsbs,
                "family_analysis": family_tsb_analysis,
                "family_actions": await self._generate_family_tsb_actions(family_tsb_analysis),
                "fetched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"🚨 Error processing family TSBs: {str(e)}")
            return {
                "success": False,
                "error": f"Family TSB processing error: {str(e)}",
                "family_vehicle": f"{make} {model} {model_year}"
            }
    
    async def _process_family_investigations(self, investigation_data: Dict, make: str, model: str, model_year: int) -> Dict[str, Any]:
        """Process NHTSA investigations affecting family"""
        try:
            raw_data = investigation_data.get("data", {})
            results = raw_data.get("results", []) if isinstance(raw_data.get("results"), list) else []
            
            active_investigations = []
            family_impact_investigations = []
            
            for investigation in results:
                inv_info = {
                    "investigation_id": investigation.get("InvestigationId", "Unknown"),
                    "date_opened": investigation.get("DateOpened", "Unknown"),
                    "component": investigation.get("Component", "Unknown"),
                    "summary": investigation.get("Summary", "Unknown"),
                    "status": investigation.get("Status", "Unknown"),
                    "family_impact": "LOW"
                }
                
                active_investigations.append(inv_info)
                
                # Check family impact
                component = inv_info["component"].upper()
                summary = inv_info["summary"].upper()
                
                if any(term in component or term in summary for term in [
                    "FIRE", "CRASH", "INJURY", "DEATH", "BATTERY", "ELECTRICAL",
                    "ENGINE", "FUEL", "SAFETY", "SUDDEN"
                ]):
                    inv_info["family_impact"] = "HIGH"
                    family_impact_investigations.append(inv_info)
            
            family_investigation_analysis = {
                "total_investigations": len(active_investigations),
                "family_impact_investigations": len(family_impact_investigations),
                "active_investigations": len([i for i in active_investigations if i.get("status", "").upper() == "OPEN"]),
                "family_alert_level": "HIGH" if len(family_impact_investigations) > 0 else "LOW"
            }
            
            return {
                "success": True,
                "family_vehicle": f"{make} {model} {model_year}",
                "family_impact_investigations": family_impact_investigations,
                "all_investigations": active_investigations,
                "family_analysis": family_investigation_analysis,
                "family_monitoring": await self._generate_family_investigation_monitoring(family_investigation_analysis),
                "fetched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"🚨 Error processing family investigations: {str(e)}")
            return {
                "success": False,
                "error": f"Family investigation processing error: {str(e)}",
                "family_vehicle": f"{make} {model} {model_year}"
            }
    
    async def _assess_family_threats(self, protection_report: Dict) -> Dict[str, Any]:
        """Assess overall threats to Ford family"""
        threat_score = 0
        threat_factors = []
        critical_actions = []
        
        # Analyze recalls
        recalls = protection_report.get("recall_intelligence", {})
        if recalls.get("success"):
            critical_recalls = len(recalls.get("critical_recalls", []))
            safety_recalls = len(recalls.get("safety_recalls", []))
            
            if critical_recalls > 0:
                threat_score += critical_recalls * 50
                threat_factors.append(f"{critical_recalls} CRITICAL safety recalls")
                critical_actions.append("IMMEDIATE: Check recall completion status")
            
            if safety_recalls > 0:
                threat_score += safety_recalls * 25
                threat_factors.append(f"{safety_recalls} safety-related recalls")
        
        # Analyze safety complaints
        complaints = protection_report.get("safety_complaints", {})
        if complaints.get("success"):
            safety_incidents = complaints.get("family_analysis", {}).get("safety_incidents", 0)
            battery_issues = complaints.get("family_analysis", {}).get("battery_electrical_issues", 0)
            
            if safety_incidents > 0:
                threat_score += safety_incidents * 30
                threat_factors.append(f"{safety_incidents} safety incidents reported")
                critical_actions.append("HIGH: Monitor for similar symptoms")
            
            if battery_issues > 5:
                threat_score += 20
                threat_factors.append(f"High battery/electrical complaint volume: {battery_issues}")
        
        # Analyze investigations
        investigations = protection_report.get("safety_investigations", {})
        if investigations.get("success"):
            family_impact = len(investigations.get("family_impact_investigations", []))
            if family_impact > 0:
                threat_score += family_impact * 35
                threat_factors.append(f"{family_impact} active NHTSA investigations")
                critical_actions.append("MONITOR: NHTSA investigation in progress")
        
        # Determine overall threat level
        if threat_score >= 100:
            threat_level = "CRITICAL"
        elif threat_score >= 75:
            threat_level = "HIGH"
        elif threat_score >= 40:
            threat_level = "MEDIUM"
        else:
            threat_level = "LOW"
        
        return {
            "overall_threat_score": min(threat_score, 100),
            "threat_level": threat_level,
            "threat_factors": threat_factors,
            "critical_actions": critical_actions,
            "family_safety_status": "AT_RISK" if threat_level in ["CRITICAL", "HIGH"] else "MONITORING",
            "last_assessment": datetime.now().isoformat()
        }
    
    async def _generate_immediate_actions(self, threat_assessment: Dict) -> List[Dict[str, Any]]:
        """Generate immediate protective actions for family"""
        actions = []
        
        threat_level = threat_assessment.get("threat_level", "LOW")
        critical_actions = threat_assessment.get("critical_actions", [])
        
        if threat_level == "CRITICAL":
            actions.append({
                "action_type": "IMMEDIATE_CONTACT",
                "priority": "URGENT",
                "title": "CRITICAL SAFETY ALERT",
                "description": "Vehicle has critical safety issues that could endanger family",
                "action": "Contact family immediately to schedule emergency inspection",
                "timeline": "Within 24 hours"
            })
        
        elif threat_level == "HIGH":
            actions.append({
                "action_type": "PRIORITY_CONTACT",
                "priority": "HIGH", 
                "title": "Safety Concern Detected",
                "description": "Vehicle has safety-related issues requiring attention",
                "action": "Contact family within 48 hours to schedule service",
                "timeline": "Within 48 hours"
            })
        
        for critical_action in critical_actions:
            actions.append({
                "action_type": "SPECIFIC_ACTION",
                "priority": "HIGH",
                "title": "Government Alert Response",
                "description": critical_action,
                "action": "Verify and address government-identified issue",
                "timeline": "Within 1 week"
            })
        
        return actions
    
    async def _generate_family_recommendations(self, protection_report: Dict) -> List[Dict[str, Any]]:
        """Generate comprehensive family protection recommendations"""
        recommendations = []
        
        # Recall recommendations
        recalls = protection_report.get("recall_intelligence", {})
        if recalls.get("success"):
            if recalls.get("family_analysis", {}).get("immediate_action_required"):
                recommendations.append({
                    "category": "RECALL_COMPLIANCE",
                    "priority": "CRITICAL",
                    "title": "Outstanding Safety Recalls",
                    "description": "Vehicle has incomplete safety recalls",
                    "recommendation": "Schedule immediate recall completion service",
                    "family_benefit": "Prevents potential safety incidents"
                })
        
        # Complaint pattern recommendations
        complaints = protection_report.get("safety_complaints", {})
        if complaints.get("success"):
            analysis = complaints.get("family_analysis", {})
            if analysis.get("family_alert_level") == "HIGH":
                recommendations.append({
                    "category": "PROACTIVE_INSPECTION",
                    "priority": "HIGH",
                    "title": "Preventive Safety Inspection",
                    "description": "Similar vehicles showing safety concerns",
                    "recommendation": "Perform comprehensive safety inspection",
                    "family_benefit": "Early detection of potential issues"
                })
        
        # TSB recommendations
        tsbs = protection_report.get("technical_bulletins", {})
        if tsbs.get("success"):
            if tsbs.get("family_analysis", {}).get("action_required"):
                recommendations.append({
                    "category": "TECHNICAL_UPDATE",
                    "priority": "MEDIUM",
                    "title": "Technical Service Bulletins",
                    "description": "Service bulletins available for vehicle",
                    "recommendation": "Apply relevant technical updates",
                    "family_benefit": "Improved reliability and performance"
                })
        
        return recommendations
    
    async def _generate_family_recall_actions(self, analysis: Dict, recalls: List) -> List[str]:
        """Generate family-specific recall actions"""
        actions = []
        
        if analysis.get("immediate_action_required"):
            actions.append("🚨 URGENT: Contact family immediately about critical safety recalls")
            actions.append("📅 Schedule emergency service appointment within 24 hours")
        
        if analysis.get("family_safety_status") == "AT_RISK":
            actions.append("⚠️ Advise family to avoid driving until recalls completed")
            actions.append("🔧 Prioritize recall service scheduling")
        
        return actions
    
    async def _generate_family_complaint_actions(self, analysis: Dict) -> List[str]:
        """Generate family-specific complaint response actions"""
        actions = []
        
        if analysis.get("family_alert_level") == "HIGH":
            actions.append("🔍 Perform immediate safety inspection")
            actions.append("📞 Contact family about potential safety concerns")
        
        if analysis.get("trend_status") == "SURGE":
            actions.append("📈 Monitor family vehicle closely - complaint surge detected")
            actions.append("🛡️ Implement proactive monitoring protocol")
        
        return actions
    
    async def _generate_family_tsb_actions(self, analysis: Dict) -> List[str]:
        """Generate family-specific TSB actions"""
        actions = []
        
        if analysis.get("action_required"):
            actions.append("📋 Review and apply relevant technical service bulletins")
            actions.append("🔧 Update service procedures per TSB guidelines")
        
        return actions
    
    async def _generate_family_investigation_monitoring(self, analysis: Dict) -> List[str]:
        """Generate family investigation monitoring plan"""
        monitoring = []
        
        if analysis.get("family_alert_level") == "HIGH":
            monitoring.append("👁️ Monitor NHTSA investigation progress")
            monitoring.append("📧 Set up alerts for investigation updates")
            monitoring.append("🛡️ Implement enhanced family vehicle monitoring")
        
        return monitoring
    
    async def _get_recalls_fallback(self, make: str, model: str, model_year: int, vin: Optional[str]) -> Dict[str, Any]:
        """Fallback method using VPIC API for recalls"""
        try:
            params = {
                'make': make,
                'model': model,
                'modelYear': model_year,
                'format': 'json'
            }
            
            fallback_data = await self._fetch_nhtsa_data(self.vpic_recall_endpoint, params, "recalls_fallback")
            
            return {
                "success": True,
                "source": "VPIC_FALLBACK",
                "data": fallback_data,
                "family_vehicle": f"{make} {model} {model_year}",
                "vin": vin,
                "note": "Retrieved via fallback VPIC API for family protection"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Fallback recall fetch failed: {str(e)}",
                "family_vehicle": f"{make} {model} {model_year}",
                "vin": vin
            }
    
    def _is_recent_date(self, date_str: str) -> bool:
        """Check if date is within last 18 months (family relevance)"""
        try:
            if not date_str or date_str == "Unknown":
                return False
            
            # Parse various date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y"]:
                try:
                    date_obj = datetime.strptime(date_str[:10], fmt)
                    return (datetime.now() - date_obj).days <= 545  # 18 months
                except ValueError:
                    continue
            
            return False
        except:
            return False
    
    def _get_cached_result(self, key: str) -> Optional[Dict]:
        """Get cached result if still valid"""
        if key in self.cache:
            cached_data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return cached_data
            else:
                del self.cache[key]
        return None
    
    def _cache_result(self, key: str, data: Dict):
        """Cache result with timestamp"""
        self.cache[key] = (data, datetime.now())
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """Get current worker status"""
        return {
            "worker_id": self.worker_id,
            "worker_type": "nhtsa_intelligence",
            "mission": "FORD_FAMILY_PROTECTION",
            "session_active": self.session is not None,
            "cache_entries": len(self.cache),
            "families_protected": "CLASSIFIED",
            "endpoints": {
                "recalls": self.recalls_endpoint,
                "complaints": self.complaints_endpoint,
                "tsbs": self.tsb_endpoint,
                "investigations": self.investigations_endpoint
            },
            "status": "FAMILY_GUARDIAN_ACTIVE" if self.session else "not_initialized",
            "last_updated": datetime.now().isoformat()
        }

# Example usage
async def test_family_protection():
    """Test the NHTSA family protection worker"""
    worker = NHTSAIntelligenceWorker("family_guardian_1")
    
    try:
        await worker.start()
        
        # Test family protection mode
        family_report = await worker.protect_family_vehicle(
            vin="1FTFW1ET0LFA12345",
            make="Ford",
            model="F-150", 
            model_year=2022
        )
        print(f"🛡️ Family protection report: {json.dumps(family_report, indent=2)}")
        
        # Worker status
        status = await worker.get_worker_status()
        print(f"📊 Family Guardian status: {json.dumps(status, indent=2)}")
        
    finally:
        await worker.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_family_protection()) 