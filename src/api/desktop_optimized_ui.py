"""
Desktop-Optimized VIN Stressors UI
Responsive design that adapts from mobile-first to desktop-optimized layouts
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

def get_desktop_optimized_ui():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIN Stressors - Universal Vehicle Intelligence Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* RESPONSIVE CONTAINER SYSTEM */
        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: 16px;
            flex: 1;
        }
        
        /* Desktop: Up to 1400px width with proper spacing */
        @media (min-width: 768px) {
            .container {
                max-width: 1400px;
                padding: 24px;
            }
        }
        
        @media (min-width: 1200px) {
            .container {
                padding: 32px;
            }
        }
        
        /* HEADER - Responsive */
        .header {
            text-align: center;
            margin-bottom: 24px;
        }
        
        @media (min-width: 768px) {
            .header {
                margin-bottom: 32px;
            }
        }
        
        .logo {
            font-size: 28px;
            font-weight: 800;
            color: white;
            margin-bottom: 8px;
        }
        
        @media (min-width: 768px) {
            .logo {
                font-size: 36px;
                margin-bottom: 12px;
            }
        }
        
        .subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 14px;
            font-weight: 500;
        }
        
        @media (min-width: 768px) {
            .subtitle {
                font-size: 16px;
            }
        }
        
        /* TAB NAVIGATION - Desktop Optimized */
        .tab-nav {
            display: flex;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 4px;
            margin-bottom: 24px;
            backdrop-filter: blur(10px);
        }
        
        @media (min-width: 768px) {
            .tab-nav {
                max-width: 600px;
                margin: 0 auto 32px auto;
                padding: 6px;
            }
        }
        
        .tab-btn {
            flex: 1;
            padding: 12px 16px;
            background: transparent;
            color: rgba(255,255,255,0.7);
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }
        
        @media (min-width: 768px) {
            .tab-btn {
                padding: 14px 24px;
                font-size: 15px;
            }
        }
        
        .tab-btn.active {
            background: white;
            color: #2a5298;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        
        /* CARD SYSTEM - Responsive */
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            backdrop-filter: blur(10px);
            margin-bottom: 20px;
        }
        
        @media (min-width: 768px) {
            .card {
                padding: 32px;
                margin-bottom: 24px;
            }
        }
        
        /* LEARNING TAB - Desktop Grid Optimization */
        .learning-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
        }
        
        /* Tablet: 2 columns */
        @media (min-width: 768px) {
            .learning-grid {
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
        }
        
        /* Desktop: 4 columns for better space usage */
        @media (min-width: 1200px) {
            .learning-grid {
                grid-template-columns: repeat(4, 1fr);
                gap: 24px;
            }
        }
        
        /* RISK SCORE TAB - Side-by-side Layout */
        .risk-layout {
            display: grid;
            grid-template-columns: 1fr;
            gap: 24px;
        }
        
        @media (min-width: 968px) {
            .risk-layout {
                grid-template-columns: 400px 1fr;
                gap: 32px;
            }
        }
        
        @media (min-width: 1200px) {
            .risk-layout {
                grid-template-columns: 450px 1fr;
                gap: 40px;
            }
        }
        
        .risk-input-panel {
            /* Left panel for input */
        }
        
        .risk-results-panel {
            /* Right panel for results */
            display: grid;
            gap: 20px;
        }
        
        /* DEALER PORTAL - Dashboard Layout */
        .dealer-dashboard {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }
        
        @media (min-width: 768px) {
            .dealer-dashboard {
                grid-template-columns: 300px 1fr;
                gap: 24px;
            }
        }
        
        @media (min-width: 1200px) {
            .dealer-dashboard {
                grid-template-columns: 350px 1fr 300px;
                gap: 32px;
            }
        }
        
        .dealer-sidebar {
            /* Left sidebar with summary stats */
        }
        
        .dealer-main {
            /* Main content area with leads */
        }
        
        .dealer-actions {
            /* Right sidebar with actions (desktop only) */
            display: none;
        }
        
        @media (min-width: 1200px) {
            .dealer-actions {
                display: block;
            }
        }
        
        /* LEADS GRID - Responsive */
        .leads-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
        }
        
        @media (min-width: 768px) {
            .leads-grid {
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
        }
        
        @media (min-width: 1200px) {
            .leads-grid {
                grid-template-columns: 1fr 1fr 1fr;
                gap: 24px;
            }
        }
        
        /* STATISTICS CARDS */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        @media (min-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin-bottom: 24px;
            }
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px;
            border-radius: 12px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 12px;
            opacity: 0.9;
        }
        
        /* DESKTOP CONTROLS */
        .desktop-controls {
            display: none;
        }
        
        @media (min-width: 768px) {
            .desktop-controls {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 24px;
                gap: 16px;
            }
        }
        
        .control-group {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .filter-btn, .sort-btn, .export-btn {
            padding: 8px 16px;
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .filter-btn:hover, .sort-btn:hover, .export-btn:hover {
            background: rgba(255,255,255,0.3);
        }
        
        /* FORMS - Better Desktop Layout */
        .form-row {
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
        }
        
        @media (min-width: 768px) {
            .form-row {
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
        }
        
        @media (min-width: 1200px) {
            .form-row {
                grid-template-columns: 2fr 1fr 120px;
                gap: 24px;
                align-items: end;
            }
        }
        
        /* RESULT PANELS - Side by Side */
        .results-layout {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }
        
        @media (min-width: 968px) {
            .results-layout {
                grid-template-columns: 350px 1fr;
                gap: 24px;
            }
        }
        
        .result-summary {
            /* Left: Risk score and key metrics */
        }
        
        .result-details {
            /* Right: Detailed breakdown and recommendations */
        }
        
        /* MOBILE OVERRIDES */
        @media (max-width: 767px) {
            .desktop-only {
                display: none !important;
            }
            
            .mobile-stack > * {
                margin-bottom: 16px;
            }
        }
        
        /* All existing mobile styles preserved... */
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .learning-card {
            perspective: 1000px;
            height: 200px;
            cursor: pointer;
            position: relative;
        }
        
        @media (min-width: 1200px) {
            .learning-card {
                height: 180px; /* Slightly shorter on desktop for better grid */
            }
        }
        
        .card-inner {
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
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
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .card-front {
            background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
            color: white;
        }
        
        .card-back {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            transform: rotateY(180deg);
        }
        
        .flip-indicator {
            position: absolute;
            top: 8px;
            right: 12px;
            font-size: 10px;
            opacity: 0.7;
            font-weight: 600;
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 12px;
        }
        
        @media (min-width: 1200px) {
            .card-title {
                font-size: 14px; /* Smaller on desktop grid */
                margin-bottom: 8px;
            }
        }
        
        .math-content {
            text-align: left;
        }
        
        .math-formula {
            background: rgba(255,255,255,0.1);
            padding: 8px;
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 11px;
            line-height: 1.3;
        }
        
        @media (min-width: 1200px) {
            .math-formula {
                font-size: 10px;
                padding: 6px;
            }
        }
        
        /* Form Elements */
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
        
        @media (min-width: 768px) {
            .btn {
                width: auto;
                min-width: 200px;
            }
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        /* Existing mobile styles for compatibility... */
        .dealer-header {
            background: rgba(34,197,94,0.1);
            border: 1px solid rgba(34,197,94,0.3);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .lead-card {
            background: white;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 4px solid #2a5298;
        }
        
        .lead-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        
        .customer-name {
            font-size: 16px;
            font-weight: 700;
            color: #1f2937;
        }
        
        .priority-badge {
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .priority-critical { background: #fee2e2; color: #991b1b; }
        .priority-high { background: #fef3c7; color: #92400e; }
        .priority-medium { background: #dbeafe; color: #1e40af; }
        
        .talking-points {
            background: #f8fafc;
            border-radius: 8px;
            padding: 12px;
            margin-top: 8px;
        }
        
        .revenue-estimate {
            background: rgba(34,197,94,0.1);
            color: #059669;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            text-align: center;
            margin-top: 8px;
        }
        
        /* Demo VINs Grid */
        .demo-vins {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 16px;
        }
        
        @media (min-width: 768px) {
            .demo-vins {
                grid-template-columns: repeat(4, 1fr);
                gap: 12px;
            }
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
        
        /* Risk Score Display */
        .risk-score {
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        
        @media (min-width: 768px) {
            .risk-score {
                font-size: 48px;
            }
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
        
        /* Loading and Error States */
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
        
        .footer {
            margin-top: auto;
            text-align: center;
            color: white;
            opacity: 0.8;
            font-size: 12px;
            padding: 20px 0;
        }
        
        /* Hide elements appropriately */
        .result-card {
            display: none;
        }
        
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🚗 VIN Stressors</div>
            <div class="subtitle">Universal Vehicle Intelligence Platform</div>
        </div>
        
        <!-- Tab Navigation -->
        <div class="tab-nav">
            <button class="tab-btn active" onclick="switchTab('learning')">Intelligence</button>
            <button class="tab-btn" onclick="switchTab('risk')">Risk Score</button>
            <button class="tab-btn" onclick="switchTab('dealer')">Dealer Portal</button>
        </div>
        
        <!-- Desktop Controls (hidden on mobile) -->
        <div class="desktop-controls">
            <div class="control-group">
                <button class="filter-btn">🔍 Filter</button>
                <button class="sort-btn">📊 Sort</button>
            </div>
            <div class="control-group">
                <button class="export-btn">📤 Export</button>
            </div>
        </div>
        
        <!-- Intelligence Tab (formerly Learning) -->
        <div id="learning-tab" class="tab-content active">
            <!-- Stats Overview (Desktop) -->
            <div class="stats-grid desktop-only">
                <div class="stat-card">
                    <div class="stat-value">5,247</div>
                    <div class="stat-label">Leads Generated</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$2.1M</div>
                    <div class="stat-label">Revenue Pipeline</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">78%</div>
                    <div class="stat-label">Accuracy Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">4.2x</div>
                    <div class="stat-label">ROI Multiplier</div>
                </div>
            </div>
            
            <!-- Academic Foundation Cards -->
            <div class="learning-grid">
                <div class="learning-card" onclick="flipCard(this)">
                    <div class="flip-indicator">TAP TO FLIP</div>
                    <div class="card-inner">
                        <div class="card-front">
                            <div class="card-title">Academic Foundation</div>
                            <p style="color: rgba(255,255,255,0.9); font-size: 14px; line-height: 1.5;">
                                Powered by <strong>Argonne National Laboratory</strong> research, Battery University studies, 
                                and SAE standards for scientifically-validated risk assessment.
                            </p>
                        </div>
                        <div class="card-back">
                            <div class="math-content">
                                <div class="card-title">Research Sources</div>
                                <div class="math-formula">
                                    <strong>Argonne ANL-115925.pdf:</strong><br/>
                                    6-mile recharge rule validation
                                </div>
                                <div class="math-formula">
                                    <strong>Battery University:</strong><br/>
                                    BU-804 Heat stress analysis<br/>
                                    BU-403 Duty cycle research
                                </div>
                                <div class="math-formula">
                                    <strong>SAE Standards:</strong><br/>
                                    J2334 Corrosion studies<br/>
                                    J537 Cold start analysis
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="learning-card" onclick="flipCard(this)">
                    <div class="flip-indicator">TAP TO FLIP</div>
                    <div class="card-inner">
                        <div class="card-front">
                            <div class="card-title">Bayesian Mathematics</div>
                            <p style="color: rgba(255,255,255,0.9); font-size: 14px; line-height: 1.5;">
                                Advanced <strong>Bayesian inference</strong> updates base probabilities with real-world 
                                evidence for mathematically sound predictions.
                            </p>
                        </div>
                        <div class="card-back">
                            <div class="math-content">
                                <div class="card-title">Core Formula</div>
                                <div class="math-formula">
                                    <strong>P(Failure|Evidence) =</strong><br/>
                                    Prior × LR / (Prior × LR + (1-Prior))
                                </div>
                                <div class="math-formula">
                                    <strong>Example:</strong><br/>
                                    Prior: 15% (light truck)<br/>
                                    LR: 8.74 (3 stressors)<br/>
                                    Result: 61.2% failure risk
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="learning-card" onclick="flipCard(this)">
                    <div class="flip-indicator">TAP TO FLIP</div>
                    <div class="card-inner">
                        <div class="card-front">
                            <div class="card-title">Universal Compatibility</div>
                            <p style="color: rgba(255,255,255,0.9); font-size: 14px; line-height: 1.5;">
                                Works with <strong>any vehicle make/model</strong> using VIN-based cohort matching. 
                                No telemetry required.
                            </p>
                        </div>
                        <div class="card-back">
                            <div class="math-content">
                                <div class="card-title">VIN Intelligence</div>
                                <div class="math-formula">
                                    <strong>Instant Classification:</strong><br/>
                                    VIN → Vehicle class + Region<br/>
                                    → Academic prior + Stressors<br/>
                                    → Risk assessment
                                </div>
                                <div class="math-formula">
                                    <strong>Data Independence:</strong><br/>
                                    ✅ No OBD-II required<br/>
                                    ✅ Works offline<br/>
                                    ✅ Real-time results
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="learning-card" onclick="flipCard(this)">
                    <div class="flip-indicator">TAP TO FLIP</div>
                    <div class="card-inner">
                        <div class="card-front">
                            <div class="card-title">Business Intelligence</div>
                            <p style="color: rgba(255,255,255,0.9); font-size: 14px; line-height: 1.5;">
                                Transforms academic risk into <strong>actionable business insights</strong> with revenue 
                                calculations and priority scoring.
                            </p>
                        </div>
                        <div class="card-back">
                            <div class="math-content">
                                <div class="card-title">ROI Optimization</div>
                                <div class="math-formula">
                                    <strong>Revenue Calculation:</strong><br/>
                                    Risk level → Service type<br/>
                                    → Parts + Labor pricing<br/>
                                    → Total opportunity
                                </div>
                                <div class="math-formula">
                                    <strong>Priority Scoring:</strong><br/>
                                    Failure probability<br/>
                                    × Revenue potential<br/>
                                    × Contact timing
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Risk Score Tab -->
        <div id="risk-tab" class="tab-content">
            <div class="risk-layout">
                <!-- Input Panel (Left on Desktop) -->
                <div class="risk-input-panel">
                    <div class="card">
                        <h3 style="margin-bottom: 20px; color: #1f2937;">Vehicle Risk Assessment</h3>
                        <form id="riskForm">
                            <div class="form-group">
                                <label for="vin">Vehicle Identification Number (VIN)</label>
                                <input type="text" id="vin" name="vin" placeholder="Enter 17-character VIN" maxlength="17" required>
                            </div>
                            
                            <button type="submit" class="btn" id="submitBtn">
                                Calculate Risk Score
                            </button>
                        </form>
                        
                        <div class="demo-vins">
                            <div class="demo-vin" onclick="setDemoVin('1FORD00000000001')">Demo 1</div>
                            <div class="demo-vin" onclick="setDemoVin('1FORD00000000002')">Demo 2</div>
                            <div class="demo-vin" onclick="setDemoVin('1FORD00000000003')">Demo 3</div>
                            <div class="demo-vin" onclick="setDemoVin('1FORD00000000004')">Demo 4</div>
                        </div>
                    </div>
                </div>
                
                <!-- Results Panel (Right on Desktop) -->
                <div class="risk-results-panel">
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <div>Calculating risk score...</div>
                    </div>
                    
                    <div class="error" id="error"></div>
                    
                    <div class="results-layout">
                        <!-- Risk Summary -->
                        <div class="result-summary">
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
                                    <span class="detail-label">Revenue Opportunity</span>
                                    <span class="detail-value" id="revenue">-</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Detailed Analysis -->
                        <div class="result-details">
                            <div class="card result-card" id="detailedResult" style="display: none;">
                                <h4 style="margin-bottom: 16px; color: #1f2937;">Detailed Analysis</h4>
                                <div id="recommendedAction" class="detail-row">
                                    <span class="detail-label">Recommended Action</span>
                                    <span class="detail-value">-</span>
                                </div>
                                <div id="academicSources" style="margin-top: 16px;">
                                    <h5 style="color: #6b7280; margin-bottom: 8px;">Academic Sources</h5>
                                    <div style="font-size: 12px; color: #9ca3af; line-height: 1.4;">
                                        Calculations based on peer-reviewed research
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Dealer Portal Tab -->
        <div id="dealer-tab" class="tab-content">
            <div class="dealer-dashboard">
                <!-- Sidebar (Desktop) -->
                <div class="dealer-sidebar">
                    <div class="card">
                        <div class="dealer-header">
                            <div class="dealer-title">Dealer Portal</div>
                            <div class="dealer-subtitle">High-Priority Vehicle Leads</div>
                        </div>
                        
                        <!-- Quick Stats -->
                        <div style="margin-bottom: 20px;">
                            <div class="detail-row">
                                <span class="detail-label">Total Leads</span>
                                <span class="detail-value">247</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Critical Priority</span>
                                <span class="detail-value" style="color: #dc2626;">23</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Revenue Pipeline</span>
                                <span class="detail-value" style="color: #059669;">$89,320</span>
                            </div>
                        </div>
                        
                        <!-- Filters (Desktop) -->
                        <div class="desktop-only">
                            <h5 style="margin-bottom: 12px; color: #6b7280;">Filter Leads</h5>
                            <div style="margin-bottom: 12px;">
                                <select style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #d1d5db;">
                                    <option>All Priorities</option>
                                    <option>Critical Only</option>
                                    <option>High Priority</option>
                                </select>
                            </div>
                            <div>
                                <select style="width: 100%; padding: 8px; border-radius: 6px; border: 1px solid #d1d5db;">
                                    <option>All Vehicle Types</option>
                                    <option>Light Trucks</option>
                                    <option>SUVs</option>
                                    <option>Passenger Cars</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Main Content -->
                <div class="dealer-main">
                    <div class="leads-grid" id="dealerLeads">
                        <!-- Sample leads will be populated here -->
                    </div>
                </div>
                
                <!-- Actions Sidebar (Large Desktop Only) -->
                <div class="dealer-actions">
                    <div class="card">
                        <h5 style="margin-bottom: 16px; color: #1f2937;">Quick Actions</h5>
                        
                        <button class="btn" style="margin-bottom: 12px; font-size: 14px;">
                            📧 Email All Critical
                        </button>
                        
                        <button class="btn" style="margin-bottom: 12px; font-size: 14px; background: #059669;">
                            📊 Generate Report
                        </button>
                        
                        <button class="btn" style="margin-bottom: 12px; font-size: 14px; background: #7c3aed;">
                            📤 Export CSV
                        </button>
                        
                        <div style="margin-top: 20px; padding: 16px; background: #f8fafc; border-radius: 8px;">
                            <h6 style="margin-bottom: 8px; color: #374151;">Today's Summary</h6>
                            <div style="font-size: 12px; color: #6b7280;">
                                • 12 new critical leads<br/>
                                • $23,450 potential revenue<br/>
                                • 89% contact success rate
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            Powered by Argonne National Laboratory Research & Academic Standards
        </div>
    </div>

    <script>
        // Tab switching functionality
        function switchTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remove active class from all buttons
            const tabButtons = document.querySelectorAll('.tab-btn');
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab and activate button
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
            
            // Load dealer leads if switching to dealer tab
            if (tabName === 'dealer') {
                loadDealerLeads();
            }
        }
        
        // Card flipping functionality
        function flipCard(card) {
            card.classList.toggle('flipped');
        }
        
        // Demo VIN functionality
        function setDemoVin(vin) {
            document.getElementById('vin').value = vin;
        }
        
        // Risk score calculation
        document.getElementById('riskForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const vin = document.getElementById('vin').value;
            if (vin.length !== 17) {
                showError('Please enter a valid 17-character VIN');
                return;
            }
            
            showLoading(true);
            
            try {
                const response = await fetch('/api/risk-score', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ vin: vin })
                });
                
                if (!response.ok) {
                    throw new Error('Risk calculation failed');
                }
                
                const result = await response.json();
                displayRiskResult(result);
                
            } catch (error) {
                showError('Failed to calculate risk score. Please try again.');
            }
            
            showLoading(false);
        });
        
        function showLoading(show) {
            document.getElementById('loading').style.display = show ? 'block' : 'none';
            document.getElementById('submitBtn').disabled = show;
        }
        
        function showError(message) {
            const errorElement = document.getElementById('error');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
            setTimeout(() => {
                errorElement.style.display = 'none';
            }, 5000);
        }
        
        function displayRiskResult(result) {
            // Show result cards
            document.getElementById('result').style.display = 'block';
            document.getElementById('detailedResult').style.display = 'block';
            
            // Update risk score
            const riskScore = (result.risk_score * 100).toFixed(1);
            document.getElementById('riskScore').textContent = riskScore + '%';
            
            // Update severity
            const severityBadge = document.getElementById('severityBadge');
            severityBadge.textContent = result.severity_bucket.toUpperCase();
            severityBadge.className = 'severity-badge badge-' + result.severity_bucket.toLowerCase();
            
            // Update details
            document.getElementById('confidence').textContent = (result.confidence * 100).toFixed(0) + '%';
            document.getElementById('cohort').textContent = result.cohort;
            document.getElementById('stressors').textContent = result.dominant_stressors.join(', ') || 'None detected';
            document.getElementById('revenue').textContent = '$' + result.revenue_opportunity;
            
            // Update recommended action
            document.querySelector('#recommendedAction .detail-value').textContent = result.recommended_action;
        }
        
        // Load dealer leads
        function loadDealerLeads() {
            const dealerLeads = document.getElementById('dealerLeads');
            if (dealerLeads.children.length > 0) return; // Already loaded
            
            // Sample leads for demo
            const sampleLeads = [
                {
                    name: "Sarah Johnson",
                    vehicle: "2022 F-150",
                    priority: "Critical",
                    issue: "Battery Failure Risk 84%",
                    revenue: "$405",
                    talking_points: ["3.3x above cohort average", "Short trip pattern detected", "Miami heat exposure"]
                },
                {
                    name: "Mike Rodriguez", 
                    vehicle: "2021 Explorer",
                    priority: "High",
                    issue: "Commercial Fleet Usage",
                    revenue: "$385",
                    talking_points: ["Multiple driver usage", "Extended idle time", "Maintenance due"]
                },
                {
                    name: "Jennifer Chen",
                    vehicle: "2023 Ranger",
                    priority: "Medium", 
                    issue: "Temperature Cycling",
                    revenue: "$225",
                    talking_points: ["Day/night temp swings", "Urban stop-start traffic", "Preventive care recommended"]
                }
            ];
            
            sampleLeads.forEach(lead => {
                const leadElement = createLeadCard(lead);
                dealerLeads.appendChild(leadElement);
            });
        }
        
        function createLeadCard(lead) {
            const div = document.createElement('div');
            div.className = 'lead-card';
            
            div.innerHTML = `
                <div class="lead-header">
                    <div class="customer-name">${lead.name}</div>
                    <div class="priority-badge priority-${lead.priority.toLowerCase()}">${lead.priority}</div>
                </div>
                <div class="vehicle-info">${lead.vehicle}</div>
                <div class="issue-type">${lead.issue}</div>
                <div class="talking-points">
                    <div class="talking-points-title">Key Talking Points:</div>
                    ${lead.talking_points.map(point => `<div class="talking-point">${point}</div>`).join('')}
                </div>
                <div class="revenue-estimate">Revenue Opportunity: ${lead.revenue}</div>
            `;
            
            return div;
        }
        
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            // Set up initial state
            console.log('VIN Stressors Desktop UI Loaded');
        });
    </script>
</body>
</html>
"""

def add_desktop_routes(app: FastAPI):
    """Add desktop-optimized routes to the FastAPI app"""
    
    @app.get("/desktop", response_class=HTMLResponse)
    async def desktop_interface():
        """Desktop-optimized interface"""
        return get_desktop_optimized_ui()
    
    @app.get("/responsive", response_class=HTMLResponse)  
    async def responsive_interface():
        """Responsive interface (same as desktop)"""
        return get_desktop_optimized_ui() 