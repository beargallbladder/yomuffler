"""
🚀 Promotion Path Agent
Tracks project milestones, cross-functional buy-in, and ELT awareness
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent


class PromotionPathAgent(BaseAgent):
    """Agent for tracking promotion path and organizational momentum"""
    
    def __init__(self, redis_pool):
        super().__init__("promotion_path", redis_pool)
        
        # Project milestones tracking
        self.milestones = {
            "technical_completion": {"weight": 0.25, "status": "in_progress"},
            "pilot_deployment": {"weight": 0.20, "status": "pending"},
            "dealer_validation": {"weight": 0.20, "status": "pending"},
            "executive_buy_in": {"weight": 0.15, "status": "pending"},
            "cross_functional_alignment": {"weight": 0.10, "status": "pending"},
            "business_case_validation": {"weight": 0.10, "status": "pending"}
        }
        
        # Success metrics for promotion
        self.success_metrics = {
            "system_health_score": {"target": 90, "current": 75},
            "lead_quality_score": {"target": 85, "current": 0},
            "dealer_satisfaction": {"target": 4.5, "current": 0},
            "revenue_demonstration": {"target": 100000, "current": 0}
        }
    
    async def process(self, task) -> Dict[str, Any]:
        """Track promotion path metrics and organizational readiness"""
        start_time = datetime.utcnow()
        
        try:
            # Update metrics based on current task results
            lead_value_score = task.results.get("lead_value_score", 0.0)
            final_approval = task.results.get("final_approval", False)
            revenue_opportunity = task.results.get("revenue_opportunity", {})
            
            # Update promotion metrics
            promotion_metrics = self._update_promotion_metrics(lead_value_score, final_approval, revenue_opportunity)
            
            # Calculate readiness scores
            readiness_assessment = self._calculate_readiness_assessment()
            
            # Generate promotion strategy
            promotion_strategy = self._generate_promotion_strategy(readiness_assessment)
            
            # Track milestone progress
            milestone_progress = self._track_milestone_progress()
            
            # Calculate ELT readiness score
            elt_readiness = self._calculate_elt_readiness_score(readiness_assessment, milestone_progress)
            
            result = {
                "promotion_metrics": promotion_metrics,
                "readiness_assessment": readiness_assessment,
                "promotion_strategy": promotion_strategy,
                "milestone_progress": milestone_progress,
                "elt_readiness_score": elt_readiness,
                "promotion_recommendation": self._get_promotion_recommendation(elt_readiness),
                "next_actions": self._get_next_actions(readiness_assessment),
                "timeline_estimate": self._estimate_promotion_timeline(readiness_assessment)
            }
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, False)
            
            return {"error": str(e), "elt_readiness_score": 0.0}
    
    def _update_promotion_metrics(self, lead_value_score: float, final_approval: bool, 
                                revenue_opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Update promotion metrics based on current results"""
        
        # Update lead quality score
        if lead_value_score > 0:
            current_quality = self.success_metrics["lead_quality_score"]["current"]
            # Moving average update
            updated_quality = (current_quality * 0.8) + (lead_value_score * 100 * 0.2)
            self.success_metrics["lead_quality_score"]["current"] = updated_quality
        
        # Update revenue demonstration
        expected_revenue = revenue_opportunity.get("expected_revenue", 0)
        if expected_revenue > 0:
            current_revenue = self.success_metrics["revenue_demonstration"]["current"]
            self.success_metrics["revenue_demonstration"]["current"] = current_revenue + expected_revenue
        
        return {
            "lead_quality_improvement": lead_value_score * 100,
            "approval_rate": 1.0 if final_approval else 0.0,
            "revenue_impact": expected_revenue,
            "system_maturity": self._calculate_system_maturity()
        }
    
    def _calculate_readiness_assessment(self) -> Dict[str, Any]:
        """Calculate organizational readiness for promotion"""
        
        # Technical readiness
        technical_score = min(100, (self.success_metrics["system_health_score"]["current"] / 
                                   self.success_metrics["system_health_score"]["target"]) * 100)
        
        # Business readiness
        business_score = min(100, (self.success_metrics["revenue_demonstration"]["current"] / 
                                  self.success_metrics["revenue_demonstration"]["target"]) * 100)
        
        # Market readiness
        market_score = min(100, (self.success_metrics["lead_quality_score"]["current"] / 
                                self.success_metrics["lead_quality_score"]["target"]) * 100)
        
        # Overall readiness
        overall_readiness = (technical_score * 0.4) + (business_score * 0.35) + (market_score * 0.25)
        
        return {
            "technical_readiness": technical_score,
            "business_readiness": business_score,
            "market_readiness": market_score,
            "overall_readiness": overall_readiness,
            "readiness_level": self._get_readiness_level(overall_readiness)
        }
    
    def _generate_promotion_strategy(self, readiness: Dict[str, Any]) -> Dict[str, Any]:
        """Generate promotion strategy based on readiness"""
        
        overall_readiness = readiness["overall_readiness"]
        
        if overall_readiness >= 80:
            strategy = {
                "phase": "ELT Presentation Ready",
                "approach": "Executive briefing with full business case",
                "timeline": "2-4 weeks",
                "confidence": "High"
            }
        elif overall_readiness >= 60:
            strategy = {
                "phase": "Pilot Validation",
                "approach": "Expand pilot program and gather more data",
                "timeline": "6-8 weeks",
                "confidence": "Medium"
            }
        elif overall_readiness >= 40:
            strategy = {
                "phase": "Technical Maturation",
                "approach": "Focus on system improvements and stability",
                "timeline": "10-12 weeks",
                "confidence": "Low"
            }
        else:
            strategy = {
                "phase": "Foundation Building",
                "approach": "Strengthen technical foundation and metrics",
                "timeline": "16+ weeks",
                "confidence": "Very Low"
            }
        
        return strategy
    
    def _track_milestone_progress(self) -> Dict[str, Any]:
        """Track progress on key milestones"""
        
        completed_milestones = []
        pending_milestones = []
        
        for milestone, data in self.milestones.items():
            if data["status"] == "completed":
                completed_milestones.append(milestone)
            else:
                pending_milestones.append(milestone)
        
        # Calculate completion percentage
        total_weight = sum(data["weight"] for data in self.milestones.values())
        completed_weight = sum(data["weight"] for milestone, data in self.milestones.items() 
                              if data["status"] == "completed")
        
        completion_percentage = (completed_weight / total_weight) * 100
        
        return {
            "completion_percentage": completion_percentage,
            "completed_milestones": completed_milestones,
            "pending_milestones": pending_milestones,
            "critical_path": self._identify_critical_path(),
            "estimated_completion": self._estimate_completion_date()
        }
    
    def _calculate_elt_readiness_score(self, readiness: Dict[str, Any], 
                                     milestones: Dict[str, Any]) -> float:
        """Calculate ELT (Executive Leadership Team) readiness score"""
        
        # Weighted combination of factors
        readiness_score = readiness["overall_readiness"] * 0.4
        milestone_score = milestones["completion_percentage"] * 0.3
        business_impact_score = min(100, (self.success_metrics["revenue_demonstration"]["current"] / 50000) * 100) * 0.3
        
        elt_score = (readiness_score + milestone_score + business_impact_score) / 100
        return min(1.0, elt_score)
    
    def _get_promotion_recommendation(self, elt_readiness: float) -> str:
        """Get promotion recommendation based on ELT readiness"""
        
        if elt_readiness >= 0.8:
            return "PROCEED - Schedule ELT presentation immediately"
        elif elt_readiness >= 0.6:
            return "PREPARE - Complete pilot validation first"
        elif elt_readiness >= 0.4:
            return "DEVELOP - Strengthen technical and business metrics"
        else:
            return "WAIT - Continue foundation building"
    
    def _get_next_actions(self, readiness: Dict[str, Any]) -> List[str]:
        """Get next actions for promotion path"""
        actions = []
        
        if readiness["technical_readiness"] < 80:
            actions.append("Improve system health score to 90+")
        
        if readiness["business_readiness"] < 80:
            actions.append("Demonstrate $100K+ revenue impact")
        
        if readiness["market_readiness"] < 80:
            actions.append("Achieve 85+ lead quality score")
        
        if len(actions) == 0:
            actions.append("Prepare ELT presentation materials")
            actions.append("Schedule stakeholder alignment meetings")
        
        return actions
    
    def _estimate_promotion_timeline(self, readiness: Dict[str, Any]) -> str:
        """Estimate timeline to promotion readiness"""
        
        overall_readiness = readiness["overall_readiness"]
        
        if overall_readiness >= 80:
            return "Ready now"
        elif overall_readiness >= 60:
            return "4-6 weeks"
        elif overall_readiness >= 40:
            return "8-12 weeks"
        else:
            return "16+ weeks"
    
    def _calculate_system_maturity(self) -> float:
        """Calculate overall system maturity"""
        # Placeholder calculation
        return 0.75
    
    def _get_readiness_level(self, score: float) -> str:
        """Get readiness level description"""
        if score >= 80:
            return "Promotion Ready"
        elif score >= 60:
            return "Near Ready"
        elif score >= 40:
            return "In Development"
        else:
            return "Early Stage"
    
    def _identify_critical_path(self) -> List[str]:
        """Identify critical path milestones"""
        return ["technical_completion", "pilot_deployment", "executive_buy_in"]
    
    def _estimate_completion_date(self) -> str:
        """Estimate completion date"""
        # Simplified calculation
        weeks_remaining = len([m for m in self.milestones.values() if m["status"] != "completed"]) * 2
        completion_date = datetime.now() + timedelta(weeks=weeks_remaining)
        return completion_date.strftime("%Y-%m-%d")
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": "PromotionPathAgent",
            "version": "1.0",
            "capabilities": ["Milestone tracking", "ELT readiness", "Promotion strategy", "Timeline estimation"]
        }
