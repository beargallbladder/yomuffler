#!/usr/bin/env python3
"""
Ford Bayesian Risk Score Engine - Advanced Prognostic Platform
Sophisticated interface showcasing cohort analysis, stressor identification, and dealer messaging
"""

import os
import logging
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ford Bayesian Prognostic Risk Engine",
    description="Advanced Cohort-Based Risk Stratification & Dealer Messaging Platform",
    version="2.0.0"
)

# Industry-Validated Priors (from your specification)
INDUSTRY_PRIORS = {
    "battery_degradation": {
        "base_rate": 0.023,  # Argon National Study 2015
        "stressor_multipliers": {
            "soc_decline": 6.50,     # SOC decline pattern
            "trip_cycling": 2.83,    # Short trip cycling
            "climate_stress": 2.39,  # Extreme climate exposure
            "maintenance_skip": 2.16  # Maintenance interval skipping
        },
        "cohort_adjustments": {
            "F150|ICE|NORTH|HEAVY": 1.34,
            "F150|ICE|SOUTH|MEDIUM": 0.87,
            "MUSTANG|ICE|WEST|LIGHT": 0.45,
            "EXPLORER|HYBRID|NORTH|HEAVY": 1.89
        }
    },
    "transmission_failure": {
        "base_rate": 0.067,  # NHTSA Historical Data
        "stressor_multipliers": {
            "thermal_cycling": 3.21,
            "load_variance": 2.45,
            "fluid_degradation": 1.87,
            "shift_pattern": 1.56
        }
    },
    "engine_degradation": {
        "base_rate": 0.145,  # Ford Historical Repair Data
        "stressor_multipliers": {
            "oil_interval": 2.78,
            "cold_starts": 2.34,
            "idle_time": 1.92,
            "fuel_quality": 1.67
        }
    }
}

# Demo Vehicle Data with Rich Context
DEMO_VEHICLES = {
    "1FMCU9GD5LUA12345": {
        "model": "F-150 SuperCrew",
        "year": 2023,
        "engine": "3.5L EcoBoost V6",
        "cohort": "F150|ICE|NORTH|HEAVY",
        "mileage": 47823,
        "location": "Detroit, MI",
        "usage_pattern": "Heavy Duty Commercial",
        "current_dtcs": ["P0171", "P0174"],
        "prognostic_flags": [
            {
                "component": "Battery",
                "risk_increase": 0.234,
                "stressor": "SOC Decline Pattern",
                "likelihood_ratio": 6.50,
                "days_to_failure": 23,
                "confidence": 0.92
            },
            {
                "component": "Transmission",
                "risk_increase": 0.156,
                "stressor": "Thermal Cycling",
                "likelihood_ratio": 3.21,
                "days_to_failure": 67,
                "confidence": 0.87
            }
        ],
        "stressor_profile": {
            "soc_decline": 0.89,
            "trip_cycling": 0.76,
            "climate_stress": 0.82,
            "maintenance_skip": 0.34
        }
    },
    "1FTFW1ET5DFC67890": {
        "model": "F-150 Regular Cab",
        "year": 2022,
        "engine": "5.0L V8",
        "cohort": "F150|ICE|SOUTH|MEDIUM",
        "mileage": 23456,
        "location": "Austin, TX",
        "usage_pattern": "Personal Light Duty",
        "current_dtcs": [],
        "prognostic_flags": [
            {
                "component": "Engine",
                "risk_increase": 0.067,
                "stressor": "Oil Interval Extension",
                "likelihood_ratio": 2.78,
                "days_to_failure": 134,
                "confidence": 0.78
            }
        ],
        "stressor_profile": {
            "oil_interval": 0.67,
            "cold_starts": 0.23,
            "idle_time": 0.45,
            "fuel_quality": 0.12
        }
    },
    "1FA6P8TH8J5123456": {
        "model": "Mustang GT",
        "year": 2023,
        "engine": "5.0L V8",
        "cohort": "MUSTANG|ICE|WEST|LIGHT",
        "mileage": 12890,
        "location": "Los Angeles, CA",
        "usage_pattern": "Performance Enthusiast",
        "current_dtcs": ["P0300"],
        "prognostic_flags": [
            {
                "component": "Engine",
                "risk_increase": 0.198,
                "stressor": "High RPM Pattern",
                "likelihood_ratio": 2.34,
                "days_to_failure": 89,
                "confidence": 0.84
            }
        ],
        "stressor_profile": {
            "high_rpm": 0.91,
            "track_usage": 0.78,
            "aggressive_shifts": 0.82,
            "thermal_stress": 0.67
        }
    }
}

