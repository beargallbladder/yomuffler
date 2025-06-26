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
        
    async def generate_personalized_messages(self, customer_name: str, vehicle_info: str, 
                                           stressors: List[str], risk_score: float, 
                                           channel: str = "sms") -> Dict[str, List[str]]:
        """Generate personalized messages based on stressor analysis"""
        
        if not self.openai_api_key:
            return self._fallback_messages(customer_name, vehicle_info, stressors, risk_score)
        
        try:
            # Dynamic import to avoid startup issues
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
            
            # Channel-specific prompts with realistic pricing
            prompts = {
                "sms": f"""Create 3 concise SMS messages (under 160 chars each) for {customer_name} about their {vehicle_info}. 
                Vehicle shows these stressors: {stressor_context}. Risk level: {risk_level} ({risk_score:.1f}%).
                Battery service cost: Parts ${parts_cost} + Service ${service_cost} = ${total_cost}.
                Be professional, urgent but not alarmist. Focus on prevention and value.""",
                
                "email": f"""Create 3 professional email talking points for {customer_name} about their {vehicle_info}.
                Vehicle analysis shows: {stressor_context}. Risk assessment: {risk_level} ({risk_score:.1f}%).
                Battery service estimate: Parts ${parts_cost} + Labor ${service_cost} = ${total_cost}.
                Focus on academic backing, specific stressors, and business value. Be consultative.""",
                
                "phone": f"""Create 3 phone conversation starters for {customer_name} about their {vehicle_info}.
                Detected stressors: {stressor_context}. Risk level: {risk_level} ({risk_score:.1f}%).
                Battery service pricing: ${parts_cost} parts + ${service_cost} service = ${total_cost} total.
                Natural conversation flow, build rapport, educate about specific risks."""
            }
            
            response = await client.chat.completions.acreate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert automotive service advisor. Create personalized, professional messages that build trust and demonstrate expertise. Use specific technical details but keep language accessible."},
                    {"role": "user", "content": prompts.get(channel, prompts["sms"])}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse response into individual messages
            content = response.choices[0].message.content
            messages = [msg.strip() for msg in content.split('\n') if msg.strip() and not msg.strip().startswith(('1.', '2.', '3.', '-', '•'))]
            
            return {
                "messages": messages[:3],  # Ensure max 3 messages
                "risk_level": risk_level,
                "personalized": True
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {str(e)}")
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #f8fafc;
            color: #1a202c;
            line-height: 1.6;
        }
        
        .container { 
            max-width: 420px; 
            margin: 0 auto; 
            min-height: 100vh;
            background: white;
            box-shadow: 0 0 40px rgba(0,0,0,0.06);
        }
        
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 32px 24px 24px;
            text-align: center;
            color: white;
        }
        
        .logo { 
            font-size: 20px; 
            font-weight: 700; 
            letter-spacing: -0.5px;
            margin-bottom: 6px;
        }
        
        .subtitle { 
            font-size: 13px; 
            opacity: 0.85;
            font-weight: 400;
        }
        
        .tab-nav { 
            background: white;
            display: flex; 
            border-bottom: 1px solid #e2e8f0;
        }
        
        .tab-btn { 
            flex: 1; 
            padding: 16px 12px;
            background: transparent; 
            border: none; 
            color: #64748b;
            font-weight: 500; 
            font-size: 14px;
            cursor: pointer; 
            transition: all 0.2s;
            border-bottom: 2px solid transparent;
        }
        
        .tab-btn.active { 
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-content { 
            display: none; 
            padding: 24px;
        }
        
        .tab-content.active { 
            display: block; 
        }
        
        /* Clean Cards */
        .card { 
            background: white; 
            border-radius: 12px; 
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #e2e8f0;
        }
        
        /* Learning Cards - No Overlapping */
        .learning-card { 
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px; 
            padding: 20px;
            margin-bottom: 16px;
            cursor: pointer; 
            transition: all 0.2s;
            position: relative;
            min-height: 120px;
        }
        
        .learning-card:hover {
            border-color: #667eea;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102,126,234,0.1);
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
        }
        
        .card-back { 
            transform: rotateY(180deg);
            background: #f8fafc;
            border-radius: 8px;
            padding: 16px;
        }
        
        .flip-indicator { 
            position: absolute;
            top: 8px; 
            right: 8px;
            background: #667eea;
            color: white; 
            padding: 4px 8px;
            border-radius: 6px; 
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .card-title { 
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #1a202c;
        }
        
        .card-description {
            font-size: 14px;
            color: #64748b;
            line-height: 1.5;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">VIN Stressors</div>
            <div class="subtitle">AI-Powered Vehicle Intelligence Platform</div>
        </div>
        
        <div class="tab-nav">
            <button class="tab-btn active" onclick="switchTab('intelligence')">Intelligence</button>
            <button class="tab-btn" onclick="switchTab('calculator')">Calculator</button>
            <button class="tab-btn" onclick="switchTab('engagement')">Engagement</button>
        </div>
        
        <!-- Intelligence Tab -->
        <div id="intelligence-tab" class="tab-content active">
            <div class="learning-card" onclick="flipCard(this)">
                <div class="flip-indicator">Flip</div>
                <div class="card-inner">
                    <div class="card-front">
                        <div class="card-title">Academic Foundation</div>
                        <div class="card-description">
                            Peer-reviewed research from Argonne National Laboratory validates 
                            vehicle stress patterns across all makes and models.
                        </div>
                    </div>
                    <div class="card-back">
                        <div class="math-content">
                            <div class="math-formula">
                                <strong>Argonne ANL-115925.pdf</strong><br/>
                                6-mile recharge rule validation<br/>
                                P(failure|&lt;6mi trips) = 1.9x baseline
                            </div>
                            <div class="math-formula">
                                <strong>Universal Stressors:</strong><br/>
                                • Temperature extremes: 2.0x<br/>
                                • Short trip cycles: 1.9x<br/>
                                • High ignition frequency: 2.3x<br/>
                                • Deferred maintenance: 2.1x
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="learning-card" onclick="flipCard(this)">
                <div class="flip-indicator">Flip</div>
                <div class="card-inner">
                    <div class="card-front">
                        <div class="card-title">AI-Powered Messaging</div>
                        <div class="card-description">
                            Large language models create personalized, contextual messages 
                            based on specific stressor analysis for each vehicle.
                        </div>
                    </div>
                    <div class="card-back">
                        <div class="math-content">
                            <div class="math-formula">
                                <strong>Dynamic Generation:</strong><br/>
                                • SMS: Concise, urgent messaging<br/>
                                • Email: Professional, detailed<br/>
                                • Phone: Conversational starters<br/>
                                • Context-aware personalization
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Calculator Tab -->
        <div id="calculator-tab" class="tab-content">
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
        
        <!-- AI-Enhanced Engagement Tab -->
        <div id="engagement-tab" class="tab-content">
            <div class="lead-card">
                <div class="lead-header">
                    <div class="customer-name">Sarah Johnson</div>
                    <div class="priority-badge priority-critical">Critical</div>
                </div>
                <div class="vehicle-info">2022 Light Truck • VIN: 1FTFW1ET5LFA67890 • 47,823 miles</div>
                <div class="issue-type">Battery Risk: 3.3x Above Category Average</div>
                
                <div class="engagement-channels">
                    <div class="channel-btn active" onclick="switchChannel(this, 'sms', 'sarah')">📱 SMS</div>
                    <div class="channel-btn" onclick="switchChannel(this, 'email', 'sarah')">📧 Email</div>
                    <div class="channel-btn" onclick="switchChannel(this, 'phone', 'sarah')">📞 Call</div>
                </div>
                
                <div class="ai-messages" id="sarah-messages">
                    <div class="ai-messages-title">
                        <span>AI-Generated Messages</span>
                        <span class="ai-badge">GPT-4</span>
                    </div>
                    <div class="loading-messages">Generating personalized messages...</div>
                </div>
                <div class="revenue-estimate">
                    Battery Service: Parts $280 + Service $125 = $405 • Contact Within: 24 hours
                </div>
            </div>
            
            <div class="lead-card">
                <div class="lead-header">
                    <div class="customer-name">Mike Rodriguez</div>
                    <div class="priority-badge priority-high">High</div>
                </div>
                <div class="vehicle-info">2023 SUV • VIN: 1FMHK8D83LGA89012 • 23,456 miles</div>
                <div class="issue-type">Commercial Usage: 2.1x Risk Multiplier</div>
                
                <div class="engagement-channels">
                    <div class="channel-btn active" onclick="switchChannel(this, 'sms', 'mike')">📱 SMS</div>
                    <div class="channel-btn" onclick="switchChannel(this, 'email', 'mike')">📧 Email</div>
                    <div class="channel-btn" onclick="switchChannel(this, 'phone', 'mike')">📞 Call</div>
                </div>
                
                <div class="ai-messages" id="mike-messages">
                    <div class="ai-messages-title">
                        <span>AI-Generated Messages</span>
                        <span class="ai-badge">GPT-4</span>
                    </div>
                    <div class="loading-messages">Generating personalized messages...</div>
                </div>
                <div class="revenue-estimate">
                    Battery Service: Parts $320 + Service $145 = $465 • Contact Within: 48 hours
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
            messagesContainer.innerHTML = `
                <div class="ai-messages-title">
                    <span>AI-Generated Messages</span>
                    <span class="ai-badge">GPT-4</span>
                </div>
                <div class="loading-messages">Generating personalized ${channel.toUpperCase()} messages...</div>
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
                        channel: channel
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
            
            container.innerHTML = `
                <div class="ai-messages-title">
                    <span>AI-Generated Messages</span>
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
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse
        from pydantic import BaseModel
        from typing import List
        
        # Get configuration from environment
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        
        logger.info(f"🌐 Starting server on {host}:{port}")
        
        # Create FastAPI app
        app = FastAPI(title="VIN Stressors Platform")
        
        # Request models
        class MessageRequest(BaseModel):
            customer_name: str
            vehicle_info: str
            stressors: List[str]
            risk_score: float
            channel: str = "sms"
        
        @app.get("/")
        async def root():
            return HTMLResponse(content=CLEAN_INTERFACE_HTML)
        
        @app.post("/api/generate-messages")
        async def generate_messages(request: MessageRequest):
            """Generate AI-powered personalized messages"""
            try:
                logger.info(f"🤖 Generating {request.channel} messages for {request.customer_name}")
                
                messages = await ai_generator.generate_personalized_messages(
                    customer_name=request.customer_name,
                    vehicle_info=request.vehicle_info,
                    stressors=request.stressors,
                    risk_score=request.risk_score,
                    channel=request.channel
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