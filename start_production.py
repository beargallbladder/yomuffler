#!/usr/bin/env python3
"""
VIN Stressors - Universal Vehicle Intelligence Platform
Clean, professional interface with AI-powered personalized messaging  
"""

import os
import sys
import logging
import json
from typing import Dict, List, Optional

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI-powered messaging system
class AIMessageGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("⚠️ OpenAI API key not found - using fallback messages")
        
    def generate_personalized_messages(self, customer_name: str, vehicle_info: str, 
                                       stressors: List[str], risk_score: float, 
                                       channel: str = "sms", message_type: str = "integrated") -> Dict[str, List[str]]:
        """Generate personalized messages based on stressor analysis"""
        
        if not self.openai_api_key:
            return self._fallback_messages(customer_name, vehicle_info, stressors, risk_score)
        
        try:
            # Use synchronous OpenAI client - the async version has issues
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            # Create stressor context
            stressor_context = ", ".join(stressors)
            risk_level = "CRITICAL" if risk_score >= 50 else "HIGH" if risk_score >= 30 else "MODERATE"
            
            # Calculate realistic battery service pricing
            if "Light Truck" in vehicle_info:
                parts_cost, service_cost = 280, 125
            elif "SUV" in vehicle_info:
                parts_cost, service_cost = 320, 145
            elif "Sedan" in vehicle_info:
                parts_cost, service_cost = 180, 85
            else:
                parts_cost, service_cost = 250, 110
            
            total_cost = parts_cost + service_cost
            
            # Create different prompts based on message type
            if message_type == "integrated":
                # Sarah Johnson scenario: Existing prognostics + stressor analysis
                prompt = f"""Create 3 personalized {channel} messages for {customer_name} about their {vehicle_info}.

SCENARIO: Customer has EXISTING scheduled maintenance (oil change overdue, tire rotation due) + STRESSOR ANALYSIS shows battery risk.

Vehicle Analysis:
- Existing services needed: Oil change (overdue), tire rotation
- NEW stressor risk detected: {stressor_context}
- Battery failure risk: {risk_level} ({risk_score:.1f}%)
- BUNDLED opportunity: Oil ${85} + Battery check ${parts_cost//2} + Tire rotation ${45} = ${85 + parts_cost//2 + 45}

Requirements:
- Focus on BUNDLING existing services with stressor-based battery check
- "While you're here for oil change, let's also check your battery"
- Emphasize convenience of doing everything in one visit
- Reference specific stressor patterns that increase urgency
- Show cost savings vs separate visits

Return ONLY the 3 messages, one per line, no numbering or bullets."""
                
            else:  # proactive messaging
                # Mike Rodriguez scenario: No existing prognostics, pure stressor opportunity
                prompt = f"""Create 3 personalized {channel} messages for {customer_name} about their {vehicle_info}.

SCENARIO: Customer has NO immediate service needs, but STRESSOR ANALYSIS reveals proactive opportunity.

Vehicle Analysis:
- No active prognostics or overdue maintenance
- STRESSOR-ONLY opportunity: {stressor_context}
- Risk level: {risk_level} ({risk_score:.1f}%)
- Proactive service value: Fleet health check ${total_cost//3} prevents future ${total_cost * 2} emergency

Requirements:
- Focus on PROACTIVE intervention before problems occur
- Emphasize preventing expensive future failures
- Use stressor patterns to create urgency without existing issues
- Position as smart preventive maintenance
- Reference commercial/fleet usage implications

Return ONLY the 3 messages, one per line, no numbering or bullets."""
            
            logger.info(f"🤖 Making OpenAI API call for {customer_name} - {channel} channel")
            
            # Synchronous OpenAI call that actually works
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert automotive service advisor. Create personalized, professional messages that build trust and demonstrate expertise. Use specific technical details but keep language accessible. Return only the requested messages, no extra text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            logger.info(f"✅ OpenAI API call successful for {customer_name}")
            
            # Parse response into individual messages
            content = response.choices[0].message.content.strip()
            messages = [msg.strip() for msg in content.split('\n') if msg.strip() and len(msg.strip()) > 20]
            
            # Ensure we have exactly 3 messages
            if len(messages) < 3:
                # Split by periods or sentences if not enough lines
                sentences = [s.strip() + '.' for s in content.replace('\n', ' ').split('.') if s.strip()]
                messages = sentences[:3] if len(sentences) >= 3 else [content]
            
            return {
                "messages": messages[:3],  # Ensure max 3 messages
                "risk_level": risk_level,
                "personalized": True
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI API error for {customer_name}: {str(e)}")
            logger.error(f"❌ Full error details: {type(e).__name__}: {e}")
            return self._fallback_messages(customer_name, vehicle_info, stressors, risk_score)
    
    def _fallback_messages(self, customer_name: str, vehicle_info: str, 
                          stressors: List[str], risk_score: float) -> Dict[str, List[str]]:
        """Fallback messages when AI is unavailable"""
        risk_level = "CRITICAL" if risk_score >= 50 else "HIGH" if risk_score >= 30 else "MODERATE"
        
        return {
            "messages": [
                f"{customer_name}, your {vehicle_info} shows {len(stressors)} stress factors that need attention",
                f"Our analysis indicates {risk_score:.1f}% failure risk - let's prevent a breakdown",
                f"Academic research shows this pattern leads to issues within weeks"
            ],
            "risk_level": risk_level,
            "personalized": False
        }

# Initialize AI message generator
ai_generator = AIMessageGenerator()

# Clean, professional HTML template with AI integration
CLEAN_INTERFACE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIN Stressors - Vehicle Intelligence Platform</title>
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1d1d1f;
            line-height: 1.47059;
            margin: 0;
            min-height: 100vh;
        }
        
        .container { 
            max-width: 390px; 
            margin: 0 auto; 
            min-height: 100vh;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(20px);
            border-radius: 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        }
        
        /* DESKTOP RESPONSIVE OVERRIDES */
        @media (min-width: 768px) {
            .container {
                max-width: 1200px;
                padding: 0 32px;
                border-radius: 16px;
                margin: 20px auto;
            }
            
            .header {
                padding: 40px 32px 32px;
            }
            
            .tab-content {
                padding: 0 32px 40px;
            }
        }
        
        @media (min-width: 1200px) {
            .container {
                max-width: 1400px;
                padding: 0 48px;
            }
        }
        
        .header { 
            background: transparent;
            padding: 60px 32px 40px;
            text-align: center;
            color: #1d1d1f;
            position: relative;
        }
        
        .logo { 
            font-size: 32px; 
            font-weight: 700; 
            letter-spacing: -0.022em;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle { 
            font-size: 17px; 
            opacity: 0.7;
            font-weight: 400;
            margin-bottom: 16px;
            letter-spacing: -0.022em;
        }
        
        .version-badge {
            background: rgba(102,126,234,0.1);
            color: #667eea;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            display: inline-block;
            border: 1px solid rgba(102,126,234,0.2);
            letter-spacing: -0.01em;
        }
        
        .tab-nav { 
            background: rgba(255,255,255,0.5);
            backdrop-filter: blur(20px);
            display: flex; 
            margin: 0 20px 20px;
            border-radius: 12px;
            padding: 4px;
            border: 1px solid rgba(0,0,0,0.04);
        }
        
        .tab-btn { 
            flex: 1; 
            padding: 12px 16px;
            background: transparent; 
            border: none; 
            color: #86868b;
            font-weight: 500; 
            font-size: 15px;
            cursor: pointer; 
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            border-radius: 8px;
            letter-spacing: -0.01em;
        }
        
        .tab-btn.active { 
            color: #1d1d1f;
            background: rgba(255,255,255,0.9);
            box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
            transform: scale(1.02);
        }
        
        .tab-content { 
            display: none !important; 
            padding: 0 20px 40px;
        }
        
        .tab-content.active { 
            display: block !important; 
        }
        
        /* Premium Apple-Style Cards */
        .card { 
            background: rgba(255,255,255,0.9); 
            backdrop-filter: blur(20px);
            border-radius: 16px; 
            padding: 32px 24px;
            margin-bottom: 24px;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 4px 16px rgba(0,0,0,0.04), 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.08), 0 4px 10px rgba(0,0,0,0.04);
        }
        
        /* Premium Learning Cards */
        .learning-card { 
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 20px; 
            margin-bottom: 20px;
            cursor: pointer; 
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            position: relative;
            height: 220px;
            perspective: 1000px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.02);
        }
        
        /* Desktop Grid Layout for Learning Cards */
        .learning-grid {
            display: block; /* Default mobile */
        }
        
        @media (min-width: 768px) {
            .learning-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 24px;
            }
            
            .learning-card {
                margin-bottom: 0;
                height: auto;
                min-height: 220px;
            }
        }
        
        @media (min-width: 1200px) {
            .learning-grid {
                grid-template-columns: repeat(4, 1fr);
                gap: 24px;
            }
            
            .learning-card {
                height: 180px;
                min-height: 180px;
            }
        }
        
        .learning-card:hover {
            border-color: rgba(102,126,234,0.4);
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 12px 40px rgba(102,126,234,0.12), 0 4px 12px rgba(102,126,234,0.08);
        }
        
        .card-inner { 
            position: relative;
            width: 100%; 
            height: 100%;
            transition: transform 0.6s;
            transform-style: preserve-3d;
        }
        
        .learning-card.flipped .card-inner { 
            transform: rotateY(180deg); 
        }
        
        .card-front, .card-back { 
            position: absolute;
            width: 100%; 
            height: 100%;
            backface-visibility: hidden;
            top: 0;
            left: 0;
            padding: 16px;
            box-sizing: border-box;
            border-radius: 12px;
        }
        
        @media (min-width: 1200px) {
            .card-front, .card-back {
                padding: 12px;
            }
        }
        
        .card-front {
            background: white;
            z-index: 2;
        }
        
        .card-back { 
            transform: rotateY(180deg);
            background: #f8fafc;
            z-index: 1;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;  /* iOS smooth scrolling */
            touch-action: pan-y;  /* Allow vertical scrolling on mobile */
        }
        
        .flip-indicator { 
            position: absolute;
            top: 16px; 
            right: 16px;
            background: rgba(102,126,234,0.15);
            color: #667eea; 
            padding: 6px 10px;
            border-radius: 20px; 
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.02em;
            border: 1px solid rgba(102,126,234,0.2);
            backdrop-filter: blur(10px);
        }
        
        .card-title { 
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #1d1d1f;
            letter-spacing: -0.022em;
            line-height: 1.2;
        }
        
        @media (min-width: 1200px) {
            .card-title {
                font-size: 16px;
                margin-bottom: 8px;
            }
        }
        
        .card-description {
            font-size: 13px;
            color: #86868b;
            line-height: 1.4;
            letter-spacing: -0.01em;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        @media (min-width: 1200px) {
            .card-description {
                font-size: 12px;
                line-height: 1.3;
            }
        }
        
        .math-content { 
            font-family: 'SF Mono', 'Monaco', monospace;
            font-size: 12px;
            color: #4a5568;
        }
        
        .math-formula { 
            background: #edf2f7;
            padding: 12px;
            border-radius: 6px;
            margin: 8px 0;
            border-left: 3px solid #667eea;
            font-weight: 500;
        }
        
        /* Form Elements */
        .form-group { 
            margin-bottom: 20px; 
        }
        
        label { 
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #374151;
            font-size: 14px;
        }
        
        input[type="text"] { 
            width: 100%;
            padding: 14px 16px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.2s;
            background: white;
        }
        
        input[type="text"]:focus { 
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        
        .btn { 
            width: 100%;
            padding: 14px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .btn:hover { 
            background: #5a6fd8;
        }
        
        .demo-grid { 
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 16px;
        }
        
        /* Desktop Layout for Calculator Tab */
        @media (min-width: 968px) {
            .calculator-layout {
                display: grid;
                grid-template-columns: 400px 1fr;
                gap: 32px;
                align-items: start;
            }
            
            .demo-grid {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        /* Desktop Layout for Engagement Tab */
        @media (min-width: 768px) {
            .engagement-layout {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 24px;
            }
        }
        
        @media (min-width: 1200px) {
            .engagement-layout {
                grid-template-columns: 1fr 1fr 300px;
                gap: 32px;
            }
        }
        
        .demo-btn { 
            padding: 12px 8px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 12px;
            font-family: monospace;
            color: #4a5568;
        }
        
        .demo-btn:hover { 
            background: #e2e8f0;
            border-color: #667eea;
        }
        
        /* Results */
        .result-card { 
            margin-top: 20px;
            display: none;
            border: 1px solid #e2e8f0;
        }
        
        .risk-score { 
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin: 16px 0;
            color: #1a202c;
        }
        
        .severity-badge { 
            display: block;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            text-align: center;
            margin: 12px 0;
        }
        
        .detail-row { 
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f1f5f9;
        }
        
        .detail-row:last-child {
            border-bottom: none;
        }
        
        .detail-label { 
            font-weight: 500;
            color: #64748b;
            font-size: 14px;
        }
        
        .detail-value { 
            font-weight: 600;
            color: #1a202c;
            font-size: 14px;
        }
        
        /* AI-Enhanced Engagement Portal */
        .lead-card { 
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }
        
        .lead-header { 
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        
        .customer-name { 
            font-size: 16px;
            font-weight: 600;
            color: #1a202c;
        }
        
        .priority-badge { 
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .priority-critical { 
            background: #fee2e2;
            color: #991b1b;
        }
        
        .priority-high { 
            background: #fef3c7;
            color: #92400e;
        }
        
        .vehicle-info { 
            font-size: 13px;
            color: #64748b;
            margin-bottom: 12px;
        }
        
        .issue-type { 
            background: #fee2e2;
            color: #991b1b;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            display: inline-block;
            margin-bottom: 12px;
        }
        
        .engagement-channels {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
            margin: 12px 0;
        }
        
        .channel-btn {
            padding: 8px 12px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            text-align: center;
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .channel-btn:hover {
            border-color: #667eea;
            background: #f8fafc;
        }
        
        .channel-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .ai-messages { 
            background: #f8fafc;
            border-radius: 8px;
            padding: 16px;
            margin-top: 12px;
            min-height: 80px;
        }
        
        .ai-messages-title { 
            font-size: 12px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .ai-badge {
            background: #667eea;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
        }
        
        .ai-message { 
            font-size: 12px;
            color: #4b5563;
            margin-bottom: 6px;
            padding: 8px 12px;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #667eea;
            line-height: 1.4;
        }
        
        .loading-messages {
            text-align: center;
            color: #64748b;
            font-style: italic;
            padding: 20px;
        }
        
        .revenue-estimate { 
            background: #ecfdf5;
            color: #059669;
            padding: 10px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            text-align: center;
            margin-top: 12px;
        }
        
        /* Analytics Dashboard Styles */
        .analytics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 0 20px 40px;
        }
        
        @media (max-width: 768px) {
            .analytics-grid {
                grid-template-columns: 1fr;
                gap: 16px;
                padding: 0 15px 30px;
            }
        }
        
        .analytics-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #e5e7eb;
        }
        
        .wide-card {
            grid-column: span 2;
        }
        
        @media (max-width: 768px) {
            .wide-card {
                grid-column: span 1;
            }
        }
        
        .insight-card {
            grid-column: span 2;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .insight-card .card-title {
            color: white;
        }
        
        .funnel-stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-top: 16px;
        }
        
        @media (max-width: 600px) {
            .funnel-stats {
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
            }
        }
        
        .stat {
            text-align: center;
            padding: 12px;
            background: #f8fafc;
            border-radius: 8px;
        }
        
        .stat-number {
            display: block;
            font-size: 18px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 12px;
            color: #6b7280;
            font-weight: 500;
        }
        
        .weather-legend, .complaint-summary {
            margin-top: 16px;
            font-size: 12px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 3px;
            margin-right: 8px;
        }
        
        .complaint-summary {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            color: #6b7280;
        }
        
        .revenue-breakdown {
            margin-top: 16px;
        }
        
        .revenue-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .revenue-item:last-child {
            border-bottom: none;
            font-weight: 600;
            color: #059669;
        }
        
        .revenue-label {
            color: #6b7280;
            font-size: 13px;
        }
        
        .revenue-value {
            font-weight: 600;
            color: #1f2937;
        }
        
        .scoring-summary {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-top: 16px;
        }
        
        @media (max-width: 600px) {
            .scoring-summary {
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
            }
        }
        
        .score-stat {
            text-align: center;
            padding: 12px;
            background: #f8fafc;
            border-radius: 8px;
        }
        
        .score-number {
            font-size: 16px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 4px;
        }
        
        .score-label {
            font-size: 10px;
            color: #6b7280;
            line-height: 1.3;
        }
        
        .insight-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        
        @media (max-width: 600px) {
            .insight-grid {
                grid-template-columns: 1fr;
                gap: 12px;
            }
        }
        
        .insight-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 16px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
        
        .insight-icon {
            font-size: 20px;
            min-width: 24px;
        }
        
        .insight-title {
            font-weight: 600;
            margin-bottom: 4px;
            font-size: 13px;
        }
        
        .insight-desc {
            font-size: 12px;
            opacity: 0.9;
            line-height: 1.4;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">VIN Stressors</div>
            <div class="subtitle">AI-Powered Vehicle Intelligence Platform</div>
            <div class="version-badge">Currently Testing: ABTest2 - Conversion Optimized</div>
        </div>
        
        <div class="tab-nav">
            <button class="tab-btn active" onclick="switchTab('intelligence')">Intelligence</button>
            <button class="tab-btn" onclick="switchTab('calculator')">Calculator</button>
            <button class="tab-btn" onclick="switchTab('engagement')">Engagement</button>
            <button class="tab-btn" onclick="switchTab('analytics')">Analytics</button>
        </div>
        
        <!-- Intelligence Tab -->
        <div id="intelligence-tab" class="tab-content active">
            <div class="learning-grid">
                <div class="learning-card" onclick="flipCard(this)">
                <div class="flip-indicator">Flip</div>
                <div class="card-inner">
                    <div class="card-front">
                        <div class="card-title">Academic Foundation</div>
                        <div class="card-description">
                            Peer-reviewed Argonne research provides scientifically-backed priors and 
                            likelihood ratios for vehicle battery failure prediction.
                        </div>
                    </div>
                    <div class="card-back">
                        <div class="math-content">
                            <div class="math-formula">
                                <strong>REALITY: Ford Has a Battery Problem</strong><br/>
                                Batteries failing in years 1-3 (not normal)<br/>
                                NHTSA complaints increasing (we're on their radar)<br/>
                                Need scientific cover for systematic outreach<br/>
                                Can't just tell dealers "old batteries fail"
                            </div>
                            <div class="math-formula">
                                <strong>WHAT WE ACTUALLY DO:</strong><br/>
                                Take obvious stressors (cold, heat, short trips)<br/>
                                Add Argonne research to make it sound scientific<br/>
                                Generate prioritized call lists for dealers<br/>
                                Create audit trail for NHTSA compliance
                            </div>
                            <div class="math-formula">
                                <strong>THE MATH IS SIMPLE:</strong><br/>
                                3+ stressors + 2+ years = call customer<br/>
                                Regional weather + high mileage = higher priority<br/>
                                Bayesian framework makes it look sophisticated<br/>
                                But it's basically "old truck in winter needs battery"
                            </div>
                            <div class="math-formula">
                                <strong>WHY IT WORKS:</strong><br/>
                                Dealers need systematic approach (not gut feeling)<br/>
                                Customers respond better to "data-driven" outreach<br/>
                                Regulators want to see scientific methodology<br/>
                                Everyone knows it's true, we just quantify it
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="learning-card" onclick="flipCard(this)">
                <div class="flip-indicator">Flip</div>
                <div class="card-inner">
                    <div class="card-front">
                        <div class="card-title">AI-Powered Personalization</div>
                        <div class="card-description">
                            AI-powered messaging that adapts to specific vehicle stressor patterns 
                            for higher customer engagement and conversion rates.
                        </div>
                    </div>
                    <div class="card-back">
                        <div class="math-content">
                            <div class="math-formula">
                                <strong>HONEST TRUTH ABOUT AI MESSAGING:</strong><br/>
                                • We use GPT-4 to make battery warnings sound less spammy<br/>
                                • "Your F-150 needs attention" vs "BATTERY SALE NOW!"<br/>
                                • Different tone for rural vs urban customers<br/>
                                • It's still a sales call, just sounds more professional
                            </div>
                            <div class="math-formula">
                                <strong>WHAT THE AI ACTUALLY DOES:</strong><br/>
                                Input: VIN + customer ZIP + stressor data<br/>
                                Process: Generate "data-driven" talking points<br/>
                                Output: Messages that sound smart, not pushy<br/>
                                Reality: We're selling batteries with fancy language
                            </div>
                            <div class="math-formula">
                                <strong>WHY THIS HELPS DEALERS:</strong><br/>
                                • Asheville customers want simple, direct approach<br/>
                                • Miami customers expect more technical detail<br/>
                                • AI adjusts the pitch, but it's still a pitch<br/>
                                • Converts better than "Hey, buy a battery"
                            </div>
                            <div class="math-formula">
                                <strong>BOTTOM LINE:</strong><br/>
                                We're not revolutionizing automotive service messaging<br/>
                                We're just making battery sales calls less awkward<br/>
                                And giving dealers confidence to make the call<br/>
                                Because Ford needs these batteries replaced
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="learning-card" onclick="flipCard(this)">
                <div class="flip-indicator">Flip</div>
                <div class="card-inner">
                    <div class="card-front">
                        <div class="card-title">OEM Data Advantage</div>
                        <div class="card-description">
                            Direct access to manufacturer data, real-time parts pricing, 
                            and dealer network insights that independent shops cannot access.
                        </div>
                    </div>
                    <div class="card-back">
                        <div class="math-content">
                            <div class="math-formula">
                                <strong>WHAT WE ACTUALLY HAVE:</strong><br/>
                                • Standard Ford dealer pricing (not special API)<br/>
                                • Basic parts availability (what dealers already see)<br/>
                                • VIN data from beta dealers who gave it to us<br/>
                                • NHTSA complaints we scraped from public database
                            </div>
                            <div class="math-formula">
                                <strong>WHAT WE DON'T HAVE:</strong><br/>
                                • 50 million vehicle real-time data feed<br/>
                                • Proprietary Ford failure pattern database<br/>
                                • Direct integration to dealer management systems<br/>
                                • Real-time inventory optimization algorithms
                            </div>
                            <div class="math-formula">
                                <strong>OUR ACTUAL ADVANTAGE:</strong><br/>
                                Independent shops: Don't care about Ford's problems<br/>
                                Chain shops: Not motivated to help with recalls<br/>
                                Ford dealers: Need systematic approach to battery calls<br/>
                                Us: We package obvious patterns as "intelligence"
                            </div>
                            <div class="math-formula">
                                <strong>REALITY CHECK:</strong><br/>
                                • Small dealers just want prioritized call lists<br/>
                                • Parts managers order based on historical data<br/>
                                • Service advisors use standard Ford pricing<br/>
                                • This gives them confidence to make proactive calls
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="learning-card" onclick="flipCard(this)">
                <div class="flip-indicator">Flip</div>
                <div class="card-inner">
                    <div class="card-front">
                        <div class="card-title">Strategic Cohort Targeting</div>
                        <div class="card-description">
                            Strategic vehicle cohorts designed for dealer lead generation using 
                            stressor analysis to identify high-value service opportunities.
                        </div>
                    </div>
                    <div class="card-back">
                        <div class="math-content">
                            <div class="math-formula">
                                <strong>OUR COHORTS ARE COMMON SENSE:</strong><br/>
                                • Light Truck + Winter = "Trucks in cold get dead batteries"<br/>
                                • SUV + Heat = "Big vehicles in Arizona stress batteries"<br/>
                                • Sedan + Urban = "City driving with lots of stops"<br/>
                                • We just made it sound scientific with percentages
                            </div>
                            <div class="math-formula">
                                <strong>THE "THREAT DETECTION" LOGIC:</strong><br/>
                                3+ years old + cold climate + high miles = call them<br/>
                                2+ years old + hot climate + commercial use = call them<br/>
                                It's not AI magic, it's basic automotive knowledge<br/>
                                But dealers need systematic way to prioritize
                            </div>
                            <div class="math-formula">
                                <strong>WHAT DEALERS ACTUALLY GET:</strong><br/>
                                • List of customers to call this week<br/>
                                • Basic talking points ("your battery is at risk")<br/>
                                • Pricing from standard Ford parts catalog<br/>
                                • Confidence that the calls make business sense
                            </div>
                            <div class="math-formula">
                                <strong>WHY THIS WORKS FOR FORD:</strong><br/>
                                • Gets ahead of NHTSA complaints<br/>
                                • Creates paper trail of proactive outreach<br/>
                                • Helps dealers sell more batteries systematically<br/>
                                • Solves Ford's "batteries failing too early" problem
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            </div>
        </div>
        
        <!-- Calculator Tab -->
        <div id="calculator-tab" class="tab-content">
            <div class="calculator-layout">
                <div class="card">
                <form id="riskForm">
                    <div class="form-group">
                        <label for="vin">Vehicle Identification Number</label>
                        <input type="text" id="vin" name="vin" placeholder="Enter 17-character VIN" maxlength="17" required>
                    </div>
                    <button type="submit" class="btn">Analyze Stressors</button>
                </form>
                
                <div class="demo-grid">
                    <div class="demo-btn" onclick="setDemoVin('1FTFW1ET0LFA12345')">Truck Demo</div>
                    <div class="demo-btn" onclick="setDemoVin('1FMHK8D83LGA89012')">SUV Demo</div>
                    <div class="demo-btn" onclick="setDemoVin('3FA6P0HR8LR345678')">Sedan Demo</div>
                    <div class="demo-btn" onclick="setDemoVin('1FA6P8TH4J5456789')">Sports Demo</div>
                </div>
            </div>
            
            <div class="card result-card" id="result">
                <div class="risk-score" id="riskScore">0.0%</div>
                <div class="severity-badge" id="severityBadge">Analyzing...</div>
                <div class="detail-row">
                    <span class="detail-label">Vehicle Category</span>
                    <span class="detail-value" id="category">-</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">vs Category Average</span>
                    <span class="detail-value" id="comparison">-</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Service Opportunity</span>
                    <span class="detail-value" id="revenue">-</span>
                </div>
            </div>
            </div>
        </div>
        
        <!-- Analytics Dashboard Tab -->
        <div id="analytics-tab" class="tab-content">
            <div class="analytics-grid">
                <div class="analytics-card">
                    <div class="card-title">🎯 Battery Problem Lead Funnel</div>
                    <div style="height: 300px; position: relative;">
                        <canvas id="funnelChart"></canvas>
                    </div>
                    <div class="funnel-stats">
                        <div class="stat"><span class="stat-number">5,000</span><span class="stat-label">Total VINs</span></div>
                        <div class="stat"><span class="stat-number">2,927</span><span class="stat-label">High Stress</span></div>
                        <div class="stat"><span class="stat-number">866</span><span class="stat-label">Call Today</span></div>
                        <div class="stat"><span class="stat-number">$1.06M</span><span class="stat-label">Revenue</span></div>
                    </div>
                </div>
                
                <div class="analytics-card">
                    <div class="card-title">🌡️ Weather Risk Distribution</div>
                    <div style="height: 250px; position: relative;">
                        <canvas id="weatherChart"></canvas>
                    </div>
                    <div class="weather-legend">
                        <div class="legend-item"><span class="legend-color" style="background: #dc3545;"></span>High Risk (35°F+ delta)</div>
                        <div class="legend-item"><span class="legend-color" style="background: #ffc107;"></span>Moderate (25-35°F)</div>
                        <div class="legend-item"><span class="legend-color" style="background: #28a745;"></span>Low Risk (<25°F)</div>
                    </div>
                </div>
                
                <div class="analytics-card">
                    <div class="card-title">📍 NHTSA Complaint Hotspots</div>
                    <div style="height: 250px; position: relative;">
                        <canvas id="complaintChart"></canvas>
                    </div>
                    <div class="complaint-summary">
                        <div>FL: 4 complaints</div>
                        <div>TX: 3 complaints</div>
                        <div>MI: 2 complaints</div>
                        <div>June surge: 10 complaints</div>
                    </div>
                </div>
                
                <div class="analytics-card">
                    <div class="card-title">💰 Revenue Pipeline Analysis</div>
                    <div style="height: 250px; position: relative;">
                        <canvas id="revenueChart"></canvas>
                    </div>
                    <div class="revenue-breakdown">
                        <div class="revenue-item">
                            <span class="revenue-label">Immediate Action</span>
                            <span class="revenue-value">$184,552</span>
                        </div>
                        <div class="revenue-item">
                            <span class="revenue-label">30-Day Pipeline</span>
                            <span class="revenue-value">$682,932</span>
                        </div>
                        <div class="revenue-item">
                            <span class="revenue-label">Total Opportunity</span>
                            <span class="revenue-value">$1,066,415</span>
                        </div>
                    </div>
                </div>
                
                <div class="analytics-card wide-card">
                    <div class="card-title">📊 Lead Scoring Distribution</div>
                    <div style="height: 200px; position: relative;">
                        <canvas id="scoringChart"></canvas>
                    </div>
                    <div class="scoring-summary">
                        <div class="score-stat">
                            <div class="score-number">17.3%</div>
                            <div class="score-label">Immediate Action<br/>(60%+ Risk)</div>
                        </div>
                        <div class="score-stat">
                            <div class="score-number">64.1%</div>
                            <div class="score-label">Pipeline<br/>(30-60% Risk)</div>
                        </div>
                        <div class="score-stat">
                            <div class="score-number">18.6%</div>
                            <div class="score-label">Monitor<br/>(0-30% Risk)</div>
                        </div>
                        <div class="score-stat">
                            <div class="score-number">±3.9°F</div>
                            <div class="score-label">Weather<br/>Accuracy</div>
                        </div>
                    </div>
                </div>
                
                <div class="analytics-card insight-card">
                    <div class="card-title">🧠 AI Intelligence Insights</div>
                    <div class="insight-grid">
                        <div class="insight-item">
                            <div class="insight-icon">⚡</div>
                            <div class="insight-text">
                                <div class="insight-title">Seasonal Pattern Alert</div>
                                <div class="insight-desc">June shows 5x normal complaint volume - proactive outreach recommended</div>
                            </div>
                        </div>
                        <div class="insight-item">
                            <div class="insight-icon">🎯</div>
                            <div class="insight-text">
                                <div class="insight-title">High-Value Targets</div>
                                <div class="insight-desc">Commercial SUVs in GA/NC show 68% risk scores - immediate revenue opportunity</div>
                            </div>
                        </div>
                        <div class="insight-item">
                            <div class="insight-icon">📈</div>
                            <div class="insight-text">
                                <div class="insight-title">Conversion Opportunity</div>
                                <div class="insight-desc">866 leads ready for immediate contact - $213 average revenue per lead</div>
                            </div>
                        </div>
                        <div class="insight-item">
                            <div class="insight-icon">🌡️</div>
                            <div class="insight-text">
                                <div class="insight-title">Climate Intelligence</div>
                                <div class="insight-desc">7/8 states show 35°F+ temperature swings - battery stress correlation confirmed</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- AI-Enhanced Engagement Tab -->
        <div id="engagement-tab" class="tab-content">
            <div class="engagement-layout">
                <div class="lead-card">
                <div class="lead-header">
                    <div class="customer-name">Sarah Johnson</div>
                    <div class="priority-badge priority-critical">URGENT</div>
                </div>
                <div class="vehicle-info">2022 Light Truck • VIN: 1FTFW1ET5LFA67890 • 47,823 miles</div>
                <div class="issue-type">Scheduled Service + Battery Risk (3.3x Above Cohort)</div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 12px; margin: 12px 0;">
                    <div style="font-size: 12px; font-weight: 600; color: #856404; margin-bottom: 6px;">📋 EXISTING PROGNOSTICS:</div>
                    <div style="font-size: 11px; color: #856404;">• Oil change due (3,200 miles overdue)</div>
                    <div style="font-size: 11px; color: #856404;">• Tire rotation recommended</div>
                </div>
                
                <div style="background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; padding: 12px; margin: 12px 0;">
                    <div style="font-size: 12px; font-weight: 600; color: #721c24; margin-bottom: 6px;">⚡ STRESSOR ANALYSIS:</div>
                    <div style="font-size: 11px; color: #721c24;">• Winter + short trips + high ignition cycles</div>
                    <div style="font-size: 11px; color: #721c24;">• Battery stress: 85th percentile vs cohort</div>
                </div>
                
                <div class="engagement-channels">
                    <div class="channel-btn active" onclick="switchChannel(this, 'sms', 'sarah')">📱 SMS</div>
                    <div class="channel-btn" onclick="switchChannel(this, 'email', 'sarah')">📧 Email</div>
                    <div class="channel-btn" onclick="switchChannel(this, 'phone', 'sarah')">📞 Call</div>
                </div>
                
                <div class="ai-messages" id="sarah-messages">
                    <div class="ai-messages-title">
                        <span>Integrated Service Messaging</span>
                        <span class="ai-badge">GPT-4</span>
                    </div>
                    <div class="loading-messages">Generating bundled service messaging...</div>
                </div>
                
                <div style="background: #d1ecf1; border: 1px solid #bee5eb; border-radius: 8px; padding: 12px; margin: 12px 0; text-align: center;">
                    <div style="font-size: 12px; font-weight: 600; color: #0c5460; margin-bottom: 4px;">💰 BUNDLED SERVICE OPPORTUNITY</div>
                    <div style="font-size: 13px; color: #0c5460;">Oil Service $85 + Battery Check $125 + Tire Rotation $45 = <strong>$255</strong></div>
                    <div style="font-size: 11px; color: #0c5460; margin-top: 4px;">vs. separate visits: $85 + $280 + $45 = $410</div>
                </div>
            </div>
            
            <div class="lead-card">
                <div class="lead-header">
                    <div class="customer-name">Mike Rodriguez</div>
                    <div class="priority-badge priority-high">HIGH</div>
                </div>
                <div class="vehicle-info">2023 SUV • VIN: 1FMHK8D83LGA89012 • 23,456 miles</div>
                <div class="issue-type">Fleet Usage + Multiple Stress Factors</div>
                
                <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 12px; margin: 12px 0;">
                    <div style="font-size: 12px; font-weight: 600; color: #155724; margin-bottom: 6px;">✅ NO ACTIVE PROGNOSTICS</div>
                    <div style="font-size: 11px; color: #155724;">• Next scheduled maintenance: 2,800 miles</div>
                    <div style="font-size: 11px; color: #155724;">• All systems currently within normal parameters</div>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 12px; margin: 12px 0;">
                    <div style="font-size: 12px; font-weight: 600; color: #856404; margin-bottom: 6px;">⚠️ STRESSOR-ONLY OPPORTUNITY:</div>
                    <div style="font-size: 11px; color: #856404;">• Commercial usage patterns detected</div>
                    <div style="font-size: 11px; color: #856404;">• Multiple driver stress indicators</div>
                    <div style="font-size: 11px; color: #856404;">• Proactive intervention recommended</div>
                </div>
                
                <div class="engagement-channels">
                    <div class="channel-btn active" onclick="switchChannel(this, 'sms', 'mike')">📱 SMS</div>
                    <div class="channel-btn" onclick="switchChannel(this, 'email', 'mike')">📧 Email</div>
                    <div class="channel-btn" onclick="switchChannel(this, 'phone', 'mike')">📞 Call</div>
                </div>
                
                <div class="ai-messages" id="mike-messages">
                    <div class="ai-messages-title">
                        <span>Proactive Outreach Messaging</span>
                        <span class="ai-badge">GPT-4</span>
                    </div>
                    <div class="loading-messages">Generating proactive service messaging...</div>
                </div>
                
                <div style="background: #e2e3e5; border: 1px solid #d6d8db; border-radius: 8px; padding: 12px; margin: 12px 0; text-align: center;">
                    <div style="font-size: 12px; font-weight: 600; color: #383d41; margin-bottom: 4px;">🔮 PROACTIVE SERVICE OPPORTUNITY</div>
                    <div style="font-size: 13px; color: #383d41;">Fleet Health Check $145 • Early Intervention Value</div>
                    <div style="font-size: 11px; color: #383d41; margin-top: 4px;">Prevents future $800+ emergency service</div>
                </div>
            </div>
            
            <div style="background: #e9ecef; border-radius: 12px; padding: 16px; margin-top: 20px;">
                <div style="font-size: 14px; font-weight: 600; color: #495057; margin-bottom: 12px; text-align: center;">📊 LEAD QUEUE INTELLIGENCE</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; text-align: center;">
                    <div style="background: #fff; border-radius: 8px; padding: 12px;">
                        <div style="font-size: 18px; font-weight: 700; color: #dc3545;">12</div>
                        <div style="font-size: 11px; color: #6c757d;">URGENT Leads</div>
                        <div style="font-size: 10px; color: #6c757d;">Existing + Stressors</div>
                    </div>
                    <div style="background: #fff; border-radius: 8px; padding: 12px;">
                        <div style="font-size: 18px; font-weight: 700; color: #fd7e14;">8</div>
                        <div style="font-size: 11px; color: #6c757d;">HIGH Priority</div>
                        <div style="font-size: 10px; color: #6c757d;">Stressor-Only</div>
                    </div>
                    <div style="background: #fff; border-radius: 8px; padding: 12px;">
                        <div style="font-size: 18px; font-weight: 700; color: #28a745;">34</div>
                        <div style="font-size: 11px; color: #6c757d;">NORMAL Queue</div>
                        <div style="font-size: 10px; color: #6c757d;">Routine Follow-up</div>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 12px; font-size: 12px; color: #6c757d;">
                    💡 Stressors enhance existing prognostics + create new opportunities
                </div>
                <div style="text-align: center; margin-top: 8px; font-size: 10px; color: #6c757d; font-style: italic;">
                    📊 ABTest2: Tracking conversion rates - 23% higher close rate vs ABTest1
                </div>
            </div>
            </div>
        </div>
    </div>

    <script>
        // AI message cache to avoid redundant API calls
        const messageCache = {};
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
            
            // Load AI messages when engagement tab is opened
            if (tabName === 'engagement') {
                loadAIMessages('sarah', 'sms');
                loadAIMessages('mike', 'sms');
            }
            
            // Initialize charts when analytics tab is opened
            if (tabName === 'analytics') {
                setTimeout(initializeCharts, 100);
            }
        }
        
        // Chart initialization
        let chartsInitialized = false;
        
        function initializeCharts() {
            if (chartsInitialized) return;
            chartsInitialized = true;
            
            // Battery Problem Lead Funnel Chart
            const funnelCtx = document.getElementById('funnelChart').getContext('2d');
            new Chart(funnelCtx, {
                type: 'bar',
                data: {
                    labels: ['Total VINs', 'High Stress', 'Medium Risk', 'Call Today'],
                    datasets: [{
                        label: 'Lead Funnel',
                        data: [5000, 2927, 3204, 866],
                        backgroundColor: [
                            '#e5e7eb',
                            '#fbbf24',
                            '#f59e0b',
                            '#dc2626'
                        ],
                        borderColor: '#374151',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
            
            // Weather Risk Distribution Chart
            const weatherCtx = document.getElementById('weatherChart').getContext('2d');
            new Chart(weatherCtx, {
                type: 'doughnut',
                data: {
                    labels: ['High Risk (7 states)', 'Low Risk (FL)'],
                    datasets: [{
                        data: [7, 1],
                        backgroundColor: ['#dc3545', '#28a745'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { font: { size: 11 } }
                        }
                    }
                }
            });
            
            // NHTSA Complaint Hotspots Chart
            const complaintCtx = document.getElementById('complaintChart').getContext('2d');
            new Chart(complaintCtx, {
                type: 'bar',
                data: {
                    labels: ['FL', 'TX', 'MI', 'Others'],
                    datasets: [{
                        label: 'Complaints',
                        data: [4, 3, 2, 11],
                        backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#6c757d'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
            
            // Revenue Pipeline Analysis Chart
            const revenueCtx = document.getElementById('revenueChart').getContext('2d');
            new Chart(revenueCtx, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Month 2', 'Month 3'],
                    datasets: [{
                        label: 'Cumulative Revenue',
                        data: [184552, 365104, 547656, 682932, 874281, 1066415],
                        borderColor: '#059669',
                        backgroundColor: 'rgba(5, 150, 105, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + (value / 1000).toFixed(0) + 'K';
                                }
                            }
                        }
                    }
                }
            });
            
            // Lead Scoring Distribution Chart
            const scoringCtx = document.getElementById('scoringChart').getContext('2d');
            new Chart(scoringCtx, {
                type: 'bar',
                data: {
                    labels: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'],
                    datasets: [{
                        label: 'Lead Distribution',
                        data: [930, 1602, 1602, 433, 433],
                        backgroundColor: [
                            '#28a745',
                            '#ffc107',
                            '#fd7e14',
                            '#dc3545',
                            '#6f42c1'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        }
        
        function flipCard(card) {
            card.classList.toggle('flipped');
        }
        
        function setDemoVin(vin) {
            document.getElementById('vin').value = vin;
            calculateRisk(vin);
        }
        
        function calculateRisk(vin) {
            document.getElementById('result').style.display = 'block';
            
            let riskScore, category, comparison, partsRevenue, serviceRevenue, totalRevenue;
            
            if (vin.includes('1FTFW1ET')) {
                riskScore = 49.3;
                category = "Light Truck";
                comparison = "3.3x above average";
                // F-150 battery service pricing
                partsRevenue = 280;  // Heavy duty battery + terminals
                serviceRevenue = 125; // Testing, installation, system check
                totalRevenue = partsRevenue + serviceRevenue;
            } else if (vin.includes('1FMHK8D8')) {
                riskScore = 68.6;
                category = "SUV Commercial";
                comparison = "2.8x above average";
                // Commercial SUV pricing
                partsRevenue = 320;  // Premium commercial battery
                serviceRevenue = 145; // Extended testing, fleet documentation
                totalRevenue = partsRevenue + serviceRevenue;
            } else if (vin.includes('3FA6P0HR')) {
                riskScore = 14.2;
                category = "Passenger Sedan";
                comparison = "1.6x above average";
                // Standard sedan pricing
                partsRevenue = 180;  // Standard battery
                serviceRevenue = 85;  // Basic service
                totalRevenue = partsRevenue + serviceRevenue;
            } else {
                riskScore = 28.7;
                category = "Performance Vehicle";
                comparison = "2.1x above average";
                // Performance vehicle pricing
                partsRevenue = 250;  // High-performance battery
                serviceRevenue = 110; // Performance system check
                totalRevenue = partsRevenue + serviceRevenue;
            }
            
            document.getElementById('riskScore').textContent = riskScore.toFixed(1) + '%';
            document.getElementById('category').textContent = category;
            document.getElementById('comparison').textContent = comparison;
            document.getElementById('revenue').innerHTML = `
                <div style="font-size: 12px; color: #64748b; margin-bottom: 4px;">Parts: $${partsRevenue} • Service: $${serviceRevenue}</div>
                <div style="font-weight: 600;">Total: $${totalRevenue}</div>
            `;
            
            const badge = document.getElementById('severityBadge');
            if (riskScore >= 50) {
                badge.textContent = 'SEVERE';
                badge.style.background = '#fecaca';
                badge.style.color = '#7f1d1d';
            } else if (riskScore >= 30) {
                badge.textContent = 'CRITICAL';
                badge.style.background = '#fed7d7';
                badge.style.color = '#c53030';
            } else if (riskScore >= 20) {
                badge.textContent = 'HIGH';
                badge.style.background = '#fef5e7';
                badge.style.color = '#c05621';
            } else {
                badge.textContent = 'MODERATE';
                badge.style.background = '#f0fff4';
                badge.style.color = '#38a169';
            }
        }
        
        async function switchChannel(button, channel, customer) {
            // Update active channel button
            button.parentElement.querySelectorAll('.channel-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Load AI messages for this channel
            await loadAIMessages(customer, channel);
        }
        
        async function loadAIMessages(customer, channel) {
            const cacheKey = `${customer}-${channel}`;
            const messagesContainer = document.getElementById(`${customer}-messages`);
            
            // Check cache first
            if (messageCache[cacheKey]) {
                displayMessages(messagesContainer, messageCache[cacheKey]);
                return;
            }
            
            // Show loading state
            const messageTitle = customer === 'sarah' ? 'Integrated Service Messaging' : 'Proactive Outreach Messaging';
            const loadingText = customer === 'sarah' ? 'bundled service messaging' : 'proactive service messaging';
            
            messagesContainer.innerHTML = `
                <div class="ai-messages-title">
                    <span>${messageTitle}</span>
                    <span class="ai-badge">GPT-4</span>
                </div>
                <div class="loading-messages">Generating ${loadingText}...</div>
            `;
            
            try {
                // Get customer-specific data
                const customerData = getCustomerData(customer);
                
                // Call AI message generation API
                const response = await fetch('/api/generate-messages', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        customer_name: customerData.name,
                        vehicle_info: customerData.vehicle,
                        stressors: customerData.stressors,
                        risk_score: customerData.riskScore,
                        channel: channel,
                        message_type: customer === 'sarah' ? 'integrated' : 'proactive'
                    })
                });
                
                const data = await response.json();
                
                // Cache the result
                messageCache[cacheKey] = data;
                
                // Display messages
                displayMessages(messagesContainer, data);
                
            } catch (error) {
                console.error('Error loading AI messages:', error);
                
                // Fallback to static messages
                const fallbackData = {
                    messages: [
                        `${customer === 'sarah' ? 'Sarah' : 'Mike'}, your vehicle shows stress factors that need attention`,
                        `Our analysis indicates high failure risk - let's prevent a breakdown`,
                        `Research shows this pattern leads to issues within weeks`
                    ],
                    personalized: false
                };
                
                displayMessages(messagesContainer, fallbackData);
            }
        }
        
        function displayMessages(container, data) {
            const personalizedBadge = data.personalized ? 
                '<span class="ai-badge">GPT-4</span>' : 
                '<span class="ai-badge">Fallback</span>';
            
            // Determine if this is Sarah or Mike based on container ID
            const isSarah = container.id.includes('sarah');
            const messageTitle = isSarah ? 'Integrated Service Messaging' : 'Proactive Outreach Messaging';
            
            container.innerHTML = `
                <div class="ai-messages-title">
                    <span>${messageTitle}</span>
                    ${personalizedBadge}
                </div>
                ${data.messages.map(msg => `<div class="ai-message">${msg}</div>`).join('')}
            `;
        }
        
        function getCustomerData(customer) {
            const customerData = {
                sarah: {
                    name: "Sarah Johnson",
                    vehicle: "2022 Light Truck",
                    stressors: ["temperature_extremes", "short_trip_cycles", "high_ignition_frequency"],
                    riskScore: 49.3,
                    partsRevenue: 280,
                    serviceRevenue: 125,
                    totalRevenue: 405
                },
                mike: {
                    name: "Mike Rodriguez", 
                    vehicle: "2023 SUV",
                    stressors: ["commercial_usage", "multiple_drivers", "high_mileage"],
                    riskScore: 68.6,
                    partsRevenue: 320,
                    serviceRevenue: 145,
                    totalRevenue: 465
                }
            };
            
            return customerData[customer];
        }
        
        document.getElementById('riskForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const vin = document.getElementById('vin').value.trim().toUpperCase();
            if (vin.length === 17) {
                calculateRisk(vin);
            } else {
                alert('Please enter a valid 17-character VIN');
            }
        });
        
        // Initialize AI messages on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Auto-load messages for first customer on SMS channel
            setTimeout(() => {
                if (document.getElementById('engagement-tab').classList.contains('active')) {
                    loadAIMessages('sarah', 'sms');
                    loadAIMessages('mike', 'sms');
                }
            }, 1000);
        });
    </script>
</body>
</html>
"""

def main():
    """Start VIN Stressors platform with AI-powered messaging"""
    try:
        logger.info("🚀 Starting VIN Stressors - AI-Powered Vehicle Intelligence Platform")
        logger.info(f"📁 Working directory: {os.getcwd()}")
        
        # Import after path setup
        import uvicorn
        from fastapi import FastAPI, HTTPException, Depends
        from fastapi.responses import HTMLResponse
        from fastapi.security import HTTPBasic, HTTPBasicCredentials
        from pydantic import BaseModel
        from typing import List
        import secrets
        
        # Get configuration from environment
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        
        logger.info(f"🌐 Starting server on {host}:{port}")
        
        # Create FastAPI app
        app = FastAPI(title="VIN Stressors Platform")
        
        # Security setup
        security = HTTPBasic()
        
        def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
            """Simple authentication for demo protection"""
            correct_username = secrets.compare_digest(credentials.username, "dealer")
            correct_password = secrets.compare_digest(credentials.password, "stressors2024")
            if not (correct_username and correct_password):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Basic"},
                )
            return credentials.username
        
        # Request models
        class MessageRequest(BaseModel):
            customer_name: str
            vehicle_info: str
            stressors: List[str]
            risk_score: float
            channel: str = "sms"
            message_type: str = "integrated"  # "integrated" or "proactive"
        
        @app.get("/")
        async def root(username: str = Depends(authenticate)):
            return HTMLResponse(content=CLEAN_INTERFACE_HTML)
        
        @app.post("/api/generate-messages")
        async def generate_messages(request: MessageRequest, username: str = Depends(authenticate)):
            """Generate AI-powered personalized messages"""
            try:
                logger.info(f"🤖 Generating {request.message_type} {request.channel} messages for {request.customer_name}")
                
                messages = ai_generator.generate_personalized_messages(
                    customer_name=request.customer_name,
                    vehicle_info=request.vehicle_info,
                    stressors=request.stressors,
                    risk_score=request.risk_score,
                    channel=request.channel,
                    message_type=request.message_type
                )
                
                return messages
                
            except Exception as e:
                logger.error(f"❌ Message generation failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Message generation failed")
        
        @app.get("/health")
        async def health():
            return {
                "status": "healthy", 
                "service": "vin-stressors", 
                "version": "2.1",
                "ai_enabled": bool(ai_generator.openai_api_key)
            }
        
        @app.get("/api/test-ai")
        async def test_ai(username: str = Depends(authenticate)):
            """Test endpoint to verify AI message generation is working"""
            try:
                test_messages = ai_generator.generate_personalized_messages(
                    customer_name="Test Customer",
                    vehicle_info="2022 Light Truck", 
                    stressors=["temperature_extremes", "short_trips"],
                    risk_score=45.0,
                    channel="sms"
                )
                
                return {
                    "status": "success",
                    "ai_working": test_messages.get("personalized", False),
                    "sample_message": test_messages.get("messages", ["No messages generated"])[0] if test_messages.get("messages") else "No messages",
                    "api_key_found": bool(ai_generator.openai_api_key)
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "api_key_found": bool(ai_generator.openai_api_key)
                }
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 