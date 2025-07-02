from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CAROUSEL TEST - NO AUTH</title>
        <style>
            body { background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%); margin: 0; padding: 20px; color: white; font-family: Arial, sans-serif; }
            .main { text-align: center; padding: 50px; }
        </style>
    </head>
    <body>
        <div class="main">
            <h1>🎯 CAROUSEL TEST - NO AUTHENTICATION REQUIRED</h1>
            <p>If you can see this page, the carousel should be visible on the right side!</p>
        </div>
        
        <!-- Toggle Button for Lead Carousel -->
        <div id="carousel-toggle" style="
            position: fixed;
            right: 20px;
            top: 20px;
            background: linear-gradient(45deg, #22c55e, #16a34a);
            color: white;
            padding: 12px 16px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(34,197,94,0.4);
            border: 2px solid rgba(34,197,94,0.8);
            animation: pulse 2s infinite;
        " onclick="toggleCarousel()">
            💰 LIVE LEADS
        </div>
        
        <!-- Lead Carousel -->
        <div id="lead-carousel" style="
            position: fixed;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            width: 300px;
            max-height: 70vh;
            background: rgba(0,0,0,0.9);
            border-radius: 12px;
            padding: 16px;
            border: 2px solid rgba(34,197,94,0.5);
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            z-index: 9999;
            overflow: hidden;
            display: block;
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
                <div style="margin-bottom: 12px; padding: 12px; background: rgba(34,197,94,0.2); border-radius: 8px; border-left: 3px solid #22c55e;">
                    <div style="font-size: 12px; font-weight: 600; color: #86efac;">RETENTION</div>
                    <div style="font-size: 13px; margin: 4px 0;">2021 F-150 Regular</div>
                    <div style="font-size: 10px; color: rgba(255,255,255,0.8);">Phoenix • 28K miles</div>
                    <div style="font-size: 12px; color: #22c55e; font-weight: 600;">$195 opportunity</div>
                </div>
            </div>
        </div>
        
        <style>
            @keyframes scrollDown {
                0% { transform: translateY(0); }
                100% { transform: translateY(-50%); }
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
        </style>
        
        <script>
            function toggleCarousel() {
                const carousel = document.getElementById('lead-carousel');
                const toggle = document.getElementById('carousel-toggle');
                
                if (carousel.style.display === 'none') {
                    carousel.style.display = 'block';
                    toggle.innerHTML = '💰 HIDE LEADS';
                } else {
                    carousel.style.display = 'none';
                    toggle.innerHTML = '💰 SHOW LEADS';
                }
            }
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 