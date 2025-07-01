"""
🎯 Lead Likelihood Agent
Applies threshold banding and tags diagnostic confidence, data completeness
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent


class LeadLikelihoodAgent(BaseAgent):
    """Agent for lead qualification and likelihood assessment"""
    
    def __init__(self, redis_pool):
        super().__init__("lead_likelihood", redis_pool)
        
        # Lead qualification thresholds
        self.thresholds = {
            "critical": {"min": 0.35, "action": "immediate", "priority": 1},
            "high": {"min": 0.25, "action": "urgent", "priority": 2},
            "moderate": {"min": 0.15, "action": "scheduled", "priority": 3},
            "low": {"min": 0.05, "action": "routine", "priority": 4}
        }
    
    async def process(self, task) -> Dict[str, Any]:
        """Process lead likelihood assessment"""
        start_time = datetime.utcnow()
        
        try:
            risk_score = task.results.get("risk_score", 0.0)
            confidence = task.results.get("confidence", 0.0)
            validated_stressors = task.results.get("validated_stressors", [])
            
            # Apply threshold banding
            lead_classification = self._classify_lead(risk_score)
            
            # Calculate diagnostic confidence
            diagnostic_confidence = self._calculate_diagnostic_confidence(confidence, validated_stressors)
            
            # Assess data completeness
            data_completeness = self._assess_data_completeness(task.results)
            
            # Calculate lead quality score
            lead_quality = self._calculate_lead_quality(risk_score, diagnostic_confidence, data_completeness)
            
            result = {
                "lead_classification": lead_classification,
                "diagnostic_confidence": diagnostic_confidence,
                "data_completeness": data_completeness,
                "lead_quality_score": lead_quality,
                "qualified_lead": lead_quality > 0.7,
                "recommended_action": lead_classification["action"],
                "priority_level": lead_classification["priority"]
            }
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, False)
            
            return {"error": str(e), "qualified_lead": False}
    
    def _classify_lead(self, risk_score: float) -> Dict[str, Any]:
        """Classify lead based on risk score"""
        for level, threshold in self.thresholds.items():
            if risk_score >= threshold["min"]:
                return {
                    "level": level,
                    "action": threshold["action"],
                    "priority": threshold["priority"],
                    "threshold_met": threshold["min"]
                }
        
        return {"level": "minimal", "action": "monitor", "priority": 5, "threshold_met": 0.0}
    
    def _calculate_diagnostic_confidence(self, base_confidence: float, stressors: List[str]) -> float:
        """Calculate diagnostic confidence"""
        # More stressors = higher confidence
        stressor_boost = min(0.2, len(stressors) * 0.05)
        return min(0.95, base_confidence + stressor_boost)
    
    def _assess_data_completeness(self, results: Dict[str, Any]) -> float:
        """Assess completeness of available data"""
        required_fields = ["vehicle_data", "validated_stressors", "risk_score", "confidence"]
        available = sum(1 for field in required_fields if field in results and results[field])
        return available / len(required_fields)
    
    def _calculate_lead_quality(self, risk_score: float, confidence: float, completeness: float) -> float:
        """Calculate overall lead quality score"""
        # Weighted combination
        quality = (risk_score * 0.4) + (confidence * 0.35) + (completeness * 0.25)
        return min(1.0, quality)
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": "LeadLikelihoodAgent",
            "version": "1.0",
            "capabilities": ["Lead qualification", "Threshold banding", "Quality assessment"]
        }
