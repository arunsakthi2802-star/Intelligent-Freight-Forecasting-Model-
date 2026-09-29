from pydantic import BaseModel
from typing import List, Optional

class VoyageRequest(BaseModel):
    cargo_type: str
    cargo_quantity_tonnes: float
    origin_country: str
    loading_port: str
    destination_port: str
    loading_date: str
    latest_arrival_date: str
    vessel_classes: List[str]
    preferred_loading_window_start: Optional[str] = None
    preferred_loading_window_end: Optional[str] = None
    preferred_discharge_window_start: Optional[str] = None
    preferred_discharge_window_end: Optional[str] = None
    maximum_total_cost: Optional[float] = None
    maximum_risk: Optional[str] = None
    maximum_transit_days: Optional[int] = None

class VesselCandidate(BaseModel):
    imo: str
    name: str
    vessel_class: str
    availability_status: str
    availability_probability: float
    eta_loading_port: str
    distance_to_loading_port_nm: float
    predicted_total_cost: float
    cost_per_tonne: float
    risk_score: float
    source: str
