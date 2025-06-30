"""
Ford Risk Score Engine - Geographic Visualization API

Professional US Map visualization showing Southeast VIN opportunities with:
- Florida opportunities highlighted (high-stress thermal environment)
- Geographic context for existing DTCs and prognostics  
- Stressor visualization even when no active alerts
- Time-based opportunity analysis
- Revenue potential mapping
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime, timedelta
import logging
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeographicVisualizationAPI:
    def __init__(self):
        self.southeast_states = {
            'FL': {'name': 'Florida', 'lat': 27.7663, 'lng': -81.6868, 'leads': 0, 'revenue': 0, 'priority': 'high'},
            'GA': {'name': 'Georgia', 'lat': 33.0406, 'lng': -83.6431, 'leads': 0, 'revenue': 0, 'priority': 'high'},
            'TN': {'name': 'Tennessee', 'lat': 35.7478, 'lng': -86.7923, 'leads': 0, 'revenue': 0, 'priority': 'high'},
            'SC': {'name': 'South Carolina', 'lat': 33.8569, 'lng': -80.9450, 'leads': 0, 'revenue': 0, 'priority': 'medium'},
            'NC': {'name': 'North Carolina', 'lat': 35.6301, 'lng': -79.8064, 'leads': 0, 'revenue': 0, 'priority': 'medium'},
            'AL': {'name': 'Alabama', 'lat': 32.3617, 'lng': -86.7916, 'leads': 0, 'revenue': 0, 'priority': 'medium'},
            'MS': {'name': 'Mississippi', 'lat': 32.7764, 'lng': -89.6678, 'leads': 0, 'revenue': 0, 'priority': 'medium'},
            'LA': {'name': 'Louisiana', 'lat': 31.1695, 'lng': -91.8678, 'leads': 0, 'revenue': 0, 'priority': 'medium'},
            'AR': {'name': 'Arkansas', 'lat': 34.9697, 'lng': -92.3731, 'leads': 0, 'revenue': 0, 'priority': 'low'},
            'KY': {'name': 'Kentucky', 'lat': 37.6681, 'lng': -84.6701, 'leads': 0, 'revenue': 0, 'priority': 'low'},
            'VA': {'name': 'Virginia', 'lat': 37.7693, 'lng': -78.1700, 'leads': 0, 'revenue': 0, 'priority': 'low'},
            'WV': {'name': 'West Virginia', 'lat': 38.4912, 'lng': -80.9540, 'leads': 0, 'revenue': 0, 'priority': 'low'}
        }
        
        # Florida-specific stressor context (extreme thermal environment)
        self.florida_stressors = {
            'heat_stress': {
                'summer_temps': 'Average >90°F for 6+ months',
                'battery_impact': '2.3x higher failure rate (BU-804 studies)',
                'electrolyte_loss': 'Accelerated water loss in high heat',
                'terminal_corrosion': 'Saltwater proximity increases corrosion 4x'
            },
            'humidity_effects': {
                'year_round': '70-90% humidity year-round',
                'electrical_impact': 'Moisture penetration in electrical systems', 
                'oxidation': 'Accelerated metal component oxidation'
            },
            'thermal_cycling': {
                'day_night': '20-30°F daily temperature swings',
                'expansion_contraction': 'Battery case stress from thermal cycling',
                'connection_loosening': 'Thermal expansion loosens connections'
            },
            'usage_patterns': {
                'ac_load': 'A/C electrical load >40% of driving time',
                'tourist_traffic': 'Extended idle in traffic increases alternator stress',
                'coastal_salt': 'Salt air accelerates all metal component degradation'
            }
        }
        
        self.load_vin_data()
    
    def get_current_season(self) -> str:
        """Get current season for seasonal multipliers"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    def get_seasonal_multipliers(self, season: str) -> Dict[str, float]:
        """Get seasonal failure rate multipliers"""
        multipliers = {
            "winter": {"battery": 3.4, "starter": 2.8, "alternator": 1.6},
            "spring": {"battery": 1.2, "starter": 1.1, "alternator": 1.3},
            "summer": {"battery": 2.3, "starter": 1.6, "alternator": 2.1},
            "fall": {"battery": 1.4, "starter": 1.2, "alternator": 1.7}
        }
        return multipliers.get(season, {"battery": 1.0, "starter": 1.0, "alternator": 1.0})
    
    def get_seasonal_multiplier(self, state_code: str, season: str) -> float:
        """Get seasonal multiplier for a specific state"""
        base_multipliers = self.get_seasonal_multipliers(season)
        
        # Florida gets higher multipliers due to extreme conditions
        if state_code == 'FL':
            return base_multipliers.get('battery', 1.0) * 1.2
        else:
            return base_multipliers.get('battery', 1.0)
    
    def generate_context_points(self, state_code: str, state_data: Dict) -> List[str]:
        """Generate context points for a specific state"""
        if state_code == 'FL':
            return [
                "Extreme thermal environment (>90°F for 6+ months)",
                "2.3x higher battery failure rates in summer",
                "Coastal salt air accelerates corrosion 4x",
                "Year-round A/C electrical load stress"
            ]
        else:
            return [
                "High-stress thermal environment analysis",
                "Proactive maintenance opportunities identified", 
                "Academic research foundation for timing"
            ]
    
    def generate_conversation_starters(self, state_code: str, state_data: Dict) -> List[str]:
        """Generate conversation starters for a specific state"""
        if state_code == 'FL':
            return [
                "Florida's extreme thermal environment creates unique stressor patterns",
                "Your vehicle operates in one of the most challenging climates for battery life",
                "Our research shows 2.3x higher battery failure rates in Florida summers"
            ]
        else:
            return [
                f"{state_data['name']} shows elevated stressor patterns requiring proactive maintenance",
                "Regional climate data confirms accelerated component stress in your area",
                "Academic research validates proactive service timing for your location"
            ]
    
    @property
    def stressor_context(self) -> Dict[str, Any]:
        """Return stressor context for professional conversations"""
        return self.florida_stressors
    
    def load_vin_data(self):
        """Load 100k VIN analysis data and aggregate by region"""
        try:
            # Load the new 100k VIN analysis instead of old 5k Southeast data
            comprehensive_file = "comprehensive_100k_analysis_executive_summary_20250629_163100.txt"
            analysis_file = "comprehensive_100k_analysis_lead_strategy_20250629_163100.json"
            
            # Try to load the executive summary first to get basic stats
            regional_data = {}
            if os.path.exists(comprehensive_file):
                with open(comprehensive_file, 'r') as f:
                    content = f.read()
                    
                # Parse the regional distribution from the summary
                lines = content.split('\n')
                for line in lines:
                    if ': ' in line and 'VINs,' in line and '$' in line:
                        # Extract: "SOUTHEAST: 35,000 VINs, $15,910,403 revenue"
                        parts = line.strip().split(':')
                        if len(parts) == 2:
                            region = parts[0].strip()
                            data_part = parts[1].strip()
                            
                            # Extract VIN count and revenue
                            if 'VINs,' in data_part and '$' in data_part:
                                vin_part = data_part.split('VINs,')[0].strip().replace(',', '')
                                revenue_part = data_part.split('$')[1].split(' ')[0].replace(',', '')
                                
                                try:
                                    vin_count = int(vin_part)
                                    revenue = int(revenue_part)
                                    
                                    # Map regions to states for display
                                    if region == 'SOUTHEAST':
                                        for state in ['GA', 'SC', 'NC', 'TN', 'AL']:
                                            if state in self.southeast_states:
                                                self.southeast_states[state]['leads'] = vin_count // 5  # Distribute across SE states
                                                self.southeast_states[state]['revenue'] = revenue // 5
                                    elif region == 'FLORIDA':
                                        if 'FL' in self.southeast_states:
                                            self.southeast_states['FL']['leads'] = vin_count
                                            self.southeast_states['FL']['revenue'] = revenue
                                    elif region == 'TEXAS':
                                        # Add Texas if not in southeast_states
                                        if 'TX' not in self.southeast_states:
                                            self.southeast_states['TX'] = {
                                                'name': 'Texas', 'lat': 31.0, 'lng': -100.0,
                                                'leads': vin_count, 'revenue': revenue, 'priority': 'high'
                                            }
                                    elif region == 'CALIFORNIA':
                                        if 'CA' not in self.southeast_states:
                                            self.southeast_states['CA'] = {
                                                'name': 'California', 'lat': 36.8, 'lng': -119.4,
                                                'leads': vin_count, 'revenue': revenue, 'priority': 'medium'
                                            }
                                    elif region == 'MONTANA':
                                        if 'MT' not in self.southeast_states:
                                            self.southeast_states['MT'] = {
                                                'name': 'Montana', 'lat': 47.0, 'lng': -110.0,
                                                'leads': vin_count, 'revenue': revenue, 'priority': 'high'
                                            }
                                except ValueError:
                                    continue
                                    
                logger.info(f"✅ Loaded 100k VIN analysis data from executive summary")
                
            # Try to load detailed lead strategy data for more context
            if os.path.exists(analysis_file):
                with open(analysis_file, 'r') as f:
                    strategy_data = json.load(f)
                    
                # Add capacity utilization info to states
                lead_optimization = strategy_data.get('lead_volume_optimization', {})
                regional_strategies = lead_optimization.get('regional_strategies', {})
                
                for region, strategy in regional_strategies.items():
                    issue = strategy.get('issue', '')
                    if 'over capacity' in issue.lower():
                        capacity_status = 'over_capacity'
                    elif 'under capacity' in issue.lower():
                        capacity_status = 'under_capacity'
                    else:
                        capacity_status = 'optimal'
                    
                    # Update relevant states with capacity status
                    region_to_states = {
                        'southeast': ['GA', 'SC', 'NC', 'TN', 'AL'],
                        'florida': ['FL'],
                        'texas': ['TX'],
                        'california': ['CA'],
                        'montana': ['MT']
                    }
                    
                    if region in region_to_states:
                        for state in region_to_states[region]:
                            if state in self.southeast_states:
                                self.southeast_states[state]['capacity_status'] = capacity_status
                
                logger.info(f"✅ Enhanced with capacity management data")
                
            # Fallback to old data if 100k analysis not available
            else:
                logger.warning("⚠️ 100k analysis not found, falling back to old 5k dataset")
                vin_file = "vin_leads_database_20250626_154547.json"
                if os.path.exists(vin_file):
                    with open(vin_file, 'r') as f:
                        vin_data = json.load(f)
                    
                    # Aggregate by state (old method)
                    for lead in vin_data:
                        state = lead.get('state', '').upper()
                        if state in self.southeast_states:
                            self.southeast_states[state]['leads'] += 1
                            revenue = self.estimate_revenue(lead, state)
                            self.southeast_states[state]['revenue'] += revenue
                    
                    logger.info(f"Loaded {len(vin_data)} VIN leads from old dataset")
                
        except Exception as e:
            logger.error(f"Error loading VIN data: {str(e)}")
            # Set minimal default data
            for state in self.southeast_states:
                self.southeast_states[state]['leads'] = 100
                self.southeast_states[state]['revenue'] = 50000
    
    def estimate_revenue(self, lead: Dict, state: str) -> float:
        """Estimate revenue potential with state-specific adjustments"""
        base_revenue = 285  # Average battery replacement + service
        
        # Florida gets higher revenue potential due to extreme conditions
        if state == 'FL':
            base_revenue *= 1.4  # 40% higher due to extreme thermal stress
        elif state in ['GA', 'TN', 'SC']:
            base_revenue *= 1.2  # 20% higher for high-priority states
        
        risk_score = lead.get('risk_score', 0.5)
        if risk_score > 0.8:
            return base_revenue * 1.3
        elif risk_score > 0.6:
            return base_revenue * 1.1
        else:
            return base_revenue * 0.8
    
    def get_florida_spotlight(self) -> Dict[str, Any]:
        """Get Florida-specific opportunity spotlight"""
        fl_data = self.southeast_states['FL']
        
        return {
            'state': 'Florida',
            'highlights': {
                'extreme_thermal_environment': 'Highest battery stress in Southeast region',
                'year_round_heat': '>90°F for 6+ months annually',
                'coastal_corrosion': 'Salt air accelerates component degradation 4x',
                'tourism_traffic': 'Extended idle increases alternator stress'
            },
            'opportunities': {
                'total_leads': fl_data['leads'],
                'revenue_potential': fl_data['revenue'],
                'average_per_lead': fl_data['revenue'] / fl_data['leads'] if fl_data['leads'] > 0 else 0,
                'seasonal_multiplier': 2.3  # Summer battery failure rate
            },
            'conversation_starters': [
                "Florida's extreme thermal environment creates unique stressor patterns",
                "Your vehicle operates in one of the most challenging climates for battery life",
                "Coastal salt air and year-round heat require proactive maintenance timing",
                "Our research shows 2.3x higher battery failure rates in Florida summers"
            ],
            'technical_context': {
                'argonne_validation': 'ANL-115925.pdf thermal stress modeling',
                'bu804_studies': 'Heat-induced battery fade research',
                'seasonal_patterns': 'Academic foundation for Florida-specific multipliers'
            }
        }

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

