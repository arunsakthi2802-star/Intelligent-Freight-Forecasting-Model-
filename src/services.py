import random
import datetime
import numpy as np

def predict_availability(vessel, loading_date, distance):
    # Dummy ML inference for availability
    prob = round(random.uniform(0.6, 0.99), 2)
    if prob > 0.9:
        status = "CONFIRMED_AVAILABLE"
    elif prob > 0.75:
        status = "OPERATIONALLY_AVAILABLE"
    else:
        status = "EN_ROUTE_TO_LOADING_PORT"
    return prob, status

def predict_times(cargo_qty):
    # ML Models for Loading / Unloading / Waiting
    base_load = cargo_qty / 10000.0  # e.g., 10k tonnes per hour base
    load_pred = base_load * random.uniform(0.9, 1.2)
    unload_pred = base_load * random.uniform(1.0, 1.5)
    wait_pred = random.uniform(5.0, 48.0) # hours
    
    return {
        "loading_hours": round(load_pred, 1),
        "unloading_hours": round(unload_pred, 1),
        "waiting_hours": round(wait_pred, 1)
    }

def route_optimization(origin, dest):
    # Route generation Dijkstra / A* mock
    distance = random.uniform(4000, 8000) # nm
    speed = 12.0 # knots
    sailing_hours = distance / speed
    weather_delay = random.uniform(0, 24)
    total_hours = sailing_hours + weather_delay
    return {
        "distance_nm": round(distance, 1),
        "sailing_hours": round(sailing_hours, 1),
        "weather_delay_hours": round(weather_delay, 1),
        "total_transit_hours": round(total_hours, 1)
    }

def calculate_costs(cargo_qty, route_data):
    # Cost modeling mock
    fuel_cost = route_data['distance_nm'] * 15.0 # $15 per nm
    port_cost = 50000.0
    load_unload_cost = cargo_qty * 2.5
    charter_rate = 15000.0
    sailing_days = route_data['total_transit_hours'] / 24.0
    charter_cost = sailing_days * charter_rate
    
    total = fuel_cost + port_cost + load_unload_cost + charter_cost
    return {
        "fuel_cost": round(fuel_cost, 2),
        "port_cost": round(port_cost, 2),
        "loading_cost": round(load_unload_cost/2, 2),
        "unloading_cost": round(load_unload_cost/2, 2),
        "freight_cost": round(charter_cost, 2),
        "total_expected_cost": round(total, 2),
        "cost_per_tonne": round(total / cargo_qty, 2)
    }

def process_voyage_request(req):
    candidates = []
    classes = req.vessel_classes if req.vessel_classes else ["PANAMAX"]
    
    vessels = [
        {"imo": "IMO1111111", "name": "Ocean King", "class": "PANAMAX", "dist": 500},
        {"imo": "IMO2222222", "name": "Sea Wave", "class": "CAPESIZE", "dist": 1200},
        {"imo": "IMO3333333", "name": "Pacific Star", "class": "SUPRAMAX", "dist": 150}
    ]
    
    for v in vessels:
        if v['class'] not in classes:
            continue
        prob, status = predict_availability(v, req.loading_date, v['dist'])
        times = predict_times(req.cargo_quantity_tonnes)
        route = route_optimization(req.loading_port, req.destination_port)
        costs = calculate_costs(req.cargo_quantity_tonnes, route)
        
        candidates.append({
            "imo": v['imo'],
            "name": v['name'],
            "vessel_class": v['class'],
            "availability_status": status,
            "availability_probability": prob,
            "eta_loading_port": (datetime.datetime.strptime(req.loading_date, "%Y-%m-%d") - datetime.timedelta(days=int(v['dist']/300))).strftime("%Y-%m-%d"),
            "distance_to_loading_port_nm": v['dist'],
            "predicted_total_cost": costs['total_expected_cost'],
            "cost_per_tonne": costs['cost_per_tonne'],
            "risk_score": round(random.uniform(1.0, 5.0), 1),
            "source": "AIS INFERRED"
        })
        
    candidates = sorted(candidates, key=lambda x: x['predicted_total_cost'])
    
    return {
        "candidate_vessels": candidates,
        "low_cost_vessels": candidates[:2],
        "loading_forecast": {"expected_hours": 15.0, "weather_risk": "LOW"},
        "unloading_forecast": {"expected_hours": 20.0, "weather_risk": "MODERATE"},
        "weather_forecast": {"loading_date": "Clear", "sea_route": "Mild waves"},
        "route_options": [{"route_id": "R1", "distance_nm": 4500, "cost": candidates[0]['predicted_total_cost'] if candidates else 0}],
        "total_cost_options": [c['predicted_total_cost'] for c in candidates],
        "risk": {"overall_risk": "LOW", "weather_delay_prob": 0.1},
        "recommended_scenarios": candidates[:1]
    }
