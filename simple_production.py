from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI(title="Ford Lead Generation - SIMPLE VERSION")

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ford VIN Intelligence - 100k Vehicle Analysis v3.0</title>
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
        </style>
    </head>
    <body>
        <div class="hero-section">
            <h1 class="hero-title">Ford VIN Intelligence</h1>
            <p class="hero-subtitle">100,000 vehicles analyzed across 5 regions with academic-backed stressor analysis and predictive intelligence for proactive dealer engagement</p>
            
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
                    <div class="stat-number">48%</div>
                    <div class="stat-label">DTC Integration</div>
                </div>
                <div class="hero-stat">
                    <div class="stat-number">5</div>
                    <div class="stat-label">Regions Covered</div>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <h2>Lead Generation Platform</h2>
            <p>This is the simplified version showing the lead carousel functionality.</p>
            
            <div class="demo-notice">
                <h3>🎯 WORKING DEMO - NO AUTHENTICATION REQUIRED</h3>
                <p>The giant red bouncing button on the right shows live dealer leads!</p>
            </div>
        </div>
        
        <!-- GIANT IMPOSSIBLE TO MISS CAROUSEL BUTTON -->
        <div id="carousel-toggle" style="
            position: fixed;
            right: 10px;
            top: 50px;
            background: linear-gradient(45deg, #ff0000, #ff4444);
            color: white;
            padding: 20px 30px;
            border-radius: 15px;
            font-size: 18px;
            font-weight: 900;
            cursor: pointer;
            z-index: 99999;
            box-shadow: 0 8px 25px rgba(255,0,0,0.8);
            border: 4px solid #ff0000;
            animation: bounce 1s infinite;
            text-transform: uppercase;
            letter-spacing: 2px;
        " onclick="toggleCarousel()">
            🚨 CLICK ME - LEADS 🚨
        </div>
        
        <!-- GIANT OBVIOUS LEAD CAROUSEL -->
        <div id="lead-carousel" style="
            position: fixed;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            width: 320px;
            max-height: 80vh;
            background: rgba(0,0,0,0.95);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 4px solid #ff0000;
            box-shadow: 0 0 30px rgba(255,0,0,0.8);
            z-index: 99998;
            overflow: hidden;
            display: block;
            animation: pulse 2s infinite;
            color: white;
        ">
            <div style="text-align: center; margin-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 12px;">
                <div style="font-size: 14px; font-weight: 700; color: #22c55e;">💰 LIVE LEADS</div>
                <div style="font-size: 11px; color: rgba(255,255,255,0.7);">Real dealer dashboard</div>
            </div>
            <div style="max-height: 400px; overflow-y: auto; animation: scrollDown 20s linear infinite;">
                <div style="margin-bottom: 12px; padding: 12px; background: rgba(239,68,68,0.2); border-radius: 8px; border-left: 3px solid #ef4444;">
                    <div style="font-size: 12px; font-weight: 600; color: #fca5a5;">HIGH PRIORITY</div>
                    <div style="font-size: 13px; margin: 4px 0;">2023 F-150 SuperCrew</div>
                    <div style="font-size: 10px; color: rgba(255,255,255,0.8);">Detroit • 47K miles</div>
                    <div style="font-size: 12px; color: #22c55e; font-weight: 600;">$450 opportunity</div>
                </div>
                <div style="margin-bottom: 12px; padding: 12px; background: rgba(245,158,11,0.2); border-radius: 8px; border-left: 3px solid #f59e0b;">
                    <div style="font-size: 12px; font-weight: 600; color: #fbbf24;">MODERATE</div>
                    <div style="font-size: 13px; margin: 4px 0;">2022 Explorer Hybrid</div>
                    <div style="font-size: 10px; color: rgba(255,255,255,0.8);">Austin • 34K miles</div>
                    <div style="font-size: 12px; color: #22c55e; font-weight: 600;">$285 opportunity</div>
                </div>
                <div style="margin-bottom: 12px; padding: 12px; background: rgba(139,92,246,0.2); border-radius: 8px; border-left: 3px solid #8b5cf6;">
                    <div style="font-size: 12px; font-weight: 600; color: #c4b5fd;">FOLLOW-UP</div>
                    <div style="font-size: 13px; margin: 4px 0;">2023 Mustang GT</div>
                    <div style="font-size: 10px; color: rgba(255,255,255,0.8);">LA • 12K miles</div>
                    <div style="font-size: 12px; color: #22c55e; font-weight: 600;">$380 opportunity</div>
                </div>
                <div style="margin-bottom: 12px; padding: 12px; background: rgba(239,68,68,0.2); border-radius: 8px; border-left: 3px solid #ef4444;">
                    <div style="font-size: 12px; font-weight: 600; color: #fca5a5;">HIGH PRIORITY</div>
                    <div style="font-size: 13px; margin: 4px 0;">2022 F-250 PowerStroke</div>
                    <div style="font-size: 10px; color: rgba(255,255,255,0.8);">Houston • 23K miles</div>
                    <div style="font-size: 12px; color: #22c55e; font-weight: 600;">$680 opportunity</div>
                </div>
                <div style="margin-bottom: 12px; padding: 12px; background: rgba(34,197,94,0.2); border-radius: 8px; border-left: 3px solid #22c55e;">
                    <div style="font-size: 12px; font-weight: 600; color: #86efac;">RETENTION</div>
                    <div style="font-size: 13px; margin: 4px 0;">2021 F-150 Regular</div>
                    <div style="font-size: 10px; color: rgba(255,255,255,0.8);">Phoenix • 28K miles</div>
                    <div style="font-size: 12px; color: #22c55e; font-weight: 600;">$195 opportunity</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.2);">
                <div style="font-size: 10px; color: rgba(255,255,255,0.7);">Total: $1,990 today</div>
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
                100% { transform: translateY(-50%); }
            }
        </style>
        
        <script>
            function toggleCarousel() {
                console.log('🚨 SIMPLE Carousel toggle clicked!');
                const carousel = document.getElementById('lead-carousel');
                const toggle = document.getElementById('carousel-toggle');
                
                if (carousel.style.display === 'none') {
                    carousel.style.display = 'block';
                    toggle.innerHTML = '🚨 HIDE LEADS 🚨';
                } else {
                    carousel.style.display = 'none';
                    toggle.innerHTML = '🚨 CLICK ME - LEADS 🚨';
                }
            }
            
            document.addEventListener('DOMContentLoaded', function() {
                console.log('🚨 SIMPLE PAGE LOADED - CAROUSEL SHOULD BE VISIBLE');
            });
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "simple"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 10000)),
        reload=False
    ) 