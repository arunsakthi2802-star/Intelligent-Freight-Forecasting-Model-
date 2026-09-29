import pandas as pd
import numpy as np
import networkx as nx
from .logger import get_logger
import os

logger = get_logger("voyage_optimizer")

def build_maritime_graph():
    """
    Builds a simplified global maritime routing graph.
    Nodes are major ports or waypoints (like canals).
    Edges contain distances in km and risk multipliers.
    """
    G = nx.Graph()
    
    # Define major ports & waypoints
    ports = ["INMAA", "AEDXB", "CNSHA", "USLAX", "NLRTM", "SGSIN", "EGSUZ", "PAPAN"]
    G.add_nodes_from(ports)
    
    # Add routes with (distance_km, weather_risk)
    routes = [
        ("CNSHA", "SGSIN", {"dist": 3800, "risk": 1.1}),
        ("SGSIN", "INMAA", {"dist": 2900, "risk": 1.0}),
        ("INMAA", "AEDXB", {"dist": 2700, "risk": 1.0}),
        ("AEDXB", "EGSUZ", {"dist": 5000, "risk": 1.05}),
        ("EGSUZ", "NLRTM", {"dist": 6000, "risk": 1.2}),
        ("CNSHA", "USLAX", {"dist": 10500, "risk": 1.15}),
        ("USLAX", "PAPAN", {"dist": 4800, "risk": 1.0}),
        ("PAPAN", "NLRTM", {"dist": 7500, "risk": 1.1}),
        ("SGSIN", "EGSUZ", {"dist": 8300, "risk": 1.2})
    ]
    G.add_edges_from(routes)
    return G

def calculate_voyage_cost(distance, vessel_speed_kmh, capacity_teu, fuel_price_usd_ton):
    """
    Estimates total voyage cost.
    Cost = Fuel Cost + Fixed Daily Charter + Port Handling (Load/Unload)
    """
    duration_hours = distance / vessel_speed_kmh
    duration_days = duration_hours / 24
    
    # Fuel consumption approximation: scales with capacity and square of speed
    fuel_tons_per_day = (capacity_teu / 1000) * (vessel_speed_kmh / 20)**2 * 10
    total_fuel_cost = fuel_tons_per_day * duration_days * fuel_price_usd_ton
    
    # Daily operating/charter cost
    daily_cost = 10000 + (capacity_teu * 3)
    total_charter = daily_cost * duration_days
    
    # Port Load/Unload cost ($150 per TEU total for both ends)
    port_handling = capacity_teu * 150
    
    total_cost = total_fuel_cost + total_charter + port_handling
    return total_cost, duration_days

def predict_lowest_cost_route(origin, destination, capacity_teu, fuel_price):
    G = build_maritime_graph()
    
    if origin not in G or destination not in G:
        logger.error(f"Origin {origin} or Destination {destination} not in routing network.")
        return None
        
    logger.info(f"Calculating Shortest Route & Lowest Cost from {origin} to {destination} for {capacity_teu} TEU vessel...")
    
    # 1. Shortest Route Prediction (Dijkstra)
    try:
        path = nx.dijkstra_path(G, origin, destination, weight='dist')
        total_dist = nx.dijkstra_path_length(G, origin, destination, weight='dist')
    except nx.NetworkXNoPath:
        logger.error("No valid maritime route found.")
        return None
        
    logger.info(f"Shortest Route Predicted: {' -> '.join(path)} (Distance: {total_dist} km)")
    
    # 2. Cost Estimation across different speeds (Slow Steaming vs Fast)
    speeds_kmh = [25.0, 30.0, 35.0, 40.0]
    speed_profiles = ["Eco Slow", "Standard", "Fast", "Express"]
    
    results = []
    for speed, profile in zip(speeds_kmh, speed_profiles):
        cost, days = calculate_voyage_cost(total_dist, speed, capacity_teu, fuel_price)
        results.append({
            'Route': ' -> '.join(path),
            'Distance_km': total_dist,
            'Speed_Profile': profile,
            'Speed_kmh': speed,
            'Duration_Days': round(days, 2),
            'Total_Cost_USD': round(cost, 2),
            'Cost_per_TEU': round(cost / capacity_teu, 2)
        })
        
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values(by='Total_Cost_USD')
    
    best = df_results.iloc[0]
    logger.info(f"Lowest Cost Prediction: {best['Speed_Profile']} Speed at ${best['Total_Cost_USD']:,.2f} total (${best['Cost_per_TEU']:,.2f}/TEU). Duration: {best['Duration_Days']} days.")
    
    os.makedirs('predictions', exist_ok=True)
    out_path = 'predictions/voyage_cost_predictions.csv'
    df_results.to_csv(out_path, index=False)
    logger.info(f"Full cost matrix saved to {out_path}")
    
    return df_results

if __name__ == "__main__":
    predict_lowest_cost_route("CNSHA", "NLRTM", 15000, 600)
