#!/usr/bin/env python3
"""
Bayesian Vehicle Risk Engine - Advanced Stressor Platform
Cohort-based behavioral stressor identification for dealer engagement
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
    title="Bayesian Vehicle Stressor Engine",
    description="Advanced Cohort-Based Behavioral Analysis & Dealer Messaging Platform",
    version="2.0.1"
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
        "base_rate": 0.145,  # Historical Repair Data
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
        "stressor_flags": [
            {
                "component": "Battery",
                "risk_increase": 0.234,
                "stressor": "SOC Decline Pattern",
                "likelihood_ratio": 6.50,
                "cohort_outlier": "95th percentile",
                "confidence": 0.92
            },
            {
                "component": "Transmission",
                "risk_increase": 0.156,
                "stressor": "Thermal Cycling",
                "likelihood_ratio": 3.21,
                "cohort_outlier": "87th percentile",
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
        "stressor_flags": [
            {
                "component": "Engine",
                "risk_increase": 0.067,
                "stressor": "Oil Interval Extension",
                "likelihood_ratio": 2.78,
                "cohort_outlier": "68th percentile",
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
        "stressor_flags": [
            {
                "component": "Engine",
                "risk_increase": 0.198,
                "stressor": "High RPM Pattern",
                "likelihood_ratio": 2.34,
                "cohort_outlier": "91st percentile",
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

class StressorAnalysis(BaseModel):
    vin: str
    vehicle_info: Dict
    risk_summary: Dict
    stressor_insights: List[Dict]
    stressor_analysis: Dict
    cohort_comparison: Dict
    dealer_messaging: Dict
    revenue_opportunity: Dict

@app.get("/", response_class=HTMLResponse)
async def stressor_dashboard():
    """Advanced Stressor Dashboard - Dealer Engagement Platform"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bayesian Vehicle Stressor Engine</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
                min-height: 100vh;
                color: white;
                overflow-x: hidden;
            }
            
            .header {
                background: rgba(255,255,255,0.1);
                padding: 24px;
                text-align: center;
                border-bottom: 1px solid rgba(255,255,255,0.2);
                backdrop-filter: blur(10px);
            }
            
            .logo { 
                font-size: 32px; 
                font-weight: 700; 
                margin-bottom: 8px;
                color: white;
                letter-spacing: -0.5px;
            }
            
            .subtitle { 
                opacity: 0.9; 
                font-size: 16px; 
                color: rgba(255,255,255,0.8);
                font-weight: 400;
            }
            
            .main-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 32px 24px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 24px;
            }
            
                                      .card {
                 background: rgba(255,255,255,0.1);
                 border-radius: 16px;
                 padding: 0;
                 backdrop-filter: blur(20px);
                 border: 1px solid rgba(255,255,255,0.2);
                 position: relative;
                 cursor: pointer;
                 min-height: 320px;
                 max-height: 450px;
                 overflow: hidden;
                 perspective: 1000px;
             }
             
             .card-inner {
                 position: relative;
                 width: 100%;
                 height: 100%;
                 text-align: center;
                 transition: transform 0.6s;
                 transform-style: preserve-3d;
             }
             
             .card.flipped .card-inner {
                 transform: rotateY(180deg);
             }
             
             .card-front, .card-back {
                 position: absolute;
                 width: 100%;
                 height: 100%;
                 padding: 20px;
                 border-radius: 16px;
                 -webkit-backface-visibility: hidden;
                 backface-visibility: hidden;
                 overflow-y: auto;
                 overflow-x: hidden;
             }
             
             .card-front {
                 background: rgba(255,255,255,0.1);
             }
             
             .card-back {
                 background: rgba(30,64,175,0.2);
                 border: 1px solid rgba(96,165,250,0.4);
                 transform: rotateY(180deg);
             }
            
                         .math-content {
                 font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
                 font-size: 12px;
                 line-height: 1.5;
                 color: rgba(255,255,255,0.9);
                 max-height: 350px;
                 overflow-y: auto;
             }
            
                         .math-formula {
                 background: rgba(0,0,0,0.3);
                 padding: 10px;
                 border-radius: 6px;
                 margin: 8px 0;
                 border-left: 3px solid #60a5fa;
                 font-weight: 500;
                 font-size: 11px;
                 line-height: 1.4;
             }
            
            .flip-indicator {
                position: absolute;
                top: 12px;
                right: 12px;
                background: rgba(96,165,250,0.3);
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .card-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 16px;
                color: white;
                border-bottom: 2px solid rgba(255,255,255,0.2);
                padding-bottom: 12px;
            }
            
            .input-section {
                grid-column: 1 / -1;
                text-align: center;
                background: rgba(255,255,255,0.1);
            }
            
            .vin-input {
                width: 320px;
                padding: 16px 20px;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                background: rgba(255,255,255,0.95);
                color: #1e40af;
                margin: 0 12px;
                font-weight: 500;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            .analyze-btn {
                padding: 16px 32px;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                background: linear-gradient(45deg, #ef4444, #dc2626);
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(239,68,68,0.3);
            }
            
            .analyze-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(239,68,68,0.4);
            }
            
            .demo-vins {
                margin-top: 24px;
                display: flex;
                justify-content: center;
                gap: 12px;
                flex-wrap: wrap;
            }
            
            .demo-vin {
                padding: 12px 20px;
                background: rgba(255,255,255,0.15);
                border-radius: 24px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.2);
                font-weight: 500;
            }
            
            .demo-vin:hover {
                background: rgba(255,255,255,0.25);
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
                 margin-top: 24px;
                 max-width: 1200px;
                 margin-left: auto;
                 margin-right: auto;
             }
            
            .metric {
                display: flex;
                justify-content: space-between;
                margin: 12px 0;
                padding: 12px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
            }
            
            .metric-label { 
                color: rgba(255,255,255,0.8); 
                font-weight: 500;
            }
            .metric-value { 
                font-weight: 600; 
                color: white;
            }
            
            .risk-high { color: #fca5a5; }
            .risk-moderate { color: #fde047; }
            .risk-low { color: #86efac; }
            
            .stressor-bar {
                width: 100%;
                height: 24px;
                background: rgba(255,255,255,0.1);
                border-radius: 12px;
                overflow: hidden;
                margin: 8px 0;
            }
            
            .stressor-fill {
                height: 100%;
                background: linear-gradient(90deg, #86efac, #fde047, #fca5a5);
                transition: width 0.8s ease;
                border-radius: 12px;
            }
            
            .stressor-alert {
                background: rgba(239,68,68,0.2);
                border-left: 4px solid #ef4444;
                padding: 16px;
                margin: 12px 0;
                border-radius: 8px;
            }
            
            .dealer-message {
                background: rgba(96,165,250,0.2);
                border-left: 4px solid #60a5fa;
                padding: 16px;
                margin: 12px 0;
                border-radius: 8px;
                font-style: italic;
                line-height: 1.5;
            }
            
            .revenue-highlight {
                background: rgba(34,197,94,0.2);
                border-left: 4px solid #22c55e;
                padding: 16px;
                margin: 12px 0;
                border-radius: 8px;
                text-align: center;
            }
            
            .loading {
                text-align: center;
                padding: 48px;
                color: white;
                font-size: 18px;
            }
            
            .loading::after {
                content: "⚡";
                animation: pulse 1s infinite;
                font-size: 28px;
                margin-left: 12px;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }
            
                         @media (max-width: 768px) {
                 .main-container {
                     grid-template-columns: 1fr;
                     padding: 16px;
                 }
                 .vin-input {
                     width: 280px;
                     margin: 8px;
                 }
                 .results-grid {
                     grid-template-columns: 1fr;
                     gap: 16px;
                 }
                 .card {
                     min-height: 300px;
                     max-height: 400px;
                     padding: 16px;
                 }
                 .card-front, .card-back {
                     padding: 16px;
                 }
                 .math-content {
                     font-size: 11px;
                     max-height: 300px;
                 }
                 .math-formula {
                     padding: 8px;
                     margin: 6px 0;
                     font-size: 10px;
                 }
             }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🎯 VEHICLE STRESSOR ENGINE</div>
            <div class="subtitle">Cohort-Based Behavioral Analysis for Dealer Engagement</div>
        </div>
        
        <div class="main-container">
            <div class="card input-section">
                <div class="card-title">🔬 Stressor Analysis</div>
                <p style="margin-bottom: 24px; color: rgba(255,255,255,0.8); line-height: 1.5;">
                    Enter a VIN to identify <strong>behavioral stressor patterns</strong> using industry-validated priors.
                    See how this vehicle compares to its cohort and generate dealer conversation opportunities.
                </p>
                
                <input type="text" id="vin" class="vin-input" placeholder="Enter 17-character VIN">
                <button class="analyze-btn" onclick="analyzeVehicle()">🔍 Analyze Stressors</button>
                
                <div class="demo-vins">
                    <div class="demo-vin" onclick="setVin('1FMCU9GD5LUA12345')">
                        🚛 F-150 Heavy Duty (High Stressor)
                    </div>
                    <div class="demo-vin" onclick="setVin('1FTFW1ET5DFC67890')">
                        🚗 F-150 Personal (Moderate Stressor)
                    </div>
                    <div class="demo-vin" onclick="setVin('1FA6P8TH8J5123456')">
                        🏎️ Mustang GT (Performance Stressor)
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
                vinInput.value = '';
                setTimeout(() => {
                    vinInput.value = vin;
                    vinInput.focus();
                }, 100);
            }
            
            function flipCard(cardElement) {
                cardElement.classList.toggle('flipped');
                // Prevent event bubbling
                event.stopPropagation();
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
                resultsGrid.innerHTML = '<div class="loading">🔬 Analyzing Behavioral Stressors...</div>';
                
                try {
                    const response = await fetch('/analyze-stressors', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ vin: vin })
                    });
                    
                    const data = await response.json();
                    displayResults(data);
                } catch (error) {
                    resultsGrid.innerHTML = '<div style="color: #fca5a5; text-align: center;">Analysis failed. Please try again.</div>';
                }
            }
            
            function displayResults(data) {
                const resultsGrid = document.getElementById('resultsGrid');
                
                resultsGrid.innerHTML = `
                    <!-- Customer Overview - Clean Dealer View -->
                    <div class="card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-inner">
                            <div class="card-front">
                                <div class="card-title">👤 ${data.vehicle_info.model}</div>
                                <div style="text-align: center; margin: 30px 0;">
                                    <div style="font-size: 20px; opacity: 0.8;">${data.vehicle_info.mileage.toLocaleString()} miles</div>
                                    <div style="font-size: 16px; opacity: 0.7;">${data.vehicle_info.location}</div>
                                </div>
                                <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 12px; text-align: center;">
                                    <div style="font-size: 18px; font-weight: 600;">${data.vehicle_info.usage_pattern}</div>
                                </div>
                            </div>
                            <div class="card-back">
                                <div class="card-title">🏗️ For Your Engineering Team</div>
                                <div class="math-content">
                                    <strong>Why We Built Cohorts This Way:</strong>
                                    <div class="math-formula">
                                        We minimize cohorts to maximize dealer coverage. Start small, scale smart.
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <strong>This Vehicle's Cohort:</strong><br>
                                        ${data.vehicle_info.cohort}
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <strong>Your Rollout Strategy:</strong><br>
                                        • Phase 1: 5-10 cohorts (beta dealers)<br>
                                        • Phase 2: 15-25 cohorts (US expansion)<br>
                                        • Phase 3: 30-50 cohorts (North America)<br>
                                        • Always prioritize coverage over granularity
                                    </div>
                                    <div style="margin: 15px 0;">
                                        <strong>Statistical Foundation:</strong><br>
                                        ${data.cohort_comparison.sample_size.toLocaleString()} similar vehicles provide robust analysis power
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Conversation Opportunity - Clean Dealer View -->
                    <div class="card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-inner">
                            <div class="card-front">
                            <div class="card-title">💬 Conversation Opportunity</div>
                            <div style="text-align: center; margin: 20px 0;">
                                <div style="font-size: 32px; font-weight: bold; color: ${data.risk_summary.severity === 'High' ? '#fca5a5' : data.risk_summary.severity === 'Moderate' ? '#fde047' : '#86efac'};">
                                    ${data.risk_summary.severity}
                                </div>
                                <div style="font-size: 14px; opacity: 0.8;">Priority Level</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 16px; border-radius: 12px; margin: 16px 0;">
                                <div style="font-size: 14px; opacity: 0.9;">Talking Point</div>
                                <div style="font-size: 16px; font-weight: 500; line-height: 1.4;">
                                    ${data.risk_summary.severity === 'High' ? 'Behavioral patterns suggest proactive maintenance discussion' : 
                                      data.risk_summary.severity === 'Moderate' ? 'Good opportunity for maintenance conversation' : 
                                      'Reinforce current maintenance habits'}
                                </div>
                            </div>
                        </div>
                        <div class="card-back">
                            <div class="card-title">🧠 Stressor Score Logic</div>
                            <div class="math-content">
                                <strong>No Synchronous Bayesian Inference:</strong>
                                <div class="math-formula">
                                    All calculations pre-computed overnight → FastAPI serves cached results
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Score Calculation:</strong><br>
                                    • Industry base rates (Argon, NHTSA)<br>
                                    • Cohort-specific multipliers<br>
                                    • Stressor pattern matching<br>
                                    • Historical failure correlation
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Daily Recalculation:</strong><br>
                                    Same VIN yesterday ≠ Same VIN today<br>
                                    Fresh leads every day as behavior changes
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Performance:</strong> Sub-millisecond API response<br>
                                    <strong>Confidence:</strong> ${(data.risk_summary.confidence * 100).toFixed(0)}%
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Component Stressors - What Dealers Need to Know -->
                    <div class="card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-front">
                            <div class="card-title">⚡ Key Issues to Discuss</div>
                            ${data.stressor_insights.map(insight => `
                                <div style="background: rgba(239,68,68,0.15); border-left: 4px solid #ef4444; padding: 14px; margin: 12px 0; border-radius: 8px;">
                                    <div style="font-size: 16px; font-weight: 600; margin-bottom: 4px;">
                                        ${insight.component === 'Battery' ? '🔋 Battery Stress' : 
                                          insight.component === 'Engine' ? '🔧 Engine Patterns' : 
                                          '⚙️ Transmission Stress'}
                                    </div>
                                    <div style="font-size: 14px; opacity: 0.9;">
                                        ${insight.component === 'Battery' ? 'Cold weather + short trips affecting battery life' :
                                          insight.component === 'Engine' ? 'Usage patterns impacting engine performance' :
                                          'Thermal cycling from driving patterns'}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="card-back">
                            <div class="card-title">🔬 Modular Stressor System</div>
                            <div class="math-content">
                                <strong>Component-Specific Stressor Combinations:</strong>
                                <div class="math-formula">
                                    Different components = Different stressor fingerprints
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Diesel Regen Issues:</strong><br>
                                    • Temperature delta (25°F+ ignition off → start)<br>
                                    • Short trips (insufficient regen time)
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Battery Issues:</strong><br>
                                    • Temperature delta<br>
                                    • Short trips<br>
                                    • Ignition cycles (start/stop stress)
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Engine/Transmission:</strong><br>
                                    • Odometer patterns<br>
                                    • Trip characteristics<br>
                                    • Ignition cycles<br>
                                    • Extreme heat exposure
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>LLM Enrichment:</strong><br>
                                    System feeds precise stressor data to LLM for contextual dealer conversations
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Customer Behavior - Simple for Dealers -->
                    <div class="card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-front">
                            <div class="card-title">📊 Driving Patterns</div>
                            <div style="margin: 16px 0;">
                                ${Object.entries(data.stressor_analysis).slice(0, 3).map(([stressor, value]) => `
                                    <div style="margin: 12px 0;">
                                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                            <span style="font-size: 14px; font-weight: 500;">
                                                ${stressor === 'soc_decline' ? 'Cold Weather Impact' :
                                                  stressor === 'trip_cycling' ? 'Short Trip Frequency' :
                                                  stressor === 'climate_stress' ? 'Climate Exposure' :
                                                  stressor === 'high_rpm' ? 'Performance Usage' :
                                                  'Usage Intensity'}
                                            </span>
                                            <span style="font-weight: 600;">${value > 0.7 ? 'High' : value > 0.4 ? 'Moderate' : 'Low'}</span>
                                        </div>
                                        <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.2); border-radius: 4px; overflow: hidden;">
                                            <div style="height: 100%; background: ${value > 0.7 ? '#fca5a5' : value > 0.4 ? '#fde047' : '#86efac'}; width: ${value * 100}%; border-radius: 4px; transition: width 0.8s ease;"></div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        <div class="card-back">
                            <div class="card-title">📈 Behavioral Analysis Architecture</div>
                            <div class="math-content">
                                <strong>Real-Time Stressor Detection:</strong>
                                <div class="math-formula">
                                    Telemetry streams → Pattern recognition → Stressor identification
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Temperature Delta Tracking:</strong><br>
                                    • Monitor ignition off temperature<br>
                                    • Track next start temperature<br>
                                    • Flag 25°F+ deltas as stressor<br>
                                    • Correlate with component stress
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Trip Pattern Analysis:</strong><br>
                                    • Trip duration vs. component warm-up time<br>
                                    • Ignition cycle frequency<br>
                                    • Insufficient regen opportunity detection<br>
                                    • Battery charging time analysis
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Pre-Calculation Strategy:</strong><br>
                                    All patterns computed overnight, indexed for instant dealer access
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Cohort Position - Clean for Dealers -->
                    <div class="card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-front">
                            <div class="card-title">📍 Vehicle Position</div>
                            <div style="text-align: center; margin: 20px 0;">
                                <div style="font-size: 28px; font-weight: bold; margin-bottom: 8px;">
                                    ${data.cohort_comparison.percentile}th
                                </div>
                                <div style="font-size: 14px; opacity: 0.8;">Percentile in Cohort</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); padding: 16px; border-radius: 12px; margin: 16px 0;">
                                <div style="font-size: 14px; opacity: 0.9;">Compared to</div>
                                <div style="font-size: 18px; font-weight: 600;">${data.cohort_comparison.sample_size.toLocaleString()} Similar Vehicles</div>
                            </div>
                            <div style="font-size: 14px; text-align: center; opacity: 0.8;">
                                ${data.cohort_comparison.percentile > 80 ? '🔴 High outlier - Great conversation opportunity' : 
                                  data.cohort_comparison.percentile > 60 ? '🟡 Moderate outlier - Good talking point' : 
                                  '🟢 Normal range - Maintenance reinforcement'}
                            </div>
                        </div>
                        <div class="card-back">
                            <div class="card-title">🎯 Cohort Outlier Strategy</div>
                            <div class="math-content">
                                <strong>Outlier = Conversation Opportunity:</strong>
                                <div class="math-formula">
                                    Statistical outliers in cohort behavior = Dealer leads
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Percentile Interpretation:</strong><br>
                                    • 80th+ percentile = High priority conversation<br>
                                    • 60-80th percentile = Moderate opportunity<br>
                                    • <60th percentile = Maintenance reinforcement<br>
                                    • Daily recalculation = Fresh leads
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>This Vehicle:</strong><br>
                                    Rank: ${data.cohort_comparison.percentile}th of ${data.cohort_comparison.sample_size.toLocaleString()}<br>
                                    Status: ${data.cohort_comparison.percentile > 80 ? 'HIGH OUTLIER' : data.cohort_comparison.percentile > 60 ? 'MODERATE OUTLIER' : 'NORMAL RANGE'}
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Business Logic:</strong><br>
                                    Outliers get dealer attention, normal vehicles get maintenance reinforcement
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- AI Conversation - What Dealers See -->
                    <div class="card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-front">
                            <div class="card-title">🤖 Suggested Conversation</div>
                            <div style="background: rgba(96,165,250,0.2); border-left: 4px solid #60a5fa; padding: 16px; margin: 16px 0; border-radius: 8px; font-style: italic; line-height: 1.5;">
                                "${data.dealer_messaging.message.substring(0, 200)}..."
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 16px;">
                                <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; flex: 1; margin-right: 8px; text-align: center;">
                                    <div style="font-size: 12px; opacity: 0.8;">Priority</div>
                                    <div style="font-size: 16px; font-weight: 600;">${data.dealer_messaging.urgency}</div>
                                </div>
                                <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; flex: 1; margin-left: 8px; text-align: center;">
                                    <div style="font-size: 12px; opacity: 0.8;">Action</div>
                                    <div style="font-size: 16px; font-weight: 600;">${data.dealer_messaging.action.split(' ')[0]}</div>
                                </div>
                            </div>
                        </div>
                        <div class="card-back">
                            <div class="card-title">🧠 LLM Enrichment Strategy</div>
                            <div class="math-content">
                                <strong>Contextual Conversation Generation:</strong>
                                <div class="math-formula">
                                    Stressor data + Cohort position + Component issues = Personalized dealer script
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>LLM Training Inputs:</strong><br>
                                    • Specific stressor combinations<br>
                                    • Component vulnerability mapping<br>
                                    • Cohort comparison context<br>
                                    • Regional/seasonal factors<br>
                                    • Historical repair correlations
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Example Enrichment:</strong><br>
                                    "Your diesel F-150 in Detroit shows 28°F temperature deltas and 12-minute average trips - perfect storm for regen issues. Let's discuss extended drive cycles."
                                </div>
                                <div style="margin: 12px 0;">
                                    <strong>Dynamic Updates:</strong><br>
                                    LLM gets fresh stressor data daily, generates new conversation angles as patterns evolve
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
        </script>
    </body>
    </html>
    """)

@app.post("/analyze-stressors", response_model=StressorAnalysis)
async def analyze_stressor_patterns(vehicle: VehicleInput):
    """Analyze behavioral stressor patterns for dealer conversations"""
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
    
    # Generate dealer conversation messages (no failure prediction)
    dealer_messages = {
        "High": f"Based on our cohort analysis, your {vehicle_data['model']} shows behavioral patterns similar to vehicles that have experienced issues. Your usage pattern indicates {max(vehicle_data['stressor_profile'], key=vehicle_data['stressor_profile'].get).replace('_', ' ')} stress levels that are outliers in your cohort. This creates a great opportunity for a preventive maintenance conversation.",
        "Moderate": f"Your {vehicle_data['model']} shows some interesting behavioral patterns compared to similar vehicles in your cohort. We'd love to discuss how your driving patterns compare and explore preventive maintenance options.",
        "Low": f"Great news! Your {vehicle_data['model']} behavioral patterns are well within normal ranges for your cohort. This is a perfect opportunity to reinforce good maintenance habits.",
        "Critical": f"Your {vehicle_data['model']} shows behavioral stressor patterns that are significant outliers in your cohort. Based on historical data from similar vehicles, this creates an excellent opportunity for a proactive service conversation."
    }
    
    # Calculate revenue opportunity
    service_revenue = random.randint(150, 400)
    parts_revenue = random.randint(200, 800)
    downtime_prevention = random.randint(500, 2000)
    retention_value = random.randint(1000, 5000)
    
    return StressorAnalysis(
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
            "confidence": 0.89
        },
        stressor_insights=vehicle_data["stressor_flags"],
        stressor_analysis=vehicle_data["stressor_profile"],
        cohort_comparison={
            "multiplier": cohort_multiplier,
            "percentile": random.randint(60, 95),
            "sample_size": random.randint(15000, 50000)
        },
        dealer_messaging={
            "message": dealer_messages[severity],
            "urgency": severity,
            "action": "Preventive Service Discussion" if severity in ["High", "Critical"] else "Maintenance Reinforcement"
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
        "service": "Bayesian Vehicle Stressor Engine",
        "version": "2.0.0",
        "deployment": "render.com",
        "features": [
            "Industry-validated behavioral analysis",
            "Cohort-based stressor identification", 
            "Dealer conversation opportunities",
            "No failure date predictions",
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