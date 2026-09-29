import pandas as pd
import numpy as np
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
from .logger import get_logger

logger = get_logger()

def route_optimization(predicted_freight):
    """
    Simulates a Route Optimization engine using Dijkstra / A* or OR-Tools.
    This function assigns vessels to routes to maximize profit (Predicted Freight Rate - Route Cost).
    """
    logger.info("Starting Vessel Routing & Logistics Optimization (CP-SAT)...")
    
    # In a real scenario, this would come from a vessel characteristics dataset
    vessels = [
        {'id': 'V1', 'capacity_teu': 10000, 'daily_cost': 50000},
        {'id': 'V2', 'capacity_teu': 15000, 'daily_cost': 70000},
        {'id': 'V3', 'capacity_teu': 5000,  'daily_cost': 30000}
    ]
    
    # Process predicted freight routes
    routes = []
    for _, row in predicted_freight.iterrows():
        # Using predicted_freight_rate_usd as the reward per TEU
        reward = row.get('predicted_freight_rate_usd', 0)
        route_name = f"{row.get('origin_port', 'UNKNOWN')}_{row.get('destination_port', 'UNKNOWN')}"
        routes.append({
            'name': route_name,
            'reward_per_teu': reward,
            'demand_teu': np.random.randint(2000, 20000) # Mock demand for planning
        })
        
    model = cp_model.CpModel()
    
    # Variables: assign[v, r] = 1 if vessel v is assigned to route r
    assign = {}
    for v_idx, v in enumerate(vessels):
        for r_idx, r in enumerate(routes):
            assign[(v_idx, r_idx)] = model.NewBoolVar(f'assign_v{v_idx}_r{r_idx}')
            
    # Constraint 1: Each vessel can only be assigned to at most one route
    for v_idx in range(len(vessels)):
        model.AddAtMostOne(assign[(v_idx, r_idx)] for r_idx in range(len(routes)))
        
    # Constraint 2: Each route can have at most one vessel (for simplicity)
    for r_idx in range(len(routes)):
        model.AddAtMostOne(assign[(v_idx, r_idx)] for v_idx in range(len(vessels)))
        
    # Objective: Maximize Profit
    # Profit = (Assigned Vessel Capacity * Reward per TEU) - Vessel Cost
    profit_expr = []
    for v_idx, v in enumerate(vessels):
        for r_idx, r in enumerate(routes):
            capacity = v['capacity_teu']
            reward = routes[r_idx]['reward_per_teu']
            cost = v['daily_cost']
            
            # Simple profit calculation per trip
            trip_profit = int((capacity * reward) - cost)
            profit_expr.append(trip_profit * assign[(v_idx, r_idx)])
            
    model.Maximize(sum(profit_expr))
    
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    plan = []
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        logger.info(f"Optimization successful! Total Max Profit: ${solver.ObjectiveValue():,.2f}")
        for v_idx, v in enumerate(vessels):
            for r_idx, r in enumerate(routes):
                if solver.Value(assign[(v_idx, r_idx)]):
                    logger.info(f"Assigned Vessel {v['id']} to Route {routes[r_idx]['name']}")
                    plan.append({
                        'Vessel': v['id'],
                        'Route': routes[r_idx]['name'],
                        'Capacity': v['capacity_teu'],
                        'Predicted_Rate': routes[r_idx]['reward_per_teu']
                    })
    else:
        logger.warning("No optimal solution found for logistics planning.")
        
    plan_df = pd.DataFrame(plan)
    if not plan_df.empty:
        plan_df.to_csv('predictions/logistics_plan.csv', index=False)
        logger.info("Logistics plan saved to predictions/logistics_plan.csv")
    
    return plan_df

def run_logistics_pipeline():
    try:
        preds = pd.read_csv('predictions/prediction_results.csv')
    except FileNotFoundError:
        logger.error("prediction_results.csv not found. Please run the predict step first.")
        return
        
    route_optimization(preds)
    
if __name__ == "__main__":
    run_logistics_pipeline()
