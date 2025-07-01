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
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client (optional)
client = None
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    logger.info("✅ OpenAI client initialized")
except ImportError:
    logger.warning("⚠️ OpenAI not available - using fallback messaging")
except Exception as e:
    logger.warning(f"⚠️ OpenAI initialization failed: {e}")
    client = None

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
    dealer_conversation: str

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
                 padding: 20px;
                 backdrop-filter: blur(10px);
                 border: 1px solid rgba(255,255,255,0.2);
                 transition: all 0.3s ease;
                 cursor: pointer;
                 position: relative;
                 min-height: 280px;
                 max-height: 350px;
                 overflow: hidden;
                 perspective: 1000px;
             }
             
             .card-inner {
                 position: relative;
                 width: 100%;
                 height: 100%;
                 text-align: left;
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
                 backface-visibility: hidden;
                 padding: 0;
                 overflow-y: auto;
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
                 grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                 gap: 16px;
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
                     gap: 12px;
                 }
                 .card {
                     min-height: 240px;
                     max-height: 300px;
                     padding: 16px;
                 }
                 .card-front, .card-back {
                     padding: 16px;
                 }
                 .math-content {
                     font-size: 11px;
                     max-height: 200px;
                 }
                 .math-formula {
                     padding: 6px;
                     margin: 4px 0;
                     font-size: 10px;
                 }
             }
            
            .lead-card {
                border: 2px solid #22c55e;
                box-shadow: 0 8px 32px rgba(34, 197, 94, 0.3);
                background: rgba(34, 197, 94, 0.1);
            }
            
            .lead-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px rgba(34, 197, 94, 0.4);
            }
            
            .followup-card {
                border: 2px solid #8b5cf6;
                box-shadow: 0 8px 32px rgba(139, 92, 246, 0.3);
                background: rgba(139, 92, 246, 0.1);
            }
            
            .followup-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px rgba(139, 92, 246, 0.4);
            }
            
            .dashboard-card {
                border: 2px solid #3b82f6;
                box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
                background: rgba(59, 130, 246, 0.1);
            }
            
            .dashboard-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px rgba(59, 130, 246, 0.4);
            }
            
            .ai-generate-btn {
                background: linear-gradient(45deg, #8b5cf6, #7c3aed);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
            }
            
            .ai-generate-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
            }
            
            .phone-card {
                background: linear-gradient(135deg, rgba(34,197,94,0.2), rgba(16,163,74,0.2));
                border: 2px solid rgba(34,197,94,0.4);
                box-shadow: 0 8px 32px rgba(34,197,94,0.3);
            }
            
            .phone-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px rgba(34,197,94,0.4);
            }
            
            .phone-card .card-title {
                color: #22c55e;
                text-shadow: 0 0 10px rgba(34,197,94,0.3);
            }
            
            /* DEALER LEAD CAROUSEL - Side Scrolling Display */
            .lead-carousel {
                position: fixed;
                right: 20px;
                top: 120px;
                width: 320px;
                height: calc(100vh - 140px);
                background: rgba(15,23,42,0.95);
                border-radius: 16px;
                border: 1px solid rgba(96,165,250,0.3);
                backdrop-filter: blur(15px);
                overflow: hidden;
                z-index: 50;
                box-shadow: 0 8px 32px rgba(0,0,0,0.4);
                transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                transform: translateX(0);
                opacity: 1;
            }
            
            .carousel-header {
                background: linear-gradient(45deg, #1e40af, #3b82f6);
                padding: 16px;
                text-align: center;
                border-bottom: 1px solid rgba(96,165,250,0.3);
            }
            
            .carousel-title {
                font-size: 14px;
                font-weight: 700;
                color: white;
                margin-bottom: 4px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .carousel-subtitle {
                font-size: 11px;
                color: rgba(255,255,255,0.7);
            }
            
            .carousel-content {
                height: calc(100% - 80px);
                overflow: hidden;
                position: relative;
            }
            
            .lead-cards-container {
                animation: scrollLeads 45s linear infinite;
                display: flex;
                flex-direction: column;
                gap: 16px;
                padding: 16px;
            }
            
            @keyframes scrollLeads {
                0% { transform: translateY(100%); }
                100% { transform: translateY(-100%); }
            }
            
            .dealer-lead-card {
                background: rgba(30,41,59,0.9);
                border-radius: 12px;
                padding: 16px;
                border: 1px solid rgba(96,165,250,0.2);
                min-height: 160px;
                transition: all 0.3s ease;
                position: relative;
            }
            
            .dealer-lead-card:hover {
                border-color: rgba(96,165,250,0.5);
                transform: scale(1.02);
                box-shadow: 0 4px 20px rgba(96,165,250,0.2);
            }
            
            .lead-priority {
                position: absolute;
                top: 12px;
                right: 12px;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            .priority-high {
                background: rgba(239,68,68,0.2);
                color: #fca5a5;
                border: 1px solid #ef4444;
            }
            
            .priority-moderate {
                background: rgba(245,158,11,0.2);
                color: #fbbf24;
                border: 1px solid #f59e0b;
            }
            
            .priority-low {
                background: rgba(34,197,94,0.2);
                color: #86efac;
                border: 1px solid #22c55e;
            }
            
            .lead-vehicle {
                font-size: 14px;
                font-weight: 600;
                color: #60a5fa;
                margin-bottom: 8px;
            }
            
            .lead-customer {
                font-size: 12px;
                color: rgba(255,255,255,0.8);
                margin-bottom: 12px;
            }
            
            .lead-opportunity {
                background: rgba(96,165,250,0.1);
                padding: 8px;
                border-radius: 6px;
                margin-bottom: 8px;
                border-left: 3px solid #60a5fa;
            }
            
            .lead-opportunity-text {
                font-size: 11px;
                color: rgba(255,255,255,0.9);
                line-height: 1.4;
            }
            
            .lead-revenue {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 8px;
            }
            
            .revenue-amount {
                font-size: 14px;
                font-weight: 700;
                color: #22c55e;
            }
            
            .conversion-rate {
                font-size: 11px;
                color: rgba(255,255,255,0.6);
            }
            
            .carousel-toggle {
                position: fixed;
                right: 20px;
                top: 80px;
                background: linear-gradient(45deg, #ef4444, #dc2626);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 700;
                cursor: pointer;
                z-index: 51;
                box-shadow: 0 6px 20px rgba(239,68,68,0.6);
                transition: all 0.3s ease;
                animation: pulse-red 2s infinite;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            @keyframes pulse-red {
                0%, 100% { 
                    box-shadow: 0 6px 20px rgba(239,68,68,0.6);
                    transform: scale(1);
                }
                50% { 
                    box-shadow: 0 8px 30px rgba(239,68,68,0.8);
                    transform: scale(1.05);
                }
            }
            
            .carousel-toggle:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(30,64,175,0.6);
            }
            
            /* Hide carousel on mobile */
            @media (max-width: 768px) {
                .lead-carousel, .carousel-toggle {
                    display: none;
                }
            }
        </style>
    </head>
    <body>
        <!-- DEALER LEAD CAROUSEL - Shows What Dealers Actually See -->
        <button class="carousel-toggle" onclick="toggleCarousel()">📊 LIVE LEADS</button>
        
        <div class="lead-carousel" id="leadCarousel">
            <div class="carousel-header">
                <div class="carousel-title">💰 Live Dealer Leads</div>
                <div class="carousel-subtitle">What Your Dashboard Shows</div>
            </div>
            <div class="carousel-content">
                <div class="lead-cards-container">
                    <!-- High Priority Lead -->
                    <div class="dealer-lead-card">
                        <div class="lead-priority priority-high">HIGH</div>
                        <div class="lead-vehicle">2023 F-150 SuperCrew</div>
                        <div class="lead-customer">Detroit, MI • 47,823 miles • Heavy Duty</div>
                        <div class="lead-opportunity">
                            <div class="lead-opportunity-text">
                                "Hi John, I noticed your F-150 shows cold weather + short trip patterns similar to vehicles that needed preventive battery service. You're in the 87th percentile of similar trucks. Can I schedule a quick inspection this week?"
                            </div>
                        </div>
                        <div class="lead-revenue">
                            <div class="revenue-amount">$450</div>
                            <div class="conversion-rate">23% conversion</div>
                        </div>
                    </div>
                    
                    <!-- Moderate Priority Lead -->
                    <div class="dealer-lead-card">
                        <div class="lead-priority priority-moderate">MODERATE</div>
                        <div class="lead-vehicle">2022 Explorer Hybrid</div>
                        <div class="lead-customer">Austin, TX • 34,156 miles • Personal</div>
                        <div class="lead-opportunity">
                            <div class="lead-opportunity-text">
                                "Hello Sarah, your Explorer has some interesting usage patterns that put it in the 72nd percentile. Let's chat about optimizing your hybrid system performance for your specific driving style."
                            </div>
                        </div>
                        <div class="lead-revenue">
                            <div class="revenue-amount">$285</div>
                            <div class="conversion-rate">18% conversion</div>
                        </div>
                    </div>
                    
                    <!-- High Priority Performance Lead -->
                    <div class="dealer-lead-card">
                        <div class="lead-priority priority-high">HIGH</div>
                        <div class="lead-vehicle">2023 Mustang GT</div>
                        <div class="lead-customer">Los Angeles, CA • 12,890 miles • Performance</div>
                        <div class="lead-opportunity">
                            <div class="lead-opportunity-text">
                                "Hi Mike, your Mustang shows high-performance usage patterns that put you in the 91st percentile. This creates a great opportunity for our performance maintenance program."
                            </div>
                        </div>
                        <div class="lead-revenue">
                            <div class="revenue-amount">$380</div>
                            <div class="conversion-rate">21% conversion</div>
                        </div>
                    </div>
                    
                    <!-- Retention/Low Priority Lead -->
                    <div class="dealer-lead-card">
                        <div class="lead-priority priority-low">RETENTION</div>
                        <div class="lead-vehicle">2021 F-150 Regular Cab</div>
                        <div class="lead-customer">Phoenix, AZ • 28,450 miles • Light Duty</div>
                        <div class="lead-opportunity">
                            <div class="lead-opportunity-text">
                                "Great news about your F-150! Your driving patterns show excellent vehicle care. This is perfect timing to discuss our premium maintenance program to keep you in the top tier."
                            </div>
                        </div>
                        <div class="lead-revenue">
                            <div class="revenue-amount">$195</div>
                            <div class="conversion-rate">16% conversion</div>
                        </div>
                    </div>
                    
                    <!-- Another High Priority Lead -->
                    <div class="dealer-lead-card">
                        <div class="lead-priority priority-high">HIGH</div>
                        <div class="lead-vehicle">2022 Expedition Max</div>
                        <div class="lead-customer">Chicago, IL • 41,200 miles • Family Heavy</div>
                        <div class="lead-opportunity">
                            <div class="lead-opportunity-text">
                                "Hi Lisa, your Expedition shows heavy family usage + climate stress patterns. You're at 89th percentile - perfect time for a comprehensive service discussion."
                            </div>
                        </div>
                        <div class="lead-revenue">
                            <div class="revenue-amount">$520</div>
                            <div class="conversion-rate">25% conversion</div>
                        </div>
                    </div>
                    
                    <!-- Moderate Commercial Lead -->
                    <div class="dealer-lead-card">
                        <div class="lead-priority priority-moderate">MODERATE</div>
                        <div class="lead-vehicle">2021 Transit 350</div>
                        <div class="lead-customer">Denver, CO • 67,800 miles • Commercial</div>
                        <div class="lead-opportunity">
                            <div class="lead-opportunity-text">
                                "Hello Tom, your Transit shows commercial usage patterns at 68th percentile. Good opportunity to discuss fleet maintenance optimization and downtime prevention."
                            </div>
                        </div>
                        <div class="lead-revenue">
                            <div class="revenue-amount">$340</div>
                            <div class="conversion-rate">19% conversion</div>
                        </div>
                    </div>
                    
                    <!-- High Priority Diesel Lead -->
                    <div class="dealer-lead-card">
                        <div class="lead-priority priority-high">HIGH</div>
                        <div class="lead-vehicle">2023 F-250 PowerStroke</div>
                        <div class="lead-customer">Houston, TX • 23,100 miles • Heavy Commercial</div>
                        <div class="lead-opportunity">
                            <div class="lead-opportunity-text">
                                "Hi Carlos, your F-250 diesel shows short trip + regen patterns at 94th percentile. This is exactly the kind of usage that benefits from proactive DPF service."
                            </div>
                        </div>
                        <div class="lead-revenue">
                            <div class="revenue-amount">$680</div>
                            <div class="conversion-rate">28% conversion</div>
                        </div>
                    </div>
                    
                    <!-- Moderate Hybrid Lead -->
                    <div class="dealer-lead-card">
                        <div class="lead-priority priority-moderate">MODERATE</div>
                        <div class="lead-vehicle">2022 Escape Hybrid</div>
                        <div class="lead-customer">Seattle, WA • 19,450 miles • Commuter</div>
                        <div class="lead-opportunity">
                            <div class="lead-opportunity-text">
                                "Hi Jennifer, your Escape hybrid shows interesting efficiency patterns. You're at 74th percentile - good time to optimize your hybrid battery performance."
                            </div>
                        </div>
                        <div class="lead-revenue">
                            <div class="revenue-amount">$220</div>
                            <div class="conversion-rate">17% conversion</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="header">
            <div class="logo">💰 FORD LEAD GENERATION ENGINE</div>
            <div class="subtitle">Stressor-Based Behavioral Analysis → AI-Powered Customer Conversations → Revenue</div>
            <div style="margin-top: 20px;">
                <a href="/technical-walkthrough" style="
                    color: #ffffff; 
                    background: linear-gradient(45deg, #8b5cf6, #7c3aed); 
                    text-decoration: none; 
                    font-weight: 700; 
                    padding: 12px 24px; 
                    border: 2px solid #8b5cf6; 
                    border-radius: 25px; 
                    font-size: 15px; 
                    transition: all 0.3s ease;
                    display: inline-block;
                    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 25px rgba(139, 92, 246, 0.6)'" 
                onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 15px rgba(139, 92, 246, 0.4)'">
                    🧠 Technical Mathematics Walkthrough
                </a>
            </div>
        </div>
        
        <div class="main-container">
            <div class="card input-section">
                <div class="card-title">💰 Lead Generation</div>
                <p style="margin-bottom: 24px; color: rgba(255,255,255,0.8); line-height: 1.5;">
                    Enter a VIN to generate <strong>AI-powered dealer conversations</strong> using Ford's stressor data.
                    Our LLM analyzes behavioral patterns and creates personalized customer engagement strategies for maximum revenue.
                </p>
                
                <input type="text" id="vin" class="vin-input" placeholder="Enter 17-character VIN">
                <button class="analyze-btn" onclick="analyzeVehicle()">💰 Generate Lead</button>
                
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
                resultsGrid.innerHTML = '<div class="loading">🤖 Generating AI-Powered Lead...</div>';
                
                try {
                    const response = await fetch('/analyze-stressors', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ vin: vin })
                    });
                    
                    const data = await response.json();
                    displayResults(data);
                } catch (error) {
                    resultsGrid.innerHTML = '<div style="color: #fca5a5; text-align: center;">Lead generation failed. Please try again.</div>';
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
                    </div>
                    
                    <!-- Component Stressors - What Dealers Need to Know -->
                    <div class="card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-inner">
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
                    </div>
                    
                    <!-- Customer Behavior - Simple for Dealers -->
                    <div class="card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-inner">
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
                    </div>
                    
                    <!-- Cohort Position - Clean for Dealers -->
                    <div class="card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-inner">
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
                    </div>
                    
                    <!-- AI LEAD GENERATION - The Money Shot -->
                    <div class="card lead-card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-inner">
                            <div class="card-front">
                                <div class="card-title">💰 GENERATED LEAD</div>
                                <div style="background: linear-gradient(45deg, #22c55e, #16a34a); padding: 16px; border-radius: 12px; margin: 16px 0; color: white; font-weight: 600; text-align: center;">
                                    ${data.risk_summary.severity} Priority Customer
                                </div>
                                
                                <div style="background: rgba(255,255,255,0.15); padding: 16px; border-radius: 12px; margin: 16px 0;">
                                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">🎯 Conversation Starter:</div>
                                    <div id="ai-conversation" style="font-size: 15px; font-weight: 500; line-height: 1.4; font-style: italic;">
                                        "${data.dealer_conversation}"
                                    </div>
                                    
                                    <div style="text-align: center; margin-top: 16px;">
                                        <button id="generate-ai-btn" onclick="generateAIConversation('${data.vehicle_info.vin}')" 
                                                class="ai-generate-btn">
                                            🤖 Generate Personalized Message
                                        </button>
                                        <div id="ai-loading" style="display: none; font-size: 13px; opacity: 0.7; margin-top: 8px;">
                                            🤖 AI is crafting personalized conversation...
                                        </div>
                                    </div>
                                </div>
                                
                                <div style="display: flex; justify-content: space-between; margin-top: 16px;">
                                    <div style="background: rgba(34,197,94,0.2); padding: 12px; border-radius: 8px; flex: 1; margin-right: 8px; text-align: center;">
                                        <div style="font-size: 12px; opacity: 0.8;">Revenue Opportunity</div>
                                        <div style="font-size: 16px; font-weight: 600; color: #22c55e;">$${data.revenue_opportunity.total.toLocaleString()}</div>
                                    </div>
                                    <div style="background: rgba(96,165,250,0.2); padding: 12px; border-radius: 8px; flex: 1; margin-left: 8px; text-align: center;">
                                        <div style="font-size: 12px; opacity: 0.8;">Confidence</div>
                                        <div style="font-size: 16px; font-weight: 600; color: #60a5fa;">${(data.risk_summary.confidence * 100).toFixed(0)}%</div>
                                    </div>
                                </div>
                            </div>
                            <div class="card-back">
                                <div class="card-title">🧠 LLM Lead Generation Engine</div>
                                <div class="math-content">
                                    <strong>Deep Personalization Strategy:</strong>
                                    <div class="math-formula">
                                        Ford Deterministic Data + Environmental Stressors + Cohort Analysis = Personalized Customer Conversations
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>Why This Customer is a ${data.risk_summary.severity} Priority Lead:</strong><br>
                                        ${data.risk_summary.severity === 'High' ? 
                                            `• Stressor combinations: ${Object.entries(data.stressor_analysis).filter(([k,v]) => v > 0.7).map(([k,v]) => `${k.replace('_', ' ')} (${(v*100).toFixed(0)}%)`).join(', ')}<br>• Cohort outlier: ${data.cohort_comparison.percentile}th percentile<br>• Historical correlation: Similar patterns led to ${Math.floor(data.risk_summary.score * 100)}% service events<br>• Timing: Proactive intervention window is NOW` :
                                          data.risk_summary.severity === 'Moderate' ?
                                            `• Moderate stressors: ${Object.entries(data.stressor_analysis).filter(([k,v]) => v > 0.4 && v <= 0.7).map(([k,v]) => `${k.replace('_', ' ')} (${(v*100).toFixed(0)}%)`).join(', ')}<br>• Cohort position: ${data.cohort_comparison.percentile}th percentile<br>• Engagement opportunity: Customer education + service upsell<br>• Revenue potential: Service + parts + retention` :
                                            `• Excellent patterns: All stressors below 40% threshold<br>• Cohort leader: Top ${100-data.cohort_comparison.percentile}% of similar vehicles<br>• Retention strategy: Reinforce good habits<br>• Upsell opportunity: Premium maintenance packages`
                                        }
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>LLM Training Inputs for This Lead:</strong><br>
                                        • Vehicle: ${data.vehicle_info.year} ${data.vehicle_info.model} (${data.vehicle_info.engine})<br>
                                        • Usage: ${data.vehicle_info.usage_pattern} in ${data.vehicle_info.location}<br>
                                        • Mileage: ${data.vehicle_info.mileage.toLocaleString()} miles<br>
                                        • Cohort: ${data.vehicle_info.cohort}<br>
                                        • Stressor fingerprint: ${Object.entries(data.stressor_analysis).map(([k,v]) => `${k}=${(v*100).toFixed(0)}%`).join(', ')}
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>Conversation Outcome Strategy:</strong><br>
                                        1. Lead qualification: ${data.risk_summary.severity} priority<br>
                                        2. Service booking: ${data.dealer_messaging.action}<br>
                                        3. Revenue target: $${data.revenue_opportunity.total.toLocaleString()}<br>
                                        4. Follow-up: Stressor monitoring + cohort updates
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- DEALER DASHBOARD - One-Click Follow-Up System -->
                    <div class="card dashboard-card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-inner">
                            <div class="card-front">
                                <div class="card-title">📊 DEALER DASHBOARD</div>
                                <div style="background: rgba(255,255,255,0.1); padding: 16px; border-radius: 12px; margin: 16px 0;">
                                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 12px;">🎯 One-Click Follow-Up Actions:</div>
                                    
                                    <div style="background: rgba(34,197,94,0.2); padding: 12px; border-radius: 8px; margin: 8px 0; display: flex; justify-content: space-between; align-items: center;">
                                        <div>
                                            <div style="font-weight: 600; color: #22c55e;">LOW RISK VEHICLES (23)</div>
                                            <div style="font-size: 12px; opacity: 0.8;">Retention messaging ready</div>
                                        </div>
                                        <button style="background: #22c55e; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">SEND ALL</button>
                                    </div>
                                    
                                    <div style="background: rgba(139,92,246,0.2); padding: 12px; border-radius: 8px; margin: 8px 0; display: flex; justify-content: space-between; align-items: center;">
                                        <div>
                                            <div style="font-weight: 600; color: #8b5cf6;">RECENTLY SERVICED (15)</div>
                                            <div style="font-size: 12px; opacity: 0.8;">Validation follow-ups ready</div>
                                        </div>
                                        <button style="background: #8b5cf6; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">SEND ALL</button>
                                    </div>
                                    
                                    <div style="background: rgba(239,68,68,0.2); padding: 12px; border-radius: 8px; margin: 8px 0; display: flex; justify-content: space-between; align-items: center;">
                                        <div>
                                            <div style="font-weight: 600; color: #ef4444;">HIGH PRIORITY (8)</div>
                                            <div style="font-size: 12px; opacity: 0.8;">Immediate intervention needed</div>
                                        </div>
                                        <button style="background: #ef4444; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">REVIEW</button>
                                    </div>
                                </div>
                                
                                <div style="text-align: center; margin-top: 16px; font-size: 14px; opacity: 0.8;">
                                    💰 Total 36-Month Value: $${((data.revenue_opportunity.total * 2.3) * 46 / 1000).toFixed(0)}K
                                </div>
                            </div>
                            <div class="card-back">
                                <div class="card-title">🚀 Ecosystem Engagement Engine</div>
                                <div class="math-content">
                                    <strong>The "Stay in Rolodex" Strategy:</strong>
                                    <div class="math-formula">
                                        Continuous touchpoints = Top-of-mind positioning = Loyalty retention
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>Automated Follow-Up Triggers:</strong><br>
                                        • LOW RISK: Monthly "you're doing great" messages<br>
                                        • POST-SERVICE: 7-day validation + 30-day optimization<br>
                                        • HIGH PRIORITY: Immediate intervention + weekly check-ins<br>
                                        • QUARTERLY: Behavioral insights report for all customers
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>The 36-Month Retention Math:</strong><br>
                                        • Touch-and-go customers: 23% retention rate<br>
                                        • Continuous engagement: 67% retention rate<br>
                                        • Revenue difference: $${(data.revenue_opportunity.total * 1.5).toLocaleString()} per customer<br>
                                        • Dealer ROI: 890% on engagement investment
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>Customer Psychology Impact:</strong><br>
                                        "My dealer actually monitors my vehicle performance."<br>
                                        "They follow up to make sure their work was good."<br>
                                        "They care about my success, not just the sale."<br>
                                        → Customer becomes ADVOCATE, not just buyer
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>Competitive Moat:</strong><br>
                                        Other dealers: Transactional relationships<br>
                                        Ford dealers: Continuous advisory partnerships<br>
                                        Result: Customer won't even shop around
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- PHONE CONVERSION ADVANTAGE - The Money Maker -->
                    <div class="card phone-card" onclick="flipCard(this)">
                        <div class="flip-indicator">FLIP FOR TECH</div>
                        <div class="card-inner">
                            <div class="card-front">
                                <div class="card-title">📞 PHONE CONVERSION ADVANTAGE</div>
                                <div style="background: linear-gradient(45deg, #22c55e, #16a34a); padding: 20px; border-radius: 12px; margin: 16px 0; color: white; text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; margin-bottom: 8px;">2.1x HIGHER CONVERSION</div>
                                    <div style="font-size: 14px; opacity: 0.9;">Phone leads vs Web leads</div>
                                </div>
                                
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0;">
                                    <div style="background: rgba(34,197,94,0.2); padding: 16px; border-radius: 8px; text-align: center; border: 2px solid #22c55e;">
                                        <div style="font-size: 18px; font-weight: bold; color: #22c55e;">📞 PHONE</div>
                                        <div style="font-size: 24px; font-weight: bold; color: #22c55e;">23%</div>
                                        <div style="font-size: 12px; opacity: 0.8;">Net Conversion</div>
                                        <div style="font-size: 11px; margin-top: 8px; opacity: 0.7;">
                                            74% Set × 62% Show × 50% Complete
                                        </div>
                                    </div>
                                    <div style="background: rgba(239,68,68,0.2); padding: 16px; border-radius: 8px; text-align: center; border: 2px solid #ef4444;">
                                        <div style="font-size: 18px; font-weight: bold; color: #ef4444;">🌐 WEB</div>
                                        <div style="font-size: 24px; font-weight: bold; color: #ef4444;">11%</div>
                                        <div style="font-size: 12px; opacity: 0.8;">Net Conversion</div>
                                        <div style="font-size: 11px; margin-top: 8px; opacity: 0.7;">
                                            40% Set × 56% Show × 50% Complete
                                        </div>
                                    </div>
                                </div>
                                
                                <div style="background: rgba(255,255,255,0.15); padding: 16px; border-radius: 12px; margin: 16px 0;">
                                    <div style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">🎯 DEALER STRATEGY:</div>
                                    <div style="font-size: 13px; line-height: 1.4;">
                                        <strong>Use AI-generated insights to drive PHONE conversations</strong><br>
                                        • Email/SMS = Lead qualification<br>
                                        • Phone call = Revenue conversion<br>
                                        • Personal touch = Customer retention
                                    </div>
                                </div>
                                
                                <div style="text-align: center; margin-top: 16px;">
                                    <div style="background: rgba(96,165,250,0.2); padding: 12px; border-radius: 8px; display: inline-block;">
                                        <div style="font-size: 12px; opacity: 0.8;">Revenue Impact</div>
                                        <div style="font-size: 16px; font-weight: 600; color: #60a5fa;">
                                            +${(data.revenue_opportunity.total * 0.12).toLocaleString()} per phone lead
                                        </div>
                                    </div>
                                </div>
                                
                                <div style="text-align: center; margin-top: 20px;">
                                    <button onclick="generatePhoneScript('${data.vehicle_info.vin}')" style="background: linear-gradient(45deg, #22c55e, #16a34a); color: white; border: none; padding: 16px 32px; border-radius: 12px; font-weight: 600; font-size: 16px; cursor: pointer; box-shadow: 0 4px 12px rgba(34,197,94,0.3); transition: all 0.3s ease;">
                                        📞 GENERATE PHONE SCRIPT
                                    </button>
                                    <div style="font-size: 12px; opacity: 0.7; margin-top: 8px;">
                                        AI-powered conversation starter for this customer
                                    </div>
                                </div>
                            </div>
                            <div class="card-back">
                                <div class="card-title">📊 Conversion Science & Strategy</div>
                                <div class="math-content">
                                    <strong>Why Phone Converts 2.1x Better:</strong>
                                    <div class="math-formula">
                                        Human connection + Real-time objection handling + Trust building = Higher conversion
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>Phone vs Web Psychology:</strong><br>
                                        • Phone: Personal, immediate, trust-building<br>
                                        • Web: Impersonal, delayed, transactional<br>
                                        • Phone: Real-time problem solving<br>
                                        • Web: Self-service limitations
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>Dealer Communication Strategy:</strong><br>
                                        1. <strong>Email/SMS</strong>: "We noticed something about your ${data.vehicle_info.model}..."<br>
                                        2. <strong>Phone Call</strong>: "Let me explain what this means for you..."<br>
                                        3. <strong>Service Booking</strong>: "I can get you in this week..."<br>
                                        4. <strong>Follow-up</strong>: "How did that service work out?"
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>AI-Generated Phone Scripts:</strong><br>
                                        "Hi ${data.vehicle_info.model} owner, this is [Dealer] from [Location].<br>
                                        Our system flagged your vehicle for ${data.stressor_insights[0]?.component || 'preventive maintenance'}.<br>
                                        Based on ${data.cohort_comparison.sample_size.toLocaleString()} similar vehicles,<br>
                                        this creates a great opportunity to prevent future issues.<br>
                                        Can I schedule you for a quick inspection this week?"
                                    </div>
                                    <div style="margin: 12px 0;">
                                        <strong>Revenue Math:</strong><br>
                                        • Web lead: $${data.revenue_opportunity.total} × 11% = $${(data.revenue_opportunity.total * 0.11).toFixed(0)}<br>
                                        • Phone lead: $${data.revenue_opportunity.total} × 23% = $${(data.revenue_opportunity.total * 0.23).toFixed(0)}<br>
                                        • <strong>Difference: $${(data.revenue_opportunity.total * 0.12).toFixed(0)} per lead</strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            async function generateAIConversation(vin) {
                const aiConversationElement = document.getElementById('ai-conversation');
                const aiLoadingElement = document.getElementById('ai-loading');
                const generateBtn = document.getElementById('generate-ai-btn');
                
                try {
                    // Hide button and show loading
                    generateBtn.style.display = 'none';
                    aiLoadingElement.style.display = 'block';
                    
                    const response = await fetch('/generate-ai-conversation', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ vin: vin })
                    });
                    
                    const data = await response.json();
                    
                    // Hide loading and update with AI conversation
                    aiLoadingElement.style.display = 'none';
                    aiConversationElement.innerHTML = `"${data.ai_conversation}"`;
                    
                    // Show success indicator
                    aiLoadingElement.innerHTML = '✅ Personalized message generated!';
                    aiLoadingElement.style.display = 'block';
                    aiLoadingElement.style.color = '#22c55e';
                    setTimeout(() => {
                        aiLoadingElement.style.display = 'none';
                    }, 2000);
                    
                } catch (error) {
                    // Show error and restore button
                    aiLoadingElement.style.display = 'none';
                    generateBtn.style.display = 'block';
                    generateBtn.innerHTML = '⚠️ Try Again';
                    generateBtn.style.background = 'linear-gradient(45deg, #ef4444, #dc2626)';
                    console.log('AI conversation failed to load');
                }
            }
            
            async function generatePhoneScript(vin) {
                // Find the phone card and update its content
                const phoneCard = document.querySelector('.phone-card');
                if (phoneCard) {
                    const cardFront = phoneCard.querySelector('.card-front');
                    const button = cardFront.querySelector('button');
                    const originalText = button.innerHTML;
                    
                    // Show loading state
                    button.innerHTML = '🤖 Generating Phone Script...';
                    button.style.background = 'linear-gradient(45deg, #f59e0b, #d97706)';
                    button.disabled = true;
                    
                    try {
                        const response = await fetch('/generate-ai-conversation', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ vin: vin })
                        });
                        
                        const data = await response.json();
                        
                        // Create a new section to display the phone script
                        const scriptSection = document.createElement('div');
                        scriptSection.style.cssText = `
                            background: rgba(34,197,94,0.2); 
                            padding: 16px; 
                            border-radius: 12px; 
                            margin: 16px 0; 
                            border-left: 4px solid #22c55e;
                        `;
                        scriptSection.innerHTML = `
                            <div style="font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #22c55e;">📞 PHONE SCRIPT:</div>
                            <div style="font-size: 13px; line-height: 1.4; font-style: italic; color: white;">
                                "${data.ai_conversation}"
                            </div>
                        `;
                        
                        // Insert the script section before the button
                        button.parentNode.insertBefore(scriptSection, button);
                        
                        // Update button to success state
                        button.innerHTML = '✅ Phone Script Generated!';
                        button.style.background = 'linear-gradient(45deg, #22c55e, #16a34a)';
                        
                        setTimeout(() => {
                            button.innerHTML = originalText;
                            button.style.background = 'linear-gradient(45deg, #22c55e, #16a34a)';
                            button.disabled = false;
                        }, 3000);
                        
                    } catch (error) {
                        // Show error state
                        button.innerHTML = '⚠️ Try Again';
                        button.style.background = 'linear-gradient(45deg, #ef4444, #dc2626)';
                        setTimeout(() => {
                            button.innerHTML = originalText;
                            button.style.background = 'linear-gradient(45deg, #22c55e, #16a34a)';
                            button.disabled = false;
                        }, 2000);
                        console.log('Phone script generation failed');
                    }
                }
            }
            
            // Carousel Toggle Functionality
            let carouselVisible = true;
            
            function toggleCarousel() {
                const carousel = document.getElementById('leadCarousel');
                const toggleBtn = document.querySelector('.carousel-toggle');
                
                if (carouselVisible) {
                    carousel.style.transform = 'translateX(100%)';
                    carousel.style.opacity = '0';
                    toggleBtn.innerHTML = '📊 SHOW LEADS';
                    carouselVisible = false;
                } else {
                    carousel.style.transform = 'translateX(0)';
                    carousel.style.opacity = '1';
                    toggleBtn.innerHTML = '📊 LIVE LEADS';
                    carouselVisible = true;
                }
            }
            
            // Carousel stays visible by default
            // User can toggle manually with the red button
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
    
    # Calculate revenue opportunity based on realistic service costs and risk level
    def calculate_realistic_revenue(severity: str, model: str, risk_score: float) -> dict:
        """Calculate realistic revenue breakdown based on severity, model, and risk score"""
        
        # Base service costs (realistic Ford dealer pricing)
        base_costs = {
            "Critical": {"battery": 350, "service": 150, "diagnostic": 85},  # Immediate battery replacement
            "High": {"battery": 280, "service": 125, "diagnostic": 85},      # Preventive battery service
            "Moderate": {"battery": 0, "service": 85, "diagnostic": 85},     # Diagnostic + maintenance
            "Low": {"battery": 0, "service": 65, "diagnostic": 65}           # Basic inspection
        }
        
        # Get base costs for severity
        costs = base_costs.get(severity, base_costs["Moderate"])
        
        # Calculate components
        parts_cost = costs["battery"]
        service_cost = costs["service"] + costs["diagnostic"]
        
        # Apply model-specific multipliers
        if model in ["F-250", "F-350"]:
            parts_cost = int(parts_cost * 1.4)  # Heavy duty premium
            service_cost = int(service_cost * 1.4)
        elif model in ["F-150"]:
            parts_cost = int(parts_cost * 1.2)  # Light truck premium
            service_cost = int(service_cost * 1.2)
        elif model in ["Expedition"]:
            parts_cost = int(parts_cost * 1.1)  # SUV premium
            service_cost = int(service_cost * 1.1)
        
        # Risk-based adjustment (higher risk = higher urgency = higher revenue)
        risk_multiplier = 1.0 + (risk_score * 0.5)  # 0-50% additional for high risk
        parts_cost = int(parts_cost * risk_multiplier)
        service_cost = int(service_cost * risk_multiplier)
        
        total_cost = parts_cost + service_cost
        
        return {
            "parts": parts_cost,
            "service": service_cost,
            "total": total_cost
        }
    
    revenue_breakdown = calculate_realistic_revenue(severity, vehicle_data["model"], final_risk)
    total_revenue = revenue_breakdown["total"]
    
    # Generate cohort comparison data
    cohort_data = {
        "multiplier": cohort_multiplier,
        "percentile": random.randint(60, 95),
        "sample_size": random.randint(15000, 50000)
    }
    
    # Generate risk summary
    risk_data = {
        "score": final_risk,
        "severity": severity,
        "confidence": 0.89
    }
    
    # Generate personalized dealer conversation using OpenAI (async, non-blocking)
    # Start with fallback conversation for instant response
    fallback_conversation = generate_fallback_conversation(vehicle_data, risk_data, cohort_data)
    
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
        risk_summary=risk_data,
        stressor_insights=vehicle_data["stressor_flags"],
        stressor_analysis=vehicle_data["stressor_profile"],
        cohort_comparison=cohort_data,
        dealer_messaging={
            "message": dealer_messages[severity],
            "urgency": severity,
            "action": "Preventive Service Discussion" if severity in ["High", "Critical"] else "Maintenance Reinforcement"
        },
        revenue_opportunity={
            "service": revenue_breakdown["service"],
            "parts": revenue_breakdown["parts"], 
            "downtime_prevention": "TBD",
            "retention_value": "TBD",
            "total": total_revenue
        },
        dealer_conversation=fallback_conversation
    )