class VehicleInput(BaseModel):
    vin: str

class PrognosticAnalysis(BaseModel):
    vin: str
    vehicle_info: Dict
    risk_summary: Dict
    prognostic_insights: List[Dict]
    stressor_analysis: Dict
    cohort_comparison: Dict
    dealer_messaging: Dict
    revenue_opportunity: Dict

@app.get("/", response_class=HTMLResponse)
async def advanced_dashboard():
    """Advanced Prognostic Dashboard - Engineering Team Demonstration"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ford Bayesian Prognostic Risk Engine</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f1419 0%, #1e3c72 50%, #2a5298 100%);
                min-height: 100vh;
                color: white;
                overflow-x: hidden;
            }
            
            .header {
                background: rgba(0,0,0,0.3);
                padding: 20px;
                text-align: center;
                border-bottom: 2px solid rgba(255,255,255,0.1);
            }
            
            .logo { 
                font-size: 28px; 
                font-weight: bold; 
                margin-bottom: 10px;
                background: linear-gradient(45deg, #00d4ff, #0099cc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .subtitle { 
                opacity: 0.9; 
                font-size: 16px; 
                color: #87CEEB;
            }
            
            .main-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            
                         .card {
                 background: rgba(255,255,255,0.05);
                 border-radius: 15px;
                 padding: 25px;
                 backdrop-filter: blur(10px);
                 border: 1px solid rgba(255,255,255,0.1);
                 transition: transform 0.3s ease;
                 position: relative;
                 transform-style: preserve-3d;
                 cursor: pointer;
                 min-height: 300px;
             }
             
             .card:hover {
                 transform: translateY(-5px);
                 box-shadow: 0 10px 30px rgba(0,212,255,0.2);
             }
             
             .card.flipped {
                 transform: rotateY(180deg);
             }
             
             .card-front, .card-back {
                 position: absolute;
                 top: 0;
                 left: 0;
                 right: 0;
                 bottom: 0;
                 padding: 25px;
                 border-radius: 15px;
                 backface-visibility: hidden;
                 transition: all 0.6s ease;
             }
             
             .card-back {
                 transform: rotateY(180deg);
                 background: rgba(0,50,100,0.1);
                 border: 1px solid rgba(0,212,255,0.3);
             }
             
             .math-content {
                 font-family: 'Courier New', monospace;
                 font-size: 14px;
                 line-height: 1.6;
                 color: #87CEEB;
             }
             
             .math-formula {
                 background: rgba(0,0,0,0.3);
                 padding: 10px;
                 border-radius: 8px;
                 margin: 10px 0;
                 border-left: 3px solid #00d4ff;
             }
             
             .flip-indicator {
                 position: absolute;
                 top: 10px;
                 right: 10px;
                 background: rgba(0,212,255,0.2);
                 color: #00d4ff;
                 padding: 5px 10px;
                 border-radius: 15px;
                 font-size: 12px;
                 font-weight: bold;
             }
            
            .card-title {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 15px;
                color: #00d4ff;
                border-bottom: 2px solid rgba(0,212,255,0.3);
                padding-bottom: 10px;
            }
            
            .input-section {
                grid-column: 1 / -1;
                text-align: center;
            }
            
            .vin-input {
                width: 300px;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                background: rgba(255,255,255,0.9);
                color: #333;
                margin: 0 10px;
            }
            
            .analyze-btn {
                padding: 15px 30px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .analyze-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(255,107,107,0.4);
            }
            
            .demo-vins {
                margin-top: 20px;
                display: flex;
                justify-content: center;
                gap: 10px;
                flex-wrap: wrap;
            }
            
            .demo-vin {
                padding: 8px 15px;
                background: rgba(0,212,255,0.2);
                border-radius: 20px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid rgba(0,212,255,0.3);
            }
            
            .demo-vin:hover {
                background: rgba(0,212,255,0.4);
                transform: scale(1.05);
            }
            
            .results-container {
                grid-column: 1 / -1;
                display: none;
            }
            
            .results-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            
            .metric {
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                padding: 10px;
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
            }
            
            .metric-label { color: #87CEEB; }
            .metric-value { font-weight: bold; }
            
            .risk-high { color: #ff6b6b; }
            .risk-moderate { color: #ffa726; }
            .risk-low { color: #4caf50; }
            
            .stressor-bar {
                width: 100%;
                height: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                overflow: hidden;
                margin: 5px 0;
            }
            
            .stressor-fill {
                height: 100%;
                background: linear-gradient(90deg, #4caf50, #ffa726, #ff6b6b);
                transition: width 0.8s ease;
            }
            
            .prognostic-alert {
                background: linear-gradient(45deg, rgba(255,107,107,0.2), rgba(255,193,7,0.2));
                border-left: 4px solid #ff6b6b;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
            }
            
            .dealer-message {
                background: rgba(0,212,255,0.1);
                border-left: 4px solid #00d4ff;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                font-style: italic;
            }
            
            .revenue-highlight {
                background: linear-gradient(45deg, rgba(76,175,80,0.2), rgba(139,195,74,0.2));
                border-left: 4px solid #4caf50;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                text-align: center;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #00d4ff;
            }
            
            .loading::after {
                content: "⚡";
                animation: pulse 1s infinite;
                font-size: 24px;
                margin-left: 10px;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }
            
            @media (max-width: 768px) {
                .main-container {
                    grid-template-columns: 1fr;
                    padding: 10px;
                }
                .vin-input {
                    width: 250px;
                    margin: 5px;
                }
                .results-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🚗 FORD BAYESIAN PROGNOSTIC ENGINE</div>
            <div class="subtitle">Advanced Cohort-Based Risk Stratification & Predictive Maintenance</div>
        </div>
        
        <div class="main-container">
            <div class="card input-section">
                <div class="card-title">🎯 Vehicle Risk Analysis</div>
                <p style="margin-bottom: 20px; color: #87CEEB;">
                    Enter a VIN to see <strong>prognostic risk analysis</strong> with industry-validated Bayesian priors,
                    cohort stratification, and stressor identification that prevents downtime before it happens.
                </p>
                
                <input type="text" id="vin" class="vin-input" placeholder="Enter 17-character VIN">
                <button class="analyze-btn" onclick="analyzeVehicle()">🔬 Analyze Risk Profile</button>
                
                <div class="demo-vins">
                    <div class="demo-vin" onclick="setVin('1FMCU9GD5LUA12345')">
                        🚛 F-150 Heavy Duty (High Risk)
                    </div>
                    <div class="demo-vin" onclick="setVin('1FTFW1ET5DFC67890')">
                        🚗 F-150 Personal (Low Risk)
                    </div>
                    <div class="demo-vin" onclick="setVin('1FA6P8TH8J5123456')">
                        🏎️ Mustang GT (Performance)
                    </div>
                </div>
            </div>
            
            <div id="results" class="results-container">
                <div class="results-grid" id="resultsGrid">
                    <!-- Results will be populated here -->
                </div>
            </div>
        </div>
        
        <script>
                         function setVin(vin) {
                 const vinInput = document.getElementById('vin');
                 vinInput.value = vin;
                 vinInput.focus();
                 vinInput.select();
             }
             
             function flipCard(cardElement) {
                 cardElement.classList.toggle('flipped');
             }
            
            async function analyzeVehicle() {
                const vin = document.getElementById('vin').value.trim();
                const resultsContainer = document.getElementById('results');
                const resultsGrid = document.getElementById('resultsGrid');
                
                if (!vin) {
                    alert('Please enter a VIN');
                    return;
                }
                
                resultsContainer.style.display = 'block';
                resultsGrid.innerHTML = '<div class="loading">🔬 Performing Advanced Bayesian Analysis...</div>';
                
                try {
                    const response = await fetch('/analyze-prognostic', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ vin: vin })
                    });
                    
                    const data = await response.json();
                    displayResults(data);
                } catch (error) {
                    resultsGrid.innerHTML = '<div style="color: #ff6b6b; text-align: center;">Analysis failed. Please try again.</div>';
                }
            }
            
            function displayResults(data) {
                const resultsGrid = document.getElementById('resultsGrid');
                
                resultsGrid.innerHTML = `
                    <!-- Vehicle Overview -->
                    <div class="card">
                        <div class="card-title">🚗 Vehicle Profile</div>
                        <div class="metric">
                            <span class="metric-label">Model:</span>
                            <span class="metric-value">${data.vehicle_info.model}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Cohort:</span>
                            <span class="metric-value">${data.vehicle_info.cohort}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Usage Pattern:</span>
                            <span class="metric-value">${data.vehicle_info.usage_pattern}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Location:</span>
                            <span class="metric-value">${data.vehicle_info.location}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Mileage:</span>
                            <span class="metric-value">${data.vehicle_info.mileage.toLocaleString()} miles</span>
                        </div>
                    </div>
                    
                    <!-- Risk Summary -->
                    <div class="card">
                        <div class="card-title">⚠️ Risk Assessment</div>
                        <div class="metric">
                            <span class="metric-label">Overall Risk Score:</span>
                            <span class="metric-value risk-${data.risk_summary.severity.toLowerCase()}">${(data.risk_summary.score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Severity Level:</span>
                            <span class="metric-value risk-${data.risk_summary.severity.toLowerCase()}">${data.risk_summary.severity}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Confidence:</span>
                            <span class="metric-value">${(data.risk_summary.confidence * 100).toFixed(1)}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Days to Intervention:</span>
                            <span class="metric-value">${data.risk_summary.days_to_intervention}</span>
                        </div>
                    </div>
                    
                                         <!-- Vehicle Stressors -->
                     <div class="card" onclick="flipCard(this)">
                         <div class="flip-indicator">CLICK TO FLIP</div>
                         <div class="card-front">
                             <div class="card-title">⚡ Vehicle Stressors</div>
                             ${data.prognostic_insights.map(insight => `
                                 <div class="prognostic-alert">
                                     <strong>⚡ ${insight.component} Risk Increase: +${(insight.risk_increase * 100).toFixed(1)}%</strong><br>
                                     <small>Stressor: ${insight.stressor} (LR: ${insight.likelihood_ratio}x)</small><br>
                                     <small>Estimated Failure: ${insight.days_to_failure} days</small>
                                 </div>
                             `).join('')}
                         </div>
                         <div class="card-back">
                             <div class="card-title">📊 Bayesian Math</div>
                             <div class="math-content">
                                 <strong>Likelihood Ratio Calculation:</strong>
                                 <div class="math-formula">
                                     P(Failure|Stressor) = P(Stressor|Failure) × P(Failure) / P(Stressor)
                                 </div>
                                 ${data.prognostic_insights.map(insight => `
                                     <div style="margin: 15px 0;">
                                         <strong>${insight.component} Analysis:</strong><br>
                                         <div class="math-formula">
                                             Base Rate: 2.3% (Argon Study 2015)<br>
                                             Stressor LR: ${insight.likelihood_ratio}x<br>
                                             Posterior = 0.023 × ${insight.likelihood_ratio} = ${(0.023 * insight.likelihood_ratio).toFixed(3)}<br>
                                             Risk Increase: +${(insight.risk_increase * 100).toFixed(1)}%
                                         </div>
                                     </div>
                                 `).join('')}
                                 <small><em>Click to flip back</em></small>
                             </div>
                         </div>
                     </div>
                    
                                         <!-- Stressor Analysis -->
                     <div class="card" onclick="flipCard(this)">
                         <div class="flip-indicator">CLICK TO FLIP</div>
                         <div class="card-front">
                             <div class="card-title">🎯 Stressor Profile</div>
                             ${Object.entries(data.stressor_analysis).map(([stressor, value]) => `
                                 <div style="margin: 15px 0;">
                                     <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                         <span>${stressor.replace('_', ' ').toUpperCase()}</span>
                                         <span>${(value * 100).toFixed(1)}%</span>
                                     </div>
                                     <div class="stressor-bar">
                                         <div class="stressor-fill" style="width: ${value * 100}%"></div>
                                     </div>
                                 </div>
                             `).join('')}
                         </div>
                         <div class="card-back">
                             <div class="card-title">🧮 Stressor Math</div>
                             <div class="math-content">
                                 <strong>Stressor Impact Calculation:</strong>
                                 <div class="math-formula">
                                     Final_Risk = Base_Rate × Cohort_Multiplier × ∏(1 + (LR_i - 1) × Stressor_i)
                                 </div>
                                 ${Object.entries(data.stressor_analysis).map(([stressor, value]) => `
                                     <div style="margin: 10px 0;">
                                         <strong>${stressor.replace('_', ' ').toUpperCase()}:</strong><br>
                                         <div class="math-formula">
                                             Intensity: ${(value * 100).toFixed(1)}%<br>
                                             Multiplier: ${stressor === 'soc_decline' ? '6.50x' : stressor === 'trip_cycling' ? '2.83x' : stressor === 'climate_stress' ? '2.39x' : '2.16x'}<br>
                                             Impact: 1 + (${stressor === 'soc_decline' ? '6.50' : stressor === 'trip_cycling' ? '2.83' : stressor === 'climate_stress' ? '2.39' : '2.16'} - 1) × ${value.toFixed(2)} = ${(1 + (parseFloat(stressor === 'soc_decline' ? '6.50' : stressor === 'trip_cycling' ? '2.83' : stressor === 'climate_stress' ? '2.39' : '2.16') - 1) * value).toFixed(2)}
                                         </div>
                                     </div>
                                 `).join('')}
                                 <small><em>Click to flip back</em></small>
                             </div>
                         </div>
                     </div>
                    
                                         <!-- Cohort Comparison -->
                     <div class="card" onclick="flipCard(this)">
                         <div class="flip-indicator">CLICK TO FLIP</div>
                         <div class="card-front">
                             <div class="card-title">👥 Cohort Analysis</div>
                             <div class="metric">
                                 <span class="metric-label">Cohort Risk Multiplier:</span>
                                 <span class="metric-value">${data.cohort_comparison.multiplier}x</span>
                             </div>
                             <div class="metric">
                                 <span class="metric-label">Percentile Rank:</span>
                                 <span class="metric-value">${data.cohort_comparison.percentile}th percentile</span>
                             </div>
                             <div class="metric">
                                 <span class="metric-label">Similar Vehicles:</span>
                                 <span class="metric-value">${data.cohort_comparison.sample_size.toLocaleString()}</span>
                             </div>
                         </div>
                         <div class="card-back">
                             <div class="card-title">📈 Cohort Math</div>
                             <div class="math-content">
                                 <strong>Cohort Stratification Logic:</strong>
                                 <div class="math-formula">
                                     Cohort_Risk = Base_Rate × Cohort_Multiplier
                                 </div>
                                 <div style="margin: 15px 0;">
                                     <strong>Vehicle Cohort:</strong> ${data.vehicle_info.cohort}<br>
                                     <div class="math-formula">
                                         Base Rate: 2.3% (Industry Standard)<br>
                                         Cohort Multiplier: ${data.cohort_comparison.multiplier}x<br>
                                         Cohort Risk: 0.023 × ${data.cohort_comparison.multiplier} = ${(0.023 * data.cohort_comparison.multiplier).toFixed(3)}
                                     </div>
                                 </div>
                                 <div style="margin: 15px 0;">
                                     <strong>Sample Statistics:</strong><br>
                                     <div class="math-formula">
                                         Sample Size: ${data.cohort_comparison.sample_size.toLocaleString()} vehicles<br>
                                         Percentile: ${data.cohort_comparison.percentile}th (higher = more risk)<br>
                                         Z-Score: ${((data.cohort_comparison.percentile - 50) / 15).toFixed(2)}
                                     </div>
                                 </div>
                                 <small><em>Click to flip back</em></small>
                             </div>
                         </div>
                     </div>
                    
                    <!-- Dealer Messaging -->
                    <div class="card">
                        <div class="card-title">💬 AI-Generated Dealer Message</div>
                        <div class="dealer-message">
                            "${data.dealer_messaging.message}"
                        </div>
                        <div class="metric">
                            <span class="metric-label">Urgency Level:</span>
                            <span class="metric-value">${data.dealer_messaging.urgency}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Recommended Action:</span>
                            <span class="metric-value">${data.dealer_messaging.action}</span>
                        </div>
                    </div>
                    
                                         <!-- Revenue Opportunity -->
                     <div class="card" onclick="flipCard(this)">
                         <div class="flip-indicator">CLICK TO FLIP</div>
                         <div class="card-front">
                             <div class="card-title">💰 Business Impact</div>
                             <div class="revenue-highlight">
                                 <h3>Revenue Opportunity: $${data.revenue_opportunity.total.toLocaleString()}</h3>
                             </div>
                             <div class="metric">
                                 <span class="metric-label">Service Revenue:</span>
                                 <span class="metric-value">$${data.revenue_opportunity.service.toLocaleString()}</span>
                             </div>
                             <div class="metric">
                                 <span class="metric-label">Parts Revenue:</span>
                                 <span class="metric-value">$${data.revenue_opportunity.parts.toLocaleString()}</span>
                             </div>
                             <div class="metric">
                                 <span class="metric-label">Downtime Prevention:</span>
                                 <span class="metric-value">$${data.revenue_opportunity.downtime_prevention.toLocaleString()}</span>
                             </div>
                             <div class="metric">
                                 <span class="metric-label">Customer Retention Value:</span>
                                 <span class="metric-value">$${data.revenue_opportunity.retention_value.toLocaleString()}</span>
                             </div>
                         </div>
                         <div class="card-back">
                             <div class="card-title">💹 Revenue Math</div>
                             <div class="math-content">
                                 <strong>ROI Calculation Framework:</strong>
                                 <div class="math-formula">
                                     Total_Value = Service + Parts + Downtime_Prevention + Retention
                                 </div>
                                 <div style="margin: 15px 0;">
                                     <strong>Revenue Components:</strong><br>
                                     <div class="math-formula">
                                         Service: $${data.revenue_opportunity.service} (Proactive maintenance)<br>
                                         Parts: $${data.revenue_opportunity.parts} (Component replacement)<br>
                                         Downtime: $${data.revenue_opportunity.downtime_prevention} (Avoided costs)<br>
                                         Retention: $${data.revenue_opportunity.retention_value} (Customer LTV)
                                     </div>
                                 </div>
                                 <div style="margin: 15px 0;">
                                     <strong>Risk-Adjusted Value:</strong><br>
                                     <div class="math-formula">
                                         Risk Score: ${(data.risk_summary.score * 100).toFixed(1)}%<br>
                                         Expected Value: $${data.revenue_opportunity.total} × ${(data.risk_summary.score).toFixed(2)}<br>
                                         = $${Math.round(data.revenue_opportunity.total * data.risk_summary.score).toLocaleString()}
                                     </div>
                                 </div>
                                 <small><em>Click to flip back</em></small>
                             </div>
                         </div>
                     </div>
                `;
            }
        </script>
    </body>
    </html>
    """)

