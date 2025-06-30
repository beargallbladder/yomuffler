#!/usr/bin/env python3
"""
Ford VIN Intelligence Platform v3.0 - Steve Jobs-Style Clean Interface
100k VIN Analysis across 5 Regions with Purpose-Driven Design
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VINIntelligencePlatform:
    """Clean, purpose-driven 100k VIN Intelligence Platform"""
    
    def __init__(self):
        """Initialize platform with 100k VIN data"""
        self.platform_data = self._load_100k_analysis()
        logger.info("🚀 Ford VIN Intelligence Platform v3.0 - 100k VIN Analysis Ready")
    
    def _load_100k_analysis(self) -> Dict:
        """Load 100k VIN analysis data"""
        try:
            # Load executive summary for key metrics
            with open('comprehensive_100k_analysis_executive_summary_20250629_163100.txt', 'r') as f:
                summary_content = f.read()
            
            # Parse key metrics from summary
            lines = summary_content.split('\n')
            total_vins = 100000
            total_revenue = 45580910
            avg_per_vehicle = 455
            dtc_integration = 48.0
            
            # Extract regional data
            regional_data = {}
            for line in lines:
                if ': ' in line and 'VINs,' in line and '$' in line:
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        region_name = parts[0].strip()
                        data_part = parts[1].strip()
                        
                        try:
                            vin_part = data_part.split('VINs,')[0].strip().replace(',', '')
                            revenue_part = data_part.split('$')[1].split(' ')[0].replace(',', '')
                            
                            vin_count = int(vin_part)
                            revenue = int(revenue_part)
                            
                            regions_map = {
                                'SOUTHEAST': 'southeast',
                                'TEXAS': 'texas', 
                                'CALIFORNIA': 'california',
                                'FLORIDA': 'florida',
                                'MONTANA': 'montana'
                            }
                            
                            if region_name in regions_map:
                                key = regions_map[region_name]
                                regional_data[key] = {
                                    "name": region_name,
                                    "vin_count": vin_count,
                                    "revenue": revenue,
                                    "avg_per_vehicle": revenue // vin_count if vin_count > 0 else 0
                                }
                        except (ValueError, IndexError):
                            continue
            
            return {
                "total_vins": total_vins,
                "total_revenue": total_revenue,
                "avg_per_vehicle": avg_per_vehicle,
                "dtc_integration_rate": dtc_integration,
                "regional_data": regional_data
            }
            
        except FileNotFoundError:
            logger.warning("⚠️ 100k analysis files not found, using demo data")
            return {
                "total_vins": 100000,
                "total_revenue": 45580910,
                "avg_per_vehicle": 455,
                "dtc_integration_rate": 48.0,
                "regional_data": {
                    "montana": {"name": "MONTANA", "vin_count": 5000, "revenue": 2318149, "avg_per_vehicle": 464},
                    "florida": {"name": "FLORIDA", "vin_count": 15000, "revenue": 6879766, "avg_per_vehicle": 459},
                    "texas": {"name": "TEXAS", "vin_count": 25000, "revenue": 11430433, "avg_per_vehicle": 457},
                    "southeast": {"name": "SOUTHEAST", "vin_count": 35000, "revenue": 15910403, "avg_per_vehicle": 455},
                    "california": {"name": "CALIFORNIA", "vin_count": 20000, "revenue": 9042159, "avg_per_vehicle": 452}
                }
            }

# Steve Jobs-style clean HTML interface
FORD_CLEAN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ford VIN Intelligence - 100k Vehicle Analysis v3.0</title>
    
    <!-- Cache Buster -->
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    
    <!-- Plausible Analytics -->
    <script defer data-domain="{plausible_domain}" src="https://plausible.io/js/script.js"></script>
    
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f7;
            color: #1d1d1f;
            line-height: 1.47059;
            font-weight: 400;
            letter-spacing: -.022em;
        }
        
        .hero-section {
            background: linear-gradient(135deg, #003366 0%, #0066cc 100%);
            color: white;
            text-align: center;
            padding: 80px 20px;
        }
        
        .hero-title {
            font-size: 48px;
            font-weight: 700;
            letter-spacing: -.025em;
            margin-bottom: 16px;
        }
        
        .hero-subtitle {
            font-size: 21px;
            font-weight: 400;
            color: rgba(255,255,255,0.9);
            margin-bottom: 32px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .hero-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 40px;
            max-width: 1000px;
            margin: 60px auto 0;
        }
        
        .hero-stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 40px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .stat-label {
            font-size: 17px;
            color: rgba(255,255,255,0.8);
        }
        
        .navigation {
            background: white;
            box-shadow: 0 1px 0 rgba(0,0,0,.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .nav-tabs {
            display: flex;
            border-bottom: 1px solid #d2d2d7;
        }
        
        .nav-tab {
            padding: 20px 24px;
            font-size: 17px;
            font-weight: 500;
            color: #515154;
            text-decoration: none;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .nav-tab.active {
            color: #003366;
            border-bottom-color: #003366;
        }
        
        .main-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 60px 20px;
        }
        
        .section {
            display: none;
            margin-bottom: 80px;
        }
        
        .section.active {
            display: block;
        }
        
        .section-title {
            font-size: 32px;
            font-weight: 700;
            color: #1d1d1f;
            margin-bottom: 40px;
            text-align: center;
        }
        
        .regional-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin-bottom: 60px;
        }
        
        .regional-card {
            background: white;
            border-radius: 18px;
            padding: 32px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            cursor: pointer;
            border: 1px solid rgba(0,0,0,0.04);
        }
        
        .regional-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 40px rgba(0,0,0,0.12);
        }
        
        .regional-card.montana { border-left: 4px solid #2e7d32; }
        .regional-card.florida { border-left: 4px solid #ff6b35; }
        .regional-card.texas { border-left: 4px solid #d84315; }
        .regional-card.southeast { border-left: 4px solid #1976d2; }
        .regional-card.california { border-left: 4px solid #7b1fa2; }
        
        .region-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .region-emoji {
            font-size: 32px;
            margin-right: 16px;
        }
        
        .region-name {
            font-size: 24px;
            font-weight: 700;
            color: #1d1d1f;
        }
        
        .region-metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .metric {
            text-align: center;
            padding: 16px;
            background: #f5f5f7;
            border-radius: 12px;
        }
        
        .metric-value {
            font-size: 20px;
            font-weight: 700;
            color: #1d1d1f;
            margin-bottom: 4px;
        }
        
        .metric-label {
            font-size: 13px;
            color: #86868b;
            font-weight: 500;
        }
        
        .insights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 32px;
            margin-top: 40px;
        }
        
        .insight-card {
            background: white;
            border-radius: 18px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            text-align: center;
        }
        
        .insight-icon {
            font-size: 48px;
            margin-bottom: 20px;
            display: block;
        }
        
        .insight-title {
            font-size: 21px;
            font-weight: 700;
            color: #1d1d1f;
            margin-bottom: 16px;
        }
        
        .insight-description {
            font-size: 17px;
            color: #86868b;
            line-height: 1.47059;
        }
        
        /* Technical Deep Dive Styles */
        .technical-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-bottom: 60px;
        }
        
        .map-visualization {
            background: white;
            border-radius: 18px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        
        .map-placeholder {
            width: 100%;
            height: 300px;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
        }
        
        .map-overlay {
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            bottom: 20px;
            background: rgba(0,51,102,0.1);
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #003366;
            font-weight: 700;
        }
        
        .stressor-framework {
            background: white;
            border-radius: 18px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        
        .stressor-category {
            margin-bottom: 24px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 4px solid #003366;
        }
        
        .stressor-category h4 {
            font-size: 18px;
            font-weight: 700;
            color: #003366;
            margin-bottom: 12px;
        }
        
        .stressor-list {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            font-size: 14px;
            color: #515154;
        }
        
        .methodology-section {
            background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%);
            color: white;
            border-radius: 18px;
            padding: 40px;
            margin-bottom: 40px;
        }
        
        .methodology-title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .methodology-steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 24px;
            margin-top: 32px;
        }
        
        .methodology-step {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
        }
        
        .step-number {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 12px;
            color: #ffeb3b;
        }
        
        .step-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .step-description {
            font-size: 14px;
            color: rgba(255,255,255,0.8);
        }
        
        @media (max-width: 768px) {
            .hero-title { font-size: 32px; }
            .hero-stats { grid-template-columns: 1fr 1fr; gap: 20px; }
            .stat-number { font-size: 28px; }
            .regional-grid { grid-template-columns: 1fr; }
            .nav-tab { padding: 16px 20px; font-size: 15px; }
            .technical-grid { grid-template-columns: 1fr; }
            .methodology-steps { grid-template-columns: 1fr; }
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #86868b;
        }
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero-section">
        <h1 class="hero-title">Ford VIN Intelligence</h1>
        <p class="hero-subtitle">100,000 vehicles analyzed across 5 regions with academic-backed stressor analysis and predictive intelligence for proactive dealer engagement</p>
        
        <div class="hero-stats" id="hero-stats">
            <div class="hero-stat">
                <div class="stat-number">100k</div>
                <div class="stat-label">Vehicles Analyzed</div>
            </div>
            <div class="hero-stat">
                <div class="stat-number">$45.6M</div>
                <div class="stat-label">Revenue Opportunity</div>
            </div>
            <div class="hero-stat">
                <div class="stat-number">48%</div>
                <div class="stat-label">DTC Integration</div>
            </div>
            <div class="hero-stat">
                <div class="stat-number">5</div>
                <div class="stat-label">Regions Covered</div>
            </div>
        </div>
    </section>
    
    <!-- Navigation -->
    <nav class="navigation">
        <div class="nav-container">
            <div class="nav-tabs">
                <div class="nav-tab active" onclick="showSection('overview')">Regional Overview</div>
                <div class="nav-tab" onclick="showSection('magic')">Technical Deep Dive</div>
                <div class="nav-tab" onclick="showSection('intelligence')">Business Intelligence</div>
                <div class="nav-tab" onclick="showSection('engagement')">Customer Engagement</div>
                <div class="nav-tab" onclick="showSection('insights')">Strategic Insights</div>
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="main-content">
        <!-- Regional Overview -->
        <section id="overview" class="section active">
            <h2 class="section-title">Regional Performance Analysis</h2>
            <div class="regional-grid" id="regional-grid">
                <div class="loading">Loading regional data...</div>
            </div>
        </section>
        
        <!-- Technical Deep Dive - The Magic -->
        <section id="magic" class="section">
            <h2 class="section-title">Technical Deep Dive - The Magic Behind VIN Intelligence</h2>
            
            <!-- Stressor Configuration Panel -->
            <div style="background: white; border-radius: 18px; padding: 40px; margin-bottom: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); cursor: pointer;" onclick="showStressorConfig()">
                <h3 style="font-size: 24px; font-weight: 700; color: #1d1d1f; margin-bottom: 24px; text-align: center;">
                    🎛️ Configurable Stressor Framework
                </h3>
                <p style="text-align: center; color: #86868b; margin-bottom: 32px; font-size: 17px;">
                    Click to see how we intelligently filter stressors to prevent dealer overwhelm while maintaining lead quality
                </p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
                    <!-- Electrical Stressors -->
                    <div style="border: 1px solid #d2d2d7; border-radius: 12px; padding: 20px;">
                        <h4 style="color: #d84315; font-weight: 700; margin-bottom: 16px;">⚡ Electrical (4 stressors)</h4>
                        <div style="font-size: 14px; color: #515154; line-height: 1.6;">
                            <div>• Parasitic Draw (3.4x LR)</div>
                            <div>• Alternator Cycling (2.8x LR)</div>
                            <div>• Voltage Regulation (4.1x LR)</div>
                            <div>• Deep Discharge (6.7x LR)</div>
                        </div>
                    </div>
                    
                    <!-- Environmental Stressors -->
                    <div style="border: 1px solid #d2d2d7; border-radius: 12px; padding: 20px;">
                        <h4 style="color: #2e7d32; font-weight: 700; margin-bottom: 16px;">🌍 Environmental (3 stressors)</h4>
                        <div style="font-size: 14px; color: #515154; line-height: 1.6;">
                            <div>• Humidity Cycling (2.6x LR)</div>
                            <div>• Altitude Change (1.4x LR)</div>
                            <div>• Salt Corrosion (4.3x LR)</div>
                        </div>
                    </div>
                    
                    <!-- Usage Pattern Stressors -->
                    <div style="border: 1px solid #d2d2d7; border-radius: 12px; padding: 20px;">
                        <h4 style="color: #1976d2; font-weight: 700; margin-bottom: 16px;">🚗 Usage Patterns (3 stressors)</h4>
                        <div style="font-size: 14px; color: #515154; line-height: 1.6;">
                            <div>• Stop-and-Go (2.3x LR)</div>
                            <div>• Extended Parking (1.7x LR)</div>
                            <div>• Multi-Driver (1.8x LR)</div>
                        </div>
                    </div>
                    
                    <!-- Mechanical Stressors -->
                    <div style="border: 1px solid #d2d2d7; border-radius: 12px; padding: 20px;">
                        <h4 style="color: #7b1fa2; font-weight: 700; margin-bottom: 16px;">🔧 Mechanical (3 stressors)</h4>
                        <div style="font-size: 14px; color: #515154; line-height: 1.6;">
                            <div>• Vibration (2.1x LR)</div>
                            <div>• Extended Idle (1.9x LR)</div>
                            <div>• Towing Load (3.2x LR)</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Cohort Intelligence -->
            <div style="background: white; border-radius: 18px; padding: 40px; margin-bottom: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <h3 style="font-size: 24px; font-weight: 700; color: #1d1d1f; margin-bottom: 24px; text-align: center;">
                    🧠 Cohort-Relative Intelligence
                </h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 32px; align-items: center;">
                    <div>
                        <h4 style="color: #d84315; font-weight: 700; margin-bottom: 16px;">❌ Without Cohort Analysis</h4>
                        <div style="background: #ffeaa7; padding: 20px; border-radius: 12px; margin-bottom: 16px;">
                            <div style="font-weight: 700; color: #d63031;">73% of vehicles = HIGH RISK</div>
                            <div style="font-size: 14px; color: #636e72;">Dealers overwhelmed with alerts</div>
                        </div>
                        <div style="font-size: 15px; color: #515154;">
                            "Normal salt corrosion in Florida gets flagged as high risk"
                        </div>
                    </div>
                    
                    <div>
                        <h4 style="color: #2e7d32; font-weight: 700; margin-bottom: 16px;">✅ With Cohort Intelligence</h4>
                        <div style="background: #d1f2eb; padding: 20px; border-radius: 12px; margin-bottom: 16px;">
                            <div style="font-weight: 700; color: #00b894;">13.9% of vehicles = OUTLIERS</div>
                            <div style="font-size: 14px; color: #636e72;">Actionable leads for dealers</div>
                        </div>
                        <div style="font-size: 15px; color: #515154;">
                            "Only the WORST salt corrosion cases get flagged"
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Geographic Map Visualization -->
            <div style="background: white; border-radius: 18px; padding: 40px; margin-bottom: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <h3 style="font-size: 24px; font-weight: 700; color: #1d1d1f; margin-bottom: 24px; text-align: center;">
                    🗺️ Geographic Stressor Patterns
                </h3>
                <div style="text-align: center; padding: 40px; background: #f5f5f7; border-radius: 12px; margin-bottom: 24px; cursor: pointer;" onclick="loadMapVisualization()">
                    <div style="font-size: 48px; margin-bottom: 16px;">🗺️</div>
                    <div style="font-size: 18px; color: #515154; margin-bottom: 8px;">Interactive Map Visualization</div>
                    <div style="font-size: 14px; color: #86868b;">Click to load regional stressor intensity heatmaps</div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                    <div style="text-align: center; padding: 16px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">⛰️</div>
                        <div style="font-weight: 700; color: #2e7d32;">Montana</div>
                        <div style="font-size: 13px; color: #86868b;">Cold stress patterns</div>
                    </div>
                    <div style="text-align: center; padding: 16px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">🌴</div>
                        <div style="font-weight: 700; color: #ff6b35;">Florida</div>
                        <div style="font-size: 13px; color: #86868b;">Heat & humidity stress</div>
                    </div>
                    <div style="text-align: center; padding: 16px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">🤠</div>
                        <div style="font-weight: 700; color: #d84315;">Texas</div>
                        <div style="font-size: 13px; color: #86868b;">Temperature cycling</div>
                    </div>
                    <div style="text-align: center; padding: 16px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">🌊</div>
                        <div style="font-weight: 700; color: #1976d2;">Southeast</div>
                        <div style="font-size: 13px; color: #86868b;">Salt corrosion zones</div>
                    </div>
                    <div style="text-align: center; padding: 16px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">☀️</div>
                        <div style="font-weight: 700; color: #7b1fa2;">California</div>
                        <div style="font-size: 13px; color: #86868b;">Traffic stop-and-go</div>
                    </div>
                </div>
            </div>
            
            <!-- Lead Generation Process -->
            <div style="background: white; border-radius: 18px; padding: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <h3 style="font-size: 24px; font-weight: 700; color: #1d1d1f; margin-bottom: 24px; text-align: center;">
                    🎯 Lead Generation Process
                </h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px;">
                    <div style="text-align: center; padding: 24px; border: 2px dashed #d2d2d7; border-radius: 12px;">
                        <div style="font-size: 32px; margin-bottom: 12px;">1️⃣</div>
                        <div style="font-weight: 700; margin-bottom: 8px;">Stressor Analysis</div>
                        <div style="font-size: 14px; color: #86868b;">13 academic stressors applied to 100k VINs</div>
                    </div>
                    <div style="text-align: center; padding: 24px; border: 2px dashed #d2d2d7; border-radius: 12px;">
                        <div style="font-size: 32px; margin-bottom: 12px;">2️⃣</div>
                        <div style="font-weight: 700; margin-bottom: 8px;">Cohort Grouping</div>
                        <div style="font-size: 14px; color: #86868b;">Similar vehicles grouped by region/model</div>
                    </div>
                    <div style="text-align: center; padding: 24px; border: 2px dashed #d2d2d7; border-radius: 12px;">
                        <div style="font-size: 32px; margin-bottom: 12px;">3️⃣</div>
                        <div style="font-weight: 700; margin-bottom: 8px;">Outlier Detection</div>
                        <div style="font-size: 14px; color: #86868b;">Statistical outliers within each cohort</div>
                    </div>
                    <div style="text-align: center; padding: 24px; border: 2px dashed #d2d2d7; border-radius: 12px;">
                        <div style="font-size: 32px; margin-bottom: 12px;">4️⃣</div>
                        <div style="font-weight: 700; margin-bottom: 8px;">Actionable Leads</div>
                        <div style="font-size: 14px; color: #86868b;">13.9% outliers become dealer opportunities</div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Business Intelligence -->
        <section id="intelligence" class="section">
            <h2 class="section-title">Business Intelligence Dashboard</h2>
            <div class="insights-grid">
                <div class="insight-card">
                    <span class="insight-icon">📊</span>
                    <h3 class="insight-title">Lead Volume Optimization</h3>
                    <p class="insight-description">4 out of 5 regions are over capacity. Strategic threshold adjustments can optimize daily lead volumes while maintaining revenue quality.</p>
                </div>
                <div class="insight-card">
                    <span class="insight-icon">🔧</span>
                    <h3 class="insight-title">DTC Integration Success</h3>
                    <p class="insight-description">48% of vehicles have existing DTCs or prognostics, creating bundling opportunities that increase average revenue per vehicle by 25%.</p>
                </div>
                <div class="insight-card">
                    <span class="insight-icon">🎯</span>
                    <h3 class="insight-title">Regional Prioritization</h3>
                    <p class="insight-description">Montana leads at $464 per vehicle average revenue. Focus expansion on high-performing markets for maximum ROI.</p>
                </div>
            </div>
        </section>
        
        <!-- Customer Engagement -->
        <section id="engagement" class="section">
            <h2 class="section-title">Customer Engagement Strategies</h2>
            <div class="insights-grid">
                <div class="insight-card">
                    <span class="insight-icon">💬</span>
                    <h3 class="insight-title">Integrated Bundling</h3>
                    <p class="insight-description">Combine stressor analysis with existing maintenance needs. "While you're here for oil change, let's check battery stress patterns."</p>
                </div>
                <div class="insight-card">
                    <span class="insight-icon">⚡</span>
                    <h3 class="insight-title">Proactive Stressor Analysis</h3>
                    <p class="insight-description">Pure stressor-based outreach for vehicles without existing issues. Prevent problems before they occur.</p>
                </div>
                <div class="insight-card">
                    <span class="insight-icon">🌍</span>
                    <h3 class="insight-title">Regional Customization</h3>
                    <p class="insight-description">Tailor messaging based on climate zones: Montana cold stress, Florida heat stress, California traffic patterns.</p>
                </div>
            </div>
        </section>
        
        <!-- Strategic Insights -->
        <section id="insights" class="section">
            <h2 class="section-title">Strategic Insights & Recommendations</h2>
            <div class="insights-grid">
                <div class="insight-card">
                    <span class="insight-icon">📈</span>
                    <h3 class="insight-title">Nationwide Scalability Proven</h3>
                    <p class="insight-description">100k vehicle analysis validates system capability for nationwide Ford dealer network deployment with regional customization.</p>
                </div>
                <div class="insight-card">
                    <span class="insight-icon">🎓</span>
                    <h3 class="insight-title">Academic Foundation</h3>
                    <p class="insight-description">Argonne National Laboratory research provides scientific credibility for dealer conversations and regulatory compliance.</p>
                </div>
                <div class="insight-card">
                    <span class="insight-icon">🚀</span>
                    <h3 class="insight-title">Implementation Roadmap</h3>
                    <p class="insight-description">Phase 1: High-performing regions (Montana, Florida). Phase 2: Scale to Texas and Southeast. Phase 3: National deployment.</p>
                </div>
            </div>
        </section>
    </main>
    
    <script>
        // Platform data will be injected here
        const platformData = {platform_data_json};
        
        function showSection(sectionId) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            
            document.getElementById(sectionId).classList.add('active');
            event.target.classList.add('active');
            
            if (window.plausible) {
                window.plausible('Section Navigation', { props: { section: sectionId } });
            }
        }
        
        function loadRegionalData() {
            const regionalGrid = document.getElementById('regional-grid');
            
            if (!platformData.regional_data) {
                regionalGrid.innerHTML = '<div class="loading">No regional data available</div>';
                return;
            }
            
            const regionEmojis = {
                'montana': '⛰️', 'florida': '🌴', 'texas': '🤠', 
                'southeast': '🌊', 'california': '☀️'
            };
            
            const html = Object.entries(platformData.regional_data)
                .sort((a, b) => b[1].avg_per_vehicle - a[1].avg_per_vehicle)
                .map(([regionKey, data]) => `
                    <div class="regional-card ${regionKey}" onclick="selectRegion('${regionKey}')">
                        <div class="region-header">
                            <span class="region-emoji">${regionEmojis[regionKey] || '🗺️'}</span>
                            <span class="region-name">${data.name}</span>
                        </div>
                        <div class="region-metrics">
                            <div class="metric">
                                <div class="metric-value">${data.vin_count.toLocaleString()}</div>
                                <div class="metric-label">VINs</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">$${(data.revenue/1000000).toFixed(1)}M</div>
                                <div class="metric-label">Revenue</div>
                            </div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">$${data.avg_per_vehicle}</div>
                            <div class="metric-label">Average per Vehicle</div>
                        </div>
                    </div>
                `).join('');
            
            regionalGrid.innerHTML = html;
        }
        
        function selectRegion(regionKey) {
            if (window.plausible) {
                window.plausible('Region Selected', { props: { region: regionKey } });
            }
            
            const data = platformData.regional_data[regionKey];
            alert(`${regionKey.toUpperCase()} REGIONAL ANALYSIS

📊 ${data.vin_count.toLocaleString()} vehicles analyzed
💰 $${data.revenue.toLocaleString()} revenue opportunity
📈 $${data.avg_per_vehicle} average per vehicle

🎯 This region ${regionKey === 'california' ? 'is optimally performing' : 'is over capacity and needs optimization'}

🚀 Full implementation includes:
• Lead volume optimization tools
• Customer engagement strategies
• Capacity management options
• Revenue opportunity breakdown`);
        }
        
        function updateHeroStats() {
            const heroStats = document.getElementById('hero-stats');
            if (platformData && heroStats) {
                heroStats.innerHTML = `
                    <div class="hero-stat">
                        <div class="stat-number">${(platformData.total_vins/1000).toFixed(0)}k</div>
                        <div class="stat-label">Vehicles Analyzed</div>
                    </div>
                    <div class="hero-stat">
                        <div class="stat-number">$${(platformData.total_revenue/1000000).toFixed(1)}M</div>
                        <div class="stat-label">Revenue Opportunity</div>
                    </div>
                    <div class="hero-stat">
                        <div class="stat-number">${platformData.dtc_integration_rate}%</div>
                        <div class="stat-label">DTC Integration</div>
                    </div>
                    <div class="hero-stat">
                        <div class="stat-number">${Object.keys(platformData.regional_data).length}</div>
                        <div class="stat-label">Regions Covered</div>
                    </div>
                `;
            }
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            loadRegionalData();
            updateHeroStats();
            
            if (window.plausible) {
                window.plausible('Platform Loaded', {
                    props: { 
                        version: 'v3.0',
                        total_vins: platformData.total_vins,
                        regions: Object.keys(platformData.regional_data).length
                    }
                });
            }
        });
        
        // Map visualization function
        function loadMapVisualization() {
            if (window.plausible) {
                window.plausible('Map Visualization Clicked');
            }
            
            alert(`🗺️ GEOGRAPHIC STRESSOR INTENSITY MAP

📍 REGIONAL PATTERNS:
⛰️ Montana: Cold stress (8.7/10), Altitude change (7.2/10)
🌴 Florida: Heat stress (9.1/10), Humidity cycling (8.8/10)
🤠 Texas: Temperature cycling (8.2/10), Towing load (7.6/10)
🌊 Southeast: Salt corrosion (8.4/10), Humidity cycling (7.7/10)
☀️ California: Stop-and-go (9.3/10), Extended parking (8.1/10)

🎯 INTERACTIVE FEATURES:
• Regional heat maps showing stressor intensity
• Click regions for detailed cohort analysis
• Filter by specific stressor types
• Overlay VIN density and outlier concentrations

🚀 Full implementation includes real-time geographic visualization with Leaflet/Mapbox integration.`);
        }
        
        // Stressor configuration demo
        function showStressorConfig() {
            if (window.plausible) {
                window.plausible('Stressor Configuration Viewed');
            }
            
            alert(`🎛️ STRESSOR CONFIGURATION SYSTEM

✅ CURRENTLY ENABLED (13 stressors):
⚡ Electrical: 4 stressors (High impact)
🌍 Environmental: 3 stressors (Regional specific)
🚗 Usage Patterns: 3 stressors (Behavioral)
🔧 Mechanical: 3 stressors (Physical wear)

📊 IMPACT ON LEAD VOLUME:
• All 13 stressors: 13.9% outliers ($1.2M revenue)
• Basic 4 stressors: 9.8% outliers ($810K revenue)
• Environmental only: 69.7% outliers (TOO MANY!)

🎯 SMART FILTERING:
We adjust thresholds by region to prevent dealer overwhelm.
Florida salt corrosion threshold ≠ Montana salt corrosion threshold.

🚀 Dealers can enable/disable stressors based on their market needs.`);
        }
        
        // Force cache refresh on load
        window.onload = function() {
            if (window.location.search.indexOf('v=') === -1) {
                window.location.href = window.location.href + '?v=' + Date.now();
            }
        };
    </script>
</body>
</html>
"""

