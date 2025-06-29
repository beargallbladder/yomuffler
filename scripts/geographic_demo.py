#!/usr/bin/env python3
"""
Ford VIN Intelligence - Geographic Visualization Demo

Demonstrates the new geographic mapping capabilities with:
- Florida opportunities spotlight
- Southeast region analysis
- Stressor context for professional conversations
- Revenue potential by state
"""

import requests
import json
from datetime import datetime

class GeographicDemo:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.auth = ("dealer", "stressors2024")
    
    def run_demo(self):
        """Run complete geographic demo"""
        print("\n🗺️  FORD VIN INTELLIGENCE - GEOGRAPHIC DEMO")
        print("=" * 60)
        
        self.demo_southeast_summary()
        self.demo_florida_spotlight()
        self.demo_state_details()
        self.demo_professional_usage()
    
    def demo_southeast_summary(self):
        """Demo Southeast region summary"""
        print("\n📊 SOUTHEAST REGION SUMMARY")
        print("-" * 40)
        
        try:
            response = requests.get(
                f"{self.base_url}/api/geographic/southeast-summary",
                auth=self.auth
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"Total VIN Leads: {data['total_leads']:,}")
                print(f"Revenue Potential: ${data['total_revenue_potential']:,.0f}")
                print(f"States Covered: {data['states_covered']}")
                
                # Florida spotlight
                florida = data.get('florida_spotlight', {})
                if florida:
                    print(f"\n🌴 FLORIDA SPOTLIGHT:")
                    print(f"  • Leads: {florida['leads']:,}")
                    print(f"  • Revenue: ${florida['revenue']:,.0f}")
                    print(f"  • Share: {florida['percentage_of_total']:.1f}% of total")
                
                print(f"\nAcademic Foundation: {data['academic_foundation']}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Demo error: {str(e)}")
    
    def demo_florida_spotlight(self):
        """Demo Florida-specific opportunities"""
        print("\n🌴 FLORIDA OPPORTUNITY SPOTLIGHT")
        print("-" * 40)
        
        try:
            response = requests.get(
                f"{self.base_url}/api/geographic/florida-spotlight",
                auth=self.auth
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"State: {data['state']}")
                
                # Highlights
                highlights = data['highlights']
                print(f"\n🔥 EXTREME ENVIRONMENT HIGHLIGHTS:")
                for key, value in highlights.items():
                    print(f"  • {key.replace('_', ' ').title()}: {value}")
                
                # Opportunities
                opportunities = data['opportunities']
                print(f"\n💰 REVENUE OPPORTUNITIES:")
                print(f"  • Total Leads: {opportunities['total_leads']:,}")
                print(f"  • Revenue Potential: ${opportunities['revenue_potential']:,.0f}")
                print(f"  • Average per Lead: ${opportunities['average_per_lead']:,.0f}")
                print(f"  • Summer Multiplier: {opportunities['seasonal_multiplier']}x")
                
                # Conversation starters
                print(f"\n💬 PROFESSIONAL CONVERSATION STARTERS:")
                for starter in data['conversation_starters']:
                    print(f"  • \"{starter}\"")
                
                # Technical context
                technical = data['technical_context']
                print(f"\n📚 TECHNICAL FOUNDATION:")
                for key, value in technical.items():
                    print(f"  • {key.replace('_', ' ').title()}: {value}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Demo error: {str(e)}")
    
    def demo_state_details(self):
        """Demo individual state analysis"""
        print("\n🏛️  STATE-BY-STATE ANALYSIS")
        print("-" * 40)
        
        states_to_demo = ['FL', 'GA', 'TN']
        
        for state in states_to_demo:
            try:
                response = requests.get(
                    f"{self.base_url}/api/geographic/state/{state}",
                    auth=self.auth
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"\n{data['state_name']} ({state}):")
                    print(f"  • Coordinates: {data['coordinates']['lat']:.2f}, {data['coordinates']['lng']:.2f}")
                    print(f"  • Leads: {data['leads']:,}")
                    print(f"  • Revenue: ${data['revenue_potential']:,.0f}")
                    print(f"  • Seasonal Adjustment: {data['seasonal_adjustment']:.1f}x")
                    print(f"  • Adjusted Revenue: ${data['adjusted_revenue']:,.0f}")
                    
                    # Show top context points
                    print(f"  • Key Context Points:")
                    for point in data['context_points'][:2]:
                        print(f"    - {point}")
                
            except Exception as e:
                print(f"❌ Error for {state}: {str(e)}")
    
    def demo_professional_usage(self):
        """Demo professional usage scenarios"""
        print("\n💼 PROFESSIONAL USAGE SCENARIOS")
        print("-" * 40)
        
        scenarios = [
            {
                'title': 'Customer with No Active DTCs',
                'context': 'Vehicle shows no current alerts but operates in Florida',
                'talking_points': [
                    'Your vehicle operates in one of the most challenging thermal environments',
                    'Florida heat patterns show 2.3x higher battery failure rates in summer',
                    'Proactive maintenance timing can prevent costly emergency repairs'
                ]
            },
            {
                'title': 'Existing DTC P0562 (System Voltage Low)',
                'context': 'Customer has charging system alert in Southeast region',
                'talking_points': [
                    'Your location shows elevated electrical system stress patterns',
                    'Southeast humidity accelerates terminal corrosion by 4x',
                    'Government weather data confirms extreme thermal cycling'
                ]
            },
            {
                'title': 'Seasonal Service Planning',
                'context': 'Summer approaching in Southeast region',
                'talking_points': [
                    'Heat wave season activates 847 battery opportunities in Florida alone',
                    'Academic research validates proactive summer maintenance timing',
                    '$289,420 in preventable failures across Florida market'
                ]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n📋 {scenario['title']}")
            print(f"Context: {scenario['context']}")
            print("Professional Talking Points:")
            for point in scenario['talking_points']:
                print(f"  • \"{point}\"")
    
    def demo_map_access(self):
        """Show how to access the visual map"""
        print("\n🗺️  VISUAL MAP ACCESS")
        print("-" * 40)
        
        print("Interactive Map Available At:")
        print(f"📍 {self.base_url}/map")
        print("\nFeatures:")
        print("  • Interactive US map with Southeast focus")
        print("  • Florida opportunities highlighted")
        print("  • State-by-state revenue breakdown")
        print("  • Professional stressor context")
        print("  • Academic foundation display")
        print("  • Responsive design for all devices")

def main():
    """Run the geographic demo"""
    demo = GeographicDemo()
    
    try:
        # Check if server is running
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running - proceeding with demo")
            demo.run_demo()
            demo.demo_map_access()
            
            print("\n" + "=" * 60)
            print("🌟 DEMO COMPLETE!")
            print("Visit http://localhost:8000/map for interactive visualization")
            print("=" * 60)
            
        else:
            print("❌ Server not responding properly")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python3 start_production.py")
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")

if __name__ == "__main__":
    main() 