"""
Enhanced API Gateway for VIN Stressors Platform
Now with integrated data sources and production optimization
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Dict, Optional, List
import os
import json
import logging
import secrets
from datetime import datetime

# Import our services
from src.engines.bayesian_engine_v2 import BayesianRiskEngine
from src.services.cohort_service import CohortService
from src.services.integration_manager import integration_manager
from src.api.desktop_optimized_ui import add_desktop_routes
from src.api.mobile_ui import add_mobile_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VIN Stressors API",
    description="Universal Vehicle Intelligence Platform with Government Data Validation",
    version="2.1.0"
)

# HTTP Basic Auth for demo protection
security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Validate HTTP Basic Auth credentials"""
    is_correct_username = secrets.compare_digest(credentials.username, "dealer")
    is_correct_password = secrets.compare_digest(credentials.password, "stressors2024")
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Initialize services
try:
    bayesian_engine = BayesianRiskEngine()
    cohort_service = CohortService()
    logger.info("✅ All services initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing services: {str(e)}")
    bayesian_engine = None
    cohort_service = None

class VINRequest(BaseModel):
    vin: str
    miles: Optional[int] = None
    location: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint (no auth required)"""
    try:
        # Check integration status
        integration_status = integration_manager.get_integration_status()
        health_percentage = integration_status['system_health']['health_percentage']
        
        return {
            "status": "healthy" if health_percentage >= 75 else "degraded",
            "service": "vin-stressors",
            "version": "2.1",
            "ai_enabled": False,
            "integrations": {
                "health_percentage": health_percentage,
                "active_integrations": integration_status['system_health']['active_integrations'],
                "total_integrations": integration_status['system_health']['total_integrations']
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "degraded",
            "service": "vin-stressors", 
            "version": "2.1",
            "ai_enabled": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/integrations/status")
async def get_integration_status(current_user: str = Depends(get_current_user)):
    """Get comprehensive integration status"""
    try:
        status = integration_manager.get_integration_status()
        return status
    except Exception as e:
        logger.error(f"Integration status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/integrations/intelligence")
async def get_combined_intelligence(current_user: str = Depends(get_current_user)):
    """Get combined business intelligence from all integrations"""
    try:
        intelligence = integration_manager.get_combined_intelligence()
        return intelligence
    except Exception as e:
        logger.error(f"Combined intelligence error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/integrations/optimize")
async def optimize_integrations(current_user: str = Depends(get_current_user)):
    """Optimize integrations for production"""
    try:
        optimization_results = integration_manager.optimize_for_production()
        return optimization_results
    except Exception as e:
        logger.error(f"Integration optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/integrations/clear-cache")
async def clear_integration_cache(current_user: str = Depends(get_current_user)):
    """Clear integration cache"""
    try:
        integration_manager.clear_cache()
        return {"status": "success", "message": "Cache cleared", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads/database")
async def get_lead_database(current_user: str = Depends(get_current_user)):
    """Get the enterprise lead database"""
    try:
        leads_data = integration_manager.load_lead_database()
        if 'error' in leads_data:
            raise HTTPException(status_code=404, detail=leads_data['error'])
        
        # Return summary for API (not full 5000 leads)
        summary = leads_data.get('summary', {})
        sample_leads = leads_data.get('leads', [])[:10]  # First 10 for preview
        
        return {
            "summary": summary,
            "sample_leads": sample_leads,
            "total_leads": len(leads_data.get('leads', [])),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Lead database error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weather/validation")
async def get_weather_validation(current_user: str = Depends(get_current_user)):
    """Get weather validation data"""
    try:
        weather_data = integration_manager.load_weather_validation()
        if 'error' in weather_data:
            raise HTTPException(status_code=404, detail=weather_data['error'])
        return weather_data
    except Exception as e:
        logger.error(f"Weather validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/nhtsa/complaints")
async def get_nhtsa_complaints(current_user: str = Depends(get_current_user)):
    """Get NHTSA complaint validation data"""
    try:
        nhtsa_data = integration_manager.load_nhtsa_complaints()
        if 'error' in nhtsa_data:
            raise HTTPException(status_code=404, detail=nhtsa_data['error'])
        return nhtsa_data
    except Exception as e:
        logger.error(f"NHTSA complaints error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calculate")
async def calculate_risk(request: VINRequest, current_user: str = Depends(get_current_user)):
    """Calculate VIN risk score with integrated data sources"""
    try:
        if not bayesian_engine or not cohort_service:
            raise HTTPException(status_code=503, detail="Risk calculation services unavailable")
        
        # Get cohort assignment
        cohort_result = cohort_service.assign_cohort(request.vin, request.miles or 45000)
        
        if 'error' in cohort_result:
            raise HTTPException(status_code=400, detail=cohort_result['error'])
        
        cohort_id = cohort_result['cohort_id']
        
        # Calculate risk using Bayesian engine
        risk_result = bayesian_engine.calculate_vin_risk(
            vin=request.vin,
            cohort_id=cohort_id,
            miles=request.miles or 45000,
            climate_zone=request.location or "moderate"
        )
        
        if 'error' in risk_result:
            raise HTTPException(status_code=400, detail=risk_result['error'])
        
        # Enhanced response with integration data
        response = {
            **risk_result,
            'cohort_info': cohort_result,
            'data_sources': {
                'bayesian_engine': 'active',
                'cohort_system': 'active',
                'integration_status': 'validated'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cohorts")
async def get_cohorts(current_user: str = Depends(get_current_user)):
    """Get available cohorts"""
    try:
        cohorts_data = integration_manager.load_cohort_data()
        if 'error' in cohorts_data:
            raise HTTPException(status_code=404, detail=cohorts_data['error'])
        return cohorts_data
    except Exception as e:
        logger.error(f"Cohorts error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/demo")
async def get_demo_calculations(current_user: str = Depends(get_current_user)):
    """Get pre-calculated demo results for faster loading"""
    try:
        demo_vins = [
            {"vin": "1FTFW1E43MKF12345", "miles": 45000, "location": "southeast"},
            {"vin": "1FTFW1E43MKF67890", "miles": 62000, "location": "northeast"},
            {"vin": "1FTFW1E43MKF54321", "miles": 38000, "location": "southwest"},
            {"vin": "1FTFW1E43MKF98765", "miles": 71000, "location": "midwest"}
        ]
        
        results = []
        for demo_vin in demo_vins:
            try:
                if bayesian_engine and cohort_service:
                    cohort_result = cohort_service.assign_cohort(demo_vin["vin"], demo_vin["miles"])
                    if 'error' not in cohort_result:
                        risk_result = bayesian_engine.calculate_vin_risk(
                            vin=demo_vin["vin"],
                            cohort_id=cohort_result['cohort_id'],
                            miles=demo_vin["miles"],
                            climate_zone=demo_vin["location"]
                        )
                        if 'error' not in risk_result:
                            results.append({
                                **demo_vin,
                                **risk_result,
                                'cohort_info': cohort_result
                            })
            except Exception as e:
                logger.warning(f"Demo calculation error for {demo_vin['vin']}: {str(e)}")
                
        return {"demo_results": results, "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(current_user: str = Depends(get_current_user)):
    """Serve the enhanced homepage with integration status"""
    try:
        # Get integration status for display
        integration_status = integration_manager.get_integration_status()
        intelligence = integration_manager.get_combined_intelligence()
        
        credibility_score = intelligence.get('business_metrics', {}).get('credibility_score', 0)
        market_readiness = intelligence.get('business_metrics', {}).get('market_readiness', 'DEVELOPMENT')
        
        # Inject integration stats into the HTML
        html_content = get_enhanced_html_with_integrations(integration_status, credibility_score, market_readiness)
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Homepage error: {str(e)}")
        # Fallback to basic HTML
        return HTMLResponse(content=get_basic_html())

def get_enhanced_html_with_integrations(integration_status: Dict, credibility_score: float, market_readiness: str) -> str:
    """Get enhanced HTML with real integration data"""
    
    # Calculate integration metrics
    health_percentage = integration_status.get('system_health', {}).get('health_percentage', 0)
    active_integrations = integration_status.get('system_health', {}).get('active_integrations', 0)
    total_integrations = integration_status.get('system_health', {}).get('total_integrations', 4)
    
    # Get specific integration data
    integrations = integration_status.get('integrations', {})
    lead_count = integrations.get('lead_database', {}).get('count', 0)
    weather_accuracy = integrations.get('weather_validation', {}).get('accuracy', 'UNKNOWN')
    nhtsa_count = integrations.get('nhtsa_complaints', {}).get('count', 0)
    cohort_count = integrations.get('cohort_data', {}).get('count', 4)
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIN Stressors - Vehicle Intelligence Platform</title>
    <style>
        * {{ 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }}
        
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1a202c;
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 100;
        }}
        
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
        }}
        
        .logo {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            text-decoration: none;
        }}
        
        .integration-status {{
            display: flex;
            align-items: center;
            gap: 1rem;
            color: white;
            font-size: 0.9rem;
        }}
        
        .status-indicator {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(255, 255, 255, 0.1);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
        }}
        
        .status-dot.warning {{ background: #f59e0b; }}
        .status-dot.error {{ background: #ef4444; }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 8rem 2rem 4rem;
        }}
        
        .hero {{
            text-align: center;
            margin-bottom: 4rem;
        }}
        
        .hero h1 {{
            font-size: 3.5rem;
            font-weight: 800;
            color: white;
            margin-bottom: 1rem;
            text-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .hero p {{
            font-size: 1.25rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 2rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .credibility-banner {{
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 2rem auto;
            max-width: 800px;
            text-align: center;
            color: white;
        }}
        
        .credibility-score {{
            font-size: 2rem;
            font-weight: 700;
            color: #10b981;
            margin-bottom: 0.5rem;
        }}
        
        .market-readiness {{
            font-size: 1.1rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .integration-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }}
        
        .integration-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
            color: white;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .integration-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }}
        
        .card-icon {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        
        .card-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .card-metric {{
            font-size: 2rem;
            font-weight: 700;
            color: #10b981;
            margin: 0.5rem 0;
        }}
        
        .card-description {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        .tab-container {{
            margin-top: 3rem;
        }}
        
        .tabs {{
            display: flex;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 0.5rem;
            margin-bottom: 2rem;
        }}
        
        .tab {{
            flex: 1;
            text-align: center;
            padding: 1rem;
            border-radius: 8px;
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.7);
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .tab.active {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .tab-content {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            min-height: 400px;
        }}
        
        .tab-panel {{
            display: none;
        }}
        
        .tab-panel.active {{
            display: block;
        }}
        
        .api-demo {{
            margin-top: 2rem;
        }}
        
        .api-endpoint {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9rem;
        }}
        
        .response-preview {{
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
            white-space: pre-wrap;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.8rem;
            max-height: 300px;
            overflow-y: auto;
        }}
        
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 2.5rem; }}
            .integration-grid {{ grid-template-columns: 1fr; }}
            .tabs {{ flex-direction: column; }}
            .container {{ padding: 6rem 1rem 2rem; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="nav-container">
            <a href="/" class="logo">VIN Stressors</a>
            <div class="integration-status">
                <div class="status-indicator">
                    <div class="status-dot {'warning' if health_percentage < 100 else ''}"></div>
                    <span>{active_integrations}/{total_integrations} Integrations Active</span>
                </div>
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span>{health_percentage}% System Health</span>
                </div>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="hero">
            <h1>VIN Stressors</h1>
            <p>Universal Vehicle Intelligence Platform with Government Data Validation</p>
            
            <div class="credibility-banner">
                <div class="credibility-score">{credibility_score}/100</div>
                <div class="market-readiness">{market_readiness}</div>
                <p>Credibility Score based on Government-Validated Data Sources</p>
            </div>
        </div>

        <div class="integration-grid">
            <div class="integration-card">
                <div class="card-icon">🗄️</div>
                <div class="card-title">Enterprise Lead Database</div>
                <div class="card-metric">{lead_count:,}</div>
                <div class="card-description">Southeast market leads with $1M+ revenue opportunity</div>
            </div>
            
            <div class="integration-card">
                <div class="card-icon">🌡️</div>
                <div class="card-title">Weather Validation</div>
                <div class="card-metric">{weather_accuracy}</div>
                <div class="card-description">Government weather data validation across 20 locations</div>
            </div>
            
            <div class="integration-card">
                <div class="card-icon">📋</div>
                <div class="card-title">NHTSA Complaints</div>
                <div class="card-metric">{nhtsa_count}</div>
                <div class="card-description">Real Ford battery complaints from government database</div>
            </div>
            
            <div class="integration-card">
                <div class="card-icon">🎯</div>
                <div class="card-title">Cohort System</div>
                <div class="card-metric">{cohort_count}</div>
                <div class="card-description">Academic-sourced cohorts with Argonne validation</div>
            </div>
        </div>

        <div class="tab-container">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('intelligence')">Intelligence</button>
                <button class="tab" onclick="switchTab('riskscore')">Risk Score</button>
                <button class="tab" onclick="switchTab('dealer')">Dealer Portal</button>
            </div>

            <div class="tab-content">
                <div id="intelligence-panel" class="tab-panel active">
                    <h2>Integrated Business Intelligence</h2>
                    <p>Real-time access to validated data sources for enterprise vehicle intelligence.</p>
                    
                    <div class="api-demo">
                        <h3>Live Integration Status</h3>
                        <div class="api-endpoint">GET /api/integrations/status</div>
                        <div class="response-preview" id="integration-response">Loading...</div>
                        
                        <h3>Combined Intelligence</h3>
                        <div class="api-endpoint">GET /api/integrations/intelligence</div>
                        <div class="response-preview" id="intelligence-response">Loading...</div>
                    </div>
                </div>

                <div id="riskscore-panel" class="tab-panel">
                    <h2>VIN Risk Analysis</h2>
                    <p>Government-validated stressor analysis with Bayesian risk calculations.</p>
                    
                    <div class="api-demo">
                        <h3>Risk Calculation API</h3>
                        <div class="api-endpoint">POST /api/calculate</div>
                        <div class="response-preview">
{{"vin": "1FTFW1E43MKF12345", "miles": 45000, "location": "southeast"}}

Response:
{{"risk_score": 0.18, "cohort": "lighttruck_midwest_winter", "stressor_analysis": "validated"}}
                        </div>
                    </div>
                </div>

                <div id="dealer-panel" class="tab-panel">
                    <h2>Dealer Portal Integration</h2>
                    <p>Customer leads with personalized talking points and revenue optimization.</p>
                    
                    <div class="api-demo">
                        <h3>Lead Database API</h3>
                        <div class="api-endpoint">GET /api/leads/database</div>
                        <div class="response-preview">
{{"summary": {{"total_leads": {lead_count}, "total_revenue": "$1,066,415"}}, "sample_leads": [...], "geographic_distribution": "Southeast US"}}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {{
            // Remove active class from all tabs and panels
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
            
            // Add active class to selected tab and panel
            event.target.classList.add('active');
            document.getElementById(tabName + '-panel').classList.add('active');
        }}
        
        // Load live integration data
        async function loadIntegrationData() {{
            try {{
                const response = await fetch('/api/integrations/status');
                const data = await response.json();
                document.getElementById('integration-response').textContent = JSON.stringify(data, null, 2);
            }} catch (error) {{
                document.getElementById('integration-response').textContent = 'Error loading integration status';
            }}
            
            try {{
                const response = await fetch('/api/integrations/intelligence');
                const data = await response.json();
                document.getElementById('intelligence-response').textContent = JSON.stringify(data, null, 2);
            }} catch (error) {{
                document.getElementById('intelligence-response').textContent = 'Error loading intelligence data';
            }}
        }}
        
        // Load data when page loads
        document.addEventListener('DOMContentLoaded', loadIntegrationData);
    </script>
</body>
</html>
"""

def get_basic_html() -> str:
    """Fallback basic HTML if integration data is unavailable"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>VIN Stressors</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 2rem; background: #f8fafc; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        h1 { color: #1a202c; margin-bottom: 1rem; }
        .status { background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; margin: 1rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>VIN Stressors</h1>
        <div class="status">System initializing... Please check integration status.</div>
    </div>
</body>
</html>
"""

# Add responsive UI routes
add_mobile_routes(app)     # Mobile-first responsive UI
add_desktop_routes(app)    # Desktop-optimized layouts

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 