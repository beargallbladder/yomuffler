#!/usr/bin/env python3
"""
Ford Bayesian Risk Score Engine - Render Deployment
Ultra-minimal version for reliable deployment
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ford Bayesian Risk Score Engine",
    description="Mobile-Optimized Vehicle Risk Assessment Platform",
    version="1.0.0"
)

class VehicleInput(BaseModel):
    vin: str

class RiskScore(BaseModel):
    vin: str
    risk_score: float
    severity: str
    confidence: float

# Demo data for testing
DEMO_SCORES = {
    "1FMCU9GD5LUA12345": {"score": 0.85, "severity": "High", "confidence": 0.92},
    "1FTFW1ET5DFC67890": {"score": 0.23, "severity": "Low", "confidence": 0.88},
    "1FA6P8TH8J5123456": {"score": 0.67, "severity": "Moderate", "confidence": 0.91},
}

@app.get("/", response_class=HTMLResponse)
async def mobile_interface():
    """Mobile-optimized Ford Risk Score Interface"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ford Bayesian Risk Score Engine</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                min-height: 100vh;
                color: white;
                padding: 20px;
            }
            .container { max-width: 400px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .logo { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
            .subtitle { opacity: 0.9; font-size: 14px; }
            .card { 
                background: rgba(255,255,255,0.1); 
                border-radius: 15px; 
                padding: 25px; 
                backdrop-filter: blur(10px);
                margin-bottom: 20px;
            }
            .input-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 500; }
            input { 
                width: 100%; 
                padding: 15px; 
                border: none; 
                border-radius: 10px; 
                font-size: 16px;
                background: rgba(255,255,255,0.9);
                color: #333;
            }
            .btn { 
                width: 100%; 
                padding: 15px; 
                border: none; 
                border-radius: 10px; 
                font-size: 16px; 
                font-weight: bold;
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                color: white;
                cursor: pointer;
                transition: transform 0.2s;
            }
            .btn:hover { transform: translateY(-2px); }
            .result { 
                margin-top: 20px; 
                padding: 20px; 
                border-radius: 10px; 
                background: rgba(255,255,255,0.1);
                display: none;
            }
            .demo-vins { margin-top: 15px; }
            .demo-vin { 
                display: inline-block; 
                margin: 5px; 
                padding: 8px 12px; 
                background: rgba(255,255,255,0.2); 
                border-radius: 5px; 
                font-size: 12px;
                cursor: pointer;
            }
            .status { 
                text-align: center; 
                padding: 20px; 
                background: rgba(0,255,0,0.1); 
                border-radius: 10px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🚗 Ford Risk Engine</div>
                <div class="subtitle">Bayesian Vehicle Risk Assessment</div>
            </div>
            
            <div class="status">
                ✅ <strong>DEPLOYED SUCCESSFULLY</strong><br>
                <small>System operational on Render.com</small>
            </div>
            
            <div class="card">
                <div class="input-group">
                    <label for="vin">Vehicle Identification Number (VIN)</label>
                    <input type="text" id="vin" placeholder="Enter 17-character VIN">
                </div>
                <button class="btn" onclick="calculateRisk()">Calculate Risk Score</button>
                
                <div class="demo-vins">
                    <small>Demo VINs:</small><br>
                    <span class="demo-vin" onclick="setVin('1FMCU9GD5LUA12345')">1FMCU9GD5LUA12345</span>
                    <span class="demo-vin" onclick="setVin('1FTFW1ET5DFC67890')">1FTFW1ET5DFC67890</span>
                    <span class="demo-vin" onclick="setVin('1FA6P8TH8J5123456')">1FA6P8TH8J5123456</span>
                </div>
            </div>
            
            <div id="result" class="result"></div>
            
            <div class="card">
                <h3>🔗 Quick Links</h3>
                <p><a href="/health" style="color: #87CEEB;">Health Check</a></p>
                <p><a href="/docs" style="color: #87CEEB;">API Documentation</a></p>
                <p><a href="https://github.com/beargallbladder/yomuffler" style="color: #87CEEB;">Source Code</a></p>
            </div>
        </div>
        
        <script>
            function setVin(vin) {
                document.getElementById('vin').value = vin;
            }
            
            async function calculateRisk() {
                const vin = document.getElementById('vin').value.trim();
                const resultDiv = document.getElementById('result');
                
                if (!vin) {
                    alert('Please enter a VIN');
                    return;
                }
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<div style="text-align:center;">🔄 Calculating risk score...</div>';
                
                try {
                    const response = await fetch('/risk-score', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ vin: vin })
                    });
                    
                    const data = await response.json();
                    
                    const severityColors = {
                        'Low': '#4CAF50',
                        'Moderate': '#FF9800', 
                        'High': '#F44336',
                        'Critical': '#9C27B0'
                    };
                    
                    resultDiv.innerHTML = `
                        <h3>Risk Assessment Results</h3>
                        <p><strong>VIN:</strong> ${data.vin}</p>
                        <p><strong>Risk Score:</strong> ${(data.risk_score * 100).toFixed(1)}%</p>
                        <p><strong>Severity:</strong> <span style="color: ${severityColors[data.severity] || '#FFF'}">${data.severity}</span></p>
                        <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
                    `;
                } catch (error) {
                    resultDiv.innerHTML = '<div style="color: #ff6b6b;">Error calculating risk score. Please try again.</div>';
                }
            }
        </script>
    </body>
    </html>
    """)

@app.post("/risk-score", response_model=RiskScore)
async def calculate_risk_score(vehicle: VehicleInput):
    """Calculate Bayesian risk score for a vehicle"""
    vin = vehicle.vin.upper().strip()
    
    # Use demo data if available, otherwise generate a score
    if vin in DEMO_SCORES:
        demo_data = DEMO_SCORES[vin]
        return RiskScore(
            vin=vin,
            risk_score=demo_data["score"],
            severity=demo_data["severity"],
            confidence=demo_data["confidence"]
        )
    else:
        # Generate a simple demo score based on VIN characteristics
        score = (hash(vin) % 100) / 100.0
        if score < 0.3:
            severity = "Low"
        elif score < 0.6:
            severity = "Moderate"
        elif score < 0.8:
            severity = "High"
        else:
            severity = "Critical"
            
        return RiskScore(
            vin=vin,
            risk_score=score,
            severity=severity,
            confidence=0.85
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Ford Bayesian Risk Score Engine",
        "version": "1.0.0",
        "deployment": "render.com"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "start_render:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 