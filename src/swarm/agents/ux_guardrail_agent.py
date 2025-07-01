"""
🛡️ UX Guardrail Agent
Tests every phrase against misleading claims and confidence overreach
"""

import asyncio
import json
import re
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent


class UXGuardrailAgent(BaseAgent):
    """Agent for UX/messaging guardrails and compliance"""
    
    def __init__(self, redis_pool):
        super().__init__("ux_guardrail", redis_pool)
        
        # Prohibited phrases and patterns
        self.prohibited_patterns = [
            r"\bguarantee[d]?\b",
            r"\bwill fail\b",
            r"\bmust replace\b",
            r"\bFDA approved\b", 
            r"\bcertified\b",
            r"\b100% accurate\b",
            r"\bfailure in \d+ days\b",
            r"\bdefinitely\b",
            r"\balways\b",
            r"\bnever fails?\b"
        ]
        
        # Warning phrases that need context
        self.warning_patterns = [
            r"\bfailure\b",
            r"\bbroken?\b", 
            r"\bemergency\b",
            r"\bdangerous\b",
            r"\bunsafe\b"
        ]
        
        # Approved alternatives
        self.approved_alternatives = {
            "will fail": "may need attention",
            "guaranteed": "likely",
            "must replace": "recommend checking",
            "failure": "service opportunity",
            "broken": "showing stress patterns"
        }
    
    async def process(self, task) -> Dict[str, Any]:
        """Apply UX guardrails to generated messages"""
        start_time = datetime.utcnow()
        
        try:
            dealer_message = task.results.get("dealer_message", "")
            customer_message = task.results.get("customer_message", "")
            phone_script = task.results.get("phone_script", "")
            
            # Check all messages for violations
            dealer_check = self._check_message_compliance(dealer_message, "dealer")
            customer_check = self._check_message_compliance(customer_message, "customer")
            phone_check = self._check_message_compliance(phone_script, "phone")
            
            # Apply corrections if needed
            corrected_dealer = self._apply_corrections(dealer_message, dealer_check)
            corrected_customer = self._apply_corrections(customer_message, customer_check)
            corrected_phone = self._apply_corrections(phone_script, phone_check)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score([dealer_check, customer_check, phone_check])
            
            result = {
                "dealer_message": corrected_dealer,
                "customer_message": corrected_customer, 
                "phone_script": corrected_phone,
                "compliance_score": compliance_score,
                "guardrail_checks": {
                    "dealer": dealer_check,
                    "customer": customer_check,
                    "phone": phone_check
                },
                "corrections_applied": dealer_message != corrected_dealer or customer_message != corrected_customer,
                "approved_for_use": compliance_score >= 0.9
            }
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self._update_metrics(processing_time, False)
            
            return {"error": str(e), "approved_for_use": False}
    
    def _check_message_compliance(self, message: str, message_type: str) -> Dict[str, Any]:
        """Check message for compliance violations"""
        violations = []
        warnings = []
        
        # Check for prohibited patterns
        for pattern in self.prohibited_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                violations.extend(matches)
        
        # Check for warning patterns
        for pattern in self.warning_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                warnings.extend(matches)
        
        # Special checks for customer messages (stricter)
        if message_type == "customer":
            if re.search(r"\bprobability\b|\bpercent\b|%", message, re.IGNORECASE):
                warnings.append("statistical_language")
        
        return {
            "violations": violations,
            "warnings": warnings,
            "violation_count": len(violations),
            "warning_count": len(warnings),
            "compliant": len(violations) == 0
        }
    
    def _apply_corrections(self, message: str, check_result: Dict[str, Any]) -> str:
        """Apply corrections to non-compliant messages"""
        corrected_message = message
        
        # Apply approved alternatives
        for problematic, alternative in self.approved_alternatives.items():
            corrected_message = re.sub(
                r"\b" + re.escape(problematic) + r"\b", 
                alternative, 
                corrected_message, 
                flags=re.IGNORECASE
            )
        
        # Remove or replace specific violations
        for violation in check_result.get("violations", []):
            if "guarantee" in violation.lower():
                corrected_message = corrected_message.replace(violation, "likely")
            elif "will fail" in violation.lower():
                corrected_message = corrected_message.replace(violation, "may need attention")
        
        return corrected_message
    
    def _calculate_compliance_score(self, checks: List[Dict[str, Any]]) -> float:
        """Calculate overall compliance score"""
        if not checks:
            return 1.0
        
        total_violations = sum(check.get("violation_count", 0) for check in checks)
        total_warnings = sum(check.get("warning_count", 0) for check in checks)
        
        # Score based on violations and warnings
        base_score = 1.0
        violation_penalty = total_violations * 0.2
        warning_penalty = total_warnings * 0.05
        
        final_score = max(0.0, base_score - violation_penalty - warning_penalty)
        return final_score
    
    def get_agent_info(self) -> Dict[str, Any]:
        return {
            "name": "UXGuardrailAgent",
            "version": "1.0",
            "capabilities": ["Message compliance", "UX validation", "Content correction"],
            "prohibited_patterns": len(self.prohibited_patterns),
            "warning_patterns": len(self.warning_patterns)
        }
