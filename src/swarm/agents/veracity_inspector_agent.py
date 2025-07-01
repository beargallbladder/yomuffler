"""
🔍 Veracity Inspector Agent  
Ensures only mathematically and operationally reasonable leads are published
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent


class VeracityInspectorAgent(BaseAgent):
    """Agent for veracity checking and reasonableness validation"""
    
    def __init__(self, redis_pool):
        super().__init__("veracity_inspector", redis_pool)
        
        # Reasonableness checks
        self.validation_checks = {
            "risk_score_bounds": {"min": 0.0, "max": 0.95},
            "confidence_bounds": {"min": 0.0, "max": 1.0},
            "max_daily_leads_per_zip": 50,
            "min_stressors_for_high_risk": 2
        }
    
    async def process(self, task) -> Dict[str, Any]:
        """Inspect lead for veracity and reasonableness"""
        start_time = datetime.utcnow()
        
        try:
            risk_score = task.results.get("risk_score", 0.0)
            confidence = task.results.get("confidence", 0.0)
            validated_stressors = task.results.get("validated_stressors", [])
            lead_classification = task.results.get("lead_classification", {})
            
            # Run verification checks
            verification_results = self._run_verification_checks(
                risk_score, confidence, validated_stressors, lead_classification
            )
            
            # Calculate veracity score
            veracity_score = self._calculate_veracity_score(verification_results)
            
            # Determine if lead passes inspection
            passes_inspection = veracity_score >= 0.8
            
            result = {
                "passes_inspection": passes_inspection,
                "veracity_score": veracity_score,
                "verification_results": verification_results,
                "inspection_status": "approved" if passes_inspection else "rejected",
                "rejection_reasons": [check["reason"] for check in verification_results if not check["passed"]]
            }
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, False)
            
            return {"error": str(e), "passes_inspection": False}
    
    def _run_verification_checks(self, risk_score: float, confidence: float, 
                               stressors: List[str], classification: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run all verification checks"""
        checks = []
        
        # Risk score bounds check
        bounds = self.validation_checks["risk_score_bounds"]
        risk_valid = bounds["min"] <= risk_score <= bounds["max"]
        checks.append({
            "check": "risk_score_bounds",
            "passed": risk_valid,
            "reason": f"Risk score {risk_score:.3f} outside valid range" if not risk_valid else "Valid range"
        })
        
        # Confidence bounds check
        conf_bounds = self.validation_checks["confidence_bounds"]
        conf_valid = conf_bounds["min"] <= confidence <= conf_bounds["max"]
        checks.append({
            "check": "confidence_bounds",
            "passed": conf_valid,
            "reason": f"Confidence {confidence:.3f} outside valid range" if not conf_valid else "Valid range"
        })
        
        # High risk stressor check
        high_risk = classification.get("level") in ["critical", "high"]
        min_stressors = self.validation_checks["min_stressors_for_high_risk"]
        stressor_valid = not high_risk or len(stressors) >= min_stressors
        checks.append({
            "check": "high_risk_stressor_count",
            "passed": stressor_valid,
            "reason": f"High risk with only {len(stressors)} stressors" if not stressor_valid else "Sufficient stressors"
        })
        
        # Mathematical consistency check
        math_consistent = self._check_mathematical_consistency(risk_score, confidence, stressors)
        checks.append({
            "check": "mathematical_consistency",
            "passed": math_consistent,
            "reason": "Mathematical inconsistency detected" if not math_consistent else "Mathematically consistent"
        })
        
        return checks
    
    def _check_mathematical_consistency(self, risk_score: float, confidence: float, stressors: List[str]) -> bool:
        """Check if results are mathematically consistent"""
        # High risk should correlate with sufficient evidence
        if risk_score > 0.5 and len(stressors) == 0:
            return False
        
        # Confidence should not exceed what's possible with available data
        if confidence > 0.95 and len(stressors) < 3:
            return False
        
        return True
    
    def _calculate_veracity_score(self, checks: List[Dict[str, Any]]) -> float:
        """Calculate overall veracity score"""
        if not checks:
            return 0.0
        
        passed_checks = sum(1 for check in checks if check["passed"])
        return passed_checks / len(checks)
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": "VeracityInspectorAgent",
            "version": "1.0",
            "capabilities": ["Veracity checking", "Reasonableness validation", "Quality assurance"]
        }
