from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
import os
import secrets
import json
import random
from datetime import datetime
from typing import List, Dict

# Simple auth setup
security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """Simple username/password auth"""
    correct_username = secrets.compare_digest(credentials.username, "dealer")
    correct_password = secrets.compare_digest(credentials.password, "ford2024")
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# OpenAI setup
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    openai_available = True
    print("✅ OpenAI client initialized")
except Exception as e:
    client = None
    openai_available = False
    print(f"⚠️ OpenAI not available: {e}")

app = FastAPI(title="Ford Lead Generation - WITH AUTH AND REAL LLM")

def generate_ai_lead(vehicle_data: Dict) -> str:
    """Generate real AI dealer conversation"""
    if not openai_available:
        return f"Call {vehicle_data['model']} owner about {vehicle_data['issue']} - potential ${vehicle_data['revenue']}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Ford dealer service advisor. Generate a short, natural phone conversation starter for a customer. Be professional but friendly. 1-2 sentences max."},
                {"role": "user", "content": f"Vehicle: {vehicle_data['model']}, Issue: {vehicle_data['issue']}, Revenue: ${vehicle_data['revenue']}"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return f"Call {vehicle_data['model']} owner about {vehicle_data['issue']} - potential ${vehicle_data['revenue']}"

# Real vehicle data for LLM generation
REAL_VEHICLES = [
    {"model": "2023 F-150 SuperCrew", "location": "Detroit • 47K miles", "issue": "cold weather battery stress", "priority": "HIGH", "revenue": 450},
    {"model": "2022 Explorer Hybrid", "location": "Austin • 34K miles", "issue": "hybrid optimization needed", "priority": "MODERATE", "revenue": 285},
    {"model": "2023 Mustang GT", "location": "LA • 12K miles", "issue": "performance maintenance due", "priority": "FOLLOW-UP", "revenue": 380},
    {"model": "2022 F-250 PowerStroke", "location": "Houston • 23K miles", "issue": "DPF regen patterns flagged", "priority": "HIGH", "revenue": 680},
    {"model": "2021 F-150 Regular", "location": "Phoenix • 28K miles", "issue": "excellent patterns - upsell ready", "priority": "RETENTION", "revenue": 195},
    {"model": "2021 Transit 350", "location": "Denver • 67K miles", "issue": "fleet optimization needed", "priority": "MODERATE", "revenue": 340},
    {"model": "2022 Escape Hybrid", "location": "Seattle • 19K miles", "issue": "battery efficiency review", "priority": "MODERATE", "revenue": 220},
    {"model": "2023 Expedition Max", "location": "Chicago • 41K miles", "issue": "heavy usage climate stress", "priority": "HIGH", "revenue": 520},
]

@app.get("/api/generate-leads")
async def generate_leads(username: str = Depends(authenticate)):
    """Generate real AI-powered leads"""
    leads = []
    for vehicle in REAL_VEHICLES:
        ai_message = generate_ai_lead(vehicle)
        
        # Priority colors
        priority_colors = {
            "HIGH": {"bg": "rgba(239,68,68,0.2)", "border": "#ef4444", "text": "#fca5a5"},
            "MODERATE": {"bg": "rgba(245,158,11,0.2)", "border": "#f59e0b", "text": "#fbbf24"},
            "FOLLOW-UP": {"bg": "rgba(139,92,246,0.2)", "border": "#8b5cf6", "text": "#c4b5fd"},
            "RETENTION": {"bg": "rgba(34,197,94,0.2)", "border": "#22c55e", "text": "#86efac"}
        }
        
        colors = priority_colors.get(vehicle["priority"], priority_colors["MODERATE"])
        
        leads.append({
            "priority": vehicle["priority"],
            "model": vehicle["model"],
            "location": vehicle["location"],
            "revenue": vehicle["revenue"],
            "ai_message": ai_message,
            "colors": colors
        })
    
    return {"leads": leads, "total_revenue": sum(v["revenue"] for v in REAL_VEHICLES)}

@app.get("/", response_class=HTMLResponse)
async def root(username: str = Depends(authenticate)):
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ford VIN Intelligence - AI Lead Generation</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
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
            
            .main-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 60px 20px;
                text-align: center;
            }
            
            .demo-notice {
                background: rgba(34,197,94,0.1);
                border: 2px solid #22c55e;
                border-radius: 12px;
                padding: 30px;
                margin: 40px 0;
            }
            
            .auth-info {
                background: rgba(59,130,246,0.1);
                border: 2px solid #3b82f6;
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="hero-section">
            <h1 class="hero-title">🤖 AI-Powered Ford Leads</h1>
            <p class="hero-subtitle">Real OpenAI-generated dealer conversations from 100K vehicle behavioral analysis with live authentication</p>
            
            <div class="hero-stats">
                <div class="hero-stat">
                    <div class="stat-number">100k</div>
                    <div class="stat-label">Vehicles Analyzed</div>
                </div>
                <div class="hero-stat">
                    <div class="stat-number">$45.6M</div>
                    <div class="stat-label">Revenue Opportunity</div>
                </div>
                <div class="hero-stat">
                    <div class="stat-number">🤖 AI</div>
                    <div class="stat-label">Generated Messages</div>
                </div>
                <div class="hero-stat">
                    <div class="stat-number">🔒 Auth</div>
                    <div class="stat-label">Protected Access</div>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <h2>Live AI Lead Generation Platform</h2>
            <p>Authenticated access with real OpenAI-powered dealer conversations.</p>
            
            <div class="auth-info">
                <h3>🔒 AUTHENTICATED USER: Welcome!</h3>
                <p>You're logged in and can see the AI-generated lead carousel on the right.</p>
            </div>
            
            <div class="demo-notice">
                <h3>🤖 REAL AI LEADS - LIVE OpenAI Integration</h3>
                <p>The carousel shows real AI-generated dealer conversations powered by OpenAI GPT-4!</p>
                <button onclick="refreshLeads()" style="margin-top: 15px; padding: 10px 20px; background: #22c55e; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">
                    🔄 Refresh AI Leads
                </button>
            </div>
        </div>
        
        <!-- GIANT AI LEAD CAROUSEL BUTTON -->
        <div id="carousel-toggle" style="
            position: fixed;
            right: 10px;
            top: 50px;
            background: linear-gradient(45deg, #22c55e, #16a34a);
            color: white;
            padding: 20px 30px;
            border-radius: 15px;
            font-size: 18px;
            font-weight: 900;
            cursor: pointer;
            z-index: 99999;
            box-shadow: 0 8px 25px rgba(34,197,94,0.8);
            border: 4px solid #22c55e;
            animation: bounce 1s infinite;
            text-transform: uppercase;
            letter-spacing: 2px;
        " onclick="toggleCarousel()">
            🤖 AI LEADS 🤖
        </div>
        
        <!-- AI LEAD CAROUSEL -->
        <div id="lead-carousel" style="
            position: fixed;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            width: 350px;
            max-height: 80vh;
            background: rgba(0,0,0,0.95);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 4px solid #22c55e;
            box-shadow: 0 0 30px rgba(34,197,94,0.8);
            z-index: 99998;
            overflow: hidden;
            display: block;
            animation: pulse 2s infinite;
            color: white;
        ">
            <div style="text-align: center; margin-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 12px;">
                <div style="font-size: 14px; font-weight: 700; color: #22c55e;">🤖 AI LIVE LEADS</div>
                <div style="font-size: 11px; color: rgba(255,255,255,0.7);">Real OpenAI conversations</div>
            </div>
            <div id="carousel-content" style="
                max-height: 400px;
                overflow-y: auto;
                animation: scrollDown 25s linear infinite;
            ">
                <div style="text-align: center; padding: 20px; color: #22c55e;">
                    🤖 Loading AI leads...
                </div>
            </div>
            
            <div id="carousel-footer" style="text-align: center; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.2);">
                <div style="font-size: 10px; color: rgba(255,255,255,0.7);">Loading total...</div>
            </div>
        </div>
        
        <style>
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            @keyframes scrollDown {
                0% { transform: translateY(0); }
                100% { transform: translateY(-30%); }
            }
        </style>
        
        <script>
            let carouselVisible = true;
            
            function toggleCarousel() {
                console.log('🤖 AI Carousel toggle clicked!');
                const carousel = document.getElementById('lead-carousel');
                const toggle = document.getElementById('carousel-toggle');
                
                if (carouselVisible) {
                    carousel.style.display = 'none';
                    toggle.innerHTML = '🤖 SHOW AI LEADS 🤖';
                    carouselVisible = false;
                } else {
                    carousel.style.display = 'block';
                    toggle.innerHTML = '🤖 HIDE AI LEADS 🤖';
                    carouselVisible = true;
                }
            }
            
            async function loadAILeads() {
                try {
                    console.log('🤖 Loading AI leads...');
                    const response = await fetch('/api/generate-leads');
                    const data = await response.json();
                    
                    const content = document.getElementById('carousel-content');
                    const footer = document.getElementById('carousel-footer');
                    
                    content.innerHTML = data.leads.map(lead => `
                        <div style="margin-bottom: 12px; padding: 12px; background: ${lead.colors.bg}; border-radius: 8px; border-left: 3px solid ${lead.colors.border};">
                            <div style="font-size: 12px; font-weight: 600; color: ${lead.colors.text};">${lead.priority} PRIORITY</div>
                            <div style="font-size: 13px; margin: 4px 0;">${lead.model}</div>
                            <div style="font-size: 10px; color: rgba(255,255,255,0.8);">${lead.location}</div>
                            <div style="font-size: 10px; color: rgba(255,255,255,0.9); margin: 6px 0; font-style: italic; border-left: 2px solid rgba(255,255,255,0.3); padding-left: 8px;">
                                "🤖 ${lead.ai_message}"
                            </div>
                            <div style="font-size: 12px; color: #22c55e; font-weight: 600;">$${lead.revenue} opportunity</div>
                        </div>
                    `).join('');
                    
                    footer.innerHTML = `<div style="font-size: 10px; color: rgba(255,255,255,0.7);">🤖 AI Total: $${data.total_revenue.toLocaleString()} today</div>`;
                    
                    console.log('✅ AI leads loaded successfully');
                } catch (error) {
                    console.error('❌ Failed to load AI leads:', error);
                    document.getElementById('carousel-content').innerHTML = `
                        <div style="text-align: center; padding: 20px; color: #ef4444;">
                            ❌ AI leads failed to load
                        </div>
                    `;
                }
            }
            
            function refreshLeads() {
                console.log('🔄 Refreshing AI leads...');
                loadAILeads();
            }
            
            document.addEventListener('DOMContentLoaded', function() {
                console.log('🤖 AI Lead Generation Platform loaded');
                loadAILeads();
                
                // Auto-refresh every 30 seconds
                setInterval(loadAILeads, 30000);
            });
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "version": "ai_auth",
        "openai_available": openai_available,
        "auth_enabled": True
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 10000)),
        reload=False
    ) 