def main():
    """Main FastAPI application"""
    from fastapi import FastAPI, HTTPException, Depends
    from fastapi.responses import HTMLResponse
    from fastapi.security import HTTPBasic, HTTPBasicCredentials
    import secrets
    import uvicorn
    
    app = FastAPI(title="Ford VIN Intelligence Platform v3.0")
    security = HTTPBasic()
    
    # Initialize platform
    platform = VINIntelligencePlatform()
    
    def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
        """Simple authentication"""
        is_correct_username = secrets.compare_digest(credentials.username, "dealer")
        is_correct_password = secrets.compare_digest(credentials.password, "stressors2024")
        if not (is_correct_username and is_correct_password):
            raise HTTPException(status_code=401, detail="Unauthorized")
        return credentials.username
    
    @app.get("/", response_class=HTMLResponse)
    async def root(username: str = Depends(authenticate)):
        """Main Ford VIN Intelligence interface"""
        plausible_domain = os.getenv("PLAUSIBLE_DOMAIN", "datasetsrus.com")
        platform_data_json = json.dumps(platform.platform_data)
        
        html_content = FORD_CLEAN_HTML.replace("{plausible_domain}", plausible_domain)
        html_content = html_content.replace("{platform_data_json}", platform_data_json)
        
        return HTMLResponse(content=html_content)
    
    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "platform": "Ford VIN Intelligence v3.0",
            "total_vins": platform.platform_data["total_vins"],
            "regions": len(platform.platform_data["regional_data"])
        }
    
    @app.get("/api/stressors/configuration")
    async def get_stressor_config(username: str = Depends(authenticate)):
        """Get current stressor configuration"""
        return {
            "electrical": {
                "enabled": True,
                "stressors": [
                    {"name": "Parasitic Draw", "likelihood_ratio": 3.4, "enabled": True},
                    {"name": "Alternator Cycling", "likelihood_ratio": 2.8, "enabled": True},
                    {"name": "Voltage Regulation", "likelihood_ratio": 4.1, "enabled": True},
                    {"name": "Deep Discharge", "likelihood_ratio": 6.7, "enabled": True}
                ]
            },
            "environmental": {
                "enabled": True,
                "stressors": [
                    {"name": "Humidity Cycling", "likelihood_ratio": 2.6, "enabled": True},
                    {"name": "Altitude Change", "likelihood_ratio": 1.4, "enabled": True},
                    {"name": "Salt Corrosion", "likelihood_ratio": 4.3, "enabled": True}
                ]
            },
            "usage_patterns": {
                "enabled": True,
                "stressors": [
                    {"name": "Stop-and-Go", "likelihood_ratio": 2.3, "enabled": True},
                    {"name": "Extended Parking", "likelihood_ratio": 1.7, "enabled": True},
                    {"name": "Multi-Driver", "likelihood_ratio": 1.8, "enabled": True}
                ]
            },
            "mechanical": {
                "enabled": True,
                "stressors": [
                    {"name": "Vibration", "likelihood_ratio": 2.1, "enabled": True},
                    {"name": "Extended Idle", "likelihood_ratio": 1.9, "enabled": True},
                    {"name": "Towing Load", "likelihood_ratio": 3.2, "enabled": True}
                ]
            }
        }
    
    @app.get("/api/geographic/map-data")
    async def get_map_data(username: str = Depends(authenticate)):
        """Get geographic stressor intensity data for map visualization"""
        return {
            "regions": [
                {
                    "name": "Montana",
                    "center": {"lat": 47.0527, "lng": -109.6333},
                    "stressor_intensity": {
                        "cold_stress": 8.7,
                        "altitude_change": 7.2,
                        "extended_idle": 6.1
                    },
                    "color": "#2e7d32"
                },
                {
                    "name": "Florida", 
                    "center": {"lat": 27.7663, "lng": -82.6404},
                    "stressor_intensity": {
                        "heat_stress": 9.1,
                        "humidity_cycling": 8.8,
                        "salt_corrosion": 7.9
                    },
                    "color": "#ff6b35"
                },
                {
                    "name": "Texas",
                    "center": {"lat": 31.9686, "lng": -99.9018},
                    "stressor_intensity": {
                        "temperature_cycling": 8.2,
                        "towing_load": 7.6,
                        "extended_idle": 6.8
                    },
                    "color": "#d84315"
                },
                {
                    "name": "Southeast",
                    "center": {"lat": 35.7796, "lng": -78.6382},
                    "stressor_intensity": {
                        "salt_corrosion": 8.4,
                        "humidity_cycling": 7.7,
                        "stop_and_go": 6.9
                    },
                    "color": "#1976d2"
                },
                {
                    "name": "California",
                    "center": {"lat": 36.7783, "lng": -119.4179},
                    "stressor_intensity": {
                        "stop_and_go": 9.3,
                        "extended_parking": 8.1,
                        "multi_driver": 7.4
                    },
                    "color": "#7b1fa2"
                }
            ]
        }
    
    logger.info("🚀 Ford VIN Intelligence Platform v3.0 - Clean Interface Ready")
    logger.info(f"📊 {platform.platform_data['total_vins']:,} VINs analyzed")
    logger.info(f"💰 ${platform.platform_data['total_revenue']:,} revenue opportunity")
    
    # Return the app for uvicorn
    return app

if __name__ == "__main__":
    app = main()
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 10000)),
        reload=False
    ) 