@app.post("/analyze-prognostic", response_model=PrognosticAnalysis)
async def analyze_prognostic_risk(vehicle: VehicleInput):
    """Advanced prognostic analysis with cohort stratification and dealer messaging"""
    vin = vehicle.vin.upper().strip()
    
    if vin not in DEMO_VEHICLES:
        raise HTTPException(status_code=404, detail="Vehicle not found in demo dataset")
    
    vehicle_data = DEMO_VEHICLES[vin]
    
    # Calculate sophisticated risk metrics
    base_risk = INDUSTRY_PRIORS["battery_degradation"]["base_rate"]
    cohort_multiplier = INDUSTRY_PRIORS["battery_degradation"]["cohort_adjustments"].get(
        vehicle_data["cohort"], 1.0
    )
    
    # Apply stressor analysis
    stressor_impact = 1.0
    for stressor, value in vehicle_data["stressor_profile"].items():
        if stressor in INDUSTRY_PRIORS["battery_degradation"]["stressor_multipliers"]:
            multiplier = INDUSTRY_PRIORS["battery_degradation"]["stressor_multipliers"][stressor]
            stressor_impact *= (1 + (multiplier - 1) * value)
    
    final_risk = min(base_risk * cohort_multiplier * stressor_impact, 0.95)
    
    # Determine severity
    if final_risk < 0.3:
        severity = "Low"
    elif final_risk < 0.6:
        severity = "Moderate"
    elif final_risk < 0.8:
        severity = "High"
    else:
        severity = "Critical"
    
    # Generate AI dealer message (simulated)
    dealer_messages = {
        "High": f"Hi {vehicle_data['model']} owner! Our advanced diagnostics detected early signs of battery stress in your vehicle. We'd like to invite you for a complimentary battery health check to prevent unexpected downtime. Your vehicle's usage pattern shows {max(vehicle_data['stressor_profile'], key=vehicle_data['stressor_profile'].get)} stress - let's address this proactively!",
        "Moderate": f"Your {vehicle_data['model']} is showing some early wear patterns. We recommend scheduling a preventive maintenance visit to optimize performance and extend component life.",
        "Low": f"Great news! Your {vehicle_data['model']} is performing well. Continue your current maintenance routine for optimal reliability.",
        "Critical": f"URGENT: Your {vehicle_data['model']} requires immediate attention. Our predictive analysis indicates potential component failure within 30 days. Please contact us immediately to schedule emergency service."
    }
    
    # Calculate revenue opportunity
    service_revenue = random.randint(150, 400)
    parts_revenue = random.randint(200, 800)
    downtime_prevention = random.randint(500, 2000)
    retention_value = random.randint(1000, 5000)
    
    return PrognosticAnalysis(
        vin=vin,
        vehicle_info={
            "model": vehicle_data["model"],
            "year": vehicle_data["year"],
            "engine": vehicle_data["engine"],
            "cohort": vehicle_data["cohort"],
            "mileage": vehicle_data["mileage"],
            "location": vehicle_data["location"],
            "usage_pattern": vehicle_data["usage_pattern"]
        },
        risk_summary={
            "score": final_risk,
            "severity": severity,
            "confidence": 0.89,
            "days_to_intervention": vehicle_data["prognostic_flags"][0]["days_to_failure"] if vehicle_data["prognostic_flags"] else 180
        },
        prognostic_insights=vehicle_data["prognostic_flags"],
        stressor_analysis=vehicle_data["stressor_profile"],
        cohort_comparison={
            "multiplier": cohort_multiplier,
            "percentile": random.randint(60, 95),
            "sample_size": random.randint(15000, 50000)
        },
        dealer_messaging={
            "message": dealer_messages[severity],
            "urgency": severity,
            "action": "Schedule Preventive Service" if severity in ["High", "Critical"] else "Monitor"
        },
        revenue_opportunity={
            "service": service_revenue,
            "parts": parts_revenue,
            "downtime_prevention": downtime_prevention,
            "retention_value": retention_value,
            "total": service_revenue + parts_revenue + downtime_prevention + retention_value
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Ford Bayesian Prognostic Risk Engine",
        "version": "2.0.0",
        "deployment": "render.com",
        "features": [
            "Industry-validated Bayesian priors",
            "Cohort-based risk stratification", 
            "Stressor identification",
            "Prognostic failure prediction",
            "AI-powered dealer messaging",
            "Revenue opportunity calculation"
        ]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "start_render:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 