def generate_fallback_conversation(vehicle_data: Dict, risk_data: Dict, cohort_data: Dict) -> str:
    """Generate instant fallback conversation while OpenAI loads"""
    severity = risk_data['severity']
    model = vehicle_data['model']
    percentile = cohort_data['percentile']
    
    if severity == 'High':
        return f"Hi there! I noticed your {model} shows some unique behavioral patterns compared to similar vehicles. You're in the {percentile}th percentile of your cohort, which creates a great opportunity for preventive maintenance that could save you significant costs down the road. Can I schedule you for a quick inspection this week?"
    elif severity == 'Moderate':
        return f"Hello! Your {model} has some interesting usage patterns that put it in the {percentile}th percentile within its cohort. Let's chat about how we can optimize your vehicle's performance for your specific driving style. When would be a good time to bring it in?"
    else:
        return f"Great news about your {model}! Your driving patterns show excellent vehicle care. This is the perfect time to discuss our premium maintenance program. Can I get you scheduled for a service appointment?"

@app.post("/generate-ai-conversation")
async def generate_ai_conversation(vehicle: VehicleInput):
    """Generate OpenAI conversation asynchronously after initial load"""
    vin = vehicle.vin.upper().strip()
    
    if vin not in DEMO_VEHICLES:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicle_data = DEMO_VEHICLES[vin]
    
    # Recalculate the same risk data for consistency
    base_risk = INDUSTRY_PRIORS["battery_degradation"]["base_rate"]
    cohort_multiplier = INDUSTRY_PRIORS["battery_degradation"]["cohort_adjustments"].get(
        vehicle_data["cohort"], 1.0
    )
    
    stressor_impact = 1.0
    for stressor, value in vehicle_data["stressor_profile"].items():
        if stressor in INDUSTRY_PRIORS["battery_degradation"]["stressor_multipliers"]:
            multiplier = INDUSTRY_PRIORS["battery_degradation"]["stressor_multipliers"][stressor]
            stressor_impact *= (1 + (multiplier - 1) * value)
    
    final_risk = min(base_risk * cohort_multiplier * stressor_impact, 0.95)
    
    if final_risk < 0.3:
        severity = "Low"
    elif final_risk < 0.6:
        severity = "Moderate"
    elif final_risk < 0.8:
        severity = "High"
    else:
        severity = "Critical"
    
    risk_data = {"score": final_risk, "severity": severity, "confidence": 0.89}
    cohort_data = {"percentile": random.randint(60, 95), "sample_size": random.randint(15000, 50000)}
    
    # Generate the AI conversation
    ai_conversation = await generate_dealer_conversation(
        vehicle_data, 
        vehicle_data["stressor_profile"], 
        risk_data, 
        cohort_data
    )
    
    return {"ai_conversation": ai_conversation}

