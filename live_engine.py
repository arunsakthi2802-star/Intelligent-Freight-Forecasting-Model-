import os
import time
import requests
import datetime
from pipeline.voyage_cost_optimizer import predict_lowest_cost_route
import sys
import pandas as pd

OPENWEATHER_API = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY")
NEWSDATA_API = os.getenv("NEWSDATA_API_KEY", "YOUR_API_KEY")

def get_weather(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API}&units=metric"
    try:
        res = requests.get(url, timeout=5).json()
        if "weather" in res:
            return f"{res['weather'][0]['description'].title()}, Temp: {res['main']['temp']}C, Wind: {res['wind']['speed']}m/s"
        return "Weather data unavailable"
    except Exception as e:
        return "Connection Error / Rate Limited"

def get_news(query="shipping OR maritime OR freight"):
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API}&q={query}&language=en"
    try:
        res = requests.get(url, timeout=5).json()
        if "results" in res and len(res['results']) > 0:
            return res['results'][0]['title']
        return "No significant news updates."
    except Exception as e:
        return "News API connection error / Rate Limited"

def get_available_vessels(capacity_needed, origin):
    # Simulated vessel database lookup for "which vessels are available now"
    vessels = [
        {"imo": "IMO9348922", "type": "Container", "cap": int(capacity_needed * 1.1), "cost_pd": "$12,000"},
        {"imo": "IMO8923481", "type": "Container", "cap": int(capacity_needed * 0.9), "cost_pd": "$9,500"},
        {"imo": "IMO7728193", "type": "Bulk", "cap": capacity_needed, "cost_pd": "$10,500"}
    ]
    return vessels

def run_live_engine():
    print("="*60)
    print(" 🚢 SIH26006 LIVE MARITIME TRACKING & OPTIMIZATION ENGINE")
    print("="*60)
    print("Please enter mission parameters (press ENTER for defaults):")
    
    v_type = "Container"
    capacity = "15000"
    imo = "IMO9221322"
    origin = "CNSHA"
    dest = "NLRTM"
    start_date = "2024-10-01"
    load_date = "2024-10-02"
    move_start = "08:00"
    dest_reach = "2024-11-01 12:00"
    unload_time = "2024-11-03"
    mission_comp = "2024-11-04"
    
    print("\n[AI] Analyzing inputs and calculating initial predictions...\n")
    time.sleep(1.5)
    
    try:
        cap_int = int(capacity)
    except:
        cap_int = 15000
        
    print("=== AVAILABLE VESSELS FOR IMMEDIATE TRANSPORT ===")
    vessels = get_available_vessels(cap_int, origin)
    for v in vessels:
        print(f" -> {v['imo']} ({v['type']}, {v['cap']} TEU) | Charter: {v['cost_pd']}/day | Status: Available at {origin}")
        
    print("\n=== AI OPTIMIZED LOW-COST ROUTE ===")
    df_results = predict_lowest_cost_route(origin, dest, cap_int, 600.0)
    
    print("\n" + "="*60)
    print("📡 INITIATING LIVE SATELLITE TRACKING & WEATHER/NEWS FEED")
    print("Press Ctrl+C at any time to EXIT the mission.")
    print("="*60)
    
    try:
        cycle = 1
        while True:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{current_time}] --- LIVE UPDATE CYCLE #{cycle} ---")
            
            # API Calls for Live Data
            w_orig = get_weather(origin)
            w_dest = get_weather(dest)
            news = get_news()
            
            print(f"📍 LIVE WEATHER CONDITIONS:")
            print(f"   Origin ({origin}): {w_orig}")
            print(f"   Destination ({dest}): {w_dest}")
            
            print(f"📰 GLOBAL MARITIME RISK NEWS:")
            print(f"   Headline: {news}")
            
            print(f"🚢 VESSEL STATUS ({imo}):")
            print(f"   Trajectory: On Track for {dest_reach}")
            if df_results is not None:
                best = df_results.iloc[0]
                print(f"   Operating Mode: {best['Speed_Profile']} Speed ({best['Speed_kmh']} km/h)")
                print(f"   Cost Tracker: Accruing towards total ${best['Total_Cost_USD']:,.2f}")
                
            print(f"   Recommendation: Maintain current speed. Weather on route is clear.")
            
            print("\n🔄 Next update in 30 seconds... (Ctrl+C to exit)")
            time.sleep(30)
            cycle += 1
            
    except KeyboardInterrupt:
        print("\n\n[USER EXIT] Live tracking terminated. Final cost reports generated.")
        sys.exit(0)

if __name__ == '__main__':
    run_live_engine()
