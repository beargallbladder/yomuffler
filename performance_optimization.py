#!/usr/bin/env python3
"""
Performance Optimization Module for Ford Dealer Portal
Fixes 10+ second lead generation delay with caching and parallel processing
"""

import asyncio
import json
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import concurrent.futures
from threading import Lock
import os

# In-memory cache for AI messages
ai_message_cache = {}
cache_lock = Lock()
cache_expiry = {}

# Performance metrics
performance_metrics = {
    "cache_hits": 0,
    "cache_misses": 0,
    "total_requests": 0,
    "avg_response_time": 0,
    "last_optimization": datetime.now().isoformat()
}

class PerformanceOptimizer:
    def __init__(self):
        self.cache_duration = 3600  # 1 hour cache
        self.fallback_messages = self._load_fallback_messages()
        
    def _load_fallback_messages(self) -> Dict[str, str]:
        """Pre-generated high-quality fallback messages"""
        return {
            "HIGH_PRIORITY": "Hi, this is [Service Advisor] from [Ford Dealer]. Our advanced diagnostics show your {model} has {primary_stressor} patterns putting you in the {cohort_percentile}th percentile of similar vehicles. We'd like to schedule a complimentary inspection to prevent potential issues. Can we set up a time this week?",
            
            "MODERATE_PRIORITY": "Hi, this is [Service Advisor] from [Ford Dealer]. Our analysis of your {model} shows {primary_stressor} patterns that suggest some preventive maintenance could benefit you. We have some recommendations based on your vehicle's usage. Would you be interested in scheduling a consultation?",
            
            "FOLLOW_UP": "Hi, this is [Service Advisor] from [Ford Dealer]. Our performance analysis shows your {model} has {primary_stressor} patterns that are worth monitoring. We'd like to discuss some optimization options that could enhance your vehicle's performance. Can we schedule a follow-up?",
            
            "RETENTION": "Hi, this is [Service Advisor] from [Ford Dealer]. Our analysis shows your {model} is performing excellently with {primary_stressor}. We'd like to discuss how to maintain this great performance and potentially extend your vehicle's life. Would you be interested in our premium maintenance program?"
        }
    
    def get_cache_key(self, vehicle_data: Dict) -> str:
        """Generate cache key for vehicle data"""
        return f"{vehicle_data['model']}_{vehicle_data['priority']}_{vehicle_data['stressor_score']}"
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in cache_expiry:
            return False
        return datetime.now() < cache_expiry[cache_key]
    
    def get_cached_message(self, vehicle_data: Dict) -> Optional[str]:
        """Get cached AI message if available and valid"""
        cache_key = self.get_cache_key(vehicle_data)
        
        with cache_lock:
            if cache_key in ai_message_cache and self.is_cache_valid(cache_key):
                performance_metrics["cache_hits"] += 1
                return ai_message_cache[cache_key]
            
            performance_metrics["cache_misses"] += 1
            return None
    
    def cache_message(self, vehicle_data: Dict, message: str):
        """Cache AI message with expiration"""
        cache_key = self.get_cache_key(vehicle_data)
        expiry_time = datetime.now() + timedelta(seconds=self.cache_duration)
        
        with cache_lock:
            ai_message_cache[cache_key] = message
            cache_expiry[cache_key] = expiry_time
    
    def get_fallback_message(self, vehicle_data: Dict) -> str:
        """Get high-quality fallback message"""
        priority = vehicle_data.get("priority", "MODERATE")
        template = self.fallback_messages.get(f"{priority}_PRIORITY", 
                                              self.fallback_messages["MODERATE_PRIORITY"])
        
        return template.format(
            model=vehicle_data.get("model", "your Ford vehicle"),
            primary_stressor=vehicle_data.get("primary_stressor", "usage patterns"),
            cohort_percentile=vehicle_data.get("cohort_percentile", 75)
        )
    
    async def generate_ai_message_async(self, vehicle_data: Dict, openai_client=None) -> str:
        """Generate AI message asynchronously with fallback"""
        # Check cache first
        cached_message = self.get_cached_message(vehicle_data)
        if cached_message:
            return cached_message
        
        # If OpenAI not available, use fallback
        if not openai_client:
            message = self.get_fallback_message(vehicle_data)
            self.cache_message(vehicle_data, message)
            return message
        
        # Generate with OpenAI
        try:
            prompt = f"""Generate what a Ford dealer service advisor should SAY TO THE CUSTOMER on the phone:

            CUSTOMER'S VEHICLE: {vehicle_data['model']} 
            TECHNICAL FINDINGS: {vehicle_data['primary_stressor']} in {vehicle_data['cohort_percentile']}th percentile
            
            Generate exact words (2-3 sentences max):
            1. Dealer introduces themselves
            2. Mentions specific findings about their vehicle
            3. Suggests proactive maintenance
            4. Asks to schedule service
            
            Start with "Hi, this is [Your Name] from [Dealer Name]..."
            """
            
            response = await asyncio.to_thread(
                openai_client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Generate dealer phone script to customer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            message = response.choices[0].message.content.strip()
            self.cache_message(vehicle_data, message)
            return message
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            message = self.get_fallback_message(vehicle_data)
            self.cache_message(vehicle_data, message)
            return message
    
    async def generate_all_leads_parallel(self, vehicles: List[Dict], openai_client=None) -> List[Dict]:
        """Generate all leads in parallel with performance optimization"""
        start_time = time.time()
        performance_metrics["total_requests"] += 1
        
        # Generate all AI messages in parallel
        tasks = [self.generate_ai_message_async(vehicle, openai_client) for vehicle in vehicles]
        ai_messages = await asyncio.gather(*tasks)
        
        # Build lead responses
        leads = []
        priority_colors = {
            "HIGH": {"bg": "rgba(239,68,68,0.2)", "border": "#ef4444", "text": "#fca5a5"},
            "MODERATE": {"bg": "rgba(245,158,11,0.2)", "border": "#f59e0b", "text": "#fbbf24"},
            "FOLLOW-UP": {"bg": "rgba(139,92,246,0.2)", "border": "#8b5cf6", "text": "#c4b5fd"},
            "RETENTION": {"bg": "rgba(34,197,94,0.2)", "border": "#22c55e", "text": "#86efac"}
        }
        
        for i, vehicle in enumerate(vehicles):
            colors = priority_colors.get(vehicle["priority"], priority_colors["MODERATE"])
            
            leads.append({
                "priority": vehicle["priority"],
                "model": vehicle["model"],
                "location": vehicle["location"],
                "revenue": vehicle["revenue"],
                "ai_message": ai_messages[i],
                "colors": colors,
                "stressor_score": vehicle["stressor_score"],
                "cohort_percentile": vehicle["cohort_percentile"],
                "primary_stressor": vehicle["primary_stressor"],
                "cohort_size": vehicle["cohort_size"],
                "confidence": vehicle["confidence"],
                "academic_basis": vehicle["academic_basis"]
            })
        
        # Update performance metrics
        end_time = time.time()
        response_time = end_time - start_time
        performance_metrics["avg_response_time"] = (
            performance_metrics["avg_response_time"] + response_time
        ) / 2
        
        return leads
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        total_cache_attempts = performance_metrics["cache_hits"] + performance_metrics["cache_misses"]
        cache_hit_rate = (performance_metrics["cache_hits"] / total_cache_attempts * 100) if total_cache_attempts > 0 else 0
        
        return {
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "total_requests": performance_metrics["total_requests"],
            "avg_response_time": f"{performance_metrics['avg_response_time']:.2f}s",
            "cached_entries": len(ai_message_cache),
            "last_optimization": performance_metrics["last_optimization"]
        }
    
    def preload_common_leads(self, vehicles: List[Dict]):
        """Preload common lead messages for instant response"""
        print("🚀 Preloading common lead messages...")
        
        for vehicle in vehicles:
            # Generate and cache fallback message
            fallback_message = self.get_fallback_message(vehicle)
            self.cache_message(vehicle, fallback_message)
        
        print(f"✅ Preloaded {len(vehicles)} lead messages")
    
    def clear_expired_cache(self):
        """Clear expired cache entries"""
        now = datetime.now()
        expired_keys = []
        
        with cache_lock:
            for cache_key, expiry_time in cache_expiry.items():
                if now >= expiry_time:
                    expired_keys.append(cache_key)
            
            for key in expired_keys:
                ai_message_cache.pop(key, None)
                cache_expiry.pop(key, None)
        
        if expired_keys:
            print(f"🧹 Cleared {len(expired_keys)} expired cache entries")

# Global optimizer instance
optimizer = PerformanceOptimizer()

def optimize_lead_generation():
    """Main optimization function"""
    print("⚡ PERFORMANCE OPTIMIZATION ACTIVE")
    print("📊 Features:")
    print("  • In-memory caching (1 hour TTL)")
    print("  • Parallel AI message generation")
    print("  • High-quality fallback messages")
    print("  • Performance metrics tracking")
    print("  • Automatic cache cleanup")
    
    return optimizer 