@app.get("/technical-walkthrough", response_class=HTMLResponse)
async def technical_walkthrough():
    """Technical mathematics walkthrough page"""
    try:
        with open("technical_math_walkthrough.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html><body>
        <h1>Technical Walkthrough Not Found</h1>
        <p>The technical walkthrough page is not available.</p>
        <a href="/">Return to Main Application</a>
        </body></html>
        """, status_code=404)

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

async def generate_dealer_conversation(vehicle_data: Dict, stressor_analysis: Dict, risk_summary: Dict, cohort_comparison: Dict) -> str:
    """Generate personalized dealer conversation using OpenAI"""
    try:
        # Check if API key is available
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            print("No OpenAI API key found, using fallback")
            raise Exception("No API key")
            
        # Create detailed prompt with stressor data
        stressor_details = []
        for stressor, value in stressor_analysis.items():
            if value > 0.4:  # Only include significant stressors
                stressor_name = stressor.replace('_', ' ').title()
                severity = "High" if value > 0.7 else "Moderate"
                stressor_details.append(f"{stressor_name}: {severity} ({value*100:.0f}%)")
        
        prompt = f"""
You are a Ford dealer service advisor. Generate a personalized, engaging conversation starter for a customer based on their vehicle's behavioral stressor analysis.

VEHICLE DETAILS:
- Vehicle: {vehicle_data['year']} {vehicle_data['model']} ({vehicle_data['engine']})
- Mileage: {vehicle_data['mileage']:,} miles
- Location: {vehicle_data['location']}
- Usage Pattern: {vehicle_data['usage_pattern']}
- Cohort: {vehicle_data['cohort']}

STRESSOR ANALYSIS:
- Risk Level: {risk_summary['severity']}
- Cohort Percentile: {cohort_comparison['percentile']}th out of {cohort_comparison['sample_size']:,} similar vehicles
- Key Stressors: {', '.join(stressor_details) if stressor_details else 'All within normal ranges'}

CONVERSATION REQUIREMENTS:
1. Be friendly and consultative, not pushy
2. Explain WHY their specific driving patterns matter
3. Reference their cohort position (outlier vs normal)
4. Connect stressors to real-world impacts they care about
5. Suggest specific, actionable next steps
6. Keep it conversational and under 150 words
7. **EMPHASIZE PHONE CONVERSATION** - this is for a phone call, not email/SMS
8. Include specific appointment scheduling language
9. Reference the 2.1x higher conversion rate of phone vs web leads

Generate a natural phone conversation starter that a dealer would actually say to this customer on the phone:
"""

        # Check if OpenAI client is available
        if not client:
            print("OpenAI client not available, using fallback")
            raise Exception("OpenAI client not initialized")

        print(f"Calling OpenAI with API key: {api_key[:10]}...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Ford dealer service advisor who creates personalized, data-driven customer conversations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        print("OpenAI response received successfully")
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"OpenAI error: {str(e)}")
        # Fallback to template-based message if OpenAI fails
        severity = risk_summary['severity']
        model = vehicle_data['model']
        
        if severity == 'High':
            return f"Hi there! I noticed your {model} shows some unique behavioral patterns compared to similar vehicles. Your driving style creates specific stressor combinations that we'd love to discuss - there's a great opportunity for preventive maintenance that could save you significant costs down the road."
        elif severity == 'Moderate':
            return f"Hello! Your {model} has some interesting usage patterns that put it in a unique position within its cohort. Let's chat about how we can optimize your vehicle's performance for your specific driving style."
        else:
            return f"Great news about your {model}! Your driving patterns show excellent vehicle care. This is the perfect time to discuss our premium maintenance program to keep you in the top tier of similar vehicles."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "start_render:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 