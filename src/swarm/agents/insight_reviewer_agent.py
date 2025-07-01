"""
📝 Insight Reviewer Agent
Ranks lead value and forecasts dealer engagement value
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent


class InsightReviewerAgent(BaseAgent):
    """Agent for insight review and lead ranking"""
    
    def __init__(self, redis_pool):
        super().__init__("insight_reviewer", redis_pool)
        
        # Lead value scoring weights
        self.scoring_weights = {
            "risk_score": 0.30,
            "confidence": 0.25, 
            "stressor_count": 0.20,
            "compliance_score": 0.15,
            "data_completeness": 0.10
        }
        
        # Revenue multipliers by classification
        self.revenue_multipliers = {
            "critical": {"base": 1200, "conversion": 0.78},
            "high": {"base": 850, "conversion": 0.65},
            "moderate": {"base": 450, "conversion": 0.45},
            "low": {"base": 280, "conversion": 0.30}
        }
    
    async def process(self, task) -> Dict[str, Any]:
        """Review insights and rank lead value"""
        start_time = datetime.utcnow()
        
        try:
            # Extract data from previous agents
            risk_score = task.results.get("risk_score", 0.0)
            confidence = task.results.get("confidence", 0.0)
            validated_stressors = task.results.get("validated_stressors", [])
            compliance_score = task.results.get("compliance_score", 0.0)
            data_completeness = task.results.get("data_completeness", 0.0)
            lead_classification = task.results.get("lead_classification", {})
            approved_for_use = task.results.get("approved_for_use", False)
            
            if not approved_for_use:
                return {"error": "Lead not approved for use", "lead_value_score": 0.0}
            
            # Calculate lead value score
            lead_value_score = self._calculate_lead_value_score(
                risk_score, confidence, len(validated_stressors), compliance_score, data_completeness
            )
            
            # Forecast dealer engagement value
            engagement_forecast = self._forecast_dealer_engagement(lead_classification, lead_value_score)
            
            # Calculate revenue opportunity
            revenue_opportunity = self._calculate_revenue_opportunity(lead_classification, lead_value_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(lead_classification, lead_value_score, validated_stressors)
            
            # Determine lead ranking
            lead_ranking = self._determine_lead_ranking(lead_value_score, engagement_forecast)
            
            result = {
                "lead_value_score": lead_value_score,
                "engagement_forecast": engagement_forecast,
                "revenue_opportunity": revenue_opportunity,
                "recommendations": recommendations,
                "lead_ranking": lead_ranking,
                "final_approval": lead_value_score >= 0.6,
                "expected_conversion_rate": engagement_forecast.get("conversion_rate", 0.0),
                "priority_tier": self._get_priority_tier(lead_value_score)
            }
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, False)
            
            return {"error": str(e), "lead_value_score": 0.0}
    
    def _calculate_lead_value_score(self, risk_score: float, confidence: float, 
                                   stressor_count: int, compliance_score: float, 
                                   data_completeness: float) -> float:
        """Calculate weighted lead value score"""
        
        # Normalize stressor count (cap at 5)
        normalized_stressor_count = min(1.0, stressor_count / 5.0)
        
        # Calculate weighted score
        score = (
            risk_score * self.scoring_weights["risk_score"] +
            confidence * self.scoring_weights["confidence"] +
            normalized_stressor_count * self.scoring_weights["stressor_count"] +
            compliance_score * self.scoring_weights["compliance_score"] +
            data_completeness * self.scoring_weights["data_completeness"]
        )
        
        return min(1.0, score)
    
    def _forecast_dealer_engagement(self, classification: Dict[str, Any], value_score: float) -> Dict[str, Any]:
        """Forecast dealer engagement metrics"""
        
        risk_level = classification.get("level", "moderate")
        multiplier = self.revenue_multipliers.get(risk_level, self.revenue_multipliers["moderate"])
        
        # Base conversion rate adjusted by value score
        base_conversion = multiplier["conversion"]
        adjusted_conversion = base_conversion * (0.5 + (value_score * 0.5))
        
        return {
            "conversion_rate": min(0.95, adjusted_conversion),
            "expected_response_time_hours": self._get_response_time(risk_level),
            "follow_up_likelihood": min(0.9, value_score + 0.2),
            "dealer_satisfaction_score": min(5.0, 3.0 + (value_score * 2.0))
        }
    
    def _calculate_revenue_opportunity(self, classification: Dict[str, Any], value_score: float) -> Dict[str, Any]:
        """Calculate revenue opportunity"""
        
        risk_level = classification.get("level", "moderate")
        multiplier = self.revenue_multipliers.get(risk_level, self.revenue_multipliers["moderate"])
        
        base_revenue = multiplier["base"]
        # Adjust based on lead quality
        adjusted_revenue = int(base_revenue * (0.7 + (value_score * 0.6)))
        
        conversion_rate = multiplier["conversion"] * (0.5 + (value_score * 0.5))
        expected_revenue = int(adjusted_revenue * conversion_rate)
        
        return {
            "potential_revenue": adjusted_revenue,
            "expected_revenue": expected_revenue,
            "conversion_rate": min(0.95, conversion_rate),
            "roi_estimate": min(15.0, 5.0 + (value_score * 10.0))
        }
    
    def _generate_recommendations(self, classification: Dict[str, Any], 
                                value_score: float, stressors: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        risk_level = classification.get("level", "moderate")
        
        # Risk-based recommendations
        if risk_level == "critical":
            recommendations.append("Schedule immediate consultation within 24-48 hours")
            recommendations.append("Prepare comprehensive diagnostic package")
        elif risk_level == "high":
            recommendations.append("Contact customer within 1 week")
            recommendations.append("Offer proactive maintenance package")
        elif risk_level == "moderate":
            recommendations.append("Add to monthly outreach campaign")
            recommendations.append("Include in next service reminder")
        else:
            recommendations.append("Reinforce positive maintenance habits")
            recommendations.append("Offer premium service packages")
        
        # Stressor-specific recommendations
        if "soc_decline" in stressors:
            recommendations.append("Focus on battery health discussion")
        if "climate_stress" in stressors:
            recommendations.append("Discuss seasonal maintenance needs")
        
        # Quality-based recommendations
        if value_score > 0.8:
            recommendations.append("Flag as high-value customer for priority handling")
        
        return recommendations
    
    def _determine_lead_ranking(self, value_score: float, engagement_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Determine lead ranking and tier"""
        
        conversion_rate = engagement_forecast.get("conversion_rate", 0.0)
        combined_score = (value_score * 0.6) + (conversion_rate * 0.4)
        
        if combined_score >= 0.8:
            tier = "Tier 1 - Premium"
            priority = "Immediate"
        elif combined_score >= 0.6:
            tier = "Tier 2 - High Value"
            priority = "This Week"
        elif combined_score >= 0.4:
            tier = "Tier 3 - Standard"
            priority = "This Month"
        else:
            tier = "Tier 4 - Low Priority"
            priority = "Quarterly"
        
        return {
            "tier": tier,
            "priority": priority,
            "combined_score": combined_score,
            "ranking_percentile": min(99, int(combined_score * 100))
        }
    
    def _get_response_time(self, risk_level: str) -> int:
        """Get expected response time by risk level"""
        response_times = {
            "critical": 4,
            "high": 24,
            "moderate": 72,
            "low": 168
        }
        return response_times.get(risk_level, 72)
    
    def _get_priority_tier(self, value_score: float) -> str:
        """Get priority tier based on value score"""
        if value_score >= 0.8:
            return "P1 - Immediate"
        elif value_score >= 0.6:
            return "P2 - High"
        elif value_score >= 0.4:
            return "P3 - Medium"
        else:
            return "P4 - Low"
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": "InsightReviewerAgent",
            "version": "1.0",
            "capabilities": ["Lead ranking", "Value assessment", "Revenue forecasting", "Dealer recommendations"]
        }
