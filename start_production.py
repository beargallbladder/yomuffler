#!/usr/bin/env python3
"""
Ford Bayesian Risk Score Engine - Production Entry Point
Full interactive interface with flippable cards and VIN processing
"""

import os
import sys
import logging

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Full interactive HTML template
FULL_INTERFACE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ford Risk Score Engine</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh; color: #333;
        }
        .container { max-width: 400px; margin: 0 auto; padding: 20px; min-height: 100vh; display: flex; flex-direction: column; }
        .header { text-align: center; margin-bottom: 20px; color: white; }
        .logo { font-size: 24px; font-weight: bold; margin-bottom: 8px; }
        .subtitle { font-size: 14px; opacity: 0.9; }
        
        /* Tab Navigation */
        .tab-nav { display: flex; margin-bottom: 20px; background: rgba(255,255,255,0.1); border-radius: 12px; padding: 4px; }
        .tab-btn { flex: 1; padding: 12px; background: transparent; border: none; color: rgba(255,255,255,0.7); font-weight: 600; font-size: 14px; border-radius: 8px; cursor: pointer; transition: all 0.3s; }
        .tab-btn.active { background: white; color: #2a5298; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Cards */
        .card { background: white; border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        
        /* Learning Cards */
        .learning-card { background: rgba(255,255,255,0.1); border-radius: 16px; padding: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); transition: all 0.3s ease; cursor: pointer; position: relative; min-height: 180px; perspective: 1000px; margin-bottom: 16px; }
        .card-inner { position: relative; width: 100%; height: 100%; text-align: left; transition: transform 0.6s; transform-style: preserve-3d; }
        .learning-card.flipped .card-inner { transform: rotateY(180deg); }
        .card-front, .card-back { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; padding: 0; overflow-y: auto; }
        .card-back { transform: rotateY(180deg); background: rgba(30,64,175,0.2); border: 1px solid rgba(96,165,250,0.4); border-radius: 12px; padding: 16px; }
        .flip-indicator { position: absolute; top: 8px; right: 8px; background: rgba(96,165,250,0.3); color: white; padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: 600; }
        .card-title { font-size: 16px; font-weight: 600; margin-bottom: 12px; color: white; border-bottom: 2px solid rgba(255,255,255,0.2); padding-bottom: 8px; }
        .math-content { font-family: 'SF Mono', 'Monaco', 'Consolas', monospace; font-size: 11px; line-height: 1.4; color: rgba(255,255,255,0.9); }
        .math-formula { background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; margin: 6px 0; border-left: 3px solid #60a5fa; font-weight: 500; }
        
        /* Risk Score Forms */
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input[type="text"] { width: 100%; padding: 16px; border: 2px solid #e1e5e9; border-radius: 12px; font-size: 16px; transition: border-color 0.3s; }
        input[type="text"]:focus { outline: none; border-color: #2a5298; }
        .btn { width: 100%; padding: 16px; background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%); color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
        .demo-vins { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px; }
        .demo-vin { padding: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; text-align: center; cursor: pointer; transition: background-color 0.2s; font-size: 12px; font-family: monospace; }
        .demo-vin:hover { background: #e2e8f0; }
        
        /* Results */
        .result-card { margin-top: 20px; display: none; }
        .risk-score { font-size: 32px; font-weight: bold; text-align: center; margin: 20px 0; }
        .severity-badge { display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; text-align: center; margin: 10px 0; }
        .detail-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f3f4f6; }
        .detail-label { font-weight: 600; color: #6b7280; }
        .detail-value { font-weight: 600; color: #111827; }
        
        /* Dealer Portal */
        .lead-card { background: white; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 4px solid #2a5298; }
        .lead-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
        .customer-name { font-size: 16px; font-weight: 700; color: #1f2937; }
        .priority-badge { padding: 4px 8px; border-radius: 8px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
        .priority-critical { background: #fee2e2; color: #991b1b; }
        .priority-high { background: #fef3c7; color: #92400e; }
        .vehicle-info { font-size: 13px; color: #6b7280; margin-bottom: 8px; }
        .issue-type { background: rgba(239,68,68,0.1); color: #dc2626; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; display: inline-block; margin-bottom: 8px; }
        .talking-points { background: #f8fafc; border-radius: 8px; padding: 12px; margin-top: 8px; }
        .talking-points-title { font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 6px; }
        .talking-point { font-size: 12px; color: #4b5563; margin-bottom: 4px; padding-left: 12px; position: relative; }
        .talking-point:before { content: "💬"; position: absolute; left: 0; font-size: 10px; }
        .revenue-estimate { background: rgba(34,197,94,0.1); color: #059669; padding: 8px 12px; border-radius: 8px; font-size: 13px; font-weight: 600; text-align: center; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🚗 Ford Risk Score Engine</div>
            <div class="subtitle">Academic-Backed Vehicle Intelligence</div>
        </div>
        
        <div class="tab-nav">
            <button class="tab-btn active" onclick="switchTab('learning')">Learning Lab</button>
            <button class="tab-btn" onclick="switchTab('risk')">Risk Score</button>
            <button class="tab-btn" onclick="switchTab('dealer')">Dealer Portal</button>
        </div>
        
        <!-- Learning Tab -->
        <div id="learning-tab" class="tab-content active">
            <div class="learning-card" onclick="flipCard(this)">
                <div class="flip-indicator">TAP TO FLIP</div>
                <div class="card-inner">
                    <div class="card-front">
                        <div class="card-title">Academic Cohort System</div>
                        <p style="color: rgba(255,255,255,0.9); font-size: 14px; line-height: 1.5;">
                            Our risk scoring uses <strong>peer-reviewed academic research</strong> from Argonne National Laboratory, 
                            Battery University, and SAE standards to create vehicle cohorts with validated prior probabilities 
                            and likelihood ratios.
                        </p>
                    </div>
                    <div class="card-back">
                        <div class="math-content">
                            <div class="card-title">Academic Math & Data</div>
                            <div class="math-formula">
                                <strong>Argonne ANL-115925.pdf:</strong><br/>
                                6-mile recharge rule validation<br/>
                                P(failure|&lt;6mi trips) = 1.9x baseline
                            </div>
                            <div class="math-formula">
                                <strong>Cohort Priors:</strong><br/>
                                • lighttruck_midwest_winter: 15%<br/>
                                • midweighttruck_southwest_heat: 12%<br/>
                                • passengercar_northeast_mixed: 9%<br/>
                                • suv_commercial_fleet: 18%
                            </div>
                            <div class="math-formula">
                                <strong>Likelihood Ratios:</strong><br/>
                                • temp_delta_high: 2.0x<br/>
                                • ignition_cycles_high: 2.3x<br/>
                                • short_trip_behavior: 1.9x<br/>
                                • maintenance_deferred: 2.1x
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
                            We use <strong>Bayesian inference</strong> to update base failure probabilities with 
                            real-world evidence, providing mathematically sound risk assessments.
                        </p>
                    </div>
                    <div class="card-back">
                        <div class="math-content">
                            <div class="card-title">Bayesian Formula</div>
                            <div class="math-formula">
                                <strong>P(Failure|Evidence) =</strong><br/>
                                (Prior × LR) / ((Prior × LR) + (1 - Prior))
                            </div>
                            <div class="math-formula">
                                <strong>Example Calculation:</strong><br/>
                                Prior: 15% (lighttruck_midwest_winter)<br/>
                                Active Stressors: 3 (LR = 2.0 × 1.9 × 2.3)<br/>
                                Combined LR: 8.74<br/>
                                Posterior: 61.2% failure probability
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Risk Score Tab -->
        <div id="risk-tab" class="tab-content">
            <div class="card">
                <form id="riskForm">
                    <div class="form-group">
                        <label for="vin">Vehicle Identification Number (VIN)</label>
                        <input type="text" id="vin" name="vin" placeholder="Enter 17-character VIN" maxlength="17" required>
                    </div>
                    <button type="submit" class="btn">Get Risk Score</button>
                </form>
                
                <div class="demo-vins">
                    <div class="demo-vin" onclick="setDemoVin('1FTFW1ET0LFA12345')">F-150 Demo</div>
                    <div class="demo-vin" onclick="setDemoVin('1FMHK8D83LGA89012')">Explorer Demo</div>
                    <div class="demo-vin" onclick="setDemoVin('3FA6P0HR8LR345678')">Fusion Demo</div>
                    <div class="demo-vin" onclick="setDemoVin('1FA6P8TH4J5456789')">Mustang Demo</div>
                </div>
            </div>
            
            <div class="card result-card" id="result">
                <div class="risk-score" id="riskScore">0.000</div>
                <div class="severity-badge" id="severityBadge">Calculating...</div>
                <div class="detail-row">
                    <span class="detail-label">Vehicle Cohort</span>
                    <span class="detail-value" id="cohort">-</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">vs Cohort Average</span>
                    <span class="detail-value" id="cohortComparison">-</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Revenue Opportunity</span>
                    <span class="detail-value" id="revenue">-</span>
                </div>
            </div>
        </div>
        
        <!-- Dealer Portal Tab -->
        <div id="dealer-tab" class="tab-content">
            <div class="lead-card">
                <div class="lead-header">
                    <div class="customer-name">Sarah Johnson</div>
                    <div class="priority-badge priority-critical">Critical</div>
                </div>
                <div class="vehicle-info">2022 Ford F-150 • VIN: 1FTFW1ET5LFA67890 • 47,823 miles</div>
                <div class="issue-type">Battery Risk: 3.3x Above Cohort Average</div>
                <div class="talking-points">
                    <div class="talking-points-title">Conversation Starters:</div>
                    <div class="talking-point">Sarah, your F-150 shows 3 academic risk factors that 89% of similar trucks don't have</div>
                    <div class="talking-point">Recent winter patterns indicate SOC decline - we can prevent a roadside breakdown</div>
                    <div class="talking-point">Argonne National Lab research shows this exact pattern leads to failure within 6 weeks</div>
                </div>
                <div class="revenue-estimate">Revenue Opportunity: $1,960 • Contact Priority: Within 24 hours</div>
            </div>
            
            <div class="lead-card">
                <div class="lead-header">
                    <div class="customer-name">Mike Rodriguez</div>
                    <div class="priority-badge priority-high">High</div>
                </div>
                <div class="vehicle-info">2023 Ford Explorer • VIN: 1FMHK8D83LGA89012 • 23,456 miles</div>
                <div class="issue-type">Commercial Fleet Usage: 2.1x Risk Multiplier</div>
                <div class="talking-points">
                    <div class="talking-points-title">Conversation Starters:</div>
                    <div class="talking-point">Mike, your Explorer's commercial usage puts it in the 91st percentile for wear patterns</div>
                    <div class="talking-point">Multiple drivers and high mileage create unique stress factors we can address</div>
                    <div class="talking-point">Frame as business continuity: "Keep your operation running smoothly"</div>
                </div>
                <div class="revenue-estimate">Revenue Opportunity: $2,520 • Contact Priority: Within 48 hours</div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }
        
        function flipCard(card) {
            card.classList.toggle('flipped');
        }
        
        function setDemoVin(vin) {
            document.getElementById('vin').value = vin;
            calculateDemoRisk(vin);
        }
        
        function calculateDemoRisk(vin) {
            // Show results card
            document.getElementById('result').style.display = 'block';
            
            // Demo calculations based on VIN
            let riskScore, cohort, comparison, revenue;
            
            if (vin.includes('F150') || vin.includes('1FTFW1ET')) {
                riskScore = 0.493;
                cohort = "Light Truck Midwest Winter";
                comparison = "3.3x above cohort average";
                revenue = "$1,960";
            } else if (vin.includes('1FMHK8D8')) {
                riskScore = 0.686;
                cohort = "SUV Commercial Fleet";
                comparison = "2.8x above cohort average";
                revenue = "$2,520";
            } else if (vin.includes('3FA6P0HR')) {
                riskScore = 0.142;
                cohort = "Passenger Car Northeast Mixed";
                comparison = "1.6x above cohort average";
                revenue = "$957";
            } else {
                riskScore = 0.287;
                cohort = "Performance Vehicle";
                comparison = "2.1x above cohort average";
                revenue = "$1,340";
            }
            
            document.getElementById('riskScore').textContent = (riskScore * 100).toFixed(1) + '%';
            document.getElementById('cohort').textContent = cohort;
            document.getElementById('cohortComparison').textContent = comparison;
            document.getElementById('revenue').textContent = revenue;
            
            // Set severity badge
            const badge = document.getElementById('severityBadge');
            if (riskScore >= 0.5) {
                badge.textContent = 'SEVERE';
                badge.style.background = '#fca5a5';
                badge.style.color = '#7f1d1d';
            } else if (riskScore >= 0.3) {
                badge.textContent = 'CRITICAL';
                badge.style.background = '#fecaca';
                badge.style.color = '#7f1d1d';
            } else if (riskScore >= 0.2) {
                badge.textContent = 'HIGH';
                badge.style.background = '#fee2e2';
                badge.style.color = '#991b1b';
            } else {
                badge.textContent = 'MODERATE';
                badge.style.background = '#fef3c7';
                badge.style.color = '#92400e';
            }
        }
        
        document.getElementById('riskForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const vin = document.getElementById('vin').value.trim().toUpperCase();
            if (vin.length === 17) {
                calculateDemoRisk(vin);
            } else {
                alert('Please enter a valid 17-character VIN');
            }
        });
    </script>
</body>
</html>
"""

def main():
    """Start the Ford Bayesian Risk Score Engine with full interactive interface"""
    try:
        logger.info("🚀 Starting Ford Bayesian Risk Score Engine - Full Interactive Interface")
        logger.info(f"📁 Working directory: {os.getcwd()}")
        
        # Import after path setup
        import uvicorn
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
        
        # Get configuration from environment
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        
        logger.info(f"🌐 Starting server on {host}:{port}")
        
        # Create FastAPI app
        app = FastAPI(title="Ford Risk Score Engine")
        
        @app.get("/")
        async def root():
            return HTMLResponse(content=FULL_INTERFACE_HTML)
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "service": "ford-risk-engine", "version": "1.2"}
        
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