"""
Ford Risk Score Engine - Mobile-Friendly Web Interface

Responsive web UI for accessing the risk scoring API from mobile devices.
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
import json
from typing import Optional
import os

# Mobile-friendly HTML template
MOBILE_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ford Risk Score Engine</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 16px;
            border: 2px solid #e1e5e9;
            border-radius: 12px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #2a5298;
        }
        
        .btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .result-card {
            margin-top: 20px;
            display: none;
        }
        
        .risk-score {
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        
        .severity-low { color: #10b981; }
        .severity-moderate { color: #f59e0b; }
        .severity-high { color: #ef4444; }
        .severity-critical { color: #dc2626; }
        .severity-severe { color: #991b1b; }
        
        .severity-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            text-align: center;
            margin: 10px 0;
        }
        
        .badge-low { background: #d1fae5; color: #065f46; }
        .badge-moderate { background: #fef3c7; color: #92400e; }
        .badge-high { background: #fee2e2; color: #991b1b; }
        .badge-critical { background: #fecaca; color: #7f1d1d; }
        .badge-severe { background: #fca5a5; color: #7f1d1d; }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f3f4f6;
        }
        
        .detail-row:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            font-weight: 600;
            color: #6b7280;
        }
        
        .detail-value {
            font-weight: 600;
            color: #111827;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #2a5298;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #fee2e2;
            color: #991b1b;
            padding: 16px;
            border-radius: 12px;
            margin: 16px 0;
            display: none;
        }
        
        .demo-vins {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 16px;
        }
        
        .demo-vin {
            padding: 12px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: background-color 0.2s;
            font-size: 12px;
            font-family: monospace;
        }
        
        .demo-vin:hover {
            background: #e2e8f0;
        }
        
        .footer {
            margin-top: auto;
            text-align: center;
            color: white;
            opacity: 0.8;
            font-size: 12px;
            padding: 20px 0;
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 16px;
            }
            
            .card {
                padding: 20px;
            }
            
            .risk-score {
                font-size: 28px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🚗 Ford Risk Score</div>
            <div class="subtitle">Bayesian Vehicle Risk Assessment</div>
        </div>
        
        <div class="card">
            <form id="riskForm">
                <div class="form-group">
                    <label for="vin">Vehicle Identification Number (VIN)</label>
                    <input type="text" id="vin" name="vin" placeholder="Enter 17-character VIN" maxlength="17" required>
                </div>
                
                <button type="submit" class="btn" id="submitBtn">
                    Get Risk Score
                </button>
            </form>
            
            <div class="demo-vins">
                <div class="demo-vin" onclick="setDemoVin('1FORD00000000001')">Demo VIN 1</div>
                <div class="demo-vin" onclick="setDemoVin('1FORD00000000002')">Demo VIN 2</div>
                <div class="demo-vin" onclick="setDemoVin('1FORD00000000003')">Demo VIN 3</div>
                <div class="demo-vin" onclick="setDemoVin('1FORD00000000004')">Demo VIN 4</div>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div>Calculating risk score...</div>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="card result-card" id="result">
            <div class="risk-score" id="riskScore">0.000</div>
            <div class="severity-badge" id="severityBadge">Unknown</div>
            
            <div class="detail-row">
                <span class="detail-label">Confidence</span>
                <span class="detail-value" id="confidence">-</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Vehicle Cohort</span>
                <span class="detail-value" id="cohort">-</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Dominant Stressors</span>
                <span class="detail-value" id="stressors">-</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Recommended Action</span>
                <span class="detail-value" id="action">-</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Revenue Opportunity</span>
                <span class="detail-value" id="revenue">-</span>
            </div>
            
            <div class="detail-row">
                <span class="detail-label">Response Time</span>
                <span class="detail-value" id="responseTime">-</span>
            </div>
        </div>
        
        <div class="footer">
            Ford Bayesian Risk Score Engine<br>
            Powered by Industry-Validated Data
        </div>
    </div>

    <script>
        function setDemoVin(vin) {
            document.getElementById('vin').value = vin;
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            document.getElementById('submitBtn').disabled = true;
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('submitBtn').disabled = false;
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            document.getElementById('result').style.display = 'none';
        }
        
        function showResult(data) {
            const result = data.data;
            
            // Risk score
            document.getElementById('riskScore').textContent = result.risk_score.toFixed(3);
            
            // Severity badge
            const severity = result.severity_bucket.toLowerCase();
            const badge = document.getElementById('severityBadge');
            badge.textContent = result.severity_bucket;
            badge.className = `severity-badge badge-${severity}`;
            
            // Risk score color
            const riskScore = document.getElementById('riskScore');
            riskScore.className = `risk-score severity-${severity}`;
            
            // Details
            document.getElementById('confidence').textContent = (result.confidence * 100).toFixed(1) + '%';
            document.getElementById('cohort').textContent = result.cohort.replace(/\|/g, ' | ');
            document.getElementById('stressors').textContent = result.dominant_stressors.join(', ') || 'None';
            document.getElementById('action').textContent = result.recommended_action;
            document.getElementById('revenue').textContent = '$' + result.revenue_opportunity.toLocaleString();
            document.getElementById('responseTime').textContent = data.processing_time_ms.toFixed(1) + 'ms';
            
            document.getElementById('result').style.display = 'block';
            document.getElementById('error').style.display = 'none';
        }
        
        document.getElementById('riskForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const vin = document.getElementById('vin').value.trim().toUpperCase();
            
            if (vin.length !== 17) {
                showError('VIN must be exactly 17 characters long');
                return;
            }
            
            showLoading();
            
            try {
                const response = await fetch('/risk-score', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        vin: vin,
                        include_metadata: true
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showResult(data);
                } else {
                    showError(data.error || 'Failed to calculate risk score');
                }
                
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                hideLoading();
            }
        });
        
        // Auto-format VIN input
        document.getElementById('vin').addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
        });
    </script>
</body>
</html>
"""


def add_mobile_routes(app: FastAPI):
    """Add mobile-friendly routes to the FastAPI app"""
    
    @app.get("/", response_class=HTMLResponse)
    async def mobile_interface():
        """Serve the mobile-friendly interface"""
        return HTMLResponse(content=MOBILE_HTML_TEMPLATE)
    
    @app.get("/mobile", response_class=HTMLResponse)
    async def mobile_interface_explicit():
        """Explicit mobile interface route"""
        return HTMLResponse(content=MOBILE_HTML_TEMPLATE)
    
    @app.get("/demo", response_class=HTMLResponse)
    async def demo_interface():
        """Demo interface with sample data"""
        return HTMLResponse(content=MOBILE_HTML_TEMPLATE)
    
    return app 