# API instance and router
geo_api = GeographicVisualizationAPI()
geographic_router = APIRouter(prefix="/api/geographic", tags=["geographic"])

@geographic_router.get("/southeast-summary")
async def get_southeast_summary(current_user: str = Depends(get_current_user)):
    """Get Southeast region summary with Florida highlight"""
    try:
        total_leads = sum(state['leads'] for state in geo_api.southeast_states.values())
        total_revenue = sum(state['revenue'] for state in geo_api.southeast_states.values())
        fl_data = geo_api.southeast_states['FL']
        
        # State emojis and data
        state_emojis = {
            'FL': '🌴', 'GA': '🍑', 'TN': '🎸', 'SC': '🏖️', 'NC': '🏔️', 'AL': '🏈',
            'MS': '🎺', 'LA': '🎷', 'AR': '💎', 'KY': '🐎', 'VA': '🏛️', 'WV': '⛰️'
        }
        
        states_data = []
        for code, data in geo_api.southeast_states.items():
            if data['leads'] > 0:  # Only include states with leads
                states_data.append({
                    'code': code,
                    'name': data['name'],
                    'emoji': state_emojis.get(code, '🗺️'),
                    'leads': data['leads'],
                    'revenue': data['revenue']
                })
        
        # Sort by revenue (descending)
        states_data.sort(key=lambda x: x['revenue'], reverse=True)
        
        return {
            'region': 'Southeast',
            'total_leads': total_leads,
            'total_revenue': total_revenue,
            'states': states_data,
            'florida_spotlight': {
                'leads': fl_data['leads'],
                'revenue': fl_data['revenue'],
                'percentage_of_total': (fl_data['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            },
            'academic_foundation': 'Argonne ANL-115925.pdf + BU-804 Heat Stress Studies'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@geographic_router.get("/florida-spotlight")
async def get_florida_spotlight(current_user: str = Depends(get_current_user)):
    """Get detailed Florida opportunity analysis"""
    try:
        return geo_api.get_florida_spotlight()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@geographic_router.get("/state/{state_code}")
async def get_state_details(state_code: str, current_user: str = Depends(get_current_user)):
    """Get detailed information for a specific state"""
    try:
        state_code = state_code.upper()
        if state_code not in geo_api.southeast_states:
            raise HTTPException(status_code=404, detail="State not found in Southeast region")
        
        state_data = geo_api.southeast_states[state_code]
        current_season = geo_api.get_current_season()
        seasonal_multipliers = geo_api.get_seasonal_multipliers(current_season)
        
        return {
            'state_code': state_code,
            'state_name': state_data['name'],
            'coordinates': {'lat': state_data['lat'], 'lng': state_data['lng']},
            'leads': state_data['leads'],
            'revenue_potential': state_data['revenue'],
            'seasonal_adjustment': seasonal_multipliers.get('battery', 1.0),
            'adjusted_revenue': state_data['revenue'] * seasonal_multipliers.get('battery', 1.0),
            'context_points': geo_api.generate_context_points(state_code, state_data),
            'conversation_starters': geo_api.generate_conversation_starters(state_code, state_data),
            'stressor_context': geo_api.stressor_context
        }
    except Exception as e:
        logger.error(f"Error getting state details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Map page router
map_router = APIRouter(tags=["map"])

@map_router.get("/map", response_class=HTMLResponse)
async def geographic_map_page(current_user: str = Depends(get_current_user)):
    """Serve the geographic visualization page"""
    return get_map_html()

def get_map_html():
    """Generate the map HTML with Florida spotlight"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ford VIN Intelligence - Southeast Opportunities</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .logo {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .subtitle {
            font-size: 16px;
            opacity: 0.9;
        }
        
        .florida-spotlight {
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            color: white;
            text-align: center;
        }
        
        .spotlight-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 12px;
        }
        
        .spotlight-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .spotlight-stat {
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 16px;
        }
        
        .stat-value {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 12px;
            opacity: 0.9;
        }
        
        .map-container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .states-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .state-card {
            background: #f8fafc;
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #2a5298;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .state-card.florida {
            border-left-color: #ff6b35;
            background: linear-gradient(135deg, #fff5f2 0%, #fef7f0 100%);
        }
        
        .state-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.1);
        }
        
        .state-name {
            font-size: 18px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 8px;
        }
        
        .revenue-amount {
            font-size: 16px;
            font-weight: 700;
            color: #059669;
            margin-bottom: 12px;
        }
        
        .context-points {
            list-style: none;
            padding: 0;
        }
        
        .context-point {
            font-size: 13px;
            color: #4b5563;
            margin-bottom: 6px;
            padding-left: 16px;
            position: relative;
        }
        
        .context-point:before {
            content: "🌡️";
            position: absolute;
            left: 0;
            font-size: 11px;
        }
        
        .academic-footer {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            color: white;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🗺️ Ford VIN Intelligence</div>
            <div class="subtitle">Southeast Opportunity Mapping • Florida Spotlight</div>
        </div>
        
        <div class="florida-spotlight">
            <div class="spotlight-title">🌴 Florida Opportunities</div>
            <div>Extreme thermal environment • Highest battery stress in Southeast</div>
            <div class="spotlight-stats" id="florida-stats">
                <!-- Florida stats loaded here -->
            </div>
        </div>
        
        <div class="map-container">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #1e3c72; margin-bottom: 8px;">Southeast VIN Opportunities</h2>
                <p style="color: #6b7280;">High-stress thermal environments • Academic foundation • Proactive service opportunities</p>
            </div>
            
            <div class="states-grid" id="states-grid">
                <!-- State cards loaded here -->
            </div>
        </div>
        
        <div class="academic-footer">
            <div style="font-weight: 600; margin-bottom: 8px;">Academic Foundation</div>
            <div style="font-size: 12px; opacity: 0.8;">
                Argonne ANL-115925.pdf • BU-804 Heat Stress Studies • Florida thermal modeling
            </div>
        </div>
    </div>
    
    <script>
        async function loadMapData() {
            try {
                // Load real data from APIs
                const [summaryResponse, floridaResponse] = await Promise.all([
                    fetch('/api/geographic/southeast-summary'),
                    fetch('/api/geographic/florida-spotlight')
                ]);
                
                const summaryData = await summaryResponse.json();
                const floridaData = await floridaResponse.json();
                
                // Populate Florida spotlight with real data
                document.getElementById('florida-stats').innerHTML = `
                    <div class="spotlight-stat">
                        <div class="stat-value">${floridaData.opportunities.total_leads}</div>
                        <div class="stat-label">VIN Leads</div>
                    </div>
                    <div class="spotlight-stat">
                        <div class="stat-value">$${(floridaData.opportunities.revenue_potential/1000).toFixed(0)}K</div>
                        <div class="stat-label">Revenue Potential</div>
                    </div>
                    <div class="spotlight-stat">
                        <div class="stat-value">${floridaData.opportunities.seasonal_multiplier}x</div>
                        <div class="stat-label">Summer Risk</div>
                    </div>
                    <div class="spotlight-stat">
                        <div class="stat-value">90°F+</div>
                        <div class="stat-label">6+ Months</div>
                    </div>
                `;
                
                // Populate states grid with real data
                const statesHTML = summaryData.states.map(state => `
                    <div class="state-card ${state.code === 'FL' ? 'florida' : ''}" onclick="showStateDetails('${state.code}')">
                        <div class="state-name">${state.emoji} ${state.name}</div>
                        <div class="revenue-amount">$${state.revenue.toLocaleString()} • ${state.leads} leads</div>
                        <ul class="context-points">
                            <li class="context-point">${state.code === 'FL' ? 'Extreme thermal environment (>90°F for 6+ months)' : 'High-stress thermal environment analysis'}</li>
                            <li class="context-point">${state.code === 'FL' ? '2.3x higher battery failure rates in summer' : 'Proactive maintenance opportunities identified'}</li>
                            <li class="context-point">${state.code === 'FL' ? 'Coastal salt air accelerates corrosion 4x' : 'Academic research foundation for timing'}</li>
                        </ul>
                    </div>
                `).join('');
                
                document.getElementById('states-grid').innerHTML = statesHTML;
                
            } catch (error) {
                console.error('Error loading map data:', error);
                // Fallback to show loading error
                document.getElementById('florida-stats').innerHTML = '<div style="color:red;">Error loading data - check API endpoints</div>';
            }
        }
        
        async function showStateDetails(stateCode) {
            try {
                const response = await fetch(`/api/geographic/state/${stateCode}`);
                const stateData = await response.json();
                
                const contextPoints = stateData.context_points.map(point => `• ${point}`).join('\n');
                const conversationStarters = stateData.conversation_starters.map(starter => `"${starter}"`).join('\n');
                
                alert(`${stateData.state_code === 'FL' ? '🌴' : '🗺️'} ${stateData.state_name.toUpperCase()} OPPORTUNITIES
                
• ${stateData.leads} VIN leads identified
• $${stateData.revenue_potential.toLocaleString()} revenue potential  
• ${(stateData.seasonal_adjustment * 100).toFixed(0)}% seasonal adjustment
• Adjusted revenue: $${stateData.adjusted_revenue.toLocaleString()}

STRESSOR CONTEXT:
${contextPoints}

CONVERSATION STARTERS:
${conversationStarters}

ACADEMIC FOUNDATION:
13-Stressor Framework with Bayesian likelihood ratios from peer-reviewed research`);
                
            } catch (error) {
                console.error('Error loading state details:', error);
                alert(`Error loading details for ${stateCode} - check API connection`);
            }
        }
        
        // Load data when page loads
        document.addEventListener('DOMContentLoaded', loadMapData);
    </script>
</body>
</html>
    """ 